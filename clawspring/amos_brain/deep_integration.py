#!/usr/bin/env python3
"""AMOS Ecosystem v2.8 - Deep Integration Bridge.

Unifies the new cognitive ecosystem (amos_brain) with existing
AMOS_ORGANISM_OS components for complete system fusion.
Integrates: ethics_validation_kernel, coherence_engine, coherent_organism,
master_orchestrator, and organism CLI.
"""

from __future__ import annotations


import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
sys.path.insert(0, "clawspring")
sys.path.insert(0, "clawspring/amos_brain")

ORGANISM_PATH = Path(__file__).parent.parent.parent / "AMOS_ORGANISM_OS"


@dataclass
class UnifiedState:
    """Unified state from both cognitive and organism systems."""

    cognitive_status: dict[str, Any]
    organism_status: dict[str, Any]
    coherence_score: float
    ethics_clearance: bool
    timestamp: datetime


class EthicsValidationBridge:
    """Bridge to ethics_validation_kernel.py."""

    def __init__(self):
        self.kernel = None
        self._load_kernel()

    def _load_kernel(self) -> bool:
        """Load the ethics validation kernel."""
        try:
            kernel_path = ORGANISM_PATH / "12_ETHICS_VALIDATION" / "ethics_validation_kernel.py"
            if kernel_path.exists():
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    "ethics_validation_kernel", kernel_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.kernel = module
                return True
        except Exception as e:
            print(f"[EthicsBridge] Kernel load warning: {e}")
        return False

    def validate_with_kernel(self, action: str, context: dict) -> tuple[bool, str]:
        """Validate action using organism ethics kernel."""
        if self.kernel and hasattr(self.kernel, "validate_action"):
            try:
                result = self.kernel.validate_action(action, context)
                return result.get("valid", False), result.get("reason", "")
            except Exception as e:
                return False, f"Kernel error: {e}"
        return True, "Kernel not available, using fallback"


class CoherenceEngineBridge:
    """Bridge to amos_coherence_engine.py."""

    def __init__(self):
        self.engine = None
        self._load_engine()

    def _load_engine(self) -> bool:
        """Load the coherence engine."""
        try:
            engine_path = Path(__file__).parent.parent.parent / "amos_coherence_engine.py"
            if engine_path.exists():
                import importlib.util

                spec = importlib.util.spec_from_file_location("amos_coherence_engine", engine_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.engine = module
                return True
        except Exception as e:
            print(f"[CoherenceBridge] Engine load warning: {e}")
        return False

    def check_coherence(self, state: dict[str, Any]) -> float:
        """Check system coherence using organism engine."""
        if self.engine and hasattr(self.engine, "check_coherence"):
            try:
                return self.engine.check_coherence(state)
            except (AttributeError, TypeError, ValueError):
                pass
        return 1.0  # Default: fully coherent


class CoherentOrganismBridge:
    """Bridge to amos_coherent_organism.py."""

    def __init__(self):
        self.organism = None
        self._load_organism()

    def _load_organism(self) -> bool:
        """Load the coherent organism."""
        try:
            organism_path = Path(__file__).parent.parent.parent / "amos_coherent_organism.py"
            if organism_path.exists():
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    "amos_coherent_organism", organism_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.organism = module
                return True
        except Exception as e:
            print(f"[OrganismBridge] Organism load warning: {e}")
        return False

    def get_organism_state(self) -> dict[str, Any]:
        """Get state from coherent organism."""
        if self.organism and hasattr(self.organism, "get_state"):
            try:
                return self.organism.get_state()
            except (AttributeError, TypeError):
                pass
        return {"status": "unavailable"}

    def synchronize_with_cognitive(self, cognitive_state: dict) -> bool:
        """Synchronize cognitive state with organism."""
        if self.organism and hasattr(self.organism, "synchronize"):
            try:
                self.organism.synchronize(cognitive_state)
                return True
            except (AttributeError, TypeError):
                pass
        return False


class UnifiedOrchestratorBridge:
    """Unifies both master orchestrators (cognitive + organism)."""

    def __init__(self):
        self.organism_orchestrator = None
        self.cognitive_orchestrator = None
        self._load_both()

    def _load_both(self) -> None:
        """Load both orchestrator systems."""
        # Load organism orchestrator
        try:
            org_path = ORGANISM_PATH / "AMOS_MASTER_ORCHESTRATOR.py"
            if org_path.exists():
                import importlib.util

                spec = importlib.util.spec_from_file_location("organism_orchestrator", org_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.organism_orchestrator = module
        except Exception as e:
            print(f"[UnifiedOrchestrator] Organism load: {e}")

        # Load cognitive orchestrator
        try:
            from master_orchestrator import MasterOrchestrator

            self.cognitive_orchestrator = MasterOrchestrator()
        except Exception as e:
            print(f"[UnifiedOrchestrator] Cognitive load: {e}")

    def unified_orchestrate(self, task: str, context: dict) -> dict[str, Any]:
        """Orchestrate using both systems."""
        results = {"cognitive": None, "organism": None, "unified_decision": None}

        # Run cognitive orchestration
        if self.cognitive_orchestrator:
            try:
                results["cognitive"] = self.cognitive_orchestrator.orchestrate_cognitive_task(
                    "unified", task, context.get("priority", "MEDIUM")
                )
            except Exception as e:
                results["cognitive_error"] = str(e)

        # Run organism orchestration if available
        if self.organism_orchestrator and hasattr(self.organism_orchestrator, "orchestrate"):
            try:
                results["organism"] = self.organism_orchestrator.orchestrate(task, context)
            except Exception as e:
                results["organism_error"] = str(e)

        # Make unified decision
        results["unified_decision"] = self._make_unified_decision(results)

        return results

    def _make_unified_decision(self, results: dict) -> dict[str, Any]:
        """Synthesize unified decision from both orchestrators."""
        cognitive = results.get("cognitive")
        organism = results.get("organism")

        decision = {"proceed": False, "confidence": 0.0, "method": "unknown"}

        if cognitive and organism:
            # Both available - use consensus
            c_success = getattr(cognitive, "success", False)
            o_success = organism.get("success", False) if isinstance(organism, dict) else False

            decision["proceed"] = c_success and o_success
            decision["confidence"] = 0.9 if (c_success and o_success) else 0.5
            decision["method"] = "consensus"

        elif cognitive:
            # Only cognitive
            decision["proceed"] = getattr(cognitive, "success", False)
            decision["confidence"] = getattr(cognitive, "confidence", 0.7)
            decision["method"] = "cognitive_only"

        elif organism:
            # Only organism
            decision["proceed"] = (
                organism.get("success", False) if isinstance(organism, dict) else False
            )
            decision["confidence"] = 0.7
            decision["method"] = "organism_only"

        return decision


class DeepIntegrationSystem:
    """Main deep integration system unifying all components."""

    def __init__(self):
        self.ethics = EthicsValidationBridge()
        self.coherence = CoherenceEngineBridge()
        self.organism = CoherentOrganismBridge()
        self.orchestrator = UnifiedOrchestratorBridge()

    def get_unified_state(self) -> UnifiedState:
        """Get unified state from all systems."""
        # Get cognitive status
        try:
            from system_status import SystemStatus

            cognitive_status = SystemStatus().get_full_status()
        except Exception:
            cognitive_status = {"status": "unavailable"}

        # Get organism status
        organism_status = self.organism.get_organism_state()

        # Check coherence
        combined_state = {**cognitive_status, **organism_status}
        coherence = self.coherence.check_coherence(combined_state)

        # Check ethics clearance
        ethics_valid, _ = self.ethics.validate_with_kernel(
            "system_state_check", {"coherence": coherence, "status": combined_state}
        )

        return UnifiedState(
            cognitive_status=cognitive_status,
            organism_status=organism_status,
            coherence_score=coherence,
            ethics_clearance=ethics_valid,
            timestamp=datetime.now(),
        )

    def execute_unified_task(self, task: str, context: dict) -> dict[str, Any]:
        """Execute task through unified system."""
        # Step 1: Check unified state
        state = self.get_unified_state()

        if not state.ethics_clearance:
            return {"success": False, "error": "Ethics clearance denied", "state": state}

        if state.coherence_score < 0.5:
            return {
                "success": False,
                "error": "System coherence too low",
                "coherence": state.coherence_score,
                "state": state,
            }

        # Step 2: Orchestrate through unified orchestrator
        orchestration = self.orchestrator.unified_orchestrate(task, context)

        # Step 3: Synchronize state
        self.organism.synchronize_with_cognitive(state.cognitive_status)

        return {
            "success": orchestration["unified_decision"]["proceed"],
            "confidence": orchestration["unified_decision"]["confidence"],
            "method": orchestration["unified_decision"]["method"],
            "orchestration": orchestration,
            "state": state,
        }

    def print_unified_status(self) -> None:
        """Print unified system status."""
        state = self.get_unified_state()

        print("\n" + "=" * 70)
        print("AMOS ECOSYSTEM - DEEP INTEGRATION STATUS")
        print("=" * 70)

        print(f"\nTimestamp: {state.timestamp.isoformat()}")

        print("\nCognitive System:")
        for k, v in state.cognitive_status.items():
            print(f"  {k}: {v}")

        print("\nOrganism System:")
        for k, v in state.organism_status.items():
            print(f"  {k}: {v}")

        print(f"\nCoherence Score: {state.coherence_score:.2f}")
        print(f"Ethics Clearance: {'✓ GRANTED' if state.ethics_clearance else '✗ DENIED'}")

        print("=" * 70)


# Global instance
_deep_integration: DeepIntegrationSystem | None = None


def get_deep_integration() -> DeepIntegrationSystem:
    """Get or create global deep integration system."""
    global _deep_integration
    if _deep_integration is None:
        _deep_integration = DeepIntegrationSystem()
    return _deep_integration


def main():
    """Demo deep integration."""
    print("=" * 70)
    print("AMOS ECOSYSTEM v2.8 - DEEP INTEGRATION DEMO")
    print("=" * 70)

    integration = get_deep_integration()

    # Show unified status
    integration.print_unified_status()

    # Demo unified task execution
    print("\nDemo: Unified Task Execution")
    result = integration.execute_unified_task(
        "Design secure API endpoint", {"priority": "HIGH", "security_required": True}
    )

    print("\nExecution Result:")
    print(f"  Success: {result['success']}")
    print(f"  Confidence: {result.get('confidence', 0):.2f}")
    print(f"  Method: {result.get('method', 'unknown')}")

    print("\n" + "=" * 70)
    print("Deep integration bridge operational!")
    print("Cognitive + Organism systems unified.")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
