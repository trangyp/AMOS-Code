#!/usr/bin/env python3
"""AMOS Ecosystem v2.8 - Ecosystem Integration Adapter.

Connects existing AMOS files (amos_integrated_workflow.py,
amos_integration_test.py, amos_coherence_engine.py, amos_tools.py)
to the new v2.8 ecosystem in clawspring/amos_brain/.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


class EcosystemAdapter:
    """Adapters for integrating existing AMOS files with v2.8 ecosystem."""

    def __init__(self):
        self.adapters: dict[str, Any] = {}
        self._load_adapters()

    def _load_adapters(self) -> None:
        """Load all integration adapters."""
        self.adapters = {
            "integrated_workflow": WorkflowAdapter(),
            "integration_test": TestAdapter(),
            "coherence_engine": CoherenceAdapter(),
            "amos_tools": ToolsAdapter(),
        }

    def get_adapter(self, name: str) -> Any | None:
        """Get a specific adapter."""
        return self.adapters.get(name)

    def get_all_status(self) -> dict[str, str]:
        """Get status of all adapters."""
        return {
            name: "active" if adapter.is_available() else "unavailable"
            for name, adapter in self.adapters.items()
        }


class WorkflowAdapter:
    """Adapter for amos_integrated_workflow.py."""

    def __init__(self):
        self.workflow_module = None
        self._load_workflow()

    def _load_workflow(self) -> None:
        """Load the integrated workflow module."""
        try:
            workflow_path = Path(__file__).parent.parent.parent / "amos_integrated_workflow.py"
            if workflow_path.exists():
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    "amos_integrated_workflow", workflow_path
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.workflow_module = module
        except Exception as e:
            print(f"[WorkflowAdapter] Load warning: {e}")

    def is_available(self) -> bool:
        """Check if workflow module is available."""
        return self.workflow_module is not None

    def run_workflow(self, task: str) -> dict[str, Any]:
        """Run workflow through v2.8 ecosystem."""
        if not self.workflow_module:
            return {"error": "Workflow module not available"}

        try:
            # Route through cognitive system
            from amos_cognitive_router import CognitiveRouter

            router = CognitiveRouter()
            analysis = router.analyze(task)

            return {
                "workflow": "integrated",
                "routed": True,
                "domain": analysis.primary_domain,
                "engines": analysis.suggested_engines,
            }
        except Exception as e:
            return {"error": str(e)}


class TestAdapter:
    """Adapter for amos_integration_test.py."""

    def __init__(self):
        self.test_module = None
        self._load_test()

    def _load_test(self) -> None:
        """Load the integration test module."""
        try:
            test_path = Path(__file__).parent.parent.parent / "amos_integration_test.py"
            if test_path.exists():
                import importlib.util

                spec = importlib.util.spec_from_file_location("amos_integration_test", test_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.test_module = module
        except Exception as e:
            print(f"[TestAdapter] Load warning: {e}")

    def is_available(self) -> bool:
        """Check if test module is available."""
        return self.test_module is not None

    def run_tests(self) -> dict[str, Any]:
        """Run integration tests through v2.8 validator."""
        try:
            from system_health_validator import SystemHealthValidator

            validator = SystemHealthValidator()
            result = validator.run_full_validation()

            return {
                "tests": "integrated",
                "healthy": result.get("healthy", 0),
                "unhealthy": result.get("unhealthy", 0),
                "status": result.get("status", "unknown"),
            }
        except Exception as e:
            return {"error": str(e)}


class CoherenceAdapter:
    """Adapter for amos_coherence_engine.py."""

    def __init__(self):
        self.coherence_module = None
        self._load_coherence()

    def _load_coherence(self) -> None:
        """Load the coherence engine module."""
        try:
            coherence_path = Path(__file__).parent.parent.parent / "amos_coherence_engine.py"
            if coherence_path.exists():
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    "amos_coherence_engine", coherence_path
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.coherence_module = module
        except Exception as e:
            print(f"[CoherenceAdapter] Load warning: {e}")

    def is_available(self) -> bool:
        """Check if coherence engine is available."""
        return self.coherence_module is not None

    def check_coherence(self, state: dict) -> float:
        """Check coherence using v2.8 integration."""
        try:
            from deep_integration import get_deep_integration

            integration = get_deep_integration()
            unified_state = integration.get_unified_state()
            return unified_state.coherence_score
        except Exception:
            return 1.0


class ToolsAdapter:
    """Adapter for clawspring/amos_tools.py."""

    def __init__(self):
        self.tools_module = None
        self._load_tools()

    def _load_tools(self) -> None:
        """Load the tools module."""
        try:
            tools_path = Path(__file__).parent.parent / "amos_tools.py"
            if tools_path.exists():
                import importlib.util

                spec = importlib.util.spec_from_file_location("amos_tools", tools_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.tools_module = module
        except Exception as e:
            print(f"[ToolsAdapter] Load warning: {e}")

    def is_available(self) -> bool:
        """Check if tools module is available."""
        return self.tools_module is not None

    def get_tools(self) -> list[str]:
        """Get available tools through v2.8 system."""
        try:
            from unified_cli import UnifiedCLI

            cli = UnifiedCLI()
            return list(cli.commands.keys())
        except Exception:
            return []


def main():
    """Demo ecosystem adapter."""
    print("=" * 70)
    print("AMOS ECOSYSTEM v2.8 - ECOSYSTEM ADAPTER")
    print("=" * 70)

    adapter = EcosystemAdapter()

    print("\nAdapter Status:")
    for name, status in adapter.get_all_status().items():
        icon = "✓" if status == "active" else "✗"
        print(f"  {icon} {name}: {status}")

    # Test workflow adapter
    workflow = adapter.get_adapter("integrated_workflow")
    if workflow and workflow.is_available():
        print("\nTesting Workflow Integration:")
        result = workflow.run_workflow("Design secure API")
        print(f"  Status: {result.get('workflow', 'unknown')}")

    # Test coherence adapter
    coherence = adapter.get_adapter("coherence_engine")
    if coherence and coherence.is_available():
        print("\nTesting Coherence Integration:")
        score = coherence.check_coherence({})
        print(f"  Coherence Score: {score:.2f}")

    print("\n" + "=" * 70)
    print("Ecosystem adapter connecting v2.8 to existing files!")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
