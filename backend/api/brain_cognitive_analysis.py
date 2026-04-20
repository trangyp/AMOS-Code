"""Brain Cognitive Analysis API - Real brain-powered code analysis.

Uses amos_brain_working.think() for cognitive processing of:
- Code quality assessment
- Architecture decisions
- Security vulnerability analysis
- Performance optimization suggestions
"""

from pathlib import Path
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

# Add brain path
_AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
from amos_brain_working import think as brain_think

router = APIRouter(prefix="/brain-cognitive", tags=["brain-cognitive"])


class CodeAnalysisRequest(BaseModel):
    """Request for brain-powered code analysis."""

    code: str
    language: str = "python"
    context: dict[str, Any] = {}


class CognitiveAnalysisResponse(BaseModel):
    """Brain cognitive analysis result."""

    status: str
    confidence: float
    legality: float
    mode: str
    analysis: str
    recommendations: list[str]
    risk_level: str


class ArchitectureDecisionRequest(BaseModel):
    """Request for architecture decision support."""

    decision: str
    options: list[str]
    constraints: dict[str, Any] = {}


class SecurityScanRequest(BaseModel):
    """Request for security vulnerability scan."""

    code: str
    file_path: str = ""
    language: str = "python"


@router.post("/analyze-code", response_model=CognitiveAnalysisResponse)
async def analyze_code(request: CodeAnalysisRequest) -> CognitiveAnalysisResponse:
    """Analyze code quality using AMOS brain cognitive engine."""
    # REAL BRAIN USAGE - NOT MOCK
    brain_input = f"""Analyze this {request.language} code for quality, patterns, and issues:

```{request.language}
{request.code[:2000]}  # Limit to prevent overflow
```

Provide analysis of:
1. Code quality and readability
2. Design patterns used
3. Potential bugs or issues
4. Performance considerations
5. Security concerns
"""

    result = brain_think(brain_input, {"domain": "code_review", **request.context})

    # Extract analysis from brain response
    raw_response = str(result)

    # Parse recommendations from brain output
    recommendations = []
    if "recommend" in raw_response.lower() or "suggest" in raw_response.lower():
        lines = raw_response.split("\n")
        for line in lines:
            if line.strip().startswith(("-", "*", "1.", "2.", "3.")):
                recommendations.append(line.strip())

    if not recommendations:
        recommendations = [
            "Brain analysis complete - review detailed output",
            f"Sigma confidence: {result.get('sigma', 0):.2f}",
            f"Legality score: {result.get('legality', 0):.2f}",
        ]

    # Determine risk level based on legality score
    legality = result.get("legality", 0)
    if legality >= 8:
        risk_level = "low"
    elif legality >= 4:
        risk_level = "medium"
    else:
        risk_level = "high"

    return CognitiveAnalysisResponse(
        status=result.get("status", "UNKNOWN"),
        confidence=result.get("sigma", 0),
        legality=legality,
        mode=result.get("mode", "unknown"),
        analysis=raw_response[:500],
        recommendations=recommendations[:5],
        risk_level=risk_level,
    )


@router.post("/architecture-decision")
async def architecture_decision(request: ArchitectureDecisionRequest) -> dict[str, Any]:
    """Get brain-powered architecture decision support."""
    # REAL BRAIN USAGE
    options_text = "\n".join([f"{i + 1}. {opt}" for i, opt in enumerate(request.options)])

    brain_input = f"""Architecture Decision Required:

Decision: {request.decision}

Options:
{options_text}

Constraints: {request.constraints}

Analyze each option considering:
1. Technical feasibility
2. Long-term maintainability
3. Scalability
4. Risk factors
5. Alignment with AMOS principles

Recommend the best option with justification."""

    result = brain_think(brain_input, {"domain": "architecture"})

    return {
        "decision": request.decision,
        "brain_status": result.get("status"),
        "brain_confidence": result.get("sigma"),
        "brain_legality": result.get("legality"),
        "recommendation": str(result)[:1000],
        "options_analyzed": len(request.options),
    }


@router.post("/security-scan")
async def security_scan(request: SecurityScanRequest) -> dict[str, Any]:
    """Scan code for security vulnerabilities using brain."""
    # REAL BRAIN USAGE
    brain_input = f"""Security vulnerability scan for {request.language} code:

File: {request.file_path or "unknown"}

Code:
```{request.language}
{request.code[:1500]}
```

Identify:
1. Security vulnerabilities
2. Injection risks
3. Authentication/authorization issues
4. Data exposure risks
5. Input validation gaps
6. Cryptographic weaknesses

Rate severity: Critical, High, Medium, Low"""

    result = brain_think(brain_input, {"domain": "security"})

    # Determine severity based on brain legality score
    legality = result.get("legality", 0)
    if legality < 2:
        severity = "critical"
    elif legality < 4:
        severity = "high"
    elif legality < 7:
        severity = "medium"
    else:
        severity = "low"

    return {
        "file_path": request.file_path or "anonymous",
        "language": request.language,
        "brain_status": result.get("status"),
        "brain_confidence": result.get("sigma"),
        "brain_legality": legality,
        "severity_level": severity,
        "findings": str(result)[:800],
        "scan_complete": True,
    }


@router.get("/brain-health")
async def brain_health() -> dict[str, Any]:
    """Check brain cognitive engine health."""
    # REAL BRAIN USAGE - Health check
    result = brain_think("Brain health check diagnostic", {"check": True})

    return {
        "operational": result.get("status") == "SUCCESS",
        "status": result.get("status"),
        "sigma": result.get("sigma"),
        "legality": result.get("legality"),
        "mode": result.get("mode"),
        "brain_used": True,
        "timestamp": "active",
    }
