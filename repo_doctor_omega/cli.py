from __future__ import annotations

"""Repo Doctor Ω∞∞∞ - Command Line Interface.

Commands:
    scan        - Compute state vector and evaluate invariants
    contracts   - Compare public API claims vs runtime reality
    state       - Print amplitudes, energy, and collapsed subsystems
    drift       - Show per-commit drift and first-bad commits
    bisect      - Run invariant oracle under git bisect
    repair-plan - Emit minimum restoring repair set
    fleet       - Multi-repo analysis and batch remediation

Examples:
    repo-doctor scan
    repo-doctor contracts --strict
    repo-doctor state --format json
    repo-doctor drift --since v14.0.0
    repo-doctor repair-plan --output markdown
"""

import argparse
import json
import sys

from .engine import RepoDoctorEngine
from .state.basis import BasisVector


def cmd_scan(args: argparse.Namespace) -> int:
    """Run full repository scan."""
    engine = RepoDoctorEngine(args.repo_path)
    state = engine.compute_state()

    # Evaluate all hard invariants
    results = engine.evaluate_invariants()

    # Compute repository energy
    energy = state.compute_energy()

    # Check releaseability
    releaseable = state.is_releaseable(args.threshold)

    # Get failed invariants
    failed = [r for r in results if not r.passed]

    if args.format == "json":
        output = {
            "state": state.to_dict(),
            "energy": energy,
            "releaseable": releaseable,
            "invariants": [
                {
                    "name": r.invariant,
                    "passed": r.passed,
                    "severity": r.severity,
                    "violations": len(r.violations),
                }
                for r in results
            ],
            "failed_invariants": [r.invariant for r in failed],
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        print(f"\nRepository: {args.repo_path}")
        print(f"Energy: {energy:.2f}")
        print(f"Releaseable: {'YES' if releaseable else 'NO'}")

        print("\nState Vector:")
        for basis in BasisVector:
            amp = state.get_amplitude(basis)
            status = "✓" if amp > 0.8 else "⚠" if amp > 0.5 else "✗"
            print(f"  {status} {basis.name:15} = {amp:.2f}")

        if failed:
            print(f"\nFailed Invariants ({len(failed)}):")
            for r in failed:
                print(f"  ✗ {r.invariant} (severity: {r.severity:.2f})")
                for v in r.violations[:3]:
                    print(f"    - {v.message}")
        else:
            print("\n✓ All invariants passed")

    return 0 if releaseable else 1


def cmd_contracts(args: argparse.Namespace) -> int:
    """Check API contract commutativity."""
    engine = RepoDoctorEngine(args.repo_path)

    # Compare documented vs actual API
    contract_results = engine.check_contracts(strict=args.strict)

    if args.format == "json":
        print(json.dumps([r.to_dict() for r in contract_results], indent=2))
    else:
        print("\nAPI Contract Analysis:")
        print(f"Issues found: {len(contract_results)}")

        for issue in contract_results[:10]:
            print(f"\n  [{issue.kind.name}] {issue.severity:.2f}")
            print(f"    {issue.message}")
            if issue.file:
                print(f"    at {issue.file}:{issue.line}")

    return 0 if not contract_results else 1


def cmd_state(args: argparse.Namespace) -> int:
    """Print detailed state information."""
    engine = RepoDoctorEngine(args.repo_path)
    state = engine.compute_state()

    if args.format == "json":
        print(json.dumps(state.to_dict(), indent=2))
    else:
        print("\nRepository State:")
        print(f"  Timestamp: {state.timestamp}")
        print(f"  Energy: {state.compute_energy():.2f}")
        print(f"  Releaseable: {state.is_releaseable()}")

        collapsed = state.collapsed_subsystems()
        if collapsed:
            print(f"\n  Collapsed Subsystems ({len(collapsed)}):")
            for b in collapsed:
                print(f"    ✗ {b.name}")

    return 0


def cmd_drift(args: argparse.Namespace) -> int:
    """Analyze temporal drift."""
    engine = RepoDoctorEngine(args.repo_path)

    # Compute drift from reference
    drift_results = engine.compute_drift(since=args.since)

    if args.format == "json":
        print(json.dumps(drift_results, indent=2))
    else:
        print(f"\nTemporal Drift Analysis (since {args.since}):")
        print(f"  Total drift: {drift_results.get('total_drift', 0):.4f}")

        if "per_basis" in drift_results:
            print("\n  Per-basis drift:")
            for basis, delta in drift_results["per_basis"].items():
                if abs(delta) > 0.1:
                    print(f"    {basis}: {delta:+.4f}")

    return 0


def cmd_repair_plan(args: argparse.Namespace) -> int:
    """Generate repair plan."""
    engine = RepoDoctorEngine(args.repo_path)

    # Compute optimal repair set
    plan = engine.compute_repair_plan()

    if args.format == "json":
        print(json.dumps(plan, indent=2))
    elif args.output == "markdown":
        print("\n# Repository Repair Plan\n")
        print(f"**Energy**: {plan.get('energy', 0):.2f}\n")
        print("## Repair Order\n")
        for i, step in enumerate(plan.get("steps", []), 1):
            print(f"{i}. **{step['invariant']}**")
            print(f"   - Cost: {step.get('cost', 'medium')}")
            print(f"   - Blast radius: {step.get('blast_radius', 'unknown')}")
            print(f"   - {step.get('description', 'No description')}\n")
    else:
        print("\nRepair Plan:")
        print(f"  Estimated energy reduction: {plan.get('energy_reduction', 0):.2f}")
        print(f"  Steps: {len(plan.get('steps', []))}")

    return 0


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="repo-doctor",
        description="Repo Doctor Ω∞∞∞ - Repository Verification System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--repo-path",
        default=".",
        help="Path to repository (default: current directory)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # scan command
    scan_parser = subparsers.add_parser("scan", help="Run full repository scan")
    scan_parser.add_argument(
        "--threshold",
        type=float,
        default=10.0,
        help="Energy threshold for releaseability",
    )
    scan_parser.set_defaults(func=cmd_scan)

    # contracts command
    contracts_parser = subparsers.add_parser("contracts", help="Check API contracts")
    contracts_parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode - flag all discrepancies",
    )
    contracts_parser.set_defaults(func=cmd_contracts)

    # state command
    state_parser = subparsers.add_parser("state", help="Print state vector")
    state_parser.set_defaults(func=cmd_state)

    # drift command
    drift_parser = subparsers.add_parser("drift", help="Analyze temporal drift")
    drift_parser.add_argument(
        "--since",
        default="HEAD~10",
        help="Reference commit for drift analysis",
    )
    drift_parser.set_defaults(func=cmd_drift)

    # repair-plan command
    repair_parser = subparsers.add_parser("repair-plan", help="Generate repair plan")
    repair_parser.add_argument(
        "--output",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format",
    )
    repair_parser.set_defaults(func=cmd_repair_plan)

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
