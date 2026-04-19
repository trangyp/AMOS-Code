
from typing import Optional, Any

"""Backend Brain Integration - Real AMOS brain integration for FastAPI backend.

Provides:
- Brain-powered cognitive endpoints
- Real-time brain status monitoring
- Cognitive task processing
- Integration with existing backend infrastructure
"""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

# Setup paths
AMOS_ROOT = Path(__file__).parent.parent.resolve()
for p in [AMOS_ROOT, AMOS_ROOT / "clawspring", AMOS_ROOT / "clawspring" / "amos_brain"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Lazy imports
_brain_available: Optional[bool] = None
_kernel_class: Any = None
_dashboard_class: Any = None


def _ensure_brain() -> bool:
    """Ensure brain is available, return status."""
    global _brain_available, _kernel_class, _dashboard_class
    if _brain_available is not None:
        return _brain_available

    try:
        from amos_kernel_runtime import AMOSKernelRuntime  # noqa: E402

        from amos_brain.dashboard import BrainDashboard
from typing import Any
from typing import Dict

        _kernel_class = AMOSKernelRuntime
        _dashboard_class = BrainDashboard
        _brain_available = True
        return True
    except ImportError:
        _brain_available = False
        return False


class BrainIntegration:
    """Real brain integration for backend use."""

    def __init__(self):
        self._kernel: Any = None
        self._dashboard: Any = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize brain components."""
        if self._initialized:
            return True

        if not _ensure_brain():
            return False

        try:
            self._kernel = _kernel_class()
            self._dashboard = _dashboard_class()
            self._initialized = True
            return True
        except Exception:
            return False

    async def cognitive_cycle(
        self, observation: Dict[str, Any], goal: Dict[str, Any], timeout_ms: int = 5000
    ) -> Dict[str, Any]:
        """Execute cognitive cycle with real brain kernel."""
        if not self._initialized:
            await self.initialize()

        if not self._kernel:
            return {"error": "Brain kernel not available", "status": "failed"}

        try:
            result = await asyncio.wait_for(
                self._kernel.execute_cycle(observation, goal), timeout=timeout_ms / 1000.0
            )
            return result
        except TimeoutError:
            return {"error": "Timeout", "status": "timeout"}
        except Exception as e:
            return {"error": str(e), "status": "error"}

    async def get_dashboard_data(self, days: int = 7) -> Dict[str, Any]:
        """Get dashboard analytics data."""
        if not self._initialized:
            await self.initialize()

        if not self._dashboard:
            return {"error": "Dashboard not available"}

        try:
            return self._dashboard.generate_report(days=days, include_charts=False)
        except Exception as e:
            return {"error": str(e)}

    def get_health(self) -> Dict[str, Any]:
        """Get brain health status."""
        available = _ensure_brain()
        return {
            "available": available,
            "initialized": self._initialized,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global instance
_brain_integration: Optional[BrainIntegration] = None


def get_brain_integration() -> BrainIntegration:
    """Get or create global brain integration instance."""
    global _brain_integration
    if _brain_integration is None:
        _brain_integration = BrainIntegration()
    return _brain_integration


async def brain_cognitive_cycle(
    observation: Dict[str, Any], goal: Dict[str, Any], timeout_ms: int = 5000
) -> Dict[str, Any]:
    """Convenience function to run cognitive cycle."""
    brain = get_brain_integration()
    return await brain.cognitive_cycle(observation, goal, timeout_ms)


async def get_brain_dashboard(days: int = 7) -> Dict[str, Any]:
    """Convenience function to get dashboard data."""
    brain = get_brain_integration()
    return await brain.get_dashboard_data(days)
