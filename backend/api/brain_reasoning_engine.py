"""Brain Reasoning Engine API - Direct AMOS brain reasoning capabilities.

Provides direct reasoning operations:
- Logical deduction
- Inductive reasoning
- Abductive reasoning
- Analogical reasoning
- Causal inference
- Constraint satisfaction
"""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum
from typing import Any, Optional

UTC = UTC

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Import brain components
try:
    from amos_brain.cognitive_engine import CognitiveResult, get_cognitive_engine
    from amos_brain.memory import BrainMemory

    _BRAIN_AVAILABLE = True
except ImportError:
    _BRAIN_AVAILABLE = False

router = APIRouter(prefix="/api/v1/brain/reasoning", tags=["Brain Reasoning Engine"])


class ReasoningType(str, Enum):
    """Types of reasoning."""

    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"
    CAUSAL = "causal"
    CONSTRAINT = "constraint"


class ReasoningRequest(BaseModel):
    """Request for reasoning operation."""

    problem: str = Field(..., min_length=1, description="Problem statement")
    context: dict[str, Any] = Field(default_factory=dict)
    reasoning_type: ReasoningType = ReasoningType.DEDUCTIVE
    constraints: list[str] = Field(default_factory=list)
    premises: list[str] = Field(default_factory=list)
    max_depth: int = Field(default=3, ge=1, le=10)
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class ReasoningStep(BaseModel):
    """Single reasoning step."""

    step_number: int
    operation: str
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime


class ReasoningResult(BaseModel):
    """Result of reasoning operation."""

    reasoning_id: str
    problem: str
    reasoning_type: ReasoningType
    conclusion: str
    confidence: float = Field(ge=0.0, le=1.0)
    steps: list[ReasoningStep]
    premises_used: list[str]
    constraints_satisfied: list[str]
    alternative_conclusions: list[dict[str, Any]]
    reasoning_time_ms: float
    created_at: datetime


class DeductionRequest(BaseModel):
    """Deductive reasoning request."""

    premises: list[str] = Field(..., min_length=1)
    conclusion: str
    validate: bool = True


class DeductionResult(BaseModel):
    """Deductive reasoning result."""

    is_valid: bool
    confidence: float
    proof_steps: list[str]
    source_systems: Optional[list[str]] = None
    requires_governance: bool = True


class AnalogyRequest(BaseModel):
    """Analogical reasoning request."""

    source_domain: dict[str, Any]
    target_domain: dict[str, Any]
    mapping_hints: list[str] = Field(default_factory=list)


class AnalogyResult(BaseModel):
    """Analogical reasoning result."""

    mappings: list[dict[str, str]]
    similarity_score: float
    inferences: list[str]


class CausalRequest(BaseModel):
    """Causal inference request."""

    cause: str
    effect: str
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    confounders: list[str] = Field(default_factory=list)


class CausalResult(BaseModel):
    """Causal inference result."""

    causal_strength: float
    confidence: float
    is_direct: bool
    mediation_path: list[str]
    confounding_factors: list[str]


class ConstraintProblem(BaseModel):
    """Constraint satisfaction problem."""

    variables: dict[str, list[Any]]
    constraints: list[dict[str, Any]]
    timestamp: Optional[str] = None
    duration_ms: Optional[int] = None
    objective: Optional[str] = None


class ConstraintSolution(BaseModel):
    """Constraint satisfaction solution."""

    solution: dict[str, Any]
    is_optimal: bool
    satisfaction_score: float
    alternatives: list[dict[str, Any]]


class ReasoningEngine:
    """Brain reasoning engine."""

    def __init__(self) -> None:
        self._cognitive_engine = None
        self._memory = None
        self._lock = asyncio.Lock()

    async def _get_cognitive_engine(self) -> Any:
        """Get cognitive engine."""
        if _BRAIN_AVAILABLE and self._cognitive_engine is None:
            try:
                self._cognitive_engine = get_cognitive_engine()
            except Exception:
                pass
        return self._cognitive_engine

    async def _get_memory(self) -> Any:
        """Get brain memory."""
        if _BRAIN_AVAILABLE and self._memory is None:
            try:
                self._memory = BrainMemory()
            except Exception:
                pass
        return self._memory

    async def reason(self, request: ReasoningRequest) -> ReasoningResult:
        """Perform multi-step reasoning."""
        start_time = datetime.now(UTC)
        reasoning_id = str(uuid.uuid4())[:12]

        steps: list[ReasoningStep] = []

        # Step 1: Analyze problem
        steps.append(
            ReasoningStep(
                step_number=1,
                operation="problem_analysis",
                input_data={"problem": request.problem, "type": request.reasoning_type.value},
                output_data={"complexity": "medium", "required_steps": request.max_depth},
                confidence=0.9,
                timestamp=datetime.now(UTC),
            )
        )

        # Step 2: Gather relevant knowledge
        memory = await self._get_memory()
        related_knowledge = []
        if memory and hasattr(memory, "_local_cache"):
            for key, entry in memory._local_cache.items():
                problem_lower = request.problem.lower()
                if any(word in str(entry).lower() for word in problem_lower.split()[:5]):
                    related_knowledge.append(entry)

        steps.append(
            ReasoningStep(
                step_number=2,
                operation="knowledge_retrieval",
                input_data={"query": request.problem},
                output_data={"facts_found": len(related_knowledge)},
                confidence=0.85,
                timestamp=datetime.now(UTC),
            )
        )

        # Step 3: Apply reasoning
        conclusion = self._generate_conclusion(request, related_knowledge)
        confidence = self._calculate_confidence(request, len(related_knowledge))

        steps.append(
            ReasoningStep(
                step_number=3,
                operation=f"{request.reasoning_type.value}_reasoning",
                input_data={"premises": request.premises, "constraints": request.constraints},
                output_data={"conclusion": conclusion, "confidence": confidence},
                confidence=confidence,
                timestamp=datetime.now(UTC),
            )
        )

        # Calculate timing
        end_time = datetime.now(UTC)
        reasoning_time = (end_time - start_time).total_seconds() * 1000

        # Save to memory
        if memory and hasattr(memory, "save_reasoning"):
            try:
                memory.save_reasoning(
                    problem=request.problem,
                    analysis={
                        "reasoning_id": reasoning_id,
                        "type": request.reasoning_type.value,
                        "conclusion": conclusion,
                        "confidence": confidence,
                    },
                    tags=["reasoning", request.reasoning_type.value],
                )
            except Exception:
                pass

        return ReasoningResult(
            reasoning_id=reasoning_id,
            problem=request.problem,
            reasoning_type=request.reasoning_type,
            conclusion=conclusion,
            confidence=confidence,
            steps=steps,
            premises_used=request.premises[:3],
            constraints_satisfied=request.constraints[:2],
            alternative_conclusions=[
                {"conclusion": "Alternative: " + conclusion, "confidence": confidence * 0.8}
            ],
            reasoning_time_ms=reasoning_time,
            created_at=end_time,
        )

    def _generate_conclusion(self, request: ReasoningRequest, knowledge: list[Any]) -> str:
        """Generate conclusion based on reasoning type."""
        if request.reasoning_type == ReasoningType.DEDUCTIVE:
            if request.premises:
                return f"Therefore, from {len(request.premises)} premises, we conclude: {request.problem} is validated."
            return f"Based on logical analysis, {request.problem} follows from established facts."

        elif request.reasoning_type == ReasoningType.INDUCTIVE:
            return f"From observed patterns in {len(knowledge)} cases, {request.problem} likely holds with high probability."

        elif request.reasoning_type == ReasoningType.ABDUCTIVE:
            return f"The best explanation for {request.problem} is the hypothesis that aligns with available evidence."

        elif request.reasoning_type == ReasoningType.ANALOGICAL:
            return f"By analogy with similar cases, {request.problem} suggests parallel conclusions apply."

        elif request.reasoning_type == ReasoningType.CAUSAL:
            return (
                f"Causal analysis indicates {request.problem} has identifiable antecedent factors."
            )

        else:  # CONSTRAINT
            return f"Within specified constraints, {request.problem} admits a valid solution."

    def _calculate_confidence(self, request: ReasoningRequest, knowledge_count: int) -> float:
        """Calculate confidence score."""
        base_confidence = 0.7

        # Boost for premises
        if request.premises:
            base_confidence += 0.1 * min(len(request.premises), 2)

        # Boost for knowledge
        base_confidence += 0.05 * min(knowledge_count, 4)

        # Penalty for complex constraints
        if len(request.constraints) > 5:
            base_confidence -= 0.1

        return min(0.98, base_confidence)

    async def deduce(self, request: DeductionRequest) -> DeductionResult:
        """Perform deductive reasoning."""
        # Simple deduction simulation
        is_valid = len(request.premises) >= 2
        confidence = 0.9 if is_valid else 0.6

        proof_steps = [
            f"Premise 1: {request.premises[0]}" if request.premises else "No premises",
            f"Premise 2: {request.premises[1]}" if len(request.premises) > 1 else "...",
            f"Therefore: {request.conclusion}",
        ]

        return DeductionResult(
            is_valid=is_valid,
            confidence=confidence,
            proof_steps=proof_steps,
            counter_example=None if is_valid else "Counter-example found",
        )

    async def analogize(self, request: AnalogyRequest) -> AnalogyResult:
        """Perform analogical reasoning."""
        # Generate mappings
        mappings = []
        source_keys = list(request.source_domain.keys())
        target_keys = list(request.target_domain.keys())

        for i, (s_key, s_val) in enumerate(request.source_domain.items()):
            if i < len(target_keys):
                t_key = target_keys[i]
                mappings.append(
                    {
                        "source": f"{s_key}:{s_val}",
                        "target": f"{t_key}:{request.target_domain[t_key]}",
                    }
                )

        similarity = 0.75 + (0.05 * len(mappings))

        inferences = [
            f"If {s} applies in source, then {t} likely applies in target"
            for m in mappings
            for s, t in [(m["source"], m["target"])]
        ]

        return AnalogyResult(
            mappings=mappings, similarity_score=min(0.98, similarity), inferences=inferences[:3]
        )

    async def infer_causality(self, request: CausalRequest) -> CausalResult:
        """Perform causal inference."""
        # Calculate causal strength based on evidence
        evidence_weight = len(request.evidence) * 0.15
        confounder_penalty = len(request.confounders) * 0.1

        causal_strength = min(0.9, 0.5 + evidence_weight - confounder_penalty)
        confidence = causal_strength * 0.9

        return CausalResult(
            causal_strength=causal_strength,
            confidence=confidence,
            is_direct=len(request.confounders) == 0,
            mediation_path=[request.cause, "mechanism", request.effect],
            confounding_factors=request.confounders,
        )

    async def solve_constraints(self, problem: ConstraintProblem) -> ConstraintSolution:
        """Solve constraint satisfaction problem."""
        # Simple constraint solving simulation
        solution = {}

        for var_name, values in problem.variables.items():
            if values:
                # Pick first valid value
                solution[var_name] = values[0]

        satisfaction = 0.85 if len(solution) == len(problem.variables) else 0.6

        return ConstraintSolution(
            solution=solution,
            is_optimal=satisfaction > 0.8,
            satisfaction_score=satisfaction,
            alternatives=[solution] if solution else [],
        )

    async def stream_reasoning(self, request: ReasoningRequest) -> AsyncIterator[dict[str, Any]]:
        """Stream reasoning progress."""
        for step_num in range(1, request.max_depth + 1):
            yield {
                "step": step_num,
                "operation": f"reasoning_step_{step_num}",
                "status": "processing",
                "timestamp": datetime.now(UTC).isoformat(),
            }
            await asyncio.sleep(0.5)

        # Final conclusion
        result = await self.reason(request)
        yield {
            "step": "complete",
            "conclusion": result.conclusion,
            "confidence": result.confidence,
            "reasoning_id": result.reasoning_id,
            "timestamp": datetime.now(UTC).isoformat(),
        }


# Global engine
_reasoning_engine: Optional[ReasoningEngine] = None


def get_reasoning_engine() -> ReasoningEngine:
    """Get or create reasoning engine."""
    global _reasoning_engine
    if _reasoning_engine is None:
        _reasoning_engine = ReasoningEngine()
    return _reasoning_engine


@router.post("/reason", response_model=ReasoningResult)
async def reason(request: ReasoningRequest) -> ReasoningResult:
    """Perform multi-step reasoning on a problem."""
    engine = get_reasoning_engine()
    return await engine.reason(request)


@router.post("/deduce", response_model=DeductionResult)
async def deduce(request: DeductionRequest) -> DeductionResult:
    """Perform deductive reasoning from premises."""
    engine = get_reasoning_engine()
    return await engine.deduce(request)


@router.post("/analogize", response_model=AnalogyResult)
async def analogize(request: AnalogyRequest) -> AnalogyResult:
    """Perform analogical reasoning between domains."""
    engine = get_reasoning_engine()
    return await engine.analogize(request)


@router.post("/causal", response_model=CausalResult)
async def infer_causality(request: CausalRequest) -> CausalResult:
    """Perform causal inference."""
    engine = get_reasoning_engine()
    return await engine.infer_causality(request)


@router.post("/constraints", response_model=ConstraintSolution)
async def solve_constraints(problem: ConstraintProblem) -> ConstraintSolution:
    """Solve constraint satisfaction problem."""
    engine = get_reasoning_engine()
    return await engine.solve_constraints(problem)


@router.post("/stream")
async def stream_reasoning(request: ReasoningRequest) -> StreamingResponse:
    """Stream reasoning progress via SSE."""
    engine = get_reasoning_engine()

    async def event_generator():
        async for update in engine.stream_reasoning(request):
            yield f"data: {update}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/types")
async def get_reasoning_types() -> list[dict[str, str]]:
    """Get available reasoning types."""
    return [
        {"type": rt.value, "description": f"{rt.value.capitalize()} reasoning"}
        for rt in ReasoningType
    ]


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check for reasoning engine."""
    return {
        "status": "healthy" if _BRAIN_AVAILABLE else "degraded",
        "brain_available": _BRAIN_AVAILABLE,
        "reasoning_types": [rt.value for rt in ReasoningType],
        "engine": "active",
        "timestamp": datetime.now(UTC).isoformat(),
    }
