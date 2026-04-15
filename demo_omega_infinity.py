#!/usr/bin/env python3
"""Repo Doctor Ω∞ - Live Demo

Demonstrates the maximum-strength repository mechanics engine
on a real repository with detailed output.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add repo_doctor to path
sys.path.insert(0, str(Path(__file__).parent))


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


def print_subsection(title: str) -> None:
    """Print a subsection header."""
    print()
    print(f"▶ {title}")
    print("-" * 50)


def demo_state_vector(doctor) -> None:
    """Demonstrate state vector computation."""
    print_subsection("Repository State Vector |Ψ_repo⟩")

    report = doctor.scan()
    d = report.to_dict()

    print(f"\nEnergy: {d['energy']:.2f}")
    print(f"Status: {'✅ HEALTHY' if d['repo_valid'] else '❌ FAILING'}")
    print()

    print("12-Dimensional State:")
    print(f"{'Dimension':<20} {'Amplitude':<10} {'Status':<10} {'Weight':<10}")
    print("-" * 55)

    for dim, amp in sorted(d["state_vector"].items()):
        status = "✅" if amp > 0.9 else "⚠️ " if amp > 0.5 else "❌"
        weight = doctor.state_vector.WEIGHTS.get(doctor._get_dimension_from_string(dim), 0)
        print(f"{dim:<20} {amp:<10.2f} {status:<10} {weight:<10.0f}")

    if d["critical_dimensions"]:
        print(f"\n🔴 Critical Dimensions: {', '.join(d['critical_dimensions'])}")


def demo_invariants(doctor) -> None:
    """Demonstrate hard invariant checking."""
    print_subsection("12 Hard Invariants RepoValid = ∧n I_n")

    checker = doctor.checker
    results = checker.check_all()

    print(f"\n{'Invariant':<15} {'Status':<10} {'Severity':<12} {'Message'}")
    print("-" * 70)

    for r in results:
        status = "✅ PASS" if r.passed else "❌ FAIL"
        print(f"{r.name:<15} {status:<10} {r.severity:<12} {r.message[:35]}")

    failing = [r for r in results if not r.passed]
    print(f"\nResult: {len(failing)}/12 invariants failing")

    if failing:
        print("\n⚠️  Repository is NOT valid. Repairs required.")
    else:
        print("\n✅ All invariants pass. Repository is valid.")


def demo_entanglement(doctor) -> None:
    """Demonstrate entanglement analysis."""
    print_subsection("Module Entanglement Analysis")

    if not doctor.graph.nodes:
        print("No modules to analyze.")
        return

    # Pick first few modules
    modules = list(doctor.graph.nodes.keys())[:3]

    for module in modules:
        entangled = doctor.compute_entanglement(module)

        if entangled:
            print(f"\n📦 {module}")
            print(f"  {'Connected Module':<30} {'Coupling':<10}")
            print(f"  {'-'*40}")
            for mod, coupling in entangled[:5]:  # Top 5
                bar = "█" * int(coupling * 10) + "░" * (10 - int(coupling * 10))
                print(f"  {mod:<30} {bar} {coupling:.2f}")
        else:
            print(f"\n📦 {module}: No entanglements detected")


def demo_temporal(doctor) -> None:
    """Demonstrate temporal analysis."""
    print_subsection("Temporal Mechanics")

    print("Computing drift analysis...")

    # Create mock temporal data
    from repo_doctor.omega_infinity import StateDimension, StateVector, TemporalState

    history = [
        TemporalState("commit_1", None, StateVector({StateDimension.SYNTAX: 1.0})),
        TemporalState("commit_2", None, StateVector({StateDimension.SYNTAX: 0.95})),
        TemporalState("commit_3", None, StateVector({StateDimension.SYNTAX: 0.90})),
    ]

    if len(history) >= 2:
        drift = doctor.temporal.compute_drift(history[0].state_vector, history[1].state_vector)
        print(f"\n📊 Drift between commits: {drift:.4f}")
        print(
            f"   Interpretation: {'Low' if drift < 0.1 else 'Medium' if drift < 0.3 else 'High'} temporal drift"
        )

    print("\n⏱️  First-bad-commit detection available via:")
    print("   repo-doctor bisect --invariant I_api")


def demo_repair_plan(doctor) -> None:
    """Demonstrate repair optimization."""
    print_subsection("Minimum Restoring Repair Set")

    repairs = doctor.get_repair_plan()

    if not repairs:
        print("No repairs needed - repository is valid!")
        return

    print(f"\n🛠️  Optimal Repair Order ({len(repairs)} actions):")
    print()
    print(f"{'#':<4} {'Target':<15} {'Cost':<8} {'Blast':<8} {'Risk':<8} {'Energy Δ'}")
    print("-" * 60)

    for i, r in enumerate(repairs[:10], 1):  # Show top 10
        print(
            f"{i:<4} {r.target:<15} {r.edit_cost:<8.0f} "
            f"{r.blast_radius:<8.0f} {r.entanglement_risk:<8.2f} "
            f"{r.energy_reduction:+.1f}"
        )

    total_energy = sum(r.energy_reduction for r in repairs)
    print(f"\n📈 Total Energy Reduction: {total_energy:.1f}")


def demo_z3_integration(doctor) -> None:
    """Demonstrate Z3 SMT solver."""
    print_subsection("Z3 SMT Solver Integration")

    from repo_doctor.solver.z3_model import Z3Model

    z3 = Z3Model()

    if not z3.is_available():
        print("⚠️  Z3 not installed. Install with: pip install z3-solver")
        return

    print("✅ Z3 solver available with core minimization enabled")
    print("   Settings: smt.core.minimize=true")
    print()

    # Test invariant verification
    repo_state = {
        "entrypoints": ["cli", "server", "worker"],
        "modules": ["main", "api", "core"],
        "initialized": True,
        "specs_count": 15,
    }

    print("Testing invariant proofs:")
    for inv_type in ["entrypoint", "status"]:
        result = z3.prove_invariant(inv_type, repo_state)
        status = "✅ SAT" if result.satisfiable else "❌ UNSAT"
        print(f"  {inv_type:<15}: {status} ({result.proof_time_ms:.1f} ms)")


def demo_fleet_analysis() -> None:
    """Demonstrate fleet-level analysis."""
    print_subsection("Fleet-Level Analysis")

    from repo_doctor.omega_infinity import FleetState, StateDimension, StateVector

    fleet = FleetState()

    # Add sample repositories
    for i in range(3):
        sv = StateVector()
        sv.amplitudes[StateDimension.API] = 0.8 - i * 0.2
        sv.amplitudes[StateDimension.SYNTAX] = 0.95
        fleet.add_repository(f"service-{i+1}", sv, weight=1.0 - i * 0.1)

    energy = fleet.compute_fleet_energy()

    print(f"\n🌐 Fleet Analysis ({len(fleet.repos)} repositories)")
    print(f"   Total Fleet Energy: {energy:.2f}")

    # Detect class defects
    defects = fleet.find_class_defects()
    if defects:
        print("\n⚠️  Class Defects Detected:")
        for inv, repos in defects.items():
            print(f"   {inv}: affects {len(repos)} repositories")
    else:
        print("\n✅ No class defects detected")


def demo_output_formats(doctor) -> None:
    """Demonstrate output formats."""
    print_subsection("Output Formats")

    report = doctor.scan()

    print("📄 Available Output Formats:")
    print("   1. JSON (structured data)")
    print("   2. Markdown (human-readable)")
    print("   3. SARIF (CI/CD integration)")
    print()

    # Show JSON preview
    d = report.to_dict()
    json_preview = json.dumps(
        {
            "repository": d["repository"],
            "energy": d["energy"],
            "valid": d["repo_valid"],
            "failing_invariants": len(d["hard_invariant_failures"]),
        },
        indent=2,
    )
    print("JSON Preview:")
    print(json_preview)


def main() -> int:
    """Run the demo."""
    print_section("REPO DOCTOR Ω∞ - MAXIMUM STRENGTH REPOSITORY MECHANICS ENGINE")

    print("Initializing on current repository...")
    print()

    from repo_doctor.omega_infinity import RepoDoctorOmegaInfinity

    try:
        doctor = RepoDoctorOmegaInfinity(Path("."))

        print("✅ Engine initialized")
        print(f"   Repository: {doctor.repo_path}")
        print(f"   Graph Nodes: {len(doctor.graph.nodes)}")
        print(f"   Graph Edges: {len(doctor.graph.edges)}")

        # Run all demos
        demo_state_vector(doctor)
        demo_invariants(doctor)
        demo_entanglement(doctor)
        demo_temporal(doctor)
        demo_repair_plan(doctor)
        demo_z3_integration(doctor)
        demo_fleet_analysis()
        demo_output_formats(doctor)

        print_section("DEMO COMPLETE")

        print("📚 Next Steps:")
        print("   1. Run full scan: python -m repo_doctor.omega_infinity scan")
        print("   2. Check invariants: python -m repo_doctor.omega_infinity invariants")
        print("   3. Get repair plan: python -m repo_doctor.omega_infinity repair-plan")
        print()
        print("📖 Documentation:")
        print("   - REPO_DOCTOR_OMEGA_DESIGN_DOCUMENT.md")
        print("   - REPO_DOCTOR_OMEGA_INFINITY_IMPLEMENTATION.md")
        print("   - REPO_DOCTOR_OMEGA_INFINITY_COMPLETE.md")
        print()
        print("Ω∞ Engine Operational")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
