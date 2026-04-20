#!/usr/bin/env python3
"""AMOS ORGANISM OS — Run the digital organism

Usage:
    python run.py [command]

Commands:
    demo       Run the organism demo
    cli        Start interactive CLI
    api        Start API server
    status     Show organism status
"""

import importlib.util
from pathlib import Path

# Load organism module using importlib
_HERE = Path(__file__).parent
_org_path = _HERE / "organism.py"
_spec = importlib.util.spec_from_file_location("_organism", _org_path)
_org_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_org_mod)
AmosOrganism = _org_mod.AmosOrganism
from organism import main as organism_main


def run_demo():
    """Run the organism demo."""
    organism_main()


def run_cli():
    """Run interactive CLI."""
    organism = AmosOrganism()
    cli = AmosCLI(organism=organism)

    print("=" * 60)
    print("AMOS ORGANISM OS — Interactive CLI")
    print("Type 'help' for commands, 'exit' to quit")
    print("=" * 60)

    while True:
        try:
            user_input = input("\namos> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                print("Shutting down organism...")
                break
            if user_input.lower() == "help":
                print("\nCommands:")
                print("  status        Show organism status")
                print("  perceive <x>  Send perception to brain")
                print("  plan <goal>   Create a plan")
                print("  cycle         Run one organism cycle")
                print("  route <act>   Route an action")
                print("  memory        Show memory stats")
                print("  exit          Quit the CLI")
                continue

            # Parse command
            parts = user_input.split()
            cmd = parts[0]
            args = parts[1:] if len(parts) > 1 else []

            if cmd == "status":
                status = organism.status()
                print(f"\nSession: {status['session_id']}")
                print(f"Cycles: {status['cycle_count']}")
                print(f"Thoughts: {status['subsystems']['brain']['thought_count']}")
                print(f"Memories: {status['subsystems']['memory']['total_memories']}")

            elif cmd == "perceive" and args:
                content = " ".join(args)
                thought = organism.perceive(content)
                print(f"Thought created: {thought.id}")

            elif cmd == "plan" and args:
                goal = " ".join(args)
                plan = organism.plan(goal)
                print(f"Plan created: {plan.id}")
                print(f"Goal: {plan.goal}")

            elif cmd == "cycle":
                results = organism.cycle()
                print(f"Cycle {organism.state.cycle_count} complete")
                print(f"Active subsystem: {organism.state.current_subsystem}")

            elif cmd == "route" and args:
                action = args[0]
                decision = organism.decide(action)
                print(f"'{action}' -> {decision.target}")
                print(f"Reason: {decision.reason}")

            elif cmd == "memory":
                stats = organism.memory.stats()
                print(f"\nTotal memories: {stats['total_memories']}")
                for layer, count in stats["by_layer"].items():
                    cap = stats["capacity"][layer]
                    print(f"  {layer}: {count}/{cap}")

            else:
                print(f"Unknown command: {cmd}")

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except Exception as e:
            print(f"Error: {e}")


def run_api():
    """Run API server."""
    organism = AmosOrganism()
    from INTERFACES.api_server import APIServer

    server = APIServer(organism, host="localhost", port=8765)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down API server...")
        server.stop()


def main():
    """Main entry point."""
    command = sys.argv[1] if len(sys.argv) > 1 else "demo"

    if command == "demo":
        run_demo()
    elif command == "cli":
        run_cli()
    elif command == "api":
        run_api()
    elif command == "status":
        organism = AmosOrganism()
        import json

        print(json.dumps(organism.status(), indent=2, default=str))
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
