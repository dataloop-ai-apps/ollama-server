"""
Smoke test against the deployed Ollama service on Dataloop.

Flow:
  1. GET gate URL with Bearer token -> 302 redirect to apps URL
  2. All subsequent requests go directly to the apps URL (no auth needed)

Login first: python -c "import dtlpy as dl; dl.setenv('rc'); dl.login()"
"""

import requests
import dtlpy as dl

APP_ID = "69e1e76af52467d417e5624e"
GATE_BASE = "https://rc-gate.dataloop.ai/api/v1/apps/ollama-service-69e1e76af52467d417e5624e/panels"

dl.setenv("rc")
if dl.token_expired():
    dl.login(callback_port=7364)

session = requests.Session()
resp = session.get(GATE_BASE + "/v1", headers=dl.client_api.auth)
base_url = resp.url.rstrip("/")
print(f"Probe status:   {resp.status_code}")
print(f"Location:       {resp.headers.get('Location', 'none')}")
print(f"All headers:    {dict(resp.headers)}")
print(f"All cookies:    {dict(resp.cookies)}")
print(f"Set-Cookie raw: {resp.headers.get('Set-Cookie', 'none')}")
print(f"Body:           {resp.text[:200]}")
print()

APPS_URL = base_url
JWT_APP = session.cookies.get("JWT-APP")

SESSION = requests.Session()
if JWT_APP:
    SESSION.cookies.set("JWT-APP", JWT_APP)


def req(path, body=None):
    url = APPS_URL.rstrip("/") + path
    if body:
        resp = SESSION.post(url, json=body, timeout=120)
    else:
        resp = SESSION.get(url, timeout=120)
    print(f"  [{resp.status_code}] {url}")
    if not resp.ok:
        print(f"  Error: {resp.text}")
    resp.raise_for_status()
    return resp.json()


def test_list_models():
    print("--- GET /v1/models ---")
    resp = req("/models")
    models = [m["id"] for m in resp["data"]]
    print(f"  Models: {models}")
    print("PASS\n")


def test_chat():
    print("--- POST /v1/chat/completions (phi4-mini) ---")
    resp = req("/chat/completions", {
        "model": "phi4-mini",
        "messages": [{"role": "user", "content": "Say hello in one sentence."}],
        "max_tokens": 64,
    })
    msg = resp["choices"][0]["message"]["content"]
    print(f"  Response: {msg}")
    print("PASS\n")


def test_chat_openai_streaming():
    print("--- OpenAI SDK streaming (phi4-mini) ---")
    from openai import OpenAI

    client = OpenAI(
        base_url=APPS_URL,
        api_key="",
        default_headers={"Cookie": f"JWT-APP={JWT_APP}"} if JWT_APP else {},
    )

    stream = client.chat.completions.create(
        model="phi4-mini",
        messages=[{"role": "user", "content": "Count from 1 to 5."}],
        max_tokens=64,
        stream=True,
    )

    print("  Response: ", end="")
    full = ""
    for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        print(delta, end="", flush=True)
        full += delta
    print()

    assert len(full) > 0
    print("PASS\n")


if __name__ == "__main__":
    print(f"\nTesting: {APPS_URL}\n")
    test_list_models()
    test_chat()
    test_chat_openai_streaming()
    print("All tests passed.")
