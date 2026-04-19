#!/usr/bin/env python3

"""AMOS Brain CLI - Command-line interface for brain-powered operations.

Commands:
  process <task>     Process task synchronously
  submit <task>        Submit task to queue
  status <task_id>     Check task status
  queue                Show queue status
  health               Brain health check

Owner: Trang Phan
"""

import asyncio
import sys
from typing import List

try:
    from .api_integration import (
        brain_get_result,
        brain_process_sync,
        brain_submit_task,
        get_brain_api,
    )
except ImportError:
    from api_integration import (
        brain_get_result,
        brain_process_sync,
        brain_submit_task,
        get_brain_api,
    )


class BrainCLI:
    """Command-line interface for AMOS brain."""

    def __init__(self):
        self.commands = {
            "process": self.cmd_process,
            "submit": self.cmd_submit,
            "status": self.cmd_status,
            "queue": self.cmd_queue,
            "health": self.cmd_health,
            "help": self.cmd_help,
        }

    async def run(self, args: List[str]) -> int:
        """Run CLI with arguments."""
        if not args or args[0] in ("help", "-h", "--help"):
            return await self.cmd_help()

        cmd = args[0]
        if cmd not in self.commands:
            print(f"Unknown command: {cmd}")
            print("Run 'brain_cli.py help' for usage")
            return 1

        return await self.commands[cmd](args[1:])

    async def cmd_process(self, args: List[str]) -> int:
        """Process task synchronously."""
        if not args:
            print("Usage: process <task description>")
            return 1

        description = " ".join(args)
        print(f"Processing: {description[:60]}...")

        result = await brain_process_sync(description, "HIGH")

        print("\nResult:")
        print(f"  Task ID: {result['task_id']}")
        print(f"  Domain: {result['domain']}")
        print(f"  Success: {result['success']}")
        print(f"  Duration: {result['duration_ms']:.1f}ms")
        print(f"  Engines: {', '.join(result['engines_used'][:3])}")
        return 0

    async def cmd_submit(self, args: List[str]) -> int:
        """Submit task to queue."""
        if not args:
            print("Usage: submit <task description>")
            return 1

        description = " ".join(args)
        result = await brain_submit_task(description, "MEDIUM")

        print(f"Submitted: {result['task_id']}")
        print(f"Priority: {result['priority']}")
        print(f"\nCheck status with: python brain_cli.py status {result['task_id']}")
        return 0

    async def cmd_status(self, args: List[str]) -> int:
        """Check task status."""
        if not args:
            print("Usage: status <task_id>")
            return 1

        task_id = args[0]
        task = await brain_get_result(task_id)

        if not task:
            print(f"Task not found: {task_id}")
            return 1

        print(f"Task: {task_id}")
        print(f"  Description: {task['description'][:50]}...")
        print(f"  Status: {task['status']}")
        print(f"  Priority: {task['priority']}")

        if task.get("result"):
            print(f"  Domain: {task['result'].get('domain')}")
            print(f"  Duration: {task['result'].get('duration_ms', 0):.1f}ms")

        if task.get("error"):
            print(f"  Error: {task['error']}")

        return 0

    async def cmd_queue(self, args: List[str]) -> int:
        """Show queue status."""
        try:
            from .task_queue import get_task_queue
        except ImportError:
            from task_queue import get_task_queue

        queue = await get_task_queue()
        tasks = queue.list_tasks()

        print("Queue Status:")
        print(f"  Workers: {queue._max_workers}")
        print(f"  Total tasks: {len(tasks)}")

        pending = sum(1 for t in tasks if t.status.value == "pending")
        running = sum(1 for t in tasks if t.status.value == "running")
        completed = sum(1 for t in tasks if t.status.value == "completed")
        failed = sum(1 for t in tasks if t.status.value == "failed")

        print("\nTasks by status:")
        print(f"  Pending: {pending}")
        print(f"  Running: {running}")
        print(f"  Completed: {completed}")
        print(f"  Failed: {failed}")

        if tasks:
            print("\nRecent tasks:")
            for task in list(tasks)[-5:]:
                icon = {
                    "pending": "⏳",
                    "running": "▶️",
                    "completed": "✓",
                    "failed": "✗",
                }.get(task.status.value, "?")
                print(f"  {icon} {task.id}: {task.request.description[:40]}...")

        return 0

    async def cmd_health(self, args: List[str]) -> int:
        """Check brain health."""
        api = await get_brain_api()
        health = await api.health_check()

        print("Brain Health:")
        print(f"  Status: {health['status']}")
        print(f"  Initialized: {health['initialized']}")
        print(f"  Workers: {health.get('workers', 0)}")

        if health["status"] == "healthy":
            print("\n✓ Brain operational")
        else:
            print(f"\n✗ Brain unhealthy: {health.get('error')}")
            return 1

        return 0

    async def cmd_help(self, args: List[str] = None) -> int:
        """Show help."""
        print("AMOS Brain CLI")
        print("=" * 60)
        print("\nCommands:")
        print("  process <task>      Process task synchronously")
        print("  submit <task>       Submit task to queue")
        print("  status <task_id>    Check task status")
        print("  queue               Show queue status")
        print("  health              Brain health check")
        print("  help                Show this help")
        print("\nExamples:")
        print('  python brain_cli.py process "Design API"')
        print('  python brain_cli.py submit "Optimize queries"')
        print("  python brain_cli.py status queue-abc123")
        print("=" * 60)
        return 0


async def main() -> int:
    """Main entry point."""
    cli = BrainCLI()
    return await cli.run(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
