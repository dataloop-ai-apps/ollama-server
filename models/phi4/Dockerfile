FROM hub.dataloop.ai/dtlpy-runner-images/cpu:python3.13_full_bci

RUN curl -fsSLk -L https://github.com/ollama/ollama/releases/download/v0.9.0/ollama-linux-amd64.tgz \
        -o /tmp/ollama.tgz && \
    tar -xzf /tmp/ollama.tgz -C /usr && \
    rm /tmp/ollama.tgz && \
    ollama --version

RUN ollama serve & OLLAMA_PID=$! && \
    sleep 5 && \
    ollama pull phi4-mini && \
    kill $OLLAMA_PID || true

ENV OLLAMA_HOST=0.0.0.0:3000
ENV OLLAMA_KEEP_ALIVE=-1
ENV OLLAMA_WARMUP_MODEL=phi4-mini
EXPOSE 3000


# Build & push (this is the sole runtime image; app code is deployed via FaaS codebase):
# docker build --no-cache -t gcr.io/viewo-g/piper/agent/runner/apps/ollama-server:phi4-mini-1.0.1 -f Dockerfile .
# docker push gcr.io/viewo-g/piper/agent/runner/apps/ollama-server:phi4-mini-1.0.1
