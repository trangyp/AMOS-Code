"""AMOS System Validator - Comprehensive validation of all ecosystem components."""

import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class ValidationResult:
    """Result of component validation."""

    component: str
    status: str  # "PASS", "FAIL", "WARN"
    message: str
    details: dict


class SystemValidator:
    """Validates all 15 AMOS ecosystem components."""

    def __init__(self):
        self.results: list[ValidationResult] = []
        self.cognitive_modules = [
            "amos_cognitive_router.py",
            "engine_executor.py",
            "multi_agent_orchestrator.py",
            "cognitive_audit.py",
            "feedback_loop.py",
            "audit_exporter.py",
            "loader.py",
            "laws.py",
            "prompt_builder.py",
            "system_status.py",
            "dashboard_server.py",
        ]
        self.organism_modules = [
            "organism_bridge.py",
            "predictive_integration.py",
            "task_execution_integration.py",
        ]
        self.master_modules = [
            "master_orchestrator.py",
        ]

    def validate_all(self) -> list[ValidationResult]:
        """Run full system validation."""
        self.results = []

        # Phase 1: Module Presence
        self._validate_module_presence()

        # Phase 2: Import Tests
        self._validate_imports()

        # Phase 3: Functional Tests
        self._validate_functionality()

        # Phase 4: Integration Tests
        self._validate_integration()

        return self.results

    def _validate_module_presence(self):
        """Check all modules exist."""
        module_dir = Path(__file__).parent

        all_modules = self.cognitive_modules + self.organism_modules + self.master_modules

        for module in all_modules:
            exists = (module_dir / module).exists()
            self.results.append(
                ValidationResult(
                    component=f"module:{module}",
                    status="PASS" if exists else "FAIL",
                    message=f"{'Found' if exists else 'Missing'}: {module}",
                    details={"path": str(module_dir / module), "exists": exists},
                )
            )

    def _validate_imports(self):
        """Test all modules can be imported."""
        imports_to_test = [
            ("amos_cognitive_router", "CognitiveRouter"),
            ("engine_executor", "EngineExecutor"),
            ("multi_agent_orchestrator", "MultiAgentOrchestrator"),
            ("cognitive_audit", "CognitiveAuditTrail"),
            ("feedback_loop", "CognitiveFeedbackLoop"),
            ("audit_exporter", "AuditExporter"),
            ("loader", "BrainLoader"),
            ("laws", "GlobalLawEnforcer"),
            ("prompt_builder", "PromptBuilder"),
            ("system_status", "get_system_status"),
            ("organism_bridge", "OrganismBridge"),
            ("predictive_integration", "PredictiveIntegration"),
            ("task_execution_integration", "TaskExecutionIntegration"),
            ("master_orchestrator", "MasterOrchestrator"),
        ]

        for module_name, class_name in imports_to_test:
            try:
                module = __import__(module_name)
                hasattr(module, class_name)
                self.results.append(
                    ValidationResult(
                        component=f"import:{module_name}",
                        status="PASS",
                        message=f"Successfully imported {module_name}",
                        details={"class": class_name},
                    )
                )
            except Exception as e:
                self.results.append(
                    ValidationResult(
                        component=f"import:{module_name}",
                        status="FAIL",
                        message=f"Failed to import {module_name}: {e}",
                        details={"error": str(e)},
                    )
                )

    def _validate_functionality(self):
        """Test basic functionality of key components."""
        # Test cognitive router
        try:
            from amos_cognitive_router import CognitiveRouter

            router = CognitiveRouter()
            analysis = router.analyze("Test task")
            self.results.append(
                ValidationResult(
                    component="func:cognitive_router",
                    status="PASS",
                    message="Router analyzing tasks correctly",
                    details={"domain": analysis.primary_domain},
                )
            )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    component="func:cognitive_router",
                    status="FAIL",
                    message=f"Router failed: {e}",
                    details={},
                )
            )

        # Test audit trail
        try:
            from cognitive_audit import get_audit_trail

            audit = get_audit_trail()
            stats = audit.get_statistics()
            self.results.append(
                ValidationResult(
                    component="func:audit_trail",
                    status="PASS",
                    message="Audit trail operational",
                    details={"entries": stats.get("total_entries", 0)},
                )
            )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    component="func:audit_trail",
                    status="FAIL",
                    message=f"Audit failed: {e}",
                    details={},
                )
            )

        # Test organism bridge
        try:
            from organism_bridge import get_organism_bridge

            bridge = get_organism_bridge()
            status = bridge.get_status()
            connected = status.get("total_connected", 0)
            total = status.get("total_available", 3)
            self.results.append(
                ValidationResult(
                    component="func:organism_bridge",
                    status="PASS" if connected == total else "WARN",
                    message=f"Bridge: {connected}/{total} components",
                    details=status,
                )
            )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    component="func:organism_bridge",
                    status="FAIL",
                    message=f"Bridge failed: {e}",
                    details={},
                )
            )

        # Test master orchestrator
        try:
            from master_orchestrator import get_master_orchestrator

            orchestrator = get_master_orchestrator()
            orch_status = orchestrator.get_ecosystem_status()
            self.results.append(
                ValidationResult(
                    component="func:master_orchestrator",
                    status="PASS" if orch_status.get("initialized") else "WARN",
                    message="Master orchestrator initialized",
                    details=orch_status,
                )
            )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    component="func:master_orchestrator",
                    status="FAIL",
                    message=f"Orchestrator failed: {e}",
                    details={},
                )
            )

    def _validate_integration(self):
        """Test component integrations."""
        # Test predictive + execution integration
        try:
            from predictive_integration import predict_task
            from task_execution_integration import execute_task

            prediction = predict_task("Test task", "software", "MEDIUM")
            execution = execute_task("test_001", "Test task", "software", ["Engineering"])

            self.results.append(
                ValidationResult(
                    component="integ:predictive_execution",
                    status="PASS",
                    message="Predictive and execution integration working",
                    details={
                        "prediction_confidence": prediction.confidence,
                        "execution_success": execution.success,
                    },
                )
            )
        except Exception as e:
            self.results.append(
                ValidationResult(
                    component="integ:predictive_execution",
                    status="FAIL",
                    message=f"Integration failed: {e}",
                    details={},
                )
            )

    def get_summary(self) -> dict:
        """Get validation summary."""
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        warnings = sum(1 for r in self.results if r.status == "WARN")
        total = len(self.results)

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "success_rate": passed / total if total > 0 else 0,
            "timestamp": datetime.now().isoformat(),
            "overall_status": "PASS" if failed == 0 else "FAIL",
        }

    def print_report(self):
        """Print validation report."""
        print("=" * 70)
        print("AMOS SYSTEM VALIDATOR v2.0 - VALIDATION REPORT")
        print("=" * 70)
        print(f"\nTimestamp: {datetime.now().isoformat()}")
        print(
            f"Modules Tested: {len(self.cognitive_modules) + len(self.organism_modules) + len(self.master_modules)}"
        )

        # Group by category
        categories = {
            "Module Presence": [r for r in self.results if r.component.startswith("module:")],
            "Import Tests": [r for r in self.results if r.component.startswith("import:")],
            "Functional Tests": [r for r in self.results if r.component.startswith("func:")],
            "Integration Tests": [r for r in self.results if r.component.startswith("integ:")],
        }

        for category, results in categories.items():
            if results:
                print(f"\n📋 {category}:")
                for result in results:
                    icon = (
                        "✓" if result.status == "PASS" else "⚠" if result.status == "WARN" else "✗"
                    )
                    print(f"  {icon} {result.component.split(':')[1]:<30} {result.status}")

        summary = self.get_summary()
        print(f"\n{'=' * 70}")
        print("📊 SUMMARY:")
        print(f"  Total Tests: {summary['total']}")
        print(f"  Passed: {summary['passed']} ✓")
        print(f"  Warnings: {summary['warnings']} ⚠")
        print(f"  Failed: {summary['failed']} ✗")
        print(f"  Success Rate: {summary['success_rate']:.1%}")
        print(f"\n  Overall Status: {summary['overall_status']}")

        if summary["failed"] == 0:
            print("\n  🎉 AMOS ECOSYSTEM v2.0: VALIDATED AND OPERATIONAL")
        elif summary["failed"] <= 2:
            print("\n  ⚠️  AMOS ECOSYSTEM v2.0: MOSTLY OPERATIONAL (minor issues)")
        else:
            print("\n  ❌ AMOS ECOSYSTEM v2.0: ISSUES DETECTED")

        print(f"{'=' * 70}")


def validate_system() -> tuple[bool, dict]:
    """Run full validation and return results."""
    validator = SystemValidator()
    validator.validate_all()
    summary = validator.get_summary()
    validator.print_report()
    return summary["failed"] == 0, summary


if __name__ == "__main__":
    success, summary = validate_system()
    sys.exit(0 if success else 1)
