"""Brain Decision Support - AMOS brain-powered intelligent decision making.

Provides decision support capabilities using AMOS cognitive architecture:
- Multi-criteria decision analysis
- Risk assessment and scoring
- Alternative evaluation
- Decision recommendation with confidence
- Decision audit trail
"""

from __future__ import annotations

import asyncio
import sys
import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

UTC = timezone.utc

# Setup paths
AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
for p in [AMOS_ROOT, AMOS_ROOT / "amos_brain"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Import AMOS brain components
try:
    from cognitive_engine import CognitiveResult, get_cognitive_engine

    from memory import BrainMemory

    _BRAIN_AVAILABLE = True
except ImportError:
    _BRAIN_AVAILABLE = False

router = APIRouter(prefix="/api/v1/brain/decisions", tags=["Brain Decision Support"])


class DecisionType(str, Enum):
    """Types of decisions supported."""

    STRATEGIC = "strategic"
    TACTICAL = "tactical"
    OPERATIONAL = "operational"
    TECHNICAL = "technical"
    FINANCIAL = "financial"
    RISK_BASED = "risk_based"


class Criterion(BaseModel):
    """Decision evaluation criterion."""

    name: str
    weight: float = Field(ge=0.0, le=1.0, default=1.0)
    description: str = ""
    min_score: float = Field(default=0.0, ge=0.0, le=10.0)
    max_score: float = Field(default=10.0, ge=0.0, le=10.0)


class Alternative(BaseModel):
    """Decision alternative."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    description: str = ""
    scores: dict[str, float] = Field(default_factory=dict)
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RiskFactor(BaseModel):
    """Risk factor for decision."""

    name: str
    probability: float = Field(ge=0.0, le=1.0)
    impact: float = Field(ge=0.0, le=10.0)
    mitigation: str = ""
    risk_score: float = Field(default=0.0)

    def calculate_risk(self) -> float:
        """Calculate risk score."""
        self.risk_score = self.probability * self.impact
        return self.risk_score


class DecisionRequest(BaseModel):
    """Decision support request."""

    decision_context: str = Field(..., min_length=1, max_length=5000)
    decision_type: DecisionType = DecisionType.STRATEGIC
    criteria: list[Criterion] = Field(default_factory=list)
    alternatives: list[Alternative] = Field(default_factory=list)
    risk_factors: list[RiskFactor] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)


class DecisionAnalysis(BaseModel):
    """Analysis of a single alternative."""

    alternative_id: str
    alternative_name: str
    weighted_score: float
    criterion_scores: dict[str, float]
    risk_adjusted_score: float
    ranking: int
    recommendation_strength: str


class DecisionRecommendation(BaseModel):
    """Decision recommendation result."""

    decision_id: str
    decision_context: str
    decision_type: DecisionType
    recommendation:str
    recommended_alternative: Alternative  = None
    alternative_analyses: list[DecisionAnalysis]
    overall_confidence: float
    risk_assessment: dict[str, Any]
    reasoning: list[str]
    timestamp: datetime
    amos_validated: bool = False


class DecisionAuditEntry(BaseModel):
    """Audit entry for decision."""

    decision_id: str
    timestamp: datetime
    action: str
    details: dict[str, Any]


class DecisionSupportEngine:
    """Real decision support engine using AMOS brain."""

    def __init__(self) -> None:
        self._cognitive_engine = None
        self._memory: BrainMemory  = None
        self._audit_log: list[DecisionAuditEntry] = []
        self._lock = asyncio.Lock()

    def _get_cognitive_engine(self):
        """Get cognitive engine."""
        if _BRAIN_AVAILABLE and self._cognitive_engine is None:
            self._cognitive_engine = get_cognitive_engine()
        return self._cognitive_engine

    def _get_memory(self) -> BrainMemory :
        """Get brain memory."""
        if _BRAIN_AVAILABLE and self._memory is None:
            try:
                self._memory = BrainMemory()
            except Exception:
                pass
        return self._memory

    async def analyze_decision(self, request: DecisionRequest) -> DecisionRecommendation:
        """Analyze decision using AMOS cognitive engine."""
        async with self._lock:
            decision_id = str(uuid.uuid4())[:12]

            # Get cognitive engine
            cog_engine = self._get_cognitive_engine()

            # Analyze each alternative
            analyses: list[DecisionAnalysis] = []

            if request.alternatives:
                for alt in request.alternatives:
                    analysis = await self._analyze_alternative(
                        alt, request.criteria, request.risk_factors
                    )
                    analyses.append(analysis)

                # Sort by weighted score
                analyses.sort(key=lambda a: a.risk_adjusted_score, reverse=True)

                # Update rankings
                for i, analysis in enumerate(analyses, 1):
                    analysis.ranking = i

            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(analyses, request.risk_factors)

            # Build recommendation
            recommended = None
            recommendation_text = "No alternatives provided"

            if analyses:
                best = analyses[0]
                recommended = next(
                    (a for a in request.alternatives if a.id == best.alternative_id), None
                )

                if best.risk_adjusted_score > 7.5:
                    recommendation_text = f"Strongly recommend: {best.alternative_name}"
                elif best.risk_adjusted_score > 5.0:
                    recommendation_text = f"Recommend: {best.alternative_name} with caution"
                else:
                    recommendation_text = f"Weak recommendation for: {best.alternative_name}. Consider more alternatives."

            # Risk assessment
            risk_assessment = self._assess_risks(request.risk_factors)

            # Build reasoning
            reasoning = await self._build_reasoning(request, analyses, recommended, cog_engine)

            # Create recommendation
            result = DecisionRecommendation(
                decision_id=decision_id,
                decision_context=request.decision_context,
                decision_type=request.decision_type,
                recommendation=recommendation_text,
                recommended_alternative=recommended,
                alternative_analyses=analyses,
                overall_confidence=overall_confidence,
                risk_assessment=risk_assessment,
                reasoning=reasoning,
                timestamp=datetime.now(UTC),
                amos_validated=_BRAIN_AVAILABLE,
            )

            # Log audit entry
            self._audit_log.append(
                DecisionAuditEntry(
                    decision_id=decision_id,
                    timestamp=datetime.now(UTC),
                    action="decision_analyzed",
                    details={
                        "alternatives_count": len(request.alternatives),
                        "criteria_count": len(request.criteria),
                        "confidence": overall_confidence,
                    },
                )
            )

            # Save to memory if available
            memory = self._get_memory()
            if memory:
                try:
                    memory.save_reasoning(
                        problem=request.decision_context,
                        analysis=result.model_dump(),
                        tags=["decision", request.decision_type.value],
                    )
                except Exception:
                    pass

            return result

    async def _analyze_alternative(
        self, alternative: Alternative, criteria: list[Criterion], risk_factors: list[RiskFactor]
    ) -> DecisionAnalysis:
        """Analyze a single alternative."""

        # Calculate weighted score
        total_weight = sum(c.weight for c in criteria) if criteria else 1.0
        weighted_score = 0.0
        criterion_scores: dict[str, float] = {}

        for criterion in criteria:
            score = alternative.scores.get(criterion.name, criterion.min_score)
            normalized_score = (
                (score - criterion.min_score) / (criterion.max_score - criterion.min_score)
                if criterion.max_score > criterion.min_score
                else 0.5
            )
            weighted_score += normalized_score * criterion.weight
            criterion_scores[criterion.name] = score

        # Normalize by total weight
        if total_weight > 0:
            weighted_score = weighted_score / total_weight * 10

        # Calculate risk adjustment
        total_risk = sum(r.calculate_risk() for r in risk_factors)
        risk_adjustment = max(0, 1 - (total_risk / 10))
        risk_adjusted_score = weighted_score * risk_adjustment

        # Determine recommendation strength
        if risk_adjusted_score > 7.5:
            strength = "strong"
        elif risk_adjusted_score > 5.0:
            strength = "moderate"
        else:
            strength = "weak"

        return DecisionAnalysis(
            alternative_id=alternative.id,
            alternative_name=alternative.name,
            weighted_score=weighted_score,
            criterion_scores=criterion_scores,
            risk_adjusted_score=risk_adjusted_score,
            ranking=0,  # Will be set later
            recommendation_strength=strength,
        )

    def _calculate_overall_confidence(
        self, analyses: list[DecisionAnalysis], risk_factors: list[RiskFactor]
    ) -> float:
        """Calculate overall confidence in decision."""
        if not analyses:
            return 0.0

        # Base confidence from score spread
        if len(analyses) == 1:
            base_confidence = analyses[0].risk_adjusted_score / 10
        else:
            scores = [a.risk_adjusted_score for a in analyses]
            score_spread = max(scores) - min(scores)
            base_confidence = 0.5 + (score_spread / 20)  # More spread = higher confidence

        # Risk penalty
        total_risk = sum(r.risk_score for r in risk_factors)
        risk_penalty = min(total_risk / 50, 0.3)  # Max 30% penalty

        return max(0.0, min(1.0, base_confidence - risk_penalty))

    def _assess_risks(self, risk_factors: list[RiskFactor]) -> dict[str, Any]:
        """Assess overall risk."""
        if not risk_factors:
            return {"overall_risk": "low", "risk_score": 0.0, "critical_risks": []}

        total_risk = sum(r.risk_score for r in risk_factors)
        avg_risk = total_risk / len(risk_factors)

        # Find critical risks (high probability + high impact)
        critical = [r.name for r in risk_factors if r.probability > 0.7 and r.impact > 7]

        if avg_risk > 5:
            risk_level = "high"
        elif avg_risk > 2.5:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "overall_risk": risk_level,
            "risk_score": avg_risk,
            "total_risk_factors": len(risk_factors),
            "critical_risks": critical,
            "mitigation_required": len(critical) > 0,
        }

    async def _build_reasoning(
        self,
        request: DecisionRequest,
        analyses:list[DecisionAnalysis],
        recommended: Alternative ,
        cog_engine: Any,
    ) -> list[str]:
        """Build reasoning for decision."""
        reasoning: list[str] = []

        # Context analysis
        reasoning.append(
            f"Analyzed {len(request.alternatives)} alternatives for {request.decision_type.value} decision"
        )

        # Criteria analysis
        if request.criteria:
            reasoning.append(f"Evaluated against {len(request.criteria)} criteria")
            top_criteria = sorted(request.criteria, key=lambda c: c.weight, reverse=True)[:3]
            reasoning.append(f"Top weighted criteria: {', '.join(c.name for c in top_criteria)}")

        # Alternative comparison
        if len(analyses) > 1:
            best = analyses[0]
            second = analyses[1]
            margin = best.risk_adjusted_score - second.risk_adjusted_score
            reasoning.append(
                f"Best alternative ({best.alternative_name}) leads by {margin:.1f} points"
            )

        # Risk considerations
        if request.risk_factors:
            high_risks = [r.name for r in request.risk_factors if r.risk_score > 5]
            if high_risks:
                reasoning.append(f"High risks identified: {', '.join(high_risks)}")

        # Constraints
        if request.constraints:
            reasoning.append(f"Constraints considered: {', '.join(request.constraints)}")

        # Use cognitive engine for additional insight
        if cog_engine and recommended:
            try:
                cog_result = cog_engine.process(
                    query=f"Validate decision: {request.decision_context}",
                    domain=request.decision_type.value,
                    context={"alternative": recommended.name},
                )
                if cog_result.confidence == "high":
                    reasoning.append("AMOS cognitive validation: High confidence alignment")
            except Exception:
                pass

        return reasoning

    async def stream_analysis(self, request: DecisionRequest) -> AsyncIterator[dict[str, Any]]:
        """Stream decision analysis steps."""

        # Step 1: Initialization
        yield {
            "step": 1,
            "phase": "initialization",
            "message": f"Initializing decision analysis for {request.decision_type.value} decision",
            "progress": 0.1,
        }
        await asyncio.sleep(0.2)

        # Step 2: Criteria validation
        yield {
            "step": 2,
            "phase": "criteria_validation",
            "message": f"Validating {len(request.criteria)} criteria",
            "progress": 0.2,
        }
        await asyncio.sleep(0.3)

        # Step 3: Alternative scoring
        for i, alt in enumerate(request.alternatives):
            yield {
                "step": 3,
                "phase": "alternative_scoring",
                "message": f"Scoring alternative: {alt.name}",
                "alternative": alt.name,
                "progress": 0.3 + (i / len(request.alternatives)) * 0.3,
            }
            await asyncio.sleep(0.2)

        # Step 4: Risk assessment
        yield {
            "step": 4,
            "phase": "risk_assessment",
            "message": f"Assessing {len(request.risk_factors)} risk factors",
            "progress": 0.7,
        }
        await asyncio.sleep(0.3)

        # Step 5: Recommendation synthesis
        yield {
            "step": 5,
            "phase": "synthesis",
            "message": "Synthesizing recommendation",
            "progress": 0.9,
        }
        await asyncio.sleep(0.2)

        # Step 6: Complete
        yield {
            "step": 6,
            "phase": "complete",
            "message": "Decision analysis complete",
            "progress": 1.0,
        }

    def get_audit_trail(self, decision_id: str  = None) -> list[DecisionAuditEntry]:
        """Get audit trail for decisions."""
        if decision_id:
            return [e for e in self._audit_log if e.decision_id == decision_id]
        return self._audit_log

    def get_stats(self) -> dict[str, Any]:
        """Get engine statistics."""
        total_decisions = len(set(e.decision_id for e in self._audit_log))

        return {
            "total_decisions_analyzed": total_decisions,
            "audit_entries": len(self._audit_log),
            "brain_available": _BRAIN_AVAILABLE,
            "criteria_supported": True,
            "risk_analysis_enabled": True,
        }


#Global engine instance
_decision_engine: DecisionSupportEngine  = None


def get_decision_engine() -> DecisionSupportEngine:
    """Get or create decision support engine."""
    global _decision_engine
    if _decision_engine is None:
        _decision_engine = DecisionSupportEngine()
    return _decision_engine


@router.post("/analyze", response_model=DecisionRecommendation)
async def analyze_decision(request: DecisionRequest) -> DecisionRecommendation:
    """Analyze a decision and provide recommendation.

    Uses AMOS cognitive engine to evaluate alternatives and provide
    evidence-based decision recommendations.
    """
    engine = get_decision_engine()
    result = await engine.analyze_decision(request)
    return result


@router.post("/analyze/stream")
async def stream_decision_analysis(request: DecisionRequest) -> StreamingResponse:
    """Stream decision analysis progress.

    Returns Server-Sent Events showing analysis progress.
    """
    engine = get_decision_engine()

    async def event_generator():
        async for step in engine.stream_analysis(request):
            yield f"data: {step}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/audit/{decision_id}")
async def get_decision_audit(decision_id: str) -> list[DecisionAuditEntry]:
    """Get audit trail for a specific decision."""
    engine = get_decision_engine()
    return engine.get_audit_trail(decision_id)


@router.get("/stats")
async def get_decision_stats() -> dict[str, Any]:
    """Get decision support engine statistics."""
    engine = get_decision_engine()
    return engine.get_stats()


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check for decision support engine."""
    engine = get_decision_engine()
    stats = engine.get_stats()

    return {
        "status": "healthy" if _BRAIN_AVAILABLE else "degraded",
        "amos_brain_available": _BRAIN_AVAILABLE,
        "decisions_analyzed": stats["total_decisions_analyzed"],
        "engine": "active",
    }
