"""AMOS Model Fabric - Core Schemas

Type definitions for the unified model fabric.
"""

from __future__ import annotations


from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any


class ModelCapability(Enum):
    """Model capabilities for capability-based routing."""

    CHAT = auto()
    EDIT = auto()  # Apply patches/edits
    AUTOCOMPLETE = auto()  # FIM (fill-in-middle)
    FILL_IN_MIDDLE = auto()  # Alternative name for autocomplete
    EMBEDDINGS = auto()
    RERANK = auto()
    VISION = auto()
    TOOL_USE = auto()
    LONG_CONTEXT = auto()  # >32k context
    STRUCTURED_OUTPUT = auto()  # JSON mode
    REASONING = auto()  # Chain-of-thought
    CODE = auto()  # Code-specific training
    FUNCTION_CALLING = auto()


class RoutingStrategy(Enum):
    """Request routing strategies."""

    CAPABILITY_MATCH = auto()  # Route to model with required capabilities
    COST_OPTIMIZED = auto()  # Cheapest model meeting requirements
    SPEED_PRIORITY = auto()  # Fastest available
    QUALITY_PRIORITY = auto()  # Best quality for task
    FALLBACK_CHAIN = auto()  # Try primary, fall back on failure
    LOAD_BALANCED = auto()  # Distribute across available


class ProviderType(Enum):
    """Supported provider types."""

    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"
    LLAMA_CPP = "llama_cpp"
    VLLM = "vllm"
    SGLANG = "sglang"
    OPENAI_COMPATIBLE = "openai_compatible"  # Generic OpenAI-compatible


@dataclass
class CapabilitySet:
    """Set of capabilities a model supports."""

    capabilities: set[ModelCapability] = field(default_factory=set)
    context_window: int = 4096
    max_output_tokens: int = 4096
    supports_streaming: bool = True
    quantization: str = None  # "Q4_K_M", "Q8_0", etc.

    def has_capability(self, capability: ModelCapability) -> bool:
        return capability in self.capabilities

    def has_all(self, capabilities: list[ModelCapability]) -> bool:
        return all(c in self.capabilities for c in capabilities)

    def has_any(self, capabilities: list[ModelCapability]) -> bool:
        return any(c in self.capabilities for c in capabilities)


@dataclass
class ModelInfo:
    """Information about a model in the fabric."""

    id: str  # Unique model ID
    name: str  # Human-readable name
    provider: ProviderType
    provider_model_id: str  # Provider's internal ID
    capabilities: CapabilitySet

    # Routing metadata
    priority: int = 100  # Lower = higher priority
    cost_per_1k_tokens: float = 0.0  # For local models, usually 0
    avg_latency_ms: float = None

    # Health
    is_available: bool = True
    last_health_check: datetime = field(default_factory=lambda: datetime.now(UTC))
    error_count: int = 0

    # Provider-specific config
    endpoint_url: str = None
    api_key: str = None
    extra_headers: dict[str, str] = field(default_factory=dict)


@dataclass
class FabricRequest:
    """Unified request to the model fabric."""

    messages: list[dict[str, str]]  # [{"role": "user", "content": "..."}]
    model: str = None  # Specific model ID, or None for auto-select

    # Generation parameters
    temperature: float = 0.7
    max_tokens: int = None
    top_p: float = 1.0
    top_k: int = None
    repetition_penalty: float = 1.0

    # Routing hints
    required_capabilities: list[ModelCapability] = field(default_factory=list)
    preferred_providers: list[ProviderType] = field(default_factory=list)
    routing_strategy: RoutingStrategy = RoutingStrategy.CAPABILITY_MATCH

    # Features
    stream: bool = False
    tools: list[dict] = None
    response_format: dict[str, Any] = None  # JSON schema for structured output

    # Metadata
    request_id: str = None
    tenant_id: str = None
    timeout_seconds: float = 120.0

    # AMOS-specific
    amos_context: dict[str, Any] = field(default_factory=dict)  # Repo state, file context, etc.


@dataclass
class FabricUsage:
    """Token usage information."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    # Local model specific
    load_time_ms: float = None  # Time to load model into VRAM
    tokens_per_second: float = None


@dataclass
class FabricResponse:
    """Unified response from the model fabric."""

    content: str
    model: str  # Actual model used
    provider: ProviderType

    # Usage
    usage: FabricUsage = field(default_factory=FabricUsage)

    # Timing
    latency_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Metadata
    request_id: str = None
    finish_reason: str = None  # "stop", "length", "tool_calls", etc.

    # Tool calls (if applicable)
    tool_calls: list[dict] = None

    # Raw provider response for debugging
    raw_response: dict[str, Any] = None


@dataclass
class FabricStreamChunk:
    """Single chunk from a streaming response."""

    content: str
    model: str
    provider: ProviderType
    request_id: str

    # May be empty for intermediate chunks
    is_finished: bool = False
    finish_reason: str = None

    # Usage (usually only in final chunk)
    usage: FabricUsage | None = None


@dataclass
class ProviderHealth:
    """Health status of a provider."""

    provider: ProviderType
    is_healthy: bool
    endpoint_url: str

    # Models available on this provider
    available_models: list[str] = field(default_factory=list)

    # Performance metrics
    avg_latency_ms: float = None
    error_rate_5m: float = 0.0

    # Resources (for local GPU servers)
    gpu_utilization: float = None  # 0-100%
    vram_used_gb: float = None
    vram_total_gb: float = None

    # Timestamp
    checked_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# Type alias for streaming responses
FabricStream = AsyncGenerator[FabricStreamChunk, None]
