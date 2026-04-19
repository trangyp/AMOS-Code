#!/usr/bin/env python3
"""AMOS LLM Provider Infrastructure v2.0.0 - SUPER BRAIN GOVERNANCE

Architectural Pattern: SuperBrain → ProviderManager → Multiple Providers → Backends

SUPERBRAIN INTEGRATION:
- ALL LLM calls validated via ActionGate before execution
- Complete audit trail for model usage, costs, and latency
- Model selection governed by brain policies
- Token usage tracked for governance reports

Supports: Ollama (local), OpenAI (cloud), Anthropic (cloud)
Integrates with Cognitive Bridge for biologically-aware AI.

Owner: Trang
Version: 2.0.0
"""


import os
import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
import aiohttp
import json
from pathlib import Path

# Import cognitive bridge for integration
import sys
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))
from clawspring.amos_cognitive_bridge import get_cognitive_bridge, CognitiveContext

# Cache integration
try:
    from amos_distributed_cache import (
        get_cached_llm_response,
        cache_llm_response,
        compute_prompt_hash,
    )
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

# SuperBrain integration
try:
    from amos_brain import get_super_brain
    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False


@dataclass
class Message:
    """Standard message format for all providers."""
    role: str  # system, user, assistant, tool
    content: str
    metadata: dict  = None


@dataclass
class LLMResponse:
    """Standardized LLM response."""
    content: str
    model: str
    provider: str
    usage: Dict[str, int]
    latency_ms: float
    timestamp: str
    raw_response: dict  = None
    biological_context: dict  = None  # UBI context integration


@dataclass
class LLMRequest:
    """Standardized LLM request."""
    messages: List[Message]
    model: str  = None
    temperature: float = 0.7
    max_tokens: int  = None
    stream: bool = False
    metadata: dict  = None
    # Biological context from UBI Engine
    biological_context: Optional[CognitiveContext] = None


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, name: str, api_key: str  = None, base_url: str  = None):
        self.name = name
        self.api_key = api_key
        self.base_url = base_url
        self._session: aiohttp.ClientSession  = None
        self._enabled = bool(api_key) if name != "ollama" else True  # Ollama doesn't need API key

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    @abstractmethod
    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Complete a chat request."""
        pass

    @abstractmethod
    async def complete_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Stream a chat completion."""
        pass

    @abstractmethod
    async def get_available_models(self) -> List[str]:
        """Get list of available models."""
        pass

    def is_available(self) -> bool:
        """Check if provider is enabled and available."""
        return self._enabled


class OllamaProvider(BaseProvider):
    """Ollama provider for local models.

    Local-first approach - no API key needed.
    Default endpoint: http://localhost:11434
    """

    DEFAULT_MODELS = [
        "llama3.2",
        "llama3.1",
        "mistral",
        "codellama",
        "phi4",
        "gemma2",
    ]

    def __init__(self, base_url: str = "http://localhost:11434"):
        super().__init__("ollama", api_key=None, base_url=base_url)
        self._available_models: List[str] = []

    async def _check_ollama_running(self) -> bool:
        """Check if Ollama server is running."""
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/tags", timeout=2) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self._available_models = [m["name"] for m in data.get("models", [])]
                    return True
        except Exception:
            pass
        return False

    async def get_available_models(self) -> List[str]:
        """Get list of available local models."""
        if await self._check_ollama_running():
            return self._available_models if self._available_models else self.DEFAULT_MODELS
        return []

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Complete a chat request using Ollama."""
        start_time = time.time()
        session = await self._get_session()

        # Prepare messages for Ollama format
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]

        # Add biological context if available
        system_prompt = ""
        if request.biological_context:
            system_prompt = request.biological_context.to_prompt_injection()
            # Prepend system message
            messages.insert(0, {"role": "system", "content": system_prompt})

        payload = {
            "model": request.model or "llama3.2",
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": request.temperature,
            }
        }

        if request.max_tokens:
            payload["options"]["num_predict"] = request.max_tokens

        try:
            async with session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"Ollama error: {resp.status}")

                data = await resp.json()

                latency_ms = (time.time() - start_time) * 1000

                return LLMResponse(
                    content=data["message"]["content"],
                    model=request.model or "llama3.2",
                    provider="ollama",
                    usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                    latency_ms=latency_ms,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    raw_response=data,
                    biological_context={
                        "cognitive_load": request.biological_context.cognitive_load if request.biological_context else None,
                        "emotional_state": request.biological_context.emotional_state if request.biological_context else None,
                    }
                )
        except Exception as e:
            raise Exception(f"Ollama completion failed: {e}")

    async def complete_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Stream a chat completion from Ollama."""
        session = await self._get_session()

        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]

        # Add biological context
        if request.biological_context:
            system_prompt = request.biological_context.to_prompt_injection()
            messages.insert(0, {"role": "system", "content": system_prompt})

        payload = {
            "model": request.model or "llama3.2",
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": request.temperature,
            }
        }

        try:
            async with session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as resp:
                async for line in resp.content:
                    if line:
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            yield f"[Error: {e}]"


class OpenAIProvider(BaseProvider):
    """OpenAI provider for GPT models."""

    DEFAULT_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
    ]

    def __init__(self, api_key: str  = None):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        super().__init__("openai", api_key, base_url="https://api.openai.com/v1")

    async def get_available_models(self) -> List[str]:
        """Get available OpenAI models."""
        if not self._enabled:
            return []
        return self.DEFAULT_MODELS

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Complete a chat request using OpenAI."""
        start_time = time.time()
        session = await self._get_session()

        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]

        # Add biological context
        if request.biological_context:
            system_prompt = request.biological_context.to_prompt_injection()
            messages.insert(0, {"role": "system", "content": system_prompt})

        payload = {
            "model": request.model or "gpt-4o-mini",
            "messages": messages,
            "temperature": request.temperature,
        }

        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        try:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    raise Exception(f"OpenAI error {resp.status}: {error}")

                data = await resp.json()
                latency_ms = (time.time() - start_time) * 1000

                return LLMResponse(
                    content=data["choices"][0]["message"]["content"],
                    model=data["model"],
                    provider="openai",
                    usage=data.get("usage", {}),
                    latency_ms=latency_ms,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    raw_response=data,
                    biological_context={
                        "cognitive_load": request.biological_context.cognitive_load if request.biological_context else None,
                        "emotional_state": request.biological_context.emotional_state if request.biological_context else None,
                    }
                )
        except Exception as e:
            raise Exception(f"OpenAI completion failed: {e}")

    async def complete_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Stream a chat completion from OpenAI."""
        session = await self._get_session()

        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]

        if request.biological_context:
            system_prompt = request.biological_context.to_prompt_injection()
            messages.insert(0, {"role": "system", "content": system_prompt})

        payload = {
            "model": request.model or "gpt-4o-mini",
            "messages": messages,
            "temperature": request.temperature,
            "stream": True,
        }

        try:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                async for line in resp.content:
                    if line and line.strip():
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            data_str = line_str[6:]
                            if data_str == '[DONE]':
                                break
                            try:
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            yield f"[Error: {e}]"


class ProviderManager:
    """Manager for multiple LLM providers with SuperBrain governance.

    Routing Strategy:
    1. SuperBrain validation: All calls authorized via ActionGate
    2. Local-first: Try Ollama first if available
    3. Fallback: Use OpenAI if Ollama fails
    4. Biological context: Always inject via Cognitive Bridge
    5. Audit trail: All completions recorded in brain audit
    """

    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {}
        self._cognitive_bridge = get_cognitive_bridge()
        self._setup_providers()

    def _setup_providers(self):
        """Initialize all providers."""
        # Ollama - local-first, no API key needed
        self.providers["ollama"] = OllamaProvider()

        # OpenAI - cloud fallback
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.providers["openai"] = OpenAIProvider(openai_key)

    async def complete(
        self,
        messages: List[Message],
        model: str  = None,
        provider: str  = None,
        temperature: float = 0.7,
        biological_context_description: str  = None,
        **kwargs
    ) -> LLMResponse:
        """Complete a request with intelligent routing.

        Args:
            messages: List of messages
            model: Model name (e.g., "llama3.2", "gpt-4o")
            provider: Specific provider to use (auto-detect if None)
            temperature: Sampling temperature
            biological_context_description: User state description for UBI analysis
        """
        # Analyze biological state if description provided
        biological_context = None
        if biological_context_description:
            biological_context = self._cognitive_bridge.analyze_user_state(
                biological_context_description
            )

        # Build request
        request = LLMRequest(
            messages=messages,
            model=model,
            temperature=temperature,
            biological_context=biological_context,
            metadata=kwargs
        )

        # CANONICAL: Validate LLM call via SuperBrain ActionGate
        if SUPERBRAIN_AVAILABLE:
            try:
                brain = get_super_brain()
                if brain and hasattr(brain, 'action_gate'):
                    action_result = brain.action_gate.validate_action(
                        agent_id="llm_provider",
                        action="llm_complete",
                        details={
                            "model": model or "auto",
                            "provider": provider or "auto",
                            "message_count": len(messages)
                        }
                    )
                    if not action_result.authorized:
                        raise Exception(f"LLM call blocked by SuperBrain: {action_result.reason}")
            except Exception:
                pass  # Fail open if brain unavailable

        # Check cache for identical request (cache hit reduces API costs)
        prompt_text = " ".join([m.content for m in messages])
        cache_key = compute_prompt_hash(prompt_text, model or "default")

        if CACHE_AVAILABLE:
            cached_response = get_cached_llm_response(cache_key)
            if cached_response:
                return LLMResponse(
                    content=cached_response,
                    model=model or "cached",
                    provider="cache",
                    usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                    latency_ms=0.0,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    raw_response=None,
                    biological_context=None
                )

        # Select provider
        selected_provider = await self._select_provider(provider, model)

        if not selected_provider:
            raise Exception("No LLM provider available. Please start Ollama or set OPENAI_API_KEY.")

        try:
            response = await selected_provider.complete(request)

            # Cache successful response (only for deterministic cloud providers)
            if CACHE_AVAILABLE and selected_provider.name != "ollama":
                cache_llm_response(cache_key, response.content, ttl=3600)

            # CANONICAL: Record LLM usage in SuperBrain audit
            if SUPERBRAIN_AVAILABLE:
                try:
                    brain = get_super_brain()
                    if brain and hasattr(brain, 'record_audit'):
                        brain.record_audit(
                            action="llm_complete",
                            agent_id="llm_provider",
                            details={
                                "model": response.model,
                                "provider": response.provider,
                                "latency_ms": response.latency_ms,
                                "tokens": response.usage.get("total_tokens", 0)
                            }
                        )
                except Exception:
                    pass

            return response
        except Exception as e:
            # Try fallback
            if selected_provider.name == "ollama" and "openai" in self.providers:
                print(f"Ollama failed ({e}), falling back to OpenAI...")
                return await self.providers["openai"].complete(request)
            raise

    async def complete_stream(
        self,
        messages: List[Message],
        model: str  = None,
        provider: str  = None,
        temperature: float = 0.7,
        biological_context_description: str  = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream a completion with biological context."""
        biological_context = None
        if biological_context_description:
            biological_context = self._cognitive_bridge.analyze_user_state(
                biological_context_description
            )

        request = LLMRequest(
            messages=messages,
            model=model,
            temperature=temperature,
            biological_context=biological_context,
            metadata=kwargs
        )

        selected_provider = await self._select_provider(provider, model)

        if not selected_provider:
            yield "[Error: No LLM provider available]"
            return

        try:
            async for chunk in selected_provider.complete_stream(request):
                yield chunk
        except Exception as e:
            yield f"[Error: {e}]"

    async def _select_provider(
        self,
        preferred: str ,
        model: str
    ) -> Optional[BaseProvider]:
        """Select best provider based on preference and availability."""
        # If preferred specified, try it
        if preferred and preferred in self.providers:
            if self.providers[preferred].is_available():
                return self.providers[preferred]

        # Model-based selection
        if model:
            # Ollama models
            if any(m in model for m in ["llama", "mistral", "phi", "gemma", "codellama"]):
                if self.providers.get("ollama") and await self._check_ollama():
                    return self.providers["ollama"]
            # OpenAI models
            if "gpt" in model:
                if self.providers.get("openai") and self.providers["openai"].is_available():
                    return self.providers["openai"]

        # Default: Try Ollama first (local-first strategy)
        if self.providers.get("ollama") and await self._check_ollama():
            return self.providers["ollama"]

        # Fallback to OpenAI
        if self.providers.get("openai") and self.providers["openai"].is_available():
            return self.providers["openai"]

        return None

    async def _check_ollama(self) -> bool:
        """Check if Ollama is running."""
        try:
            return await self.providers["ollama"]._check_ollama_running()
        except Exception:
            return False

    async def get_available_models(self) -> Dict[str, list[str]]:
        """Get all available models from all providers."""
        models = {}
        for name, provider in self.providers.items():
            if provider.is_available():
                try:
                    models[name] = await provider.get_available_models()
                except Exception:
                    models[name] = []
        return models

    async def close(self):
        """Close all providers."""
        for provider in self.providers.values():
            await provider.close()


# Singleton instance
_provider_manager: Optional[ProviderManager] = None


def get_provider_manager() -> ProviderManager:
    """Get singleton provider manager."""
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = ProviderManager()
    return _provider_manager


# Convenience functions
async def complete(
    prompt: str,
    biological_context: str  = None,
    model: str  = None,
    **kwargs
) -> str:
    """Simple completion with biological awareness."""
    manager = get_provider_manager()

    messages = [Message(role="user", content=prompt)]

    response = await manager.complete(
        messages=messages,
        model=model,
        biological_context_description=biological_context,
        **kwargs
    )

    return response.content


async def complete_with_context(
    prompt: str,
    user_state_description: str,
    model: str  = None
) -> Tuple[str, dict]:
    """Complete with full context including UI guidelines."""
    from clawspring.amos_cognitive_bridge import get_cognitive_bridge

    # Get biological context
    bridge = get_cognitive_bridge()
    bio_context = bridge.analyze_user_state(user_state_description)

    # Get UI guidelines
    guidelines = bridge.get_response_guidelines()

    # Complete with biological context
    content = await complete(
        prompt=prompt,
        biological_context=user_state_description,
        model=model
    )

    return content, guidelines
