"""
AMOS CLI — Command-line interface for the organism.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class CommandHandler:
    """A CLI command handler."""
    name: str
    description: str
    handler: Callable
    args: List[tuple] = None  # [(name, type, help), ...]


class AmosCLI:
    """
    Command-line interface for AMOS Organism.

    Commands:
    - status: Show organism status
    - brain: Brain subsystem commands
    - muscle: Execute commands
    - run: Run the primary loop
    - workflow: Manage workflows
    - config: Show/edit configuration
    """

    def __init__(self, organism=None):
        self.organism = organism
        self._handlers: Dict[str, CommandHandler] = {}
        self._setup_default_handlers()

    def _setup_default_handlers(self):
        """Register default command handlers."""
        self.register(CommandHandler(
            name="status",
            description="Show organism status",
            handler=self._cmd_status,
        ))
        self.register(CommandHandler(
            name="brain",
            description="Brain subsystem commands (perceive, think, plan)",
            handler=self._cmd_brain,
            args=[("action", str, "Action to perform")],
        ))
        self.register(CommandHandler(
            name="muscle",
            description="Muscle subsystem commands (exec, code, run)",
            handler=self._cmd_muscle,
            args=[("action", str, "Action to perform")],
        ))
        self.register(CommandHandler(
            name="route",
            description="Route an action through the organism",
            handler=self._cmd_route,
            args=[
                ("action", str, "Action to route"),
                ("--params", str, "JSON parameters"),
            ],
        ))

    def register(self, handler: CommandHandler):
        """Register a command handler."""
        self._handlers[handler.name] = handler

    def run(self, args: List[str] = None) -> int:
        """Run the CLI."""
        if args is None:
            args = sys.argv[1:]

        if not args or args[0] in ("-h", "--help", "help"):
            self._print_help()
            return 0

        command = args[0]
        handler = self._handlers.get(command)

        if not handler:
            print(f"Unknown command: {command}")
            self._print_help()
            return 1

        try:
            return handler.handler(args[1:])
        except Exception as e:
            print(f"Error: {e}")
            return 1

    def _print_help(self):
        """Print help message."""
        print("AMOS Organism OS — CLI")
        print("=" * 40)
        print()
        for name, handler in sorted(self._handlers.items()):
            print(f"  {name:12} {handler.description}")
        print()
        print("Usage: python -m AMOS_ORGANISM_OS <command> [args...]")

    def _cmd_status(self, args: List[str]) -> int:
        """Show organism status."""
        if not self.organism:
            print("No organism instance connected")
            return 1

        status = self.organism.status()
        print("AMOS Organism Status")
        print("=" * 40)
        print(f"Session ID: {status['session_id']}")
        print(f"Cycle Count: {status['cycle_count']}")
        print(f"Active Subsystems: {', '.join(status['active_subsystems'])}")
        print()
        print("Subsystem Status:")
        for sub, info in status['subsystems'].items():
            print(f"  {sub}: {info}")
        return 0

    def _cmd_brain(self, args: List[str]) -> int:
        """Brain subsystem commands."""
        if not self.organism or not self.organism.brain:
            print("Brain subsystem not available")
            return 1

        if not args:
            # Show brain status
            status = self.organism.brain.status()
            print("Brain Status:")
            for key, val in status.items():
                print(f"  {key}: {val}")
            return 0

        action = args[0]
        if action == "perceive":
            content = " ".join(args[1:]) if len(args) > 1 else "Empty input"
            thought = self.organism.brain.perceive(content)
            print(f"Perceived: {thought.id} -> {thought.content[:50]}...")
        elif action == "plan":
            goal = " ".join(args[1:]) if len(args) > 1 else "Unspecified goal"
            plan = self.organism.brain.create_plan(goal)
            print(f"Created plan: {plan.id} for goal: {plan.goal}")
        else:
            print(f"Unknown brain action: {action}")
            return 1
        return 0

    def _cmd_muscle(self, args: List[str]) -> int:
        """Muscle subsystem commands."""
        if not self.organism or not self.organism.muscle:
            print("Muscle subsystem not available")
            return 1

        if not args:
            status = self.organism.muscle.status()
            print("Muscle Status:")
            for key, val in status.items():
                print(f"  {key}: {val}")
            return 0

        action = args[0]
        if action == "exec" and len(args) > 1:
            from AMOS_ORGANISM_OS.MUSCLE.executor import ExecutionContext
            ctx = ExecutionContext()
            result = self.organism.muscle.execute(args[1], ctx)
            print(f"Executed: {result.command}")
            print(f"Status: {result.status.value}")
            print(f"Output: {result.stdout[:200] if result.stdout else '(none)'}")
        else:
            print(f"Unknown muscle action: {action}")
            return 1
        return 0

    def _cmd_route(self, args: List[str]) -> int:
        """Route an action."""
        if not self.organism:
            print("No organism instance connected")
            return 1

        if not args:
            print("Usage: route <action> [--params <json>]")
            return 1

        action = args[0]
        params = {}

        # Parse --params if provided
        for i, arg in enumerate(args[1:]):
            if arg == "--params" and i + 1 < len(args[1:]):
                import json
                try:
                    params = json.loads(args[1:][i + 1])
                except json.JSONDecodeError:
                    print("Invalid JSON params")
                    return 1

        decision = self.organism.router.route(action, params)
        print(f"Routed '{action}' to {decision.target}")
        print(f"Reason: {decision.reason}")
        return 0


def main():
    """CLI entry point."""
    # Import organism here to avoid circular imports
    from ..organism import AmosOrganism

    organism = AmosOrganism()
    cli = AmosCLI(organism=organism)
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
