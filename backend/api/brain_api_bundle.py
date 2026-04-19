"""Brain API Bundle - Complete brain API router for main app.

Mounts all brain-powered endpoints in one import.
Usage:
    from backend.api.brain_api_bundle import get_brain_router
    app.include_router(get_brain_router())
"""

from fastapi import APIRouter

from .brain_active_processor import router as active_processor_router
from .brain_analytics_engine import router as analytics_router
from .brain_code_intelligence import router as code_intelligence_router
from .brain_cognitive_query import router as cognitive_router
from .brain_dashboard_api import router as dashboard_router
from .brain_decision_support import router as decision_router
from .brain_kernel_direct import router as kernel_router
from .brain_knowledge_graph import router as knowledge_router
from .brain_learning_system import router as learning_router
from .brain_memory_api import router as memory_router
from .brain_multi_agent import router as multi_agent_router
from .brain_pattern_recognition import router as pattern_router
from .brain_powered_endpoints import router as powered_router
from .brain_prediction_engine import router as prediction_router
from .brain_realtime_monitor import router as monitor_router
from .brain_reasoning_engine import router as reasoning_router
from .brain_self_healing import router as self_healing_router
from .brain_streaming import router as streaming_router
from .brain_task_automation import router as automation_router
from .brain_workflow_orchestrator import router as workflow_orchestrator_router
from .enhanced_task_processor import router as task_router


def get_brain_router() -> APIRouter:
    """Get combined brain API router."""
    # Create main brain router
    brain_router = APIRouter(prefix="/api/v1/brain", tags=["Brain Bundle"])

    # Include all sub-routers
    brain_router.include_router(kernel_router, prefix="/kernel")
    brain_router.include_router(dashboard_router, prefix="/dashboard")
    brain_router.include_router(task_router, prefix="/tasks")
    brain_router.include_router(powered_router, prefix="/powered")
    brain_router.include_router(automation_router, prefix="/automation")
    brain_router.include_router(streaming_router, prefix="/stream")
    brain_router.include_router(cognitive_router, prefix="/cognitive")
    brain_router.include_router(memory_router, prefix="/memory")
    brain_router.include_router(decision_router, prefix="/decisions")
    brain_router.include_router(monitor_router, prefix="/monitor")
    brain_router.include_router(knowledge_router, prefix="/knowledge")
    brain_router.include_router(pattern_router, prefix="/patterns")
    brain_router.include_router(learning_router, prefix="/learning")
    brain_router.include_router(reasoning_router, prefix="/reasoning")
    brain_router.include_router(analytics_router, prefix="/analytics")
    brain_router.include_router(active_processor_router, prefix="/active")
    brain_router.include_router(code_intelligence_router, prefix="/code")
    brain_router.include_router(workflow_orchestrator_router, prefix="/workflow")
    brain_router.include_router(multi_agent_router, prefix="/agents")
    brain_router.include_router(prediction_router, prefix="/prediction")
    brain_router.include_router(self_healing_router, prefix="/healing")

    # Add bundle health endpoint
    @brain_router.get("/bundle-health")
    async def bundle_health() -> dict:
        """Check all brain API health."""
        return {
            "kernel": "mounted",
            "dashboard": "mounted",
            "tasks": "mounted",
            "powered": "mounted",
            "automation": "mounted",
            "streaming": "mounted",
            "cognitive": "mounted",
            "memory": "mounted",
            "decisions": "mounted",
            "monitor": "mounted",
            "knowledge": "mounted",
            "patterns": "mounted",
            "learning": "mounted",
            "reasoning": "mounted",
            "analytics": "mounted",
            "active": "mounted",
            "code": "mounted",
            "workflow": "mounted",
            "agents": "mounted",
            "prediction": "mounted",
            "healing": "mounted",
            "version": "28-phase",
        }

    return brain_router


# Export individual routers too for selective mounting
__all__ = [
    "get_brain_router",
    "kernel_router",
    "dashboard_router",
    "task_router",
    "powered_router",
    "automation_router",
    "streaming_router",
    "cognitive_router",
    "memory_router",
    "decision_router",
    "monitor_router",
    "knowledge_router",
    "pattern_router",
    "learning_router",
    "reasoning_router",
    "analytics_router",
    "active_processor_router",
    "code_intelligence_router",
    "workflow_orchestrator_router",
    "multi_agent_router",
    "prediction_router",
    "self_healing_router",
]
