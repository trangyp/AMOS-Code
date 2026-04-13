#!/usr/bin/env python3
"""
AMOS Unified CLI (14_INTERFACES)
===============================

Command-line interface for the complete AMOS system:
- Brain (cognition)
- Organism (execution)
- Bridge (coordination)

Owner: Trang
Version: 2.0.0 - Now with standalone amos_brain
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

# Add paths for standalone brain
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))


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
    """Interact with standalone AMOS brain package."""
    try:
        from amos_brain import get_amos_integration
        from amos_brain.memory import get_brain_memory
        from amos_brain.dashboard import print_dashboard
        from amos_brain.cookbook import ArchitectureDecision

        amos = get_amos_integration()

        if args.action == "status":
            status = amos.get_status()
            print("AMOS Brain Status (Standalone Package)")
            print("=" * 50)
            print(f"Initialized: {status.get('initialized')}")
            print(f"Engines: {status.get('engines_count')} domain engines")
            print(f"Laws: {len(status.get('laws_active', []))} global laws")
            print("\nActive Laws:")
            for law in status.get('laws_active', []):
                print(f"  • {law}")

        elif args.action == "think":
            if not args.question:
                print("[ERROR] --question required for think action")
                return 1
            print(f"Analyzing: {args.question}")
            print("-" * 50)
            analysis = amos.analyze_with_rules(args.question)
            print(f"\nRule of 2 Confidence: {analysis.get('rule_of_two', {}).get('confidence', 0):.0%}")
            print(f"Rule of 4 Coverage: {analysis.get('rule_of_four', {}).get('completeness_score', 0):.0%}")
            print("\nRecommendations:")
            for rec in analysis.get('recommendations', []):
                print(f"  • {rec}")

        elif args.action == "engines":
            status = amos.get_status()
            print(f"Domain Engines ({status.get('engines_count', 0)}):")
            for domain in status.get('domains_covered', []):
                print(f"  • {domain}")

        elif args.action == "dashboard":
            days = int(args.days) if hasattr(args, 'days') else 30
            print_dashboard(days)

        elif args.action == "memory":
            memory = get_brain_memory()
            if args.subaction == "history":
                history = memory.get_reasoning_history(limit=args.limit or 5)
                print(f"Reasoning History (last {len(history)}):")
                for entry in history:
                    print(f"  [{entry.get('timestamp', 'unknown')[:10]}] {entry.get('problem_preview', 'N/A')[:50]}...")
            elif args.subaction == "recall":
                if not args.query:
                    print("[ERROR] --query required for recall")
                    return 1
                recall = memory.recall_for_problem(args.query)
                if recall.get("has_prior_reasoning"):
                    print(f"Found {len(recall.get('similar_entries', []))} similar past analyses")
                else:
                    print("No similar past reasoning found")

    except Exception as e:
        print(f"[ERROR] Brain error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


def cmd_bridge(args) -> int:
    """Execute tasks through brain-organism bridge."""
    try:
        from amos_brain_organism_bridge import BrainOrganismBridge

        bridge = BrainOrganismBridge()

        if args.action == "status":
            status = bridge.get_system_status()
            print("Brain-Organism Bridge Status")
            print("=" * 50)
            print(f"Brain: {status['brain']['engines']} engines, {status['brain']['laws']} laws")
            print(f"Organism: {'Connected' if status['organism']['connected'] else 'Stub mode'}")
            print(f"Bridge: {status['bridge']['status']} (v{status['bridge']['version']})")

        elif args.action == "execute":
            if not args.task:
                print("[ERROR] --task required")
                return 1

            print(f"Executing: {args.task}")
            print("-" * 50)

            context = {}
            if args.context:
                context = json.loads(args.context)

            result = bridge.analyze_and_execute(args.task, context)

            print(f"\nStatus: {result.status.upper()}")
            print(f"Action: {result.organism_action}")
            print(f"Resources: {result.resources_used}")
            print(f"\nOutput:\n{result.output}")

    except Exception as e:
        print(f"[ERROR] Bridge error: {e}")
        import traceback
        traceback.print_exc()
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


def cmd_immune(args) -> int:
    """Interact with IMMUNE security system."""
    root = get_organism_root()
    immune_dir = root / "03_IMMUNE"

    sys.path.insert(0, str(immune_dir))
    from immune_system import ImmuneSystem, ActionType

    immune = ImmuneSystem()

    if args.action == "status":
        status = immune.status()
        print("IMMUNE System Status")
        print("=" * 40)
        print(f"Active policies: {status['total_policies']}")
        print(f"Audit logs: {status['total_audit_logs']}")
        print(f"Policies: {', '.join(status['policies'])}")

    elif args.action == "validate" and args.action_type:
        action_type = getattr(ActionType, args.action_type.upper(), ActionType.READ)
        result = immune.validate(
            action="cli_test",
            action_type=action_type,
            target=args.target or "test_target"
        )
        print(f"Validation Result:")
        print(f"  Approved: {result.approved}")
        print(f"  Risk Level: {result.risk_level.value}")
        print(f"  Reason: {result.reason}")

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

    # Brain command (standalone package)
    brain_parser = subparsers.add_parser("brain", help="AMOS brain (standalone)")
    brain_parser.add_argument("action", choices=["status", "think", "engines", "dashboard", "memory"])
    brain_parser.add_argument("--question", "-q", help="Question for think")
    brain_parser.add_argument("--days", "-d", type=int, default=30, help="Dashboard days")
    brain_parser.add_argument("--subaction", choices=["history", "recall"], help="Memory subaction")
    brain_parser.add_argument("--limit", "-l", type=int, default=5, help="History limit")
    brain_parser.add_argument("--query", help="Recall query")
    brain_parser.set_defaults(func=cmd_brain)

    # Bridge command (unified execution)
    bridge_parser = subparsers.add_parser("bridge", help="Brain-Organism bridge")
    bridge_parser.add_argument("action", choices=["status", "execute"])
    bridge_parser.add_argument("--task", "-t", help="Task to execute")
    bridge_parser.add_argument("--context", "-c", help="JSON context")
    bridge_parser.set_defaults(func=cmd_bridge)

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

    # Immune command
    immune_parser = subparsers.add_parser(
        "immune", help="Security system (IMMUNE)"
    )
    immune_parser.add_argument(
        "action", choices=["status", "validate"], nargs="?",
        default="status"
    )
    immune_parser.add_argument(
        "--action-type", "-t", help="Action type to validate"
    )
    immune_parser.add_argument(
        "--target", "-g", help="Target for validation"
    )
    immune_parser.set_defaults(func=cmd_immune)

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
