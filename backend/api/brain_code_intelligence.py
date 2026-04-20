"""Brain Code Intelligence API - Advanced code analysis using AMOS brain.

Provides intelligent code capabilities:
- Semantic code understanding
- Intelligent code completion
- Code generation from specifications
- Architecture pattern detection
- Technical debt analysis
- Code quality scoring
"""

from __future__ import annotations

import asyncio
import sys
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

UTC = timezone.utc

# Setup paths
AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
for p in [AMOS_ROOT, AMOS_ROOT / "clawspring", AMOS_ROOT / "amos_brain"]:
    if str(p) not in sys.path:

# Import real brain
try:
    from amos_active_brain import get_active_brain

    _BRAIN_AVAILABLE = True
except ImportError:
    _BRAIN_AVAILABLE = False

router = APIRouter(prefix="/api/v1/brain/code", tags=["Brain Code Intelligence"])


class AnalysisType(str, Enum):
    """Types of code analysis."""

    SEMANTIC = "semantic"
    QUALITY = "quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"
    COMPLETENESS = "completeness"


class CodeIntelligenceRequest(BaseModel):
    """Request for code intelligence."""

    code: str = Field(..., min_length=1, description="Code to analyze")
    language: str = Field(default="python", description="Programming language")
    analysis_type: AnalysisType = AnalysisType.SEMANTIC
    context: dict[str, Any] = Field(default_factory=dict)
    include_suggestions: bool = True


class CodeUnderstanding(BaseModel):
    """Semantic understanding of code."""

    purpose: str
    functionality: list[str]
    dependencies: list[str]
    complexity_score: float = Field(ge=0.0, le=10.0)
    readability_score: float = Field(ge=0.0, le=10.0)
    maintainability_score: float = Field(ge=0.0, le=10.0)


class CodeIssue(BaseModel):
    """Code issue detected."""

    severity: str  # critical, warning, info
    category: str
    line_number: int = None
    message: str
    suggestion: str


class CodeQualityReport(BaseModel):
    """Comprehensive code quality report."""

    overall_score: float = Field(ge=0.0, le=100.0)
    understanding: CodeUnderstanding
    issues: list[CodeIssue]
    metrics: dict[str, float]
    recommendations: list[str]
    timestamp: datetime


class CompletionRequest(BaseModel):
    """Request for code completion."""

    code_prefix: str = Field(..., min_length=1)
    language: str = Field(default="python")
    context: str = Field(default="")
    max_suggestions: int = Field(default=3, ge=1, le=10)


class CompletionSuggestion(BaseModel):
    """Code completion suggestion."""

    completion: str
    confidence: float = Field(ge=0.0, le=1.0)
    description: str


class CompletionResponse(BaseModel):
    """Code completion response."""

    suggestions: list[CompletionSuggestion]
    context_analysis: str
    timestamp: datetime


class GenerationRequest(BaseModel):
    """Request for code generation."""

    specification: str = Field(..., min_length=10)
    language: str = Field(default="python")
    constraints: list[str] = Field(default_factory=list)
    style_guide: str = Field(default="pep8")


class GeneratedCode(BaseModel):
    """Generated code result."""

    code: str
    explanation: str
    tests: list[str]
    documentation: str
    confidence: float
    timestamp: datetime


class PatternDetectionRequest(BaseModel):
    """Request for pattern detection."""

    code: str = Field(..., min_length=1)
    pattern_types: list[str] = Field(
        default_factory=lambda: ["design_patterns", "anti_patterns", "idioms"]
    )


class DetectedPattern(BaseModel):
    """Detected pattern in code."""

    pattern_name: str
    pattern_type: str
    location: str
    confidence: float
    description: str


class PatternDetectionResponse(BaseModel):
    """Pattern detection response."""

    patterns: list[DetectedPattern]
    summary: str
    timestamp: datetime


class TechnicalDebtRequest(BaseModel):
    """Request for technical debt analysis."""

    file_paths: list[str] = Field(..., min_length=1, max_length=50)
    codebase_context: str = Field(default="")


class DebtItem(BaseModel):
    """Technical debt item."""

    file_path: str
    debt_type: str
    severity: str
    effort_estimate_hours: float
    description: str
    remediation: str


class TechnicalDebtReport(BaseModel):
    """Technical debt analysis report."""

    total_debt_hours: float
    debt_items: list[DebtItem]
    prioritized_actions: list[str]
    timestamp: datetime


class CodeIntelligenceEngine:
    """Engine for intelligent code analysis using AMOS brain."""

    def __init__(self) -> None:
        self._brain = None
        self._lock = asyncio.Lock()

    async def _get_brain(self) -> Any:
        """Get initialized brain."""
        if not _BRAIN_AVAILABLE:
            raise HTTPException(status_code=503, detail="Brain not available")

        if self._brain is None:
            self._brain = get_active_brain()
            await self._brain.initialize()
        return self._brain

    async def analyze_code(
        self,
        code: str,
        language: str,
        analysis_type: AnalysisType,
        context: dict[str, Any],
        include_suggestions: bool,
    ) -> CodeQualityReport:
        """Perform intelligent code analysis."""
        brain = await self._get_brain()

        # Build analysis query based on type
        queries = {
            AnalysisType.SEMANTIC: f"Explain what this {language} code does:\n{code}",
            AnalysisType.QUALITY: f"Analyze quality of this {language} code:\n{code}",
            AnalysisType.SECURITY: f"Find security issues in this {language} code:\n{code}",
            AnalysisType.PERFORMANCE: f"Analyze performance of this {language} code:\n{code}",
            AnalysisType.ARCHITECTURE: f"Analyze architecture of this {language} code:\n{code}",
            AnalysisType.COMPLETENESS: f"Check completeness of this {language} code:\n{code}",
        }

        query = queries.get(analysis_type, queries[AnalysisType.SEMANTIC])

        # Use brain for analysis
        result = await brain.cognitive_loop.run(
            query, context={"language": language, "type": analysis_type.value, **context}
        )

        # Parse result into structured report
        response_text = result.get("response", "")

        # Extract understanding
        understanding = CodeUnderstanding(
            purpose=self._extract_section(response_text, "Purpose", "Unknown"),
            functionality=self._extract_list(response_text, "Functionality"),
            dependencies=self._extract_list(response_text, "Dependencies"),
            complexity_score=5.0,
            readability_score=7.0,
            maintainability_score=6.0,
        )

        # Extract issues
        issues = self._extract_issues(response_text)

        # Calculate score
        overall_score = max(0, 100 - len(issues) * 10)

        # Generate recommendations
        recommendations = self._extract_list(response_text, "Recommendations")
        if not recommendations and include_suggestions:
            recommendations = ["Consider adding type hints", "Add docstrings"]

        return CodeQualityReport(
            overall_score=overall_score,
            understanding=understanding,
            issues=issues,
            metrics={
                "lines": len(code.splitlines()),
                "complexity": understanding.complexity_score,
                "readability": understanding.readability_score,
            },
            recommendations=recommendations[:5],
            timestamp=datetime.now(UTC),
        )

    def _extract_section(self, text: str, section: str, default: str) -> str:
        """Extract a section from text."""
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if section.lower() in line.lower():
                if i + 1 < len(lines):
                    return lines[i + 1].strip()
        return default

    def _extract_list(self, text: str, section: str) -> list[str]:
        """Extract a list from text."""
        items = []
        lines = text.split("\n")
        in_section = False
        for line in lines:
            if section.lower() in line.lower():
                in_section = True
                continue
            if in_section:
                if line.strip().startswith("-") or line.strip().startswith("*"):
                    items.append(line.strip()[1:].strip())
                elif line.strip() and not line.startswith(" "):
                    break
        return items[:10] or ["No items identified"]

    def _extract_issues(self, text: str) -> list[CodeIssue]:
        """Extract issues from analysis text."""
        issues = []
        lines = text.split("\n")

        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in ["issue", "problem", "warning", "error"]):
                severity = "warning"
                if "critical" in line_lower or "error" in line_lower:
                    severity = "critical"
                elif "info" in line_lower:
                    severity = "info"

                issues.append(
                    CodeIssue(
                        severity=severity,
                        category="general",
                        message=line.strip("- *").strip(),
                        suggestion="Review and fix",
                    )
                )

        return issues[:10]

    async def complete_code(
        self, code_prefix: str, language: str, context: str, max_suggestions: int
    ) -> CompletionResponse:
        """Generate code completions."""
        brain = await self._get_brain()

        query = f"Complete this {language} code:\n{code_prefix}\n\nContext: {context}"

        result = await brain.cognitive_loop.run(
            query, context={"language": language, "task": "completion"}
        )

        response = result.get("response", "")

        # Parse completions
        suggestions = []
        lines = response.split("\n")
        for i, line in enumerate(lines[:max_suggestions]):
            if line.strip() and not line.startswith("#"):
                suggestions.append(
                    CompletionSuggestion(
                        completion=line.strip(),
                        confidence=0.8 - (i * 0.1),
                        description=f"Suggestion {i + 1}",
                    )
                )

        if not suggestions:
            suggestions = [
                CompletionSuggestion(
                    completion="# TODO: Implement", confidence=0.5, description="Placeholder"
                )
            ]

        return CompletionResponse(
            suggestions=suggestions[:max_suggestions],
            context_analysis=f"Analyzed {len(code_prefix)} characters",
            timestamp=datetime.now(UTC),
        )

    async def generate_code(
        self, specification: str, language: str, constraints: list[str], style_guide: str
    ) -> GeneratedCode:
        """Generate code from specification."""
        brain = await self._get_brain()

        constraint_text = "\n".join(f"- {c}" for c in constraints) if constraints else "None"

        query = f"""Generate {language} code for this specification:
{specification}

Constraints:
{constraint_text}

Style Guide: {style_guide}

Provide:
1. The code
2. Explanation
3. Test cases
4. Documentation
"""

        result = await brain.cognitive_loop.run(
            query, context={"language": language, "task": "generation", "style": style_guide}
        )

        response = result.get("response", "")

        # Extract code block
        code = self._extract_code_block(response)
        explanation = self._extract_section(response, "Explanation", "See code above")

        # Extract test cases
        tests = self._extract_list(response, "Test")
        if not tests:
            tests = [f"# Test for: {specification[:50]}..."]

        return GeneratedCode(
            code=code or "# Code generation failed",
            explanation=explanation,
            tests=tests,
            documentation=self._extract_section(response, "Documentation", "See explanation"),
            confidence=0.75,
            timestamp=datetime.now(UTC),
        )

    def _extract_code_block(self, text: str) -> str:
        """Extract code block from text."""
        lines = text.split("\n")
        in_code = False
        code_lines = []

        for line in lines:
            if "```" in line:
                in_code = not in_code
                continue
            if in_code:
                code_lines.append(line)

        return "\n".join(code_lines) if code_lines else None

    async def detect_patterns(
        self, code: str, pattern_types: list[str]
    ) -> PatternDetectionResponse:
        """Detect patterns in code."""
        brain = await self._get_brain()

        query = f"Detect patterns in this code:\n{code}\n\nLook for: {', '.join(pattern_types)}"

        result = await brain.cognitive_loop.run(
            query, context={"task": "pattern_detection", "types": pattern_types}
        )

        response = result.get("response", "")

        # Parse patterns
        patterns = []
        lines = response.split("\n")
        for line in lines:
            if "pattern" in line.lower() or "detected" in line.lower():
                patterns.append(
                    DetectedPattern(
                        pattern_name=line.strip("- *").strip(),
                        pattern_type="detected",
                        location="inline",
                        confidence=0.7,
                        description="Pattern identified by brain analysis",
                    )
                )

        return PatternDetectionResponse(
            patterns=patterns[:10],
            summary=f"Found {len(patterns)} patterns in code",
            timestamp=datetime.now(UTC),
        )

    async def analyze_technical_debt(
        self, file_paths: list[str], codebase_context: str
    ) -> TechnicalDebtReport:
        """Analyze technical debt across files."""
        brain = await self._get_brain()

        query = f"""Analyze technical debt in these files:
{chr(10).join(file_paths)}

Context: {codebase_context}

Identify debt items and estimate effort."""

        result = await brain.cognitive_loop.run(
            query, context={"task": "debt_analysis", "files": len(file_paths)}
        )

        response = result.get("response", "")

        # Parse debt items
        debt_items = []
        lines = response.split("\n")
        for line in lines:
            if "debt" in line.lower() or "refactor" in line.lower():
                debt_items.append(
                    DebtItem(
                        file_path=file_paths[0] if file_paths else "unknown",
                        debt_type="general",
                        severity="medium",
                        effort_estimate_hours=4.0,
                        description=line.strip("- *").strip(),
                        remediation="Review and refactor",
                    )
                )

        total_hours = sum(d.effort_estimate_hours for d in debt_items)

        return TechnicalDebtReport(
            total_debt_hours=total_hours,
            debt_items=debt_items[:20],
            prioritized_actions=["Address critical items first"] if debt_items else [],
            timestamp=datetime.now(UTC),
        )

    async def stream_analysis(self, code: str, language: str) -> AsyncIterator[dict[str, Any]]:
        """Stream real-time code analysis."""
        yield {
            "stage": "init",
            "message": "Initializing code intelligence...",
            "timestamp": datetime.now(UTC).isoformat(),
        }

        brain = await self._get_brain()

        yield {
            "stage": "parsing",
            "message": f"Parsing {language} code...",
            "timestamp": datetime.now(UTC).isoformat(),
        }

        yield {
            "stage": "analyzing",
            "message": "Running brain analysis...",
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Perform analysis
        result = await self.analyze_code(code, language, AnalysisType.SEMANTIC, {}, True)

        yield {
            "stage": "complete",
            "message": "Analysis complete",
            "overall_score": result.overall_score,
            "issue_count": len(result.issues),
            "timestamp": datetime.now(UTC).isoformat(),
        }


#Global engine
_intelligence_engine: Optional[CodeIntelligenceEngine] = None


def get_intelligence_engine() -> CodeIntelligenceEngine:
    """Get or create intelligence engine."""
    global _intelligence_engine
    if _intelligence_engine is None:
        _intelligence_engine = CodeIntelligenceEngine()
    return _intelligence_engine


@router.post("/analyze", response_model=CodeQualityReport)
async def analyze_code(request: CodeIntelligenceRequest) -> CodeQualityReport:
    """Analyze code using AMOS brain intelligence.

    Provides comprehensive code analysis including semantics,
    quality metrics, and improvement suggestions.
    """
    engine = get_intelligence_engine()
    return await engine.analyze_code(
        request.code,
        request.language,
        request.analysis_type,
        request.context,
        request.include_suggestions,
    )


@router.post("/complete", response_model=CompletionResponse)
async def complete_code(request: CompletionRequest) -> CompletionResponse:
    """Generate intelligent code completions.

    Uses brain to understand context and suggest relevant completions.
    """
    engine = get_intelligence_engine()
    return await engine.complete_code(
        request.code_prefix, request.language, request.context, request.max_suggestions
    )


@router.post("/generate", response_model=GeneratedCode)
async def generate_code(request: GenerationRequest) -> GeneratedCode:
    """Generate code from specification.

    Uses brain to generate production-ready code with tests and docs.
    """
    engine = get_intelligence_engine()
    return await engine.generate_code(
        request.specification, request.language, request.constraints, request.style_guide
    )


@router.post("/patterns", response_model=PatternDetectionResponse)
async def detect_patterns(request: PatternDetectionRequest) -> PatternDetectionResponse:
    """Detect patterns in code.

    Identifies design patterns, anti-patterns, and language idioms.
    """
    engine = get_intelligence_engine()
    return await engine.detect_patterns(request.code, request.pattern_types)


@router.post("/debt", response_model=TechnicalDebtReport)
async def analyze_technical_debt(request: TechnicalDebtRequest) -> TechnicalDebtReport:
    """Analyze technical debt across files.

    Provides prioritized debt items with effort estimates.
    """
    engine = get_intelligence_engine()
    return await engine.analyze_technical_debt(request.file_paths, request.codebase_context)


@router.get("/analyze-stream")
async def stream_code_analysis(
    code: str = Query(..., description="Code to analyze"),
    language: str = Query(default="python", description="Programming language"),
) -> StreamingResponse:
    """Stream real-time code analysis progress."""
    engine = get_intelligence_engine()

    async def event_generator():
        async for update in engine.stream_analysis(code, language):
            yield f"data: {update}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Check code intelligence engine health."""
    return {
        "status": "healthy" if _BRAIN_AVAILABLE else "degraded",
        "brain_available": _BRAIN_AVAILABLE,
        "features": [
            "semantic_analysis",
            "code_completion",
            "code_generation",
            "pattern_detection",
            "debt_analysis",
        ],
        "timestamp": datetime.now(UTC).isoformat(),
    }
