"""
providers.py
Handles all outbound API calls for Orbit's three model providers:
  - Gemini              (Google Generative Language REST API)
  - DeepSeek             (GitHub Models, OpenAI-compatible endpoint)
  - Llama (Meta)          (GitHub Models, OpenAI-compatible endpoint)

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
from typing import Optional

import requests
from openai import OpenAI, APIConnectionError, AuthenticationError, APIStatusError

GITHUB_MODELS_BASE_URL = "https://models.github.ai/inference"

MODEL_CATALOG = {
    "Gemini 3.5 Flash": {"provider": "gemini", "model_id": "gemini-3.5-flash"},
    "DeepSeek R1": {"provider": "github", "model_id": "deepseek/DeepSeek-R1"},
    "Llama 3.3 70B": {"provider": "github", "model_id": "meta/Llama-3.3-70B-Instruct"},
}

# HTTP status codes that get a friendlier message than a raw Gemini error dump.
GEMINI_STATUS_MESSAGES = {
    400: "Invalid Gemini API key or malformed request.",
    403: "Invalid Gemini API key or malformed request.",
    429: "Gemini rate limit reached. Wait a moment and try again.",
}


# ---------------------------------------------------------------------------
# Result builders — every call site returns exactly this shape, defined once.
# ---------------------------------------------------------------------------

def _success(content: str, tokens: Optional[int], elapsed: float) -> dict:
    return {"ok": True, "content": content, "error": None, "tokens": tokens, "elapsed": elapsed}


def _failure(error: str, elapsed: float = 0.0, tokens: Optional[int] = None) -> dict:
    return {"ok": False, "content": "", "error": error, "tokens": tokens, "elapsed": elapsed}


def _estimate_tokens(text: str) -> int:
    """Rough fallback estimate (~4 chars/token) when an API doesn't report usage."""
    return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# Gemini
# ---------------------------------------------------------------------------

def call_gemini(api_key: str, model_id: str, messages: list, system_prompt: str) -> dict:
    if not api_key:
        return _failure("Missing Gemini API key. Add GEMINI_API_KEY to your .env file.")

    start = time.perf_counter()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"

    contents = [
        {"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]}
        for m in messages
    ]
    payload = {"contents": contents}
    if system_prompt:
        payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

    try:
        resp = requests.post(url, json=payload, timeout=60)
    except requests.exceptions.ConnectionError:
        return _failure("Connection failed. Check your internet connection.", time.perf_counter() - start)
    except requests.exceptions.Timeout:
        return _failure("Request timed out. Gemini took too long to respond.", time.perf_counter() - start)

    elapsed = time.perf_counter() - start

    if resp.status_code != 200:
        message = GEMINI_STATUS_MESSAGES.get(
            resp.status_code, f"Gemini API error ({resp.status_code}): {resp.text[:200]}"
        )
        return _failure(message, elapsed)

    data = resp.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return _failure("Gemini returned an unexpected response format.", elapsed)

    tokens = data.get("usageMetadata", {}).get("totalTokenCount", _estimate_tokens(text))
    return _success(text, tokens, elapsed)


# ---------------------------------------------------------------------------
# GitHub Models (DeepSeek, Llama — OpenAI-compatible endpoint)
# ---------------------------------------------------------------------------

def call_github_model(token: str, model_id: str, messages: list, system_prompt: str) -> dict:
    if not token:
        return _failure("Missing GitHub token. Add GITHUB_TOKEN to your .env file.")

    start = time.perf_counter()
    client = OpenAI(base_url=GITHUB_MODELS_BASE_URL, api_key=token)

    chat_messages = []
    if system_prompt:
        chat_messages.append({"role": "system", "content": system_prompt})
    chat_messages.extend({"role": m["role"], "content": m["content"]} for m in messages)

    try:
        response = client.chat.completions.create(model=model_id, messages=chat_messages)
    except AuthenticationError:
        return _failure("Invalid GitHub token. Check GITHUB_TOKEN in your .env file.", time.perf_counter() - start)
    except APIConnectionError:
        return _failure("Connection failed. Check your internet connection.", time.perf_counter() - start)
    except APIStatusError as e:
        return _failure(f"GitHub Models API error ({e.status_code}): {str(e)[:200]}", time.perf_counter() - start)
    except Exception as e:
        return _failure(f"Unexpected error: {str(e)[:200]}", time.perf_counter() - start)

    elapsed = time.perf_counter() - start
    text = response.choices[0].message.content or ""
    tokens = getattr(response.usage, "total_tokens", None) if response.usage else _estimate_tokens(text)

    return _success(text, tokens, elapsed)


# ---------------------------------------------------------------------------
# Single entry point
# ---------------------------------------------------------------------------

def get_completion(display_model: str, messages: list, system_prompt: str, api_keys: dict) -> dict:
    """Single entry point app.py calls, regardless of provider."""
    if not messages or not messages[-1]["content"].strip():
        return _failure("Cannot send an empty message.")

    config = MODEL_CATALOG.get(display_model)
    if not config:
        return _failure(f"Unknown model: {display_model}")

    if config["provider"] == "gemini":
        return call_gemini(api_keys.get("gemini", ""), config["model_id"], messages, system_prompt)
    return call_github_model(api_keys.get("github", ""), config["model_id"], messages, system_prompt)