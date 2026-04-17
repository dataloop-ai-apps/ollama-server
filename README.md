# Ollama Server — Dataloop App (DPK)

Dataloop App that runs Ollama inside a managed container, serving an **OpenAI-compatible API on port 3000**.

## Pre-loaded Models

| Model | Type | Parameters | Context Window |
|-------|------|-----------|----------------|
| `phi4-mini` | Chat | 3.8B | 16 384 |
| `qwen2.5:1.5b` | Chat | 1.5B | 32 768 |
| `nomic-embed-text` | Embedding | 137M | 8 192 |

## API Endpoints (OpenAI-compatible)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/chat/completions` | POST | Chat completion (streaming supported) |
| `/v1/embeddings` | POST | Generate embeddings |
| `/v1/models` | GET | List available models |

## Build & Push

```bash
# Build the Docker image
docker build -t gcr.io/viewo-g/piper/agent/ollama-server:1.0.0 .

# Push to registry
docker push gcr.io/viewo-g/piper/agent/ollama-server:1.0.0
```

## Deploy to Dataloop

### Publish the DPK

```python
import dtlpy as dl

project = dl.projects.get(project_name="<your-project>")
dpk = project.dpks.publish(src_path=".")
print(f"Published DPK: {dpk.name} v{dpk.version}")
```

### Install the App

```python
project = dl.projects.get(project_name="<your-project>")
dpk = project.dpks.get(dpk_name="ollama-server")
app = project.apps.install(dpk=dpk)
print(f"App installed: {app.id}")
```

## Register with Jarvis

```bash
curl -X POST http://jarvis:6789/api/v1/ai/providers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "<app-id>",
    "route_name": "llm",
    "type": "openai-compatible",
    "models": [
      {
        "id": "phi4-mini",
        "display_name": "Phi-4 Mini (3.8B)",
        "capabilities": {
          "chat": true,
          "embeddings": false,
          "function_calling": true,
          "vision": false,
          "streaming": true
        },
        "context_window": 16384,
        "max_output_tokens": 4096
      },
      {
        "id": "qwen2.5:1.5b",
        "display_name": "Qwen 2.5 (1.5B)",
        "capabilities": {
          "chat": true,
          "embeddings": false,
          "function_calling": false,
          "vision": false,
          "streaming": true
        },
        "context_window": 32768,
        "max_output_tokens": 4096
      },
      {
        "id": "nomic-embed-text",
        "display_name": "Nomic Embed Text",
        "capabilities": {
          "chat": false,
          "embeddings": true,
          "function_calling": false,
          "vision": false,
          "streaming": false
        },
        "context_window": 8192,
        "max_output_tokens": 0
      }
    ]
  }'
```

## Verify

```bash
# List models
curl http://localhost:3000/v1/models

# Chat completion
curl http://localhost:3000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi4-mini",
    "messages": [{"role": "user", "content": "Hello, who are you?"}]
  }'

# Embedding
curl http://localhost:3000/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nomic-embed-text",
    "input": "The quick brown fox jumps over the lazy dog"
  }'
```

## Adding More Models

1. Add `ollama pull <model>` to the Dockerfile
2. Rebuild & push the image
3. Update the Jarvis provider registration with the new model entry

No code changes needed — models are declared at registration time.
