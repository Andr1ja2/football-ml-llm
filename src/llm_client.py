import json

import requests

from src.live_config import settings_manager

OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
TAGS_TIMEOUT_SEC = 5
GENERATE_TIMEOUT_SEC = (5, 300)

NO_MODEL_MESSAGE = (
    "No LLM model selected. Open Settings, refresh the model list, "
    "and choose an installed Ollama model."
)


def _resolve_model(explicit: str | None) -> str:
    name = (explicit or settings_manager.get("LLM_MODEL") or "").strip()
    if not name:
        raise RuntimeError(NO_MODEL_MESSAGE)
    return name


def get_installed_models() -> list[str]:
    """Return full Ollama model names from the local server, or [] if unreachable."""
    try:
        resp = requests.get(OLLAMA_TAGS_URL, timeout=TAGS_TIMEOUT_SEC)
    except (requests.ConnectionError, requests.Timeout):
        return []

    if resp.status_code != 200:
        return []

    try:
        payload = resp.json()
    except json.JSONDecodeError:
        return []

    names = [entry["name"] for entry in payload.get("models", []) if entry.get("name")]
    return sorted(set(names))


def ask_model(prompt: str, model: str | None = None) -> str:
    resolved = _resolve_model(model)
    data = {
        "model": resolved,
        "prompt": prompt,
    }

    try:
        resp = requests.post(
            OLLAMA_GENERATE_URL,
            json=data,
            stream=True,
            timeout=GENERATE_TIMEOUT_SEC,
        )
    except (requests.ConnectionError, requests.Timeout) as exc:
        raise RuntimeError(
            "Could not reach the Ollama server at localhost:11434. "
            "Make sure Ollama is running and try again."
        ) from exc

    if resp.status_code != 200:
        raise RuntimeError(f"Error from Ollama: {resp.text}")

    full_response = []

    # Read the streamed chunks
    for chunk in resp.iter_lines():
        if chunk:
            parsed = json.loads(chunk.decode())
            if "response" in parsed:
                full_response.append(parsed["response"])

    return "".join(full_response)
