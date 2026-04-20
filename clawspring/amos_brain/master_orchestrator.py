"""AMOS Master Orchestrator - Unified command layer for all ecosystem components."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

# Import all ecosystem components
from .organism_bridge import get_organism_bridge
from .predictive_integration import get_predictive_integration, predict_task
from .task_execution_integration import execute_task, get_task_execution_integration


@dataclass
class OrchestrationResult:
    """Result of orchestrated cognitive workflow."""

    task_id: str
    timestamp: str
    domain: str
    analysis: dict[str, Any]
    prediction: dict[str, Any]
    execution: dict[str, Any]
    organism_enhancements: dict[str, Any]
    overall_success: bool
    total_duration_ms: float
    mathematical_analysis: dict[str, Any | None] = None


class MasterOrchestrator:
    """Master orchestration layer for AMOS ecosystem.
    Coordinates cognitive routing, prediction, and execution.
    """

    def __init__(self):
        self._organism_bridge = None
        self._predictive = None
        self._task_executor = None
        self._math_engine = None
        self._orchestration_history: list[OrchestrationResult] = []
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize all ecosystem connections."""
        try:
            self._organism_bridge = get_organism_bridge()
            self._predictive = get_predictive_integration()
            self._task_executor = get_task_execution_integration()
            # Initialize mathematical framework engine
            try:
                from .mathematical_framework_engine import get_framework_engine

                self._math_engine = get_framework_engine()
            except Exception:
                self._math_engine = None
            self._initialized = True
            return True
        except Exception as e:
            print(f"[MasterOrchestrator] Initialization failed: {e}")
            return False

    def orchestrate_cognitive_task(
        self, task_id: str, task_description: str, priority: str = "MEDIUM"
    ) -> OrchestrationResult:
        """Execute full cognitive workflow with organism enhancement.

        Workflow:
        1. Cognitive domain analysis
        2. Organism coherence check
        3. Predictive outcome forecasting
        4. Task execution
        5. Result synthesis
        """
        import time

        start_time = time.time()

        if not self._initialized:
            self.initialize()

        # Step 1: Cognitive Analysis (via router)
        domain = self._analyze_domain(task_description)

        # Step 2: Organism Enhancement
        organism_enhancements = {}
        if self._organism_bridge:
            try:
                enhancement = self._organism_bridge.enhance_cognitive_analysis(task_description)
                organism_enhancements = enhancement.get("organism_enhancements", {})
            except Exception:
                pass

        # Step 3: Predictive Analysis
        prediction_result = None
        if self._predictive:
            try:
                prediction_result = predict_task(task_description, domain, priority)
            except Exception:
                pass

        # Step 3b: Mathematical Framework Analysis
        math_analysis = None
        if self._math_engine:
            try:
                math_analysis = self._math_engine.analyze_architecture(task_description)
            except Exception:
                pass

        # Step 4: Task Execution
        execution_result = None
        engines = self._get_recommended_engines(domain)
        if self._task_executor:
            try:
                execution_result = execute_task(
                    task_id, task_description, domain, engines, priority
                )
            except Exception:
                pass

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Create result
        result = OrchestrationResult(
            task_id=task_id,
            timestamp=datetime.now().isoformat(),
            domain=domain,
            analysis={
                "detected_domain": domain,
                "recommended_engines": engines,
                "mathematical_domains": (
                    math_analysis.get("detected_domains", []) if math_analysis else []
                ),
                "recommended_frameworks": (
                    math_analysis.get("recommended_frameworks", []) if math_analysis else []
                ),
            },
            prediction={
                "predicted_duration_ms": (
                    prediction_result.predicted_duration_ms if prediction_result else 0
                ),
                "confidence": (prediction_result.confidence if prediction_result else 0),
                "risk_factors": (prediction_result.risk_factors if prediction_result else []),
            }
            if prediction_result
            else {},
            execution={
                "success": execution_result.success if execution_result else False,
                "duration_ms": (execution_result.duration_ms if execution_result else 0),
                "execution_type": (
                    execution_result.execution_type if execution_result else "unknown"
                ),
            }
            if execution_result
            else {},
            organism_enhancements=organism_enhancements,
            overall_success=(execution_result.success if execution_result else False),
            total_duration_ms=duration_ms,
            mathematical_analysis=math_analysis,
        )

        self._orchestration_history.append(result)
        return result

    def _analyze_domain(self, task_description: str) -> str:
        """Analyze task domain (simplified without router import)."""
        task_lower = task_description.lower()

        # Domain detection patterns
        domains = {
            "security": ["security", "vulnerability", "threat", "attack"],
            "software": ["code", "function", "api", "class", "module"],
            "analysis": ["analyze", "evaluate", "assess", "review"],
            "design": ["design", "architecture", "structure", "layout"],
            "infrastructure": ["deploy", "server", "cloud", "infrastructure"],
            "data": ["data", "database", "query", "dataset"],
        }

        for domain, keywords in domains.items():
            if any(kw in task_lower for kw in keywords):
                return domain

        return "analysis"

    def _get_recommended_engines(self, domain: str) -> list[str]:
        """Get recommended engines for domain."""
        engine_map = {
            "security": ["AMOS_Deterministic_Logic_And_Law_Engine"],
            "software": ["AMOS_Engineering_And_Mathematics_Engine"],
            "analysis": ["AMOS_Deterministic_Logic_And_Law_Engine"],
            "design": ["AMOS_Design_Language_Engine"],
            "infrastructure": ["AMOS_Engineering_And_Mathematics_Engine"],
            "data": ["AMOS_Engineering_And_Mathematics_Engine"],
        }
        return engine_map.get(domain, ["AMOS_Deterministic_Logic_And_Law_Engine"])

    def get_ecosystem_status(self) -> dict[str, Any]:
        """Get complete ecosystem status."""
        organism_status = self._organism_bridge.get_status() if self._organism_bridge else {}
        predictive_status = self._predictive.get_status() if self._predictive else {}
        executor_status = self._task_executor.get_status() if self._task_executor else {}

        return {
            "initialized": self._initialized,
            "cognitive_modules": 11,
            "organism_bridge": organism_status.get("total_connected", 0),
            "organism_total": organism_status.get("total_available", 3),
            "predictive_ready": predictive_status.get("initialized", False),
            "executor_ready": executor_status.get("initialized", False),
            "orchestrations_completed": len(self._orchestration_history),
            "ecosystem_health": "OPERATIONAL" if self._initialized else "DEGRADED",
        }

    def print_status(self):
        """Print ecosystem status."""
        status = self.get_ecosystem_status()

        print("=" * 70)
        print("AMOS MASTER ORCHESTRATOR - ECOSYSTEM STATUS")
        print("=" * 70)
        print(f"\n🧠 Cognitive Modules: {status['cognitive_modules']}")
        print(f"🔗 Organism Bridge: {status['organism_bridge']}/{status['organism_total']}")
        print(f"📊 Predictive: {'Ready' if status['predictive_ready'] else 'Not Ready'}")
        print(f"⚡ Executor: {'Ready' if status['executor_ready'] else 'Not Ready'}")
        print(f"📈 Orchestrations: {status['orchestrations_completed']}")
        print(f"\n🏥 Health: {status['ecosystem_health']}")
        print("=" * 70)


# Singleton instance
_master_orchestrator: MasterOrchestrator | None = None


def get_master_orchestrator() -> MasterOrchestrator:
    """Get or create singleton master orchestrator."""
    global _master_orchestrator
    if _master_orchestrator is None:
        _master_orchestrator = MasterOrchestrator()
        _master_orchestrator.initialize()
    return _master_orchestrator


def orchestrate_task(
    task_id: str, task_description: str, priority: str = "MEDIUM"
) -> OrchestrationResult:
    """Convenience function for task orchestration."""
    orchestrator = get_master_orchestrator()
    return orchestrator.orchestrate_cognitive_task(task_id, task_description, priority)


if __name__ == "__main__":
    print("=" * 70)
    print("AMOS MASTER ORCHESTRATOR v1.3")
    print("Full Ecosystem Integration")
    print("=" * 70)

    orchestrator = get_master_orchestrator()
    orchestrator.print_status()

    # Test orchestration
    print("\n🧪 Testing Orchestration:")
    test_tasks = [
        ("orch_001", "Design secure API endpoint", "HIGH"),
        ("orch_002", "Analyze code complexity", "MEDIUM"),
    ]

    for tid, desc, priority in test_tasks:
        result = orchestrate_task(tid, desc, priority)
        status_icon = "✓" if result.overall_success else "✗"
        print(f"  {status_icon} {tid}: {result.domain} ({result.total_duration_ms:.1f}ms)")


# Global orchestrator instance
_orchestrator: MasterOrchestrator | None = None


def get_orchestrator() -> MasterOrchestrator:
    """Get or create the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MasterOrchestrator()
    return _orchestrator
