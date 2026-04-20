"""AMOS ML Model Registry.

MLflow-based model versioning, staging, and deployment tracking.

Author: AMOS ML Engineering Team
Version: 2.0.0
"""

import os
from dataclasses import dataclass
from datetime import datetime, timezone
UTC = timezone.utc, timezone

UTC = UTC
from enum import Enum
from typing import Any
from uuid import uuid4

import mlflow
from mlflow.tracking import MlflowClient


class ModelStage(Enum):
    """Model lifecycle stages."""

    NONE = "None"
    STAGING = "Staging"
    PRODUCTION = "Production"
    ARCHIVED = "Archived"


class ModelFramework(Enum):
    """Supported ML frameworks."""

    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    SKLEARN = "sklearn"
    ONNX = "onnx"
    HUGGINGFACE = "huggingface"


@dataclass
class ModelVersion:
    """Model version metadata."""

    name: str
    version: int
    stage: ModelStage
    framework: ModelFramework
    metrics: dict[str, float]
    parameters: dict[str, Any]
    tags: dict[str, str]
    run_id: str
    created_at: datetime
    artifact_uri: str
    description: str = ""


@dataclass
class Experiment:
    """ML experiment metadata."""

    experiment_id: str
    name: str
    artifact_location: str
    lifecycle_stage: str
    created_at: datetime


class ModelRegistry:
    """MLflow model registry for equation ML models."""

    def __init__(
        self,
        tracking_uri: str = None,
        registry_uri: str = None,
    ):
        """Initialize model registry.

        Args:
            tracking_uri: MLflow tracking server URI
            registry_uri: MLflow model registry URI
        """
        self.tracking_uri = tracking_uri or os.getenv(
            "MLFLOW_TRACKING_URI", "http://localhost:5000"
        )
        self.registry_uri = registry_uri or os.getenv(
            "MLFLOW_REGISTRY_URI", "postgresql://mlflow:mlflow@localhost:5432/mlflow"
        )

        mlflow.set_tracking_uri(self.tracking_uri)
        mlflow.set_registry_uri(self.registry_uri)
        self.client = MlflowClient()

    def create_experiment(
        self,
        name: str,
        artifact_location: str = None,
        tags: dict[str, Any] = None,
    ) -> str:
        """Create new ML experiment.

        Args:
            name: Experiment name
            artifact_location: S3/artifact storage path
            tags: Experiment metadata tags

        Returns:
            Experiment ID
        """
        experiment_id = self.client.create_experiment(
            name=name,
            artifact_location=artifact_location,
            tags=tags or {},
        )
        return experiment_id

    def get_experiment(self, experiment_id: str) -> Experiment:
        """Get experiment by ID."""
        try:
            exp = self.client.get_experiment(experiment_id)
            return Experiment(
                experiment_id=exp.experiment_id,
                name=exp.name,
                artifact_location=exp.artifact_location,
                lifecycle_stage=exp.lifecycle_stage,
                created_at=datetime.fromtimestamp(exp.creation_time / 1000, tz=timezone.utc)
                if exp.creation_time
                else datetime.now(timezone.utc),
            )
        except Exception:
            return None

    def start_run(
        self,
        experiment_id: str = None,
        run_name: str = None,
        tags: dict[str, Any] = None,
    ) -> str:
        """Start ML training run.

        Returns:
            Run ID
        """
        run = self.client.create_run(
            experiment_id=experiment_id,
            run_name=run_name or f"run-{uuid4().hex[:8]}",
            tags=tags or {},
        )
        return run.info.run_id

    def log_metrics(self, run_id: str, metrics: dict[str, float]) -> None:
        """Log metrics for run."""
        for key, value in metrics.items():
            self.client.log_metric(run_id, key, value)

    def log_params(self, run_id: str, params: dict[str, Any]) -> None:
        """Log parameters for run."""
        for key, value in params.items():
            self.client.log_param(run_id, key, value)

    def log_artifact(self, run_id: str, local_path: str, artifact_path: str = None) -> None:
        """Upload artifact to run."""
        self.client.log_artifact(run_id, local_path, artifact_path)

    def log_model(
        self,
        run_id: str,
        model_path: str,
        model_name: str,
        framework: ModelFramework,
        signature: Any = None,
        input_example: Any = None,
        code_paths: list[str] = None,
    ) -> None:
        """Log and register model.

        Args:
            run_id: MLflow run ID
            model_path: Local path to model
            model_name: Registered model name
            framework: ML framework used
            signature: Model input/output signature
            input_example: Example input for signature inference
            code_paths: Additional code dependencies
        """
        # Log model with framework-specific flavor
        if framework == ModelFramework.SKLEARN:
            import mlflow.sklearn

            mlflow.sklearn.log_model(
                sk_model=model_path,
                artifact_path="model",
                registered_model_name=model_name,
                signature=signature,
                input_example=input_example,
                code_paths=code_paths,
            )
        elif framework == ModelFramework.PYTORCH:
            import mlflow.pytorch

            mlflow.pytorch.log_model(
                pytorch_model=model_path,
                artifact_path="model",
                registered_model_name=model_name,
                signature=signature,
                input_example=input_example,
            )
        elif framework == ModelFramework.HUGGINGFACE:
            import mlflow.transformers

            mlflow.transformers.log_model(
                transformers_model=model_path,
                artifact_path="model",
                registered_model_name=model_name,
                signature=signature,
                input_example=input_example,
            )
        else:
            # Generic pyfunc model
            mlflow.pyfunc.log_model(
                artifact_path="model",
                python_model=model_path,
                registered_model_name=model_name,
                signature=signature,
                input_example=input_example,
                code_paths=code_paths,
            )

    def register_model(
        self,
        model_uri: str,
        name: str,
        tags: dict[str, Any] = None,
        description: str = "",
    ) -> ModelVersion:
        """Register model from run artifacts."""
        model_version = mlflow.register_model(
            model_uri=model_uri,
            name=name,
            tags=tags or {},
            description=description,
        )

        return ModelVersion(
            name=name,
            version=model_version.version,
            stage=ModelStage.NONE,
            framework=ModelFramework.SKLEARN,  # Detected from artifact
            metrics={},
            parameters={},
            tags=tags or {},
            run_id=model_version.run_id,
            created_at=datetime.now(timezone.utc),
            artifact_uri=model_version.source,
            description=description,
        )

    def transition_stage(
        self,
        name: str,
        version: int,
        stage: ModelStage,
        description: str = "",
    ) -> ModelVersion:
        """Transition model to new stage."""
        self.client.transition_model_version_stage(
            name=name,
            version=version,
            stage=stage.value,
            archive_existing_versions=(stage == ModelStage.PRODUCTION),
        )

        if description:
            self.client.update_model_version(
                name=name,
                version=version,
                description=description,
            )

        mv = self.client.get_model_version(name, version)
        return ModelVersion(
            name=name,
            version=version,
            stage=stage,
            framework=ModelFramework.SKLEARN,  # Parse from tags
            metrics={},  # Load from run
            parameters={},  # Load from run
            tags=dict(mv.tags) if mv.tags else {},
            run_id=mv.run_id,
            created_at=datetime.fromtimestamp(mv.creation_timestamp / 1000, tz=timezone.utc),
            artifact_uri=mv.source,
            description=description or mv.description,
        )

    def get_model_version(self, name: str, version: int) -> ModelVersion:
        """Get specific model version."""
        try:
            mv = self.client.get_model_version(name, version)
            return ModelVersion(
                name=name,
                version=version,
                stage=ModelStage(mv.current_stage),
                framework=ModelFramework.SKLEARN,
                metrics={},
                parameters={},
                tags=dict(mv.tags) if mv.tags else {},
                run_id=mv.run_id,
                created_at=datetime.fromtimestamp(mv.creation_timestamp / 1000, tz=timezone.utc),
                artifact_uri=mv.source,
                description=mv.description,
            )
        except Exception:
            return None

    def get_production_model(self, name: str) -> ModelVersion:
        """Get current production model."""
        try:
            latest_versions = self.client.get_latest_versions(name, stages=["Production"])
            if not latest_versions:
                return None

            mv = latest_versions[0]
            return ModelVersion(
                name=name,
                version=mv.version,
                stage=ModelStage.PRODUCTION,
                framework=ModelFramework(mv.tags.get("framework", "sklearn")),
                metrics={},
                parameters={},
                tags=dict(mv.tags) if mv.tags else {},
                run_id=mv.run_id,
                created_at=datetime.fromtimestamp(mv.creation_timestamp / 1000, tz=timezone.utc),
                artifact_uri=mv.source,
                description=mv.description,
            )
        except Exception:
            return None

    def list_models(self, name: str = None) -> list[ModelVersion]:
        """List all model versions."""

        models = []
        registered_models = self.client.search_registered_models(
            filter_string=f"name='{name}'" if name else None
        )

        for rm in registered_models:
            for mv in rm.latest_versions:
                models.append(
                    ModelVersion(
                        name=rm.name,
                        version=mv.version,
                        stage=ModelStage(mv.current_stage),
                        framework=ModelFramework.SKLEARN,
                        metrics={},
                        parameters={},
                        tags=dict(mv.tags) if mv.tags else {},
                        run_id=mv.run_id,
                        created_at=datetime.fromtimestamp(
                            mv.creation_timestamp / 1000, tz=timezone.utc
                        ),
                        artifact_uri=mv.source,
                        description=mv.description,
                    )
                )

        return models

    def delete_model_version(self, name: str, version: int) -> None:
        """Delete model version."""
        self.client.delete_model_version(name, version)

    def load_model(self, model_uri: str) -> Any:
        """Load model for inference.

        Args:
            model_uri: models:/{model_name}/{stage} or run:/.../model

        Returns:
            Loaded model object
        """
        return mlflow.pyfunc.load_model(model_uri)

    def compare_versions(
        self,
        name: str,
        version1: int,
        version2: int,
    ) -> dict[str, Any]:
        """Compare two model versions."""
        mv1 = self.get_model_version(name, version1)
        mv2 = self.get_model_version(name, version2)

        if not mv1 or not mv2:
            raise ValueError("Model version not found")

        # Load runs for metrics comparison
        run1 = self.client.get_run(mv1.run_id)
        run2 = self.client.get_run(mv2.run_id)

        metrics1 = run1.data.metrics
        metrics2 = run2.data.metrics

        return {
            "version1": {"version": version1, "metrics": metrics1, "stage": mv1.stage.value},
            "version2": {"version": version2, "metrics": metrics2, "stage": mv2.stage.value},
            "metric_diff": {
                k: metrics2.get(k, 0) - metrics1.get(k, 0)
                for k in set(metrics1.keys()) | set(metrics2.keys())
            },
        }

    def health_check(self) -> dict[str, Any]:
        """Check registry connectivity."""
        try:
            # Try to list experiments
            experiments = self.client.search_experiments()
            return {
                "status": "healthy",
                "tracking_uri": self.tracking_uri,
                "experiments_count": len(experiments),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "tracking_uri": self.tracking_uri,
            }


class ModelPromoter:
    """Automated model promotion based on metrics."""

    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    def auto_promote(
        self,
        model_name: str,
        metric_thresholds: dict[str, float],
        required_metrics: list[str],
    ) -> ModelVersion:
        """Auto-promote model to production if metrics meet thresholds.

        Args:
            model_name: Model to evaluate
            metric_thresholds: {metric_name: min_value} requirements
            required_metrics: Metrics that must exist

        Returns:
            Promoted model version or None
        """
        # Get latest staging model
        versions = self.registry.list_models(model_name)
        staging_versions = [v for v in versions if v.stage == ModelStage.STAGING]

        if not staging_versions:
            return None

        latest = max(staging_versions, key=lambda v: v.version)

        # Load run metrics
        run = self.registry.client.get_run(latest.run_id)
        metrics = run.data.metrics

        # Validate required metrics exist
        for metric in required_metrics:
            if metric not in metrics:
                return None

        # Check thresholds
        for metric, threshold in metric_thresholds.items():
            if metrics.get(metric, 0) < threshold:
                return None

        # Promote to production
        return self.registry.transition_stage(
            name=model_name,
            version=latest.version,
            stage=ModelStage.PRODUCTION,
            description=f"Auto-promoted: metrics {metrics}",
        )
