"""AMOS Mathematical Framework Dashboard Server.

Provides REST API endpoints for dashboard visualization of:
- Mathematical framework statistics
- Design validation results
- Audit logs and history
- Real-time metrics
"""

from datetime import datetime, timezone

UTC = timezone.utc
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Import math framework components
try:
    from .mathematical_framework_engine import get_framework_engine

    MATH_ENGINE_AVAILABLE = True
except ImportError:
    MATH_ENGINE_AVAILABLE = False

try:
    from .design_validation_engine import get_design_validation_engine

    VALIDATION_ENGINE_AVAILABLE = True
except ImportError:
    VALIDATION_ENGINE_AVAILABLE = False

try:
    from .math_audit_logger import get_math_audit_logger

    AUDIT_LOGGER_AVAILABLE = True
except ImportError:
    AUDIT_LOGGER_AVAILABLE = False

try:
    from .telemetry import get_telemetry

    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False


app = FastAPI(title="AMOS Math Framework Dashboard API", version="2.6.0")

# CORS for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/math/stats")
async def get_math_stats() -> dict[str, Any]:
    """Get mathematical framework engine statistics."""
    if not MATH_ENGINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Math engine not available")

    try:
        engine = get_framework_engine()
        return {
            "engine_stats": engine.get_stats(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "operational",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/math/domains")
async def get_math_domains() -> dict[str, Any]:
    """Get available mathematical domains and their equations."""
    if not MATH_ENGINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Math engine not available")

    try:
        engine = get_framework_engine()
        domains = {}
        for domain in ["UI_UX", "AI_ML", "SECURITY", "DISTRIBUTED_SYSTEMS"]:
            equations = engine.query_by_domain(domain)
            domains[domain] = {
                "equation_count": len(equations),
                "equations": [
                    {"name": eq.name, "formula": eq.formula[:100]}
                    for eq in equations[:5]  # First 5 only
                ],
            }

        return {"domains": domains, "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/math/analyze")
async def analyze_task(task: dict[str, str]) -> dict[str, Any]:
    """Analyze a task using mathematical framework."""
    if not MATH_ENGINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Math engine not available")

    task_description = task.get("task", "")
    if not task_description:
        raise HTTPException(status_code=400, detail="Task description required")

    try:
        engine = get_framework_engine()
        result = engine.analyze_architecture(task_description)

        # Log to audit
        if AUDIT_LOGGER_AVAILABLE:
            try:
                logger = get_math_audit_logger()
                logger.log_architecture_analysis(
                    task_description,
                    result.get("detected_domains", []),
                    result.get("recommended_frameworks", []),
                )
            except Exception:
                pass

        return {"analysis": result, "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/validation/history")
async def get_validation_history(limit: int = 10) -> dict[str, Any]:
    """Get recent validation results."""
    if not VALIDATION_ENGINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Validation engine not available")

    try:
        engine = get_design_validation_engine()
        history = engine.get_validation_history()

        # Convert to dict
        results = []
        for result in history[-limit:]:
            results.append(
                {
                    "is_valid": result.is_valid,
                    "score": result.score,
                    "violation_count": len(result.violations),
                    "passed_count": len(result.passed_checks),
                    "recommendation_count": len(result.recommendations),
                    "mathematical_analysis": result.mathematical_analysis,
                }
            )

        return {
            "validations": results,
            "total_count": len(history),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/validation/ui")
async def validate_ui(params: dict[str, Any]) -> dict[str, Any]:
    """Validate UI design parameters."""
    if not VALIDATION_ENGINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Validation engine not available")

    try:
        engine = get_design_validation_engine()

        spacing = params.get("spacing_values", [])
        typography = params.get("typography_sizes", [])
        colors = params.get("color_contrasts", [])

        result = engine.validate_ui_design(spacing, typography, colors)

        return {
            "validation": {
                "is_valid": result.is_valid,
                "score": result.score,
                "violations": [
                    {"rule": v.rule, "severity": v.severity, "message": v.message}
                    for v in result.violations
                ],
                "passed_checks": result.passed_checks,
                "recommendations": result.recommendations,
                "mathematical_analysis": result.mathematical_analysis,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/audit/recent")
async def get_recent_audit(limit: int = 20) -> dict[str, Any]:
    """Get recent audit entries."""
    if not AUDIT_LOGGER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Audit logger not available")

    try:
        logger = get_math_audit_logger()
        entries = logger.get_entries(limit=limit)

        return {
            "entries": [
                {
                    "timestamp": e.timestamp,
                    "action": e.action,
                    "domain": e.domain,
                    "result_summary": e.result_summary,
                    "task_hash": e.task_hash,
                }
                for e in entries
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/audit/statistics")
async def get_audit_statistics() -> dict[str, Any]:
    """Get audit statistics."""
    if not AUDIT_LOGGER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Audit logger not available")

    try:
        logger = get_math_audit_logger()
        stats = logger.get_statistics()

        return {"statistics": stats, "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/telemetry/dashboard")
async def get_telemetry_dashboard() -> dict[str, Any]:
    """Get telemetry dashboard data."""
    if not TELEMETRY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Telemetry not available")

    try:
        telemetry = get_telemetry()
        return telemetry.get_dashboard_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check() -> dict[str, Any]:
    """Health check for all math framework components."""
    components = {
        "mathematical_framework_engine": MATH_ENGINE_AVAILABLE,
        "design_validation_engine": VALIDATION_ENGINE_AVAILABLE,
        "math_audit_logger": AUDIT_LOGGER_AVAILABLE,
        "telemetry": TELEMETRY_AVAILABLE,
    }

    all_healthy = all(components.values())

    return {
        "status": "healthy" if all_healthy else "degraded",
        "components": components,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.6.0",
    }


@app.get("/api/dashboard/summary")
async def get_dashboard_summary() -> dict[str, Any]:
    """Get comprehensive dashboard summary."""
    summary = {"timestamp": datetime.now(timezone.utc).isoformat(), "status": "operational"}

    # Math engine stats
    if MATH_ENGINE_AVAILABLE:
        try:
            engine = get_framework_engine()
            summary["math_engine"] = engine.get_stats()
        except Exception:
            summary["math_engine"] = {"error": "Failed to get stats"}

    # Validation history
    if VALIDATION_ENGINE_AVAILABLE:
        try:
            engine = get_design_validation_engine()
            history = engine.get_validation_history()
            if history:
                avg_score = sum(r.score for r in history) / len(history)
                summary["validation"] = {
                    "total_validations": len(history),
                    "average_score": avg_score,
                    "last_validation_valid": history[-1].is_valid if history else None,
                }
        except Exception:
            summary["validation"] = {"error": "Failed to get validation data"}

    # Audit statistics
    if AUDIT_LOGGER_AVAILABLE:
        try:
            logger = get_math_audit_logger()
            summary["audit"] = logger.get_statistics()
        except Exception:
            summary["audit"] = {"error": "Failed to get audit stats"}

    # Telemetry metrics
    if TELEMETRY_AVAILABLE:
        try:
            telemetry = get_telemetry()
            summary["telemetry"] = telemetry.get_summary()
        except Exception:
            summary["telemetry"] = {"error": "Failed to get telemetry"}

    return summary


# Static file serving and root endpoint
BASE_DIR = Path(__file__).parent


@app.get("/")
async def serve_dashboard():
    """Serve the main dashboard HTML file."""
    dashboard_path = BASE_DIR / "math_dashboard.html"
    if dashboard_path.exists():
        return FileResponse(str(dashboard_path))
    return {"message": "AMOS Mathematical Framework Dashboard API", "docs": "/docs"}


# Mount static files if they exist
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8081)
