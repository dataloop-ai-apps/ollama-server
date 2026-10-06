# Qwen3 — Ollama Model

**Qwen3** is a 4-billion-parameter open-source model by Alibaba Cloud, served via Ollama, running on CPU. It supports a hybrid thinking mode — it can reason step-by-step before answering or respond directly, making it well suited for tasks that benefit from structured reasoning.

## Model Overview

Qwen3 is a compact reasoning-capable model suitable for:
- General conversational AI applications
- Complex reasoning and problem-solving
- Step-by-step thinking and explanation (thinking mode)
- Technical documentation and explanations
- Multi-turn dialogues with long context retention

## Model Specifications

| Property | Value |
|---|---|
| Ollama model name | `qwen3:4b` |
| Ollama model page | [https://ollama.com/library/qwen3](https://ollama.com/library/qwen3) |
| Type | Chat (Hybrid Reasoning) |
| Parameters | 4 B |
| Architecture | Transformer-based |
| Context window | 262,144 tokens |
| Streaming | Yes |
| Pod type | `highmem-l` (CPU) |
| DPK name | `ollama-server-qwen3` |

## Resource Requirements

- **CPU**: High-memory CPU instance (`highmem-l`)
- **Model size**: ~2-4 GiB in memory (quantized)
- **Warmup time**: 1-2 minutes for initial model load
- **Recommended timeout**: 300s (5 minutes) for cold-start scenarios

The model runs on CPU without requiring a GPU. The image configures `OLLAMA_WARMUP_MODEL=qwen3:4b` so the model is loaded into memory on container start — requests are served immediately without a cold-start delay.

## Performance Characteristics

- **Latency**: Low in standard mode; moderate in thinking mode (reasoning adds tokens)
- **Throughput**: Good for real-time applications with streaming
- **Quality**: Strong reasoning capabilities for its size class
- **Context retention**: Excellent — 262K token context window
- **Response structure**: Standard chat by default; prepends reasoning trace when thinking mode is enabled

## Deployment Considerations

### Hybrid Thinking Mode
Qwen3 supports two modes controlled via the `thinking` parameter in requests:
- **Thinking mode (default on)**: The model outputs a `<think>...</think>` reasoning block before the final answer. Use `max_tokens` of 512+ to avoid truncating the reasoning trace.
- **Non-thinking mode**: Pass `/no_think` in the system prompt or set `thinking: false` to get a direct response without the reasoning prefix.

### Warmup Configuration
The service uses `OLLAMA_WARMUP_MODEL=qwen3:4b` to pre-load the model on startup, avoiding cold-start latency on the first request.

### Resource Management
- Ensure sufficient CPU memory is available (8GB+ recommended)
- Monitor CPU utilization during inference
- Suitable for horizontal scaling due to lower resource requirements

## Model Information

Qwen3 is an open-source model from Alibaba Cloud, available through Ollama. It brings reasoning capability to a compact 4B parameter footprint, making structured thinking accessible without GPU infrastructure.

The model supports a 262,144 token context window and is pre-pulled at image build time (`ollama pull qwen3:4b`), so no download occurs on the first request. It is based on transformer architecture and supports multi-turn dialogue, streaming responses, and both thinking and non-thinking output modes.

## Limitations

- CPU-bound inference is slower than GPU-accelerated models under heavy load
- Thinking mode increases response latency and token count
- No function calling or embeddings support in this deployment
- 4B parameter size limits performance on highly specialized tasks compared to larger reasoning models (e.g., Qwen3.5 9B)

For general deployment instructions, build/push procedures, and API testing, see the [root README](../../README.md).
