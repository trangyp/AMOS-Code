"""LLM Provider Integrations for AMOS SuperBrain.

Supports multiple LLM providers with unified interface:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3, Claude 3.5)
- Kimi K2.5 (via Together AI or direct API)
- Ollama (local models)

State-of-the-art patterns from Anthropic's "Building Effective Agents" 2025.
"""

from __future__ import annotations


import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMResponse:
    """Standardized LLM response."""

    success: bool
    content: str
    model: str
    provider: str
    usage: dict[str, int] = None
    tool_calls: list[dict] = None
    error: str = None
    latency_ms: float = 0.0


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    def __init__(self, model_id: str, api_key: str = None):
        self.model_id = model_id
        self.api_key = api_key or os.environ.get(self._get_api_key_env())
        self._client = None

    @abstractmethod
    def _get_api_key_env(self) -> str:
        """Get environment variable name for API key."""
        pass

    @abstractmethod
    def _initialize_client(self) -> Any:
        """Initialize the API client."""
        pass

    @abstractmethod
    def query(
        self,
        prompt: str,
        system_prompt: str = None,
        tools: list[dict] = None,
        context: dict[str, Any] = None,
    ) -> LLMResponse:
        """Query the LLM."""
        pass

    def _build_messages(self, prompt: str, system_prompt: str = None) -> list[dict[str, str]]:
        """Build message list for API call."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider."""

    def _get_api_key_env(self) -> str:
        return "OPENAI_API_KEY"

    def _initialize_client(self) -> Any:
        try:
            import openai

            return openai.OpenAI(api_key=self.api_key)
        except ImportError:
            return None

    def query(
        self,
        prompt: str,
        system_prompt: str = None,
        tools: list[dict] = None,
        context: dict[str, Any] = None,
    ) -> LLMResponse:
        """Query OpenAI API."""
        import time

        start = time.time()

        try:
            if self._client is None:
                self._client = self._initialize_client()

            if self._client is None:
                return LLMResponse(
                    success=False,
                    content="",
                    model=self.model_id,
                    provider="openai",
                    error="OpenAI client not available (pip install openai)",
                )

            messages = self._build_messages(prompt, system_prompt)

            kwargs = {
                "model": self.model_id,
                "messages": messages,
            }

            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = self._client.chat.completions.create(**kwargs)

            latency = (time.time() - start) * 1000

            return LLMResponse(
                success=True,
                content=response.choices[0].message.content or "",
                model=self.model_id,
                provider="openai",
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
                if response.usage
                else None,
                tool_calls=[
                    {"name": tc.function.name, "arguments": json.loads(tc.function.arguments)}
                    for tc in (response.choices[0].message.tool_calls or [])
                ]
                if response.choices[0].message.tool_calls
                else None,
                latency_ms=latency,
            )

        except Exception as e:
            return LLMResponse(
                success=False, content="", model=self.model_id, provider="openai", error=str(e)
            )


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider."""

    def _get_api_key_env(self) -> str:
        return "ANTHROPIC_API_KEY"

    def _initialize_client(self) -> Any:
        try:
            import anthropic

            return anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            return None

    def query(
        self,
        prompt: str,
        system_prompt: str = None,
        tools: list[dict] = None,
        context: dict[str, Any] = None,
    ) -> LLMResponse:
        """Query Anthropic API."""
        import time

        start = time.time()

        try:
            if self._client is None:
                self._client = self._initialize_client()

            if self._client is None:
                return LLMResponse(
                    success=False,
                    content="",
                    model=self.model_id,
                    provider="anthropic",
                    error="Anthropic client not available (pip install anthropic)",
                )

            kwargs: dict[str, Any] = {
                "model": self.model_id,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            if tools:
                # Convert OpenAI format to Anthropic format
                anthropic_tools = []
                for tool in tools:
                    anthropic_tools.append(
                        {
                            "name": tool["function"]["name"],
                            "description": tool["function"]["description"],
                            "input_schema": tool["function"]["parameters"],
                        }
                    )
                kwargs["tools"] = anthropic_tools

            response = self._client.messages.create(**kwargs)

            latency = (time.time() - start) * 1000

            # Extract text content
            content = ""
            tool_calls = None

            for block in response.content:
                if block.type == "text":
                    content += block.text
                elif block.type == "tool_use":
                    if tool_calls is None:
                        tool_calls = []
                    tool_calls.append({"name": block.name, "arguments": block.input})

            return LLMResponse(
                success=True,
                content=content,
                model=self.model_id,
                provider="anthropic",
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                }
                if response.usage
                else None,
                tool_calls=tool_calls,
                latency_ms=latency,
            )

        except Exception as e:
            return LLMResponse(
                success=False, content="", model=self.model_id, provider="anthropic", error=str(e)
            )


class KimiProvider(BaseLLMProvider):
    """Kimi K2.5 provider (via Together AI or direct API)."""

    def _get_api_key_env(self) -> str:
        return "KIMI_API_KEY"

    def _initialize_client(self) -> Any:
        try:
            import openai

            # Kimi uses OpenAI-compatible API
            base_url = os.environ.get("KIMI_BASE_URL", "https://api.moonshot.cn/v1")
            return openai.OpenAI(api_key=self.api_key, base_url=base_url)
        except ImportError:
            return None

    def query(
        self,
        prompt: str,
        system_prompt: str = None,
        tools: list[dict] = None,
        context: dict[str, Any] = None,
    ) -> LLMResponse:
        """Query Kimi API."""
        import time

        start = time.time()

        try:
            if self._client is None:
                self._client = self._initialize_client()

            if self._client is None:
                return LLMResponse(
                    success=False,
                    content="",
                    model=self.model_id,
                    provider="kimi",
                    error="OpenAI client not available for Kimi (pip install openai)",
                )

            messages = self._build_messages(prompt, system_prompt)

            kwargs = {
                "model": self.model_id,
                "messages": messages,
            }

            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = self._client.chat.completions.create(**kwargs)

            latency = (time.time() - start) * 1000

            return LLMResponse(
                success=True,
                content=response.choices[0].message.content or "",
                model=self.model_id,
                provider="kimi",
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
                if response.usage
                else None,
                tool_calls=[
                    {"name": tc.function.name, "arguments": json.loads(tc.function.arguments)}
                    for tc in (response.choices[0].message.tool_calls or [])
                ]
                if response.choices[0].message.tool_calls
                else None,
                latency_ms=latency,
            )

        except Exception as e:
            return LLMResponse(
                success=False, content="", model=self.model_id, provider="kimi", error=str(e)
            )


class OllamaProvider(BaseLLMProvider):
    """Ollama local model provider."""

    def _get_api_key_env(self) -> str:
        return ""  # Ollama doesn't need API key

    def _initialize_client(self) -> Any:
        try:
            import ollama

            return ollama
        except ImportError:
            return None

    def query(
        self,
        prompt: str,
        system_prompt: str = None,
        tools: list[dict] = None,
        context: dict[str, Any] = None,
    ) -> LLMResponse:
        """Query Ollama API."""
        import time

        start = time.time()

        try:
            if self._client is None:
                self._client = self._initialize_client()

            if self._client is None:
                return LLMResponse(
                    success=False,
                    content="",
                    model=self.model_id,
                    provider="ollama",
                    error="Ollama client not available (pip install ollama)",
                )

            messages = self._build_messages(prompt, system_prompt)

            response = self._client.chat(model=self.model_id, messages=messages)

            latency = (time.time() - start) * 1000

            return LLMResponse(
                success=True,
                content=response.message.content,
                model=self.model_id,
                provider="ollama",
                latency_ms=latency,
            )

        except Exception as e:
            return LLMResponse(
                success=False, content="", model=self.model_id, provider="ollama", error=str(e)
            )


# Provider factory
PROVIDER_MAP: dict[str, type[BaseLLMProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "kimi": KimiProvider,
    "ollama": OllamaProvider,
}


def create_provider(provider: str, model_id: str, api_key: str = None) -> Optional[BaseLLMProvider]:
    """Create a provider instance."""
    provider_class = PROVIDER_MAP.get(provider)
    if provider_class:
        return provider_class(model_id, api_key)
    return None
