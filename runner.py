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
        logger.info("Runner initialization complete, service is ready")

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
