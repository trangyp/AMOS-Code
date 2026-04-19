"""LLM Model API contracts for AMOS model routing."""

from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum
from typing import Any, Optional

from pydantic import Field

from amos_universe.contracts.pydantic.base import BaseAMOSModel


class ModelProvider(str, Enum):
    """Supported LLM providers."""
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"
    LLAMA_CPP = "llama_cpp"
    VLLM = "vllm"
    SGLANG = "sglang"
    LITELLM = "litellm"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class ModelCapabilities(BaseAMOSModel):
    """Capabilities of a language model."""
    
    context_window: int = Field(
        ...,
        ge=1024,
        description="Maximum context window in tokens"
    )
    max_output_tokens: int = Field(
        ...,
        ge=1,
        description="Maximum output tokens per request"
    )
    supports_tools: bool = Field(
        default=False,
        description="Whether the model supports function calling"
    )
    supports_vision: bool = Field(
        default=False,
        description="Whether the model supports image input"
    )
    supports_streaming: bool = Field(
        default=True,
        description="Whether the model supports streaming responses"
    )
    supports_json_mode: bool = Field(
        default=False,
        description="Whether the model supports constrained JSON output"
    )
    quantization: Optional[str] = Field(
        None,
        description="Quantization level (e.g., 'Q4_K_M', 'Q8_0')"
    )


class ModelInfo(BaseAMOSModel):
    """Information about an available LLM model."""
    
    model_id: str = Field(..., description="Unique model identifier")
    name: str = Field(..., description="Human-readable model name")
    provider: ModelProvider = Field(..., description="Model provider")
    capabilities: ModelCapabilities = Field(..., description="Model capabilities")
    description: Optional[str] = Field(
        None,
        description="Model description"
    )
    size_gb: Optional[float] = Field(
        None,
        ge=0.0,
        description="Model size in gigabytes"
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Model tags (e.g., ['coding', 'chat'])"
    )
    is_local: bool = Field(
        default=True,
        description="Whether the model runs locally"
    )
    is_loaded: bool = Field(
        default=False,
        description="Whether the model is currently loaded in memory"
    )
    loaded_at: Optional[datetime] = Field(
        None,
        description="When the model was loaded"
    )


class ModelRequest(BaseAMOSModel):
    """Request to interact with a specific model."""
    
    model_id: str = Field(..., description="Model to use")
    prompt: str = Field(..., min_length=1, description="Input prompt")
    system_prompt: Optional[str] = Field(
        None,
        description="System prompt/instructions"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature"
    )
    max_tokens: Optional[int] = Field(
        None,
        ge=1,
        description="Maximum tokens to generate"
    )
    stream: bool = Field(
        default=False,
        description="Whether to stream the response"
    )
    tools: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Available tools"
    )
    response_format: Optional[str] = Field(
        None,
        description="Response format (e.g., 'json')"
    )


class ModelResponse(BaseAMOSModel):
    """Response from a model request."""
    
    content: str = Field(..., description="Generated content")
    model_id: str = Field(..., description="Model that generated the response")
    usage: dict[str, int] = Field(
        default_factory=dict,
        description="Token usage statistics"
    )
    finish_reason: Optional[str] = Field(
        None,
        description="Why generation stopped"
    )
    tool_calls: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Tool calls requested"
    )
    generation_time_ms: Optional[int] = Field(
        None,
        ge=0,
        description="Generation time in milliseconds"
    )
