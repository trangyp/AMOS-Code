"""AMOS Local Model Fabric

Unified offline-first model gateway supporting:
- Ollama-native protocol
- OpenAI-compatible endpoints (LM Studio, vLLM, SGLang, llama.cpp)
- Anthropic-compatible endpoints
- Direct GGUF execution

Creator: Trang Phan
Version: 1.0.0
"""

from .capability_registry import CapabilityRegistry, ModelCapability, get_capability_registry
from .gateway import LiteLLMRouter, ModelFabricGateway, RoutingStrategy, get_gateway
from .providers import (
    BaseProvider,
    LlamaCppProvider,
    LMStudioProvider,
    OllamaProvider,
    SGLangProvider,
    VLLMProvider,
    create_provider,
)
from .schemas import (
    CapabilitySet,
    FabricRequest,
    FabricResponse,
    FabricStreamChunk,
    ModelCapability,
    ModelInfo,
    ProviderHealth,
    ProviderType,
)

__all__ = [
    "ModelFabricGateway",
    "get_gateway",
    "CapabilityRegistry",
    "get_capability_registry",
    "ModelCapability",
    "OllamaProvider",
    "LMStudioProvider",
    "LlamaCppProvider",
    "VLLMProvider",
    "SGLangProvider",
    "BaseProvider",
    "create_provider",
    "LiteLLMRouter",
    "RoutingStrategy",
    "FabricRequest",
    "FabricResponse",
    "FabricStreamChunk",
    "ModelInfo",
    "CapabilitySet",
    "ProviderHealth",
    "ProviderType",
]

__version__ = "1.0.0"
