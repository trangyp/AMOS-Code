#!/usr/bin/env python3
"""
AMOS CLI Interface (14_INTERFACES)
=================================

Command-line interface for interacting with the AMOS Organism.
Provides commands for orchestration, agent management, and task execution.

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional


def get_organism_root() -> Path:
    """Get the organism root directory."""
    return Path(__file__).parent.parent


def cmd_status(args) -> int:
    """Show organism status."""
    root = get_organism_root()

    print("AMOS Organism Status")
    print("=" * 50)

    # Load world state
    state_path = root / "world_state.json"
    if state_path.exists():
        with open(state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)

        health = state.get("system_health", {})
        print(f"Overall Status: {health.get('overall_status', 'unknown')}")
        print(f"Last Check: {health.get('last_check', 'unknown')}")

        print("\nSubsystems:")
        for code, status in health.get("subsystems", {}).items():
            indicator = "●" if status == "active" else "○"
            print(f"  {indicator} {code}: {status}")

    # Load pipeline state
    pipeline_path = root / "memory" / "pipeline_state.json"
    if pipeline_path.exists():
        with open(pipeline_path, 'r', encoding='utf-8') as f:
            pipeline = json.load(f)

        print("\nPipeline:")
        print(f"  Cycles: {pipeline.get('status', {}).get('cycle_count', 0)}")
        print(f"  Errors: {pipeline.get('status', {}).get('error_count', 0)}")

    return 0


def cmd_run(args) -> int:
    """Run the orchestrator."""
    root = get_organism_root()
    orchestrator = root / "AMOS_ONECLICK_ORCHESTRATOR.py"

    if not orchestrator.exists():
        print("[ERROR] Orchestrator not found")
        return 1

    import subprocess
    result = subprocess.run([sys.executable, str(orchestrator)])
    return result.returncode


def cmd_agents(args) -> int:
    """List or manage agents."""
    root = get_organism_root()
    factory_dir = root / "13_FACTORY"

    if args.action == "list":
        agents_dir = factory_dir / "agents"
        if not agents_dir.exists():
            print("No agents created yet")
            return 0

        registry = agents_dir / "registry.json"
        if registry.exists():
            with open(registry, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"Agents ({data.get('agent_count', 0)} total):")
            for agent in data.get("agents", []):
                print(f"  - {agent['id']}: {agent['spec']['name']} ({agent['status']})")
        else:
            print("No agent registry found")

    elif args.action == "create":
        # Create standard agents
        sys.path.insert(0, str(factory_dir))
        from agent_factory import AgentFactory

        factory = AgentFactory(root)
        agents = factory.create_standard_agents()
        print(f"Created {len(agents)} agents")

    return 0


def cmd_workers(args) -> int:
    """Execute worker tasks."""
    root = get_organism_root()
    muscle_dir = root / "06_MUSCLE"

    sys.path.insert(0, str(muscle_dir))
    from amos_worker_engine import get_worker_engine

    engine = get_worker_engine(root)

    if args.task == "write":
        plan = {
            "steps": [
                {
                    "action": "write_file",
                    "content": args.content,
                    "target_file": args.file
                }
            ]
        }
        result = engine.execute_plan(plan)
        print(f"Success: {result.success}")
        if result.artifacts:
            print(f"Created: {result.artifacts}")

    elif args.task == "analyze":
        plan = {
            "steps": [
                {
                    "action": "analyze",
                    "topic": args.topic
                }
            ]
        }
        result = engine.execute_plan(plan)
        print(result.output)

    return 0


def cmd_brain(args) -> int:
    """Interact with AMOS brain."""
    root = get_organism_root()
    brain_root = root.parent / "_AMOS_BRAIN"

    # Try brain loader first
    sys.path.insert(0, str(root / "01_BRAIN"))
    try:
        from brain_loader import get_brain_loader

        loader = get_brain_loader(brain_root)
        loader.load_all_engines()

        if args.engines:
            status = loader.get_status()
            print(f"Brain Engines ({status['engines_count']}):")
            for engine in status['engines']:
                print(f"  - {engine}")
            print(f"\nTotal size: {status['total_size_mb']:.2f} MB")
            return 0

        if args.search:
            print(f"Searching brain for: '{args.search}'")
            results = loader.search(args.search, max_results=10)
            print(f"\nFound {len(results)} results:")
            for r in results:
                content = str(r.content)[:100]
                print(f"  [{r.engine_name}] {r.path}")
                print(f"    Score: {r.relevance_score:.2f} | {content}...")
            return 0

    except Exception as e:
        print(f"[INFO] Brain loader not available: {e}")

    # Fallback to cognitive runtime
    sys.path.insert(0, str(root.parent))
    try:
        from amos_cognitive_runtime import AMOSCognitiveRuntime

        runtime = AMOSCognitiveRuntime(brain_root)

        if args.action == "think":
            result = runtime.think(args.question, args.mode)
            print(json.dumps(result, indent=2))

        elif args.action == "status":
            status = runtime.get_status()
            print(json.dumps(status, indent=2))

        elif args.action == "engines":
            engines = runtime.list_available_engines()
            print(f"Available engines ({len(engines)}):")
            for e in engines:
                print(f"  - {e}")

    except Exception as e:
        print(f"[ERROR] Brain not available: {e}")
        return 1

    return 0


def cmd_blood(args) -> int:
    """Interact with BLOOD financial engine."""
    root = get_organism_root()
    blood_dir = root / "04_BLOOD"

    sys.path.insert(0, str(blood_dir))
    from financial_engine import FinancialEngine

    engine = FinancialEngine(root)

    if args.action == "status":
        status = engine.get_status()
        print("BLOOD Financial Status")
        print("=" * 40)
        print(f"Status: {status['status']}")
        print(f"Budget categories: {status['budget_categories']}")
        print(f"Active allocations: {status['active_allocations']}")
        print(f"Total transactions: {status['total_transactions']}")

        print("\nBudget Status:")
        for cat, budget in status['budget_status'].items():
            if budget:
                print(f"  {cat}: ${budget['remaining']:.2f} remaining")

    elif args.action == "budget":
        if args.category and args.amount:
            engine.set_budget(args.category, args.amount, args.period)
            print(f"Set budget for {args.category}: ${args.amount}")
        else:
            print("Usage: amos blood budget --category compute --amount 100")

    return 0


def cmd_legal(args) -> int:
    """Interact with LEGAL engine."""
    root = get_organism_root()
    legal_dir = root / "11_LEGAL_BRAIN"

    sys.path.insert(0, str(legal_dir))
    from legal_engine import LegalEngine

    engine = LegalEngine(root)

    if args.action == "status":
        status = engine.get_status()
        print("LEGAL Engine Status")
        print("=" * 40)
        print(f"Status: {status['status']}")
        print(f"Active rules: {status['active_rules']}")
        print(f"Total checks: {status['total_checks_performed']}")
        print(f"Pass rate: {status['recent_pass_rate']:.1%}")

    elif args.action == "check" and args.content:
        results = engine.check_compliance(args.content, "cli_check")
        print(f"\nCompliance Check Results:")
        for r in results:
            status = "✓" if r.passed else "✗"
            print(f"  {status} [{r.rule_id}] {r.message}")

    return 0


def cmd_social(args) -> int:
    """Interact with SOCIAL engine."""
    root = get_organism_root()
    social_dir = root / "09_SOCIAL_ENGINE"

    sys.path.insert(0, str(social_dir))
    from social_engine import SocialEngine

    engine = SocialEngine(root)

    if args.action == "status":
        status = engine.get_status()
        print("SOCIAL Engine Status")
        print("=" * 40)
        print(f"Status: {status['status']}")
        print(f"Registered agents: {status['registered_agents']}")
        print(f"Total messages: {status['total_messages']}")
        print(f"Total connections: {status['total_connections']}")
        print(f"Knowledge shares: {status['knowledge_shares']}")

    elif args.action == "graph" and args.agent:
        graph = engine.get_social_graph(args.agent)
        print(f"\nSocial Graph for {args.agent}:")
        print(f"  Connections: {graph['connection_count']}")
        print(f"  Messages sent: {graph['messages_sent']}")
        print(f"  Messages received: {graph['messages_received']}")
        print(f"  Unread: {graph['unread_messages']}")

    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="amos",
        description="AMOS 7-System Organism CLI"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show organism status")
    status_parser.set_defaults(func=cmd_status)

    # Run command
    run_parser = subparsers.add_parser("run", help="Run orchestrator")
    run_parser.set_defaults(func=cmd_run)

    # Agents command
    agent_parser = subparsers.add_parser("agents", help="Manage agents")
    agent_parser.add_argument("action", choices=["list", "create"], nargs="?",
                              default="list")
    agent_parser.set_defaults(func=cmd_agents)

    # Workers command
    worker_parser = subparsers.add_parser("workers", help="Execute workers")
    worker_parser.add_argument("task", choices=["write", "analyze"])
    worker_parser.add_argument("--file", "-f", help="Target file")
    worker_parser.add_argument("--content", "-c", help="Content to write")
    worker_parser.add_argument("--topic", "-t", help="Analysis topic")
    worker_parser.set_defaults(func=cmd_workers)

    # Brain command
    brain_parser = subparsers.add_parser("brain", help="Interact with brain")
    brain_parser.add_argument("action", choices=["think", "status", "engines"])
    brain_parser.add_argument(
        "--question", "-q", help="Question to think about"
    )
    brain_parser.add_argument(
        "--mode", "-m", default="exploratory_mapping",
        help="Reasoning mode"
    )
    brain_parser.add_argument(
        "--search", "-s", help="Search term for brain"
    )
    brain_parser.add_argument(
        "--engines", "-e", action="store_true",
        help="List brain engines"
    )
    brain_parser.set_defaults(func=cmd_brain)

    # Blood command
    blood_parser = subparsers.add_parser(
        "blood", help="Financial engine (BLOOD)"
    )
    blood_parser.add_argument(
        "action", choices=["status", "budget"], nargs="?",
        default="status"
    )
    blood_parser.add_argument(
        "--category", "-c", help="Budget category"
    )
    blood_parser.add_argument(
        "--amount", "-a", type=float, help="Budget amount"
    )
    blood_parser.add_argument(
        "--period", "-p", default="monthly",
        help="Budget period"
    )
    blood_parser.set_defaults(func=cmd_blood)

    # Social command
    social_parser = subparsers.add_parser(
        "social", help="Agent communication (SOCIAL)"
    )
    social_parser.add_argument(
        "action", choices=["status", "graph"], nargs="?",
        default="status"
    )
    social_parser.add_argument(
        "--agent", "-a", help="Agent ID for graph view"
    )
    social_parser.set_defaults(func=cmd_social)

    # Legal command
    legal_parser = subparsers.add_parser(
        "legal", help="Legal compliance (LEGAL)"
    )
    legal_parser.add_argument(
        "action", choices=["status", "check"], nargs="?",
        default="status"
    )
    legal_parser.add_argument(
        "--content", "-c", help="Content to check"
    )
    legal_parser.set_defaults(func=cmd_legal)

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
