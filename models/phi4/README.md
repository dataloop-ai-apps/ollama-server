# Phi-4 Mini — Ollama Model

**Phi-4 Mini** is a 3.8-billion-parameter open-source chat model served via Ollama, running on CPU. This compact language model is designed for efficient inference while maintaining strong performance on a wide range of natural language tasks.

## Model Overview

Phi-4 Mini is a lightweight model suitable for:
- General conversational AI applications
- Question answering and information retrieval
- Text summarization and comprehension
- Basic code generation and assistance
- Multi-language text processing

## Model Specifications

| Property | Value |
|---|---|
| Ollama model name | `phi4-mini` |
| Ollama model page | [https://ollama.com/library/phi4-mini](https://ollama.com/library/phi4-mini) |
| Type | Chat |
| Parameters | 3.8 B |
| Architecture | Transformer-based |
| Streaming | Yes |
| Pod type | `highmem-m` (CPU) |
| DPK name | `ollama-server-phi4` |

## Resource Requirements

- **CPU**: High-memory CPU instance recommended
- **Model size**: ~2-3 GiB in memory
- **Warmup time**: 1-2 minutes for initial model load
- **Recommended timeout**: 300s (5 minutes) for cold-start scenarios

The model is optimized for CPU deployment and requires less memory than larger models, making it suitable for environments with limited GPU resources or where cost efficiency is a priority.

## Performance Characteristics

- **Latency**: Lower than larger models due to smaller parameter count
- **Throughput**: High throughput suitable for real-time applications
- **Quality**: Good performance on general NLP tasks
- **Context retention**: Maintains context for moderate-length conversations

## Deployment Considerations

### Warmup Configuration
The runner uses the default 300s (5-minute) warmup timeout, which is sufficient for the 3.8B parameter model. The smaller model size allows for faster initialization compared to larger models.

### Resource Management
- Ensure sufficient CPU memory is available (8GB+ recommended)
- Monitor CPU utilization during inference
- Suitable for horizontal scaling due to lower resource requirements
- Faster cold-start times compared to larger models

### Model-Specific Configuration
The warmup timeout uses the default 300s setting, which is adequate for the smaller model size and allows for quick deployment cycles.

## Model Information

Phi-4 Mini is an open-source large language model available through Ollama. It provides an excellent balance between performance and resource efficiency, making it ideal for deployments where GPU resources are limited or cost constraints are a concern.

The model is based on transformer architecture and has been trained on a diverse dataset to handle a wide range of natural language processing tasks. It supports streaming responses for real-time applications and can maintain context across multi-turn conversations.

As a 3.8-billion-parameter model, it is significantly more resource-efficient than larger models (20B+ parameters) while still providing strong capabilities for most common NLP tasks. This makes it suitable for organizations that need a balance between performance and operational costs.

## Limitations

- Limited reasoning capabilities compared to larger models
- May struggle with highly complex technical tasks
- Smaller context window compared to larger models
- Lower performance on specialized tasks (e.g., advanced code generation)

For general deployment instructions, build/push procedures, and API testing, see the [root README](../../README.md).
