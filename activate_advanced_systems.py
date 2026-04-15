#!/usr/bin/env python3
"""
AMOS Advanced Systems Activator
================================

Activates discovered capabilities:
- Repo Doctor Omega (repository analysis)
- Self-Evolution Engine (self-improving codebase)
- Fleet Management (multi-repo coordination)
- Graph Analysis (entanglement computation)

Usage:
    python activate_advanced_systems.py [command]

Commands:
    scan      - Run full repository scan
    evolve    - Run self-evolution cycle
    status    - Show all system statuses
    repair    - Generate repair plan
"""

from __future__ import annotations

import sys
import json
from pathlib import Path
from datetime import datetime

# Add AMOS to path
AMOS_ROOT = Path(__file__).parent
sys.path.insert(0, str(AMOS_ROOT))


def print_banner():
    """Print activation banner."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║           AMOS ADVANCED SYSTEMS ACTIVATOR                        ║
║              Repo Doctor Ω • Self-Evolution                      ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)


def activate_repo_doctor():
    """Activate Repo Doctor Omega."""
    print("\n🔬 ACTIVATING: Repo Doctor Ω∞∞∞")
    print("-" * 60)
    
    try:
        from repo_doctor_omega.engine import RepoDoctorEngine
        
        engine = RepoDoctorEngine(str(AMOS_ROOT))
        
        print("  ✓ Engine initialized")
        print(f"  ✓ Repository: {AMOS_ROOT.name}")
        print(f"  ✓ Invariants: {len(engine.invariants)} registered")
        
        # Compute state
        print("\n  📊 Computing repository state...")
        state = engine.compute_state()
        
        print(f"    • Energy: {state.compute_energy():.3f}")
        print(f"    • Releaseable: {state.is_releaseable()}")
        print(f"    • Timestamp: {datetime.fromtimestamp(state.timestamp).isoformat()}")
        
        # Run invariant checks
        print("\n  🔍 Running invariant checks...")
        results = engine.evaluate_invariants()
        
        passed = sum(1 for r in results if r.passed)
        failed = sum(1 for r in results if not r.passed)
        
        print(f"    • Passed: {passed}/{len(results)}")
        print(f"    • Failed: {failed}/{len(results)}")
        
        if failed > 0:
            print("\n    ⚠ Failed invariants:")
            for result in results:
                if not result.passed:
                    print(f"      - {result.invariant} (severity: {result.severity:.2f})")
        
        # Generate repair plan
        print("\n  🔧 Computing repair plan...")
        plan = engine.compute_repair_plan()
        
        print(f"    • Current energy: {plan['energy']:.3f}")
        print(f"    • Estimated reduction: {plan['energy_reduction']:.3f}")
        print(f"    • Repair steps: {len(plan['steps'])}")
        print(f"    • Estimated time: {plan['estimated_time']} minutes")
        
        if plan['steps']:
            print("\n    📋 Repair order:")
            for i, step in enumerate(plan['steps'][:5], 1):
                print(f"      {i}. {step['invariant']}: {step['description']}")
        
        return {
            "status": "active",
            "energy": state.compute_energy(),
            "releaseable": state.is_releaseable(),
            "invariants_passed": passed,
            "invariants_failed": failed,
            "repair_steps": len(plan['steps'])
        }
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


def activate_self_evolution():
    """Activate Self-Evolution Engine."""
    print("\n🧬 ACTIVATING: Self-Evolution Engine")
    print("-" * 60)
    
    try:
        from repo_doctor.self_evolution.engine import SelfEvolutionEngine
        
        memory_path = "/tmp/amos_evolution_memory.json"
        audit_path = "/tmp/amos_evolution_audit.jsonl"
        
        engine = SelfEvolutionEngine(
            amos_root=str(AMOS_ROOT),
            memory_path=memory_path,
            audit_path=audit_path
        )
        
        print("  ✓ Engine initialized")
        print(f"  ✓ Memory store: {memory_path}")
        print(f"  ✓ Audit trail: {audit_path}")
        
        # Get status
        print("\n  📊 Current status...")
        status = engine.get_status()
        
        print(f"    • Active contracts: {status['active_contracts']}")
        print(f"    • Completed evolutions: {status['completed_evolutions']}")
        print(f"    • Rolled back: {status['rolled_back']}")
        print(f"    • Success rate: {status['success_rate']:.1%}")
        print(f"    • Learned patterns: {status['learned_patterns']}")
        print(f"    • Total memories: {status['total_memories']}")
        print(f"    • Can evolve: {status['can_evolve']}")
        
        # Run one evolution cycle
        print("\n  🔄 Running evolution cycle...")
        report = engine.evolve(max_evolutions=1)
        
        print(f"    • Hotspots detected: {report.hotspots_detected}")
        print(f"    • Contracts created: {report.contracts_created}")
        print(f"    • Patches planned: {report.patches_planned}")
        print(f"    • Patches applied: {report.patches_applied}")
        print(f"    • Patches rolled back: {report.patches_rolled_back}")
        print(f"    • Success rate: {report.success_rate:.1%}")
        print(f"    • Learned patterns: {report.learned_patterns}")
        
        if report.details:
            print("\n    📋 Evolution details:")
            for detail in report.details:
                print(f"      • {detail['evolution_id']}: {detail['status']}")
        
        return {
            "status": "active",
            "hotspots": report.hotspots_detected,
            "contracts": report.contracts_created,
            "patches": report.patches_applied,
            "success_rate": report.success_rate,
            "learned": report.learned_patterns
        }
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


def show_all_statuses():
    """Show status of all advanced systems."""
    print("\n📊 ADVANCED SYSTEMS STATUS")
    print("=" * 60)
    
    systems = {}
    
    # Repo Doctor Omega
    print("\n🔬 Repo Doctor Ω∞∞∞:")
    try:
        from repo_doctor_omega.engine import RepoDoctorEngine
        engine = RepoDoctorEngine(str(AMOS_ROOT))
        state = engine.compute_state()
        print(f"  Status: ✅ ACTIVE")
        print(f"  Energy: {state.compute_energy():.3f}")
        print(f"  Releaseable: {state.is_releaseable()}")
        systems["repo_doctor"] = "active"
    except Exception as e:
        print(f"  Status: ❌ ERROR - {e}")
        systems["repo_doctor"] = "error"
    
    # Self-Evolution
    print("\n🧬 Self-Evolution Engine:")
    try:
        from repo_doctor.self_evolution.engine import SelfEvolutionEngine
        engine = SelfEvolutionEngine(str(AMOS_ROOT))
        status = engine.get_status()
        print(f"  Status: ✅ ACTIVE")
        print(f"  Can evolve: {status['can_evolve']}")
        print(f"  Success rate: {status['success_rate']:.1%}")
        print(f"  Learned patterns: {status['learned_patterns']}")
        systems["self_evolution"] = "active"
    except Exception as e:
        print(f"  Status: ❌ ERROR - {e}")
        systems["self_evolution"] = "error"
    
    # Brain UI
    print("\n🧠 Brain UI:")
    import urllib.request
    try:
        with urllib.request.urlopen("http://localhost:9000/api/status", timeout=2) as resp:
            data = json.loads(resp.read())
            print(f"  Status: ✅ ACTIVE (Port 9000)")
            print(f"  Session: {data.get('brain', {}).get('session_id', 'N/A')[:8]}")
            systems["brain_ui"] = "active"
    except:
        print(f"  Status: ⚪ NOT RUNNING")
        systems["brain_ui"] = "inactive"
    
    print("\n" + "=" * 60)
    print("Summary:")
    for name, status in systems.items():
        icon = "✅" if status == "active" else "❌" if status == "error" else "⚪"
        print(f"  {icon} {name}: {status}")
    
    return systems


def generate_repair_plan():
    """Generate and display repair plan."""
    print("\n🔧 GENERATING REPAIR PLAN")
    print("=" * 60)
    
    try:
        from repo_doctor_omega.engine import RepoDoctorEngine
        
        engine = RepoDoctorEngine(str(AMOS_ROOT))
        plan = engine.compute_repair_plan()
        
        print(f"\nCurrent Energy: {plan['energy']:.3f}")
        print(f"Estimated Reduction: {plan['energy_reduction']:.3f}")
        print(f"Final Energy: {plan['energy'] - plan['energy_reduction']:.3f}")
        print(f"\nRepair Steps ({len(plan['steps'])} total):")
        
        for i, step in enumerate(plan['steps'], 1):
            print(f"\n  {i}. Restore {step['invariant']} Integrity")
            print(f"     Description: {step['description']}")
            print(f"     Cost: {step['cost']}")
            print(f"     Blast Radius: {step['blast_radius']}")
        
        print(f"\nEstimated Time: {plan['estimated_time']} minutes")
        
        return plan
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point."""
    print_banner()
    
    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if command == "scan":
        result = activate_repo_doctor()
        print("\n" + "=" * 60)
        print("SCAN COMPLETE")
        print("=" * 60)
        print(json.dumps(result, indent=2, default=str))
        
    elif command == "evolve":
        result = activate_self_evolution()
        print("\n" + "=" * 60)
        print("EVOLUTION COMPLETE")
        print("=" * 60)
        print(json.dumps(result, indent=2, default=str))
        
    elif command == "status":
        show_all_statuses()
        
    elif command == "repair":
        generate_repair_plan()
        
    else:
        print(f"\n❌ Unknown command: {command}")
        print("\nAvailable commands:")
        print("  scan      - Run repository scan")
        print("  evolve    - Run self-evolution")
        print("  status    - Show all statuses")
        print("  repair    - Generate repair plan")
        return 1
    
    print("\n✅ ACTIVATION COMPLETE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
