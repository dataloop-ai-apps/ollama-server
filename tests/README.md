# Tests Documentation

This folder contains integration tests for the Ollama Server Dataloop applications.

## Test Overview

The tests verify that deployed Ollama services are functioning correctly by:
- Listing available models via `/v1/models`
- Sending simple chat requests via `/v1/chat/completions`
- Testing streaming chat responses

## Test Files

- `test_models.py` - Test functions that run against deployed services

## How to Configure

Edit the constants at the top of `test_models.py`:

```python
PROJECT_NAME = "project-name"   # Your Dataloop project name
RUN_ENV = "rc"                  # "rc" or "prod"

# DPK names of the deployed Ollama services to test
DPK_NAMES = [
    "ollama-server-gpt-oss-20b",
    "ollama-server-qwen35",
    "ollama-server-phi4",
]
```

## How to Run Tests

```bash
python tests/test_models.py
```

On first run you will be prompted to log in via browser (for RC) or with an API key (for PROD).

## Test Functions

### `test_app_model_request(dpk_name, app_id)`
Tests GET `/v1/models` and returns the response JSON. The first model ID is used for subsequent tests.

### `test_app_chat_simple(model_name, app_id)`
Tests POST `/v1/chat/completions` and asserts a non-empty reply.

### `test_chat_openai_streaming(model_name, app_id)`
Tests POST `/v1/chat/completions` with `stream: true` and asserts a non-empty streamed response.

## Test Flow

1. Login to Dataloop using `RUN_ENV`
2. Iterate over all DPK names in `DPK_NAMES`
3. Look up the installed app by DPK display name — skip if not found
4. Run all three test functions for each app

## Troubleshooting

- **App not found**: Ensure the DPK is published and installed in the project. Check `DPK_NAMES` values match exactly.
- **401/403 errors**: Re-run to trigger a fresh login, or check your credentials.
