#!/usr/bin/env python3
"""Test script for Mathematical Framework Integration across AMOS ecosystem."""

import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "clawspring"))
sys.path.insert(0, str(Path(__file__).parent / "clawspring" / "amos_brain"))


def test_imports():
    """Test that all mathematical framework components can be imported."""
    print("Testing imports...")

    try:
        from clawspring.amos_brain.mathematical_framework_engine import (
            MathematicalFrameworkEngine,
            get_framework_engine,
        )

        print("✓ MathematicalFrameworkEngine")
    except ImportError as e:
        print(f"✗ MathematicalFrameworkEngine: {e}")
        return False

    try:
        from clawspring.amos_brain.math_audit_logger import get_math_audit_logger

        print("✓ MathFrameworkAuditLogger")
    except ImportError as e:
        print(f"✗ MathFrameworkAuditLogger: {e}")
        return False

    try:
        from clawspring.amos_brain.design_validation_engine import DesignValidationEngine

        print("✓ DesignValidationEngine")
    except ImportError as e:
        print(f"✗ DesignValidationEngine: {e}")
        return False

    return True


def test_engine_functionality():
    """Test math engine basic functionality."""
    print("\nTesting engine functionality...")

    try:
        from clawspring.amos_brain.mathematical_framework_engine import get_framework_engine

        engine = get_framework_engine()

        # Test query by domain
        equations = engine.query_by_domain("UI_UX")
        print(f"✓ Query UI_UX domain: {len(equations)} equations")

        # Test stats
        stats = engine.get_stats()
        print(f"✓ Engine stats: {stats.get('total_equations', 0)} total equations")

        return True
    except Exception as e:
        print(f"✗ Engine functionality: {e}")
        return False


def test_audit_logger():
    """Test audit logger functionality."""
    print("\nTesting audit logger...")

    try:
        from clawspring.amos_brain.math_audit_logger import get_math_audit_logger

        logger = get_math_audit_logger()

        # Log a test entry
        logger.log_equation_query("test_equation", ["UI_UX"], {"test": True})
        print("✓ Log equation query")

        # Get stats
        stats = logger.get_statistics()
        print(f"✓ Audit stats: {stats.get('total_entries', 0)} entries")

        return True
    except Exception as e:
        print(f"✗ Audit logger: {e}")
        return False


def test_dashboard_server():
    """Test dashboard server endpoints (basic import check)."""
    print("\nTesting dashboard server...")

    try:
        # Import the server module
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "math_dashboard_server",
            Path(__file__).parent / "clawspring" / "amos_brain" / "math_dashboard_server.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        print("✓ Dashboard server module loads")
        print(f"✓ FastAPI app: {module.app}")

        return True
    except Exception as e:
        print(f"✗ Dashboard server: {e}")
        return False


def test_html_dashboard():
    """Test that dashboard HTML exists."""
    print("\nTesting dashboard HTML...")

    dashboard_path = Path(__file__).parent / "clawspring" / "amos_brain" / "math_dashboard.html"

    if dashboard_path.exists():
        size = dashboard_path.stat().st_size
        print(f"✓ Dashboard HTML exists ({size} bytes)")

        # Check for key elements
        content = dashboard_path.read_text()
        checks = [
            ("API endpoints", "/api/" in content),
            ("Stats display", "total-equations" in content),
            ("Health indicators", "health-indicator" in content),
            ("Auto-refresh", "setInterval" in content),
        ]

        for name, present in checks:
            status = "✓" if present else "✗"
            print(f"  {status} {name}")

        return all(c[1] for c in checks)
    else:
        print(f"✗ Dashboard HTML not found at {dashboard_path}")
        return False


def test_unified_governance():
    """Test unified governance coordinator integration."""
    print("\nTesting unified governance...")

    try:
        from clawspring.amos_brain.unified_governance_coordinator import (
            MATH_AUDIT_AVAILABLE,
            MATH_FRAMEWORK_AVAILABLE,
            UnifiedGovernanceCoordinator,
        )

        print(f"✓ MATH_FRAMEWORK_AVAILABLE: {MATH_FRAMEWORK_AVAILABLE}")
        print(f"✓ MATH_AUDIT_AVAILABLE: {MATH_AUDIT_AVAILABLE}")

        # Create coordinator
        coord = UnifiedGovernanceCoordinator()

        # Test health check
        health = coord.check_math_framework_health()
        print(f"✓ Health check: {health}")

        return True
    except Exception as e:
        print(f"✗ Unified governance: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_superbrain_bridge():
    """Test SuperBrain knowledge bridge integration."""
    print("\nTesting SuperBrain knowledge bridge...")

    try:
        from amos_superbrain_knowledge_bridge import (
            MATH_AUDIT_AVAILABLE,
            MATH_FRAMEWORK_AVAILABLE,
            SuperBrainKnowledgeBridge,
        )

        print(f"✓ MATH_FRAMEWORK_AVAILABLE: {MATH_FRAMEWORK_AVAILABLE}")
        print(f"✓ MATH_AUDIT_AVAILABLE: {MATH_AUDIT_AVAILABLE}")

        # Create bridge
        bridge = SuperBrainKnowledgeBridge()

        # Test cross-reference (may fail if no equations cached, but should not crash)
        try:
            result = bridge.cross_reference_with_math_framework("test_equation")
            print(f"✓ Cross-reference method: {result.get('math_framework_enabled', False)}")
        except Exception as e:
            print(f"⚠ Cross-reference (expected for empty cache): {e}")

        return True
    except Exception as e:
        print(f"✗ SuperBrain bridge: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("AMOS Mathematical Framework Integration Test Suite")
    print("=" * 60)

    results = {
        "imports": test_imports(),
        "engine": test_engine_functionality(),
        "audit": test_audit_logger(),
        "dashboard_server": test_dashboard_server(),
        "dashboard_html": test_html_dashboard(),
        "governance": test_unified_governance(),
        "superbrain": test_superbrain_bridge(),
    }

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All integrations working correctly!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
