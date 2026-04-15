#!/usr/bin/env python3
"""Repair planning example - generates optimized repair plan."""

from repo_doctor_omega.engine import RepoDoctorEngine
from repo_doctor_omega.solver import RepairOptimizer


def main():
    """Generate and display repair plan."""
    print("=" * 60)
    print("REPAIR PLANNING EXAMPLE")
    print("=" * 60)

    # Initialize
    engine = RepoDoctorEngine(".")
    print(f"\nRepository: {engine.repo_path}")

    # Evaluate invariants
    results = engine.evaluate_invariants()
    failed = [r for r in results if not r.passed]

    if not failed:
        print("\n✓ All invariants passed - no repairs needed!")
        return 0

    print(f"\n⚠ {len(failed)} invariants failed:")
    for result in failed:
        print(f"  - {result.invariant}: {len(result.violations)} violations")

    # Collect all violations
    violations = []
    for result in failed:
        violations.extend(result.violations)

    print(f"\nTotal violations: {len(violations)}")

    # Generate repair plan
    print("\nGenerating optimized repair plan...")
    optimizer = RepairOptimizer()
    plan = optimizer.optimize_repairs(violations, str(engine.repo_path))

    # Display plan
    print(f"\n{'=' * 60}")
    print("REPAIR PLAN")
    print(f"{'=' * 60}")
    print(f"Total Cost: {plan.total_cost:.1f}")
    print(f"Total Blast Radius: {plan.total_blast_radius:.1f}")
    print(f"Expected Energy Drop: {plan.energy_drop:.1f}")
    print(f"Actions: {len(plan.actions)}")

    print("\nSequenced Actions:")
    for action in plan.actions:
        print(f"\n  {action.step}. {action.action}")
        print(f"     Target: {action.target}")
        print(f"     Description: {action.description}")
        print(f"     Cost: {action.cost:.1f} | Blast: {action.blast_radius:.1f}")

    if plan.risks:
        print("\n⚠ Risks:")
        for risk in plan.risks:
            print(f"  - {risk}")

    # Validate plan
    is_valid = optimizer.validate_plan(plan, violations)
    print(f"\nPlan Valid: {'YES' if is_valid else 'NO'}")

    return 0


if __name__ == "__main__":
    exit(main())
