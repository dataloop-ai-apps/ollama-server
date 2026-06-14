# Tests Documentation

This folder contains integration tests for the Ollama Server Dataloop applications.

## Test Overview

The tests verify that deployed Ollama services are functioning correctly by:
- Listing available models via `/v1/models`
- Sending simple chat requests via `/v1/chat/completions`
- Testing streaming chat responses

## Test Files

- `test_configs.py` - Configuration for test models and environments
- `test_models.py` - Test functions that run against deployed services

## How to Configure Test Models

Edit `test_configs.py` to add or modify model configurations:

```python
TEST_MODELS = {
    'model_key': {
        'app_id': '<your-app-id>',
        'model_name': '<ollama-model-name>',
        'service_name': '<service-name>'
    }
}
```

**Parameters:**
- `app_id`: The Dataloop app ID of the deployed Ollama service
- `model_name`: The Ollama model name (e.g., `phi4-mini`, `gpt-oss:20b`)
- `service_name`: The service name used to construct the gate URL

To get the `app_id` after deploying:
```python
import dtlpy as dl
project = dl.projects.get(project_name="<your-project>")
dpk = project.dpks.publish(src_path="apps/<model-folder>")
app = project.apps.install(dpk=dpk)
print(app.id)  # Use this as app_id in test_configs.py
```

## How to Run Tests

1. Set up your environment:
   - For PROD: Set `DTLPY_API_KEY` environment variable
   - For RC: No setup needed (will prompt for login)

2. Set the environment in `test_configs.py`:
   ```python
   RUN_ENV = Environment.PROD  # or Environment.RC
   ```

3. Run the tests:
   ```bash
   python tests/test_models.py
   ```

## Test Functions

### `test_app_model_request(model_name, app_id)`
Tests GET `/v1/models` via the Dataloop app request method and asserts the model is listed.

### `test_app_chat_simple(model_name, app_id)`
Tests POST `/v1/chat/completions` via the Dataloop app request method and asserts a non-empty reply.

### `test_chat_openai_streaming(model_name, app_id, service_name)`
Tests POST `/v1/chat/completions` with streaming enabled via direct HTTP and asserts a non-empty response. This test follows the redirect flow to get the apps URL and JWT cookie.

## Test Flow

1. Login to Dataloop using the configured environment
2. Iterate over all models in `TEST_MODELS`
3. For each model, run all three test functions
4. Report pass/fail for each test

## Environment Setup

### PROD Environment
Requires an API key:
```bash
export DTLPY_API_KEY=your-api-key
```

### RC Environment
No setup required - will prompt for interactive login via browser.

## Troubleshooting

- **Socket hang up errors**: May indicate model warmup issues or service timeouts. Check the service logs in the Dataloop console.
- **401/403 errors**: Check your API key or login credentials.
- **App not found**: Verify the `app_id` in test_configs.py matches your deployed app.
