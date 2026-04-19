# AMOS SuperBrain ML Model Serving & AI Inference Layer v2.0.0

## Overview

Model registry, feature store, and inference optimization for all 251+ AMOS engines. Supports A/B testing, model versioning, and SuperBrain governance.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 ML INFERENCE LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │    Model     │  │   Feature    │  │   Inference        │   │
│  │   Registry   │  │    Store     │  │    Service         │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│         │                 │                      │              │
│         └─────────────────┴──────────────────────┘              │
│                              │                                  │
│                    ┌────────▼────────┐                         │
│                    │   A/B Testing   │                         │
│                    │    Shadow Mode  │                         │
│                    └─────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Model Registry** | Version control for models | Semantic versioning, metadata, status tracking |
| **Feature Store** | Centralized feature management | 8 pre-defined AMOS features, online/offline |
| **Inference Service** | Execute predictions | Real-time, batch, shadow modes |
| **A/B Testing** | Model comparison | Traffic splitting, statistical analysis |

---

## Model Registry

### Model Status Lifecycle

```
DEVELOPMENT → STAGING → PRODUCTION → ARCHIVED
```

### Supported Frameworks

| Framework | Description |
|-----------|-------------|
| `pytorch` | PyTorch models |
| `tensorflow` | TensorFlow models |
| `sklearn` | Scikit-learn models |
| `onnx` | ONNX format |
| `custom` | AMOS custom engines |

### Usage

```python
from backend.ml_inference.model_serving import register_model

# Register new model version
register_model(
    model_id="cognitive_router",
    version="2.0.0",
    framework="custom",
    features_required=["cognitive.task_complexity", "cognitive.domain_confidence"],
    config={"batch_size": 32},
    status="production"
)
```

---

## Feature Store

### Pre-defined AMOS Features

| Feature | Data Type | Source | TTL |
|---------|-----------|--------|-----|
| `knowledge.embedding` | vector:768 | knowledge_loader | 1h |
| `knowledge.category` | string | knowledge_loader | 1h |
| `cognitive.task_complexity` | float | cognitive_router | 5m |
| `cognitive.domain_confidence` | float | cognitive_router | 5m |
| `ubi.state_vector` | vector:6 | ubi_engine | 1m |
| `ubi.coherence_score` | float | ubi_engine | 1m |
| `agent.message_sentiment` | float:-1:1 | agent_messaging | 5m |
| `agent.activity_level` | float | agent_observability | 1m |
| `system.load_average` | float | system_metrics | 30s |
| `system.memory_usage` | float:0:100 | system_metrics | 30s |

### Usage

```python
from backend.ml_inference.model_serving import get_feature, set_feature

# Store feature
set_feature(
    feature_name="cognitive.task_complexity",
    entity_id="task-123",
    value=0.85,
    ttl=300  # 5 minutes
)

# Retrieve feature
complexity = get_feature(
    feature_name="cognitive.task_complexity",
    entity_id="task-123",
    default=0.5
)
```

---

## Inference Service

### Inference Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `realtime` | Synchronous prediction | API responses |
| `batch` | Asynchronous bulk processing | Data pipelines |
| `shadow` | Test new models without impact | Model validation |

### Usage

```python
from backend.ml_inference.model_serving import predict

# Real-time inference
result = predict(
    model_id="cognitive_router",
    input_data={"task_description": "analyze data", "entity_id": "task-123"},
    version="2.0.0",
    mode="realtime"
)

print(f"Prediction: {result.prediction}")
print(f"Latency: {result.latency_ms}ms")
print(f"Confidence: {result.confidence}")
```

---

## A/B Testing

### Create A/B Test

```python
from backend.ml_inference.model_serving import create_ab_test

# Create test between two model versions
create_ab_test(
    test_id="router_v2_test",
    model_a_id="cognitive_router_v1",
    model_b_id="cognitive_router_v2",
    traffic_split=0.5  # 50/50 split
)
```

### Predict with A/B Test

```python
from backend.ml_inference.model_serving import inference_service

# Route traffic based on test configuration
result = inference_service.predict_with_ab_test(
    test_id="router_v2_test",
    input_data={"task": "route request"},
    entity_id="user-123"  # Used for consistent bucketing
)

# Result includes A/B test metadata
print(f"Model used: {result.metadata['ab_test_bucket']}")  # A or B
```

---

## Integration with SuperBrain

All inference operations are validated via ActionGate:

```python
# CANONICAL: Inference validation
action_result = brain.action_gate.validate_action(
    agent_id="inference_service",
    action="model_predict",
    details={
        "model_id": "cognitive_router",
        "version": "2.0.0",
        "tenant_id": "tenant-123"
    }
)
```

---

## Events Published

| Event | Description |
|-------|-------------|
| `feature_updated` | Feature value changed |
| `model_registered` | New model version added |
| `model_status_changed` | Model status updated |
| `model_inference` | Prediction executed |
| `ab_test_created` | New A/B test started |

---

## Best Practices

### 1. Use Feature Store for Consistency

```python
# Good - use feature store
def get_task_features(task_id):
    return {
        "complexity": get_feature("cognitive.task_complexity", task_id),
        "confidence": get_feature("cognitive.domain_confidence", task_id)
    }

# Bad - compute features inline every time
def get_task_features_bad(task_id):
    return compute_features_expensive(task_id)  # Slow!
```

### 2. Version Models Explicitly

```python
# Good - explicit version
predict(model_id="router", version="2.0.0", ...)

# Risky - implicit latest
predict(model_id="router", ...)  # May change unexpectedly
```

### 3. Use Shadow Mode for Testing

```python
# Test new model in production without impact
predict(
    model_id="router_v2",
    mode="shadow"  # Runs but doesn't affect response
)
```

---

## Statistics

```python
from backend.ml_inference.model_serving import inference_service

stats = inference_service.get_inference_stats()
print(f"Active A/B tests: {stats['ab_tests_active']}")
print(f"Models registered: {stats['models_registered']}")
print(f"Features available: {stats['features_available']}")
```

---

**Maintainer:** Trang Phan  
**Last Updated:** 2026-04-16  
**Version:** 2.0.0
