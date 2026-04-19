"""AMOS API Schemas

Pydantic models for request/response validation.
Centralized schema definitions for all API domains.

Creator: Trang Phan
Version: 3.0.0
"""

from datetime import datetime, timezone

UTC = timezone.utc
from typing import Any, Literal

from pydantic import BaseModel, Field

# ============================================================================
# LLM Schemas
# ============================================================================


class MessageSchema(BaseModel):
    """Chat message schema."""

    role: Literal["system", "user", "assistant", "tool"] = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    metadata: dict[str, Any] = Field(None, description="Additional metadata")


class ChatRequest(BaseModel):
    """LLM chat completion request."""

    messages: list[MessageSchema] = Field(..., description="Conversation messages")
    model: str = Field(None, description="Model to use (e.g., llama3.2, gpt-4o)")
    provider: str = Field(None, description="Provider preference (ollama, openai, anthropic)")
    temperature: float = Field(0.7, ge=0, le=2, description="Sampling temperature")
    max_tokens: int = Field(None, ge=1, description="Maximum tokens to generate")
    stream: bool = Field(False, description="Enable streaming response")


class ChatResponse(BaseModel):
    """LLM chat completion response."""

    content: str = Field(..., description="Generated content")
    model: str = Field(..., description="Model used")
    provider: str = Field(..., description="Provider used")
    usage: dict[str, int] = Field(..., description="Token usage statistics")
    latency_ms: float = Field(..., description="Request latency in milliseconds")
    timestamp: datetime = Field(..., description="Response timestamp")


class ProviderInfo(BaseModel):
    """LLM provider information."""

    name: str = Field(..., description="Provider name")
    models: list[str] = Field(..., description="Available models")
    enabled: bool = Field(..., description="Whether provider is available")


class ProvidersResponse(BaseModel):
    """List of available providers."""

    providers: list[ProviderInfo] = Field(..., description="Available LLM providers")


# ============================================================================
# Agent Schemas
# ============================================================================


class AgentTaskRequest(BaseModel):
    """Request to create an agent task."""

    name: str = Field(..., description="Task name")
    description: str = Field(..., description="Task description")
    agent_type: Literal["code", "analysis", "research", "general"] = Field(
        "general", description="Agent specialization"
    )
    priority: Literal["low", "normal", "high", "critical"] = Field(
        "normal", description="Task priority"
    )
    context: dict[str, Any] = Field(None, description="Task context/data")


class AgentTaskResponse(BaseModel):
    """Agent task information."""

    id: str = Field(..., description="Task ID")
    name: str = Field(..., description="Task name")
    description: str = Field(..., description="Task description")
    status: Literal["pending", "running", "completed", "failed"] = Field(
        ..., description="Current status"
    )
    progress: int = Field(0, ge=0, le=100, description="Completion percentage")
    agent_type: str = Field(..., description="Agent type")
    priority: str = Field(..., description="Task priority")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(None, description="Last update timestamp")
    result: dict[str, Any] = Field(None, description="Task result if completed")
    error: str = Field(None, description="Error message if failed")


class TaskListResponse(BaseModel):
    """List of agent tasks."""

    tasks: list[AgentTaskResponse] = Field(..., description="Agent tasks")
    total: int = Field(..., description="Total task count")
    running: int = Field(..., description="Number of running tasks")
    pending: int = Field(..., description="Number of pending tasks")


# ============================================================================
# System Schemas
# ============================================================================


class SystemStatus(BaseModel):
    """AMOS system status."""

    version: str = Field(..., description="AMOS version")
    status: Literal["healthy", "degraded", "critical"] = Field(..., description="System health")
    uptime_seconds: float = Field(..., description="System uptime")
    components: dict[str, Any] = Field(..., description="Component statuses")
    providers: list[ProviderInfo] = Field(..., description="Available LLM providers")


class EvolutionStatus(BaseModel):
    """Self-evolution system status."""

    enabled: bool = Field(..., description="Whether evolution is enabled")
    total_cycles: int = Field(..., description="Total evolution cycles completed")
    last_cycle: datetime = Field(None, description="Last evolution timestamp")
    opportunities_found: int = Field(..., description="Total opportunities detected")
    current_mode: Literal["autonomous", "supervised", "manual"] = Field(
        ..., description="Governance mode"
    )


class MetricsResponse(BaseModel):
    """System metrics."""

    cpu_percent: float = Field(..., description="CPU usage percentage")
    memory_percent: float = Field(..., description="Memory usage percentage")
    active_tasks: int = Field(..., description="Number of active tasks")
    total_requests: int = Field(..., description="Total API requests served")
    average_latency_ms: float = Field(..., description="Average request latency")


class GovernanceRuleSchema(BaseModel):
    """Governance rule definition."""

    id: str = Field(..., description="Rule ID")
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    priority: str = Field(..., description="Rule priority")
    status: str = Field(..., description="Rule status")
    trigger: str = Field(..., description="Trigger condition")
    action: str = Field(..., description="Action to take")


class GovernanceUpdate(BaseModel):
    """Update governance mode."""

    mode: Literal["autonomous", "supervised", "manual"] = Field(
        ..., description="New governance mode"
    )


# ============================================================================
# WebSocket Schemas
# ============================================================================


class WSMessage(BaseModel):
    """WebSocket message wrapper."""

    type: str = Field(..., description="Message type")
    payload: dict[str, Any] = Field(..., description="Message payload")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class StreamChunk(BaseModel):
    """Streaming response chunk."""

    chunk: str = Field(..., description="Content chunk")
    is_final: bool = Field(False, description="Whether this is the final chunk")


# ============================================================================
# Math Framework Schemas
# ============================================================================


class EquationInfo(BaseModel):
    """Equation information."""

    name: str = Field(..., description="Equation name")
    latex: str = Field(..., description="LaTeX representation")
    description: str = Field(..., description="Equation description")
    domain: str = Field(..., description="Domain (physics, math, etc.)")
    variables: list[str] = Field(default_factory=list, description="Variables in equation")


class MathQueryRequest(BaseModel):
    """Math framework query request."""

    query: str = Field(..., description="Search query text")
    domain: str = Field(None, description="Domain filter (physics, math, cs, etc.)")
    limit: int = Field(10, ge=1, le=100, description="Maximum results")


class MathQueryResponse(BaseModel):
    """Math framework query response."""

    equations: list[EquationInfo] = Field(..., description="Matching equations")
    total: int = Field(..., description="Total matches")
    domain: str = Field(None, description="Domain queried")


class EquationValidationRequest(BaseModel):
    """Equation validation request."""

    equation: str = Field(..., description="Equation to validate (LaTeX)")
    domain: str = Field("general", description="Domain context")


class EquationValidationResponse(BaseModel):
    """Equation validation response."""

    valid: bool = Field(..., description="Whether equation is valid")
    message: str = Field(..., description="Validation message")
    suggestions: list[str] = Field(default_factory=list, description="Suggested fixes")


class MathFrameworkStatus(BaseModel):
    """Math framework status."""

    available: bool = Field(..., description="Whether framework is available")
    initialized: bool = Field(..., description="Whether framework is initialized")
    total_equations: int = Field(0, description="Total equations in framework")
    domains: list[str] = Field(default_factory=list, description="Available domains")
    version: str = Field("1.0.0", description="Framework version")
