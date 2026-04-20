"""AMOS ML Inference API - Model Serving & Feature Store

Production-grade ML model serving endpoints.

Owner: Trang Phan
Version: 2.0.0
"""

from __future__ import annotations

import time
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.ml_inference.model_serving import (
    InferenceMode,
    InferenceService,
    ModelFramework,
    ModelStatus,
    ModelVersion,
    inference_service,
)

router = APIRouter(prefix="/ml", tags=["ml-inference"])


class RegisterModelRequest(BaseModel):
    """Register new model request."""

    model_id: str = Field(..., description="Unique model identifier")
    version: str = Field(..., description="Model version (semver)")
    framework: str = Field(..., description="pytorch, tensorflow, sklearn, onnx, custom")
    artifact_path: str = Field(..., description="Path to model artifacts")
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    features_required: list[str] = Field(default_factory=list)


class InferenceRequest(BaseModel):
    """Model inference request."""

    model_id: str = Field(..., description="Model identifier")
    version: Optional[str] = Field(None, description="Specific version (default: latest)")
    inputs: dict[str, Any] = Field(..., description="Model inputs")
    mode: str = Field(default="realtime", description="realtime, batch, or shadow")


class FeatureLookupRequest(BaseModel):
    """Feature store lookup request."""

    entity_id: str = Field(..., description="Entity identifier")
    feature_names: list[str] = Field(..., description="Features to retrieve")


class ModelResponse(BaseModel):
    """Model metadata response."""

    model_id: str
    version: str
    framework: str
    status: str
    created_at: str
    artifact_path: Optional[str]


class InferenceResponse(BaseModel):
    """Inference result response."""

    model_id: str
    version: str
    predictions: dict[str, Any]
    latency_ms: float
    timestamp: float


class FeatureResponse(BaseModel):
    """Feature values response."""

    entity_id: str
    features: dict[str, Any]
    timestamp: float


def get_inference_service() -> InferenceService:
    """Dependency injection for inference service."""
    return inference_service


@router.post("/models", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def register_model(
    request: RegisterModelRequest, service: InferenceService = Depends(get_inference_service)
) -> ModelResponse:
    """Register a new ML model version."""
    # Convert string enums
    framework = ModelFramework(request.framework.lower())

    model_version = ModelVersion(
        model_id=request.model_id,
        version=request.version,
        framework=framework,
        status=ModelStatus.STAGING,
        artifact_path=request.artifact_path,
        input_schema=request.input_schema,
        output_schema=request.output_schema,
        features_required=request.features_required,
    )

    success = service.register_model(model_version)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to register model (may already exist)",
        )

    return ModelResponse(
        model_id=model_version.model_id,
        version=model_version.version,
        framework=model_version.framework.value,
        status=model_version.status.value,
        created_at=model_version.created_at,
        artifact_path=model_version.artifact_path,
    )


@router.post("/infer", response_model=InferenceResponse)
async def run_inference(
    request: InferenceRequest, service: InferenceService = Depends(get_inference_service)
) -> InferenceResponse:
    """Run model inference.

    Supports real-time, batch, and shadow (test) modes.
    """
    mode = InferenceMode(request.mode)

    start_time = time.time()

    result = await service.predict(
        model_id=request.model_id, version=request.version, inputs=request.inputs, mode=mode
    )

    latency = (time.time() - start_time) * 1000

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["error"]
        )

    return InferenceResponse(
        model_id=request.model_id,
        version=result.get("version", request.version or "latest"),
        predictions=result.get("predictions", {}),
        latency_ms=round(latency, 2),
        timestamp=time.time(),
    )


@router.post("/batch_infer")
async def run_batch_inference(
    requests: list[InferenceRequest], service: InferenceService = Depends(get_inference_service)
) -> list[InferenceResponse]:
    """Run batch inference on multiple inputs."""
    results = []

    for req in requests:
        start_time = time.time()

        result = await service.predict(
            model_id=req.model_id, version=req.version, inputs=req.inputs, mode=InferenceMode.BATCH
        )

        latency = (time.time() - start_time) * 1000

        results.append(
            InferenceResponse(
                model_id=req.model_id,
                version=result.get("version", req.version or "latest"),
                predictions=result.get("predictions", {}),
                latency_ms=round(latency, 2),
                timestamp=time.time(),
            )
        )

    return results


@router.get("/models/{model_id}", response_model=list[ModelResponse])
async def list_model_versions(
    model_id: str, service: InferenceService = Depends(get_inference_service)
) -> list[ModelResponse]:
    """List all versions of a model."""
    versions = service.list_model_versions(model_id)

    return [
        ModelResponse(
            model_id=v.model_id,
            version=v.version,
            framework=v.framework.value,
            status=v.status.value,
            created_at=v.created_at,
            artifact_path=v.artifact_path,
        )
        for v in versions
    ]


@router.post("/models/{model_id}/versions/{version}/promote")
async def promote_model(
    model_id: str,
    version: str,
    target_status: str,
    service: InferenceService = Depends(get_inference_service),
) -> dict[str, Any]:
    """Promote model version to production or archive."""
    status_enum = ModelStatus(target_status.lower())

    success = service.update_model_status(model_id, version, status_enum)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model {model_id} version {version} not found",
        )

    return {"model_id": model_id, "version": version, "new_status": target_status, "promoted": True}


@router.post("/features/lookup", response_model=FeatureResponse)
async def lookup_features(
    request: FeatureLookupRequest, service: InferenceService = Depends(get_inference_service)
) -> FeatureResponse:
    """Look up entity features from feature store."""
    features = service.feature_store.get_features(
        entity_id=request.entity_id, feature_names=request.feature_names
    )

    return FeatureResponse(entity_id=request.entity_id, features=features, timestamp=time.time())


@router.post("/features/store")
async def store_features(
    entity_id: str,
    features: dict[str, Any],
    ttl_seconds: int = 86400,
    service: InferenceService = Depends(get_inference_service),
) -> dict[str, Any]:
    """Store entity features in feature store."""
    success = service.feature_store.store_features(
        entity_id=entity_id, features=features, ttl_seconds=ttl_seconds
    )

    return {"entity_id": entity_id, "features_stored": len(features), "success": success}


@router.get("/models/{model_id}/metrics")
async def get_model_metrics(
    model_id: str,
    version: Optional[str] = None,
    service: InferenceService = Depends(get_inference_service),
) -> dict[str, Any]:
    """Get model inference metrics."""
    metrics = service.get_model_metrics(model_id, version)

    return {"model_id": model_id, "version": version or "all", "metrics": metrics}


@router.get("/models")
async def list_models(
    framework: Optional[str] = None,
    status: Optional[str] = None,
    service: InferenceService = Depends(get_inference_service),
) -> list[ModelResponse]:
    """List all registered models with optional filters."""
    models = service.list_models()

    if framework:
        models = [m for m in models if m.framework.value == framework]

    if status:
        models = [m for m in models if m.status.value == status]

    return [
        ModelResponse(
            model_id=m.model_id,
            version=m.version,
            framework=m.framework.value,
            status=m.status.value,
            created_at=m.created_at,
            artifact_path=m.artifact_path,
        )
        for m in models
    ]
