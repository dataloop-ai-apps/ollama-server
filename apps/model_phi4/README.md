# model-phi4 — Ollama DPK

Microsoft **Phi-4 Mini** served via Ollama. Lightweight chat model optimised for reasoning and instruction-following, running on CPU.

## Model details

| Property | Value |
|---|---|
| Ollama model name | `phi4-mini` |
| Type | Chat (instruction-tuned) |
| Parameters | 3.8 B |
| Context window | 16 384 tokens |
| Streaming | Yes |
| Pod type | `highmem-m` (CPU) |
| DPK name | `ollama-server-phi4` |

## Quick test

```bash
# List available models
curl <APPS_URL>/v1/models

# Chat
curl <APPS_URL>/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi4-mini",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

Replace `<APPS_URL>` with the installed app URL from Dataloop.

## Deploy

```python
import dtlpy as dl
project = dl.projects.get(project_name="<your-project>")
dpk = project.dpks.publish(src_path=".")
app = project.apps.install(dpk=dpk)
print(app.id)  # use this as app_id in test_configs.py
```
