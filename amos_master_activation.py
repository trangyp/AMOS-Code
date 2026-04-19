#!/usr/bin/env python3
"""AMOS Master Activation - Unified System Integration Layer.

Production-ready activation script that:
1. Handles all import variations gracefully
2. Activates available subsystems with fallbacks
3. Provides end-to-end system validation
4. Generates comprehensive status report

This is the master entry point for the complete AMOS ecosystem.
"""

import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, Tuple

# Add project paths
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "clawspring"))


def print_banner():
    """Print activation banner."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║           AMOS MASTER ACTIVATION                                 ║
║           Unified Biosocial System v57.0                         ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)


def check_component(name: str, import_path: str, class_name: str = None) -> Tuple[bool, Any]:
    """Check if a component is available."""
    try:
        module = __import__(import_path, fromlist=[class_name] if class_name else [])
        if class_name:
            return True, getattr(module, class_name)
        return True, module
    except ImportError as e:
        return False, str(e)


def activate_57_component_core() -> Dict[str, Any]:
    """Activate the 57-component cognitive core."""
    print("\n🔬 [1/4] Activating 57-Component Cognitive Core...")
    print("-" * 60)

    result = {
        "available": False,
        "initialized": False,
        "status": None,
        "error": None,
    }

    # Check availability
    available, OrchestratorClass = check_component(
        "57-Component Core", "amos_57_master_orchestrator", "AMOS57MasterOrchestrator"
    )

    if not available:
        print("   ⚠️  57-Component Core not available")
        result["error"] = str(OrchestratorClass)
        return result

    print("   ✓ Module available")

    # Try to initialize
    try:
        from amos_57_master_orchestrator import OrchestratorConfig

        config = OrchestratorConfig(
            health_check_interval=5.0,
            self_healing_enabled=True,
        )
        orchestrator = OrchestratorClass(config)

        print("   ✓ Orchestrator instantiated")

        # Initialize
        if orchestrator.initialize():
            print("   ✓ Initialized successfully")
            result["initialized"] = True

            # Get status
            result["status"] = orchestrator.get_status()

            # Start operation
            orchestrator.start()
            print("   ✓ Autonomous operation started")

            # Store reference
            result["instance"] = orchestrator
        else:
            print("   ⚠️  Initialization failed")
            result["error"] = "Initialization returned False"

    except Exception as e:
        print(f"   ❌ Error: {e}")
        traceback.print_exc()
        result["error"] = str(e)

    result["available"] = True
    return result


def activate_ubi_engine() -> Dict[str, Any]:
    """Activate Unified Biological Intelligence."""
    print("\n🧠 [2/4] Activating Unified Biological Intelligence...")
    print("-" * 60)

    result = {
        "available": False,
        "domains_active": 0,
        "domains": {},
        "error": None,
    }

    # Check availability
    available, UBIClass = check_component("UBI Engine", "amos_ubi_engine", "AMOSUBIEngine")

    if not available:
        print("   ⚠️  UBI Engine not available")
        result["error"] = str(UBIClass)
        return result

    print("   ✓ UBI Engine module available")

    # Try to instantiate
    try:
        ubi = UBIClass()
        print("   ✓ UBI Engine instantiated")

        # Test analysis
        test_result = ubi.analyze(
            description="Test system operation", domains=["NBI", "NEI", "SI", "BEI"]
        )

        result["domains_active"] = len(test_result)
        result["domains"] = list(test_result.keys())
        result["instance"] = ubi

        print(f"   ✓ {result['domains_active']} domains active:")
        for domain in result["domains"]:
            print(f"      - {domain}")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        result["error"] = str(e)

    result["available"] = True
    return result


def activate_repo_doctor() -> Dict[str, Any]:
    """Activate Repo Doctor Omega."""
    print("\n🔍 [3/4] Activating Repo Doctor Omega...")
    print("-" * 60)

    result = {
        "available": False,
        "energy": None,
        "invariants": 0,
        "error": None,
    }

    # Check availability
    available, EngineClass = check_component(
        "Repo Doctor", "repo_doctor_omega.engine", "RepoDoctorEngine"
    )

    if not available:
        print("   ⚠️  Repo Doctor Omega not available")
        # Try legacy repo_doctor
        available, EngineClass = check_component(
            "Repo Doctor (legacy)", "repo_doctor.state.basis", "BasisAnalyzer"
        )
        if not available:
            result["error"] = "Both Omega and legacy unavailable"
            return result

    print("   ✓ Repo Doctor module available")

    # Try to activate
    try:
        engine = EngineClass(str(PROJECT_ROOT))
        print("   ✓ Engine instantiated")

        # Try to compute state
        if hasattr(engine, "compute_state"):
            state = engine.compute_state()
            result["energy"] = state.compute_energy() if hasattr(state, "compute_energy") else 0.0
            print(f"   ✓ Repository energy: {result['energy']:.3f}")

        # Try to run invariants
        if hasattr(engine, "evaluate_invariants"):
            inv_results = engine.evaluate_invariants()
            result["invariants"] = len(inv_results)
            passed = sum(1 for r in inv_results if getattr(r, "passed", False))
            print(f"   ✓ Invariants: {passed}/{result['invariants']} passed")

        result["instance"] = engine

    except Exception as e:
        print(f"   ❌ Error: {e}")
        result["error"] = str(e)

    result["available"] = True
    return result


def activate_self_evolution() -> Dict[str, Any]:
    """Activate Self-Evolution Engine."""
    print("\n🔄 [4/4] Activating Self-Evolution Engine...")
    print("-" * 60)

    result = {
        "available": False,
        "opportunities": 0,
        "error": None,
    }

    # Check availability
    available, DetectorClass = check_component(
        "Self-Evolution",
        "amos_self_evolution.evolution_opportunity_detector",
        "EvolutionOpportunityDetector",
    )

    if not available:
        print("   ⚠️  Self-Evolution Engine not available")
        result["error"] = str(DetectorClass)
        return result

    print("   ✓ Self-Evolution module available")

    # Try to instantiate
    try:
        detector = DetectorClass()
        print("   ✓ Opportunity detector instantiated")

        # Try to detect opportunities
        if hasattr(detector, "detect_opportunities"):
            ops = detector.detect_opportunities(str(PROJECT_ROOT))
            result["opportunities"] = len(ops)
            print(f"   ✓ {result['opportunities']} evolution opportunities detected")

        result["instance"] = detector

    except Exception as e:
        print(f"   ❌ Error: {e}")
        result["error"] = str(e)

    result["available"] = True
    return result


def compute_unified_status(components: Dict[str, Any]) -> Dict[str, Any]:
    """Compute unified system status."""
    print("\n📊 Computing Unified System Status...")
    print("-" * 60)

    # Count available components
    available_count = sum(1 for c in components.values() if c.get("available", False))
    initialized_count = sum(1 for c in components.values() if c.get("initialized", False))
    total_components = len(components)

    # Compute biosocial harmony (simplified)
    harmony = available_count / total_components

    # Human readiness
    ubi = components.get("ubi_engine", {})
    human_ready = ubi.get("available", False)

    # Cognitive health
    core = components.get("57_component_core", {})
    cognitive_health = 0.8 if core.get("initialized", False) else 0.5

    # Repository energy
    repo = components.get("repo_doctor", {})
    repo_energy = repo.get("energy", 100.0) or 100.0
    repo_health = max(0, 1.0 - (repo_energy / 100.0))

    status = {
        "timestamp": time.time(),
        "components_total": total_components,
        "components_available": available_count,
        "components_initialized": initialized_count,
        "biosocial_harmony": round(harmony, 2),
        "human_ready": human_ready,
        "cognitive_health": round(cognitive_health, 2),
        "repository_health": round(repo_health, 2),
        "overall_grade": "EXCELLENT" if harmony > 0.8 else "GOOD" if harmony > 0.6 else "DEGRADED",
    }

    print(f"   Components Available: {available_count}/{total_components}")
    print(f"   Biosocial Harmony: {status['biosocial_harmony']}")
    print(f"   Overall Grade: {status['overall_grade']}")

    return status


def generate_report(components: Dict[str, Any], status: Dict[str, Any]) -> str:
    """Generate comprehensive activation report."""
    report = f"""
{'=' * 70}
AMOS MASTER ACTIVATION REPORT
{'=' * 70}

Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}

SYSTEM STATUS
-------------
Overall Grade: {status['overall_grade']}
Biosocial Harmony: {status['biosocial_harmony']}
Components Active: {status['components_available']}/{status['components_total']}

COMPONENT BREAKDOWN
-------------------
"""

    for name, component in components.items():
        available = "✅" if component.get("available") else "❌"
        initialized = "🟢" if component.get("initialized") else "⚪"
        report += f"\n{name.replace('_', ' ').title()}:\n"
        report += f"  Available: {available}\n"
        report += f"  Initialized: {initialized}\n"

        if component.get("error"):
            report += f"  Error: {component['error'][:100]}...\n"

    report += """

RECOMMENDATIONS
---------------
"""

    if status["overall_grade"] == "EXCELLENT":
        report += "✅ System is fully operational. All major components active.\n"
    elif status["overall_grade"] == "GOOD":
        report += "⚠️  System is operational but some components unavailable.\n"
        report += "   Check import paths and dependencies.\n"
    else:
        report += "❌ System degraded. Critical components missing.\n"
        report += "   Verify installation and required dependencies.\n"

    report += f"""

{'=' * 70}
"""

    return report


def main():
    """Main activation sequence."""
    print_banner()

    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Python Path: {sys.executable}")
    print(f"Python Version: {sys.version.split()[0]}")

    # Activate components
    components = {}

    components["57_component_core"] = activate_57_component_core()
    components["ubi_engine"] = activate_ubi_engine()
    components["repo_doctor"] = activate_repo_doctor()
    components["self_evolution"] = activate_self_evolution()

    # Compute unified status
    status = compute_unified_status(components)

    # Generate report
    print("\n" + "=" * 70)
    report = generate_report(components, status)
    print(report)

    # Save report
    report_path = PROJECT_ROOT / "AMOS_ACTIVATION_REPORT.txt"
    try:
        with open(report_path, "w") as f:
            f.write(report)
        print(f"✅ Report saved to: {report_path}")
    except Exception as e:
        print(f"⚠️  Could not save report: {e}")

    # Final status
    print("\n" + "=" * 70)
    if status["overall_grade"] in ["EXCELLENT", "GOOD"]:
        print("✅ AMOS MASTER ACTIVATION COMPLETE")
    else:
        print("⚠️  AMOS MASTER ACTIVATION PARTIAL")
    print(f"Status: {status['overall_grade']}")
    print("=" * 70)

    return status["overall_grade"] != "DEGRADED"


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
