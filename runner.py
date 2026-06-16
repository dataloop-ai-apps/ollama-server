import json
import logging
import os
import subprocess
import threading
import time
import urllib.error
import urllib.request

import dtlpy as dl

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("Ollama-Runner")


def _stream_output(pipe, log_level=logging.INFO, prefix=""):
    try:
        for line in iter(pipe.readline, ""):
            if line:
                msg = line.rstrip("\n\r")
                if prefix:
                    msg = f"{prefix}{msg}"
                logger.log(log_level, msg)
    finally:
        pipe.close()


class Runner(dl.BaseServiceRunner):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        os.environ.setdefault("OLLAMA_HOST", "0.0.0.0:3000")
        logger.info("OLLAMA_HOST: %s", os.environ.get("OLLAMA_HOST"))

        logger.info("Starting Ollama server...")
        self.server_process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        logger.info("Ollama server started with PID: %d", self.server_process.pid)

        logger.info("Starting output streaming threads...")
        threading.Thread(
            target=_stream_output,
            args=(self.server_process.stdout, logging.INFO),
            daemon=True,
        ).start()
        threading.Thread(
            target=_stream_output,
            args=(self.server_process.stderr, logging.WARNING, "[stderr] "),
            daemon=True,
        ).start()
        logger.info("Output streaming threads started")

        logger.info("Waiting for Ollama to be ready...")
        self._wait_for_ready()
        logger.info("Ollama is ready, starting model warmup in background...")

        threading.Thread(
            target=self._warmup_model,
            daemon=True,
        ).start()

        logger.info("Runner initialization complete, service is ready")

    def _log_system_info(self):
        """Log system memory and GPU information."""
        import psutil
        mem = psutil.virtual_memory()
        logger.info("System memory: total=%.2f GiB, available=%.2f GiB, used=%.2f GiB (%.1f%%)",
                    mem.total / (1024**3), mem.available / (1024**3),
                    mem.used / (1024**3), mem.percent)

        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,memory.free", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info("GPU info: %s", result.stdout.strip())
            else:
                logger.info("nvidia-smi not available or failed")
        except Exception as e:
            logger.info("Could not query GPU info: %s", e)

    def _log_loaded_models(self):
        """Log currently loaded models in Ollama."""
        try:
            with urllib.request.urlopen("http://localhost:3000/api/tags", timeout=5) as resp:
                data = json.loads(resp.read())
                models = [m.get('name', 'unknown') for m in data.get('models', [])]
                logger.info("Loaded models: %s", models)
        except Exception as e:
            logger.warning("Could not query loaded models: %s", e)

    def _warmup_model(self, timeout=3600):
        """Warm up the model by sending a minimal chat request."""
        model_name = os.environ.get("OLLAMA_WARMUP_MODEL", "")
        if not model_name:
            logger.info("Skipping warmup — OLLAMA_WARMUP_MODEL not set")
            return

        logger.info("Warming up model '%s' (this may take several minutes on GPU) ...", model_name)
        self._log_system_info()
        self._log_loaded_models()

        payload = json.dumps({
            "model": model_name,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 1,
            "stream": False,
        }).encode()

        req = urllib.request.Request(
            "http://localhost:3000/v1/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        t0 = time.time()
        try:
            logger.info("Sending warmup request to %s with %ds timeout...", req.full_url, timeout)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = json.loads(resp.read())
                elapsed = time.time() - t0
                logger.info(
                    "Model '%s' warm-up complete in %.1fs — finish_reason: %s",
                    model_name,
                    elapsed,
                    body.get("choices", [{}])[0].get("finish_reason", "?"),
                )
        except urllib.error.HTTPError as e:
            elapsed = time.time() - t0
            logger.error("Model warm-up HTTP error after %.1fs: %s - %s", elapsed, e.code, e.reason)
            logger.error("Response body: %s", e.read().decode() if hasattr(e, 'read') else 'N/A')
        except urllib.error.URLError as e:
            elapsed = time.time() - t0
            logger.error("Model warm-up URL error after %.1fs: %s", elapsed, e.reason)
        except Exception as e:
            elapsed = time.time() - t0
            logger.error("Model warm-up failed after %.1fs: %s", elapsed, e)

    def _wait_for_ready(self, timeout=60):
        """Poll Ollama until it responds on a health endpoint."""
        logger.info("Checking Ollama readiness with %ds timeout...", timeout)
        urls = [
            "http://localhost:3000/api/tags",
            "http://localhost:3000/v1/models",
        ]
        start = time.time()
        while time.time() - start < timeout:
            for url in urls:
                try:
                    with urllib.request.urlopen(url, timeout=2) as resp:
                        if resp.status == 200:
                            elapsed = time.time() - start
                            logger.info("Ollama is ready on port 3000 (via %s) after %.1fs", url, elapsed)
                            return
                except Exception:
                    pass
            time.sleep(1)
        elapsed = time.time() - start
        logger.error("Ollama failed to start within %ds (elapsed: %.1fs)", timeout, elapsed)
        raise RuntimeError(f"Ollama failed to start within {timeout}s")


if __name__ == "__main__":
    r = Runner()
    r.server_process.wait()
