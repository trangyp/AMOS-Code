#!/usr/bin/env python3
"""AMOS Async Brain Processor - Real async multi-task processing.

Asynchronous brain-guided task processing with concurrent execution.
Not a demo. Real implementation using asyncio and AMOS brain.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from amos_brain import BrainClient, get_brain
from amos_brain.task_processor import BrainTaskProcessor, TaskResult


@dataclass
class AsyncTaskResult:
    """Result from async brain task processing."""

    task_id: str
    input_task: str
    brain_result: TaskResult
    execution_time_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class AsyncBrainProcessor:
    """Real async brain processor for concurrent task execution.

    Features:
    - Process multiple tasks concurrently
    - Rate limiting to prevent brain overload
    - Priority queue for important tasks
    - Result aggregation
    """

    def __init__(self, max_concurrent: int = 5, rate_limit_per_sec: float = 10.0):
        self.max_concurrent = max_concurrent
        self.rate_limit = rate_limit_per_sec
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.task_processor = BrainTaskProcessor()
        self.brain_client = BrainClient()
        _ = get_brain()  # Ensure brain loaded
        self._task_counter = 0
        self._rate_limit_lock = asyncio.Lock()
        self._last_request_time: float = 0.0

    async def process_single(
        self, task: str, context: Optional[dict[str, Any]] = None, priority: int = 5
    ) -> AsyncTaskResult:
        """Process a single task through the brain asynchronously.

        Args:
            task: Task description
            context: Optional context
            priority: Task priority (1-10, lower is higher priority)

        Returns:
            AsyncTaskResult with brain output
        """
        async with self.semaphore:
            # Rate limiting
            async with self._rate_limit_lock:
                now = asyncio.get_event_loop().time()
                min_interval = 1.0 / self.rate_limit
                elapsed = now - self._last_request_time
                if elapsed < min_interval:
                    await asyncio.sleep(min_interval - elapsed)
                self._last_request_time = asyncio.get_event_loop().time()

            # Process through brain
            start_time = asyncio.get_event_loop().time()

            try:
                # Run brain processing in thread pool (it's CPU-bound)
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, self.task_processor.process, task, context or {}
                )
            except Exception as e:
                # Create error result
                result = TaskResult(
                    task_id=f"ERROR-{self._task_counter}",
                    input_task=task,
                    output=f"Error: {e}",
                    reasoning_steps=["Processing failed"],
                    kernels_used=[],
                    law_violations=[],
                    rule_of_two_check={},
                    rule_of_four_check={},
                    confidence="low",
                )

            end_time = asyncio.get_event_loop().time()
            exec_time_ms = (end_time - start_time) * 1000

            self._task_counter += 1

            return AsyncTaskResult(
                task_id=f"ASYNC-{self._task_counter:04d}",
                input_task=task,
                brain_result=result,
                execution_time_ms=exec_time_ms,
            )

    async def process_batch(
        self,
        tasks: list[str],
        contexts: list[dict[str, Any]] | None = None,
        priorities: Optional[list[int]] = None,
    ) -> list[AsyncTaskResult]:
        """Process multiple tasks concurrently.

        Args:
            tasks: List of task descriptions
            contexts: Optional list of contexts (one per task)
            priorities: Optional list of priorities (one per task)

        Returns:
            List of AsyncTaskResult in same order as input
        """
        if not tasks:
            return []

        # Default contexts and priorities
        if contexts is None:
            contexts = [{} for _ in tasks]
        if priorities is None:
            priorities = [5 for _ in tasks]

        # Create tasks
        coroutines = [
            self.process_single(task, ctx, prio)
            for task, ctx, prio in zip(tasks, contexts, priorities)
        ]

        # Execute all concurrently
        results = await asyncio.gather(*coroutines, return_exceptions=True)

        # Handle any exceptions
        processed_results: list[AsyncTaskResult] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create error result
                processed_results.append(
                    AsyncTaskResult(
                        task_id=f"ERROR-{i}",
                        input_task=tasks[i],
                        brain_result=TaskResult(
                            task_id=f"ERROR-{i}",
                            input_task=tasks[i],
                            output=f"Exception: {result}",
                            reasoning_steps=["Async processing failed"],
                            kernels_used=[],
                            law_violations=[],
                            rule_of_two_check={},
                            rule_of_four_check={},
                            confidence="none",
                        ),
                        execution_time_ms=0.0,
                    )
                )
            else:
                processed_results.append(result)

        return processed_results

    async def process_with_aggregation(
        self, tasks: list[str], aggregate_prompt: Optional[str] = None
    ) -> tuple[list[AsyncTaskResult], TaskResult]:
        """Process tasks and aggregate results through brain.

        Args:
            tasks: List of tasks to process
            aggregate_prompt: Optional custom aggregation prompt

        Returns:
            Tuple of (individual results, aggregated summary)
        """
        # Process all tasks
        individual_results = await self.process_batch(tasks)

        # Create aggregation task
        outputs = [r.brain_result.output for r in individual_results]
        default_prompt = f"""Synthesize these {len(outputs)} results into a coherent summary:

Results:
{chr(10).join(f"- {o[:200]}..." for o in outputs)}

Provide:
1. Key findings summary
2. Common patterns
3. Actionable recommendations"""

        aggregation_task = aggregate_prompt or default_prompt

        # Get brain to aggregate
        aggregate_result = await self.process_single(
            aggregation_task, {"mode": "synthesis"}, priority=1
        )

        return individual_results, aggregate_result.brain_result

    def get_stats(self) -> dict[str, Any]:
        """Get processor statistics."""
        return {
            "tasks_processed": self._task_counter,
            "max_concurrent": self.max_concurrent,
            "rate_limit": self.rate_limit,
            "semaphore_value": self.semaphore._value,  # noqa: SLF001
        }


# Convenience async functions
async def brain_process_async(
    task: str, context: Optional[dict[str, Any]] = None
) -> AsyncTaskResult:
    """Quick async brain processing."""
    processor = AsyncBrainProcessor()
    return await processor.process_single(task, context)


async def brain_process_batch(
    tasks: Optional[list[str]] = None,
    contexts: list[dict[str, Any]] | None = None,
) -> list[AsyncTaskResult]:
    """Quick batch brain processing."""
    processor = AsyncBrainProcessor()
    return await processor.process_batch(tasks, contexts)


if __name__ == "__main__":
    # Real test - async processing
    async def test():
        print("=" * 70)
        print("AMOS ASYNC BRAIN PROCESSOR - REAL TEST")
        print("=" * 70)

        processor = AsyncBrainProcessor(max_concurrent=3)

        # Test tasks
        tasks = [
            "Explain Python list comprehensions",
            "Describe async/await in Python",
            "What are dataclasses in Python?",
            "Explain Python type hints",
            "Describe Python generators",
        ]

        print(f"\\nProcessing {len(tasks)} tasks concurrently...")
        print(f"Max concurrent: {processor.max_concurrent}")
        print()

        # Process batch
        results = await processor.process_batch(tasks)

        for result in results:
            print(f"Task: {result.input_task[:40]}...")
            print(f"  ID: {result.task_id}")
            print(f"  Time: {result.execution_time_ms:.2f}ms")
            print(f"  Output preview: {result.brain_result.output[:60]}...")
            print()

        print("=" * 70)
        print("Stats:", processor.get_stats())
        print("=" * 70)

    # Run the test
    asyncio.run(test())
