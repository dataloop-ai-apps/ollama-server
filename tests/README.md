# Ollama Service — Smoke Tests

End-to-end smoke tests for the Ollama service deployed on Dataloop.

## Files

- **`test_models.py`** — Main test runner. Contains session helpers and all test functions.
- **`test_configs.py`** — Configuration: environment selection and model registry.

---

## Configuration (`test_configs.py`)

Before running the tests, open `test_configs.py` and set the following two things to match your deployment:

**1. Environment** — set `RUN_ENV` to either `PROD` or `RC`:

```python
RUN_ENV = Environment.PROD  # or Environment.RC
```

**2. Model registry** — for each model you want to test, add an entry to `TEST_MODELS` with:
- `app_id` — set to the installed app ID of the Ollama service on Dataloop for each model

```python
TEST_MODELS = {
    'phi4-mini':  {'app_id': "<installed_app_id>", 'model_name': "phi4-mini"},
    'gpt-oss-20b': {'app_id': "<installed_app_id>", 'model_name': "gpt-oss-20b"},
}
```

> The `app_id` can be found in the Dataloop platform under the installed app for each model service.

---

## Prerequisites

**PROD** — requires a `DTLPY_API_KEY` environment variable (or `.env` file):

```
DTLPY_API_KEY=<your_api_key>
```

**RC** — requires an active Dataloop RC login token. If expired, a browser login will be triggered automatically on port `7364`.

---

## Running the Tests

```bash
python tests/test_models.py
```

Tests iterate over every entry in `TEST_MODELS` and run three checks per model:

| Test | Description |
|---|---|
| `test_app_model_request` | `GET /v1/models` via `app.request` — asserts HTTP 200 |
| `test_app_chat_simple` | `POST /v1/chat/completions` via `app.request` — asserts a non-empty reply |
| `test_chat_openai_streaming` | `POST /v1/chat/completions` with `stream=True` via direct HTTP — asserts non-empty streamed content |
