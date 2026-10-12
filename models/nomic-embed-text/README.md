# Nomic Embed Text — Ollama Model

**Nomic Embed Text** is a high-performing open text embedding model served via Ollama, running on CPU. It produces 768-dimensional embedding vectors suitable for semantic search, retrieval-augmented generation (RAG), and similarity tasks.

## Model Overview

Nomic Embed Text is an embedding model suitable for:
- Semantic search and similarity ranking
- Retrieval-Augmented Generation (RAG) pipelines
- Document clustering and deduplication
- Text classification and nearest-neighbour retrieval
- Replacing hosted embedding APIs with a self-hosted alternative

## Model Specifications

| Property | Value |
|---|---|
| Ollama model name | `nomic-embed-text` |
| Ollama model page | [https://ollama.com/library/nomic-embed-text](https://ollama.com/library/nomic-embed-text) |
| Type | Embedding |
| Parameters | ~137 M |
| Embedding dimensions | 768 |
| Context window | 8 192 tokens |
| Architecture | BERT-style (nomic-bert) |
| Pod type | `highmem-m` (CPU) |
| DPK name | `ollama-server-nomic-embed-text` |

## Resource Requirements

- **CPU**: High-memory CPU instance
- **Model size**: ~300 MB in memory
- **Warmup time**: < 1 minute for initial model load
- **Recommended timeout**: 120s for cold-start scenarios

The model is small and CPU-optimised. It initialises quickly and can sustain high concurrency without GPU resources.

## Performance Characteristics

- **Latency**: Very low — fast encode for short and medium texts
- **Throughput**: High — batching many inputs per request is supported
- **Quality**: State-of-the-art for open embedding models on MTEB benchmark
- **Context retention**: Up to 8 192 tokens per input

## API Usage

Embed a single text:

```bash
curl http://localhost:3000/api/embed \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nomic-embed-text",
    "input": "The quick brown fox jumps over the lazy dog."
  }'
```

OpenAI-compatible endpoint:

```bash
curl http://localhost:3000/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nomic-embed-text",
    "input": "The quick brown fox jumps over the lazy dog."
  }'
```

Both return L2-normalised (unit-length) 768-dimensional vectors.

## Deployment Considerations

### Warmup Configuration
The runner uses the embedding warmup path (`OLLAMA_MODEL_TYPE=embedding`), which hits `/api/embed` instead of `/v1/chat/completions`. This is required because embedding-only models do not support the chat completions endpoint.

### Resource Management
- No GPU required — CPU-only deployment
- Low memory footprint compared to chat models
- Suitable for high-concurrency or auto-scaled deployments
- Can run alongside chat models on the same cluster if needed

### Model-Specific Configuration
Nomic Embed Text supports a `search_document:` / `search_query:` task prefix for improved retrieval performance:
- Prepend `search_document:` to texts being indexed
- Prepend `search_query:` to query texts at search time

## Model Information

Nomic Embed Text is an open-source text embedding model trained on a large corpus using a contrastive objective similar to CLIP. It is among the highest-performing small embedding models on the MTEB leaderboard and is the most popular embedding model in the Ollama library (88M+ pulls).

The model uses the nomic-bert architecture and produces 768-dimensional embeddings. It is fully open-weights (Apache 2.0) and does not require a vendor API key.

## Limitations

- Text-only — does not embed images
- No streaming (embeddings are returned in a single response)
- Not a generative model — cannot be used for chat completions

For general deployment instructions, build/push procedures, and API testing, see the [root README](../../README.md).
