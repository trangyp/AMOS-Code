"""
Axiom Enhanced CLI - Natural Language Command Interface

Integrates NL Processor, Control Directory, and Integration Buses
for a complete command-line experience.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from .axiom_state import get_state_manager
from .control_directory import get_control_manager
from .integration_bus import BusMessage, BusPriority, BusType, get_bus_coordinator
from .nl_processor import RiskLevel, get_nl_processor


def cmd_init(args: argparse.Namespace) -> int:
    """Initialize .amos/ control directory."""
    manager = get_control_manager(args.path)

    if manager.exists() and not args.force:
        print(f"Error: .amos/ already exists in {args.path}")
        print("Use --force to overwrite")
        return 1

    manager.init(name=args.name, language=args.language)

    print(f"✅ Initialized .amos/ control directory in {args.path}")
    print(f"   Name: {args.name}")
    print(f"   Language: {args.language}")
    print("\nCreated files:")
    for filename in [
        "repo.yaml",
        "glossary.yaml",
        "policies.yaml",
        "architecture.yaml",
        "verify.yaml",
        "ssot.yaml",
    ]:
        print(f"   - .amos/{filename}")
    return 0


def cmd_config(args: argparse.Namespace) -> int:
    """Show or modify control directory configuration."""
    manager = get_control_manager(args.path)

    if not manager.exists():
        print(f"Error: No .amos/ directory in {args.path}")
        print("Run: amos init")
        return 1

    if args.show:
        repo = manager.get_repo()
        print(f"Repository: {repo.name}")
        print(f"Version: {repo.version}")
        print(f"Language: {repo.language}")
        print(f"Entrypoints: {', '.join(repo.entrypoints)}")
        print(f"Protected: {', '.join(repo.protected_paths)}")

        policies = manager.get_policies()
        print(f"\nPolicies: {len(policies.rules)} rules")
        for rule in policies.rules:
            status = "✓" if rule.enabled else "✗"
            print(f"   [{status}] {rule.name} ({rule.severity})")

    return 0


def cmd_nl(args: argparse.Namespace) -> int:
    """Process natural language command."""
    processor = get_nl_processor()

    # Process the natural language input
    intent, proposals, explanation = processor.process(args.command, auto_commit=args.auto_commit)

    print(f"Intent ID: {intent.intent_id}")
    print(f"Action: {intent.action_type}")
    print(f"Targets: {', '.join(intent.target_files) or 'N/A'}")
    print(f"Code Scope: {', '.join(intent.code_scope) or 'N/A'}")

    # Show risk classification
    risk = processor.classify_risk(intent)
    risk_emoji = {
        RiskLevel.LOW: "🟢",
        RiskLevel.MEDIUM: "🟡",
        RiskLevel.HIGH: "🟠",
        RiskLevel.CRITICAL: "🔴",
    }
    print(f"Risk: {risk_emoji.get(risk, '⚪')} {risk.value.upper()}")

    # Show explanation
    print("\n" + explanation)

    if args.dry_run:
        print("\n(Dry run - no changes made)")

    return 0


async def cmd_bus_start(args: argparse.Namespace) -> int:
    """Start integration bus coordinator."""
    coordinator = get_bus_coordinator()

    print("Starting Axiom Integration Buses...")
    await coordinator.start_all()

    print("✅ Buses started:")
    for bus_type in coordinator.buses.keys():
        print(f"   - {bus_type.value}")

    # Health check
    health = await coordinator.health_check_all()
    print("\nHealth Status:")
    for name, status in health.items():
        emoji = "✅" if status.get("status") == "healthy" else "⚠️"
        print(f"   {emoji} {name}: {status.get('status', 'unknown')}")

    if args.daemon:
        print("\nRunning in daemon mode (Ctrl+C to stop)...")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping buses...")
            await coordinator.stop_all()

    return 0


def cmd_bus_status(args: argparse.Namespace) -> int:
    """Check integration bus status."""
    coordinator = get_bus_coordinator()

    health = asyncio.run(coordinator.health_check_all())

    print("Integration Bus Status")
    print("=" * 40)

    for name, status in health.items():
        emoji = "✅" if status.get("status") == "healthy" else "⚠️"
        print(f"\n{emoji} {name.upper()}")
        for key, value in status.items():
            if key != "status":
                print(f"   {key}: {value}")

    return 0


async def cmd_bus_publish(args: argparse.Namespace) -> int:
    """Publish message to a bus."""
    coordinator = get_bus_coordinator()
    await coordinator.start_all()

    try:
        bus_type = BusType(args.bus)
    except ValueError:
        print(f"Error: Unknown bus type '{args.bus}'")
        print(f"Available: {', '.join(b.value for b in BusType)}")
        return 1

    # Parse payload
    try:
        payload = json.loads(args.payload)
    except json.JSONDecodeError:
        payload = {"message": args.payload}

    # Create and publish message
    message = BusMessage.create(
        bus_type=bus_type,
        topic=args.topic,
        payload=payload,
        source="axiom_cli",
        priority=BusPriority[args.priority.upper()],
    )

    await coordinator.publish(message)
    print(f"✅ Published to {args.bus}/{args.topic}")
    print(f"   Message ID: {message.msg_id}")

    return 0


def cmd_state(args: argparse.Namespace) -> int:
    """Show current Axiom state."""
    state_manager = get_state_manager()
    state = state_manager.get_current()

    if args.json:
        print(json.dumps(state.to_dict(), indent=2))
        return 0

    print("Axiom State")
    print("=" * 40)
    print(f"Hash: {state.canonical_hash[:16]}...")
    print(f"Timestamp: {state.timestamp.isoformat()}")

    print("\nDomain States:")
    print(f"   Classical: load={state.classical.system_load:.1f}%")
    print(f"   Biological: health={state.biological.health_score:.2f}")
    print(f"   Quantum: coherence={state.quantum.coherence_time:.2f}s")
    print(f"   World: pressure={state.world.external_pressure:.2f}")
    print(f"   Uncertainty: epistemic={state.uncertainty.epistemic_uncertainty:.2f}")

    if args.full:
        print("\nProjections:")
        for view in ["deterministic", "observational", "decision", "health"]:
            projection = state.project(view)
            print(f"\n   {view}:")
            for key, value in projection.items():
                print(f"      {key}: {value}")

    return 0


def cmd_ledger(args: argparse.Namespace) -> int:
    """Show command ledger."""
    processor = get_nl_processor()

    if args.intent_id:
        ledger = processor.get_ledger(args.intent_id)
        if not ledger:
            print(f"Error: Ledger not found for intent {args.intent_id}")
            return 1

        print(f"Ledger: {ledger.ledger_id}")
        print(f"Intent: {ledger.intent_id}")
        print(f"Status: {ledger.status.value}")
        print(f"Final State: {ledger.final_state}")
        print(f"\nTransitions ({len(ledger.transitions)}):")
        for t in ledger.transitions:
            print(f"   [{t['timestamp']}] {t['status']}")
    else:
        print("Recent ledgers:")
        # Would need to add method to list all ledgers
        print("   (Use --intent-id to view specific ledger)")

    return 0


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="amos",
        description="Axiom AI Platform CLI - Natural language to code",
    )
    parser.add_argument("--version", action="version", version="Axiom 7.1.0")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize .amos/ control directory")
    init_parser.add_argument("--path", default=".", help="Repository root path")
    init_parser.add_argument("--name", required=True, help="Repository name")
    init_parser.add_argument("--language", default="python", help="Primary language")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing")
    init_parser.set_defaults(func=cmd_init)

    # config command
    config_parser = subparsers.add_parser("config", help="Manage control directory")
    config_parser.add_argument("--path", default=".", help="Repository root path")
    config_parser.add_argument("--show", action="store_true", help="Show configuration")
    config_parser.set_defaults(func=cmd_config)

    # nl command (natural language)
    nl_parser = subparsers.add_parser("do", help="Execute natural language command")
    nl_parser.add_argument("command", nargs="+", help="Natural language command")
    nl_parser.add_argument("--auto-commit", action="store_true", help="Auto-approve changes")
    nl_parser.add_argument("--dry-run", action="store_true", help="Show plan without executing")
    nl_parser.set_defaults(func=lambda args: cmd_nl(args))

    # bus command group
    bus_parser = subparsers.add_parser("bus", help="Integration bus management")
    bus_subparsers = bus_parser.add_subparsers(dest="bus_command")

    bus_start = bus_subparsers.add_parser("start", help="Start bus coordinator")
    bus_start.add_argument("--daemon", action="store_true", help="Run as daemon")
    bus_start.set_defaults(func=lambda args: asyncio.run(cmd_bus_start(args)))

    bus_status = bus_subparsers.add_parser("status", help="Check bus status")
    bus_status.set_defaults(func=cmd_bus_status)

    bus_publish = bus_subparsers.add_parser("publish", help="Publish message to bus")
    bus_publish.add_argument("bus", choices=[b.value for b in BusType], help="Bus type")
    bus_publish.add_argument("topic", help="Message topic")
    bus_publish.add_argument("payload", help="JSON payload or message string")
    bus_publish.add_argument(
        "--priority",
        default="NORMAL",
        choices=[p.name for p in BusPriority],
        help="Message priority",
    )
    bus_publish.set_defaults(func=lambda args: asyncio.run(cmd_bus_publish(args)))

    # state command
    state_parser = subparsers.add_parser("state", help="Show Axiom state")
    state_parser.add_argument("--json", action="store_true", help="Output as JSON")
    state_parser.add_argument("--full", action="store_true", help="Show full projections")
    state_parser.set_defaults(func=cmd_state)

    # ledger command
    ledger_parser = subparsers.add_parser("ledger", help="View command ledger")
    ledger_parser.add_argument("--intent-id", help="Specific intent to view")
    ledger_parser.set_defaults(func=cmd_ledger)

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    # Handle nl command args concatenation
    if args.command == "do" and hasattr(args, "command"):
        args.command = " ".join(args.command)

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
