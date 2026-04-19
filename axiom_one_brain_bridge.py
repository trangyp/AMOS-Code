#!/usr/bin/env python3
"""
Axiom One Brain Bridge

Connects the standalone Axiom One server to the AMOS brain for cognitive capabilities.
Provides a lightweight HTTP bridge that forwards requests to the brain.

Owner: Trang Phan
Version: 1.0.0
"""

import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

# Add repo root to path
_REPO_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(_REPO_ROOT / "clawspring" / "amos_brain"))
sys.path.insert(0, str(_REPO_ROOT))

# Try to import the real AMOS brain (amos_brain_working has the actual think function)
try:
    from amos_brain_working import think as amos_think

    _BRAIN_AVAILABLE = True
except ImportError:
    _BRAIN_AVAILABLE = False
    amos_think = None


@dataclass
class BrainTask:
    """Task for brain processing."""

    id: str
    query: str
    context: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    result: Dict[str, Any] = None
    error: str = None
    completed_at: datetime = None


class AxiomOneBrainBridge:
    """Bridge between Axiom One and AMOS Brain."""

    def __init__(self):
        """Initialize the brain bridge."""
        self._think_func = amos_think if _BRAIN_AVAILABLE else None
        self._initialized = _BRAIN_AVAILABLE
        self._tasks: Dict[str, BrainTask] = {}
        self._stats = {"total": 0, "completed": 0, "failed": 0, "pending": 0}
        self._lock = Lock()

    def _ensure_initialized(self) -> bool:
        """Ensure brain connection is initialized."""
        if self._initialized:
            return True

        if not _BRAIN_AVAILABLE:
            return False

        try:
            self._initialized = True
            return True
        except Exception as e:
            print(f"Brain initialization failed: {e}")
            return False

    def think(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Use brain to think about a query using real AMOS brain."""
        with self._lock:
            task_id = str(uuid.uuid4())
            self._stats["total"] += 1
            self._stats["pending"] += 1

        task = BrainTask(
            id=task_id,
            query=query,
            context=context or {},
            status="pending",
            created_at=datetime.now(timezone.utc),
        )
        self._tasks[task_id] = task

        if not self._ensure_initialized():
            task.status = "failed"
            task.error = "Brain not available"
            with self._lock:
                self._stats["pending"] -= 1
                self._stats["failed"] += 1
            return {
                "status": "error",
                "error": "Brain not available",
                "brain_available": False,
                "task_id": task_id,
            }

        try:
            task.status = "running"
            # Use the real think function from amos_brain_working
            result = self._think_func(query, context or {})
            task.status = "completed"
            task.completed_at = datetime.now(timezone.utc)
            task.result = result

            with self._lock:
                self._stats["pending"] -= 1
                self._stats["completed"] += 1

            return {
                "status": result.get("status", "success"),
                "result": result,
                "brain_available": True,
                "task_id": task_id,
                "legality": result.get("legality"),
                "brain_used": result.get("brain_used", True),
            }
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.now(timezone.utc)

            with self._lock:
                self._stats["pending"] -= 1
                self._stats["failed"] += 1

            return {
                "status": "error",
                "error": str(e),
                "brain_available": True,
                "task_id": task_id,
            }

    def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Analyze code using brain cognitive capabilities."""
        prompt = f"""Analyze this {language} code:

```{language}
{code}
```

Provide:
1. A summary of what the code does
2. Potential bugs or issues
3. Security concerns
4. Performance considerations
5. Best practices that should be applied"""

        return self.think(prompt, domain="code_review")

    def suggest_fixes(
        self, code: str, issues: List[str], language: str = "python"
    ) -> Dict[str, Any]:
        """Suggest fixes for identified issues."""
        prompt = f"""Given this {language} code with these issues:

Issues: {', '.join(issues)}

Code:
```{language}
{code}
```

Provide specific fixes with code examples."""

        return self.think(prompt, domain="code_fix")

    def explain_architecture(self, file_tree: List[str], repo_name: str) -> Dict[str, Any]:
        """Explain repository architecture."""
        prompt = f"""Analyze the architecture of repository '{repo_name}':

File structure:
{chr(10).join(file_tree[:50])}

Provide:
1. Architectural pattern (if identifiable)
2. Layer/module organization
3. Key components and their roles
4. Suggested improvements"""

        return self.think(prompt, domain="architecture")

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status."""
        task = self._tasks.get(task_id)
        if task is None:
            return None

        return {
            "task_id": task.task_id,
            "status": task.status,
            "query": task.query,
            "domain": task.domain,
            "created_at": task.created_at,
            "result": task.result,
            "error": task.error,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get bridge statistics."""
        total = len(self._tasks)
        completed = sum(1 for t in self._tasks.values() if t.status == "completed")
        failed = sum(1 for t in self._tasks.values() if t.status == "failed")
        pending = sum(1 for t in self._tasks.values() if t.status == "pending")

        return {
            "initialized": self._initialized,
            "brain_available": _BRAIN_AVAILABLE,
            "total_tasks": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
        }


# Global bridge instance
_bridge: Optional[AxiomOneBrainBridge] = None


def get_brain_bridge() -> AxiomOneBrainBridge:
    """Get or create global brain bridge."""
    global _bridge
    if _bridge is None:
        _bridge = AxiomOneBrainBridge()
    return _bridge


if __name__ == "__main__":
    # Test the bridge
    bridge = get_brain_bridge()

    print("Testing Axiom One Brain Bridge...")
    print(f"Brain available: {_BRAIN_AVAILABLE}")

    if bridge.initialize():
        print("✓ Brain initialized")

        # Test code analysis
        test_code = """
def process_data(data):
    result = []
    for item in data:
        if item['value'] > 10:
            result.append(item)
    return result
"""
        result = bridge.analyze_code(test_code)
        print("\nCode analysis result:")
        print(f"  Success: {result.get('success')}")
        if result.get("success"):
            print(f"  Content preview: {result.get('content', '')[:100]}...")
    else:
        print("✗ Brain not available - standalone mode only")
