from typing import Any

"""AMOS Brain API Integration - FastAPI-compatible brain interface.

Provides high-level API endpoints for brain cognitive operations
with proper error handling and async support.
"""
from __future__ import annotations


import asyncio

from .facade import BrainClient
from .super_brain import SuperBrainRuntime, get_super_brain


class BrainAPI:
    """API layer for brain operations.

    Wraps BrainClient and SuperBrain for FastAPI integration.
    """

    def __init__(self) -> None:
        self._client: BrainClient | None = None
        self._super_brain: SuperBrainRuntime | None = None
        self._initialized = False

    def initialize(self) -> None:
        """Initialize brain connections."""
        if not self._initialized:
            self._client = BrainClient()
            self._super_brain = get_super_brain()
            self._initialized = True

    def think(self, query: str, domain: str = "general") -> dict[str, Any]:
        """Process a cognitive query.

        Args:
            query: The question or task
            domain: Domain context

        Returns:
            Response dict with content, confidence, metadata
        """
        self.initialize()
        if self._client is None:
            return {
                "success": False,
                "content": "Brain not available",
                "confidence": "low",
                "error": "Client initialization failed",
            }

        try:
            response = self._client.think(query, domain=domain)
            return {
                "success": response.success,
                "content": response.content,
                "reasoning": response.reasoning,
                "confidence": response.confidence,
                "law_compliant": response.law_compliant,
                "violations": response.violations,
                "metadata": response.metadata,
            }
        except Exception as e:
            return {
                "success": False,
                "content": str(e),
                "confidence": "low",
                "error": type(e).__name__,
            }

    async def think_async(self, query: str, domain: str = "general") -> dict[str, Any]:
        """Async version of think."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.think, query, domain)

    def get_stats(self) -> dict[str, Any]:
        """Get brain statistics."""
        self.initialize()
        if self._super_brain is None:
            return {"status": "unavailable"}

        try:
            return self._super_brain.get_status()
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Global instance
_brain_api: BrainAPI | None = None


def get_brain_api() -> BrainAPI:
    """Get or create global BrainAPI instance."""
    global _brain_api
    if _brain_api is None:
        _brain_api = BrainAPI()
    return _brain_api


# Convenience functions for direct usage
def brain_process_sync(query: str, domain: str = "general") -> dict[str, Any]:
    """Synchronous brain processing.

    Args:
        query: The query to process
        domain: Domain context

    Returns:
        Processing result dict
    """
    return get_brain_api().think(query, domain)


async def brain_submit_task(task_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Submit a task to the brain task queue.

    Args:
        task_type: Type of task (think, decide, validate, etc.)
        payload: Task parameters

    Returns:
        Task submission result with task_id
    """
    api = get_brain_api()
    api.initialize()

    import uuid

    task_id = f"task_{uuid.uuid4().hex[:12]}"

    if task_type == "think":
        query = payload.get("query", "")
        domain = payload.get("domain", "general")
        result = await api.think_async(query, domain)
        result["task_id"] = task_id
        result["type"] = "think"
        return result
    elif task_type == "stats":
        return {"task_id": task_id, "type": "stats", "result": api.get_stats()}
    else:
        return {
            "success": False,
            "task_id": task_id,
            "error": f"Unknown task type: {task_type}",
            "supported_types": ["think", "stats"],
        }


def brain_get_result(task_id: str) -> dict[str, Any]:
    """Get result for a previously submitted task.

    Args:
        task_id: The task ID returned from brain_submit_task

    Returns:
        Task result dict or None if not found
    """
    # In a real implementation, this would query a task store
    # For now, return a placeholder indicating task lookup
    return {
        "task_id": task_id,
        "status": "completed",
        "found": False,
        "note": "Task store not implemented - results retrieved synchronously",
    }
