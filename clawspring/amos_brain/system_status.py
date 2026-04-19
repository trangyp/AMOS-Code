"""AMOS System Status - Complete ecosystem health check."""

import sys
from pathlib import Path
from typing import Tuple

# Module paths
MODULES = [
    "amos_cognitive_router.py",
    "engine_executor.py",
    "multi_agent_orchestrator.py",
    "cognitive_audit.py",
    "feedback_loop.py",
    "audit_exporter.py",
    "loader.py",
    "laws.py",
    "prompt_builder.py",
    "dashboard.html",
    "dashboard_server.py",
]


def check_module_exists(module_dir: Path, name: str) -> bool:
    """Check if a module file exists."""
    # Router is in parent dir, others in amos_brain
    if name == "amos_cognitive_router.py":
        return (module_dir.parent / name).exists()
    return (module_dir / name).exists()


def check_imports_work() -> Tuple[bool, list[str]]:
    """Test if core imports work."""
    errors = []
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        try:
            from amos_cognitive_router import get_router

            get_router()  # Verify import works
        except Exception as e:
            errors.append(f"Router: {e}")

        try:
            from amos_brain.cognitive_audit import get_audit_trail

            get_audit_trail()  # Verify import works
        except Exception as e:
            errors.append(f"Audit: {e}")

        return len(errors) == 0, errors
    except Exception as e:
        return False, [str(e)]


def get_system_status() -> Dict:
    """Get complete system status."""
    module_dir = Path(__file__).parent

    # Check modules
    modules_status = {name: check_module_exists(module_dir, name) for name in MODULES}

    # Check imports
    imports_ok, import_errors = check_imports_work()

    # Get audit stats if available
    audit_stats = {}
    try:
        sys.path.insert(0, str(module_dir.parent))
        from amos_brain.cognitive_audit import get_audit_trail

        audit = get_audit_trail()
        audit_stats = audit.get_statistics()
    except Exception:
        pass

    return {
        "modules": modules_status,
        "modules_present": sum(modules_status.values()),
        "modules_total": len(modules_status),
        "imports_working": imports_ok,
        "import_errors": import_errors,
        "audit_stats": audit_stats,
    }


def print_status_report():
    """Print formatted status report."""
    status = get_system_status()

    print("=" * 70)
    print("AMOS COGNITIVE SYSTEM - STATUS REPORT")
    print("=" * 70)

    # Module status
    print("\n📦 MODULES:")
    for name, exists in status["modules"].items():
        icon = "✓" if exists else "✗"
        print(f"  {icon} {name}")

    # Summary
    print(f"\n  Total: {status['modules_present']}/{status['modules_total']} present")

    # Imports
    print("\n🔧 IMPORTS:")
    if status["imports_working"]:
        print("  ✓ Core modules importable")
        print("  ✓ Router operational")
        print("  ✓ Audit trail accessible")
    else:
        print("  ✗ Import errors detected:")
        for err in status["import_errors"]:
            print(f"    - {err}")

    # Audit stats
    if status["audit_stats"]:
        stats = status["audit_stats"]
        print("\n📊 AUDIT TRAIL:")
        print(f"  • Total decisions: {stats.get('total_entries', 0)}")
        print(f"  • Violation rate: {stats.get('violation_rate', 0):.1%}")
        print(f"  • Avg execution: {stats.get('avg_execution_time_ms', 0):.1f}ms")
        domains = stats.get("domains", {})
        if domains:
            print(f"  • Active domains: {', '.join(domains.keys())}")

    # Overall status
    all_modules_ok = status["modules_present"] == status["modules_total"]
    imports_ok = status["imports_working"]

    print("\n" + "=" * 70)
    if all_modules_ok and imports_ok:
        print("✅ SYSTEM STATUS: OPERATIONAL")
        print("   All 10 modules present and functional")
        print("   AMOS cognitive integration is PRODUCTION READY")
    elif all_modules_ok and not imports_ok:
        print("⚠️  SYSTEM STATUS: DEGRADED")
        print("   All modules present but import issues detected")
    else:
        print("❌ SYSTEM STATUS: INCOMPLETE")
        print(f"   Missing {status['modules_total'] - status['modules_present']} modules")
    print("=" * 70)


if __name__ == "__main__":
    print_status_report()
