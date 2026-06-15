# FROM hub.dataloop.ai/dtlpy-runner-images/cpu:python3.12_opencv
FROM hub.dataloop.ai/dtlpy-runner-images/gpu:python3.12_cuda11.8_opencv

RUN apt-get update && \
    apt-get install -y --no-install-recommends zstd && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    curl -fsSLk https://ollama.com/install.sh | sed 's/curl -/curl -k -/g' | sh && \
    ollama --version

ENV PATH="/usr/local/bin:${PATH}"

# Pre-pull models at build time so the container starts instantly
RUN ollama serve & OLLAMA_PID=$! && \
    sleep 5 && \    
    ollama pull qwen3.5 && \    
    kill $OLLAMA_PID || true

COPY runner.py /runner.py

ENV OLLAMA_HOST=0.0.0.0:3000
ENV OLLAMA_KEEP_ALIVE=-1
EXPOSE 3000


# Build & push (this is the sole runtime image; app code is deployed via FaaS codebase):
# docker build --no-cache -t gcr.io/viewo-g/piper/agent/ollama-server:1.0.1 -f Dockerfile .
# docker push gcr.io/viewo-g/piper/agent/ollama-server:1.0.1
