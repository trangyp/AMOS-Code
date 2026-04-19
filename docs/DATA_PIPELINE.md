# AMOS SuperBrain Data Pipeline v2.0.0

## Overview

Event streaming infrastructure with SuperBrain governance for real-time data flow across all 12 systems. Supports stream processing, data lineage tracking, and governance-controlled message flows.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA PIPELINE LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   Kafka      │  │   Redis      │  │   Governance       │   │
│  │  (Primary)    │  │ (Fallback)   │  │   Validation       │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐           ┌────▼────┐           ┌────▼────┐
   │Publish  │           │Process  │           │Lineage  │
   │Events   │           │Stream   │           │Track    │
   └─────────┘           └─────────┘           └─────────┘
```

---

## Event Topics

### Governance Topics

| Topic | Description | Retention |
|-------|-------------|-----------|
| `superbrain.events` | Governance events | 7 days |
| `superbrain.audit` | Audit trail | 365 days |

### System Topics (12 Systems)

| System | Topics |
|--------|--------|
| **Cognitive Router** | `cognitive_router.tasks`, `cognitive_router.decisions` |
| **Resilience Engine** | `resilience_engine.circuit_events`, `resilience_engine.metrics` |
| **Knowledge Loader** | `knowledge_loader.updates`, `knowledge_loader.queries` |
| **Master Orchestrator** | `master_orchestrator.workflows`, `master_orchestrator.completions` |
| **Production API** | `production_api.requests`, `production_api.responses` |
| **GraphQL API** | `graphql_api.mutations`, `graphql_api.subscriptions` |
| **Agent Messaging** | `agent_messaging.messages` |
| **Agent Observability** | `agent_observability.telemetry` |
| **UBI Engine** | `ubi_engine.analyses`, `ubi_engine.results` |
| **AMOS Tools** | `amos_tools.executions` |
| **Audit Exporter** | `audit_exporter.exports` |

---

## Usage

### Publishing Events

```python
from backend.data_pipeline.streaming import pipeline, StreamEvent

# Publish event with governance
event_id = pipeline.publish_event(
    event_type="tasks",
    source_system="cognitive_router",
    payload={"task": "analyze_data", "priority": "high"},
    target_system="master_orchestrator",
    requires_governance=True
)

# Convenience functions
from backend.data_pipeline.streaming import (
    publish_task_routing,
    publish_circuit_event,
    publish_knowledge_update,
    publish_workflow_completion
)

# Publish task routing
publish_task_routing(
    task="user_query",
    decision="cognitive_router",
    correlation_id="workflow-123"
)

# Publish circuit event
publish_circuit_event(
    circuit_name="llm_provider",
    state="OPEN",
    correlation_id="workflow-123"
)
```

### Subscribing to Streams

```python
from backend.data_pipeline.streaming import pipeline, StreamEvent

def handle_routing_decision(event: StreamEvent):
    print(f"Routing: {event.payload['decision']}")
    # Process event...

# Subscribe to routing decisions
pipeline.subscribe_to_stream(
    "cognitive_router.decisions",
    handle_routing_decision
)
```

### Stream Processing

```python
# Process single event
from backend.data_pipeline.streaming import pipeline

event = StreamEvent(
    event_id="evt-123",
    event_type="analysis",
    source_system="ubi_engine",
    payload={"result": "coherent"}
)

success = pipeline.process_event(event)
```

---

## Data Lineage

### Automatic Lineage Tracking

Every event tracks its journey through the pipeline:

```python
{
  "event_id": "evt-abc123",
  "lineage": [
    {"stage": "published", "timestamp": "2026-04-16T18:30:00Z", "system": "data_pipeline"},
    {"stage": "processing", "timestamp": "2026-04-16T18:30:01Z", "system": "data_pipeline"},
    {"stage": "consumed", "timestamp": "2026-04-16T18:30:02Z", "system": "cognitive_router"}
  ]
}
```

### Query Lineage

```python
from backend.data_pipeline.streaming import pipeline

# Get lineage for specific event
lineage = pipeline.get_lineage_report("evt-abc123")
for stage in lineage:
    print(f"{stage['stage']} at {stage['timestamp']}")
```

---

## Stream Topologies

### Pre-configured Topologies

```python
from backend.data_pipeline.streaming import pipeline

# Get topology for cognitive router
topology = pipeline.create_stream_topology("cognitive_router")
# Returns:
# {
#   "system": "cognitive_router",
#   "input_topics": ["master_orchestrator.workflows"],
#   "output_topics": ["cognitive_router.decisions", "resilience_engine.circuit_events"],
#   "processors": [],
#   "governance_required": True
# }
```

---

## Governance Integration

### Event Validation

All events are validated via SuperBrain ActionGate:

```python
# Event is automatically validated on publish
action_result = brain.action_gate.validate_action(
    agent_id="cognitive_router",
    action="stream_event_tasks",
    details={
        "event_id": event_id,
        "target": "master_orchestrator",
        "payload_size": 1024
    }
)

if not action_result.authorized:
    event_blocked = True
```

### Metrics

| Metric | Description |
|--------|-------------|
| `total_events` | Total events published |
| `governance_allowed` | Events allowed by governance |
| `governance_blocked` | Events blocked by governance |
| `processing_latency_ms` | Average processing time |
| `events_per_second` | Current throughput |
| `errors` | Processing errors |

```python
from backend.data_pipeline.streaming import get_stream_metrics

metrics = get_stream_metrics()
print(f"Events/sec: {metrics.events_per_second}")
print(f"Blocked: {metrics.governance_blocked}")
print(f"Latency: {metrics.processing_latency_ms}ms")
```

---

## Emergency Procedures

### Stream Kill Switch

Emergency stop for a system's streams:

```python
from backend.data_pipeline.streaming import pipeline

# Stop all streams for cognitive router
pipeline.emergency_stop_stream("cognitive_router")
```

### Fallback Strategy

1. **Primary**: Kafka
2. **Fallback**: Redis pub/sub
3. **Last Resort**: Local buffer

---

## Monitoring

### CloudWatch Integration

```yaml
# CloudWatch metrics
DataPipelineMetrics:
  - TotalEvents
  - EventsPerSecond
  - GovernanceBlocked
  - ProcessingLatency
  - ErrorRate
```

### Alarms

```yaml
HighErrorRate:
  MetricName: ErrorRate
  Threshold: 5
  EvaluationPeriods: 3
  
HighBlockedRate:
  MetricName: GovernanceBlocked
  Threshold: 100
  EvaluationPeriods: 1
```

---

## Best Practices

### 1. Always Use Correlation IDs

```python
# Good - enables tracing
pipeline.publish_event(
    event_type="analysis",
    source_system="ubi_engine",
    payload={...},
    correlation_id="workflow-123"  # Same across all events
)

# Bad - lost traceability
pipeline.publish_event(
    event_type="analysis",
    source_system="ubi_engine",
    payload={...}
)
```

### 2. Enable Governance for Critical Events

```python
# Good - validated by SuperBrain
pipeline.publish_event(
    ...,
    requires_governance=True  # For critical events
)

# Acceptable - for telemetry
pipeline.publish_event(
    ...,
    requires_governance=False  # For non-critical metrics
)
```

### 3. Handle Processing Errors

```python
def safe_handler(event):
    try:
        process(event)
    except Exception as e:
        # Error is automatically logged
        # Error event is published
        pass

pipeline.subscribe_to_stream("topic", safe_handler)
```

---

**Maintainer:** Trang Phan  
**Last Updated:** 2026-04-16  
**Version:** 2.0.0
