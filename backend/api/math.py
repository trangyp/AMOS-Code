"""
AMOS Math Framework API

REST API endpoints for mathematical framework operations.
Equation queries, validation, and framework status.

Creator: Trang Phan
Version: 3.0.0
"""

from fastapi import APIRouter, HTTPException

from .schemas import (
    EquationInfo,
    EquationValidationRequest,
    EquationValidationResponse,
    MathFrameworkStatus,
    MathQueryRequest,
    MathQueryResponse,
)

router = APIRouter()

# Lazy initialization of SuperBrainRuntime
_brain_runtime = None


def _get_brain():
    """Get or initialize SuperBrainRuntime."""
    global _brain_runtime
    if _brain_runtime is None:
        try:
            from amos_brain import SuperBrainRuntime

            _brain_runtime = SuperBrainRuntime()
            if not hasattr(_brain_runtime, "_initialized"):
                _brain_runtime.initialize()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Brain runtime not available: {e}")
    return _brain_runtime


@router.get("/status", response_model=MathFrameworkStatus)
async def get_math_framework_status():
    """Get mathematical framework status."""
    try:
        brain = _get_brain()

        # Check if math engine is available
        if not hasattr(brain, "_math_engine") or brain._math_engine is None:
            return MathFrameworkStatus(
                available=False, initialized=False, total_equations=0, domains=[], version="1.0.0"
            )

        # Get stats from brain
        stats = await brain.get_math_framework_stats()

        return MathFrameworkStatus(
            available=stats.get("available", False),
            initialized=stats.get("initialized", False),
            total_equations=stats.get("total_equations", 0),
            domains=stats.get("domains", []),
            version=stats.get("version", "1.0.0"),
        )
    except HTTPException:
        raise
    except Exception:
        return MathFrameworkStatus(
            available=False, initialized=False, total_equations=0, domains=[], version="1.0.0"
        )


@router.post("/query", response_model=MathQueryResponse)
async def query_equations(request: MathQueryRequest):
    """Query equations by domain or text search."""
    try:
        brain = _get_brain()

        # Query through brain runtime
        results = await brain.query_math_framework(query=request.query, domain=request.domain)

        # Convert to API schema
        equations = []
        for eq in results[: request.limit]:
            equations.append(
                EquationInfo(
                    name=eq.get("name", "Unknown"),
                    latex=eq.get("latex", ""),
                    description=eq.get("description", ""),
                    domain=eq.get("domain", "general"),
                    variables=eq.get("variables", []),
                )
            )

        return MathQueryResponse(equations=equations, total=len(results), domain=request.domain)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")


@router.post("/validate", response_model=EquationValidationResponse)
async def validate_equation(request: EquationValidationRequest):
    """Validate an equation."""
    try:
        brain = _get_brain()

        valid, message = await brain.validate_equation(
            equation=request.equation, domain=request.domain
        )

        return EquationValidationResponse(valid=valid, message=message, suggestions=[])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {e}")


@router.get("/domains")
async def get_domains():
    """Get list of available equation domains."""
    try:
        brain = _get_brain()

        if not hasattr(brain, "_math_engine") or brain._math_engine is None:
            return {"domains": []}

        # Get available domains from engine
        domains = []
        if hasattr(brain._math_engine, "equations_by_domain"):
            domains = list(brain._math_engine.equations_by_domain.keys())

        return {"domains": domains}
    except HTTPException:
        raise
    except Exception as e:
        return {"domains": [], "error": str(e)}
