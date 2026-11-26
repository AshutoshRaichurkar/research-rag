"""Call the local LLM (Llama 3.1 via Ollama) and return its answer."""

import time

import httpx

from research_rag.config import get_settings

# Tokens the model can read at once (prompt + answer). Ollama's default is smaller.
CONTEXT_WINDOW = 8192


class LLMError(RuntimeError):
    """Raised when the LLM can't produce an answer."""


def generate(
    prompt: str, temperature: float = 0, retries: int = 1, json_format: bool = False
) -> str:
    """Send a prompt to Ollama and return the answer text. Retries on network errors."""
    settings = get_settings()
    url = f"{settings.ollama_base_url}/api/generate"
    body = {
        "model": settings.llm_model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_ctx": CONTEXT_WINDOW},
    }
    if json_format:
        body["format"] = "json"  # Ollama guarantees the reply parses as JSON

    for attempt in range(retries + 1):
        try:
            response = httpx.post(url, json=body, timeout=120)
            response.raise_for_status()
            return response.json()["response"].strip()
        except (httpx.TransportError, httpx.HTTPStatusError) as error:
            if attempt == retries:
                raise LLMError(f"Ollama failed after {retries + 1} attempts: {error}") from error
            time.sleep(1)  # wait a moment, then try again
