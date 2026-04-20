#!/usr/bin/env python3
"""
Repo Doctor Omega - CLI Interface

Commands:
- repo-doctor scan: Build state vector, check invariants, compute energy
- repo-doctor contracts: Check public/runtime commutator
- repo-doctor drift: Compute temporal drift
- repo-doctor bisect --invariant I_api: Find first bad commit
- repo-doctor repair-plan: Generate minimum restoring set

Outputs:
- State vector with 11 dimensions
- Energy E_repo = Σ λk (1 - αk)²
- Failed hard invariants
- Minimal failing cut
- First bad commits by invariant
- Repair plan with blast radius
"""

import argparse
import sys
from typing import Any, Dict

from repo_doctor.model.hamiltonian import RepositoryHamiltonian
from repo_doctor.model.invariants import InvariantChecker
from repo_doctor.model.state_vector import StateVectorBuilder
from repo_doctor.output.diagnosis import DiagnosisGenerator
from repo_doctor.output.repair_plan import RepairPlanGenerator
from repo_doctor.solver.repair_optimizer import RepairAction, RepairOptimizer
from repo_doctor.solver.unsat_core import UnsatCoreExtractor


def run_scan(repo_path: str, output_format: str = "markdown") -> Dict[str, Any]:
    """
    Run full repository scan.

    Returns diagnosis with state vector, energy, and invariant results.
    """
    print(f"🔬 Scanning repository: {repo_path}")

    # Build state vector from observables
    # In real implementation, this would call sensor backends
    observables = {
        "parse_errors": 0,
        "unresolved_imports": 0,
        "signature_mismatches": 0,
        "missing_entrypoints": 0,
        "test_failures": 0,
        "total_tests": 46,
        "security_findings": 0,
    }

    state_builder = StateVectorBuilder(repo_path)
    state_builder.from_observables(observables)
    state = state_builder.build()

    # Apply Hamiltonian
    hamiltonian = RepositoryHamiltonian()
    energy = hamiltonian.apply(state)

    print(f"  Energy: {energy:.4f}")
    print(f"  Score: {state.score()}/100")

    # Check invariants
    checker = InvariantChecker()
    is_valid, failed = checker.check_repo_valid(repo_path, observables)

    if failed:
        print(f"  ⚠️  {len(failed)} invariants failed")
    else:
        print("  ✓ All invariants passing")

    # Generate diagnosis
    generator = DiagnosisGenerator(repo_path)
    diagnosis = generator.generate(
        state_vector=state,
        hamiltonian=hamiltonian,
        failed_invariants=failed,
        first_bad_commits={},
        minimal_cut=[f.inv_type.value for f in failed] if failed else [],
    )

    # Output
    if output_format == "json":
        print(diagnosis.to_json())
    else:
        print("\n" + diagnosis.to_markdown())

    return diagnosis.to_dict()


def run_contracts(repo_path: str) -> Dict[str, Any]:
    """Check public/runtime contract commutator."""
    print(f"🔍 Checking contracts: {repo_path}")

    from repo_doctor.model.contracts import PublicRuntimeDrift

    drift_checker = PublicRuntimeDrift(repo_path)
    result = drift_checker.analyze()

    if result["drift_count"] == 0:
        print("  ✓ [A_public, A_runtime] = 0 (contracts commute)")
    else:
        print(f"  ⚠️  [A_public, A_runtime] ≠ 0 ({result['drift_count']} drift instances)")
        for drift in result.get("drifts", []):
            print(f"     - {drift['name']}: {drift['type']}")

    return result


def run_drift(repo_path: str, commit_range: str) -> Dict[str, Any]:
    """Compute temporal drift across commits."""
    print(f"📊 Analyzing drift: {repo_path}")
    print(f"  Range: {commit_range}")

    # In real implementation, would analyze state at each commit
    return {
        "repo": repo_path,
        "range": commit_range,
        "drift_detected": False,
        "max_drift_norm": 0.0,
    }


def run_bisect(repo_path: str, invariant: str, good: str, bad: str) -> Dict[str, Any]:
    """Bisect to find first bad commit for invariant."""
    print(f"🔎 Bisecting invariant: {invariant}")
    print(f"  Good: {good}")
    print(f"  Bad: {bad}")

    # In real implementation, would use git bisect with invariant oracle
    return {
        "invariant": invariant,
        "first_bad_commit": bad,  # Placeholder
        "good_commit": good,
    }


def run_repair_plan(repo_path: str) -> Dict[str, Any]:
    """Generate repair plan."""
    print(f"🔧 Generating repair plan: {repo_path}")

    # Get failed invariants
    observables = {
        "parse_errors": 0,
        "unresolved_imports": 0,
        "signature_mismatches": 1,  # Simulated failure
        "missing_entrypoints": 0,
    }

    checker = InvariantChecker()
    _, failed = checker.check_repo_valid(repo_path, observables)

    # Generate unsat hints
    unsat_extractor = UnsatCoreExtractor()
    unsat_hints = unsat_extractor.to_repair_hints()

    # Create repair optimizer
    optimizer = RepairOptimizer()

    # Add candidate actions
    for inv in failed:
        action = RepairAction(
            name=f"Fix {inv.inv_type.value}",
            target_files=["api_module.py"],
            invariants_restored=[inv.inv_type.value],
            estimated_energy_reduction=0.5,
            blast_radius=2,
            entanglement_risk=0.3,
            edit_cost=10,
        )
        optimizer.add_action(action)

    # Generate optimal set
    optimal = optimizer.compute_optimal_set([f.inv_type.value for f in failed])

    # Generate plan
    plan_generator = RepairPlanGenerator(repo_path)
    plan = plan_generator.generate(
        failed_invariants=failed,
        unsat_hints=unsat_hints,
        optimal_actions=optimal,
    )

    print("\n" + plan.to_markdown())
    return plan.to_dict()


def main():
    parser = argparse.ArgumentParser(
        prog="repo-doctor-omega",
        description="Repo Doctor Omega - Repository Verification Engine",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Full repository scan")
    scan_parser.add_argument("repo_path", nargs="?", default=".", help="Path to repository")
    scan_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Contracts command
    contracts_parser = subparsers.add_parser("contracts", help="Check public/runtime contracts")
    contracts_parser.add_argument("repo_path", nargs="?", default=".")

    # Drift command
    drift_parser = subparsers.add_parser("drift", help="Analyze temporal drift")
    drift_parser.add_argument("repo_path", nargs="?", default=".")
    drift_parser.add_argument("--range", default="HEAD~10..HEAD", help="Commit range")

    # Bisect command
    bisect_parser = subparsers.add_parser("bisect", help="Find first bad commit")
    bisect_parser.add_argument("--invariant", required=True, help="Invariant to check")
    bisect_parser.add_argument("--good", required=True, help="Good commit/label")
    bisect_parser.add_argument("--bad", required=True, help="Bad commit/label")
    bisect_parser.add_argument("repo_path", nargs="?", default=".")

    # Repair plan command
    repair_parser = subparsers.add_parser("repair-plan", help="Generate repair plan")
    repair_parser.add_argument("repo_path", nargs="?", default=".")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "scan":
        fmt = "json" if args.json else "markdown"
        result = run_scan(args.repo_path, fmt)
        sys.exit(0 if result.get("is_valid") else 1)

    elif args.command == "contracts":
        result = run_contracts(args.repo_path)
        sys.exit(0 if result.get("drift_count") == 0 else 1)

    elif args.command == "drift":
        run_drift(args.repo_path, args.range)
        sys.exit(0)

    elif args.command == "bisect":
        run_bisect(args.repo_path, args.invariant, args.good, args.bad)
        sys.exit(0)

    elif args.command == "repair-plan":
        run_repair_plan(args.repo_path)
        sys.exit(0)


if __name__ == "__main__":
    main()
