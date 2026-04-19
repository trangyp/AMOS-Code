#!/usr/bin/env python3
"""AXIOM One CLI - Command Line Interface

Unified entry point for AXIOM One Technical Operating System.
Supports all 3 operating modes with brain integration.

Author: AMOS System
Version: 3.0.0
"""

import argparse
import json
import sys
from pathlib import Path

from .brain_integration import BrainExecutionConfig, BrainPoweredOrchestrator
from .execution_slot import SlotMode
from .orchestrator import AxiomOne, OrchestratorConfig


def cmd_execute(args: argparse.Namespace) -> int:
    """Execute command handler."""
    mode_map = {
        "local": SlotMode.LOCAL,
        "managed": SlotMode.MANAGED,
        "orch": SlotMode.ORCHESTRATION,
    }

    if args.brain:
        # Use brain-powered orchestrator
        config = BrainExecutionConfig(
            repo_path=args.repo,
            enable_cognitive_planning=args.cognitive,
            enable_repo_doctor=args.verify,
        )
        orchestrator = BrainPoweredOrchestrator(config)
        slot = orchestrator.execute_intelligent(objective=args.objective, mode=mode_map[args.mode])
    else:
        # Use standard orchestrator
        config = OrchestratorConfig(
            repo_path=args.repo,
            mode=mode_map[args.mode],
        )
        axiom = AxiomOne(config)
        slot = axiom.execute(args.objective)

    # Output
    if args.json:
        output = {
            "slot_id": slot.slot_id,
            "status": slot.status.name,
            "mode": slot.mode.value,
            "events": len(slot.event_log),
            "verification_bundle": slot.verification_bundle,
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Slot ID: {slot.slot_id}")
        print(f"Status: {slot.status.name}")
        print(f"Mode: {slot.mode.value}")
        print(f"Events: {len(slot.event_log)}")
        if slot.verification_bundle:
            print(f"Receipt: {slot.verification_bundle.get('receipt_id', 'N/A')}")

    return 0 if slot.status.name in ("COMPLETED", "ALLOCATED") else 1


def cmd_status(args: argparse.Namespace) -> int:
    """Status command handler."""
    config = OrchestratorConfig(repo_path=args.repo)
    axiom = AxiomOne(config)
    status = axiom.get_status()

    if args.json:
        print(json.dumps(status, indent=2, default=str))
    else:
        print("AXIOM One Status")
        print("================")
        for key, value in status.items():
            print(f"{key}: {value}")

    return 0


def cmd_slot(args: argparse.Namespace) -> int:
    """Slot management command handler."""
    config = OrchestratorConfig(repo_path=args.repo)
    axiom = AxiomOne(config)

    if args.slot_command == "list":
        # This would list from persistent storage
        print("Active slots: (implementation needed)")
    elif args.slot_command == "show":
        if not args.slot_id:
            print("Error: --slot-id required", file=sys.stderr)
            return 1
        slot = axiom._active_slots.get(args.slot_id)
        if slot:
            print(json.dumps(slot.to_dict(), indent=2, default=str))
        else:
            print(f"Slot not found: {args.slot_id}", file=sys.stderr)
            return 1
    elif args.slot_command == "rollback":
        if not args.slot_id:
            print("Error: --slot-id required", file=sys.stderr)
            return 1
        success = axiom.rollback(args.slot_id)
        print(f"Rollback: {'success' if success else 'failed'}")

    return 0


def cmd_twin(args: argparse.Namespace) -> int:
    """Twin command handler."""
    from .twin import Twin

    twin = Twin(args.repo)

    if args.twin_command == "capture":
        state = twin.capture_state(args.label or "manual_capture")
        print(f"Captured state: {state.compute_signature()}")
        print(f"Files: {len(state.repo_graph.files)}")
    elif args.twin_command == "compare":
        if not args.state_a or not args.state_b:
            print("Error: --state-a and --state-b required", file=sys.stderr)
            return 1
        diff = twin.compare_states(args.state_a, args.state_b)
        print(json.dumps(diff, indent=2))
    elif args.twin_command == "replay":
        if not args.state_label:
            print("Error: --state-label required", file=sys.stderr)
            return 1
        state = twin.replay_failure(args.state_label)
        if state:
            print(f"Replaying state: {state.compute_signature()}")
        else:
            print(f"State not found: {args.state_label}", file=sys.stderr)
            return 1

    return 0


def main(argv: List[str] = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="axiom",
        description="AXIOM One - Technical Operating System",
    )
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository path")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Execute command
    exec_parser = subparsers.add_parser("execute", help="Execute objective")
    exec_parser.add_argument("objective", help="Task to execute")
    exec_parser.add_argument(
        "--mode", choices=["local", "managed", "orch"], default="local", help="Execution mode"
    )
    exec_parser.add_argument("--brain", action="store_true", help="Use brain-powered execution")
    exec_parser.add_argument("--cognitive", action="store_true", help="Enable cognitive planning")
    exec_parser.add_argument(
        "--verify", action="store_true", help="Enable repo_doctor verification"
    )

    # Status command
    subparsers.add_parser("status", help="Show system status")

    # Slot command
    slot_parser = subparsers.add_parser("slot", help="Slot management")
    slot_parser.add_argument("slot_command", choices=["list", "show", "rollback"])
    slot_parser.add_argument("--slot-id", help="Slot ID")

    # Twin command
    twin_parser = subparsers.add_parser("twin", help="Digital twin operations")
    twin_parser.add_argument("twin_command", choices=["capture", "compare", "replay"])
    twin_parser.add_argument("--label", help="State label")
    twin_parser.add_argument("--state-a", help="First state for comparison")
    twin_parser.add_argument("--state-b", help="Second state for comparison")
    twin_parser.add_argument("--state-label", help="State label for replay")

    args = parser.parse_args(argv)

    if args.command == "execute":
        return cmd_execute(args)
    elif args.command == "status":
        return cmd_status(args)
    elif args.command == "slot":
        return cmd_slot(args)
    elif args.command == "twin":
        return cmd_twin(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
