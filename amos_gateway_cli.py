#!/usr/bin/env python3
"""AMOS Gateway CLI - Real Commands for Unified Gateway
=====================================================

Production CLI for managing the AMOS Unified Gateway with real brain integration.

Commands:
    start       Start the API gateway server
    status      Check brain system status
    chat        Send chat message via CLI
    agent       Run agent task
    test        Run integration tests

Usage:
    python amos_gateway_cli.py start --port 8000
    python amos_gateway_cli.py chat "Design a secure API"
    python amos_gateway_cli.py agent --type repo_scan --task "Analyze codebase"
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add project root
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))


def cmd_start(args: argparse.Namespace) -> int:
    """Start the real gateway server."""
    try:
        import uvicorn
        from amos_unified_gateway import BRAIN_AVAILABLE, app

        if not BRAIN_AVAILABLE:
            print("ERROR: AMOS brain systems not available")
            return 1

        print(f"Starting AMOS Unified Gateway on port {args.port}")
        print(f"Brain systems: {'OK' if BRAIN_AVAILABLE else 'MISSING'}")

        uvicorn.run(
            "amos_unified_gateway:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info",
        )
        return 0
    except ImportError as e:
        print(f"ERROR: Cannot start server - {e}")
        return 1


async def cmd_chat(args: argparse.Namespace) -> int:
    """Send real chat message via SDK."""
    try:
        from amos_platform_sdk import AMOSPlatformSDK

        async with AMOSPlatformSDK(base_url=args.api_url) as sdk:
            response = await sdk.chat.send(
                message=args.message,
                workspace_id=args.workspace or "cli",
            )

            print(f"\nResponse: {response.message}")
            print(f"Confidence: {response.confidence}")
            print(f"Domain: {response.domain}")
            print(f"Law Compliant: {response.law_compliant}")

            if response.violations:
                print(f"Violations: {', '.join(response.violations)}")

            return 0
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


async def cmd_agent(args: argparse.Namespace) -> int:
    """Run real agent via API."""
    try:
        from amos_platform_sdk import AMOSPlatformSDK

        async with AMOSPlatformSDK(base_url=args.api_url) as sdk:
            # Start agent
            task = await sdk.agents.run(
                agent_type=args.type,
                task_description=args.task,
                priority=args.priority,
            )

            print(f"Agent started: {task.task_id}")
            print(f"Status: {task.status}")

            if args.wait:
                print("Waiting for completion...")
                final = await sdk.agents.wait_for_completion(task.task_id)
                print(f"\nFinal status: {final.status}")
                if final.result:
                    print(f"Result: {final.result}")

            return 0
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


def cmd_status(args: argparse.Namespace) -> int:
    """Check real brain system status."""
    try:
        from amos_agentic_ai import create_agent
        from amos_brain.facade import BrainClient
        from amos_hybrid_orchestrator import HybridNeuralSymbolicOrchestrator

        status = {
            "brain_client": False,
            "amos_agent": False,
            "orchestrator": False,
        }

        # Test brain client
        try:
            client = BrainClient()
            status["brain_client"] = True
        except Exception as e:
            print(f"BrainClient: FAIL - {e}")

        # Test agent creation
        try:
            agent = asyncio.run(create_agent("test", tools=[]))
            status["amos_agent"] = True
        except Exception as e:
            print(f"AMOSAgent: FAIL - {e}")

        # Test orchestrator
        try:
            orch = HybridNeuralSymbolicOrchestrator()
            status["orchestrator"] = True
        except Exception as e:
            print(f"Orchestrator: FAIL - {e}")

        print("\nBrain System Status:")
        print("=" * 30)
        for component, ok in status.items():
            status_str = "✅ OK" if ok else "❌ FAIL"
            print(f"{component:20}: {status_str}")

        return 0 if all(status.values()) else 1
    except Exception as e:
        print(f"ERROR checking status: {e}")
        return 1


async def cmd_test(args: argparse.Namespace) -> int:
    """Run real integration tests."""
    try:
        from amos_platform_sdk import AMOSPlatformSDK

        print("Running integration tests...")
        print("=" * 40)

        async with AMOSPlatformSDK(base_url=args.api_url) as sdk:
            # Test 1: Health check
            print("\n1. Testing health endpoint...")
            health = await sdk.health()
            print(f"   Health: {health.get('status', 'unknown')}")

            # Test 2: Chat
            print("\n2. Testing chat endpoint...")
            response = await sdk.chat.send(
                message="Hello",
                workspace_id="test",
            )
            print(f"   Response received: {len(response.message)} chars")

            # Test 3: Agent
            print("\n3. Testing agent endpoint...")
            task = await sdk.agents.run(
                agent_type="test",
                task_description="Test task",
            )
            print(f"   Task created: {task.task_id}")

            print("\n✅ All tests passed")
            return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AMOS Unified Gateway CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s start --port 8000
  %(prog)s chat "Design API" --api-url http://localhost:8000
  %(prog)s agent --type repo_scan --task "Analyze code" --wait
  %(prog)s status
  %(prog)s test --api-url http://localhost:8000
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start gateway server")
    start_parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    start_parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    start_parser.add_argument("--reload", action="store_true", help="Auto-reload on changes")

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Send chat message")
    chat_parser.add_argument("message", help="Message to send")
    chat_parser.add_argument("--api-url", default="http://localhost:8000", help="API URL")
    chat_parser.add_argument("--workspace", help="Workspace ID")

    # Agent command
    agent_parser = subparsers.add_parser("agent", help="Run agent task")
    agent_parser.add_argument("--type", required=True, help="Agent type")
    agent_parser.add_argument("--task", required=True, help="Task description")
    agent_parser.add_argument("--priority", default="normal", help="Task priority")
    agent_parser.add_argument("--api-url", default="http://localhost:8000", help="API URL")
    agent_parser.add_argument("--wait", action="store_true", help="Wait for completion")

    # Status command
    subparsers.add_parser("status", help="Check brain system status")

    # Test command
    test_parser = subparsers.add_parser("test", help="Run integration tests")
    test_parser.add_argument("--api-url", default="http://localhost:8000", help="API URL")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to command handler
    if args.command == "start":
        return cmd_start(args)
    elif args.command == "chat":
        return asyncio.run(cmd_chat(args))
    elif args.command == "agent":
        return asyncio.run(cmd_agent(args))
    elif args.command == "status":
        return cmd_status(args)
    elif args.command == "test":
        return asyncio.run(cmd_test(args))

    return 0


if __name__ == "__main__":
    sys.exit(main())
