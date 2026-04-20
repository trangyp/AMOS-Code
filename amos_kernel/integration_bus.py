"""
AMOS Integration Bus Architecture - 8 OpenClaws Buses

Implements Section 103.1 from Axiom specification:
- Model Bus: LLM/AI model routing and management
- Runtime Bus: Execution environment orchestration
- Memory Bus: Short-term, long-term, and working memory
- Tool Bus: Tool discovery, execution, and lifecycle
- Protocol Bus: A2A, MCP, and custom protocol adapters
- Frontend Bus: UI/UX component integration
- Policy Bus: Governance and constraint enforcement
- Sync Bus: Distributed state synchronization
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum
from typing import Any, Generic, TypeVar

from .axiom_state import get_state_manager

# ============================================================================
# Bus Types and Base Classes
# ============================================================================


class BusType(Enum):
    """The 8 OpenClaws integration buses."""

    MODEL = "model"
    RUNTIME = "runtime"
    MEMORY = "memory"
    TOOL = "tool"
    PROTOCOL = "protocol"
    FRONTEND = "frontend"
    POLICY = "policy"
    SYNC = "sync"


class BusPriority(Enum):
    """Message priority levels."""

    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


@dataclass(frozen=True)
class BusMessage:
    """Standard message format for all buses."""

    msg_id: str
    bus_type: BusType
    topic: str
    payload: dict[str, Any]
    source: str
    timestamp: datetime
    priority: BusPriority = BusPriority.NORMAL
    correlation_id: str = ""

    @classmethod
    def create(
        cls,
        bus_type: BusType,
        topic: str,
        payload: dict[str, Any],
        source: str,
        priority: BusPriority = BusPriority.NORMAL,
        correlation_id: str = "",
    ) -> BusMessage:
        """Factory method to create a message."""
        msg_id = hashlib.sha256(
            f"{bus_type.value}:{topic}:{datetime.now(UTC).isoformat()}:{json.dumps(payload, sort_keys=True, default=str)}".encode()
        ).hexdigest()[:16]

        return cls(
            msg_id=msg_id,
            bus_type=bus_type,
            topic=topic,
            payload=payload,
            source=source,
            timestamp=datetime.now(UTC),
            priority=priority,
            correlation_id=correlation_id or msg_id,
        )


@dataclass
class BusSubscription:
    """Subscription to bus messages."""

    id: str
    bus_type: BusType
    topic_pattern: str
    handler: Callable[[BusMessage], Coroutine[Any, Any, None]]
    priority: BusPriority = BusPriority.NORMAL


T = TypeVar("T")


class IntegrationBus(ABC, Generic[T]):
    """Abstract base class for all integration buses."""

    def __init__(self, bus_type: BusType) -> None:
        self.bus_type = bus_type
        self._subscriptions: list[BusSubscription] = []
        self._message_queue: asyncio.PriorityQueue[tuple[int, BusMessage]] = asyncio.PriorityQueue()
        self._running = False
        self._state_manager = get_state_manager()

    async def start(self) -> None:
        """Start the bus message processing loop."""
        self._running = True
        asyncio.create_task(self._process_messages())

    async def stop(self) -> None:
        """Stop the bus."""
        self._running = False

    async def publish(self, message: BusMessage) -> None:
        """Publish message to bus."""
        await self._message_queue.put((message.priority.value, message))

    def subscribe(
        self,
        topic_pattern: str,
        handler: Callable[[BusMessage], Coroutine[Any, Any, None]],
        priority: BusPriority = BusPriority.NORMAL,
    ) -> str:
        """Subscribe to messages matching topic pattern."""
        sub_id = hashlib.sha256(
            f"{self.bus_type.value}:{topic_pattern}:{datetime.now(UTC).isoformat()}".encode()
        ).hexdigest()[:16]

        subscription = BusSubscription(
            id=sub_id,
            bus_type=self.bus_type,
            topic_pattern=topic_pattern,
            handler=handler,
            priority=priority,
        )
        self._subscriptions.append(subscription)
        return sub_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """Remove subscription by ID."""
        for i, sub in enumerate(self._subscriptions):
            if sub.id == subscription_id:
                self._subscriptions.pop(i)
                return True
        return False

    async def _process_messages(self) -> None:
        """Main message processing loop."""
        while self._running:
            try:
                _, message = await asyncio.wait_for(self._message_queue.get(), timeout=1.0)
                await self._route_message(message)
            except TimeoutError:
                continue
            except Exception:
                # Log error but keep processing
                pass

    async def _route_message(self, message: BusMessage) -> None:
        """Route message to matching subscribers."""
        for sub in self._subscriptions:
            if self._topic_matches(sub.topic_pattern, message.topic):
                try:
                    await sub.handler(message)
                except Exception:
                    # Log error but don't stop other handlers
                    pass

    def _topic_matches(self, pattern: str, topic: str) -> bool:
        """Check if topic matches pattern (supports * wildcards)."""
        if pattern == "*":
            return True
        if pattern == topic:
            return True
        if pattern.endswith("*") and topic.startswith(pattern[:-1]):
            return True
        return False

    @abstractmethod
    async def initialize(self) -> None:
        """Bus-specific initialization."""
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Return health status for this bus."""
        pass


# ============================================================================
# Model Bus - LLM/AI Model Routing
# ============================================================================


@dataclass
class ModelRequest:
    """Request to call an AI model."""

    model_id: str
    prompt: str
    context: dict[str, Any] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)
    streaming: bool = False


@dataclass
class ModelResponse:
    """Response from AI model."""

    request_id: str
    content: str
    model_id: str
    tokens_used: int = 0
    latency_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class ModelRouter:
    """Routes model requests to appropriate providers."""

    def __init__(self) -> None:
        self._providers: dict[
            str, Callable[[ModelRequest], Coroutine[Any, Any, ModelResponse]]
        ] = {}
        self._default_model: str = ""

    def register_provider(
        self,
        model_id: str,
        handler: Callable[[ModelRequest], Coroutine[Any, Any, ModelResponse]],
        is_default: bool = False,
    ) -> None:
        """Register a model provider."""
        self._providers[model_id] = handler
        if is_default:
            self._default_model = model_id

    async def route(self, request: ModelRequest) -> ModelResponse:
        """Route request to appropriate provider."""
        model_id = request.model_id or self._default_model

        if model_id not in self._providers:
            return ModelResponse(
                request_id=request.model_id,
                content=f"Error: Unknown model '{model_id}'",
                model_id=model_id,
                metadata={"error": "model_not_found"},
            )

        start_time = datetime.now(UTC)
        response = await self._providers[model_id](request)
        end_time = datetime.now(UTC)

        response.latency_ms = (end_time - start_time).total_seconds() * 1000
        return response

    def list_models(self) -> list[str]:
        """List available models."""
        return list(self._providers.keys())


class ModelBus(IntegrationBus[ModelRequest]):
    """Bus for LLM/AI model integration."""

    def __init__(self) -> None:
        super().__init__(BusType.MODEL)
        self.router = ModelRouter()
        self._request_history: list[dict[str, Any]] = []

    async def initialize(self) -> None:
        """Initialize model bus with default providers."""
        # Subscribe to model requests
        self.subscribe("request.*", self._handle_model_request)
        self.subscribe("health.check", self._handle_health_check)

    async def health_check(self) -> dict[str, Any]:
        """Check model bus health."""
        return {
            "status": "healthy",
            "providers": len(self.router._providers),
            "default_model": self.router._default_model,
            "request_count": len(self._request_history),
        }

    async def _handle_model_request(self, message: BusMessage) -> None:
        """Handle incoming model request."""
        payload = message.payload
        request = ModelRequest(
            model_id=payload.get("model_id", ""),
            prompt=payload.get("prompt", ""),
            context=payload.get("context", {}),
            parameters=payload.get("parameters", {}),
            streaming=payload.get("streaming", False),
        )

        response = await self.router.route(request)

        # Publish response
        response_msg = BusMessage.create(
            bus_type=BusType.MODEL,
            topic=f"response.{message.payload.get('request_id', 'unknown')}",
            payload={
                "content": response.content,
                "model_id": response.model_id,
                "tokens_used": response.tokens_used,
                "latency_ms": response.latency_ms,
                "metadata": response.metadata,
            },
            source="model_bus",
            correlation_id=message.correlation_id,
        )
        await self.publish(response_msg)

        # Track request
        self._request_history.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "model_id": request.model_id,
                "latency_ms": response.latency_ms,
            }
        )

    async def _handle_health_check(self, message: BusMessage) -> None:
        """Handle health check request."""
        health = await self.health_check()
        response_msg = BusMessage.create(
            bus_type=BusType.MODEL,
            topic="health.response",
            payload=health,
            source="model_bus",
            correlation_id=message.correlation_id,
        )
        await self.publish(response_msg)


# ============================================================================
# Memory Bus - Memory Management
# ============================================================================


@dataclass
class MemoryEntry:
    """Single memory entry."""

    entry_id: str
    content: str
    memory_type: str  # short_term, long_term, working
    importance: float  # 0.0 to 1.0
    tags: list[str]
    created_at: datetime
    accessed_at: datetime | None = None
    access_count: int = 0


class MemoryStore:
    """In-memory store with persistence hooks."""

    def __init__(self) -> None:
        self._short_term: dict[str, MemoryEntry] = {}
        self._long_term: dict[str, MemoryEntry] = {}
        self._working: dict[str, MemoryEntry] = {}
        self._max_short_term = 100
        self._max_working = 10

    async def store(self, entry: MemoryEntry) -> str:
        """Store memory entry."""
        store = self._get_store(entry.memory_type)
        store[entry.entry_id] = entry

        # Prune if needed
        await self._prune_store(entry.memory_type)

        return entry.entry_id

    async def retrieve(self, entry_id: str) -> MemoryEntry | None:
        """Retrieve memory by ID."""
        for store in [self._short_term, self._long_term, self._working]:
            if entry_id in store:
                entry = store[entry_id]
                entry.access_count += 1
                entry.accessed_at = datetime.now(UTC)
                return entry
        return None

    async def search(self, query: str, memory_type: str | None = None) -> list[MemoryEntry]:
        """Search memories by content."""
        results: list[MemoryEntry] = []

        stores = []
        if memory_type:
            stores = [self._get_store(memory_type)]
        else:
            stores = [self._short_term, self._long_term, self._working]

        query_lower = query.lower()
        for store in stores:
            for entry in store.values():
                if query_lower in entry.content.lower():
                    results.append(entry)

        # Sort by importance and access count
        results.sort(key=lambda e: (e.importance, e.access_count), reverse=True)
        return results[:10]  # Return top 10

    async def delete(self, entry_id: str) -> bool:
        """Delete memory entry."""
        for store in [self._short_term, self._long_term, self._working]:
            if entry_id in store:
                del store[entry_id]
                return True
        return False

    def _get_store(self, memory_type: str) -> dict[str, MemoryEntry]:
        """Get appropriate store for memory type."""
        if memory_type == "short_term":
            return self._short_term
        elif memory_type == "long_term":
            return self._long_term
        elif memory_type == "working":
            return self._working
        return self._short_term

    async def _prune_store(self, memory_type: str) -> None:
        """Prune store to max size."""
        store = self._get_store(memory_type)
        max_size = self._max_short_term if memory_type == "short_term" else self._max_working

        if len(store) > max_size:
            # Remove least important/oldest entries
            entries = list(store.values())
            entries.sort(key=lambda e: (e.importance, e.created_at.timestamp()))
            to_remove = entries[: len(entries) - max_size]
            for entry in to_remove:
                del store[entry.entry_id]


class MemoryBus(IntegrationBus[Any]):
    """Bus for memory management."""

    def __init__(self) -> None:
        super().__init__(BusType.MEMORY)
        self.store = MemoryStore()

    async def initialize(self) -> None:
        """Initialize memory bus."""
        self.subscribe("store.*", self._handle_store)
        self.subscribe("retrieve.*", self._handle_retrieve)
        self.subscribe("search.*", self._handle_search)
        self.subscribe("delete.*", self._handle_delete)

    async def health_check(self) -> dict[str, Any]:
        """Check memory bus health."""
        return {
            "status": "healthy",
            "short_term_entries": len(self.store._short_term),
            "long_term_entries": len(self.store._long_term),
            "working_entries": len(self.store._working),
        }

    async def _handle_store(self, message: BusMessage) -> None:
        """Handle store request."""
        payload = message.payload
        entry = MemoryEntry(
            entry_id=payload.get("entry_id", ""),
            content=payload.get("content", ""),
            memory_type=payload.get("memory_type", "short_term"),
            importance=payload.get("importance", 0.5),
            tags=payload.get("tags", []),
            created_at=datetime.now(UTC),
        )

        entry_id = await self.store.store(entry)

        await self.publish(
            BusMessage.create(
                bus_type=BusType.MEMORY,
                topic=f"stored.{entry_id}",
                payload={"entry_id": entry_id, "success": True},
                source="memory_bus",
                correlation_id=message.correlation_id,
            )
        )

    async def _handle_retrieve(self, message: BusMessage) -> None:
        """Handle retrieve request."""
        entry_id = message.payload.get("entry_id", "")
        entry = await self.store.retrieve(entry_id)

        await self.publish(
            BusMessage.create(
                bus_type=BusType.MEMORY,
                topic=f"retrieved.{entry_id}",
                payload={
                    "entry_id": entry_id,
                    "found": entry is not None,
                    "content": entry.content if entry else None,
                    "memory_type": entry.memory_type if entry else None,
                    "importance": entry.importance if entry else None,
                },
                source="memory_bus",
                correlation_id=message.correlation_id,
            )
        )

    async def _handle_search(self, message: BusMessage) -> None:
        """Handle search request."""
        query = message.payload.get("query", "")
        memory_type = message.payload.get("memory_type")

        results = await self.store.search(query, memory_type)

        await self.publish(
            BusMessage.create(
                bus_type=BusType.MEMORY,
                topic="search.results",
                payload={
                    "query": query,
                    "count": len(results),
                    "results": [
                        {
                            "entry_id": r.entry_id,
                            "content": r.content[:200],  # Truncated
                            "memory_type": r.memory_type,
                            "importance": r.importance,
                        }
                        for r in results
                    ],
                },
                source="memory_bus",
                correlation_id=message.correlation_id,
            )
        )

    async def _handle_delete(self, message: BusMessage) -> None:
        """Handle delete request."""
        entry_id = message.payload.get("entry_id", "")
        success = await self.store.delete(entry_id)

        await self.publish(
            BusMessage.create(
                bus_type=BusType.MEMORY,
                topic=f"deleted.{entry_id}",
                payload={"entry_id": entry_id, "success": success},
                source="memory_bus",
                correlation_id=message.correlation_id,
            )
        )


# ============================================================================
# Tool Bus - Tool Management
# ============================================================================


@dataclass
class ToolDefinition:
    """Definition of a callable tool."""

    tool_id: str
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[..., Any] | None = None
    requires_approval: bool = False
    timeout_seconds: float = 30.0


class ToolRegistry:
    """Registry of available tools."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool."""
        self._tools[tool.tool_id] = tool

    def unregister(self, tool_id: str) -> bool:
        """Unregister a tool."""
        if tool_id in self._tools:
            del self._tools[tool_id]
            return True
        return False

    def get(self, tool_id: str) -> ToolDefinition | None:
        """Get tool by ID."""
        return self._tools.get(tool_id)

    def list_tools(self) -> list[ToolDefinition]:
        """List all registered tools."""
        return list(self._tools.values())

    def search(self, query: str) -> list[ToolDefinition]:
        """Search tools by name/description."""
        query_lower = query.lower()
        results = []
        for tool in self._tools.values():
            if query_lower in tool.name.lower() or query_lower in tool.description.lower():
                results.append(tool)
        return results


class ToolBus(IntegrationBus[Any]):
    """Bus for tool management and execution."""

    def __init__(self) -> None:
        super().__init__(BusType.TOOL)
        self.registry = ToolRegistry()
        self._execution_history: list[dict[str, Any]] = []

    async def initialize(self) -> None:
        """Initialize tool bus."""
        self.subscribe("execute.*", self._handle_execute)
        self.subscribe("discover.*", self._handle_discover)
        self.subscribe("register.*", self._handle_register)

    async def health_check(self) -> dict[str, Any]:
        """Check tool bus health."""
        return {
            "status": "healthy",
            "registered_tools": len(self.registry._tools),
            "execution_count": len(self._execution_history),
        }

    async def _handle_execute(self, message: BusMessage) -> None:
        """Handle tool execution request."""
        tool_id = message.payload.get("tool_id", "")
        parameters = message.payload.get("parameters", {})

        tool = self.registry.get(tool_id)
        if not tool:
            await self.publish(
                BusMessage.create(
                    bus_type=BusType.TOOL,
                    topic=f"error.{tool_id}",
                    payload={"error": f"Tool '{tool_id}' not found"},
                    source="tool_bus",
                    correlation_id=message.correlation_id,
                )
            )
            return

        start_time = datetime.now(UTC)

        try:
            if tool.handler:
                # Execute with timeout
                result = await asyncio.wait_for(
                    asyncio.to_thread(tool.handler, **parameters),
                    timeout=tool.timeout_seconds,
                )
                success = True
                error = None
            else:
                success = False
                result = None
                error = "No handler registered"
        except TimeoutError:
            success = False
            result = None
            error = f"Timeout after {tool.timeout_seconds}s"
        except Exception as e:
            success = False
            result = None
            error = str(e)

        end_time = datetime.now(UTC)

        # Track execution
        self._execution_history.append(
            {
                "tool_id": tool_id,
                "timestamp": start_time.isoformat(),
                "duration_ms": (end_time - start_time).total_seconds() * 1000,
                "success": success,
            }
        )

        await self.publish(
            BusMessage.create(
                bus_type=BusType.TOOL,
                topic=f"result.{tool_id}",
                payload={
                    "tool_id": tool_id,
                    "success": success,
                    "result": result,
                    "error": error,
                    "execution_time_ms": (end_time - start_time).total_seconds() * 1000,
                },
                source="tool_bus",
                correlation_id=message.correlation_id,
            )
        )

    async def _handle_discover(self, message: BusMessage) -> None:
        """Handle tool discovery request."""
        query = message.payload.get("query", "")

        if query:
            tools = self.registry.search(query)
        else:
            tools = self.registry.list_tools()

        await self.publish(
            BusMessage.create(
                bus_type=BusType.TOOL,
                topic="discover.results",
                payload={
                    "count": len(tools),
                    "tools": [
                        {
                            "tool_id": t.tool_id,
                            "name": t.name,
                            "description": t.description,
                            "parameters": t.parameters,
                            "requires_approval": t.requires_approval,
                        }
                        for t in tools
                    ],
                },
                source="tool_bus",
                correlation_id=message.correlation_id,
            )
        )

    async def _handle_register(self, message: BusMessage) -> None:
        """Handle tool registration."""
        # Note: Handler function can't be passed via message
        # This creates a definition for later handler attachment
        tool_def = message.payload.get("tool_definition", {})

        tool = ToolDefinition(
            tool_id=tool_def.get("tool_id", ""),
            name=tool_def.get("name", ""),
            description=tool_def.get("description", ""),
            parameters=tool_def.get("parameters", {}),
            requires_approval=tool_def.get("requires_approval", False),
            timeout_seconds=tool_def.get("timeout_seconds", 30.0),
        )

        self.registry.register(tool)

        await self.publish(
            BusMessage.create(
                bus_type=BusType.TOOL,
                topic=f"registered.{tool.tool_id}",
                payload={"tool_id": tool.tool_id, "success": True},
                source="tool_bus",
                correlation_id=message.correlation_id,
        )

    def _rule_matches(
        self,
        rule: PolicyRule,
        subject: str,
        resource: str,
        action: str,
        context: dict[str, Any],
    ) -> bool:
        """Check if rule matches request context."""
        # Simple string matching - production would use proper policy language
        condition = rule.condition.lower()
        check_str = f"{subject}:{resource}:{action}"

        if "subject=" in condition:
            expected = condition.split("subject=")[1].split(";")[0]
            if expected not in subject:
                return False
        if "resource=" in condition:
            expected = condition.split("resource=")[1].split(";")[0]
            if expected not in resource:
                return False
        if "action=" in condition:
            expected = condition.split("action=")[1].split(";")[0]
            if expected != action and expected != "*":
                return False

        return True


class PolicyBus(IntegrationBus[Any]):
    """Bus for policy enforcement and governance."""

    def __init__(self) -> None:
        super().__init__(BusType.POLICY)
        self.engine = PolicyEngine()
        self._violation_count = 0
        self._evaluation_count = 0

    async def initialize(self) -> None:
        """Initialize policy bus."""
        self.subscribe("evaluate.*", self._handle_evaluate)
        self.subscribe("add_rule.*", self._handle_add_rule)
        self.subscribe("remove_rule.*", self._handle_remove_rule)
        self.subscribe("audit.*", self._handle_audit)

    async def health_check(self) -> dict[str, Any]:
        """Check policy bus health."""
        return {
            "status": "healthy",
            "rules": len(self.engine._rules),
            "evaluations": self._evaluation_count,
            "violations": self._violation_count,
        }

    async def _handle_evaluate(self, message: BusMessage) -> None:
        """Handle policy evaluation request."""
        payload = message.payload
        evaluation_id = payload.get("evaluation_id", "")
        subject = payload.get("subject", "")
        resource = payload.get("resource", "")
        action = payload.get("action", "")
        context = payload.get("context", {})

        result = self.engine.evaluate(
            evaluation_id, subject, resource, action, context
        )
        self._evaluation_count += 1
        if result.decision == "deny":
            self._violation_count += 1

        await self.publish(BusMessage.create(
            bus_type=BusType.POLICY,
            topic=f"decision.{result.evaluation_id}",
            payload={
                "evaluation_id": result.evaluation_id,
                "rule_id": result.rule_id,
                "subject": result.subject,
                "resource": result.resource,
                "action": result.action,
                "decision": result.decision,
                "reason": result.reason,
            },
            source="policy_bus",
            correlation_id=message.correlation_id,
        ))

    async def _handle_add_rule(self, message: BusMessage) -> None:
        """Handle add rule request."""
        rule_def = message.payload.get("rule", {})
        rule = PolicyRule(
            rule_id=rule_def.get("rule_id", ""),
            name=rule_def.get("name", ""),
            description=rule_def.get("description", ""),
            condition=rule_def.get("condition", ""),
            action=rule_def.get("action", "deny"),
            priority=rule_def.get("priority", 100),
            enabled=rule_def.get("enabled", True),
        )

        self.engine.add_rule(rule)

        await self.publish(BusMessage.create(
            bus_type=BusType.POLICY,
            topic=f"rule_added.{rule.rule_id}",
            payload={"rule_id": rule.rule_id, "success": True},
            source="policy_bus",
            correlation_id=message.correlation_id,
        ))

    async def _handle_remove_rule(self, message: BusMessage) -> None:
        """Handle remove rule request."""
        rule_id = message.payload.get("rule_id", "")
        success = self.engine.remove_rule(rule_id)

        await self.publish(BusMessage.create(
            bus_type=BusType.POLICY,
            topic=f"rule_removed.{rule_id}",
            payload={"rule_id": rule_id, "success": success},
            source="policy_bus",
            correlation_id=message.correlation_id,
        ))

    async def _handle_audit(self, message: BusMessage) -> None:
        """Handle audit request."""
        rule_id = message.payload.get("rule_id")
        limit = message.payload.get("limit", 100)

        evaluations = self.engine._evaluations
        if rule_id:
            evaluations = [e for e in evaluations if e.rule_id == rule_id]
        evaluations = evaluations[-limit:]

        await self.publish(BusMessage.create(
            bus_type=BusType.POLICY,
            topic="audit.results",
            payload={
                "count": len(evaluations),
                "evaluations": [
                    {
                        "evaluation_id": e.evaluation_id,
                        "rule_id": e.rule_id,
                        "subject": e.subject,
                        "resource": e.resource,
                        "action": e.action,
                        "decision": e.decision,
                        "timestamp": e.timestamp.isoformat(),
                    }
                    for e in evaluations
                ],
            },
            source="policy_bus",
            correlation_id=message.correlation_id,
        ))


# ============================================================================
# Sync Bus - Synchronization and State Consistency
# ============================================================================

@dataclass
class SyncOperation:
    """Synchronization operation."""
    operation_id: str
    operation_type: str  # push, pull, merge, conflict_resolve
    source: str
    target: str
    data: dict[str, Any]
    priority: int = 100


@dataclass
class SyncResult:
    """Result of sync operation."""
    operation_id: str
    success: bool
    conflicts: list[dict[str, Any]]
    merged_data: dict[str, Any] | None
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class SyncEngine:
    """Engine for synchronization operations."""

    def __init__(self) -> None:
        self._operations: dict[str, SyncOperation] = {}
        self._results: dict[str, SyncResult] = {}
        self._pending: list[str] = []
        self._sync_states: dict[str, dict[str, Any]] = {}

    def queue_operation(self, operation: SyncOperation) -> None:
        """Queue sync operation."""
        self._operations[operation.operation_id] = operation
        # Insert by priority
        inserted = False
        for i, op_id in enumerate(self._pending):
            existing = self._operations.get(op_id)
            if existing and operation.priority < existing.priority:
                self._pending.insert(i, operation.operation_id)
                inserted = True
                break
        if not inserted:
            self._pending.append(operation.operation_id)

    async def execute_sync(self, operation: SyncOperation) -> SyncResult:
        """Execute sync operation."""
        if operation.operation_type == "push":
            result = await self._do_push(operation)
        elif operation.operation_type == "pull":
            result = await self._do_pull(operation)
        elif operation.operation_type == "merge":
            result = await self._do_merge(operation)
        else:
            result = SyncResult(
                operation_id=operation.operation_id,
                success=False,
                conflicts=[],
                merged_data=None,
            )

        self._results[operation.operation_id] = result
        return result

    async def _do_push(self, operation: SyncOperation) -> SyncResult:
        """Push data to target."""
        # Store in sync state
        self._sync_states[operation.target] = operation.data.copy()
        return SyncResult(
            operation_id=operation.operation_id,
            success=True,
            conflicts=[],
            merged_data=operation.data,
        )

    async def _do_pull(self, operation: SyncOperation) -> SyncResult:
        """Pull data from source."""
        data = self._sync_states.get(operation.source, {})
        return SyncResult(
            operation_id=operation.operation_id,
            success=True,
            conflicts=[],
            merged_data=data,
        )

    async def _do_merge(self, operation: SyncOperation) -> SyncResult:
        """Merge data from source and target."""
        source_data = self._sync_states.get(operation.source, {})
        target_data = self._sync_states.get(operation.target, {})

        conflicts = []
        merged = target_data.copy()

        for key, value in source_data.items():
            if key in target_data and target_data[key] != value:
                conflicts.append({
                    "key": key,
                    "source_value": value,
                    "target_value": target_data[key],
                })
                # Use source value in case of conflict
                merged[key] = value
            else:
                merged[key] = value

        return SyncResult(
            operation_id=operation.operation_id,
            success=True,
            conflicts=conflicts,
            merged_data=merged,
        )

    def get_result(self, operation_id: str) -> SyncResult | None:
        """Get sync result by ID."""
        return self._results.get(operation_id)


class SyncBus(IntegrationBus[Any]):
    """Bus for synchronization and state consistency."""

    def __init__(self) -> None:
        super().__init__(BusType.SYNC)
        self.engine = SyncEngine()
        self._sync_count = 0
        self._conflict_count = 0

    async def initialize(self) -> None:
        """Initialize sync bus."""
        self.subscribe("push.*", self._handle_push)
        self.subscribe("pull.*", self._handle_pull)
        self.subscribe("merge.*", self._handle_merge)
        self.subscribe("status.*", self._handle_status)

    async def health_check(self) -> dict[str, Any]:
        """Check sync bus health."""
        return {
            "status": "healthy",
            "pending_operations": len(self.engine._pending),
            "sync_count": self._sync_count,
            "conflict_count": self._conflict_count,
        }

    async def _handle_push(self, message: BusMessage) -> None:
        """Handle push request."""
        payload = message.payload
        operation = SyncOperation(
            operation_id=payload.get("operation_id", ""),
            operation_type="push",
            source=payload.get("source", ""),
            target=payload.get("target", ""),
            data=payload.get("data", {}),
            priority=payload.get("priority", 100),
        )

        self.engine.queue_operation(operation)
        result = await self.engine.execute_sync(operation)
        self._sync_count += 1

        await self.publish(BusMessage.create(
            bus_type=BusType.SYNC,
            topic=f"pushed.{result.operation_id}",
            payload={
                "operation_id": result.operation_id,
                "success": result.success,
                "conflicts": len(result.conflicts),
            },
            source="sync_bus",
            correlation_id=message.correlation_id,
        ))

    async def _handle_pull(self, message: BusMessage) -> None:
        """Handle pull request."""
        payload = message.payload
        operation = SyncOperation(
            operation_id=payload.get("operation_id", ""),
            operation_type="pull",
            source=payload.get("source", ""),
            target=payload.get("target", ""),
            data={},
            priority=payload.get("priority", 100),
        )

        result = await self.engine.execute_sync(operation)
        self._sync_count += 1

        await self.publish(BusMessage.create(
            bus_type=BusType.SYNC,
            topic=f"pulled.{result.operation_id}",
            payload={
                "operation_id": result.operation_id,
                "success": result.success,
                "data": result.merged_data,
            },
            source="sync_bus",
            correlation_id=message.correlation_id,
        ))

    async def _handle_merge(self, message: BusMessage) -> None:
        """Handle merge request."""
        payload = message.payload
        operation = SyncOperation(
            operation_id=payload.get("operation_id", ""),
            operation_type="merge",
            source=payload.get("source", ""),
            target=payload.get("target", ""),
            data={},
            priority=payload.get("priority", 100),
        )

        result = await self.engine.execute_sync(operation)
        self._sync_count += 1
        self._conflict_count += len(result.conflicts)

        await self.publish(BusMessage.create(
            bus_type=BusType.SYNC,
            topic=f"merged.{result.operation_id}",
            payload={
                "operation_id": result.operation_id,
                "success": result.success,
                "conflicts": result.conflicts,
                "merged_data": result.merged_data,
            },
            source="sync_bus",
            correlation_id=message.correlation_id,
        ))

    async def _handle_status(self, message: BusMessage) -> None:
        """Handle status request."""
        operation_id = message.payload.get("operation_id", "")
        result = self.engine.get_result(operation_id)

        await self.publish(BusMessage.create(
            bus_type=BusType.SYNC,
            topic=f"status.{operation_id}",
            payload={
                "operation_id": operation_id,
                "found": result is not None,
                "success": result.success if result else None,
                "conflicts": result.conflicts if result else [],
            },
            source="sync_bus",
            correlation_id=message.correlation_id,
        ))


# ============================================================================
# Bus Coordinator
# ============================================================================


class BusCoordinator:
    """Coordinates all 8 integration buses."""

    _instance: BusCoordinator | None = None

    def __new__(cls) -> BusCoordinator:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self.buses: dict[BusType, IntegrationBus[Any]] = {
            BusType.MODEL: ModelBus(),
            BusType.MEMORY: MemoryBus(),
            BusType.TOOL: ToolBus(),
            BusType.PROTOCOL: ProtocolBus(),
            BusType.RUNTIME: RuntimeBus(),
            BusType.FRONTEND: FrontendBus(),
            BusType.POLICY: PolicyBus(),
            BusType.SYNC: SyncBus(),
        }
        self._running = False
        self._initialized = True

    async def start_all(self) -> None:
        """Start all buses."""
        for bus in self.buses.values():
            await bus.initialize()
            await bus.start()
        self._running = True

    async def stop_all(self) -> None:
        """Stop all buses."""
        for bus in self.buses.values():
            await bus.stop()
        self._running = False

    def get_bus(self, bus_type: BusType) -> IntegrationBus[Any]:
        """Get specific bus by type."""
        return self.buses[bus_type]

    async def health_check_all(self) -> dict[str, dict[str, Any]]:
        """Health check all buses."""
        return {bus_type.value: await bus.health_check() for bus_type, bus in self.buses.items()}

    async def publish(self, message: BusMessage) -> None:
        """Publish to appropriate bus."""
        if message.bus_type in self.buses:
            await self.buses[message.bus_type].publish(message)


def get_bus_coordinator() -> BusCoordinator:
    """Get singleton bus coordinator."""
    return BusCoordinator()
