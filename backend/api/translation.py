"""
AMOS Translation Layer API Endpoints

Human-to-Machine Semantic Alignment via REST API
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from amos_translation_layer import (
    AMOSTranslationLayer,
    get_translation_layer,
)

router = APIRouter(prefix="/translation", tags=["translation"])

# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class TranslateRequest(BaseModel):
    """Request to translate human utterance to machine meaning."""

    raw_text: str = Field(..., description="Raw human utterance")
    language: str = Field(default="en", description="Language code")
    dialogue_context: dict[str, Any] = Field(
        default_factory=dict, description="Previous dialogue context"
    )
    memory_context: dict[str, Any] = Field(
        default_factory=dict, description="User memory/knowledge context"
    )


class SpeechActOutput(BaseModel):
    """Speech act classification output."""

    type: str
    weight: float


class SemanticUnitOutput(BaseModel):
    """Semantic unit output."""

    unit_id: str
    surface_text: str
    proposition_type: str
    polarity: str


class HumanStateOutput(BaseModel):
    """Human state estimate output."""

    cognitive_load: float
    emotional_intensity: float
    state_class: str


class AmbiguityOutput(BaseModel):
    """Detected ambiguity output."""

    type: str
    severity: float


class CompiledGoalOutput(BaseModel):
    """Compiled machine goal output."""

    goal_type: str
    objective: str
    execution_allowed: bool


class TranslateResponse(BaseModel):
    """Response containing full semantic translation."""

    utterance_id: str
    raw_text: str
    speech_acts: list[SpeechActOutput]
    semantic_units: list[SemanticUnitOutput]
    human_state: HumanStateOutput
    ambiguities: list[AmbiguityOutput]
    semantic_confidence: float
    requires_clarification: bool
    clarification_targets: list[str]
    compiled_goal: CompiledGoalOutput
    execution_allowed: bool


class TranslationStatusResponse(BaseModel):
    """Current translation layer status."""

    state: str
    has_active_translation: bool


# =============================================================================
# DEPENDENCY
# =============================================================================


async def get_translator() -> AMOSTranslationLayer:
    """Get translation layer instance."""
    return get_translation_layer()


# =============================================================================
# API ENDPOINTS
# =============================================================================


@router.post("/translate", response_model=TranslateResponse)
async def translate_utterance(
    request: TranslateRequest, translator: AMOSTranslationLayer = Depends(get_translator)
) -> TranslateResponse:
    """
    Translate human utterance to machine-readable semantic representation.

    Implements the full pipeline:
    Parse → Sense → Resolve → Ground → Structure → Verify → Compile

    Returns semantic intent representation with execution gating decision.
    """
    try:
        result = await translator.translate(
            raw_text=request.raw_text,
            language=request.language,
            dialogue_context=request.dialogue_context,
            memory_context=request.memory_context,
        )

        return TranslateResponse(
            utterance_id=result.utterance_id,
            raw_text=result.raw_text,
            speech_acts=[
                SpeechActOutput(type=sa.type.value, weight=sa.weight) for sa in result.speech_acts
            ],
            semantic_units=[
                SemanticUnitOutput(
                    unit_id=su.unit_id,
                    surface_text=su.surface_text,
                    proposition_type=su.proposition_type.value,
                    polarity=su.polarity.value,
                )
                for su in result.semantic_units
            ],
            human_state=HumanStateOutput(
                cognitive_load=result.human_state_estimate.cognitive_load,
                emotional_intensity=result.human_state_estimate.emotional_intensity,
                state_class=result.human_state_estimate.state_class.value,
            ),
            ambiguities=[
                AmbiguityOutput(type=a.type.value, severity=a.severity) for a in result.ambiguities
            ],
            semantic_confidence=result.semantic_confidence,
            requires_clarification=result.requires_clarification,
            clarification_targets=result.clarification_targets,
            compiled_goal=CompiledGoalOutput(
                goal_type=result.compiled_machine_goal.goal_type.value,
                objective=result.compiled_machine_goal.objective,
                execution_allowed=result.compiled_machine_goal.execution_allowed,
            ),
            execution_allowed=result.compiled_machine_goal.execution_allowed,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@router.get("/status", response_model=TranslationStatusResponse)
async def get_translation_status(
    translator: AMOSTranslationLayer = Depends(get_translator),
) -> TranslationStatusResponse:
    """Get current translation layer status."""
    return TranslationStatusResponse(
        state=translator.get_state().name,
        has_active_translation=translator.get_representation() is not None,
    )


@router.get("/bug-classes")
async def get_translation_bug_classes() -> dict[str, Any]:
    """
    Get documented translation bug classes.

    These represent the failure modes that the translation layer prevents:
    - Surface literalism
    - Reference failure
    - Speech act misclassification
    - State blindness
    - Constraint drop
    - Metaphor collapse
    - Scope error
    - Identity overread
    - Premature execution
    """
    from amos_translation_layer import TRANSLATION_BUG_CLASSES

    return TRANSLATION_BUG_CLASSES


@router.get("/guard-rules")
async def get_translation_guard_rules() -> list[dict[str, str]]:
    """
    Get translation guard rules.

    Core safety rules that prevent direct execution from raw language.
    """
    from amos_translation_layer import TRANSLATION_GUARDS

    return TRANSLATION_GUARDS
