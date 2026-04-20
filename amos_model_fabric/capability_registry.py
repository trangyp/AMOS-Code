"""AMOS Model Fabric - Capability Registry

Tracks model capabilities for intelligent routing.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

UTC = timezone.utc
from pathlib import Path
from typing import Any, Optional

from .schemas import CapabilitySet, ModelCapability, ModelInfo, ProviderType

logger = logging.getLogger(__name__)


# Known model capability database
# Maps model name patterns to their capabilities
KNOWN_MODEL_CAPABILITIES: dict[str, CapabilitySet] = {
    # Qwen Coder models
    "qwen2.5-coder": CapabilitySet(
        capabilities={
            ModelCapability.CHAT,
            ModelCapability.CODE,
            ModelCapability.EDIT,
            ModelCapability.TOOL_USE,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.LONG_CONTEXT,
        },
        context_window=131072,
        max_output_tokens=8192,
        supports_streaming=True,
    ),
    "qwen2.5": CapabilitySet(
        capabilities={
            ModelCapability.CHAT,
            ModelCapability.CODE,
            ModelCapability.TOOL_USE,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.LONG_CONTEXT,
        },
        context_window=131072,
        max_output_tokens=8192,
        supports_streaming=True,
    ),
    # DeepSeek Coder
    "deepseek-coder": CapabilitySet(
        capabilities={
            ModelCapability.CHAT,
            ModelCapability.CODE,
            ModelCapability.EDIT,
            ModelCapability.AUTOCOMPLETE,
            ModelCapability.LONG_CONTEXT,
        },
        context_window=16384,
        max_output_tokens=4096,
        supports_streaming=True,
    ),
    # CodeLlama
    "codellama": CapabilitySet(
        capabilities={
            ModelCapability.CHAT,
            ModelCapability.CODE,
            ModelCapability.EDIT,
            ModelCapability.AUTOCOMPLETE,
            ModelCapability.LONG_CONTEXT,
        },
        context_window=16384,
        max_output_tokens=4096,
        supports_streaming=True,
    ),
    # Llama 3.x
    "llama3.3": CapabilitySet(
        capabilities={
            ModelCapability.CHAT,
            ModelCapability.CODE,
            ModelCapability.TOOL_USE,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.REASONING,
            ModelCapability.LONG_CONTEXT,
        },
        context_window=128000,
        max_output_tokens=4096,
        supports_streaming=True,
    ),
    "llama3.2": CapabilitySet(
        capabilities={
            ModelCapability.CHAT,
            ModelCapability.CODE,
            ModelCapability.VISION,
            ModelCapability.TOOL_USE,
            ModelCapability.FUNCTION_CALLING,
        },
        context_window=128000,
        max_output_tokens=4096,
        supports_streaming=True,
    ),
    "llama3.1": CapabilitySet(
        capabilities={
            ModelCapability.CHAT,
            ModelCapability.CODE,
            ModelCapability.TOOL_USE,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.LONG_CONTEXT,
        },
        context_window=128000,
        max_output_tokens=4096,
        supports_streaming=True,
    ),
    # Phi-4
    "phi4": CapabilitySet(
        capabilities={ModelCapability.CHAT, ModelCapability.CODE, ModelCapability.REASONING},
        context_window=16384,
        max_output_tokens=4096,
        supports_streaming=True,
    ),
    # Mistral/Codestral
    "codestral": CapabilitySet(
        capabilities={
            ModelCapability.CHAT,
            ModelCapability.CODE,
            ModelCapability.EDIT,
            ModelCapability.AUTOCOMPLETE,
            ModelCapability.FILL_IN_MIDDLE,
        },
        context_window=32768,
        max_output_tokens=4096,
        supports_streaming=True,
    ),
    # Embedding models
    "nomic-embed": CapabilitySet(
        capabilities={ModelCapability.EMBEDDINGS},
        context_window=8192,
        supports_streaming=False,
    ),
    "mxbai-embed": CapabilitySet(
        capabilities={ModelCapability.EMBEDDINGS},
        context_window=512,
        supports_streaming=False,
    ),
    "all-minilm": CapabilitySet(
        capabilities={ModelCapability.EMBEDDINGS},
        context_window=512,
        supports_streaming=False,
    ),
    "bge-": CapabilitySet(
        capabilities={ModelCapability.EMBEDDINGS, ModelCapability.RERANK},
        context_window=512,
        supports_streaming=False,
    ),
    # Vision models
    "llava": CapabilitySet(
        capabilities={ModelCapability.CHAT, ModelCapability.VISION},
        context_window=4096,
        supports_streaming=True,
    ),
    "bakllava": CapabilitySet(
        capabilities={ModelCapability.CHAT, ModelCapability.VISION},
        context_window=4096,
        supports_streaming=True,
    ),
}


class CapabilityRegistry:
    """Registry for tracking model capabilities."""

    def __init__(self, config_path: Optional[Path] = None):
        self._models: dict[str, ModelInfo] = {}
        self._by_capability: dict[ModelCapability, list[str]] = {c: [] for c in ModelCapability}
        self._by_provider: dict[ProviderType, list[str]] = {p: [] for p in ProviderType}
        self._config_path = config_path or Path.home() / ".amos" / "model_capabilities.json"
        self._load_config()

    def _load_config(self) -> None:
        """Load persisted model configurations."""
        if self._config_path.exists():
            try:
                data = json.loads(self._config_path.read_text())
                for model_data in data.get("models", []):
                    model_info = self._deserialize_model_info(model_data)
                    self._models[model_info.id] = model_info
                    self._index_model(model_info)
                logger.info(f"Loaded {len(self._models)} models from config")
            except Exception as e:
                logger.warning(f"Failed to load model config: {e}")

    def _save_config(self) -> None:
        """Persist model configurations."""
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            data = {"models": [self._serialize_model_info(m) for m in self._models.values()]}
            self._config_path.write_text(json.dumps(data, indent=2, default=str))
        except Exception as e:
            logger.warning(f"Failed to save model config: {e}")

    def _serialize_model_info(self, model: ModelInfo) -> dict[str, Any]:
        """Convert ModelInfo to dict."""
        return {
            "id": model.id,
            "name": model.name,
            "provider": model.provider.value,
            "provider_model_id": model.provider_model_id,
            "capabilities": {
                "capabilities": [c.name for c in model.capabilities.capabilities],
                "context_window": model.capabilities.context_window,
                "max_output_tokens": model.capabilities.max_output_tokens,
                "supports_streaming": model.capabilities.supports_streaming,
                "quantization": model.capabilities.quantization,
            },
            "priority": model.priority,
            "cost_per_1k_tokens": model.cost_per_1k_tokens,
            "endpoint_url": model.endpoint_url,
        }

    def _deserialize_model_info(self, data: dict[str, Any]) -> ModelInfo:
        """Convert dict to ModelInfo."""
        caps = data.get("capabilities", {})
        return ModelInfo(
            id=data["id"],
            name=data["name"],
            provider=ProviderType(data["provider"]),
            provider_model_id=data["provider_model_id"],
            capabilities=CapabilitySet(
                capabilities={ModelCapability[c] for c in caps.get("capabilities", [])},
                context_window=caps.get("context_window", 4096),
                max_output_tokens=caps.get("max_output_tokens", 4096),
                supports_streaming=caps.get("supports_streaming", True),
                quantization=caps.get("quantization"),
            ),
            priority=data.get("priority", 100),
            cost_per_1k_tokens=data.get("cost_per_1k_tokens", 0.0),
            endpoint_url=data.get("endpoint_url"),
        )

    def _index_model(self, model: ModelInfo) -> None:
        """Add model to capability and provider indexes."""
        # Index by capability
        for cap in model.capabilities.capabilities:
            if model.id not in self._by_capability[cap]:
                self._by_capability[cap].append(model.id)

        # Index by provider
        if model.id not in self._by_provider[model.provider]:
            self._by_provider[model.provider].append(model.id)

    def register_model(self, model: ModelInfo) -> None:
        """Register a model in the fabric."""
        self._models[model.id] = model
        self._index_model(model)
        self._save_config()
        logger.info(f"Registered model: {model.id} ({model.provider.value})")

    def unregister_model(self, model_id: str) -> None:
        """Remove a model from the fabric."""
        if model_id in self._models:
            model = self._models[model_id]

            # Remove from capability index
            for cap in model.capabilities.capabilities:
                if model_id in self._by_capability[cap]:
                    self._by_capability[cap].remove(model_id)

            # Remove from provider index
            if model_id in self._by_provider[model.provider]:
                self._by_provider[model.provider].remove(model_id)

            del self._models[model_id]
            self._save_config()
            logger.info(f"Unregistered model: {model_id}")

    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """Get model info by ID."""
        return self._models.get(model_id)

    def list_models(
        self,
        provider: Optional[ProviderType] = None,
        capability: Optional[ModelCapability] = None,
        available_only: bool = True,
    ) -> list[ModelInfo]:
        """List models matching criteria."""
        if capability:
            model_ids = self._by_capability.get(capability, [])
            models = [self._models[mid] for mid in model_ids]
        elif provider:
            model_ids = self._by_provider.get(provider, [])
            models = [self._models[mid] for mid in model_ids]
        else:
            models = list(self._models.values())

        if available_only:
            models = [m for m in models if m.is_available]

        return sorted(models, key=lambda m: m.priority)

    def find_models_with_capabilities(
        self,
        required: list[ModelCapability],
        preferred_provider: Optional[ProviderType] = None,
    ) -> list[ModelInfo]:
        """Find models that have all required capabilities."""
        if not required:
            return self.list_models()

        # Start with models that have the first required capability
        candidates = set(self._by_capability.get(required[0], []))

        # Intersect with models having each additional capability
        for cap in required[1:]:
            candidates &= set(self._by_capability.get(cap, []))

        models = [self._models[mid] for mid in candidates if mid in self._models]
        models = [m for m in models if m.is_available]

        if preferred_provider:
            # Sort by preferred provider first
            models.sort(key=lambda m: (0 if m.provider == preferred_provider else 1, m.priority))
        else:
            models.sort(key=lambda m: m.priority)

        return models

    def infer_capabilities(self, model_name: str) -> CapabilitySet:
        """Infer capabilities from model name."""
        model_name_lower = model_name.lower()

        # Check for exact matches first
        if model_name_lower in KNOWN_MODEL_CAPABILITIES:
            return KNOWN_MODEL_CAPABILITIES[model_name_lower]

        # Check for prefix matches
        for prefix, caps in KNOWN_MODEL_CAPABILITIES.items():
            if model_name_lower.startswith(prefix) or prefix in model_name_lower:
                return caps

        # Default: assume basic chat capability
        return CapabilitySet(
            capabilities={ModelCapability.CHAT},
            context_window=4096,
            max_output_tokens=4096,
            supports_streaming=True,
        )

    def update_model_health(self, model_id: str, is_available: bool, error: str = None) -> None:
        """Update model availability status."""
        if model_id in self._models:
            model = self._models[model_id]
            model.is_available = is_available
            model.last_health_check = datetime.now(UTC)
            if not is_available and error:
                model.error_count += 1
            self._save_config()


# Singleton registry instance
_registry: Optional[CapabilityRegistry] = None


def get_capability_registry() -> CapabilityRegistry:
    """Get the global capability registry."""
    global _registry
    if _registry is None:
        _registry = CapabilityRegistry()
    return _registry
