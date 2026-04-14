#!/usr/bin/env python3
"""AMOS Ecosystem v2.0 - CLI Entry Point."""

import argparse
import sys

from .master_orchestrator import MasterOrchestrator
from .system_validator import validate_system


def main():
    """Main CLI entry point for AMOS Ecosystem."""
    parser = argparse.ArgumentParser(description="AMOS Ecosystem v2.0 - Cognitive Architecture")
    parser.add_argument("--version", "-v", action="version", version="AMOS Ecosystem v2.0")
    parser.add_argument("--validate", action="store_true", help="Run system validation")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--orchestrate", metavar="TASK", help="Run master orchestrator on a task")

    args = parser.parse_args()

    if args.validate:
        success, summary = validate_system()
        passed = summary["passed"]
        total = summary["total"]
        rate = summary["pass_rate"]
        print(f"\nValidation: {passed}/{total} passed")
        print(f"Health: {rate:.0f}%")
        return 0 if success else 1

    if args.status:
        from .system_status import SystemStatus

        status = SystemStatus()
        info = status.get_full_status()
        print("\nAMOS Ecosystem v2.0 - System Status")
        print("=" * 50)
        print(f"Cognitive Mode: {info.get('cognitive_mode', 'unknown')}")
        print(f"Modules: {info.get('modules_loaded', 0)} loaded")
        print(f"Health: {info.get('health', 'unknown')}")
        return 0

    if args.orchestrate:
        orchestrator = MasterOrchestrator()
        result = orchestrator.orchestrate_cognitive_task("cli_task", args.orchestrate, "MEDIUM")
        duration = result.predicted_duration_mins
        status = result.execution_result.get("status", "unknown")
        print("\nOrchestration Result:")
        print(f"  Success: {result.success}")
        print(f"  Predicted Duration: {duration} min")
        print(f"  Execution: {status}")
        return 0 if result.success else 1

    # Default: show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
