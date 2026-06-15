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


if __name__ == "__main__":
    r = Runner()
    r.server_process.wait()
