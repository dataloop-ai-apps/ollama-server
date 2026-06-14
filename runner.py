import json
import logging
import os
import subprocess
import threading
import time
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

        self.server_process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

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

    def _wait_for_ready(self, timeout=60):
        """Poll Ollama until it responds on a health endpoint."""
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
                            logger.info("Ollama is ready on port 3000 (via %s)", url)
                            return
                except Exception:
                    pass
            time.sleep(1)
        raise RuntimeError(f"Ollama failed to start within {timeout}s")

    def _log_system_info(self):
        """Log available system memory for diagnostics."""
        try:
            with open("/proc/meminfo") as f:
                lines = {l.split(":")[0]: l.split(":")[1].strip() for l in f if ":" in l}
            total = lines.get("MemTotal", "?")
            free = lines.get("MemAvailable", "?")
            logger.info("System memory — total: %s  available: %s", total, free)
        except Exception as e:
            logger.warning("Could not read /proc/meminfo: %s", e)

    def _log_loaded_models(self):
        """Log which models Ollama currently has loaded/available."""
        try:
            with urllib.request.urlopen("http://localhost:3000/v1/models", timeout=5) as resp:
                data = json.loads(resp.read())
            models = [m["id"] for m in data.get("data", [])]
            logger.info("Models available in Ollama: %s", models)
        except Exception as e:
            logger.warning("Could not fetch model list: %s", e)

    def _warmup_model(self, model_name="gpt-oss:20b", timeout=1800):
        """Send a minimal chat request to force Ollama to load the model into memory.

        Without this, the first real request triggers a cold-load of a 12+ GiB model
        and the Dataloop gateway times out (504) before inference begins.
        """
        logger.info("Warming up model '%s' (this may take several minutes on CPU) ...", model_name)
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
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = json.loads(resp.read())
                elapsed = time.time() - t0
                logger.info(
                    "Model '%s' warm-up complete in %.1fs — finish_reason: %s",
                    model_name,
                    elapsed,
                    body.get("choices", [{}])[0].get("finish_reason", "?"),
                )
        except Exception as e:
            elapsed = time.time() - t0
            logger.error("Model warm-up failed after %.1fs: %s", elapsed, e)
            raise


if __name__ == "__main__":
    r = Runner()
    r.server_process.wait()
