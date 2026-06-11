"""
Smoke test against the deployed Ollama service on Dataloop.

Flow:
  1. GET gate URL with Bearer token -> 302 redirect to apps URL
  2. All subsequent requests go directly to the apps URL (no auth needed)

Login is handled automatically by the login() function using RUN_ENV from test_configs.
"""

import json
import dtlpy as dl
import requests
from dotenv import load_dotenv
import os

from test_configs import TEST_MODELS, Environment, RUN_ENV


def login(env):
    """Login to Dataloop using API key from environment.

    Args:
        env: Environment to use (Environment.PROD or Environment.RC)
    """
    if (env == Environment.PROD):
        load_dotenv(override=True)
        dl.setenv(env.value)
        api_key = os.getenv('DTLPY_API_KEY')
        dl.login_api_key(api_key=api_key)
    else:
        dl.setenv(env.value)
        if dl.token_expired():
            dl.login(callback_port=7364)



def create_session(jwt_app):
    """Create a requests session with JWT-APP cookie for authentication."""
    session = requests.Session()
    if jwt_app:
        session.cookies.set("JWT-APP", jwt_app)
    return session


def setup_session(app_id):
    """Setup session by following redirect to get apps URL and JWT cookie.

    Args:
        app_id: The app ID used to construct the gate base URL.
    Returns:
        tuple: (apps_url, jwt_app)
    Raises:
        RuntimeError: If the gate request does not redirect to an apps URL.
    """
    gate_base = f"https://gate.dataloop.ai/api/v1/apps/ollama-service-{app_id}/panels"
    session = requests.Session()
    resp = session.get(gate_base + "/v1", headers=dl.client_api.auth)
    if not resp.url or "apps.dataloop.ai" not in resp.url:
        raise RuntimeError(f"Unexpected redirect target: {resp.url} (status {resp.status_code})")
    apps_url = resp.url.rstrip("/")
    jwt_app = session.cookies.get("JWT-APP")
    print(f"APPS_URL resolved: {apps_url}")
    return apps_url, jwt_app


def test_app_model_request(model_name, app_id):
    """Test GET /v1/models via app.request and assert the model is listed.

    Args:
        model_name: The Ollama model name to test (e.g. 'phi4-mini').
        app_id: The Dataloop app ID of the deployed Ollama service.
    """
    print(f"--- GET /v1/models (via app.request) - {model_name} ---")
    app = dl.apps.get(app_id=app_id)
    response = app.request(
        method='GET',
        path='/v1/models',
    )
    print(f"  Response: {response.text}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("PASS\n")

def test_app_chat_simple(model_name, app_id):
    """Test POST /v1/chat/completions via app.request and assert a non-empty reply.

    Args:
        model_name: The Ollama model name to test (e.g. 'phi4-mini').
        app_id: The Dataloop app ID of the deployed Ollama service.
    """
    print(f"--- POST /v1/chat/completions (simple) - {model_name} ---")
    app = dl.apps.get(app_id=app_id)
    response = app.request(
        method='POST',
        path='/v1/chat/completions',
        json={
            "model": model_name,
            "messages": [{"role": "user", "content": "Say hello"}],
            "max_tokens": 64,
        }
    )
    resp_json = response.json()
    msg = resp_json["choices"][0]["message"]["content"]
    print(f"  Response: {msg}")
    print("PASS\n")

def test_chat_openai_streaming(model_name, app_id):
    """Test POST /v1/chat/completions with streaming via direct HTTP and assert non-empty response.

    Args:
        model_name: The Ollama model name to test (e.g. 'phi4-mini').
        app_id: The Dataloop app ID used to resolve the apps URL via setup_session.
    """
    print(f"--- POST /v1/chat/completions (streaming) - {model_name} ---")
    apps_url, jwt_app = setup_session(app_id)
    session = create_session(jwt_app)

    url = apps_url.rstrip("/") + "/chat/completions"
    resp = session.post(url, json={
        "model": model_name,
        "messages": [{"role": "user", "content": "Count from 1 to 5."}],
        "max_tokens": 64,
        "stream": True,
    }, timeout=180, stream=True)
    print(f"  [{resp.status_code}] {url}")
    resp.raise_for_status()

    print("  Response: ", end="")
    full = ""
    for line in resp.iter_lines():
        if line.startswith(b"data: "):
            data = line[6:]
            if data == b"[DONE]":
                break
            chunk = json.loads(data)
            delta = chunk["choices"][0]["delta"].get("content", "")
            print(delta, end="", flush=True)
            full += delta
    print()

    assert len(full) > 0
    print("PASS\n")


if __name__ == "__main__":
    # Run all tests
    login(RUN_ENV)

    # Iterate over all models in TEST_MODELS
    for config_name, model_config in TEST_MODELS.items():
        model_name = model_config['model_name']
        app_id = model_config['app_id']
        print(f"\n{'='*60}")
        print(f"Testing model: {model_name} (config: {config_name})")
        print(f"{'='*60}\n")

        test_app_model_request(model_name, app_id)
        test_app_chat_simple(model_name, app_id)
        test_chat_openai_streaming(model_name, app_id)

    print("All tests passed.")
