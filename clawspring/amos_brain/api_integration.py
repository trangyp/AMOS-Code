from typing import Any

"""AMOS Brain API Integration - FastAPI routes for brain-powered endpoints.

Real backend integration providing:
- Task submission via brain
- Status tracking
- Result retrieval

Owner: Trang Phan
"""
from __future__ import annotations


try:
    from .cognitive_task_processor import process_cognitive_task
    from .task_queue import get_task_queue, get_task_status, submit_task
except ImportError:
    from cognitive_task_processor import process_cognitive_task
    from task_queue import get_task_queue, get_task_status, submit_task


class BrainAPIIntegration:
    """Integrates AMOS brain with FastAPI backend."""

    def __init__(self):
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize brain connections."""
        try:
            await get_task_queue()
            self._initialized = True
            return True
        except Exception as e:
            print(f"[BrainAPI] Init failed: {e}")
            return False

    async def submit_brain_task(self, description: str, priority: str = "MEDIUM") -> Dict[str, Any]:
        """Submit task to brain-powered queue."""
        if not self._initialized:
            await self.initialize()

        task_id = await submit_task(description, priority)
        return {
            "task_id": task_id,
            "status": "submitted",
            "priority": priority,
        }

    async def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """Get task status and result."""
        task = await get_task_status(task_id)
        if not task:
            return None

        return {
            "task_id": task.id,
            "status": task.status.value,
            "description": task.request.description,
            "priority": task.request.priority,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "result": task.result,
            "error": task.error,
        }

    async def process_sync(self, description: str, priority: str = "MEDIUM") -> Dict[str, Any]:
        """Process task synchronously using brain."""
        import asyncio

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None, lambda: process_cognitive_task(description, priority)
        )

        return {
            "task_id": response.task_id,
            "success": response.success,
            "domain": response.domain,
            "engines_used": response.engines_used,
            "duration_ms": response.duration_ms,
            "timestamp": response.timestamp,
            "result": response.result,
        }

    async def health_check(self) -> Dict[str, Any]:
        """Health check for brain integration."""
        try:
            queue = await get_task_queue()
            return {
                "status": "healthy",
                "initialized": self._initialized,
                "workers": queue._max_workers,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }


# Singleton
_api_integration: BrainAPIIntegration | None = None


async def get_brain_api() -> BrainAPIIntegration:
    """Get or create singleton API integration."""
    global _api_integration
    if _api_integration is None:
        _api_integration = BrainAPIIntegration()
        await _api_integration.initialize()
    return _api_integration


# Convenience functions
async def brain_submit_task(description: str, priority: str = "MEDIUM") -> Dict[str, Any]:
    """Submit task to brain."""
    api = await get_brain_api()
    return await api.submit_brain_task(description, priority)


async def brain_get_result(task_id: str) -> Dict[str, Any]:
    """Get task result."""
    api = await get_brain_api()
    return await api.get_task_result(task_id)


async def brain_process_sync(description: str, priority: str = "MEDIUM") -> Dict[str, Any]:
    """Process task synchronously."""
    api = await get_brain_api()
    return await api.process_sync(description, priority)


if __name__ == "__main__":

    async def main():
        print("=" * 60)
        print("AMOS BRAIN API INTEGRATION")
        print("=" * 60)

        # Test sync processing
        print("\n1. Synchronous Processing:")
        result = await brain_process_sync("Design microservices architecture", "HIGH")
        print(f"   Task: {result['task_id']}")
        print(f"   Domain: {result['domain']}")
        print(f"   Duration: {result['duration_ms']:.1f}ms")

        # Test async submission
        print("\n2. Asynchronous Submission:")
        submit_result = await brain_submit_task("Optimize API performance", "MEDIUM")
        task_id = submit_result["task_id"]
        print(f"   Submitted: {task_id}")

        # Wait and check
        await asyncio.sleep(2)
        task_status = await brain_get_result(task_id)
        if task_status:
            print(f"   Status: {task_status['status']}")
            if task_status.get("result"):
                print(f"   Domain: {task_status['result'].get('domain')}")

        # Health check
        print("\n3. Health Check:")
        api = await get_brain_api()
        health = await api.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Workers: {health.get('workers', 0)}")

        print("\n" + "=" * 60)

    asyncio.run(main())
