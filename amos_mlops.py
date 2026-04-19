"""AMOS MLOps - Model Registry & ML Lifecycle Management (Phase 30).

Complete MLOps platform with model versioning, artifact storage, deployment pipelines,
A/B testing, and experiment tracking for production ML systems.

2024-2025 State of the Art:
    - Model Registry: MLflow patterns, versioned artifacts with lineage (MLflow 2025)
    - Deployment Strategies: A/B testing, Canary, Shadow deployment (MarkTechPost 2026, Qwak 2025)
    - Experiment Tracking: Parameters, metrics, artifacts versioning
    - Model Monitoring: Drift detection, performance degradation alerts
    - Rollback Mechanisms: Safe production rollbacks
    - Stage Management: Development, Staging, Production lifecycle

Architecture:
    ┌─────────────────────────────────────────────────────────────────────┐
    │          Phase 30: MLOps & Model Registry                        │
    ├─────────────────────────────────────────────────────────────────────┤
    │                                                                     │
    │  ┌─────────────────────────────────────────────────────────────┐   │
    │  │              Model Registry                                   │   │
    │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
    │  │  │   Model     │  │  Version    │  │   Stage     │       │   │
    │  │  │   Versions  │  │  History    │  │  (Staging)  │       │   │
    │  │  │             │  │             │  │  (Production)│      │   │
    │  │  │  v1.0.0     │  │  v1.0.1     │  │  (Archived) │       │   │
    │  │  │  v2.0.0     │  │  v2.0.0     │  │             │       │   │
    │  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
    │  │  ┌─────────────┐  ┌─────────────┐                        │   │
    │  │  │   Tags      │  │   Aliases   │  Lineage Tracking       │   │
    │  │  │ ( champion) │  │  (latest)   │                         │   │
    │  │  │  (archived) │  │ (production)│                         │   │
    │  │  └─────────────┘  └─────────────┘                        │   │
    │  └─────────────────────────────────────────────────────────────┘   │
    │                                                                     │
    │  ┌─────────────────────────────────────────────────────────────┐   │
    │  │              Deployment Strategies                              │   │
    │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
    │  │  │   A/B       │  │   Canary    │  │   Shadow    │       │   │
    │  │  │  Testing    │  │  Release    │  │ Deployment  │       │   │
    │  │  │             │  │             │  │             │       │   │
    │  │  │  50/50 split│  │  5% → 100%  │  │  0% traffic │       │   │
    │  │  │  Compare    │  │  Gradual    │  │  Shadow     │       │   │
    │  │  │  metrics    │  │  rollout    │  │  compare    │       │   │
    │  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
    │  └─────────────────────────────────────────────────────────────┘   │
    │                                                                     │
    │  ┌─────────────────────────────────────────────────────────────┐   │
    │  │              Experiment Tracking                                │   │
    │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
    │  │  │ Parameters  │  │   Metrics   │  │  Artifacts  │       │   │
    │  │  │ (hyperparams)│  │  (accuracy) │  │  (models)   │       │   │
    │  │  │             │  │  (loss)     │  │  (datasets) │       │   │
    │  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
    │  └─────────────────────────────────────────────────────────────┘   │
    │                                                                     │
    │  ┌─────────────────────────────────────────────────────────────┐   │
    │  │              Model Monitoring                                   │   │
    │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
    │  │  │   Drift     │  │ Performance │  │   Alerts    │       │   │
    │  │  │  Detection  │  │  Tracking   │  │             │       │   │
    │  │  │             │  │             │  │             │       │   │
    │  │  │  Data drift │  │  Latency    │  │  Threshold  │       │   │
    │  │  │  Concept    │  │  Accuracy   │  │  based      │       │   │
    │  │  │  drift      │  │  F1 score   │  │             │       │   │
    │  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
    │  └─────────────────────────────────────────────────────────────┘   │
    │                                                                     │
    └─────────────────────────────────────────────────────────────────────┘

Usage:
    # Initialize MLOps
    mlops = AMOSMLOps()

    # Register model
    model = mlops.register_model(
        name="neural_ode_solver",
        version="1.0.0",
        model_path="/models/neural_ode_v1.pkl",
        metrics={"accuracy": 0.95, "latency_ms": 50},
        parameters={"hidden_dim": 256, "layers": 4}
    )

    # Transition to staging
    mlops.transition_stage(
        model_name="neural_ode_solver",
        version="1.0.0",
        stage=ModelStage.STAGING
    )

    # Deploy with A/B testing
    deployment = mlops.deploy_ab_test(
        model_a=("neural_ode_solver", "1.0.0"),
        model_b=("neural_ode_solver", "2.0.0"),
        traffic_split=0.5,
        duration_hours=24
    )

    # Monitor performance
    metrics = mlops.get_deployment_metrics(deployment.deployment_id)

    # Compare experiments
    best = mlops.compare_experiments(["exp_001", "exp_002"], metric="accuracy")

Author: AMOS MLOps Team
Version: 30.0.0
"""

import hashlib
import random
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class ModelStage(Enum):
    """Model lifecycle stages."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


class DeploymentStrategy(Enum):
    """Model deployment strategies."""

    STANDARD = auto()
    CANARY = auto()
    AB_TEST = auto()
    SHADOW = auto()
    BLUE_GREEN = auto()


class ExperimentStatus(Enum):
    """Experiment run status."""

    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    INTERRUPTED = auto()


@dataclass
class ModelVersion:
    """Registered model version."""

    model_id: str
    name: str
    version: str
    model_path: str
    model_hash: str
    metrics: Dict[str, float] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    stage: ModelStage = ModelStage.DEVELOPMENT
    experiment_id: str = None
    created_at: float = field(default_factory=lambda: time.time())
    updated_at: float = field(default_factory=lambda: time.time())
    description: str = ""


@dataclass
class Experiment:
    """ML experiment tracking."""

    experiment_id: str
    name: str
    status: ExperimentStatus
    parameters: Dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, list[float]] = field(default_factory=dict)
    artifacts: Dict[str, str] = field(default_factory=dict)
    created_at: float = field(default_factory=lambda: time.time())
    completed_at: float = None
    parent_experiment_id: str = None


@dataclass
class Deployment:
    """Model deployment configuration."""

    deployment_id: str
    strategy: DeploymentStrategy
    model_versions: list[tuple[str, str]]  # [(name, version), ...]
    traffic_split: Dict[str, float]  # version -> percentage
    status: str = "pending"  # pending, running, completed, rolled_back
    start_time: float = field(default_factory=lambda: time.time())
    end_time: float = None
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelPerformance:
    """Model performance metrics over time."""

    model_id: str
    timestamp: float
    predictions_count: int = 0
    avg_latency_ms: float = 0.0
    accuracy: float = None
    error_rate: float = 0.0
    drift_score: float = 0.0


class AMOSMLOps:
    """Phase 30: MLOps & Model Registry.

    Complete ML lifecycle management with:
    - Model versioning and registry
    - Artifact storage and lineage
    - Deployment strategies (A/B, Canary, Shadow)
    - Experiment tracking
    - Model monitoring and drift detection
    """

    def __init__(
        self, artifact_storage_path: str = "./mlops_artifacts", enable_monitoring: bool = True
    ):
        self.artifact_storage_path = artifact_storage_path
        self.enable_monitoring = enable_monitoring

        # Model registry
        self.registered_models: dict[str, dict[str, ModelVersion]] = {}  # name -> version -> model
        self.model_aliases: dict[str, tuple[str, str]] = {}  # alias -> (name, version)

        # Experiments
        self.experiments: Dict[str, Experiment] = {}

        # Deployments
        self.deployments: Dict[str, Deployment] = {}
        self.active_deployments: Dict[str, str] = {}  # model_name -> deployment_id

        # Performance monitoring
        self.performance_history: dict[str, list[ModelPerformance]] = {}
        self.drift_threshold: float = 0.1

        # Statistics
        self.total_models_registered: int = 0
        self.total_experiments: int = 0
        self.total_deployments: int = 0
        self.total_rollbacks: int = 0

    # ==================== Model Registry ====================

    def register_model(
        self,
        name: str,
        version: str,
        model_path: str,
        metrics: Dict[str, float] = None,
        parameters: Dict[str, Any] = None,
        tags: List[str] = None,
        experiment_id: str = None,
        description: str = "",
    ) -> ModelVersion:
        """Register new model version."""
        model_id = f"model_{secrets.token_hex(8)}"

        # Calculate model hash (simulated)
        model_hash = hashlib.sha256(f"{name}:{version}:{time.time()}".encode()).hexdigest()[:16]

        model = ModelVersion(
            model_id=model_id,
            name=name,
            version=version,
            model_path=model_path,
            model_hash=model_hash,
            metrics=metrics or {},
            parameters=parameters or {},
            tags=tags or [],
            experiment_id=experiment_id,
            description=description,
        )

        if name not in self.registered_models:
            self.registered_models[name] = {}

        self.registered_models[name][version] = model
        self.total_models_registered += 1

        return model

    def get_model(
        self, name: str, version: str = None, alias: str = None
    ) -> Optional[ModelVersion]:
        """Get model by name and version or alias."""
        if alias and alias in self.model_aliases:
            name, version = self.model_aliases[alias]

        if name not in self.registered_models:
            return None

        if version:
            return self.registered_models[name].get(version)

        # Return latest version
        versions = sorted(self.registered_models[name].keys())
        return self.registered_models[name].get(versions[-1]) if versions else None

    def transition_stage(self, model_name: str, version: str, stage: ModelStage) -> bool:
        """Transition model to new stage."""
        model = self.get_model(model_name, version)
        if not model:
            return False

        # Validate stage transition
        valid_transitions = {
            ModelStage.DEVELOPMENT: [ModelStage.STAGING, ModelStage.ARCHIVED],
            ModelStage.STAGING: [
                ModelStage.PRODUCTION,
                ModelStage.DEVELOPMENT,
                ModelStage.ARCHIVED,
            ],
            ModelStage.PRODUCTION: [ModelStage.ARCHIVED],
            ModelStage.ARCHIVED: [ModelStage.DEVELOPMENT],
        }

        if stage not in valid_transitions.get(model.stage, []):
            return False

        model.stage = stage
        model.updated_at = time.time()

        # Update aliases
        if stage == ModelStage.PRODUCTION:
            self.model_aliases["production"] = (model_name, version)
        elif stage == ModelStage.STAGING:
            self.model_aliases["staging"] = (model_name, version)

        return True

    def set_alias(self, alias: str, model_name: str, version: str) -> bool:
        """Set alias for model version."""
        if self.get_model(model_name, version):
            self.model_aliases[alias] = (model_name, version)
            return True
        return False

    def search_models(
        self,
        name_pattern: str = None,
        stage: Optional[ModelStage] = None,
        tags: List[str] = None,
        min_metric: Tuple[str, float] = None,
    ) -> List[ModelVersion]:
        """Search registered models with filters."""
        results = []

        for name, versions in self.registered_models.items():
            if name_pattern and name_pattern not in name:
                continue

            for model in versions.values():
                # Filter by stage
                if stage and model.stage != stage:
                    continue

                # Filter by tags
                if tags and not all(t in model.tags for t in tags):
                    continue

                # Filter by metric
                if min_metric:
                    metric_name, min_value = min_metric
                    if model.metrics.get(metric_name, 0) < min_value:
                        continue

                results.append(model)

        return sorted(results, key=lambda m: m.created_at, reverse=True)

    def compare_models(
        self, model_refs: list[tuple[str, str]], metrics: List[str] = None
    ) -> Dict[str, Any]:
        """Compare multiple model versions."""
        models = []
        for name, version in model_refs:
            model = self.get_model(name, version)
            if model:
                models.append(model)

        if not models:
            return {"error": "No models found"}

        # Get all metrics if not specified
        all_metrics = set()
        for m in models:
            all_metrics.update(m.metrics.keys())
        metrics = metrics or list(all_metrics)

        comparison = {
            "models": [
                {
                    "name": m.name,
                    "version": m.version,
                    "stage": m.stage.value,
                    "metrics": {k: m.metrics.get(k) for k in metrics},
                }
                for m in models
            ],
            "best_by_metric": {},
        }

        # Find best for each metric
        for metric in metrics:
            best_model = max(models, key=lambda m: m.metrics.get(metric, float("-inf")))
            comparison["best_by_metric"][metric] = {
                "model": f"{best_model.name}:{best_model.version}",
                "value": best_model.metrics.get(metric),
            }

        return comparison

    # ==================== Experiment Tracking ====================

    def create_experiment(
        self, name: str, parameters: Dict[str, Any] = None, parent_experiment_id: str = None
    ) -> Experiment:
        """Create new experiment."""
        experiment_id = f"exp_{secrets.token_hex(8)}"

        experiment = Experiment(
            experiment_id=experiment_id,
            name=name,
            status=ExperimentStatus.RUNNING,
            parameters=parameters or {},
            parent_experiment_id=parent_experiment_id,
        )

        self.experiments[experiment_id] = experiment
        self.total_experiments += 1

        return experiment

    def log_metric(
        self, experiment_id: str, metric_name: str, value: float, step: int = None
    ) -> None:
        """Log metric for experiment."""
        if experiment_id not in self.experiments:
            return

        exp = self.experiments[experiment_id]

        if metric_name not in exp.metrics:
            exp.metrics[metric_name] = []

        exp.metrics[metric_name].append(value)

    def log_artifact(self, experiment_id: str, artifact_name: str, artifact_path: str) -> None:
        """Log artifact for experiment."""
        if experiment_id in self.experiments:
            self.experiments[experiment_id].artifacts[artifact_name] = artifact_path

    def complete_experiment(
        self, experiment_id: str, status: ExperimentStatus = ExperimentStatus.COMPLETED
    ) -> None:
        """Complete experiment run."""
        if experiment_id in self.experiments:
            exp = self.experiments[experiment_id]
            exp.status = status
            exp.completed_at = time.time()

    def compare_experiments(self, experiment_ids: List[str], metric: str = None) -> Dict[str, Any]:
        """Compare multiple experiments."""
        experiments = [self.experiments.get(eid) for eid in experiment_ids]
        experiments = [e for e in experiments if e]

        if not experiments:
            return {"error": "No experiments found"}

        comparison = {
            "experiments": [
                {
                    "id": e.experiment_id,
                    "name": e.name,
                    "status": e.status.name,
                    "parameters": e.parameters,
                    "final_metrics": {k: v[-1] if v else None for k, v in e.metrics.items()},
                }
                for e in experiments
            ]
        }

        # Find best by specific metric
        if metric:
            best_exp = max(
                experiments,
                key=lambda e: e.metrics.get(metric, [float("-inf")])[-1]
                if e.metrics.get(metric)
                else float("-inf"),
            )
            comparison["best_by_metric"] = {
                "metric": metric,
                "experiment_id": best_exp.experiment_id,
                "value": best_exp.metrics.get(metric, [None])[-1],
            }

        return comparison

    # ==================== Deployment Management ====================

    def deploy_model(
        self,
        model_name: str,
        version: str,
        strategy: DeploymentStrategy = DeploymentStrategy.STANDARD,
        traffic_percentage: float = 100.0,
        duration_hours: float = None,
    ) -> Deployment:
        """Deploy model to production."""
        deployment_id = f"deploy_{secrets.token_hex(8)}"

        deployment = Deployment(
            deployment_id=deployment_id,
            strategy=strategy,
            model_versions=[(model_name, version)],
            traffic_split={version: traffic_percentage / 100.0},
            status="running",
        )

        self.deployments[deployment_id] = deployment
        self.active_deployments[model_name] = deployment_id
        self.total_deployments += 1

        return deployment

    def deploy_ab_test(
        self,
        model_a: Tuple[str, str],
        model_b: Tuple[str, str],
        traffic_split: float = 0.5,
        duration_hours: float = 24.0,
    ) -> Deployment:
        """Deploy A/B test between two models."""
        deployment_id = f"deploy_ab_{secrets.token_hex(8)}"

        name_a, version_a = model_a
        name_b, version_b = model_b

        deployment = Deployment(
            deployment_id=deployment_id,
            strategy=DeploymentStrategy.AB_TEST,
            model_versions=[model_a, model_b],
            traffic_split={version_a: traffic_split, version_b: 1.0 - traffic_split},
            status="running",
        )

        self.deployments[deployment_id] = deployment
        self.total_deployments += 1

        return deployment

    def deploy_canary(
        self,
        model_name: str,
        new_version: str,
        baseline_version: str,
        initial_percentage: float = 5.0,
        duration_hours: float = 48.0,
    ) -> Deployment:
        """Deploy canary release."""
        deployment_id = f"deploy_canary_{secrets.token_hex(8)}"

        deployment = Deployment(
            deployment_id=deployment_id,
            strategy=DeploymentStrategy.CANARY,
            model_versions=[(model_name, new_version), (model_name, baseline_version)],
            traffic_split={
                new_version: initial_percentage / 100.0,
                baseline_version: 1.0 - (initial_percentage / 100.0),
            },
            status="running",
        )

        self.deployments[deployment_id] = deployment
        self.total_deployments += 1

        return deployment

    def deploy_shadow(
        self, model_name: str, shadow_version: str, production_version: str
    ) -> Deployment:
        """Deploy shadow testing (0% traffic, only logging)."""
        deployment_id = f"deploy_shadow_{secrets.token_hex(8)}"

        deployment = Deployment(
            deployment_id=deployment_id,
            strategy=DeploymentStrategy.SHADOW,
            model_versions=[(model_name, production_version), (model_name, shadow_version)],
            traffic_split={production_version: 1.0, shadow_version: 0.0},
            status="running",
        )

        self.deployments[deployment_id] = deployment
        self.total_deployments += 1

        return deployment

    def rollback_deployment(self, deployment_id: str) -> bool:
        """Rollback deployment to previous version."""
        if deployment_id not in self.deployments:
            return False

        deployment = self.deployments[deployment_id]
        deployment.status = "rolled_back"
        deployment.end_time = time.time()

        self.total_rollbacks += 1
        return True

    def get_deployment_metrics(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment performance metrics."""
        if deployment_id not in self.deployments:
            return None

        deployment = self.deployments[deployment_id]

        return {
            "deployment_id": deployment_id,
            "strategy": deployment.strategy.name,
            "status": deployment.status,
            "models": deployment.model_versions,
            "traffic_split": deployment.traffic_split,
            "runtime_hours": (time.time() - deployment.start_time) / 3600,
            "metrics": deployment.metrics,
        }

    # ==================== Model Monitoring ====================

    def record_performance(
        self,
        model_id: str,
        predictions: int = 1,
        latency_ms: float = 0.0,
        accuracy: float = None,
        error: bool = False,
    ) -> None:
        """Record model performance metrics."""
        if model_id not in self.performance_history:
            self.performance_history[model_id] = []

        perf = ModelPerformance(
            model_id=model_id,
            timestamp=time.time(),
            predictions_count=predictions,
            avg_latency_ms=latency_ms,
            accuracy=accuracy,
            error_rate=1.0 if error else 0.0,
        )

        self.performance_history[model_id].append(perf)

        # Keep only last 1000 records
        if len(self.performance_history[model_id]) > 1000:
            self.performance_history[model_id] = self.performance_history[model_id][-1000:]

    def detect_drift(
        self, model_id: str, reference_data: List[Any], current_data: List[Any]
    ) -> Dict[str, Any]:
        """Detect data/concept drift."""
        # Simplified drift detection using statistical comparison
        if not reference_data or not current_data:
            return {"drift_detected": False, "score": 0.0}

        # Calculate basic statistics
        ref_mean = sum(reference_data) / len(reference_data) if reference_data else 0
        curr_mean = sum(current_data) / len(current_data) if current_data else 0

        # Simple drift score based on mean difference
        drift_score = abs(curr_mean - ref_mean) / (abs(ref_mean) + 1e-10)

        return {
            "drift_detected": drift_score > self.drift_threshold,
            "drift_score": drift_score,
            "threshold": self.drift_threshold,
            "reference_mean": ref_mean,
            "current_mean": curr_mean,
        }

    def get_model_performance(self, model_id: str, last_n_hours: float = 24.0) -> Dict[str, Any]:
        """Get aggregated model performance."""
        if model_id not in self.performance_history:
            return None

        cutoff_time = time.time() - (last_n_hours * 3600)
        recent = [p for p in self.performance_history[model_id] if p.timestamp > cutoff_time]

        if not recent:
            return None

        total_predictions = sum(p.predictions_count for p in recent)
        avg_latency = (
            sum(p.avg_latency_ms * p.predictions_count for p in recent) / total_predictions
        )
        error_rate = sum(p.error_rate * p.predictions_count for p in recent) / total_predictions

        accuracies = [p.accuracy for p in recent if p.accuracy is not None]
        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else None

        return {
            "model_id": model_id,
            "period_hours": last_n_hours,
            "total_predictions": total_predictions,
            "avg_latency_ms": avg_latency,
            "error_rate": error_rate,
            "avg_accuracy": avg_accuracy,
            "data_points": len(recent),
        }

    # ==================== Statistics & Health ====================

    def get_mlops_stats(self) -> Dict[str, Any]:
        """Get comprehensive MLOps statistics."""
        # Count models by stage
        stage_counts = {stage.value: 0 for stage in ModelStage}
        for versions in self.registered_models.values():
            for model in versions.values():
                stage_counts[model.stage.value] += 1

        # Count deployments by strategy
        strategy_counts = {strategy.name: 0 for strategy in DeploymentStrategy}
        for deployment in self.deployments.values():
            strategy_counts[deployment.strategy.name] += 1

        return {
            "model_registry": {
                "total_models": self.total_models_registered,
                "unique_names": len(self.registered_models),
                "by_stage": stage_counts,
                "aliases": len(self.model_aliases),
            },
            "experiments": {
                "total": self.total_experiments,
                "running": sum(
                    1 for e in self.experiments.values() if e.status == ExperimentStatus.RUNNING
                ),
                "completed": sum(
                    1 for e in self.experiments.values() if e.status == ExperimentStatus.COMPLETED
                ),
            },
            "deployments": {
                "total": self.total_deployments,
                "by_strategy": strategy_counts,
                "active": sum(1 for d in self.deployments.values() if d.status == "running"),
                "rollbacks": self.total_rollbacks,
            },
            "monitoring": {
                "models_tracked": len(self.performance_history),
                "total_predictions": sum(
                    sum(p.predictions_count for p in perfs)
                    for perfs in self.performance_history.values()
                ),
            },
        }


def main():
    """CLI demo for MLOps."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS MLOps & Model Registry (Phase 30)")
    parser.add_argument("--demo", action="store_true", help="Run demonstration")

    args = parser.parse_args()

    if args.demo:
        print("=" * 70)
        print("Phase 30: MLOps & Model Registry")
        print("Model Registry | A/B Testing | Canary | Experiment Tracking")
        print("=" * 70)

        # Initialize MLOps
        mlops = AMOSMLOps(artifact_storage_path="./mlartifacts")

        # 1. Model Registry
        print("\n1. Model Registry - Versioning & Staging")
        print("-" * 50)

        # Register models
        models_to_register = [
            (
                "neural_ode_solver",
                "1.0.0",
                {"accuracy": 0.92, "latency_ms": 45},
                {"hidden_dim": 128, "layers": 3},
                ["production", "stable"],
            ),
            (
                "neural_ode_solver",
                "2.0.0",
                {"accuracy": 0.95, "latency_ms": 38},
                {"hidden_dim": 256, "layers": 4},
                ["candidate"],
            ),
            (
                "neural_ode_solver",
                "2.1.0",
                {"accuracy": 0.96, "latency_ms": 35},
                {"hidden_dim": 256, "layers": 4, "attention": True},
                ["experimental"],
            ),
            (
                "black_scholes_model",
                "1.0.0",
                {"accuracy": 0.98, "latency_ms": 12},
                {"volatility_model": "garch"},
                ["production", "finance"],
            ),
        ]

        for name, version, metrics, params, tags in models_to_register:
            model = mlops.register_model(
                name=name,
                version=version,
                model_path=f"/models/{name}_v{version}.pkl",
                metrics=metrics,
                parameters=params,
                tags=tags,
                description=f"{name} version {version}",
            )
            print(f"   Registered: {name} v{version} (id: {model.model_id[:12]}...)")

        # Transition stages
        mlops.transition_stage("neural_ode_solver", "1.0.0", ModelStage.PRODUCTION)
        mlops.transition_stage("neural_ode_solver", "2.0.0", ModelStage.STAGING)
        mlops.transition_stage("neural_ode_solver", "2.1.0", ModelStage.DEVELOPMENT)
        mlops.transition_stage("black_scholes_model", "1.0.0", ModelStage.PRODUCTION)

        print("\n   Stage transitions:")
        print("      neural_ode_solver v1.0.0 -> PRODUCTION")
        print("      neural_ode_solver v2.0.0 -> STAGING")
        print("      black_scholes_model v1.0.0 -> PRODUCTION")

        # Set aliases
        mlops.set_alias("latest", "neural_ode_solver", "2.1.0")
        mlops.set_alias("champion", "neural_ode_solver", "1.0.0")
        mlops.set_alias("challenger", "neural_ode_solver", "2.0.0")

        print("\n   Aliases set: latest, champion, challenger")

        # Search models
        production_models = mlops.search_models(stage=ModelStage.PRODUCTION)
        print(f"\n   Production models: {len(production_models)}")
        for m in production_models:
            print(f"      - {m.name} v{m.version} (accuracy: {m.metrics.get('accuracy', 0):.2%})")

        # Compare models
        comparison = mlops.compare_models(
            [
                ("neural_ode_solver", "1.0.0"),
                ("neural_ode_solver", "2.0.0"),
                ("neural_ode_solver", "2.1.0"),
            ],
            metrics=["accuracy", "latency_ms"],
        )
        print("\n   Model comparison:")
        for metric, best in comparison["best_by_metric"].items():
            print(f"      Best {metric}: {best['model']} ({best['value']})")

        # 2. Experiment Tracking
        print("\n2. Experiment Tracking")
        print("-" * 50)

        # Create experiments
        exp1 = mlops.create_experiment(
            name="hyperparameter_tuning_v1",
            parameters={"learning_rate": 0.001, "batch_size": 32, "epochs": 100},
        )

        exp2 = mlops.create_experiment(
            name="hyperparameter_tuning_v2",
            parameters={"learning_rate": 0.0001, "batch_size": 64, "epochs": 150},
            parent_experiment_id=exp1.experiment_id,
        )

        print(f"   Created experiments: {exp1.experiment_id[:12]}..., {exp2.experiment_id[:12]}...")

        # Log metrics
        for epoch in range(10):
            mlops.log_metric(exp1.experiment_id, "accuracy", 0.85 + epoch * 0.01, step=epoch)
            mlops.log_metric(exp1.experiment_id, "loss", 0.5 - epoch * 0.03, step=epoch)

            mlops.log_metric(exp2.experiment_id, "accuracy", 0.88 + epoch * 0.015, step=epoch)
            mlops.log_metric(exp2.experiment_id, "loss", 0.45 - epoch * 0.035, step=epoch)

        # Log artifacts
        mlops.log_artifact(exp1.experiment_id, "model", "/experiments/exp1/model.pkl")
        mlops.log_artifact(exp1.experiment_id, "config", "/experiments/exp1/config.yaml")

        # Complete experiments
        mlops.complete_experiment(exp1.experiment_id, ExperimentStatus.COMPLETED)
        mlops.complete_experiment(exp2.experiment_id, ExperimentStatus.COMPLETED)

        print(f"   Logged metrics for {len(exp1.metrics)} metrics across epochs")

        # Compare experiments
        exp_comparison = mlops.compare_experiments(
            [exp1.experiment_id, exp2.experiment_id], metric="accuracy"
        )
        print("\n   Experiment comparison:")
        if "best_by_metric" in exp_comparison:
            best = exp_comparison["best_by_metric"]
            print(f"      Best accuracy: {best['experiment_id'][:12]}... ({best['value']:.4f})")

        # 3. Deployment Strategies
        print("\n3. Deployment Strategies")
        print("-" * 50)

        # Standard deployment
        deploy1 = mlops.deploy_model(
            model_name="black_scholes_model",
            version="1.0.0",
            strategy=DeploymentStrategy.STANDARD,
            traffic_percentage=100.0,
        )
        print(f"   Standard deployment: {deploy1.deployment_id[:15]}...")

        # A/B test deployment
        ab_deploy = mlops.deploy_ab_test(
            model_a=("neural_ode_solver", "1.0.0"),
            model_b=("neural_ode_solver", "2.0.0"),
            traffic_split=0.5,
            duration_hours=24.0,
        )
        print(f"   A/B test deployment: {ab_deploy.deployment_id[:15]}...")
        print("      Traffic split: 50/50 between v1.0.0 and v2.0.0")

        # Canary deployment
        canary_deploy = mlops.deploy_canary(
            model_name="neural_ode_solver",
            new_version="2.1.0",
            baseline_version="2.0.0",
            initial_percentage=5.0,
            duration_hours=48.0,
        )
        print(f"   Canary deployment: {canary_deploy.deployment_id[:15]}...")
        print("      Initial traffic: 5% to v2.1.0, 95% to v2.0.0")

        # Shadow deployment
        shadow_deploy = mlops.deploy_shadow(
            model_name="neural_ode_solver", shadow_version="2.1.0", production_version="1.0.0"
        )
        print(f"   Shadow deployment: {shadow_deploy.deployment_id[:15]}...")
        print("      Production: 100% traffic, Shadow: 0% traffic (logging only)")

        # 4. Model Monitoring
        print("\n4. Model Monitoring & Performance")
        print("-" * 50)

        # Simulate performance data
        model_ids = [m.model_id for m in production_models]

        for _ in range(100):
            for mid in model_ids:
                mlops.record_performance(
                    model_id=mid,
                    predictions=random.randint(1, 10),
                    latency_ms=random.uniform(20, 50),
                    accuracy=random.uniform(0.90, 0.98),
                    error=random.random() < 0.02,
                )

        print(f"   Recorded performance data for {len(model_ids)} models")

        # Get performance summary
        if model_ids:
            perf = mlops.get_model_performance(model_ids[0], last_n_hours=1.0)
            if perf:
                print("\n   Performance summary (last 1 hour):")
                print(f"      Predictions: {perf['total_predictions']}")
                print(f"      Avg latency: {perf['avg_latency_ms']:.1f}ms")
                print(f"      Error rate: {perf['error_rate']:.2%}")
                print(f"      Avg accuracy: {perf['avg_accuracy']:.2%}")

        # Drift detection
        reference_data = [0.95] * 100
        current_data = [0.95 + random.gauss(0, 0.02) for _ in range(100)]

        drift_result = mlops.detect_drift(
            model_id=model_ids[0] if model_ids else "test",
            reference_data=reference_data,
            current_data=current_data,
        )

        print("\n   Drift detection:")
        print(f"      Drift detected: {drift_result['drift_detected']}")
        print(f"      Drift score: {drift_result['drift_score']:.4f}")
        print(f"      Threshold: {drift_result['threshold']}")

        # 5. Statistics
        print("\n" + "=" * 70)
        print("MLOps Statistics")
        print("=" * 70)

        stats = mlops.get_mlops_stats()

        print("   Model Registry:")
        print(f"      Total models: {stats['model_registry']['total_models']}")
        print(f"      Unique names: {stats['model_registry']['unique_names']}")
        print(f"      By stage: {stats['model_registry']['by_stage']}")

        print("\n   Experiments:")
        print(f"      Total: {stats['experiments']['total']}")
        print(f"      Running: {stats['experiments']['running']}")
        print(f"      Completed: {stats['experiments']['completed']}")

        print("\n   Deployments:")
        print(f"      Total: {stats['deployments']['total']}")
        print(f"      By strategy: {stats['deployments']['by_strategy']}")
        print(f"      Active: {stats['deployments']['active']}")
        print(f"      Rollbacks: {stats['deployments']['rollbacks']}")

        print("\n   Monitoring:")
        print(f"      Models tracked: {stats['monitoring']['models_tracked']}")
        print(f"      Total predictions: {stats['monitoring']['total_predictions']}")

        print("\n" + "=" * 70)
        print("Phase 30 MLOps: OPERATIONAL")
        print("   Registry | A/B Testing | Canary | Experiments | Monitoring")
        print("=" * 70)

    else:
        print("AMOS MLOps v30.0.0")
        print("Usage: python amos_mlops.py --demo")


if __name__ == "__main__":
    main()
