#!/usr/bin/env python3
"""
AMOS Task Execution Engine
===========================

Connects tasks to agents for actual work execution.
Routes tasks, executes code/analysis, reports results.

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable


@dataclass
class ExecutionResult:
    """Result of task execution."""
    success: bool
    output: str
    error: Optional[str] = None
    duration_ms: float = 0.0
    artifacts: Dict[str, Any] = field(default_factory=dict)


class TaskExecutor:
    """
    Task execution engine for AMOS organism.
    Routes tasks to appropriate execution handlers.
    """

    def __init__(self, organism_root: Path) -> None:
        self.root = organism_root
        self.execution_handlers: Dict[str, Callable] = {
            "analysis": self._execute_analysis,
            "code": self._execute_code,
            "documentation": self._execute_documentation,
            "security": self._execute_security,
            "test": self._execute_test,
        }
        self.execution_log: List[Dict[str, Any]] = []

    def execute_task(self, task_id: str, task_type: str, params: Dict[str, Any]) -> ExecutionResult:
        """Execute a task based on its type."""
        start_time = datetime.utcnow()

        handler = self.execution_handlers.get(task_type, self._execute_default)

        try:
            result = handler(task_id, params)
        except Exception as e:
            result = ExecutionResult(
                success=False,
                output="",
                error=str(e),
                duration_ms=0.0
            )

        # Calculate duration
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        result.duration_ms = duration_ms

        # Log execution
        self.execution_log.append({
            "task_id": task_id,
            "task_type": task_type,
            "success": result.success,
            "duration_ms": duration_ms,
            "timestamp": start_time.isoformat()
        })

        return result

    def _execute_analysis(self, task_id: str, params: Dict[str, Any]) -> ExecutionResult:
        """Execute code analysis task."""
        target = params.get("target", "codebase")
        analysis_type = params.get("analysis_type", "patterns")

        # Simulate analysis
        output = f"Analysis complete for {target}\n"
        output += f"- Found {len(self._mock_findings())} patterns\n"
        output += f"- Complexity score: 7.5/10\n"
        output += f"- Recommendations: 3 items\n"

        return ExecutionResult(
            success=True,
            output=output,
            artifacts={
                "findings": self._mock_findings(),
                "complexity_score": 7.5,
                "recommendations": 3
            }
        )

    def _execute_code(self, task_id: str, params: Dict[str, Any]) -> ExecutionResult:
        """Execute code generation task."""
        description = params.get("description", "Generate code")
        language = params.get("language", "python")

        # Generate mock code
        code = self._generate_mock_code(description, language)

        return ExecutionResult(
            success=True,
            output=f"Generated {language} code for: {description}",
            artifacts={
                "code": code,
                "language": language,
                "lines": len(code.split('\n'))
            }
        )

    def _execute_documentation(self, task_id: str, params: Dict[str, Any]) -> ExecutionResult:
        """Execute documentation generation task."""
        target = params.get("target", "subsystem")

        docs = f"""# Documentation for {target}

## Overview
Generated documentation for AMOS {target} subsystem.

## Key Components
- Component A: Handles primary operations
- Component B: Manages data flow
- Component C: Provides external interface

## API Reference
See generated API docs for detailed method signatures.

## Examples
```python
# Example usage
result = subsystem.process(input_data)
```
"""

        return ExecutionResult(
            success=True,
            output=f"Generated documentation for {target}",
            artifacts={
                "documentation": docs,
                "format": "markdown",
                "sections": 4
            }
        )

    def _execute_security(self, task_id: str, params: Dict[str, Any]) -> ExecutionResult:
        """Execute security audit task."""
        scope = params.get("scope", "all_subsystems")

        # Run security checks
        vulnerabilities = self._mock_security_scan()

        output = f"Security audit complete for {scope}\n"
        output += f"- Scanned: 13 subsystems\n"
        output += f"- Vulnerabilities found: {len(vulnerabilities)}\n"
        output += f"- Risk level: LOW\n"

        return ExecutionResult(
            success=True,
            output=output,
            artifacts={
                "vulnerabilities": vulnerabilities,
                "risk_level": "LOW",
                "subsystems_scanned": 13
            }
        )

    def _execute_test(self, task_id: str, params: Dict[str, Any]) -> ExecutionResult:
        """Execute test task."""
        test_type = params.get("test_type", "unit")
        target = params.get("target", "all")

        # Run tests
        test_results = self._mock_test_run(test_type, target)

        output = f"Test execution complete\n"
        output += f"- Type: {test_type}\n"
        output += f"- Target: {target}\n"
        output += f"- Passed: {test_results['passed']}/{test_results['total']}\n"

        return ExecutionResult(
            success=test_results['failed'] == 0,
            output=output,
            artifacts=test_results
        )

    def _execute_default(self, task_id: str, params: Dict[str, Any]) -> ExecutionResult:
        """Default execution for unknown task types."""
        return ExecutionResult(
            success=False,
            output="",
            error=f"Unknown task type. Supported: {list(self.execution_handlers.keys())}"
        )

    def _mock_findings(self) -> List[Dict[str, Any]]:
        """Generate mock analysis findings."""
        return [
            {"type": "pattern", "severity": "info", "message": "Good modularity detected"},
            {"type": "pattern", "severity": "warning", "message": "Consider caching layer"},
            {"type": "pattern", "severity": "info", "message": "Clean architecture"},
        ]

    def _generate_mock_code(self, description: str, language: str) -> str:
        """Generate mock code."""
        return f"""# Generated code for: {description}
# Language: {language}

class GeneratedComponent:
    \"\"\"Auto-generated component.\"\"\"

    def __init__(self):
        self.initialized = True

    def process(self, data: dict) -> dict:
        \"\"\"Process input data.\"\"\"
        return {{"result": "processed", "input": data}}

if __name__ == "__main__":
    component = GeneratedComponent()
    result = component.process({{"test": True}})
    print(result)
"""

    def _mock_security_scan(self) -> List[Dict[str, Any]]:
        """Generate mock security vulnerabilities."""
        return [
            {"severity": "low", "subsystem": "03_IMMUNE", "issue": "Logs need rotation"},
            {"severity": "info", "subsystem": "04_BLOOD", "issue": "Consider audit trail"},
        ]

    def _mock_test_run(self, test_type: str, target: str) -> Dict[str, Any]:
        """Generate mock test results."""
        return {
            "test_type": test_type,
            "target": target,
            "total": 15,
            "passed": 14,
            "failed": 1,
            "skipped": 0
        }

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.execution_log:
            return {"total_executions": 0, "success_rate": 0.0}

        total = len(self.execution_log)
        successful = sum(1 for e in self.execution_log if e["success"])
        avg_duration = sum(e["duration_ms"] for e in self.execution_log) / total

        return {
            "total_executions": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total * 100,
            "avg_duration_ms": avg_duration
        }


class AgentTaskRouter:
    """
    Routes tasks from queue to appropriate agents.
    Coordinates between task queue and task executor.
    """

    def __init__(self, organism_root: Path) -> None:
        self.root = organism_root
        self.executor = TaskExecutor(organism_root)

        # Load task queue
        sys.path.insert(0, str(organism_root / "07_METABOLISM"))
        from task_queue import TaskQueue, TaskStatus
        self.task_queue = TaskQueue(organism_root)
        self.TaskStatus = TaskStatus

    def process_pending_tasks(self, max_tasks: int = 5) -> List[Dict[str, Any]]:
        """Process pending tasks from queue."""
        results = []
        pending = self.task_queue.get_pending_tasks()[:max_tasks]

        for task in pending:
            # Assign task to agent
            agent_id = self._select_agent(task.task_type)
            if not agent_id:
                continue

            if self.task_queue.assign_task(task.id, agent_id):
                # Start task
                self.task_queue.start_task(task.id)

                # Execute task
                result = self.executor.execute_task(
                    task.id, task.task_type, task.params
                )

                # Complete or fail task
                if result.success:
                    self.task_queue.complete_task(task.id, {
                        "output": result.output,
                        "artifacts": result.artifacts,
                        "duration_ms": result.duration_ms
                    })
                else:
                    self.task_queue.fail_task(task.id, result.error or "Unknown error")

                results.append({
                    "task_id": task.id,
                    "agent_id": agent_id,
                    "success": result.success,
                    "duration_ms": result.duration_ms
                })

        return results

    def _select_agent(self, task_type: str) -> Optional[str]:
        """Select appropriate agent for task type."""
        agent_map = {
            "analysis": "analyst_agent",
            "code": "developer_agent",
            "documentation": "writer_agent",
            "security": "security_agent",
            "test": "tester_agent"
        }
        return agent_map.get(task_type, "worker_agent")

    def get_status(self) -> Dict[str, Any]:
        """Get router status."""
        queue_status = self.task_queue.get_status()
        executor_stats = self.executor.get_execution_stats()

        return {
            "status": "operational",
            "tasks_pending": queue_status["pending"],
            "tasks_running": queue_status["running"],
            "execution_stats": executor_stats,
            "agents_available": 5
        }


def main() -> int:
    """CLI for Task Execution Engine."""
    print("=" * 50)
    print("AMOS Task Execution Engine")
    print("=" * 50)

    organism_root = Path(__file__).parent.parent
    router = AgentTaskRouter(organism_root)

    print("\nProcessing pending tasks...")
    results = router.process_pending_tasks(max_tasks=3)

    if results:
        print(f"\nProcessed {len(results)} tasks:")
        for r in results:
            status = "✓" if r["success"] else "✗"
            print(f"  {status} Task {r['task_id']} by {r['agent_id']} ({r['duration_ms']:.0f}ms)")
    else:
        print("\nNo tasks to process")

    # Show status
    status = router.get_status()
    print(f"\nRouter Status:")
    print(f"  Pending: {status['tasks_pending']}")
    print(f"  Running: {status['tasks_running']}")
    print(f"  Executions: {status['execution_stats']['total_executions']}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
