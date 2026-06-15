"""
Minimal Python LLM integration module.
"""

import requests
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout

service_enabled = False

backend = None
base_url = None
model = None
api_key = None


def try_enabling_service():
    global service_enabled
    global backend, base_url, model, api_key

    service_enabled = False

    from os import getenv

    backend = getenv("LLM_BACKEND", None)
    base_url = getenv("LLM_BASE_URL", None)
    model = getenv("LLM_MODEL", None)
    api_key = getenv("LLM_API_KEY", None)

    if not backend:
        print("[llm_service] Could not enable service -> LLM_BACKEND is not set")
        return False

    if not base_url:
        print("[llm_service] Could not enable service -> LLM_BASE_URL is not set")
        return False

    if not model:
        print("[llm_service] Could not enable service -> LLM_MODEL is not set")
        return False

    if backend in ["openai"] and not api_key:
        print("[llm_service] Could not enable service -> LLM_API_KEY is required for OpenAI backend")
        return False

    print(f"[llm_service] Enabling service... backend={backend}, base_url={base_url}, model={model}")
    service_enabled = True
    return True


def is_service_enabled():
    return service_enabled


def chat(message):
    """
    Send a message to the configured LLM and return the response text.
    Returns None if the service is not enabled or the request fails.
    """
    if not is_service_enabled():
        if not try_enabling_service():
            return None

    messages = [{"role": "user", "content": message}]

    try:
        match backend:
            case "ollama":
                return _ollama_chat(messages)
            case "openai":
                return _openai_chat(messages)
            case _:
                print(f"[llm_service] Unknown backend: {backend}")
                return None
    except ConnectionError as e:
        print(f"[llm_service] Connection error: {e}")
        return None
    except Timeout as e:
        print(f"[llm_service] Timeout error: {e}")
        return None
    except HTTPError as e:
        print(f"[llm_service] HTTP error: {e}")
        return None
    except RequestException as e:
        print(f"[llm_service] Request error: {e}")
        return None


def _ollama_chat(messages):
    resp = requests.post(
        f"{base_url}/api/chat",
        json={"model": model, "messages": messages, "stream": False},
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def _openai_chat(messages):
    resp = requests.post(
        f"{base_url}/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": model, "messages": messages},
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]
