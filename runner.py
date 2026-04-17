import os
import time
import subprocess
import threading
import urllib.request
import dtlpy as dl


def _stream_output(pipe, prefix=""):
    """Read lines from pipe and print to main process stdout/stderr for visibility."""
    try:
        for line in iter(pipe.readline, ""):
            if line:
                print(prefix + line, end="", flush=True)
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

        self.t_out = threading.Thread(
            target=_stream_output,
            args=(self.server_process.stdout,),
            daemon=True,
        )
        self.t_err = threading.Thread(
            target=_stream_output,
            args=(self.server_process.stderr, "[ollama] "),
            daemon=True,
        )
        self.t_out.start()
        self.t_err.start()

        self._wait_for_ready()

    def _wait_for_ready(self, timeout=60):
        """Poll Ollama until it responds on the health endpoint."""
        url = "http://localhost:3000/api/tags"
        start = time.time()
        while time.time() - start < timeout:
            try:
                with urllib.request.urlopen(url, timeout=2) as resp:
                    if resp.status == 200:
                        print("Ollama is ready on port 3000", flush=True)
                        return
            except Exception:
                pass
            time.sleep(1)
        raise RuntimeError(f"Ollama failed to start within {timeout}s")


if __name__ == "__main__":
    runner = Runner()
    runner.t_out.join()
    runner.t_err.join()
