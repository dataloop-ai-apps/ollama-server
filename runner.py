import json
import logging
import subprocess
import threading
import os
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

        logger.info("Starting Ollama server...")
        self.server_process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        logger.info("Ollama server started with PID: %d", self.server_process.pid)

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

        self._wait_for_ready()
        self._warmup_model()
        logger.info("Runner initialization complete, service is ready")

    def _warmup_model(self, timeout=3600):
        """Warm up the model by sending a minimal request.

        For chat models (default): POST /v1/chat/completions.
        For embedding models (OLLAMA_MODEL_TYPE=embedding): POST /api/embed.
        """
        model_name = os.environ.get("OLLAMA_WARMUP_MODEL", "")
        if not model_name:
            logger.info("Skipping warmup — OLLAMA_WARMUP_MODEL not set")
            return

        model_type = os.environ.get("OLLAMA_MODEL_TYPE", "chat")
        logger.info("Warming up %s model '%s' (this may take several minutes on GPU) ...", model_type, model_name)

        if model_type == "embedding":
            payload = json.dumps({"model": model_name, "input": "Hello"}).encode()
            url = "http://localhost:3000/api/embed"
        else:
            payload = json.dumps({
                "model": model_name,
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 1,
                "stream": False,
            }).encode()
            url = "http://localhost:3000/v1/chat/completions"

        req = urllib.request.Request(
            url,
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
                if model_type == "embedding":
                    n = len(body.get("embeddings", []))
                    logger.info(
                        "Model '%s' warm-up complete in %.1fs — %d embedding(s) returned",
                        model_name, elapsed, n,
                    )
                else:
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
            if self.server_process.poll() is not None:
                raise RuntimeError(f"Ollama process exited with code {self.server_process.returncode}")
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
