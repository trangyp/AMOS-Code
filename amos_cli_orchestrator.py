#!/usr/bin/env python3
"""AMOS Orchestrator CLI v14.0.0

Command-line interface for the AMOS Production Orchestrator.
Provides commands to initialize, monitor, and manage the unified system.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from amos_production_orchestrator import get_orchestrator


def cmd_init(args: argparse.Namespace) -> int:
    """Initialize the AMOS orchestrator."""
    print("🚀 AMOS Production Orchestrator v14.0.0")
    print("=" * 50)

    orchestrator = get_orchestrator()

    try:
        success = asyncio.run(orchestrator.initialize())

        if success:
            print("\n✅ Initialization Complete!")
            activated = sum(1 for m in orchestrator.modules.values() if m.activated)
            print(f"  Modules: {len(orchestrator.modules)}")
            print(f"  Activated: {activated}")
            print(f"  Memory Bridges: {len(orchestrator.bridges)}")
            print(f"  Guardrails: {len(orchestrator.guardrails)}")
            return 0
        else:
            print("\n❌ Initialization Failed")
            return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


def cmd_status(args: argparse.Namespace) -> int:
    """Show orchestrator status."""
    orchestrator = get_orchestrator()

    if not orchestrator.modules:
        print("⚠️  Orchestrator not initialized. Run: amos-cli init")
        return 1

    activated = sum(1 for m in orchestrator.modules.values() if m.activated)
    total = len(orchestrator.modules)

    print("📊 AMOS Orchestrator Status")
    print("=" * 40)
    print("Version: 14.0.0")
    pct = 100 * activated / total
    print(f"Modules: {activated}/{total} activated ({pct:.1f}%)")
    print(f"Memory Bridges: {len(orchestrator.bridges)}")
    print(f"Guardrails: {len(orchestrator.guardrails)}")
    print(f"Initialized: {'✅' if orchestrator.initialized else '❌'}")

    if args.verbose:
        print("\n📋 Module Breakdown by Tier:")
        from amos_production_orchestrator import SystemTier

        for tier in SystemTier:
            tier_modules = [m for m in orchestrator.modules.values() if m.tier == tier]
            tier_activated = sum(1 for m in tier_modules if m.activated)
            print(f"  {tier.name}: {tier_activated}/{len(tier_modules)}")

    return 0


def cmd_modules(args: argparse.Namespace) -> int:
    """List all modules."""
    orchestrator = get_orchestrator()

    if not orchestrator.modules:
        print("⚠️  No modules found. Run: amos-cli init")
        return 1

    modules: List[Any] = list(orchestrator.modules.values())

    if args.tier:
        modules = [m for m in modules if m.tier.name.lower() == args.tier.lower()]

    if args.only_active:
        modules = [m for m in modules if m.activated]

    print(f"📦 Modules ({len(modules)} total)")
    print("-" * 60)

    for module in sorted(modules, key=lambda m: m.tier.value):
        status = "✅" if module.activated else "⏳"
        size_kb = module.size_bytes / 1024
        print(f"{status} {module.name:40} | " f"{module.tier.name:12} | {size_kb:6.1f}KB")

    return 0


def cmd_api(args: argparse.Namespace) -> int:
    """Start the REST API server."""
    print(f"🌐 Starting AMOS API Server on " f"{args.host}:{args.port}")
    print("Press Ctrl+C to stop")

    orchestrator = get_orchestrator()

    if not orchestrator.initialized:
        print("⚠️  Orchestrator not initialized. Initializing now...")
        try:
            asyncio.run(orchestrator.initialize())
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return 1

    try:
        orchestrator.run(host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        return 1

    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate the orchestrator configuration."""
    print("🔍 Validating AMOS Orchestrator...")

    orchestrator = get_orchestrator()
    errors: List[str] = []
    warnings: List[str] = []

    # Check if modules exist
    if not orchestrator.modules:
        errors.append("No modules discovered")
    else:
        # Check critical modules

        from amos_production_orchestrator import SystemTier

        critical = [m for m in orchestrator.modules.values() if m.tier == SystemTier.CRITICAL]
        critical_activated = sum(1 for m in critical if m.activated)

        if critical and critical_activated < len(critical):
            msg = f"Only {critical_activated}/{len(critical)} " f"critical modules activated"
            warnings.append(msg)

        # Check activation rate
        activated = sum(1 for m in orchestrator.modules.values() if m.activated)
        total = len(orchestrator.modules)
        rate = activated / total if total > 0 else 0

        if rate < 0.5:
            errors.append(f"Activation rate too low: {rate:.1%}")
        elif rate < 0.8:
            warnings.append(f"Activation rate below optimal: {rate:.1%}")

    # Print results
    if errors:
        print("\n❌ Errors:")
        for error in errors:
            print(f"  - {error}")

    if warnings:
        print("\n⚠️  Warnings:")
        for warning in warnings:
            print(f"  - {warning}")

    if not errors and not warnings:
        print("\n✅ All validations passed!")
        return 0

    return 1 if errors else 0


def cmd_export(args: argparse.Namespace) -> int:
    """Export orchestrator state to JSON."""
    orchestrator = get_orchestrator()

    if not orchestrator.modules:
        print("⚠️  No data to export. Run: amos-cli init")
        return 1

    data: Dict[str, Any] = {
        "version": "14.0.0",
        "modules_total": len(orchestrator.modules),
        "modules_activated": sum(1 for m in orchestrator.modules.values() if m.activated),
        "memory_bridges": len(orchestrator.bridges),
        "guardrails": len(orchestrator.guardrails),
        "modules": [
            {
                "name": m.name,
                "tier": m.tier.name,
                "activated": m.activated,
                "size_bytes": m.size_bytes,
                "dependencies": list(m.dependencies),
                "provides": list(m.provides),
            }
            for m in orchestrator.modules.values()
        ],
    }

    output_path = Path(args.output)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"💾 Exported to {output_path}")
    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="amos-cli",
        description="AMOS Production Orchestrator CLI v14.0.0",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize the orchestrator",
    )
    init_parser.set_defaults(func=cmd_init)

    # status command
    status_parser = subparsers.add_parser(
        "status",
        help="Show orchestrator status",
    )
    status_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed status",
    )
    status_parser.set_defaults(func=cmd_status)

    # modules command
    modules_parser = subparsers.add_parser(
        "modules",
        help="List all modules",
    )
    modules_parser.add_argument(
        "--tier",
        help="Filter by tier (CRITICAL, ESSENTIAL, etc.)",
    )
    modules_parser.add_argument(
        "--active",
        dest="only_active",
        action="store_true",
        help="Show only active modules",
    )
    modules_parser.set_defaults(func=cmd_modules)

    # api command
    api_parser = subparsers.add_parser(
        "api",
        help="Start the REST API server",
    )
    api_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    api_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    api_parser.set_defaults(func=cmd_api)

    # validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate orchestrator configuration",
    )
    validate_parser.set_defaults(func=cmd_validate)

    # export command
    export_parser = subparsers.add_parser(
        "export",
        help="Export orchestrator state to JSON",
    )
    export_parser.add_argument(
        "-o",
        "--output",
        default="amos_state.json",
        help="Output file path (default: amos_state.json)",
    )
    export_parser.set_defaults(func=cmd_export)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
