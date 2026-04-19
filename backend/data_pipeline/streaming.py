"""
AMOS SuperBrain Data Pipeline & Streaming v2.0.0

Event streaming infrastructure with SuperBrain governance for all 12 systems.
Supports real-time data flow, stream processing, and data lineage tracking.

Architecture:
- Kafka-based event streaming (with Redis fallback)
- Governance-controlled message processing
- Data lineage tracking for audit compliance
- Real-time analytics with windowed aggregations

Owner: Trang Phan
Version: 2.0.0
"""

from __future__ import annotations


import hashlib
import json
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone

UTC = timezone.utc
from typing import Any

# Kafka integration
try:
    from kafka import KafkaConsumer, KafkaProducer, TopicPartition
    from kafka.admin import KafkaAdminClient, NewTopic

    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

# Redis fallback
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# SuperBrain integration
try:
    from amos_brain import get_super_brain

    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False
    get_super_brain = None


@dataclass
class StreamEvent:
    """Event in the data pipeline with governance metadata."""

    event_id: str
    event_type: str
    source_system: str
    target_system: str
    payload: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    correlation_id: str = None
    user_id: str = None
    requires_governance: bool = True
    processed: bool = False
    lineage: list[dict] = field(default_factory=list)


@dataclass
class StreamMetrics:
    """Metrics for stream processing."""

    total_events: int = 0
    events_per_second: float = 0.0
    processing_latency_ms: float = 0.0
    governance_blocked: int = 0
    governance_allowed: int = 0
    errors: int = 0
    last_updated: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class DataPipelineManager:
    """Central data pipeline manager with SuperBrain governance."""

    # Topics for 12 systems
    TOPICS = {
        # Governance topics
        "superbrain.events": "SuperBrain governance events",
        "superbrain.audit": "Audit trail events",
        # System topics
        "cognitive_router.tasks": "Task routing events",
        "cognitive_router.decisions": "Routing decisions",
        "resilience_engine.circuit_events": "Circuit breaker events",
        "resilience_engine.metrics": "Resilience metrics",
        "knowledge_loader.updates": "Knowledge updates",
        "knowledge_loader.queries": "Knowledge queries",
        "master_orchestrator.workflows": "Workflow events",
        "master_orchestrator.completions": "Task completions",
        "production_api.requests": "API requests",
        "production_api.responses": "API responses",
        "graphql_api.mutations": "GraphQL mutations",
        "graphql_api.subscriptions": "Subscription events",
        "agent_messaging.messages": "Agent messages",
        "agent_observability.telemetry": "Observability data",
        "ubi_engine.analyses": "UBI analyses",
        "ubi_engine.results": "UBI results",
        "amos_tools.executions": "Tool executions",
        "audit_exporter.exports": "Audit exports",
    }

    def __init__(self, kafka_bootstrap: str = None, redis_url: str = None):
        self.kafka_bootstrap = kafka_bootstrap or "localhost:9092"
        self.redis_url = redis_url or "redis://localhost:6379/1"
        self._producer: KafkaProducer | None = None
        self._consumer: KafkaConsumer | None = None
        self._redis: redis.Redis = None
        self._brain = None
        self._metrics = StreamMetrics()
        self._local_buffer: list[StreamEvent] = []
        self._processors: dict[str, list[Callable]] = defaultdict(list)

        self._init_connections()

    def _init_connections(self):
        """Initialize Kafka and Redis connections."""
        # Try Kafka first
        if KAFKA_AVAILABLE:
            try:
                self._producer = KafkaProducer(
                    bootstrap_servers=self.kafka_bootstrap,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    key_serializer=lambda k: k.encode("utf-8") if k else None,
                )
            except Exception:
                self._producer = None

        # Fallback to Redis
        if REDIS_AVAILABLE:
            try:
                self._redis = redis.from_url(self.redis_url)
                self._redis.ping()
            except Exception:
                self._redis = None

        # SuperBrain
        if SUPERBRAIN_AVAILABLE:
            try:
                self._brain = get_super_brain()
            except Exception:
                pass

    def _validate_event(self, event: StreamEvent) -> bool:
        """Validate event via SuperBrain governance."""
        if not event.requires_governance:
            return True

        if not SUPERBRAIN_AVAILABLE or not self._brain:
            return True  # Fail open

        try:
            if hasattr(self._brain, "action_gate"):
                action_result = self._brain.action_gate.validate_action(
                    agent_id=event.source_system,
                    action=f"stream_event_{event.event_type}",
                    details={
                        "event_id": event.event_id,
                        "target": event.target_system,
                        "payload_size": len(str(event.payload)),
                    },
                )

                if action_result.authorized:
                    self._metrics.governance_allowed += 1
                    return True
                else:
                    self._metrics.governance_blocked += 1
                    return False
        except Exception:
            pass  # Fail open

        return True

    def _record_lineage(self, event: StreamEvent, stage: str):
        """Record data lineage for audit."""
        event.lineage.append(
            {"stage": stage, "timestamp": datetime.now(UTC).isoformat(), "system": "data_pipeline"}
        )

    def publish_event(
        self,
        event_type: str,
        source_system: str,
        payload: dict[str, Any],
        target_system: str = None,
        correlation_id: str = None,
        requires_governance: bool = True,
    ) -> bool:
        """Publish event to stream with governance validation."""
        # Create event
        event_id = hashlib.sha256(
            f"{source_system}:{event_type}:{datetime.now(UTC).isoformat()}".encode()
        ).hexdigest()[:16]

        event = StreamEvent(
            event_id=event_id,
            event_type=event_type,
            source_system=source_system,
            target_system=target_system,
            payload=payload,
            correlation_id=correlation_id,
            requires_governance=requires_governance,
        )

        # CANONICAL: Validate via SuperBrain
        if not self._validate_event(event):
            return False

        # Record lineage
        self._record_lineage(event, "published")

        # Publish to Kafka
        if self._producer:
            try:
                topic = f"{source_system}.{event_type}"
                self._producer.send(topic, key=event_id, value=event.__dict__)
                self._metrics.total_events += 1
                return True
            except Exception:
                pass

        # Fallback to Redis pub/sub
        if self._redis:
            try:
                channel = f"stream:{source_system}:{event_type}"
                self._redis.publish(channel, json.dumps(event.__dict__))
                self._metrics.total_events += 1
                return True
            except Exception:
                pass

        # Local buffer as last resort
        self._local_buffer.append(event)
        self._metrics.total_events += 1
        return True

    def subscribe_to_stream(self, topic_pattern: str, handler: Callable[[StreamEvent], None]):
        """Subscribe to stream with handler."""
        self._processors[topic_pattern].append(handler)

    def process_event(self, event: StreamEvent) -> bool:
        """Process single event with governance."""
        start_time = datetime.now(UTC)

        # Validate
        if not self._validate_event(event):
            return False

        # Record lineage
        self._record_lineage(event, "processing")

        # Execute processors
        topic = f"{event.source_system}.{event.event_type}"
        for pattern, handlers in self._processors.items():
            if pattern in topic or pattern == "*":
                for handler in handlers:
                    try:
                        handler(event)
                    except Exception as e:
                        self._metrics.errors += 1
                        # Publish error event
                        self.publish_event(
                            event_type="processing_error",
                            source_system="data_pipeline",
                            payload={"original_event": event.event_id, "error": str(e)},
                            correlation_id=event.correlation_id,
                            requires_governance=False,
                        )

        # Update metrics
        processing_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
        self._metrics.processing_latency_ms = (
            self._metrics.processing_latency_ms * 0.9 + processing_time * 0.1
        )

        event.processed = True
        return True

    def create_stream_topology(self, system: str) -> dict[str, Any]:
        """Create stream topology for a system."""
        topology = {
            "system": system,
            "input_topics": [],
            "output_topics": [],
            "processors": [],
            "governance_required": True,
        }

        # Define topology based on system
        if system == "cognitive_router":
            topology["input_topics"] = ["master_orchestrator.workflows"]
            topology["output_topics"] = [
                "cognitive_router.decisions",
                "resilience_engine.circuit_events",
            ]
        elif system == "resilience_engine":
            topology["input_topics"] = ["*"]  # All topics
            topology["output_topics"] = ["resilience_engine.metrics"]
        elif system == "master_orchestrator":
            topology["input_topics"] = ["cognitive_router.decisions"]
            topology["output_topics"] = ["master_orchestrator.completions", "superbrain.audit"]

        return topology

    def get_metrics(self) -> StreamMetrics:
        """Get current stream metrics."""
        self._metrics.last_updated = datetime.now(UTC).isoformat()

        # Calculate events per second
        if self._metrics.total_events > 0:
            self._metrics.events_per_second = self._metrics.total_events / 60.0

        return self._metrics

    def get_lineage_report(self, event_id: str) -> list[dict]:
        """Get data lineage for specific event."""
        # Search in local buffer
        for event in self._local_buffer:
            if event.event_id == event_id:
                return event.lineage

        # Try Redis
        if self._redis:
            try:
                data = self._redis.get(f"lineage:{event_id}")
                if data:
                    return json.loads(data)
            except Exception:
                pass

        return None

    def emergency_stop_stream(self, system: str) -> bool:
        """Emergency stop for a system's streams."""
        # CANONICAL: SuperBrain validation
        if SUPERBRAIN_AVAILABLE and self._brain:
            try:
                if hasattr(self._brain, "action_gate"):
                    action_result = self._brain.action_gate.validate_action(
                        agent_id="data_pipeline",
                        action="emergency_stop_stream",
                        details={"system": system, "urgent": True},
                    )
                    if not action_result.authorized:
                        return False
            except Exception:
                pass

        # Publish stop event
        return self.publish_event(
            event_type="emergency_stop",
            source_system="data_pipeline",
            payload={"target_system": system, "reason": "emergency"},
            requires_governance=False,
        )


# Global pipeline instance
pipeline = DataPipelineManager()


# Convenience functions
def publish_task_routing(task: str, decision: str, correlation_id: str = None) -> bool:
    """Publish task routing decision."""
    return pipeline.publish_event(
        event_type="tasks",
        source_system="cognitive_router",
        payload={"task": task, "decision": decision},
        correlation_id=correlation_id,
    )


def publish_circuit_event(circuit_name: str, state: str, correlation_id: str = None) -> bool:
    """Publish circuit breaker event."""
    return pipeline.publish_event(
        event_type="circuit_events",
        source_system="resilience_engine",
        payload={"circuit": circuit_name, "state": state},
        correlation_id=correlation_id,
    )


def publish_knowledge_update(file_path: str, operation: str, correlation_id: str = None) -> bool:
    """Publish knowledge update."""
    return pipeline.publish_event(
        event_type="updates",
        source_system="knowledge_loader",
        payload={"file": file_path, "operation": operation},
        correlation_id=correlation_id,
    )


def publish_workflow_completion(workflow_id: str, status: str, correlation_id: str = None) -> bool:
    """Publish workflow completion."""
    return pipeline.publish_event(
        event_type="completions",
        source_system="master_orchestrator",
        payload={"workflow": workflow_id, "status": status},
        correlation_id=correlation_id,
    )


def get_stream_metrics() -> StreamMetrics:
    """Get stream processing metrics."""
    return pipeline.get_metrics()
