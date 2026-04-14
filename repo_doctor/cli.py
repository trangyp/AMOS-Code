"""
CLI Module - Command Line Interface for Repo Doctor

Commands:
- repo-doctor scan      : Full repository scan
- repo-doctor contracts : Check API contracts
- repo-doctor bisect    : Find first bad commit
- repo-doctor fix-plan  : Generate repair plan
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Handle both module execution and direct script execution
try:
    # Try relative imports first (when run as module: python3 -m repo_doctor.cli)
    from .bisect_engine import BisectEngine
    from .contracts import ContractAnalyzer
    from .entanglement import EntanglementMatrix
    from .entrypoints import EntrypointAnalyzer
    from .invariants_legacy import InvariantEngine
    from .packaging import PackagingAnalyzer
    from .repair_plan import AutoFixRunner, RepairPlanner
    from .sensors import SensorSuite
    from .state_vector import format_state_report
except ImportError:
    # Fall back to absolute imports (when run directly: python3 repo_doctor/cli.py)
    # Add parent directory to path for imports
    cli_dir = Path(__file__).parent
    if str(cli_dir) not in sys.path:
        sys.path.insert(0, str(cli_dir))
    if str(cli_dir.parent) not in sys.path:
        sys.path.insert(0, str(cli_dir.parent))

    from bisect_engine import BisectEngine
    from contracts import ContractAnalyzer
    from entanglement import EntanglementMatrix
    from entrypoints import EntrypointAnalyzer
    from invariants_legacy import InvariantEngine
    from packaging import PackagingAnalyzer
    from repair_plan import AutoFixRunner, RepairPlanner
    from sensors import SensorSuite
    from state_vector import format_state_report


def cmd_scan(args: argparse.Namespace) -> int:
    """Run full repository scan."""
    repo_path = Path(args.path).resolve()

    print(f"Scanning repository: {repo_path}")
    print()

    # Run invariants
    engine = InvariantEngine(repo_path)
    state, results = engine.run_all()

    # Print state vector report
    print(format_state_report(state))
    print()

    # Additional analyses
    if args.contracts:
        print("Running contract analysis...")
        analyzer = ContractAnalyzer(repo_path)
        violations = analyzer.analyze()
        print(analyzer.get_report())
        print()

    if args.packaging:
        print("Running packaging analysis...")
        pkg_analyzer = PackagingAnalyzer(repo_path)
        pkg_analyzer.analyze()
        print(pkg_analyzer.get_report())
        print()

    if args.entanglement:
        print("Running entanglement analysis...")
        matrix = EntanglementMatrix(repo_path)
        edges = matrix.analyze()
        print(matrix.get_report())
        print()

    if args.sensors:
        print("Running external tool sensors...")
        suite = SensorSuite(repo_path)
        sensor_results = suite.run_all()
        print(suite.get_report(sensor_results))
        print()

    if args.fix:
        print("Running auto-fixes...")
        fixer = AutoFixRunner(repo_path)
        fix_results = fixer.run_all(dry_run=args.dry_run)
        print(fixer.get_report())
        print()

    # Output JSON if requested
    if args.json:
        output = {
            "state": state.to_dict(),
            "invariant_results": [
                {
                    "name": r.dimension.value,
                    "passed": r.passed,
                    "message": r.message,
                    "details": r.details,
                }
                for r in results
            ],
        }

        if args.output:
            Path(args.output).write_text(json.dumps(output, indent=2))
        else:
            print(json.dumps(output, indent=2))

    # Return exit code based on releaseability
    releaseable, _ = state.is_releaseable()
    return 0 if releaseable else 1


def cmd_contracts(args: argparse.Namespace) -> int:
    """Check API contracts."""
    repo_path = Path(args.path).resolve()

    print(f"Checking API contracts in: {repo_path}")
    print()

    analyzer = ContractAnalyzer(repo_path)
    violations = analyzer.analyze()

    print(analyzer.get_report())

    # Also run entrypoint checks
    entry_analyzer = EntrypointAnalyzer(repo_path)
    entry_issues = entry_analyzer.analyze()

    print()
    print(entry_analyzer.get_report())

    return 0 if not violations and not entry_issues else 1


def cmd_bisect(args: argparse.Namespace) -> int:
    """Find first bad commit for an invariant."""
    repo_path = Path(args.path).resolve()

    print(f"Bisecting repository: {repo_path}")
    print(f"Looking for first bad commit for invariant: {args.invariant}")

    if not args.good or not args.bad:
        # Auto-detect regression range
        print("Auto-detecting regression range...")
        engine = BisectEngine(repo_path)
        range_result = engine.find_regression_range(args.invariant, lookback_commits=20)

        if not range_result:
            print("Could not detect regression range")
            return 1

        args.good, args.bad = range_result
        print(f"Detected range: good={args.good[:8]}, bad={args.bad[:8]}")

    engine = BisectEngine(repo_path)
    result = engine.bisect_invariant(args.invariant, args.good, args.bad)

    if result.success:
        print(f"\nFirst bad commit: {result.first_bad_commit}")
        print(f"Message: {result.first_bad_message}")
        print(f"Bisect steps: {result.steps}")
    else:
        print(f"\nBisect failed: {result.error}")
        return 1

    return 0


def cmd_fix_plan(args: argparse.Namespace) -> int:
    """Generate repair plan."""
    repo_path = Path(args.path).resolve()

    print(f"Generating repair plan for: {repo_path}")
    print()

    # Run invariants
    engine = InvariantEngine(repo_path)
    state, results = engine.run_all()

    # Generate plan
    planner = RepairPlanner(repo_path)
    plan = planner.generate_plan(state, results)

    print(planner.format_plan(plan))

    # Export script if requested
    if args.export:
        if planner.export_patch_script(plan, args.export):
            print(f"\nRepair script exported to: {args.export}")
        else:
            print("\nNo automated fixes available for export")

    return 0


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="repo-doctor", description="Deterministic repository diagnostic system"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Full repository scan")
    scan_parser.add_argument(
        "path", nargs="?", default=".", help="Repository path (default: current directory)"
    )
    scan_parser.add_argument("--contracts", action="store_true", help="Also check API contracts")
    scan_parser.add_argument("--packaging", action="store_true", help="Also check packaging")
    scan_parser.add_argument(
        "--entanglement", action="store_true", help="Also compute entanglement matrix"
    )
    scan_parser.add_argument(
        "--sensors",
        action="store_true",
        help="Also run external tool sensors (pip-audit, ruff, pyright, deptry)",
    )
    scan_parser.add_argument(
        "--fix", action="store_true", help="Apply auto-fixes for fixable issues"
    )
    scan_parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be fixed without making changes"
    )
    scan_parser.add_argument("--json", action="store_true", help="Output JSON")
    scan_parser.add_argument("-o", "--output", help="Output file for JSON")

    # Contracts command
    contracts_parser = subparsers.add_parser("contracts", help="Check API contracts")
    contracts_parser.add_argument("path", nargs="?", default=".", help="Repository path")

    # Bisect command
    bisect_parser = subparsers.add_parser("bisect", help="Find first bad commit")
    bisect_parser.add_argument(
        "invariant", help="Invariant name to check (e.g., parse, import, packaging)"
    )
    bisect_parser.add_argument("path", nargs="?", default=".", help="Repository path")
    bisect_parser.add_argument("--good", help="Last known good commit")
    bisect_parser.add_argument("--bad", help="Known bad commit")

    # Fix-plan command
    fix_parser = subparsers.add_parser("fix-plan", help="Generate repair plan")
    fix_parser.add_argument("path", nargs="?", default=".", help="Repository path")
    fix_parser.add_argument("--export", help="Export automated fixes to script file")

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    # Dispatch
    commands = {
        "scan": cmd_scan,
        "contracts": cmd_contracts,
        "bisect": cmd_bisect,
        "fix-plan": cmd_fix_plan,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args)

    return 1


if __name__ == "__main__":
    sys.exit(main())
