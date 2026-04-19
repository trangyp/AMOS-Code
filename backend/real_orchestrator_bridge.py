"""Real Orchestrator Bridge - Connects backend API to AMOS orchestrators.

This replaces fake task execution with real cognitive orchestration
through the clawspring/amos_brain ecosystem.
"""

import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add clawspring to path
CLAWSPRING_PATH = Path(__file__).parent.parent / "clawspring"
if str(CLAWSPRING_PATH) not in sys.path:
    sys.path.insert(0, str(CLAWSPRING_PATH))

# Import real orchestrators
from amos_brain.master_orchestrator import MasterOrchestrator, get_orchestrator
from amos_brain.task_execution_integration import (
    TaskExecutionIntegration,
    get_task_execution_integration,
)
from amos_brain.organism_bridge import get_organism_bridge, OrganismBridge


@dataclass
class TaskResult:
    """Real task execution result."""

    task_id: str
    success: bool
    output: str
    error: Optional[str] = None
    duration_ms: float = 0.0
    execution_type: str = "unknown"
    domain: str = "unknown"
    engines_used: List[str] = field(default_factory=list)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    organism_enhancements: Dict[str, Any] = field(default_factory=dict)


class RealOrchestratorBridge:
    """
    Bridge connecting FastAPI backend to real AMOS orchestrators.

    Replaces fake task execution with:
    - MasterOrchestrator cognitive routing
    - Organism task execution
    - Real engine invocation
    - Actual domain analysis
    """

    _instance: Optional["RealOrchestratorBridge"] = None

    def __new__(cls) -> "RealOrchestratorBridge":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._orchestrator: Optional[MasterOrchestrator] = None
        self._task_executor: Optional[TaskExecutionIntegration] = None
        self._organism_bridge: Optional[OrganismBridge] = None
        self._initialized = False
        self._execution_history: List[TaskResult] = []

    async def initialize(self) -> bool:
        """Initialize all real orchestrator connections."""
        if self._initialized:
            return True

        print("[RealOrchestratorBridge] Initializing real orchestrators...")

        # Initialize master orchestrator
        try:
            self._orchestrator = get_orchestrator()
            if not self._orchestrator._initialized:
                self._orchestrator.initialize()
            print("  MasterOrchestrator: READY")
        except Exception as e:
            print(f"  MasterOrchestrator: FAILED - {e}")
            self._orchestrator = None

        # Initialize task execution integration
        try:
            self._task_executor = get_task_execution_integration()
            print("  TaskExecutionIntegration: READY")
        except Exception as e:
            print(f"  TaskExecutionIntegration: FAILED - {e}")
            self._task_executor = None

        # Initialize organism bridge
        try:
            self._organism_bridge = get_organism_bridge()
            print("  OrganismBridge: READY")
        except Exception as e:
            print(f"  OrganismBridge: FAILED - {e}")
            self._organism_bridge = None

        self._initialized = True

        # Report status
        ready_count = sum(
            [
                self._orchestrator is not None,
                self._task_executor is not None,
                self._organism_bridge is not None,
            ]
        )
        print(f"[RealOrchestratorBridge] {ready_count}/3 orchestrators ready")

        return ready_count > 0

    async def execute_task(
        self,
        task_description: str,
        priority: str = "MEDIUM",
        context: Optional[dict[str, Any]] = None,
    ) -> TaskResult:
        """Execute a task through real orchestrators."""
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        start_time = time.time()

        if not self._initialized:
            await self.initialize()

        # Use orchestrator if available
        if self._orchestrator:
            try:
                result = self._orchestrator.orchestrate_cognitive_task(
                    task_id=task_id,
                    task_description=task_description,
                    priority=priority,
                )

                duration_ms = (time.time() - start_time) * 1000

                exec_type = "unknown"
                if result.execution:
                    exec_type = result.execution.get("execution_type", "unknown")
                task_result = TaskResult(
                    task_id=task_id,
                    success=result.overall_success,
                    output=result.execution.get("output", "") if result.execution else "",
                    error=(None if result.overall_success else "Execution failed"),
                    duration_ms=duration_ms,
                    execution_type=exec_type,
                    domain=result.domain,
                    engines_used=result.analysis.get("recommended_engines", []),
                    organism_enhancements=result.organism_enhancements,
                )

                self._execution_history.append(task_result)
                return task_result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                task_result = TaskResult(
                    task_id=task_id,
                    success=False,
                    output="",
                    error=str(e),
                    duration_ms=duration_ms,
                    domain="error",
                )
                self._execution_history.append(task_result)
                return task_result

        # Fallback to task executor
        if self._task_executor:
            try:
                domain = self._analyze_domain(task_description)
                engines = self._get_engines_for_domain(domain)

                execution = self._task_executor.execute_cognitive_task(
                    task_id=task_id,
                    task_description=task_description,
                    domain=domain,
                    engines=engines,
                    priority=priority,
                )

                duration_ms = (time.time() - start_time) * 1000

                task_result = TaskResult(
                    task_id=task_id,
                    success=execution.success,
                    output=execution.output,
                    error=execution.error,
                    duration_ms=duration_ms,
                    execution_type=execution.execution_type,
                    domain=domain,
                    engines_used=engines,
                    artifacts=execution.artifacts,
                )

                self._execution_history.append(task_result)
                return task_result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                return TaskResult(
                    task_id=task_id,
                    success=False,
                    output="",
                    error=str(e),
                    duration_ms=duration_ms,
                )

        # No orchestrators available
        duration_ms = (time.time() - start_time) * 1000
        return TaskResult(
            task_id=task_id,
            success=False,
            output="",
            error="No orchestrators available",
            duration_ms=duration_ms,
        )

    def _analyze_domain(self, task_description: str) -> str:
        """Analyze task domain using keyword matching."""
        task_lower = task_description.lower()

        domains = {
            "security": ["security", "vulnerability", "threat", "attack", "scan"],
            "software": ["code", "function", "api", "class", "module", "refactor"],
            "analysis": ["analyze", "evaluate", "assess", "review", "examine"],
            "design": ["design", "architecture", "structure", "pattern"],
            "infrastructure": ["deploy", "server", "cloud", "infrastructure", "docker"],
            "data": ["data", "database", "query", "dataset", "migration"],
            "testing": ["test", "testing", "coverage", "unit test", "integration test"],
        }

        for domain, keywords in domains.items():
            if any(kw in task_lower for kw in keywords):
                return domain

        return "analysis"

    def _get_engines_for_domain(self, domain: str) -> List[str]:
        """Get recommended engines for domain."""
        engine_map = {
            "security": ["AMOS_Deterministic_Logic_And_Law_Engine"],
            "software": ["AMOS_Engineering_And_Mathematics_Engine"],
            "analysis": ["AMOS_Deterministic_Logic_And_Law_Engine"],
            "design": ["AMOS_Design_Language_Engine"],
            "infrastructure": ["AMOS_Engineering_And_Mathematics_Engine"],
            "data": ["AMOS_Engineering_And_Mathematics_Engine"],
            "testing": ["AMOS_Deterministic_Logic_And_Law_Engine"],
        }
        default = ["AMOS_Deterministic_Logic_And_Law_Engine"]
        return engine_map.get(domain, default)

    def get_status(self) -> Dict[str, Any]:
        """Get bridge and orchestrator status."""
        orchestrator_status = {}
        if self._orchestrator:
            try:
                orchestrator_status = self._orchestrator.get_ecosystem_status()
            except Exception as e:
                orchestrator_status = {"error": str(e)}

        return {
            "initialized": self._initialized,
            "orchestrator_ready": self._orchestrator is not None,
            "task_executor_ready": self._task_executor is not None,
            "organism_bridge_ready": self._organism_bridge is not None,
            "execution_history_count": len(self._execution_history),
            "orchestrator_status": orchestrator_status,
        }

    def get_execution_history(self, limit: int = 100) -> List[TaskResult]:
        """Get recent execution history."""
        return self._execution_history[-limit:]


# Global bridge instance
_real_orchestrator_bridge: Optional[RealOrchestratorBridge] = None


def get_real_orchestrator_bridge() -> RealOrchestratorBridge:
    """Get or create the real orchestrator bridge."""
    global _real_orchestrator_bridge
    if _real_orchestrator_bridge is None:
        _real_orchestrator_bridge = RealOrchestratorBridge()
    return _real_orchestrator_bridge
