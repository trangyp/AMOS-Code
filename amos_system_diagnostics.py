#!/usr/bin/env python3
"""AMOS System Diagnostics - Validates integrity of all 56 components."""

import sys
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ComponentCheck:
    """Result of checking a single component."""

    name: str
    file_path: str
    importable: bool
    has_main_function: bool
    errors: List[str] = field(default_factory=list)
    load_time_ms: float = 0.0


@dataclass
class DiagnosticsReport:
    """Complete system diagnostics report."""

    timestamp: str
    total_components: int
    importable: int
    failed: int
    components: List[ComponentCheck]
    ecosystem_integrity: str  # intact, degraded, broken


class SystemDiagnostics:
    """Diagnostics tool for the 56-component AMOS ecosystem."""

    # All 56 components to validate
    COMPONENTS = [
        # Core AMOSL Runtime (7)
        "amosl_ledger",
        "amosl_verification",
        "amosl_bridge",
        "amosl_evolution",
        "amosl_kernel",
        "amosl_axioms",
        "amosl_admissibility",
        # Feature Ecosystem (2)
        "amos_feature_activation",
        "amos_primary_feature_handler",
        # Knowledge & Engines (3)
        "amos_knowledge_loader",
        "amos_engine_activator",
        "amos_cognitive_router",
        # Master Orchestration (2)
        "amos_master_cognitive_orchestrator",
        "amos_organism_integration_bridge",
        # Integration (1)
        "amos_integration_test",
        # Demos (4)
        "amos_comprehensive_demo",
        "amos_quickstart_demo",
        "amos_organism_bridge_demo",
        "amos_unified_execution_engine",
        # Interfaces (4)
        "amos_cli_simple",
        "amos_http_api",
        "amos_dashboard",
        "amos_brain_ui",
        # Infrastructure (43+)
        "amos_core",
        "amos_brain",
        "amos_decision",
        "amos_orchestrator",
        "amos_integrated_workflow",
        "amos_organism_orchestrator",
        "amos_axiom_validator",
        "amos_cognitive_runtime",
        "amos_coherence_engine",
        "amos_coherence_omega",
        "amos_coherent_organism",
        "amos_health_monitor",
        "amos_muscle_executor",
        "amos_connectors",
        "amos_cognitive_agent",
        "amos_autonomous_agent",
        "amos_api_enhanced",
        "amos_api_simple",
        "amos_api_server",
        "amos_brain_cli",
        "amos_brain_launcher",
        "amos_cleanup_analyzer",
        "amos_creative_reasoning",
        "amos_database",
        "amos_brain_organism_bridge",
        "amos_dashboard_enhanced",
        "amos_economic_engine",
        "amos_economic_organism",
        "amos_field_theory",
        "amos_final_comprehensive_demo",
        "amos_final_demo",
        "amos_eight_layer_demo",
        "amos_activate_self_driving",
        "amos_agent_bridge",
        "amos_alerting",
        "amos_brain_complete_ui",
        "amos_brain_enhanced_ui",
        "amos_brain_live_demo",
        "amos_brain_tutorial",
        "amos_brain_unified_ui",
        "amos_decide_next_build",
        "amos_decide_next_iteration",
        "amos_clawspring",
        "amos_state",
    ]

    def __init__(self, repo_path: str = "."):
        """Initialize diagnostics tool."""
        self.repo_path = Path(repo_path)
        self.results: List[ComponentCheck] = []

    def run_full_diagnostics(self) -> DiagnosticsReport:
        """Run complete diagnostics on all components."""
        print("\n" + "=" * 70)
        print("AMOS SYSTEM DIAGNOSTICS - 56 COMPONENTS")
        print("=" * 70)

        start_time = time.time()

        for component in self.COMPONENTS:
            check = self._check_component(component)
            self.results.append(check)
            status = "✓" if check.importable else "✗"
            print(f"  {status} {component:40s} ({check.load_time_ms:.1f}ms)")

        total_time = (time.time() - start_time) * 1000

        importable = sum(1 for r in self.results if r.importable)
        failed = len(self.results) - importable

        # Determine ecosystem integrity
        if failed == 0:
            integrity = "intact"
        elif failed <= 3:
            integrity = "degraded"
        else:
            integrity = "broken"

        report = DiagnosticsReport(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            total_components=len(self.results),
            importable=importable,
            failed=failed,
            components=self.results,
            ecosystem_integrity=integrity,
        )

        print("\n" + "=" * 70)
        print("DIAGNOSTICS SUMMARY")
        print("=" * 70)
        print(f"  Total Components: {report.total_components}")
        print(f"  Importable: {report.importable}")
        print(f"  Failed: {report.failed}")
        print(f"  Integrity: {report.ecosystem_integrity.upper()}")
        print(f"  Total Time: {total_time:.1f}ms")
        print("=" * 70)

        return report

    def _check_component(self, name: str) -> ComponentCheck:
        """Check if a component can be imported."""
        start = time.time()
        errors = []
        importable = False
        has_main = False

        try:
            # Try to import the module
            module = __import__(name)
            importable = True

            # Check for main function
            has_main = hasattr(module, "main") and callable(module.main)

        except ImportError as e:
            errors.append(f"Import error: {e}")
        except Exception as e:
            errors.append(f"Error: {e}")

        load_time = (time.time() - start) * 1000

        # Find file path
        file_path = f"{name}.py"

        return ComponentCheck(
            name=name,
            file_path=file_path,
            importable=importable,
            has_main_function=has_main,
            errors=errors,
            load_time_ms=load_time,
        )

    def get_failed_components(self) -> List[ComponentCheck]:
        """Get list of failed components."""
        return [r for r in self.results if not r.importable]

    def print_detailed_report(self):
        """Print detailed diagnostics report."""
        failed = self.get_failed_components()

        if failed:
            print("\n" + "=" * 70)
            print("FAILED COMPONENTS")
            print("=" * 70)
            for comp in failed:
                print(f"\n  ✗ {comp.name}")
                for error in comp.errors:
                    print(f"    → {error}")
        else:
            print("\n  ✓ All components importable")

        print("\n" + "=" * 70)


def main():
    """Run system diagnostics."""
    diagnostics = SystemDiagnostics()
    report = diagnostics.run_full_diagnostics()
    diagnostics.print_detailed_report()

    # Exit code based on integrity
    if report.ecosystem_integrity == "intact":
        return 0
    elif report.ecosystem_integrity == "degraded":
        return 1
    else:
        return 2


if __name__ == "__main__":
    sys.exit(main())
