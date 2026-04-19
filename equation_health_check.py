#!/usr/bin/env python3
"""Health check endpoints for AMOS Equation API production deployment."""

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

sys.path.insert(0, str(Path(__file__).parent))

try:
    from fastapi import APIRouter, HTTPException

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

try:
    from unified_equation_api import UnifiedEquationAPI

    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

if FASTAPI_AVAILABLE:
    router = APIRouter(prefix="/health", tags=["health"])
else:
    router = None

_health_status: Dict[str, Any] = {
    "status": "healthy",
    "timestamp": datetime.now(UTC).isoformat(),
    "version": "2.0.0",
    "checks": {},
}

_start_time = time.time()


def _check_api_available() -> Tuple[bool, str]:
    """Check if equation API is available."""
    try:
        if API_AVAILABLE:
            api = UnifiedEquationAPI()
            return True, "API operational"
        return False, "API module not available"
    except Exception as e:
        return False, str(e)


def _check_memory_usage() -> Tuple[bool, str]:
    """Check system memory usage."""
    try:
        import psutil

        mem = psutil.virtual_memory()
        if mem.percent > 90:
            return False, f"Memory critical: {mem.percent}%"
        return True, f"Memory OK: {mem.percent}%"
    except ImportError:
        return True, "psutil not available"


def _check_disk_space() -> Tuple[bool, str]:
    """Check disk space."""
    try:
        import psutil

        disk = psutil.disk_usage("/")
        if disk.percent > 90:
            return False, f"Disk critical: {disk.percent}%"
        return True, f"Disk OK: {disk.percent}%"
    except ImportError:
        return True, "psutil not available"


if FASTAPI_AVAILABLE:

    @router.get("/")
    async def health_check() -> Dict[str, Any]:
        """Basic health check endpoint."""
        uptime = time.time() - _start_time
        return {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "uptime_seconds": uptime,
            "version": "2.0.0",
        }

    @router.get("/ready")
    async def readiness_check() -> Dict[str, Any]:
        """Readiness check for Kubernetes."""
        checks = {}
        overall = True

        api_ok, api_msg = _check_api_available()
        checks["api"] = {"status": "pass" if api_ok else "fail", "message": api_msg}
        overall = overall and api_ok

        status = "ready" if overall else "not_ready"
        return {"status": status, "timestamp": datetime.now(UTC).isoformat(), "checks": checks}

    @router.get("/live")
    async def liveness_check() -> Dict[str, Any]:
        """Liveness check for Kubernetes."""
        return {"status": "alive", "timestamp": datetime.now(UTC).isoformat()}

    @router.get("/detailed")
    async def detailed_health() -> Dict[str, Any]:
        """Detailed health check with all components."""
        checks = {}

        api_ok, api_msg = _check_api_available()
        checks["api"] = {"status": "pass" if api_ok else "fail", "message": api_msg}

        mem_ok, mem_msg = _check_memory_usage()
        checks["memory"] = {"status": "pass" if mem_ok else "fail", "message": mem_msg}

        disk_ok, disk_msg = _check_disk_space()
        checks["disk"] = {"status": "pass" if disk_ok else "fail", "message": disk_msg}

        all_pass = all(c["status"] == "pass" for c in checks.values())

        return {
            "status": "healthy" if all_pass else "degraded",
            "timestamp": datetime.now(UTC).isoformat(),
            "uptime_seconds": time.time() - _start_time,
            "checks": checks,
        }
