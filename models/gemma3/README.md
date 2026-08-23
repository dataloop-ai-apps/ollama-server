# Gemma3 — Ollama Model

**Gemma3** is a 4-billion-parameter open-source chat model by Google DeepMind, served via Ollama, running on CPU. It is designed for general-purpose instruction following and conversational tasks with a very large context window.

## Model Overview

Gemma3 is a lightweight, general-purpose model suitable for:
- General conversational AI applications
- Question answering and information retrieval
- Text summarization and comprehension
- Instruction following and task completion
- Multi-turn dialogues with long context retention

## Model Specifications

| Property | Value |
|---|---|
| Ollama model name | `gemma3:4b` |
| Ollama model page | [https://ollama.com/library/gemma3](https://ollama.com/library/gemma3) |
| Type | Chat |
| Parameters | 4 B |
| Architecture | Transformer-based |
| Context window | 262,144 tokens |
| Streaming | Yes |
| Pod type | `highmem-l` (CPU) |
| DPK name | `ollama-server-gemma3` |

## Resource Requirements

- **CPU**: High-memory CPU instance (`highmem-l`)
- **Model size**: ~2-4 GiB in memory (quantized)
- **Warmup time**: 1-2 minutes for initial model load
- **Recommended timeout**: 300s (5 minutes) for cold-start scenarios

The model runs on CPU without requiring a GPU, making it suitable for cost-efficient deployments. The 4B parameter count keeps memory requirements modest while supporting a very large context window.

## Performance Characteristics

- **Latency**: Low — compact model runs efficiently on CPU
- **Throughput**: Good throughput for real-time applications
- **Quality**: Strong instruction following and general NLP performance
- **Context retention**: Excellent — 262K token context window supports very long conversations and documents
- **Response structure**: Standard chat output (no reasoning prefix)

## Deployment Considerations

### Resource Management
- Ensure sufficient CPU memory is available (8GB+ recommended)
- Monitor CPU utilization during inference
- Suitable for horizontal scaling due to lower resource requirements
- Faster cold-start times compared to larger GPU models

### Model-Specific Configuration
The model is pre-pulled at image build time (`ollama pull gemma3:4b`) so the container starts with the model already available — no download on first request. The default warmup timeout (300s) is sufficient for this model size.

## Model Information

Gemma3 is an open-source model from Google DeepMind, available through Ollama. It provides strong general-purpose capabilities while remaining resource-efficient enough for CPU-only deployments.

The model supports a 262,144 token context window, enabling it to process and retain context across very long conversations or large documents in a single pass. It is based on transformer architecture and has been trained for instruction following and multi-turn dialogue.

As a 4B-parameter CPU model, it offers a good balance between capability and operational cost — well suited for organizations that need reliable general chat without GPU infrastructure.

## Limitations

- Lower reasoning depth compared to dedicated reasoning models (e.g., Qwen3)
- CPU-bound inference is slower than GPU-accelerated models under heavy load
- No function calling or embeddings support in this deployment
- Performance on highly specialized tasks (advanced code generation, complex math) is limited relative to larger models

For general deployment instructions, build/push procedures, and API testing, see the [root README](../../README.md).
