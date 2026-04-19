"""AMOS LLM Provider System

Multi-provider LLM abstraction layer supporting OpenAI, Anthropic, and other providers.
Implements intelligent routing and fallback mechanisms.

Creator: Trang Phan
Version: 3.0.0
"""

import asyncio
import json
import os
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import datetime, timezone

UTC = timezone.utc
from typing import Any, Dict, List

import aiohttp


@dataclass
class Message:
    """Standard message format for all providers."""

    role: str  # system, user, assistant, tool
    content: str
    metadata: dict = None


@dataclass
class LLMResponse:
    """Standardized LLM response."""

    content: str
    model: str
    provider: str
    usage: Dict[str, int]
    latency_ms: float
    timestamp: str
    raw_response: dict = None


@dataclass
class LLMRequest:
    """Standardized LLM request."""

    messages: List[Message]
    model: str = None
    temperature: float = 0.7
    max_tokens: int = None
    stream: bool = False
    metadata: dict = None


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, name: str, api_key: str = None):
        self.name = name
        self.api_key = api_key
        self._session: aiohttp.ClientSession = None
        self._enabled = bool(api_key)

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    @abstractmethod
    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Complete a chat request."""
        pass

    @abstractmethod
    async def complete_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Stream a chat completion."""
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        pass

    def is_enabled(self) -> bool:
        """Check if provider is enabled."""
        return self._enabled

    async def close(self):
        """Close provider connections."""
        if self._session and not self._session.closed:
            await self._session.close()


class OpenAIProvider(BaseProvider):
    """OpenAI GPT provider."""

    API_BASE = "https://api.openai.com/v1"
    DEFAULT_MODEL = "gpt-4o"

    AVAILABLE_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    ]

    def __init__(self, api_key: str = None):
        super().__init__("openai", api_key or os.getenv("OPENAI_API_KEY"))

    def get_available_models(self) -> List[str]:
        return self.AVAILABLE_MODELS if self.is_enabled() else []

    async def complete(self, request: LLMRequest) -> LLMResponse:
        if not self.is_enabled():
            raise RuntimeError("OpenAI provider not enabled")

        start_time = datetime.now(UTC)
        session = await self._get_session()

        model = request.model or self.DEFAULT_MODEL

        payload = {
            "model": model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "temperature": request.temperature,
            "stream": False,
        }

        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with session.post(
            f"{self.API_BASE}/chat/completions", headers=headers, json=payload
        ) as response:
            data = await response.json()

            if response.status != 200:
                raise RuntimeError(f"OpenAI API error: {data}")

            latency = (datetime.now(UTC) - start_time).total_seconds() * 1000

            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=model,
                provider="openai",
                usage=data.get("usage", {"prompt_tokens": 0, "completion_tokens": 0}),
                latency_ms=latency,
                timestamp=datetime.now(UTC).isoformat(),
                raw_response=data,
            )

    async def complete_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        if not self.is_enabled():
            raise RuntimeError("OpenAI provider not enabled")

        session = await self._get_session()
        model = request.model or self.DEFAULT_MODEL

        payload = {
            "model": model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "temperature": request.temperature,
            "stream": True,
        }

        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with session.post(
            f"{self.API_BASE}/chat/completions", headers=headers, json=payload
        ) as response:
            async for line in response.content:
                line = line.decode("utf-8").strip()
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        if "choices" in chunk and chunk["choices"]:
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                    except json.JSONDecodeError:
                        continue


class AnthropicProvider(BaseProvider):
    """Anthropic Claude provider."""

    API_BASE = "https://api.anthropic.com/v1"
    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"

    AVAILABLE_MODELS = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]

    def __init__(self, api_key: str = None):
        super().__init__("anthropic", api_key or os.getenv("ANTHROPIC_API_KEY"))

    def get_available_models(self) -> List[str]:
        return self.AVAILABLE_MODELS if self.is_enabled() else []

    async def complete(self, request: LLMRequest) -> LLMResponse:
        if not self.is_enabled():
            raise RuntimeError("Anthropic provider not enabled")

        start_time = datetime.now(UTC)
        session = await self._get_session()

        model = request.model or self.DEFAULT_MODEL

        # Separate system message from other messages
        system_msg = None
        messages = []

        for msg in request.messages:
            if msg.role == "system":
                system_msg = msg.content
            else:
                messages.append(
                    {
                        "role": msg.role if msg.role != "assistant" else "assistant",
                        "content": msg.content,
                    }
                )

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": request.max_tokens or 4096,
        }

        if system_msg:
            payload["system"] = system_msg

        if request.temperature != 0.7:
            payload["temperature"] = request.temperature

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        async with session.post(
            f"{self.API_BASE}/messages", headers=headers, json=payload
        ) as response:
            data = await response.json()

            if response.status != 200:
                raise RuntimeError(f"Anthropic API error: {data}")

            latency = (datetime.now(UTC) - start_time).total_seconds() * 1000

            content = ""
            if "content" in data and data["content"]:
                # Anthropic returns a list of content blocks
                for block in data["content"]:
                    if block.get("type") == "text":
                        content += block.get("text", "")

            return LLMResponse(
                content=content,
                model=model,
                provider="anthropic",
                usage={
                    "prompt_tokens": data.get("usage", {}).get("input_tokens", 0),
                    "completion_tokens": data.get("usage", {}).get("output_tokens", 0),
                },
                latency_ms=latency,
                timestamp=datetime.now(UTC).isoformat(),
                raw_response=data,
            )

    async def complete_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        # Streaming implementation for Anthropic
        if not self.is_enabled():
            raise RuntimeError("Anthropic provider not enabled")

        session = await self._get_session()
        model = request.model or self.DEFAULT_MODEL

        system_msg = None
        messages = []

        for msg in request.messages:
            if msg.role == "system":
                system_msg = msg.content
            else:
                messages.append(
                    {
                        "role": msg.role if msg.role != "assistant" else "assistant",
                        "content": msg.content,
                    }
                )

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": request.max_tokens or 4096,
            "stream": True,
        }

        if system_msg:
            payload["system"] = system_msg

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        async with session.post(
            f"{self.API_BASE}/messages", headers=headers, json=payload
        ) as response:
            async for line in response.content:
                line = line.decode("utf-8").strip()
                if line.startswith("data: "):
                    data = line[6:]
                    try:
                        chunk = json.loads(data)
                        if chunk.get("type") == "content_block_delta":
                            delta = chunk.get("delta", {})
                            if "text" in delta:
                                yield delta["text"]
                    except json.JSONDecodeError:
                        continue


class MockProvider(BaseProvider):
    """Mock provider for testing without API keys."""

    DEFAULT_MODEL = "mock-gpt"

    def __init__(self):
        super().__init__("mock", "mock-key")
        self._enabled = True  # Always enabled for fallback

    def get_available_models(self) -> List[str]:
        return ["mock-gpt", "mock-claude"]

    async def complete(self, request: LLMRequest) -> LLMResponse:
        await asyncio.sleep(0.5)  # Simulate latency

        # Generate mock response based on last user message
        last_user_msg = None
        for msg in reversed(request.messages):
            if msg.role == "user":
                last_user_msg = msg.content
                break

        mock_response = self._generate_mock_response(last_user_msg or "Hello")

        return LLMResponse(
            content=mock_response,
            model=request.model or self.DEFAULT_MODEL,
            provider="mock",
            usage={"prompt_tokens": 10, "completion_tokens": 50},
            latency_ms=500,
            timestamp=datetime.now(UTC).isoformat(),
        )

    async def complete_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        response = await self.complete(request)
        words = response.content.split()
        for word in words:
            yield word + " "
            await asyncio.sleep(0.05)

    def _generate_mock_response(self, user_message: str) -> str:
        """Generate a context-aware mock response."""
        lower_msg = user_message.lower()

        if "hello" in lower_msg or "hi" in lower_msg:
            return (
                "Hello! I'm a mock AI assistant running in AMOS. I can help you with various tasks."
            )
        elif "code" in lower_msg or "programming" in lower_msg:
            return "I can help you with coding! Here's a simple Python example:\n\n```python\ndef hello():\n    print('Hello, World!')\n```"
        elif "help" in lower_msg:
            return "I'm here to help! I can assist with coding, analysis, writing, and many other tasks. What would you like to work on?"
        else:
            return f"I received your message: '{user_message}'. This is a mock response since the real LLM providers are not configured. To enable real AI capabilities, please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables."


class OllamaProvider(BaseProvider):
    """Ollama provider for local/offline LLMs."""

    API_BASE = "http://localhost:11434"
    DEFAULT_MODEL = "llama3.2"

    POPULAR_MODELS = [
        "llama3.3",
        "llama3.2",
        "llama3.1",
        "mistral",
        "qwen2.5",
        "gemma2",
        "phi4",
        "deepseek-r1",
        "codellama",
        "mixtral",
    ]

    def __init__(self, base_url: str = None):
        super().__init__("ollama", "local")
        self.base_url = base_url or os.getenv("OLLAMA_HOST", self.API_BASE)
        self._available_models: List[str] = []
        self._check_connection()

    def _check_connection(self):
        """Check if Ollama is running."""
        try:
            import urllib.request

            urllib.request.urlopen(f"{self.base_url}/api/tags", timeout=2)
            self._enabled = True
        except Exception:
            self._enabled = False

    async def _get_available_models_from_ollama(self) -> List[str]:
        """Fetch actually downloaded models from Ollama."""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [m["name"] for m in data.get("models", [])]
                    return models
        except Exception:
            pass
        return []

    def get_available_models(self) -> List[str]:
        """Return popular models (actual availability checked at runtime)."""
        if not self.is_enabled():
            return []
        return self.POPULAR_MODELS

    async def complete(self, request: LLMRequest) -> LLMResponse:
        if not self.is_enabled():
            raise RuntimeError("Ollama not available. Is it running?")

        start_time = datetime.now(UTC)
        session = await self._get_session()

        model = request.model or self.DEFAULT_MODEL

        # Convert messages to Ollama format
        messages = []
        system_msg = None

        for msg in request.messages:
            if msg.role == "system":
                system_msg = msg.content
            else:
                messages.append({"role": msg.role, "content": msg.content})

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": request.temperature,
            },
        }

        if system_msg:
            payload["system"] = system_msg

        if request.max_tokens:
            payload["options"]["num_predict"] = request.max_tokens

        async with session.post(f"{self.base_url}/api/chat", json=payload) as response:
            data = await response.json()

            if response.status != 200:
                raise RuntimeError(f"Ollama error: {data}")

            latency = (datetime.now(UTC) - start_time).total_seconds() * 1000

            return LLMResponse(
                content=data["message"]["content"],
                model=model,
                provider="ollama",
                usage=data.get("usage")
                or (
                    {
                        "prompt_tokens": data.get("prompt_eval_count", 0),
                        "completion_tokens": data.get("eval_count", 0),
                    }
                ),
                latency_ms=latency,
                timestamp=datetime.now(UTC).isoformat(),
                raw_response=data,
            )

    async def complete_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        if not self.is_enabled():
            raise RuntimeError("Ollama not available")

        session = await self._get_session()
        model = request.model or self.DEFAULT_MODEL

        messages = []
        system_msg = None

        for msg in request.messages:
            if msg.role == "system":
                system_msg = msg.content
            else:
                messages.append({"role": msg.role, "content": msg.content})

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {"temperature": request.temperature},
        }

        if system_msg:
            payload["system"] = system_msg

        async with session.post(f"{self.base_url}/api/chat", json=payload) as response:
            async for line in response.content:
                line = line.decode("utf-8").strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if "message" in data and "content" in data["message"]:
                        yield data["message"]["content"]
                except json.JSONDecodeError:
                    continue


class LLMRouter:
    """
    Intelligent LLM router that selects the best provider and model for each request.
    Implements fallback mechanisms and performance tracking.
    """

    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {}
        self._performance_tracker: Dict[str, list[float]] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize all available providers."""
        # Try to initialize local/offline provider first (Ollama)
        ollama = OllamaProvider()
        if ollama.is_enabled():
            self._providers["ollama"] = ollama
            print("[LLMRouter] Ollama local provider enabled - using downloaded LLMs")

        # Try to initialize cloud providers
        openai = OpenAIProvider()
        if openai.is_enabled():
            self._providers["openai"] = openai
            print("[LLMRouter] OpenAI provider enabled")

        anthropic = AnthropicProvider()
        if anthropic.is_enabled():
            self._providers["anthropic"] = anthropic
            print("[LLMRouter] Anthropic provider enabled")

        # Add mock provider as ultimate fallback
        if not self._providers:
            self._providers["mock"] = MockProvider()
            print("[LLMRouter] Using mock provider (no local or cloud providers available)")

    async def route_request(self, request: LLMRequest, preference: str = None) -> LLMResponse:
        """
        Route request to the best available provider.

        Args:
            request: The LLM request
            preference: Optional provider preference (openai, anthropic, etc.)

        Returns:
            LLM response from the selected provider
        """
        # If preference specified and available, use it
        if preference and preference in self._providers:
            provider = self._providers[preference]
            if provider.is_enabled():
                return await provider.complete(request)

        # Otherwise, use smart routing
        provider = self._select_best_provider(request)
        return await provider.complete(request)

    async def route_stream(
        self, request: LLMRequest, preference: str = None
    ) -> AsyncGenerator[str, None]:
        """Route streaming request to best provider."""
        if preference and preference in self._providers:
            provider = self._providers[preference]
            if provider.is_enabled():
                async for chunk in provider.complete_stream(request):
                    yield chunk
                return

        provider = self._select_best_provider(request)
        async for chunk in provider.complete_stream(request):
            yield chunk

    def _select_best_provider(self, request: LLMRequest) -> BaseProvider:
        """Select the best provider based on request characteristics."""
        enabled_providers = [p for p in self._providers.values() if p.is_enabled()]

        if not enabled_providers:
            raise RuntimeError("No LLM providers available")

        # Prefer local Ollama for privacy/cost if available
        if "ollama" in self._providers and self._providers["ollama"].is_enabled():
            return self._providers["ollama"]

        # Prefer other real providers (non-mock)
        real_providers = [p for p in enabled_providers if p.name not in ("mock", "ollama")]
        if real_providers:
            return real_providers[0]

        # Fall back to mock
        return enabled_providers[0]

    def get_available_providers(self) -> List[dict]:
        """Get list of available providers with their models."""
        result = []
        for name, provider in self._providers.items():
            if provider.is_enabled():
                result.append(
                    {
                        "name": name,
                        "models": provider.get_available_models(),
                        "enabled": True,
                    }
                )
        return result

    async def close_all(self):
        """Close all provider connections."""
        for provider in self._providers.values():
            await provider.close()


# Global router instance
llm_router = LLMRouter()
