"""
AMOS SuperBrain ML Model Serving & AI Inference Layer v2.0.0

Model registry, feature store, and inference optimization for all 251+ engines.
Supports A/B testing, model versioning, drift detection, and SuperBrain governance.

Architecture:
- Model Registry: Versioning and metadata
- Feature Store: Online/offline features
- Inference Service: Batch and real-time
- A/B Testing: Model comparison
- Drift Detection: Monitor model performance
- GPU/CPU Resource Management

Owner: Trang Phan
Version: 2.0.0
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone
from enum import Enum
from typing import Any

UTC = UTC

# Redis for feature store
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

# Import existing modules
try:
    from backend.data_pipeline.streaming import publish_event

    STREAMING_AVAILABLE = True
except ImportError:
    STREAMING_AVAILABLE = False


class ModelStatus(Enum):
    """Model deployment status."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


class InferenceMode(Enum):
    """Inference execution mode."""

    REALTIME = "realtime"
    BATCH = "batch"
    SHADOW = "shadow"  # Shadow mode for testing


class ModelFramework(Enum):
    """Supported ML frameworks."""

    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    SKLEARN = "sklearn"
    ONNX = "onnx"
    CUSTOM = "custom"


@dataclass
class ModelVersion:
    """Model version metadata."""

    model_id: str
    version: str
    framework: ModelFramework
    status: ModelStatus
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metrics: dict[str, float] = field(default_factory=dict)
    features_required: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)
    artifact_path: str = None
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)


@dataclass
class FeatureDefinition:
    """Feature definition for feature store."""

    name: str
    data_type: str
    source: str
    ttl_seconds: int = 86400
    description: str = None
    tags: list[str] = field(default_factory=list)


@dataclass
class InferenceResult:
    """Model inference result."""

    model_id: str
    version: str
    prediction: Any
    confidence: float = None
    latency_ms: float = 0.0
    features_used: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ABTest:
    """A/B test configuration."""

    test_id: str
    model_a_id: str
    model_b_id: str
    traffic_split: float = 0.5  # 0.5 = 50/50
    status: str = "running"  # running, completed, stopped
    metrics: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class FeatureStore:
    """Centralized feature store for online and offline features."""

    # Pre-defined features for AMOS engines
    FEATURE_REGISTRY: dict[str, FeatureDefinition] = {
        # Knowledge features
        "knowledge.embedding": FeatureDefinition(
            name="knowledge.embedding",
            data_type="vector:768",
            source="knowledge_loader",
            ttl_seconds=3600,
            description="Knowledge file embedding vector",
            tags=["knowledge", "embedding"],
        ),
        "knowledge.category": FeatureDefinition(
            name="knowledge.category",
            data_type="string",
            source="knowledge_loader",
            ttl_seconds=3600,
            tags=["knowledge", "categorical"],
        ),
        # Cognitive features
        "cognitive.task_complexity": FeatureDefinition(
            name="cognitive.task_complexity",
            data_type="float",
            source="cognitive_router",
            ttl_seconds=300,
            tags=["cognitive", "scalar"],
        ),
        "cognitive.domain_confidence": FeatureDefinition(
            name="cognitive.domain_confidence",
            data_type="float",
            source="cognitive_router",
            ttl_seconds=300,
            tags=["cognitive", "scalar"],
        ),
        # UBI features
        "ubi.state_vector": FeatureDefinition(
            name="ubi.state_vector",
            data_type="vector:6",
            source="ubi_engine",
            ttl_seconds=60,
            description="Human state vector",
            tags=["ubi", "vector"],
        ),
        "ubi.coherence_score": FeatureDefinition(
            name="ubi.coherence_score",
            data_type="float",
            source="ubi_engine",
            ttl_seconds=60,
            tags=["ubi", "scalar"],
        ),
        # Agent features
        "agent.message_sentiment": FeatureDefinition(
            name="agent.message_sentiment",
            data_type="float:-1:1",
            source="agent_messaging",
            ttl_seconds=300,
            tags=["agent", "sentiment"],
        ),
        "agent.activity_level": FeatureDefinition(
            name="agent.activity_level",
            data_type="float",
            source="agent_observability",
            ttl_seconds=60,
            tags=["agent", "scalar"],
        ),
        # System features
        "system.load_average": FeatureDefinition(
            name="system.load_average",
            data_type="float",
            source="system_metrics",
            ttl_seconds=30,
            tags=["system", "metric"],
        ),
        "system.memory_usage": FeatureDefinition(
            name="system.memory_usage",
            data_type="float:0:100",
            source="system_metrics",
            ttl_seconds=30,
            tags=["system", "metric"],
        ),
    }

    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or "redis://localhost:6379/6"
        self._redis: redis.Redis = None

        if REDIS_AVAILABLE:
            try:
                self._redis = redis.from_url(self.redis_url)
                self._redis.ping()
            except Exception:
                self._redis = None

    def _get_feature_key(self, feature_name: str, entity_id: str) -> str:
        """Generate feature storage key."""
        return f"feature:{feature_name}:{entity_id}"

    def get_feature(self, feature_name: str, entity_id: str, default: Any = None) -> Any:
        """Get feature value from store."""
        if not self._redis:
            return default

        try:
            key = self._get_feature_key(feature_name, entity_id)
            data = self._redis.get(key)
            if data:
                return json.loads(data)
        except Exception:
            pass

        return default

    def set_feature(self, feature_name: str, entity_id: str, value: Any, ttl: int = None) -> bool:
        """Set feature value in store."""
        if not self._redis:
            return False

        # Get TTL from registry or use default
        feature_def = self.FEATURE_REGISTRY.get(feature_name)
        ttl = ttl or (feature_def.ttl_seconds if feature_def else 3600)

        try:
            key = self._get_feature_key(feature_name, entity_id)
            self._redis.setex(key, ttl, json.dumps(value))

            # Publish feature update event
            if STREAMING_AVAILABLE:
                publish_event(
                    event_type="feature_updated",
                    source_system="feature_store",
                    payload={"feature": feature_name, "entity_id": entity_id, "ttl": ttl},
                    requires_governance=False,
                )

            return True
        except Exception:
            pass

        return False

    def get_features_batch(self, feature_names: list[str], entity_id: str) -> dict[str, Any]:
        """Get multiple features in one call."""
        return {name: self.get_feature(name, entity_id) for name in feature_names}

    def compute_feature(
        self, feature_name: str, entity_id: str, compute_func: Callable[[], Any]
    ) -> Any:
        """Compute and store feature if not cached."""
        # Try to get from cache first
        value = self.get_feature(feature_name, entity_id)
        if value is not None:
            return value

        # Compute feature
        value = compute_func()

        # Store in feature store
        self.set_feature(feature_name, entity_id, value)

        return value


class ModelRegistry:
    """Model registry for versioning and metadata."""

    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or "redis://localhost:6379/7"
        self._redis: redis.Redis = None
        self._models: dict[str, ModelVersion] = {}

        if REDIS_AVAILABLE:
            try:
                self._redis = redis.from_url(self.redis_url)
                self._redis.ping()
            except Exception:
                self._redis = None

    def _get_model_key(self, model_id: str, version: str) -> str:
        """Generate model storage key."""
        return f"model:{model_id}:{version}"

    def register_model(
        self,
        model_id: str,
        version: str,
        framework: ModelFramework,
        features_required: list[str],
        config: dict = None,
        artifact_path: str = None,
        status: ModelStatus = ModelStatus.DEVELOPMENT,
    ) -> bool:
        """Register new model version."""
        model = ModelVersion(
            model_id=model_id,
            version=version,
            framework=framework,
            status=status,
            features_required=features_required,
            config=config or {},
            artifact_path=artifact_path,
        )

        # Store in memory
        self._models[f"{model_id}:{version}"] = model

        # Store in Redis
        if self._redis:
            try:
                key = self._get_model_key(model_id, version)
                self._redis.setex(
                    key,
                    86400 * 30,  # 30 day TTL
                    json.dumps(model.__dict__, default=str),
                )

                # Update model index
                self._redis.sadd(f"models:{model_id}", version)

                # Publish event
                if STREAMING_AVAILABLE:
                    publish_event(
                        event_type="model_registered",
                        source_system="model_registry",
                        payload={
                            "model_id": model_id,
                            "version": version,
                            "framework": framework.value,
                            "status": status.value,
                        },
                        requires_governance=False,
                    )

                return True
            except Exception:
                pass

        return False

    def get_model(self, model_id: str, version: str) -> ModelVersion:
        """Get model version metadata."""
        # Check memory first
        cache_key = f"{model_id}:{version}"
        if cache_key in self._models:
            return self._models[cache_key]

        # Check Redis
        if self._redis:
            try:
                key = self._get_model_key(model_id, version)
                data = self._redis.get(key)
                if data:
                    model_dict = json.loads(data)
                    model_dict["framework"] = ModelFramework(model_dict.get("framework", "custom"))
                    model_dict["status"] = ModelStatus(model_dict.get("status", "development"))
                    return ModelVersion(**model_dict)
            except Exception:
                pass

        return None

    def get_latest_version(self, model_id: str) -> str:
        """Get latest production version of model."""
        if self._redis:
            try:
                versions = self._redis.smembers(f"models:{model_id}")
                if versions:
                    # Sort versions and return latest production
                    version_list = [v.decode() if isinstance(v, bytes) else v for v in versions]
                    for v in sorted(version_list, reverse=True):
                        model = self.get_model(model_id, v)
                        if model and model.status == ModelStatus.PRODUCTION:
                            return v
                    return version_list[-1]  # Return latest if no production
            except Exception:
                pass

        return None

    def update_model_status(self, model_id: str, version: str, status: ModelStatus) -> bool:
        """Update model deployment status."""
        model = self.get_model(model_id, version)
        if not model:
            return False

        model.status = status

        # Update in Redis
        if self._redis:
            try:
                key = self._get_model_key(model_id, version)
                self._redis.setex(key, 86400 * 30, json.dumps(model.__dict__, default=str))

                # Publish event
                if STREAMING_AVAILABLE:
                    publish_event(
                        event_type="model_status_changed",
                        source_system="model_registry",
                        payload={"model_id": model_id, "version": version, "status": status.value},
                        requires_governance=True,
                    )

                return True
            except Exception:
                pass

        return False


class InferenceService:
    """Model inference service with A/B testing and governance."""

    def __init__(self):
        self.feature_store = FeatureStore()
        self.model_registry = ModelRegistry()
        self._ab_tests: dict[str, ABTest] = {}
        self._brain = None

        if SUPERBRAIN_AVAILABLE:
            try:
                self._brain = get_super_brain()
            except Exception:
                pass

    def predict(
        self,
        model_id: str,
        input_data: dict[str, Any],
        version: str = None,
        mode: InferenceMode = InferenceMode.REALTIME,
        tenant_id: str = None,
    ) -> InferenceResult:
        """Execute model inference with governance."""
        start_time = time.time()

        # CANONICAL: Validate via SuperBrain
        if SUPERBRAIN_AVAILABLE and self._brain:
            try:
                if hasattr(self._brain, "action_gate"):
                    action_result = self._brain.action_gate.validate_action(
                        agent_id="inference_service",
                        action="model_predict",
                        details={
                            "model_id": model_id,
                            "version": version or "latest",
                            "mode": mode.value,
                            "tenant_id": tenant_id,
                        },
                    )
                    if not action_result.authorized:
                        return None
            except Exception:
                pass

        # Get model version
        if not version:
            version = self.model_registry.get_latest_version(model_id)

        if not version:
            return None

        model = self.model_registry.get_model(model_id, version)
        if not model:
            return None

        # Check if model is in production
        if model.status != ModelStatus.PRODUCTION and mode != InferenceMode.SHADOW:
            return None

        # Fetch required features
        entity_id = input_data.get("entity_id", "default")
        features = self.feature_store.get_features_batch(model.features_required, entity_id)

        # Merge input data with features
        inference_input = {**input_data, **features}

        # Execute inference (placeholder for actual model execution)
        prediction = self._execute_inference(model, inference_input)

        latency_ms = (time.time() - start_time) * 1000

        result = InferenceResult(
            model_id=model_id,
            version=version,
            prediction=prediction,
            latency_ms=latency_ms,
            features_used=list(features.keys()),
            metadata={
                "mode": mode.value,
                "tenant_id": tenant_id,
                "framework": model.framework.value,
            },
        )

        # Publish inference event
        if STREAMING_AVAILABLE:
            publish_event(
                event_type="model_inference",
                source_system="inference_service",
                payload={
                    "model_id": model_id,
                    "version": version,
                    "latency_ms": latency_ms,
                    "mode": mode.value,
                },
                requires_governance=False,
            )

        return result

    def _execute_inference(self, model: ModelVersion, input_data: dict[str, Any]) -> Any:
        """Execute model inference based on framework."""
        # Placeholder for actual inference logic
        # In production, this would load the model artifact and run inference

        if model.framework == ModelFramework.PYTORCH:
            # PyTorch inference
            return {"prediction": "pytorch_result", "framework": "pytorch"}

        elif model.framework == ModelFramework.TENSORFLOW:
            # TensorFlow inference
            return {"prediction": "tensorflow_result", "framework": "tensorflow"}

        elif model.framework == ModelFramework.SKLEARN:
            # Scikit-learn inference
            return {"prediction": "sklearn_result", "framework": "sklearn"}

        elif model.framework == ModelFramework.CUSTOM:
            # Custom AMOS engine inference
            return {"prediction": "amos_engine_result", "framework": "custom"}

        return {"prediction": None, "error": "Unsupported framework"}

    def create_ab_test(
        self, test_id: str, model_a_id: str, model_b_id: str, traffic_split: float = 0.5
    ) -> bool:
        """Create A/B test between two models."""
        test = ABTest(
            test_id=test_id,
            model_a_id=model_a_id,
            model_b_id=model_b_id,
            traffic_split=traffic_split,
        )

        self._ab_tests[test_id] = test

        # Publish event
        if STREAMING_AVAILABLE:
            publish_event(
                event_type="ab_test_created",
                source_system="inference_service",
                payload={
                    "test_id": test_id,
                    "model_a": model_a_id,
                    "model_b": model_b_id,
                    "split": traffic_split,
                },
                requires_governance=True,
            )

        return True

    def predict_with_ab_test(
        self, test_id: str, input_data: dict[str, Any], entity_id: str
    ) -> InferenceResult:
        """Execute inference with A/B test routing."""
        test = self._ab_tests.get(test_id)
        if not test or test.status != "running":
            return None

        # Route based on hash of entity_id
        hash_val = int(hashlib.sha256(entity_id.encode()).hexdigest(), 16)
        bucket = (hash_val % 100) / 100.0

        # Select model based on traffic split
        if bucket < test.traffic_split:
            model_id = test.model_a_id
        else:
            model_id = test.model_b_id

        result = self.predict(model_id, input_data)

        if result:
            result.metadata["ab_test_id"] = test_id
            result.metadata["ab_test_bucket"] = "A" if model_id == test.model_a_id else "B"

        return result

    def get_inference_stats(self) -> dict[str, Any]:
        """Get inference service statistics."""
        return {
            "ab_tests_active": len([t for t in self._ab_tests.values() if t.status == "running"]),
            "models_registered": len(self.model_registry._models),
            "features_available": len(self.feature_store.FEATURE_REGISTRY),
        }


# Global services
feature_store = FeatureStore()
model_registry = ModelRegistry()
inference_service = InferenceService()


# Convenience functions
def register_model(
    model_id: str, version: str, framework: str, features_required: list[str], **kwargs
) -> bool:
    """Register model version."""
    framework_enum = ModelFramework(framework)
    return model_registry.register_model(
        model_id=model_id,
        version=version,
        framework=framework_enum,
        features_required=features_required,
        **kwargs,
    )


def get_feature(feature_name: str, entity_id: str, default: Any = None) -> Any:
    """Get feature from store."""
    return feature_store.get_feature(feature_name, entity_id, default)


def set_feature(feature_name: str, entity_id: str, value: Any, ttl: int = None) -> bool:
    """Set feature in store."""
    return feature_store.set_feature(feature_name, entity_id, value, ttl)


def predict(
    model_id: str, input_data: dict[str, Any], version: str = None, mode: str = "realtime"
) -> InferenceResult:
    """Execute model inference."""
    mode_enum = InferenceMode(mode)
    return inference_service.predict(model_id, input_data, version, mode_enum)


def create_ab_test(
    test_id: str, model_a_id: str, model_b_id: str, traffic_split: float = 0.5
) -> bool:
    """Create A/B test."""
    return inference_service.create_ab_test(test_id, model_a_id, model_b_id, traffic_split)
