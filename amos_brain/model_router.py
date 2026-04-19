#!/usr/bin/env python3
"""ModelRouter - Canonical Model Routing and Lifecycle Management.

All model calls must pass through this router.
Provides unified interface for local and remote models via Model Fabric Gateway.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from threading import Lock
from typing import Any

# Import Model Fabric Gateway
from amos_model_fabric import ModelFabricGateway, get_gateway
from amos_model_fabric.schemas import FabricRequest


@dataclass
class ModelConfig:
    """Configuration for a model."""

    model_id: str
    provider: str  # e.g., "ollama", "openai", "local"
    endpoint: str = None
    api_key: str = None
    priority: int = 0
    healthy: bool = True


class ModelRouter:
    """Canonical router for all model queries.

    Manages model lifecycle, fallback chains, and routing decisions.
    All model calls in the SuperBrain go through this router.
    Integrates with Model Fabric Gateway for real provider calls.
    """

    def __init__(self, memory_governance: Any):
        self._memory_governance = memory_governance
        self._models: dict[str, ModelConfig] = {}
        self._lock = Lock()
        self._query_count = 0
        self._fabric_gateway: Optional[ModelFabricGateway] = None
        self._initialized = False

    def _ensure_gateway(self) -> ModelFabricGateway:
        """Ensure Model Fabric Gateway is initialized."""
        if self._fabric_gateway is None:
            self._fabric_gateway = get_gateway()
            if not self._initialized:
                # Initialize in background
                try:
                    asyncio.run(self._fabric_gateway.initialize())
                    self._initialized = True
                except Exception as e:
                    print(f"Warning: Could not initialize Model Fabric Gateway: {e}")
        return self._fabric_gateway

    def register_model(self, config: ModelConfig) -> bool:
        """Register a model with the router.

        Args:
            config: Model configuration

        Returns:
            True if registration successful
        """
        with self._lock:
            self._models[config.model_id] = config
            return True

    def query(self, model_id: str, prompt: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """Query a model through canonical path.

        Args:
            model_id: Model identifier
            prompt: Prompt text
            context: Optional context

        Returns:
            Model response
        """
        context = context or {}

        with self._lock:
            model = self._models.get(model_id)

        if not model:
            return {"success": False, "error": f"Model '{model_id}' not registered"}

        if not model.healthy:
            return {"success": False, "error": f"Model '{model_id}' is not healthy"}

        # Route through Model Fabric Gateway
        try:
            self._query_count += 1
            gateway = self._ensure_gateway()

            # Build FabricRequest
            request = FabricRequest(
                messages=[{"role": "user", "content": prompt}],
                model=model_id,
                temperature=context.get("temperature", 0.7),
                max_tokens=context.get("max_tokens"),
                stream=False,
            )

            # Execute through gateway
            response = asyncio.run(gateway.complete(request))

            return {
                "success": response.finish_reason != "error",
                "model": response.model,
                "response": response.content,
                "provider": response.provider.value,
                "latency_ms": response.latency_ms,
                "error": response.error if hasattr(response, "error") else None,
            }

        except Exception as e:
            return {"success": False, "error": f"Query failed: {str(e)}"}

    def query_stream(self, model_id: str, prompt: str, context: dict[str, Any] = None):
        """Stream query a model through canonical path.

        Args:
            model_id: Model identifier
            prompt: Prompt text
            context: Optional context

        Yields:
            Stream chunks from model
        """
        context = context or {}

        with self._lock:
            model = self._models.get(model_id)

        if not model:
            yield {"error": f"Model '{model_id}' not registered"}
            return

        try:
            gateway = self._ensure_gateway()

            request = FabricRequest(
                messages=[{"role": "user", "content": prompt}],
                model=model_id,
                temperature=context.get("temperature", 0.7),
                max_tokens=context.get("max_tokens"),
                stream=True,
            )

            # Stream through gateway
            for chunk in asyncio.run(gateway.complete_stream(request)):
                yield {
                    "content": chunk.content,
                    "model": chunk.model,
                    "provider": chunk.provider.value,
                    "finished": chunk.is_finished,
                }

        except Exception as e:
            yield {"error": f"Stream failed: {str(e)}"}

    def list_models(self) -> list[str]:
        """List all registered model IDs."""
        with self._lock:
            return list(self._models.keys())

    def list_available_models(self) -> list[dict[str, Any]]:
        """List all available models from Model Fabric Gateway."""
        try:
            gateway = self._ensure_gateway()
            models = gateway.list_available_models()
            return [
                {
                    "id": m.id,
                    "name": m.name,
                    "provider": m.provider.value,
                    "available": m.is_available,
                    "capabilities": [c.name for c in m.capabilities.capabilities],
                }
                for m in models
            ]
        except Exception as e:
            return [{"error": str(e)}]

    def is_healthy(self) -> bool:
        """Check if ModelRouter is healthy."""
        return len(self._models) > 0

    def get_metrics(self) -> dict[str, Any]:
        """Get router metrics."""
        return {
            "query_count": self._query_count,
            "registered_models": len(self._models),
            "fabric_initialized": self._initialized,
        }

    def shutdown(self) -> None:
        """Graceful shutdown."""
        if self._fabric_gateway:
            asyncio.run(self._fabric_gateway.close())
