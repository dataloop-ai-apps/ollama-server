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
    ollama pull gpt-oss:20b && \     
    kill $OLLAMA_PID || true

ENV OLLAMA_HOST=0.0.0.0:3000
ENV OLLAMA_KEEP_ALIVE=-1
EXPOSE 3000