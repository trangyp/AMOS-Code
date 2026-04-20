"""Kernel CLI - Command-line interface for AMOS kernel"""

import argparse
import sys
from typing import Optional

from .workflows import get_workflow_engine


def cmd_workflow(args: argparse.Namespace) -> int:
    """Execute a workflow."""
    engine = get_workflow_engine()

    # Build input from biological/environment flags
    def parse_values(s: str) -> dict:
        result = {}
        for item in s.split(","):
            k, v = item.split("=")
            try:
                result[k] = float(v)
            except ValueError:
                result[k] = v
        return result

    raw_input = {}
    if args.biological:
        raw_input["biological"] = parse_values(args.biological)
    if args.environment:
        raw_input["environment"] = parse_values(args.environment)
    if args.cognitive:
        raw_input["cognitive"] = parse_values(args.cognitive)
    if args.system:
        raw_input["system"] = parse_values(args.system)

    result = engine.execute(
        workflow_id=args.id or "cli-workflow",
        raw_input=raw_input,
        validate_laws=not args.skip_laws,
    )

    print(f"Workflow: {result.workflow_id}")
    print(f"Success: {result.success}")
    print(f"\nSteps ({len(result.steps)}):")
    for step in result.steps:
        status_icon = "✓" if step.status == "completed" else "✗"
        print(f"  {status_icon} {step.name}: {step.status}")

    if result.law_validation:
        print("\nLaw Validation:")
        print(f"  Passed: {result.law_validation.passed}")
        print(f"  Collapse Risk: {result.law_validation.collapse_risk:.2%}")

    print(f"\nDrift Detected: {result.drift_detected}")
    print(f"Repairs Proposed: {result.repairs_proposed}")

    return 0 if result.success else 1


def cmd_doctor(args: argparse.Namespace) -> int:
    """Run health check."""
    from .runtime.doctor import main as doctor_main

    return doctor_main()


def cmd_version(args: argparse.Namespace) -> int:
    """Show version."""
    from . import __version__

    print(f"AMOS Kernel {__version__}")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="amos-kernel",
        description="AMOS Kernel-First Architecture CLI",
    )
    subparsers = parser.add_subparsers(dest="command")

    # workflow command
    workflow_parser = subparsers.add_parser("workflow", help="Execute kernel workflow")
    workflow_parser.add_argument("--id", help="Workflow ID")
    workflow_parser.add_argument("--biological", help="Biological quadrant (key=value,key2=value2)")
    workflow_parser.add_argument("--cognitive", help="Cognitive quadrant (key=value,key2=value2)")
    workflow_parser.add_argument("--system", help="System quadrant (key=value,key2=value2)")
    workflow_parser.add_argument(
        "--environment", help="Environment quadrant (key=value,key2=value2)"
    )
    workflow_parser.add_argument("--skip-laws", action="store_true", help="Skip law validation")
    workflow_parser.set_defaults(func=cmd_workflow)

    # doctor command
    doctor_parser = subparsers.add_parser("doctor", help="Run health check")
    doctor_parser.set_defaults(func=cmd_doctor)

    # version command
    version_parser = subparsers.add_parser("version", help="Show version")
    version_parser.set_defaults(func=cmd_version)

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
