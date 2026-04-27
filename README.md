# Ollama Server — Dataloop App (DPK)

## What it is

**Ollama Server** is a Dataloop application that gives you **local language models** in your own environment. After you install it, you get a single service that runs **Ollama** and answers requests over a standard **HTTP interface** for chat, embeddings, and listing models. No external vendor account is required for the service itself—models run on the resources provided by the app.

Use it when you want **in-house inference** (privacy, cost control, or custom models) while still connecting from Dataloop projects, automations, or other tools you already use.

## How to use it

1. **Build and push** the container image your team uses for this DPK.  
2. **Publish** the DPK to your Dataloop project and **install** the app.  
3. **Point clients at the app’s URL** in your environment (or your platform’s recommended way to reach installed apps).  
4. **Choose a model** by name when you send a request (see the models table below).    

To attach a **Dataloop model** to this app, set the model’s **app** to this installed application and set the **model name** to the Ollama model id (for example `phi4-mini`). Your model adapter can then use the app like any other managed inference endpoint in Dataloop.

## When it is ready

The app brings Ollama up and waits until the service responds to health checks before it is considered **ready**. The container is built for **CPU** use; behavior on GPU is not the focus of this DPK as shipped.

## Models

The image is built to include **phi4-mini** out of the box. **Additional models** (see below) are on the roadmap and will be added in a future version of the image by extending the build—no code change in the app runner is required; new names simply appear once the weights are part of the image.

| Name              | Use        | In current image | Notes        |
|-------------------|------------|------------------|--------------|
| `phi4-mini`       | Chat       | Yes              | Default for testing |
| `qwen2.5:1.5b`    | Chat       | Planned          | Future release     |
| `nomic-embed-text` | Embeddings | Planned        | Future release     |

## What the service exposes (overview)

- **Chat** – send a conversation and get a reply; streaming is supported.  
- **Embeddings** – available once an embedding model is present in the image.  
- **List models** – see which model names you can use right now.  

Details follow the same patterns as Ollama’s published HTTP interface (including familiar `/v1/...` paths). Use your platform’s docs or the links from your Dataloop app for the exact base URL in each environment.

## Build and push

```bash
docker build -t gcr.io/viewo-g/piper/agent/ollama-server:1.0.0 .
docker push gcr.io/viewo-g/piper/agent/ollama-server:1.0.0
```

Align the image tag with what your `dataloop.json` and pipeline expect.

## Deploy in Dataloop

**Publish the DPK** from this repository, then **install the app** on a project. Example (adjust project and DPK name to match yours):

```python
import dtlpy as dl

project = dl.projects.get(project_name="<your-project>")
dpk = project.dpks.publish(src_path=".")
# After publish, or if the DPK already exists:
# dpk = project.dpks.get(dpk_name="ollama-server")
# app = project.apps.install(dpk=dpk)
# print(app.id)
```

## Optional: register with Jarvis

If you use **Jarvis** to list and route AI providers, register this app and the models you actually deploy. Replace placeholders (including the provider `type`) with the values your deployment guide specifies.

```bash
curl -X POST http://jarvis:6789/api/v1/ai/providers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "<app-id>",
    "route_name": "llm",
    "type": "<provider-type-per-your-docs>",
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
      }
    ]
  }'
```

Add more model blocks when you ship `qwen2.5:1.5b`, `nomic-embed-text`, or others. Field names and the allowed `type` value come from your Jarvis or internal runbook.

## Quick test

From a context where **port 3000** reaches the Ollama process (for example a port-forward to the app), you can list models and send a short chat. Replace the host with whatever your runbook says.

```bash
curl http://localhost:3000/v1/models
```

```bash
curl http://localhost:3000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi4-mini",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

After you add an embedding model, you can test embeddings the same way using that model’s name and the embeddings endpoint for your Ollama version.

## Next Step: more models

The next step for this DPK is to **ship the remaining models** in the container build (Qwen, Nomic, or any others you standardize on), then refresh registration and documentation so teams see the full list. Until then, the published image focuses on **phi4-mini** for chat.
