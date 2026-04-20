"""Facade Bridge - Integrates kernel with BrainClient facade"""

from dataclasses import dataclass
from typing import Any, Optional

from ..core.law import UniversalLawKernel
from ..persistence import get_store
from ..workflows import get_workflow_engine


@dataclass
class KernelBrainResponse:
    """Kernel-native response matching BrainClient interface."""

    success: bool
    content: str
    reasoning: list[str]
    confidence: str
    law_compliant: bool
    violations: list[str]
    metadata: dict[str, Any]
    domain: str = "general"
    kernel_workflow_id: str = ""
    collapse_risk: float = 0.0
    drift_detected: bool = False


class KernelFacadeClient:
    """Drop-in replacement for BrainClient using kernel-first architecture."""

    def __init__(self, repo_path: Optional[str] = None):
        self.workflow = get_workflow_engine()
        self.law = UniversalLawKernel()
        self.store = get_store()
        self._repo_path = repo_path

    def think(self, query: str, domain: str = "general") -> KernelBrainResponse:
        """Think through kernel workflow (replaces BrainClient.think)."""
        workflow_id = f"think-{hash(query) & 0xFFFFFFFF}"

        # Execute through kernel
        result = self.workflow.execute(
            workflow_id=workflow_id,
            raw_input={
                "biological": {"query_complexity": len(query) / 1000},
                "cognitive": {"reasoning_depth": 0.8},
                "system": {"query": query, "domain": domain},
                "environment": {"context": "thinking"},
            },
            validate_laws=True,
        )

        # Persist result
        self.store.save_workflow(result)

        # Build response
        law_passed = result.law_validation.passed if result.law_validation else False

        return KernelBrainResponse(
            success=result.success,
            content=f"Kernel processed: {query[:50]}..."
            if len(query) > 50
            else f"Kernel processed: {query}",
            reasoning=[f"Step {s.name}: {s.status}" for s in result.steps],
            confidence="high" if result.success else "low",
            law_compliant=law_passed,
            violations=["drift detected"] if result.drift_detected else [],
            metadata={
                "workflow_id": result.workflow_id,
                "steps": len(result.steps),
                "repairs": result.repairs_proposed,
            },
            domain=domain,
            kernel_workflow_id=result.workflow_id,
            collapse_risk=result.law_validation.collapse_risk if result.law_validation else 1.0,
            drift_detected=result.drift_detected,
        )

    def decide(
        self,
        question: str,
        options: list[str],
        context: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Make decision through kernel (replaces BrainClient.decide)."""
        workflow_id = f"decide-{hash(question) & 0xFFFFFFFF}"

        result = self.workflow.execute(
            workflow_id=workflow_id,
            raw_input={
                "biological": {"options_count": len(options)},
                "cognitive": {"decision_complexity": len(question) / 100},
                "system": {
                    "question": question,
                    "options": options,
                    "context": context or {},
                },
                "environment": {"decision": True},
            },
            validate_laws=True,
        )

        self.store.save_workflow(result)

        # Select option based on kernel result
        selected_idx = 0 if result.success else -1
        if result.success and options:
            # Use collapse risk to weight decision
            risk = result.law_validation.collapse_risk if result.law_validation else 0.5
            selected_idx = int((1 - risk) * (len(options) - 1))

        return {
            "approved": result.success,
            "decision_id": result.workflow_id,
            "selected_option": options[selected_idx] if 0 <= selected_idx < len(options) else None,
            "reasoning": f"Kernel validation: {'passed' if result.success else 'failed'}",
            "risk_level": "low" if result.success else "high",
            "law_violations": ["drift"] if result.drift_detected else [],
            "alternative_actions": options[:2] if len(options) > 1 else [],
            "kernel_result": {
                "steps": len(result.steps),
                "collapse_risk": result.law_validation.collapse_risk
                if result.law_validation
                else 1.0,
            },
        }

    def validate_action(self, action: str) -> tuple[bool, list[str]]:
        """Validate action through kernel (replaces BrainClient.validate_action)."""
        result = self.law.validate_action(action)
        return result.compliant, result.violations

    def get_status(self) -> dict[str, Any]:
        """Get kernel client status."""
        stats = self.store.get_stats()
        return {
            "kernel_version": "7.0.0",
            "architecture": "kernel-first",
            "layers": 6,
            "workflows_executed": stats["total_workflows"],
            "successful_workflows": stats["successful_workflows"],
            "persistence_path": stats["db_path"],
            "healthy": stats["successful_workflows"] > stats["failed_workflows"]
            if stats["total_workflows"] > 0
            else True,
        }


def get_kernel_client(repo_path: Optional[str] = None) -> KernelFacadeClient:
    """Factory for kernel-based BrainClient replacement."""
    return KernelFacadeClient(repo_path)
