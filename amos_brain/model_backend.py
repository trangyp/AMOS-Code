"""Model backend abstraction for local LLM providers.

Provides clean adapter interfaces for Ollama, LM Studio, vLLM, and other
OpenAI-compatible local endpoints. This is the primary execution boundary
for the AMOS local runtime.
"""

from __future__ import annotations

import json
import os
import time
from collections.abc import Iterator
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Protocol, TypeVar

import requests

T = TypeVar("T")


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    exceptions: tuple = (requests.RequestException,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for retry logic with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorated function with retry logic
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt < max_retries:
                        delay = min(base_delay * (2**attempt), max_delay)
                        time.sleep(delay)
                    else:
                        raise

            # Should never reach here
            raise RuntimeError("Retry logic failed")

        return wrapper

    return decorator


@dataclass
class LLMResult:
    """Result from a model generation call."""

    text: str
    raw: dict[str, Any]


class ModelBackend(Protocol):
    """Protocol for model backend implementations."""

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> LLMResult:
        """Generate a response from the model.

        Args:
            system_prompt: System instructions for the model
            user_prompt: User message/query
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            LLMResult containing generated text and raw response data
        """
        ...

    def health_check(self) -> dict[str, Any]:
        """Check if the backend is healthy and model is accessible.

        Returns:
            Dict with status, error message if any, and model info
        """
        ...

    def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> Iterator[str]:
        """Generate a streaming response from the model.

        Args:
            system_prompt: System instructions for the model
            user_prompt: User message/query
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Yields:
            Chunks of the generated response as they arrive
        """
        ...


class OllamaBackend:
    """Backend for Ollama local LLM server.

    Uses Ollama's native /api/generate endpoint.
    Default: http://127.0.0.1:11434
    """

    def __init__(self, model: str, base_url: str = "http://127.0.0.1:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()

    @with_retry(max_retries=3, base_delay=1.0)
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> LLMResult:
        """Generate using Ollama's native API with retry."""
        resp = self._session.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "system": system_prompt,
                "prompt": user_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        return LLMResult(text=data.get("response", ""), raw=data)

    def health_check(self) -> dict[str, Any]:
        """Check Ollama server and model availability."""
        try:
            # Check server is up
            resp = self._session.get(
                f"{self.base_url}/api/tags",
                timeout=10,
            )
            resp.raise_for_status()

            # Check model exists
            models = resp.json().get("models", [])
            model_names = [m.get("name", m.get("model", "")) for m in models]

            if self.model not in model_names:
                return {
                    "status": "error",
                    "error": (f"Model '{self.model}' not found. Available: {model_names}"),
                    "help": (f"Run: ollama pull {self.model}"),
                    "available_models": model_names,
                }

            return {
                "status": "healthy",
                "backend": "ollama",
                "model": self.model,
                "available_models": model_names,
            }

        except requests.ConnectionError:
            return {
                "status": "error",
                "error": (f"Cannot connect to Ollama at {self.base_url}"),
                "help": ("Is Ollama running? Try: ollama serve"),
            }
        except requests.Timeout:
            return {
                "status": "error",
                "error": f"Timeout connecting to Ollama at {self.base_url}",
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Health check failed: {e}",
            }

    def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> Iterator[str]:
        """Generate streaming response using Ollama's streaming API."""
        resp = self._session.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "system": system_prompt,
                "prompt": user_prompt,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            },
            timeout=120,
            stream=True,
        )
        resp.raise_for_status()

        for line in resp.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                    if data.get("done"):
                        break
                except json.JSONDecodeError:
                    continue


class OpenAICompatibleLocalBackend:
    """Backend for OpenAI-compatible local servers.

    Supports LM Studio, vLLM, llama.cpp server mode, and any other
    server implementing the OpenAI chat completions API.
    """

    def __init__(self, model: str, base_url: str, api_key: str = "local"):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._session = requests.Session()

    @with_retry(max_retries=3, base_delay=1.0)
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> LLMResult:
        """Generate using OpenAI-compatible chat completions API with retry."""
        resp = self._session.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        return LLMResult(text=text, raw=data)

    def health_check(self) -> dict[str, Any]:
        """Check OpenAI-compatible server and model availability."""
        try:
            # Try to list models (may not be available on all servers)
            resp = self._session.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )

            if resp.status_code == 200:
                models_data = resp.json()
                models = models_data.get("data", [])
                model_ids = [m.get("id", "") for m in models]

                # Check if our model is available
                if model_ids and self.model not in model_ids:
                    return {
                        "status": "warning",
                        "error": (f"Model '{self.model}' not in available models: {model_ids}"),
                        "help": ("Load the model in your server UI or API"),
                        "available_models": model_ids,
                    }

                return {
                    "status": "healthy",
                    "backend": "openai-compatible",
                    "model": self.model,
                    "available_models": model_ids,
                }

            # If /models fails, try a test completion
            return self._test_completion()

        except requests.ConnectionError:
            help_msg = "Is your server running?"
            if "1234" in self.base_url:
                help_msg = "Start LM Studio and enable server (port 1234)"
            elif "8000" in self.base_url:
                help_msg = "Start vLLM server"
            elif "8080" in self.base_url:
                help_msg = "Start llama.cpp server"
            return {
                "status": "error",
                "error": f"Cannot connect to server at {self.base_url}",
                "help": help_msg,
            }
        except requests.Timeout:
            return {
                "status": "error",
                "error": f"Timeout connecting to server at {self.base_url}",
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Health check failed: {e}",
            }

    def _test_completion(self) -> dict[str, Any]:
        """Test with a minimal completion request."""
        try:
            resp = self._session.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 5,
                },
                timeout=30,
            )

            if resp.status_code == 200:
                return {
                    "status": "healthy",
                    "backend": "openai-compatible",
                    "model": self.model,
                    "note": "Test completion succeeded",
                }
            else:
                return {
                    "status": "error",
                    "error": (f"Test completion failed: {resp.status_code}"),
                    "help": (f"Server returned {resp.status_code}. Check server logs."),
                }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Test completion failed: {e}",
            }

    def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> Iterator[str]:
        """Generate streaming response using OpenAI-compatible SSE API."""
        resp = self._session.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "text/event-stream",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
            },
            timeout=120,
            stream=True,
        )
        resp.raise_for_status()

        for line in resp.iter_lines():
            if line:
                line_str = line.decode("utf-8")
                if line_str.startswith("data: "):
                    data_str = line_str[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        if "content" in delta:
                            yield delta["content"]
                    except json.JSONDecodeError:
                        continue


def build_backend_from_env() -> ModelBackend:
    """Build a model backend from environment variables.

    Environment variables:
        AMOS_LLM_BACKEND: Provider type (ollama, openai-local, lmstudio, vllm)
        AMOS_MODEL: Model name (default: qwen2.5:14b-instruct for Ollama)
        AMOS_BASE_URL: Custom base URL for the server
        AMOS_API_KEY: API key for OpenAI-compatible servers (default: local)

    Returns:
        Configured ModelBackend instance

    Raises:
        ValueError: If backend type is unsupported
    """
    provider = os.getenv("AMOS_LLM_BACKEND", "ollama").lower()
    model = os.getenv("AMOS_MODEL", "qwen2.5:14b-instruct")
    base_url = os.getenv("AMOS_BASE_URL", "").strip()
    api_key = os.getenv("AMOS_API_KEY", "local")

    if provider == "ollama":
        return OllamaBackend(
            model=model,
            base_url=base_url or "http://127.0.0.1:11434",
        )

    if provider in {"openai-local", "lmstudio", "vllm", "llamacpp"}:
        default_urls = {
            "openai-local": "http://127.0.0.1:1234/v1",
            "lmstudio": "http://127.0.0.1:1234/v1",
            "vllm": "http://127.0.0.1:8000/v1",
            "llamacpp": "http://127.0.0.1:8080/v1",
        }
        url = base_url or default_urls.get(provider, "http://127.0.0.1:1234/v1")
        return OpenAICompatibleLocalBackend(
            model=model,
            base_url=url,
            api_key=api_key,
        )

    raise ValueError(
        f"Unsupported local backend: {provider}. "
        "Supported: ollama, openai-local, lmstudio, vllm, "
        "llamacpp"
    )
