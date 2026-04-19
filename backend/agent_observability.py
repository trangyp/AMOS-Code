"""AMOS AI Agent Observability & Tracing System v3.1.0 - SUPER BRAIN CONSOLIDATION.

Provides comprehensive observability for AI agents, LLM calls, and multi-agent
interactions using OpenTelemetry GenAI semantic conventions (2026).

ALL OBSERVABILITY DATA ROUTES THROUGH SUPERBRAIN FOR:
- Unified audit trail (LAW 4 compliance)
- Health metrics aggregation
- Brain state correlation with traces
- Governance-aware monitoring

Features:
- LLM call tracing with token counts, latency, model names
- Agent decision tracing (tool calls, reasoning steps)
- Multi-agent interaction tracing
- Conversation flow visualization
- Performance metrics and cost tracking
- SuperBrain audit trail integration
- Brain health metrics collection

Research Sources:
- OpenTelemetry GenAI Semantic Conventions 2026
- LangSmith Observability Patterns
- AI Agent Observability Best Practices 2026

Creator: Trang Phan
Version: 3.1.0
"""

import os
import time
import json
from typing import Any, Dict, List, Optional
from contextlib import contextmanager
from datetime import datetime, timezone
UTC = timezone.utc
from dataclasses import dataclass, field

# OpenTelemetry imports
try:
    from opentelemetry import trace
    from opentelemetry.trace import Span, SpanKind, Status, StatusCode
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

# Configuration
OTEL_ENABLED = os.getenv("OTEL_ENABLED", "true").lower() == "true"
OTEL_ENDPOINT = os.getenv("OTEL_ENDPOINT", "http://localhost:4317")
OTEL_SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "amos-brain")

# SuperBrain integration
try:
    from amos_brain import get_super_brain
    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False


@dataclass
class LLMCallInfo:
    """Information about an LLM call."""
    model: str
    provider: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    finish_reason: str  = None
    prompt: str  = None
    completion: str  = None
    cost_usd: float = 0.0


@dataclass
class AgentAction:
    """Information about an agent action."""
    agent_id: str
    action_type: str  # "llm_call", "tool_call", "decision", "handoff"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: float = 0.0
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentConversation:
    """Information about a multi-agent conversation."""
    conversation_id: str
    agents_involved: List[str] = field(default_factory=list)
    messages: List[dict[str, Any]] = field(default_factory=list)
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: datetime  = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentObservabilityManager:
    """Manager for AI agent observability and tracing."""

    def __init__(self):
        self.tracer = None
        self.llm_calls: List[LLMCallInfo] = []
        self.agent_actions: List[AgentAction] = []
        self.conversations: Dict[str, AgentConversation] = {}

        if OPENTELEMETRY_AVAILABLE and OTEL_ENABLED:
            self._setup_opentelemetry()

    def _setup_opentelemetry(self):
        """Setup OpenTelemetry tracer."""
        provider = TracerProvider()

        # OTLP exporter
        exporter = OTLPSpanExporter(endpoint=OTEL_ENDPOINT, insecure=True)
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)

        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(OTEL_SERVICE_NAME)

    @contextmanager
    def trace_llm_call(self, model: str, provider: str, prompt: str  = None):
        """Context manager to trace an LLM call."""
        start_time = time.time()
        call_info = LLMCallInfo(model=model, provider=provider, prompt=prompt)

        span = None
        if self.tracer:
            span = self.tracer.start_span(
                name=f"llm.{provider}.{model}",
                kind=SpanKind.CLIENT,
                attributes={
                    "gen_ai.system": provider,
                    "gen_ai.request.model": model,
                    "gen_ai.request.max_tokens": 4096,
                }
            )

        try:
            yield call_info

            # Record completion
            call_info.latency_ms = (time.time() - start_time) * 1000
            call_info.total_tokens = call_info.prompt_tokens + call_info.completion_tokens

            # Calculate cost (simplified)
            call_info.cost_usd = self._calculate_cost(call_info)

            self.llm_calls.append(call_info)

            # CANONICAL: Record in SuperBrain audit trail
            if SUPERBRAIN_AVAILABLE:
                try:
                    brain = get_super_brain()
                    if brain and hasattr(brain, 'record_audit'):
                        brain.record_audit(
                            action="llm_call",
                            agent_id="observability",
                            details={
                                "model": call_info.model,
                                "provider": call_info.provider,
                                "latency_ms": call_info.latency_ms,
                                "cost_usd": call_info.cost_usd,
                                "total_tokens": call_info.total_tokens
                            }
                        )
                except Exception:
                    pass

            # Update span
            if span:
                span.set_attributes({
                    "gen_ai.response.model": call_info.model,
                    "gen_ai.usage.input_tokens": call_info.prompt_tokens,
                    "gen_ai.usage.output_tokens": call_info.completion_tokens,
                    "gen_ai.usage.total_tokens": call_info.total_tokens,
                    "gen_ai.response.finish_reason": call_info.finish_reason or "unknown",
                    "llm.latency_ms": call_info.latency_ms,
                    "llm.cost_usd": call_info.cost_usd,
                })
                span.set_status(Status(StatusCode.OK))

        except Exception as e:
            if span:
                span.set_status(Status(StatusCode.ERROR, str(e)))
            raise

        finally:
            if span:
                span.end()

    def _calculate_cost(self, call_info: LLMCallInfo) -> float:
        """Calculate approximate cost of LLM call."""
        # Simplified pricing (per 1K tokens)
        pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "claude-3-opus": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        }

        model_pricing = pricing.get(call_info.model, {"input": 0.01, "output": 0.03})

        input_cost = (call_info.prompt_tokens / 1000) * model_pricing["input"]
        output_cost = (call_info.completion_tokens / 1000) * model_pricing["output"]

        return round(input_cost + output_cost, 6)

    @contextmanager
    def trace_agent_action(
        self,
        agent_id: str,
        action_type: str,
        input_data: Dict[str, Any ] = None
    ):
        """Context manager to trace an agent action."""
        start_time = time.time()

        action = AgentAction(
            agent_id=agent_id,
            action_type=action_type,
            input_data=input_data or {}
        )

        span = None
        if self.tracer:
            span = self.tracer.start_span(
                name=f"agent.{agent_id}.{action_type}",
                kind=SpanKind.INTERNAL,
                attributes={
                    "agent.id": agent_id,
                    "agent.action_type": action_type,
                }
            )

        try:
            yield action

            action.duration_ms = (time.time() - start_time) * 1000
            self.agent_actions.append(action)

            # CANONICAL: Record agent action in SuperBrain
            if SUPERBRAIN_AVAILABLE:
                try:
                    brain = get_super_brain()
                    if brain and hasattr(brain, 'record_audit'):
                        brain.record_audit(
                            action=f"agent_action:{action_type}",
                            agent_id=agent_id,
                            details={
                                "duration_ms": action.duration_ms,
                                "input_keys": list(input_data.keys()) if input_data else []
                            }
                        )
                except Exception:
                    pass

            if span:
                span.set_attributes({
                    "agent.duration_ms": action.duration_ms,
                    "agent.output": json.dumps(action.output_data)[:1000],
                })
                span.set_status(Status(StatusCode.OK))

        except Exception as e:
            if span:
                span.set_status(Status(StatusCode.ERROR, str(e)))
            raise

        finally:
            if span:
                span.end()

    def start_conversation(
        self,
        conversation_id: str,
        agents: List[str],
        metadata: Dict[str, Any ] = None
    ) -> AgentConversation:
        """Start tracing a multi-agent conversation."""
        conversation = AgentConversation(
            conversation_id=conversation_id,
            agents_involved=agents,
            metadata=metadata or {}
        )

        self.conversations[conversation_id] = conversation

        # CANONICAL: Record conversation in SuperBrain memory
        if SUPERBRAIN_AVAILABLE:
            try:
                brain = get_super_brain()
                if brain and hasattr(brain, 'memory_governance'):
                    brain.memory_governance.record_memory(
                        content=f"Conversation started: {conversation_id}",
                        memory_type="conversation",
                        agent_id=",".join(agents),
                        metadata={"agents_count": len(agents)}
                    )
            except Exception:
                pass

        if self.tracer:
            with self.tracer.start_as_current_span(
                name=f"conversation.{conversation_id}",
                kind=SpanKind.SERVER,
                attributes={
                    "conversation.id": conversation_id,
                    "conversation.agents": json.dumps(agents),
                }
            ):
                pass

        return conversation

    def add_conversation_message(
        self,
        conversation_id: str,
        agent_id: str,
        message: Dict[str, Any]
    ):
        """Add a message to a conversation."""
        if conversation_id in self.conversations:
            message_data = {
                "agent_id": agent_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "content": message,
            }
            self.conversations[conversation_id].messages.append(message_data)

    def end_conversation(self, conversation_id: str):
        """End a conversation tracing."""
        if conversation_id in self.conversations:
            self.conversations[conversation_id].end_time = datetime.now(timezone.utc)

    def get_llm_stats(self) -> Dict[str, Any]:
        """Get LLM call statistics."""
        if not self.llm_calls:
            return {"total_calls": 0, "total_cost": 0.0}

        total_calls = len(self.llm_calls)
        total_tokens = sum(c.total_tokens for c in self.llm_calls)
        total_cost = sum(c.cost_usd for c in self.llm_calls)
        avg_latency = sum(c.latency_ms for c in self.llm_calls) / total_calls

        # Group by model
        by_model: Dict[str, dict[str, Any]] = {}
        for call in self.llm_calls:
            if call.model not in by_model:
                by_model[call.model] = {"calls": 0, "tokens": 0, "cost": 0.0}
            by_model[call.model]["calls"] += 1
            by_model[call.model]["tokens"] += call.total_tokens
            by_model[call.model]["cost"] += call.cost_usd

        return {
            "total_calls": total_calls,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4),
            "avg_latency_ms": round(avg_latency, 2),
            "by_model": by_model,
        }

    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent action statistics."""
        if not self.agent_actions:
            return {"total_actions": 0}

        total_actions = len(self.agent_actions)
        avg_duration = sum(a.duration_ms for a in self.agent_actions) / total_actions

        # Group by agent
        by_agent: Dict[str, int] = {}
        by_type: Dict[str, int] = {}

        for action in self.agent_actions:
            by_agent[action.agent_id] = by_agent.get(action.agent_id, 0) + 1
            by_type[action.action_type] = by_type.get(action.action_type, 0) + 1

        return {
            "total_actions": total_actions,
            "avg_duration_ms": round(avg_duration, 2),
            "by_agent": by_agent,
            "by_type": by_type,
        }

    def get_traces(self) -> List[dict[str, Any]]:
        """Get all traces for visualization."""
        traces = []

        # LLM calls
        for call in self.llm_calls[-50:]:  # Last 50 calls
            traces.append({
                "type": "llm_call",
                "model": call.model,
                "provider": call.provider,
                "tokens": call.total_tokens,
                "cost": call.cost_usd,
                "latency": call.latency_ms,
                "finish_reason": call.finish_reason,
            })

        # Agent actions
        for action in self.agent_actions[-50:]:
            traces.append({
                "type": "agent_action",
                "agent_id": action.agent_id,
                "action_type": action.action_type,
                "duration": action.duration_ms,
                "timestamp": action.timestamp.isoformat(),
            })

        return traces

    def reset(self):
        """Reset all collected data."""
        self.llm_calls.clear()
        self.agent_actions.clear()
        self.conversations.clear()


# Global observability manager
observability_manager = AgentObservabilityManager()


# Convenience decorators
def trace_llm(model: str, provider: str):
    """Decorator to trace LLM calls in functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with observability_manager.trace_llm_call(model, provider) as call_info:
                result = func(*args, **kwargs)
                # Extract token info from result if available
                if isinstance(result, dict):
                    call_info.completion_tokens = result.get("completion_tokens", 0)
                    call_info.prompt_tokens = result.get("prompt_tokens", 0)
                    call_info.finish_reason = result.get("finish_reason")
                return result
        return wrapper
    return decorator


def trace_agent(agent_id: str, action_type: str):
    """Decorator to trace agent actions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with observability_manager.trace_agent_action(agent_id, action_type) as action:
                result = func(*args, **kwargs)
                action.output_data = {"result": result}
                return result
        return wrapper
    return decorator
