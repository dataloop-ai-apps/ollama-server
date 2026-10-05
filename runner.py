import json
import logging
import os
import subprocess
import threading
import time
import urllib.error
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

import dtlpy as dl

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("Ollama-Runner")

OLLAMA_PORT = 11434  # Ollama's default internal port
PROXY_PORT = 3000    # Port serve-agent forwards to
STRIP_PREFIX = "/ollama"  # Panel name prefix to strip


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


class _ProxyHandler(BaseHTTPRequestHandler):
    """Strips the panel prefix and forwards to the Ollama binary."""

    def _proxy(self):
        path = self.path
        if path.startswith(STRIP_PREFIX):
            path = path[len(STRIP_PREFIX):] or "/"

        url = f"http://localhost:{OLLAMA_PORT}{path}"

        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else None

        req = urllib.request.Request(url, data=body, method=self.command)
        for key, val in self.headers.items():
            if key.lower() not in ("host", "content-length", "transfer-encoding"):
                req.add_header(key, val)
        if body:
            req.add_header("Content-Length", str(len(body)))

        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                resp_body = resp.read()
                self.send_response(resp.status)
                for key, val in resp.getheaders():
                    if key.lower() not in ("transfer-encoding",):
                        self.send_header(key, val)
                self.end_headers()
                self.wfile.write(resp_body)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_GET(self):
        self._proxy()

    def do_POST(self):
        self._proxy()

    def log_message(self, format, *args):
        logger.info("[proxy] %s", format % args)


class Runner(dl.BaseServiceRunner):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Start Ollama on its default port (11434)
        os.environ["OLLAMA_HOST"] = f"0.0.0.0:{OLLAMA_PORT}"
        logger.info("Starting Ollama server on port %d...", OLLAMA_PORT)
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

        # Start reverse proxy on port 3000 (strips panel prefix)
        self._proxy_server = HTTPServer(("0.0.0.0", PROXY_PORT), _ProxyHandler)
        threading.Thread(target=self._proxy_server.serve_forever, daemon=True).start()
        logger.info("Prefix-stripping proxy ready on port %d → %d", PROXY_PORT, OLLAMA_PORT)

        logger.info("Runner initialization complete, service is ready")

    def _wait_for_ready(self, timeout=60):
        """Poll Ollama until it responds on a health endpoint."""
        logger.info("Checking Ollama readiness with %ds timeout...", timeout)
        urls = [
            f"http://localhost:{OLLAMA_PORT}/api/tags",
            f"http://localhost:{OLLAMA_PORT}/v1/models",
        ]
        start = time.time()
        while time.time() - start < timeout:
            for url in urls:
                try:
                    with urllib.request.urlopen(url, timeout=2) as resp:
                        if resp.status == 200:
                            elapsed = time.time() - start
                            logger.info("Ollama is ready on port %d (via %s) after %.1fs", OLLAMA_PORT, url, elapsed)
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
