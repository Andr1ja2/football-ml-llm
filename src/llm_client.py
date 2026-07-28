import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

def ask_model(prompt: str, model: str = "mistral") -> str:
    # Sends a prompt to the local Ollama model and returns the full response.
    data = {
        "model": model,
        "prompt": prompt,
    }

    resp = requests.post(OLLAMA_URL, json=data, stream=True)

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
