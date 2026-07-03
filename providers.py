"""
providers.py
Handles all outbound API calls for Orbit's three model providers:
  - Gemini            (Google Generative Language REST API)
  - DeepSeek           (GitHub Models, OpenAI-compatible endpoint)
  - Llama (Meta)        (GitHub Models, OpenAI-compatible endpoint)

Every function returns a dict:
  {
    "ok": bool,
    "content": str,          # assistant reply, or empty on failure
    "error": str | None,     # human-readable error message
    "tokens": int | None,    # total tokens used, if the API reports it
    "elapsed": float         # seconds taken
  }
This keeps app.py provider-agnostic.
"""

import time
import requests
from openai import OpenAI, APIConnectionError, AuthenticationError, APIStatusError

GITHUB_MODELS_BASE_URL = "https://models.github.ai/inference"

MODEL_CATALOG = {
    "Gemini 3.5 Flash": {"provider": "gemini", "model_id": "gemini-3.5-flash"},
    "DeepSeek R1": {"provider": "github", "model_id": "deepseek/DeepSeek-R1"},
    "Llama 3.3 70B": {"provider": "github", "model_id": "meta/Llama-3.3-70B-Instruct"},
}


def _estimate_tokens(text: str) -> int:
    """Rough fallback estimate (~4 chars/token) when an API doesn't report usage."""
    return max(1, len(text) // 4)


def call_gemini(api_key: str, model_id: str, messages: list, system_prompt: str) -> dict:
    start = time.perf_counter()

    if not api_key:
        return {"ok": False, "content": "", "error": "Missing Gemini API key. Add GEMINI_API_KEY to your .env file.",
                "tokens": None, "elapsed": 0.0}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"

    contents = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    payload = {"contents": contents}
    if system_prompt:
        payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

    try:
        resp = requests.post(url, json=payload, timeout=60)
    except requests.exceptions.ConnectionError:
        return {"ok": False, "content": "", "error": "Connection failed. Check your internet connection.",
                "tokens": None, "elapsed": time.perf_counter() - start}
    except requests.exceptions.Timeout:
        return {"ok": False, "content": "", "error": "Request timed out. Gemini took too long to respond.",
                "tokens": None, "elapsed": time.perf_counter() - start}

    elapsed = time.perf_counter() - start

    if resp.status_code == 400 or resp.status_code == 403:
        return {"ok": False, "content": "", "error": "Invalid Gemini API key or malformed request.",
                "tokens": None, "elapsed": elapsed}
    if resp.status_code == 429:
        return {"ok": False, "content": "", "error": "Gemini rate limit reached. Wait a moment and try again.",
                "tokens": None, "elapsed": elapsed}
    if resp.status_code != 200:
        return {"ok": False, "content": "", "error": f"Gemini API error ({resp.status_code}): {resp.text[:200]}",
                "tokens": None, "elapsed": elapsed}

    data = resp.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return {"ok": False, "content": "", "error": "Gemini returned an unexpected response format.",
                "tokens": None, "elapsed": elapsed}

    tokens = data.get("usageMetadata", {}).get("totalTokenCount", _estimate_tokens(text))
    return {"ok": True, "content": text, "error": None, "tokens": tokens, "elapsed": elapsed}


def call_github_model(token: str, model_id: str, messages: list, system_prompt: str) -> dict:
    start = time.perf_counter()

    if not token:
        return {"ok": False, "content": "", "error": "Missing GitHub token. Add GITHUB_TOKEN to your .env file.",
                "tokens": None, "elapsed": 0.0}

    client = OpenAI(base_url=GITHUB_MODELS_BASE_URL, api_key=token)

    chat_messages = []
    if system_prompt:
        chat_messages.append({"role": "system", "content": system_prompt})
    chat_messages.extend({"role": m["role"], "content": m["content"]} for m in messages)

    try:
        response = client.chat.completions.create(model=model_id, messages=chat_messages)
    except AuthenticationError:
        return {"ok": False, "content": "", "error": "Invalid GitHub token. Check GITHUB_TOKEN in your .env file.",
                "tokens": None, "elapsed": time.perf_counter() - start}
    except APIConnectionError:
        return {"ok": False, "content": "", "error": "Connection failed. Check your internet connection.",
                "tokens": None, "elapsed": time.perf_counter() - start}
    except APIStatusError as e:
        return {"ok": False, "content": "", "error": f"GitHub Models API error ({e.status_code}): {str(e)[:200]}",
                "tokens": None, "elapsed": time.perf_counter() - start}
    except Exception as e:
        return {"ok": False, "content": "", "error": f"Unexpected error: {str(e)[:200]}",
                "tokens": None, "elapsed": time.perf_counter() - start}

    elapsed = time.perf_counter() - start
    text = response.choices[0].message.content or ""
    tokens = getattr(response.usage, "total_tokens", None) if response.usage else _estimate_tokens(text)

    return {"ok": True, "content": text, "error": None, "tokens": tokens, "elapsed": elapsed}


def get_completion(display_model: str, messages: list, system_prompt: str, api_keys: dict) -> dict:
    """Single entry point app.py calls, regardless of provider."""
    if not messages or not messages[-1]["content"].strip():
        return {"ok": False, "content": "", "error": "Cannot send an empty message.", "tokens": None, "elapsed": 0.0}

    config = MODEL_CATALOG.get(display_model)
    if not config:
        return {"ok": False, "content": "", "error": f"Unknown model: {display_model}", "tokens": None, "elapsed": 0.0}

    if config["provider"] == "gemini":
        return call_gemini(api_keys.get("gemini", ""), config["model_id"], messages, system_prompt)
    else:
        return call_github_model(api_keys.get("github", ""), config["model_id"], messages, system_prompt)
