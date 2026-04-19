"""LLM Router for AMOS Platform - Centralized local model access.

Routes LLM requests to appropriate local backends (Ollama, LM Studio, vLLM, etc.)
This is the ONLY component that connects directly to local LLM providers.
"""

from __future__ import annotations

import asyncio
from enum import Enum
from typing import Any, AsyncIterator

import httpx


class LLMBackend(str, Enum):
    """Supported local LLM backends."""
    OLLAMA = "ollama"
    LM_STUDIO = "lmstudio"
    VLLM = "vllm"
    LLAMA_CPP = "llama_cpp"
    SGLANG = "sglang"
    LITELLM = "litellm"


class LLMRouter:
    """Route LLM requests to appropriate local backend.
    
    This is the ONLY place that connects directly to Ollama, LM Studio, etc.
    All frontend repos go through this router via AMOS-Consulting API.
    """
    
    DEFAULT_PORTS = {
        LLMBackend.OLLAMA: 11434,
        LLMBackend.LM_STUDIO: 1234,
        LLMBackend.VLLM: 8000,
        LLMBackend.LLAMA_CPP: 8080,
        LLMBackend.SGLANG: 30000,
        LLMBackend.LITELLM: 4000,
    }
    
    def __init__(self):
        self._backends: dict[LLMBackend, str] = {}
        self._client = httpx.AsyncClient(timeout=30.0)
        self._initialized = False
    
    async def initialize(self):
        """Auto-discover available local backends."""
        await self.discover_backends()
        self._initialized = True
    
    async def discover_backends(self) -> list[LLMBackend]:
        """Auto-discover available local backends."""
        available = []
        
        for backend, port in self.DEFAULT_PORTS.items():
            try:
                url = f"http://localhost:{port}"
                response = await self._client.get(f"{url}/health", timeout=2.0)
                if response.status_code == 200:
                    self._backends[backend] = url
                    available.append(backend)
            except Exception:
                pass
        
        return available
    
    async def list_models(self) -> list[dict[str, Any]]:
        """List models from all discovered backends."""
        models = []
        
        for backend, url in self._backends.items():
            try:
                backend_models = await self._list_for_backend(backend, url)
                models.extend(backend_models)
            except Exception:
                pass
        
        return models
    
    async def _list_for_backend(self, backend: LLMBackend, url: str) -> list[dict[str, Any]]:
        """List models for a specific backend."""
        if backend == LLMBackend.OLLAMA:
            resp = await self._client.get(f"{url}/api/tags")
            data = resp.json()
            return [
                {
                    "model_id": f"ollama/{m['name']}",
                    "name": m['name'],
                    "provider": "ollama",
                    "status": "available"
                }
                for m in data.get('models', [])
            ]
        elif backend in (LLMBackend.LM_STUDIO, LLMBackend.VLLM):
            resp = await self._client.get(f"{url}/v1/models")
            data = resp.json()
            return [
                {
                    "model_id": f"{backend.value}/{m['id']}",
                    "name": m['id'],
                    "provider": backend.value,
                    "status": "available"
                }
                for m in data.get('data', [])
            ]
        return []
    
    async def chat(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stream: bool = False
    ) -> dict[str, Any]:
        """Send chat request to appropriate backend."""
        parts = model.split("/", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid model format: {model}")
        
        provider, model_name = parts
        backend = LLMBackend(provider)
        backend_url = self._backends.get(backend)
        
        if not backend_url:
            raise ValueError(f"Backend {backend} not available")
        
        if backend == LLMBackend.OLLAMA:
            return await self._chat_ollama(backend_url, model_name, messages, temperature, max_tokens)
        elif backend in (LLMBackend.LM_STUDIO, LLMBackend.VLLM):
            return await self._chat_openai_compatible(backend_url, model_name, messages, temperature, max_tokens)
        
        raise ValueError(f"Unsupported backend: {backend}")
    
    async def _chat_ollama(
        self, url: str, model: str, messages: list[dict],
        temperature: float, max_tokens: int | None
    ) -> dict[str, Any]:
        """Chat with Ollama backend."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature}
        }
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        resp = await self._client.post(f"{url}/api/chat", json=payload)
        data = resp.json()
        
        return {
            "content": data.get("message", {}).get("content", ""),
            "usage": {
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
            },
            "finish_reason": "stop" if not data.get("done_reason") else data.get("done_reason")
        }
    
    async def _chat_openai_compatible(
        self, url: str, model: str, messages: list[dict],
        temperature: float, max_tokens: int | None
    ) -> dict[str, Any]:
        """Chat with OpenAI-compatible backend (LM Studio, vLLM)."""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": False
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        resp = await self._client.post(f"{url}/v1/chat/completions", json=payload)
        data = resp.json()
        
        choice = data.get("choices", [{}])[0]
        usage = data.get("usage", {})
        
        return {
            "content": choice.get("message", {}).get("content", ""),
            "usage": {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            },
            "finish_reason": choice.get("finish_reason", "stop")
        }
