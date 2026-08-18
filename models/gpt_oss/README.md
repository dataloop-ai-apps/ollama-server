# GPT OSS 20B — Ollama Model

**GPT OSS 20B** is a 20-billion-parameter open-source chat model served via Ollama, running on GPU (T4). This large language model is designed for complex reasoning tasks and advanced natural language understanding.

## Model Overview

GPT OSS 20B is a high-capacity model suitable for:
- Complex reasoning and problem-solving
- Code generation and analysis
- Technical documentation and explanations
- Advanced conversational AI applications
- Multi-turn dialogues with context retention

## Model Specifications

| Property | Value |
|---|---|
| Ollama model name | `gpt-oss:20b` |
| Ollama model page | [https://ollama.com/library/gpt-oss](https://ollama.com/library/gpt-oss) |
| Type | Chat |
| Parameters | 20 B |
| Architecture | Transformer-based |
| Streaming | Yes |
| Pod type | `gpu-t4-m` (GPU) |
| DPK name | `ollama-server-got-oss-20b` |

## Resource Requirements

- **GPU**: NVIDIA T4-m with 16GB VRAM minimum
- **Model size**: ~12-15 GiB in memory
- **Warmup time**: 5-10 minutes for initial model load
- **Recommended timeout**: 1800s (30 minutes) for cold-start scenarios

The model requires substantial GPU memory and benefits from the increased warmup timeout to ensure full initialization before serving requests.

## Performance Characteristics

- **Latency**: Higher than smaller models due to parameter count
- **Throughput**: Optimized for batch processing and streaming
- **Quality**: Superior performance on complex tasks requiring reasoning
- **Context retention**: Enhanced ability to maintain context over long conversations

## Deployment Considerations

### Warmup Configuration
The runner is configured with a 1800s (30-minute) warmup timeout to accommodate the large model size. This ensures the model is fully loaded into GPU memory before accepting requests, preventing timeout errors during cold-start scenarios.

### Resource Management
- Ensure sufficient GPU memory is available (16GB+ VRAM recommended)
- Monitor GPU utilization during inference
- Consider autoscaling settings based on expected load
- The model may require longer initialization times compared to smaller models

### Model-Specific Configuration
The warmup timeout is increased from the default 300s to 1800s in the runner configuration to handle the 20B parameter model's loading requirements.

## Model Information

GPT OSS 20B is an open-source large language model available through Ollama. It provides a balance between performance and resource requirements, making it suitable for production deployments that need more advanced reasoning capabilities than smaller models can offer.

The model is based on transformer architecture and has been trained on a diverse dataset to handle a wide range of natural language processing tasks. It supports streaming responses for real-time applications and can maintain context across multi-turn conversations.

As a 20-billion-parameter model, it sits in the middle range of model sizes - significantly more capable than smaller models (3-7B parameters) while being more resource-efficient than the largest models (70B+ parameters). This makes it suitable for organizations that need advanced capabilities but have constraints on GPU resources.

## Limitations

- Higher resource requirements compared to smaller models
- Increased latency due to parameter count
- Higher operational costs (GPU resources)
- Longer cold-start times

For general deployment instructions, build/push procedures, and API testing, see the [root README](../../README.md).