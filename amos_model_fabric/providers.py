"""AMOS Model Fabric - Provider Implementations

Unified adapters for local model backends:
- Ollama (native API)
- LM Studio (OpenAI-compatible)
- llama.cpp (OpenAI-compatible server)
- vLLM (OpenAI-compatible)
- SGLang (OpenAI-compatible)
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone

UTC = timezone.utc
from typing import Any, Optional

import aiohttp

from .schemas import FabricRequest, FabricResponse, FabricStreamChunk, ProviderType

logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    """Abstract base for all model providers."""

    def __init__(
        self,
        provider_type: ProviderType,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: float = 120.0,
    ):
        self.provider_type = provider_type
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
        self._available_models: list[str] = []

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers=self._default_headers(),
            )
        return self._session

    def _default_headers(self) -> dict[str, str]:
        """Default headers for requests."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    @abstractmethod
    async def complete(self, request: FabricRequest) -> FabricResponse:
        """Complete a chat request."""
        pass

    @abstractmethod
    async def complete_stream(self, request: FabricRequest):
        """Stream a chat completion."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is healthy."""
        pass

    @abstractmethod
    async def list_models(self) -> list[str]:
        """List available models."""
        pass

    def is_local(self) -> bool:
        """Check if this is a local/offline provider."""
        return "localhost" in self.base_url or "127.0.0.1" in self.base_url

    async def close(self) -> None:
        """Close provider connections."""
        if self._session and not self._session.closed:
            await self._session.close()


class OllamaProvider(BaseProvider):
    """Ollama native API provider."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: float = 120.0,
    ):
        super().__init__(ProviderType.OLLAMA, base_url, None, timeout)

    async def health_check(self) -> bool:
        """Check Ollama availability."""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/tags", timeout=5) as resp:
                return resp.status == 200
        except Exception as e:
            logger.debug(f"Ollama health check failed: {e}")
            return False

    async def list_models(self) -> list[str]:
        """List available Ollama models."""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/tags") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = [m["name"] for m in data.get("models", [])]
                    self._available_models = models
                    return models
        except Exception as e:
            logger.warning(f"Failed to list Ollama models: {e}")
        return []

    async def complete(self, request: FabricRequest) -> FabricResponse:
        """Send chat completion request to Ollama."""
        start = datetime.now(UTC)
        session = await self._get_session()
        model = request.model or "qwen2.5-coder:14b"

        payload: dict[str, Any] = {
            "model": model,
            "messages": request.messages,
            "stream": False,
            "options": {"temperature": request.temperature},
        }
        if request.max_tokens:
            payload["options"]["num_predict"] = request.max_tokens
        if request.tools:
            payload["tools"] = request.tools

        async with session.post(f"{self.base_url}/api/chat", json=payload) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(f"Ollama error: {text}")
            data = await resp.json()
            latency = (datetime.now(UTC) - start).total_seconds() * 1000

            return FabricResponse(
                content=data.get("message", {}).get("content", ""),
                model=model,
                provider=ProviderType.OLLAMA,
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                latency_ms=latency,
                finish_reason="stop" if not data.get("done_reason") else data["done_reason"],
                raw_response=data,
            )

    async def complete_stream(self, request: FabricRequest):
        """Stream completion from Ollama."""
        session = await self._get_session()
        model = request.model or "qwen2.5-coder:14b"

        payload: dict[str, Any] = {
            "model": model,
            "messages": request.messages,
            "stream": True,
            "options": {"temperature": request.temperature},
        }
        if request.max_tokens:
            payload["options"]["num_predict"] = request.max_tokens

        async with session.post(f"{self.base_url}/api/chat", json=payload) as resp:
            async for line in resp.content:
                line = line.decode("utf-8").strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    message = data.get("message", {})
                    content = message.get("content", "")
                    is_done = data.get("done", False)
                    yield FabricStreamChunk(
                        content=content,
                        model=model,
                        provider=ProviderType.OLLAMA,
                        request_id=request.request_id or "",
                        is_finished=is_done,
                        finish_reason=data.get("done_reason") if is_done else None,
                    )
                    if is_done:
                        break
                except json.JSONDecodeError:
                    continue


class OpenAICompatibleProvider(BaseProvider):
    """Base for OpenAI-compatible providers."""

    async def health_check(self) -> bool:
        """Check if server is up."""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/v1/models", timeout=5) as resp:
                return resp.status == 200
        except Exception as e:
            logger.debug(f"Health check failed: {e}")
            return False

    async def list_models(self) -> list[str]:
        """List available models."""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/v1/models") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = [m["id"] for m in data.get("data", [])]
                    self._available_models = models
                    return models
        except Exception as e:
            logger.warning(f"Failed to list models: {e}")
        return []

    def _convert_request(self, request: FabricRequest) -> dict:
        """Convert FabricRequest to OpenAI format."""
        payload: dict[str, Any] = {
            "model": request.model or "local-model",
            "messages": request.messages,
            "temperature": request.temperature,
            "stream": request.stream,
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        if request.top_p != 1.0:
            payload["top_p"] = request.top_p
        if request.tools:
            payload["tools"] = request.tools
        if request.response_format:
            payload["response_format"] = request.response_format
        return payload

    async def complete(self, request: FabricRequest) -> FabricResponse:
        """Send chat completion request."""
        start = datetime.now(UTC)
        session = await self._get_session()
        payload = self._convert_request(request)
        payload["stream"] = False

        async with session.post(f"{self.base_url}/v1/chat/completions", json=payload) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(f"API error: {text}")
            data = await resp.json()
            latency = (datetime.now(UTC) - start).total_seconds() * 1000
            choice = data["choices"][0]
            message = choice.get("message", {})
            return FabricResponse(
                content=message.get("content", ""),
                model=data.get("model", request.model or "unknown"),
                provider=self.provider_type,
                usage=data.get("usage", {}),
                latency_ms=latency,
                finish_reason=choice.get("finish_reason"),
                tool_calls=message.get("tool_calls"),
                raw_response=data,
            )

    async def complete_stream(self, request: FabricRequest):
        """Stream completion."""
        session = await self._get_session()
        payload = self._convert_request(request)
        payload["stream"] = True

        async with session.post(f"{self.base_url}/v1/chat/completions", json=payload) as resp:
            async for line in resp.content:
                line = line.decode("utf-8").strip()
                if not line or not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                    choice = data["choices"][0]
                    delta = choice.get("delta", {})
                    yield FabricStreamChunk(
                        content=delta.get("content", ""),
                        model=data.get("model", request.model or "unknown"),
                        provider=self.provider_type,
                        request_id=request.request_id or "",
                        is_finished=choice.get("finish_reason") is not None,
                        finish_reason=choice.get("finish_reason"),
                    )
                except (json.JSONDecodeError, KeyError):
                    continue


class LMStudioProvider(OpenAICompatibleProvider):
    """LM Studio OpenAI-compatible server."""

    def __init__(
        self,
        base_url: str = "http://localhost:1234",
        api_key: str | None = None,
        timeout: float = 120.0,
    ):
        super().__init__(ProviderType.LM_STUDIO, base_url, api_key or "lm-studio", timeout)


class LlamaCppProvider(OpenAICompatibleProvider):
    """llama.cpp server."""

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        timeout: float = 120.0,
    ):
        super().__init__(ProviderType.LLAMA_CPP, base_url, None, timeout)


class VLLMProvider(OpenAICompatibleProvider):
    """vLLM OpenAI-compatible server."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: str | None = None,
        timeout: float = 120.0,
    ):
        super().__init__(ProviderType.VLLM, base_url, api_key, timeout)


class SGLangProvider(OpenAICompatibleProvider):
    """SGLang OpenAI-compatible server."""

    def __init__(
        self,
        base_url: str = "http://localhost:30000",
        api_key: str | None = None,
        timeout: float = 120.0,
    ):
        super().__init__(ProviderType.SGLANG, base_url, api_key, timeout)


def create_provider(
    provider_type: ProviderType,
    base_url: str | None = None,
    api_key: str | None = None,
) -> BaseProvider:
    """Factory function to create provider instances."""
    urls = {
        ProviderType.OLLAMA: "http://localhost:11434",
        ProviderType.LM_STUDIO: "http://localhost:1234",
        ProviderType.LLAMA_CPP: "http://localhost:8080",
        ProviderType.VLLM: "http://localhost:8000",
        ProviderType.SGLANG: "http://localhost:30000",
    }
    url = base_url or urls.get(provider_type, "http://localhost:11434")
    providers = {
        ProviderType.OLLAMA: OllamaProvider,
        ProviderType.LM_STUDIO: LMStudioProvider,
        ProviderType.LLAMA_CPP: LlamaCppProvider,
        ProviderType.VLLM: VLLMProvider,
        ProviderType.SGLANG: SGLangProvider,
    }
    provider_class = providers.get(provider_type, OllamaProvider)
    return provider_class(base_url=url, api_key=api_key)
