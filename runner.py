import logging
import os
import subprocess
import threading
import time

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask

import dtlpy as dl

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("Ollama-Runner")

OLLAMA_PORT = 11434
PROXY_PORT = 3000
STRIP_PREFIX = "/ollama"
_SKIP_HEADERS = frozenset(("host", "content-length", "transfer-encoding", "connection"))

# ---------------------------------------------------------------------------
# FastAPI proxy — strips panel prefix, streams responses (SSE-safe)
# ---------------------------------------------------------------------------

proxy_app = FastAPI()
_client = httpx.AsyncClient(
    base_url=f"http://localhost:{OLLAMA_PORT}",
    timeout=httpx.Timeout(300, connect=10),
)


@proxy_app.middleware("http")
async def strip_panel_prefix(request: Request, call_next):
    path = request.scope.get("path", "")
    if path.startswith(STRIP_PREFIX):
        request.scope["path"] = path[len(STRIP_PREFIX):] or "/"
    return await call_next(request)


@proxy_app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
async def reverse_proxy(request: Request):
    """Forward all requests to the Ollama binary on port 11434.

    This is a reverse proxy — serve-agent talks to port 3000 thinking it's
    Ollama, but FastAPI intercepts, strips the panel prefix (via middleware),
    and forwards to the actual Ollama process. Needed because Ollama is a Go
    binary and we can't inject Python middleware into it.
    """
    path = request.url.path
    if request.url.query:
        path = f"{path}?{request.url.query}"

    body = await request.body()
    headers = {k: v for k, v in request.headers.items() if k.lower() not in _SKIP_HEADERS}

    req = _client.build_request(request.method, path, content=body or None, headers=headers)
    resp = await _client.send(req, stream=True)

    resp_headers = {k: v for k, v in resp.headers.multi_items() if k.lower() not in _SKIP_HEADERS}
    return StreamingResponse(
        resp.aiter_bytes(),
        status_code=resp.status_code,
        headers=resp_headers,
        background=BackgroundTask(resp.aclose),
    )


# ---------------------------------------------------------------------------
# Ollama process management
# ---------------------------------------------------------------------------

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

        threading.Thread(target=_stream_output, args=(self.server_process.stdout, logging.INFO), daemon=True).start()
        threading.Thread(target=_stream_output, args=(self.server_process.stderr, logging.WARNING, "[stderr] "), daemon=True).start()

        self._wait_for_ready()

        threading.Thread(
            target=uvicorn.run,
            args=(proxy_app,),
            kwargs={"host": "0.0.0.0", "port": PROXY_PORT, "log_level": "info"},
            daemon=True,
        ).start()
        logger.info("FastAPI proxy ready on port %d -> %d (strips '%s')", PROXY_PORT, OLLAMA_PORT, STRIP_PREFIX)

    def _wait_for_ready(self, timeout=60):
        logger.info("Checking Ollama readiness with %ds timeout...", timeout)
        urls = [
            f"http://localhost:{OLLAMA_PORT}/api/tags",
            f"http://localhost:{OLLAMA_PORT}/v1/models",
        ]
        start = time.time()
        while time.time() - start < timeout:
            for url in urls:
                try:
                    r = httpx.get(url, timeout=2)
                    if r.status_code == 200:
                        logger.info("Ollama ready on port %d (via %s) after %.1fs", OLLAMA_PORT, url, time.time() - start)
                        return
                except httpx.ConnectError:
                    pass
            time.sleep(1)
        raise RuntimeError(f"Ollama failed to start within {timeout}s")


if __name__ == "__main__":
    r = Runner()
    r.server_process.wait()
