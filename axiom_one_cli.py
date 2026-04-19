#!/usr/bin/env python3
"""Axiom One - Unified CLI Interface.

Real working CLI that integrates:
- Agent fleet orchestration
- AMOS brain cognitive runtime
- System graph analysis
- Workflow execution
"""

import argparse
import json
import sys
import time
from pathlib import Path

# Setup paths
AMOS_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(AMOS_ROOT))
sys.path.insert(0, str(AMOS_ROOT / "clawspring" / "amos_brain"))

from axiom_one_agent_fleet import AgentType, AxiomOneAgentFleet
from axiom_one_agent_fleet import demo as fleet_demo


def print_header(title: str):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def cmd_agents(args: argparse.Namespace) -> int:
    """List all available agents."""
    print_header("AGENT FLEET")

    fleet = AxiomOneAgentFleet()
    agents = fleet.list_agents()

    print(f"\nTotal agents: {len(agents)}\n")

    for agent in agents:
        print(f"  🔹 {agent['name']}")
        print(f"     Type: {agent['type']}")
        print(f"     Description: {agent['description']}")
        print(f"     Status: {agent['status']}")
        print(f"     Capabilities: {', '.join(agent['capabilities'])}")
        print()

    return 0


def cmd_workflow_create(args: argparse.Namespace) -> int:
    """Create a new workflow."""
    print_header("CREATE WORKFLOW")

    fleet = AxiomOneAgentFleet()
    workflow = fleet.create_workflow(
        name=args.name,
        description=args.description or f"Workflow: {args.name}",
        require_approval=args.approval,
    )

    print("\n✅ Workflow created:")
    print(f"   ID: {workflow.workflow_id}")
    print(f"   Name: {workflow.name}")
    print(f"   Description: {workflow.description}")
    print(f"   Status: {workflow.status.value}")
    print(f"   Created: {workflow.created_at}")

    # Save workflow ID for reference
    workflow_file = Path(f".axiom_workflow_{workflow.workflow_id[:8]}.json")
    with open(workflow_file, "w") as f:
        json.dump(
            {
                "workflow_id": workflow.workflow_id,
                "name": workflow.name,
                "created_at": workflow.created_at,
            },
            f,
            indent=2,
        )

    print(f"\n   Saved to: {workflow_file}")

    return 0


def cmd_workflow_execute(args: argparse.Namespace) -> int:
    """Execute a workflow with tasks."""
    print_header("EXECUTE WORKFLOW")

    fleet = AxiomOneAgentFleet()

    # Create workflow
    workflow = fleet.create_workflow(
        name=args.name, description=f"Execute: {args.name}", require_approval=False
    )

    print(f"\nCreated workflow: {workflow.workflow_id}")

    # Add tasks based on command
    if args.task == "research":
        task = fleet.assign_task(
            workflow=workflow,
            agent_type=AgentType.RESEARCHER,
            description=f"Research: {args.query or args.name}",
            input_data={"query": args.query or args.name, "path": args.path or "."},
            priority="high",
        )
        print(f"Assigned researcher task: {task.task_id}")

    elif args.task == "code":
        task = fleet.assign_task(
            workflow=workflow,
            agent_type=AgentType.CODE,
            description=f"Code: {args.name}",
            input_data={"action": "read", "file_path": args.file or "./test.py"},
            priority="high",
        )
        print(f"Assigned code task: {task.task_id}")

    elif args.task == "review":
        task = fleet.assign_task(
            workflow=workflow,
            agent_type=AgentType.REVIEWER,
            description=f"Review: {args.name}",
            input_data={"file_path": args.file or "./test.py"},
            priority="normal",
        )
        print(f"Assigned reviewer task: {task.task_id}")

    elif args.task == "architect":
        task = fleet.assign_task(
            workflow=workflow,
            agent_type=AgentType.ARCHITECT,
            description=f"Analyze architecture: {args.name}",
            input_data={"path": args.path or "."},
            priority="normal",
        )
        print(f"Assigned architect task: {task.task_id}")

    # Execute
    print("\n⚡ Executing workflow...")
    start = time.time()
    result = fleet.execute(workflow)
    duration = time.time() - start

    print(f"\n✅ Workflow completed in {duration:.2f}s")
    print(f"   Status: {result['status']}")
    print(f"   Tasks completed: {result['tasks_completed']}")
    print(f"   Tasks failed: {result['tasks_failed']}")

    # Print results
    if result.get("results"):
        print("\n📊 Results:")
        for task_id, task_result in result["results"].items():
            print(f"\n   Task {task_id[:8]}...")
            print(f"   Success: {task_result.get('success')}")
            print(f"   Quality: {task_result.get('quality_score', 0):.2f}")

            if "summary" in task_result:
                print(f"   Summary: {task_result['summary']}")
            if "recommendation" in task_result:
                print(f"   Recommendation: {task_result['recommendation']}")

    return 0


def cmd_graph_analyze(args: argparse.Namespace) -> int:
    """Analyze system graph."""
    print_header("SYSTEM GRAPH ANALYSIS")

    from axiom_one_agent_fleet import tool_list_directory, tool_search_code

    path = args.path or "."

    print(f"\n🔍 Analyzing: {path}\n")

    # List directory
    dir_result = tool_list_directory(path)
    if dir_result.get("success"):
        entries = dir_result.get("entries", [])
        dirs = [e for e in entries if e["type"] == "directory"]
        files = [e for e in entries if e["type"] == "file"]

        print(f"📁 Directories: {len(dirs)}")
        for d in dirs[:5]:
            print(f"   • {d['name']}/")
        if len(dirs) > 5:
            print(f"   ... and {len(dirs) - 5} more")

        print(f"\n📄 Files: {len(files)}")
        for f in files[:5]:
            size_kb = f.get("size", 0) / 1024
            print(f"   • {f['name']} ({size_kb:.1f} KB)")
        if len(files) > 5:
            print(f"   ... and {len(files) - 5} more")

    # Search for code
    if args.code:
        print("\n🔎 Searching for code patterns...")
        search_result = tool_search_code("class |def ", path, "*.py")
        if search_result.get("success"):
            files = search_result.get("files", [])
            print(f"   Found Python files: {len(files)}")
            for f in files[:10]:
                print(f"   • {f}")

    return 0


def cmd_brain_think(args: argparse.Namespace) -> int:
    """Use AMOS brain to think about a problem."""
    print_header("AMOS BRAIN COGNITIVE ANALYSIS")

    try:
        from ACTIVATE_BRAIN import get_cascade_brain

        print("\n🧠 Activating brain...")
        brain = get_cascade_brain()

        print(f"🧠 Processing intent: {args.intent}\n")

        result = brain.think(args.intent, {"context": args.context or "general", "source": "cli"})

        print("📊 Brain Analysis Results:")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Legality: {result.get('legality', 0):.3f}")
        print(f"   Sigma (Ω/K): {result.get('sigma', 0):.3f}")

        if result.get("selected_branch"):
            print(f"   Selected Branch: {result.get('selected_branch')}")

        if result.get("branches"):
            print(f"\n   Generated {len(result['branches'])} branches:")
            for i, branch in enumerate(result["branches"][:3], 1):
                print(f"   {i}. {branch.get('description', 'N/A')[:50]}...")

        return 0 if result.get("status") != "REJECTED" else 1

    except Exception as e:
        print(f"\n❌ Brain error: {e}")
        return 1


def cmd_demo(_args: argparse.Namespace) -> int:
    """Run full demonstration."""
    print_header("AXIOM ONE FULL DEMONSTRATION")

    # Run agent fleet demo
    fleet_demo()

    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="axiom",
        description="Axiom One - Unified Software Creation Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  axiom agents                          # List all agents
  axiom workflow create -n myproject    # Create workflow
  axiom execute -n analyze -t research -q "main functions"  # Run research
  axiom graph -p . --code               # Analyze codebase
  axiom think -i "Refactor auth system" # Brain analysis
  axiom demo                            # Full demonstration
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Agents command
    agents_parser = subparsers.add_parser("agents", help="List all available agents")
    agents_parser.set_defaults(func=cmd_agents)

    # Workflow create
    workflow_parser = subparsers.add_parser("workflow", help="Workflow management")
    workflow_sub = workflow_parser.add_subparsers(dest="workflow_cmd")

    create_parser = workflow_sub.add_parser("create", help="Create new workflow")
    create_parser.add_argument("-n", "--name", required=True, help="Workflow name")
    create_parser.add_argument("-d", "--description", help="Workflow description")
    create_parser.add_argument("--approval", action="store_true", help="Require approval")
    create_parser.set_defaults(func=cmd_workflow_create)

    # Execute command
    execute_parser = subparsers.add_parser("execute", help="Execute workflow")
    execute_parser.add_argument("-n", "--name", required=True, help="Workflow name")
    execute_parser.add_argument(
        "-t",
        "--task",
        required=True,
        choices=["research", "code", "review", "architect"],
        help="Task type",
    )
    execute_parser.add_argument("-q", "--query", help="Research query")
    execute_parser.add_argument("-f", "--file", help="Target file")
    execute_parser.add_argument("-p", "--path", help="Target path")
    execute_parser.set_defaults(func=cmd_workflow_execute)

    # Graph command
    graph_parser = subparsers.add_parser("graph", help="Analyze system graph")
    graph_parser.add_argument("-p", "--path", default=".", help="Path to analyze")
    graph_parser.add_argument("--code", action="store_true", help="Include code analysis")
    graph_parser.set_defaults(func=cmd_graph_analyze)

    # Brain command
    brain_parser = subparsers.add_parser("think", help="Use AMOS brain for analysis")
    brain_parser.add_argument("-i", "--intent", required=True, help="Intent or question")
    brain_parser.add_argument("-c", "--context", help="Additional context")
    brain_parser.set_defaults(func=cmd_brain_think)

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run full demonstration")
    demo_parser.set_defaults(func=cmd_demo)

    # Parse and execute
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
