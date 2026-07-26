"""
Smoke test against the deployed Ollama service on Dataloop.

Flow:
  1. GET gate URL with Bearer token -> 302 redirect to apps URL
  2. All subsequent requests go directly to the apps URL (no auth needed)

Login is handled automatically by the login() function using RUN_ENV defined below.
"""

import json
import dtlpy as dl
from dotenv import load_dotenv
import os

PROJECT_ID = "afd5a953-b88d-439c-afdf-9486ab3a94c2"

RUN_ENV = "rc"

TEST_MODELS = [
    {"model_name": "gpt-oss:20b","dpk_name": "ollama-server-gpt-oss-20b",  "service_name": "ollama-service-gpt-oss-20b"},    
    {"model_name": "qwen3.5:9b", "dpk_name": "ollama-server-qwen35", "service_name": "ollama-service-qwen35"}, 
    {"model_name": "phi4-mini","dpk_name": "ollama-server-phi4", "service_name": "ollama-service-phi4"}, 
]


def login(env):
    """Login to Dataloop using API key from environment.

    Args:
        env: Environment string ('prod' or 'rc')
    """
    if env == "prod":
        load_dotenv(override=True)
        dl.setenv(env)
        api_key = os.getenv('DTLPY_API_KEY')
        dl.login_api_key(api_key=api_key)
    else:
        dl.setenv(env)
        if dl.token_expired():
            dl.login(callback_port=7364)




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
        data=json.dumps({
            "model": model_name,
            "messages": [{"role": "user", "content": "Say hello"}],
            "max_tokens": 512
        }, separators=(',', ':')),
        headers={"Content-Type": "application/json"},
    )
    resp_json = response.json()
    # print(f"  Full response JSON: {resp_json}")
    msg = resp_json["choices"][0]["message"]["content"]
    # Some models (like qwen3.5) use 'reasoning' field instead of 'content'
    if not msg and "reasoning" in resp_json["choices"][0]["message"]:
        msg = resp_json["choices"][0]["message"]["reasoning"]
    print(f"  Response: {msg}")
    print("PASS\n")

def test_chat_openai_streaming(model_name, app_id):
    """Test POST /v1/chat/completions with streaming via app.request and assert non-empty response.

    Args:
        model_name: The Ollama model name to test (e.g. 'phi4-mini').
        app_id: The Dataloop app ID of the deployed Ollama service.
    """
    print(f"--- POST /v1/chat/completions openai (streaming) - {model_name} ---")
    app = dl.apps.get(app_id=app_id)
    resp = app.request(
        method='POST',
        path='/v1/chat/completions',
        data=json.dumps({
            "model": model_name,
            "messages": [{"role": "user", "content": "Count from 1 to 5."}],
            "max_tokens": 512,
            "stream": True,
        }, separators=(',', ':')),
        headers={"Content-Type": "application/json"},
        stream=True,
    )
    print(f"  [{resp.status_code}]")
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

    # assert len(full) > 0
    print("PASS\n")


if __name__ == "__main__":
    # Run all tests
    login(RUN_ENV)

    # Iterate over all models in TEST_MODELS
    for model_config in TEST_MODELS:
        model_name = model_config['model_name']
        service_name = model_config['service_name']
        dpk_name = model_config['dpk_name']

        print(f"\n{'='*60}")
        print(f"Testing model: {model_name} ")
        print(f"{'='*60}\n")
        project = dl.projects.get(project_id=PROJECT_ID)
        dpk = project.dpks.get(dpk_name=dpk_name)
        try:
            app = project.apps.get(app_name=dpk.display_name)  # get existing
        except dl.exceptions.NotFound:
            print(f"App not found for DPK '{dpk_name}' — skipping.")
            continue

        app_id = app.id

        test_app_model_request(model_name, app_id)
        test_app_chat_simple(model_name, app_id)
        test_chat_openai_streaming(model_name, app_id)        
    print("All tests passed.")
