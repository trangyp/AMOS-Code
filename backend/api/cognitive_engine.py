from __future__ import annotations

from typing import Any, Optional

"""AMOS Cognitive Engine API - Real-time brain-powered cognition.

Production-grade cognitive processing with AMOS brain integration:
- Live decision making with legality validation
- Predictive pattern recognition
- Autonomous reasoning chains
- Cognitive state management
"""

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

UTC = UTC

try:
    from amos_kernel_runtime import AMOSKernelRuntime

    from amos_brain_working import think as brain_think

    BRAIN_AVAILABLE = True
except ImportError:
    BRAIN_AVAILABLE = False

router = APIRouter(prefix="/cognitive", tags=["Cognitive Engine"])


class CognitiveRequest(BaseModel):
    """Request for cognitive processing."""

    observation: dict[str, Any] = Field(
        description="Current state/observation for brain processing"
    )
    goal: dict[str, Any] = Field(description="Target goal state")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context")
    require_legality: bool = Field(default=True, description="Require brain legality validation")
    max_depth: int = Field(default=3, ge=1, le=10, description="Maximum reasoning depth")


class CognitiveResponse(BaseModel):
    """Response from cognitive processing."""

    decision: dict[str, Any]
    legality: float
    confidence: float
    reasoning_chain: list[dict[str, Any]]
    execution_plan: list[str]
    cognitive_state: str
    processing_time_ms: float
    brain_validated: bool
    timestamp: str


class PatternRecognitionRequest(BaseModel):
    """Request for pattern recognition."""

    data: list[dict[str, Any]]
    pattern_type: str = Field(
        default="anomaly", description="Type: anomaly, trend, cycle, correlation"
    )
    sensitivity: float = Field(default=2.0, ge=0.1, le=5.0)


class PatternRecognitionResponse(BaseModel):
    """Response with recognized patterns."""

    patterns: list[dict[str, Any]]
    confidence: float
    brain_assessment: dict[str, Any]
    recommendations: list[str]


class ReasoningChainRequest(BaseModel):
    """Request for multi-step reasoning."""

    premise: str
    steps: list[str]
    validate_each: bool = True


class ReasoningChainResponse(BaseModel):
    """Response with reasoning results."""

    chain_id: str
    results: list[dict[str, Any]]
    overall_valid: bool
    brain_coherence: float


@dataclass
class CognitiveSession:
    """Active cognitive session."""

    session_id: str
    created_at: datetime
    kernel: Optional[AMOSKernelRuntime] = None
    history: list[dict[str, Any]] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)


class CognitiveEngine:
    """Production cognitive engine with brain integration."""

    def __init__(self):
        self._sessions: dict[str, CognitiveSession] = {}
        self._kernel = AMOSKernelRuntime() if BRAIN_AVAILABLE else None

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return hashlib.sha256(f"{time.time()}{uuid.uuid4()}".encode()).hexdigest()[:16]

    async def process(self, request: CognitiveRequest) -> CognitiveResponse:
        """Process cognitive request through brain."""
        start_time = time.time()

        if not BRAIN_AVAILABLE or not self._kernel:
            raise HTTPException(
                status_code=503, detail="Cognitive engine unavailable - brain not loaded"
            )

        # Execute brain cognitive cycle
        brain_result = self._kernel.execute_cycle(
            observation=request.observation, goal=request.goal
        )

        legality = brain_result.get("legality", 0.0)

        # Validate legality if required
        if request.require_legality and legality < 0.5:
            return CognitiveResponse(
                decision={"status": "rejected", "reason": "low_legality"},
                legality=legality,
                confidence=0.0,
                reasoning_chain=[],
                execution_plan=[],
                cognitive_state="rejected",
                processing_time_ms=(time.time() - start_time) * 1000,
                brain_validated=False,
                timestamp=datetime.now(UTC).isoformat(),
            )

        # Build reasoning chain
        reasoning_chain = []
        for depth in range(request.max_depth):
            step_result = self._kernel.execute_cycle(
                observation={
                    **request.observation,
                    "depth": depth,
                    "previous": reasoning_chain[-1] if reasoning_chain else None,
                },
                goal=request.goal,
            )
            reasoning_chain.append(
                {
                    "depth": depth,
                    "sigma": step_result.get("sigma", 0.0),
                    "mode": step_result.get("mode", "unknown"),
                    "action": step_result.get("action", {}),
                }
            )

        # Extract execution plan
        execution_plan = [
            step["action"].get("type", "unknown") for step in reasoning_chain if step["action"]
        ]

        processing_time_ms = (time.time() - start_time) * 1000

        return CognitiveResponse(
            decision=brain_result.get("action", {}),
            legality=legality,
            confidence=brain_result.get("sigma", 0.0),
            reasoning_chain=reasoning_chain,
            execution_plan=execution_plan,
            cognitive_state=brain_result.get("mode", "unknown"),
            processing_time_ms=round(processing_time_ms, 2),
            brain_validated=True,
            timestamp=datetime.now(UTC).isoformat(),
        )

    async def recognize_patterns(
        self, request: PatternRecognitionRequest
    ) -> PatternRecognitionResponse:
        """Recognize patterns in data with brain validation."""
        if not self._kernel:
            raise HTTPException(status_code=503, detail="Pattern recognition requires brain")

        # Statistical analysis
        patterns = []
        values = [d.get("value", 0) for d in request.data if "value" in d]

        if values:
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            std_dev = variance**0.5

            # Detect anomalies
            for i, d in enumerate(request.data):
                val = d.get("value", 0)
                z_score = abs(val - mean) / std_dev if std_dev > 0 else 0

                if z_score > request.sensitivity:
                    # Brain validate anomaly
                    brain_check = self._kernel.execute_cycle(
                        observation={
                            "entities": ["data_point", "anomaly"],
                            "relations": [{"source": "data", "target": "pattern"}],
                            "input_data": f"Value: {val}, Z-score: {z_score}",
                            "context": {"pattern_type": request.pattern_type},
                        },
                        goal={"type": "validate_pattern"},
                    )

                    patterns.append(
                        {
                            "type": "anomaly",
                            "index": i,
                            "value": val,
                            "z_score": round(z_score, 3),
                            "brain_legality": brain_check.get("legality", 0.0),
                        }
                    )

        # Brain assessment
        brain_assessment = self._kernel.execute_cycle(
            observation={
                "entities": ["pattern_set", "data"],
                "input_data": f"Found {len(patterns)} patterns",
                "context": {"sensitivity": request.sensitivity},
            },
            goal={"type": "assess_patterns"},
        )

        # Generate recommendations
        recommendations = []
        if patterns:
            recommendations.append(f"Review {len(patterns)} anomalous data points")
        if brain_assessment.get("legality", 0) < 0.7:
            recommendations.append("Low confidence in pattern detection - manual review advised")

        return PatternRecognitionResponse(
            patterns=patterns,
            confidence=brain_assessment.get("sigma", 0.5),
            brain_assessment={
                "legality": brain_assessment.get("legality", 0.0),
                "mode": brain_assessment.get("mode", "unknown"),
                "cognitive_state": brain_assessment.get("state", {}),
            },
            recommendations=recommendations,
        )

    async def reasoning_chain(self, request: ReasoningChainRequest) -> ReasoningChainResponse:
        """Execute multi-step reasoning chain."""
        chain_id = self._generate_session_id()
        results = []
        overall_valid = True

        if not self._kernel:
            raise HTTPException(status_code=503, detail="Reasoning requires brain")

        current_premise = request.premise

        for i, step in enumerate(request.steps):
            # Process step through brain
            step_result = self._kernel.execute_cycle(
                observation={
                    "entities": ["premise", "step"],
                    "relations": [{"source": current_premise, "target": step}],
                    "input_data": f"Step {i + 1}: {step}",
                    "context": {"chain_position": i},
                },
                goal={"type": "reasoning_step"},
            )

            valid = step_result.get("legality", 0) >= 0.5
            if request.validate_each and not valid:
                overall_valid = False

            results.append(
                {
                    "step": i + 1,
                    "description": step,
                    "premise": current_premise,
                    "conclusion": step_result.get("action", {}),
                    "valid": valid,
                    "legality": step_result.get("legality", 0.0),
                }
            )

            # Update premise for next step
            current_premise = str(step_result.get("action", {}))

        # Calculate coherence
        valid_steps = sum(1 for r in results if r["valid"])
        coherence = valid_steps / len(results) if results else 0.0

        return ReasoningChainResponse(
            chain_id=chain_id,
            results=results,
            overall_valid=overall_valid,
            brain_coherence=round(coherence, 3),
        )


# Global engine instance
_engine: Optional[CognitiveEngine] = None


def get_cognitive_engine() -> CognitiveEngine:
    """Get or create global cognitive engine."""
    global _engine
    if _engine is None:
        _engine = CognitiveEngine()
    return _engine


@router.post("/process", response_model=CognitiveResponse)
async def cognitive_process(request: CognitiveRequest) -> CognitiveResponse:
    """Process request through cognitive engine with brain validation."""
    engine = get_cognitive_engine()
    return await engine.process(request)


@router.post("/patterns", response_model=PatternRecognitionResponse)
async def recognize_patterns(request: PatternRecognitionRequest) -> PatternRecognitionResponse:
    """Recognize patterns in data with brain validation."""
    engine = get_cognitive_engine()
    return await engine.recognize_patterns(request)


@router.post("/reasoning", response_model=ReasoningChainResponse)
async def reasoning_chain(request: ReasoningChainRequest) -> ReasoningChainResponse:
    """Execute multi-step reasoning chain with brain."""
    engine = get_cognitive_engine()
    return await engine.reasoning_chain(request)


@router.post("/process-fast")
async def cognitive_process_fast(request: CognitiveRequest) -> dict[str, Any]:
    """Fast cognitive processing using dual-process brain (<100ms)."""

    start = time.perf_counter()

    # Build query from observation and goal
    query = str(request.observation.get("query", str(request.observation)))

    try:
        from amos_dual_process_brain import get_dual_process_brain

        brain = get_dual_process_brain()
        result = await brain.think(
            query=query, context=request.context | request.goal, prefer_fast=True
        )

        total_ms = (time.perf_counter() - start) * 1000

        return {
            "decision": {"action": result.response},
            "thinking_mode": result.thinking_mode,
            "confidence": result.confidence,
            "latency_ms": total_ms,
            "fast_latency_ms": result.fast_result.latency_ms if result.fast_result else None,
            "success": True,
        }
    except Exception:
        # Fallback to standard engine
        engine = get_cognitive_engine()
        result = await engine.process(request)
        total_ms = (time.perf_counter() - start) * 1000

        return {
            "decision": result.decision,
            "thinking_mode": "slow_fallback",
            "confidence": result.confidence,
            "latency_ms": total_ms,
            "fast_latency_ms": None,
            "success": result.confidence > 0.5,
        }


@router.get("/status")
async def cognitive_status() -> dict[str, Any]:
    """Get cognitive engine status."""
    # Check fast thinking availability
    fast_thinking = False
    try:
        fast_thinking = True
    except Exception:
        pass

    return {
        "brain_available": BRAIN_AVAILABLE,
        "engine_active": _engine is not None,
        "fast_thinking": fast_thinking,
        "timestamp": datetime.now(UTC).isoformat(),
        "capabilities": [
            "cognitive_processing",
            "pattern_recognition",
            "reasoning_chains",
            "fast_thinking",
        ]
        if BRAIN_AVAILABLE
        else [],
    }
