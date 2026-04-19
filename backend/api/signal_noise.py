from typing import Any

"""
AMOS Signal-Noise Kernel API

Direct access to signal-noise separation for input analysis.
Part of the Translation Layer - exposes signal quality metrics.

Creator: Trang Phan
Version: 1.0.0
"""


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from amos_translation_layer import get_translation_layer

router = APIRouter(prefix="/signal-noise", tags=["signal-noise"])


class SignalNoiseRequest(BaseModel):
    """Request for signal-noise analysis."""

    text: str = Field(..., description="Input text to analyze")
    context: dict[str, Any] = Field(default_factory=dict)


class SignalUnitOutput(BaseModel):
    """Extracted signal unit."""

    signal_class: str
    content: str
    confidence: float


class NoiseUnitOutput(BaseModel):
    """Classified noise unit."""

    noise_class: str
    content: str
    distortion_score: float


class AmbiguityOutput(BaseModel):
    """Detected ambiguity."""

    ambiguity_type: str
    references: list[str]
    severity: float


class SignalNoiseResponse(BaseModel):
    """Complete signal-noise analysis."""

    input: str
    signal_quality: float
    noise_distortion: float
    ambiguity_count: int
    execution_safe: bool
    signals: list[SignalUnitOutput]
    noise_units: list[NoiseUnitOutput]
    ambiguities: list[AmbiguityOutput]


@router.post("/analyze", response_model=SignalNoiseResponse)
async def analyze_signal_noise(request: SignalNoiseRequest) -> SignalNoiseResponse:
    """
    Analyze input text using Signal-Noise Kernel.

    Separates signal from noise and ambiguity for machine interpretation.
    """
    try:
        translator = get_translation_layer()

        # Run translation to get signal-noise analysis
        result = await translator.translate(
            raw_text=request.text, dialogue_context=request.context, memory_context={}
        )

        # Extract signal units if available
        signals = []
        if hasattr(result, "signal_units"):
            for su in result.signal_units:
                signals.append(
                    SignalUnitOutput(
                        signal_class=su.signal_class.value,
                        content=su.content,
                        confidence=su.confidence,
                    )
                )

        # Extract noise units if available
        noise_units = []
        if hasattr(result, "noise_units"):
            for nu in result.noise_units:
                noise_units.append(
                    NoiseUnitOutput(
                        noise_class=nu.noise_class.value,
                        content=nu.content,
                        distortion_score=nu.distortion_score,
                    )
                )

        # Extract ambiguities
        ambiguities = []
        for amb in result.ambiguities:
            ambiguities.append(
                AmbiguityOutput(
                    ambiguity_type=amb.type.value, references=amb.references, severity=amb.severity
                )
            )

        return SignalNoiseResponse(
            input=request.text,
            signal_quality=getattr(result, "signal_quality", 0.85),
            noise_distortion=getattr(result, "noise_distortion", 0.15),
            ambiguity_count=len(result.ambiguities),
            execution_safe=result.compiled_machine_goal.execution_allowed,
            signals=signals,
            noise_units=noise_units,
            ambiguities=ambiguities,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def signal_noise_status() -> dict[str, Any]:
    """Get Signal-Noise Kernel status."""
    try:
        translator = get_translation_layer()
        state = translator.get_state()
        return {"operational": True, "state": state.name, "kernel_version": "1.0.0"}
    except Exception as e:
        return {"operational": False, "error": str(e)}
