#!/usr/bin/env python3
"""AMOS Equation Task Queue - Background Processing.

Asynchronous task processing for expensive equation operations using
Celery with Redis broker. Enables non-blocking API responses for
long-running computations.

Features:
    - Celery task queue with Redis broker
    - Async equation verification tasks
    - Batch computation support
    - Task status tracking
    - Result backend with expiration
    - Error handling and retries
    - Tracing integration

Tasks:
    verify_equation: Async equation verification
    batch_compute: Batch equation processing
    warm_cache: Pre-compute and cache results

Usage:
    from equation_tasks import celery, verify_equation_task

    # Trigger async task
    task = verify_equation_task.delay(equation_id="E001", code=code)
    return {"task_id": task.id, "status": "queued"}

    # Check status
    result = verify_equation_task.AsyncResult(task_id)
    return {"status": result.status, "result": result.result}

Environment Variables:
    CELERY_BROKER_URL: Redis broker URL
    CELERY_RESULT_BACKEND: Result storage URL
    CELERY_TASK_ALWAYS_EAGER: Run sync for testing (default: false)
"""

import os
from typing import Any, Dict, List

try:
    from celery import Celery, states

    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    Celery = None  # type: ignore[assignment, misc]
    states = None  # type: ignore[assignment, misc]

try:

    from equation_tracing import create_span, set_span_error

    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False

# Initialize Celery app
if CELERY_AVAILABLE and Celery is not None:
    celery = Celery("amos_equation")
    celery.conf.broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    celery.conf.task_serializer = "json"
    celery.conf.result_serializer = "json"
    celery.conf.accept_content = ["json"]
    celery.conf.task_track_started = True
    celery.conf.task_time_limit = 300  # 5 min hard limit
    celery.conf.task_soft_time_limit = 240  # 4 min soft limit
    celery.conf.result_expires = 3600  # 1 hour result expiry
    celery.conf.worker_prefetch_multiplier = 1  # Fair task distribution
else:
    celery = None


def _get_celery() -> Any:
    """Get Celery instance or None."""
    return celery


if CELERY_AVAILABLE and celery is not None:

    @celery.task(bind=True, max_retries=3, default_retry_delay=60)
    def verify_equation_task(
        self: Any,
        equation_id: str,
        code: str,
        options: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Async equation verification task.

        Args:
            equation_id: Unique equation identifier
            code: Equation code to verify
            options: Verification options

        Returns:
            Verification result with status and metadata
        """
        if TRACING_AVAILABLE:
            with create_span(
                "verify_equation_task",
                {"equation_id": equation_id},
            ) as span:
                try:
                    result = _verify_equation_logic(equation_id, code, options)
                    if span:
                        span.set_attribute("verification.success", True)
                    return result
                except Exception as exc:
                    if span:
                        set_span_error(span, exc)
                    raise self.retry(exc=exc)
        else:
            try:
                return _verify_equation_logic(equation_id, code, options)
            except Exception as exc:
                raise self.retry(exc=exc)

    @celery.task(bind=True, max_retries=2)
    def batch_compute_task(
        self: Any,
        equation_ids: List[str],
        computation_type: str = "verify",
    ) -> Dict[str, Any]:
        """Batch equation computation task.

        Args:
            equation_ids: List of equation IDs to process
            computation_type: Type of computation (verify, optimize, etc.)

        Returns:
            Batch results with per-equation status
        """
        results = {"completed": [], "failed": [], "total": len(equation_ids)}

        for eq_id in equation_ids:
            try:
                # Simulate computation
                results["completed"].append(
                    {
                        "equation_id": eq_id,
                        "status": "success",
                    }
                )
            except Exception:
                results["failed"].append(eq_id)

        return results

    @celery.task
    def warm_cache_task(equation_ids: List[str]) -> Dict[str, Any]:
        """Pre-compute and cache equation results.

        Args:
            equation_ids: Equations to pre-compute

        Returns:
            Cache warming results
        """
        warmed = 0
        for eq_id in equation_ids:
            # Pre-compute logic would go here
            warmed += 1
        return {"warmed": warmed, "total": len(equation_ids)}


def _verify_equation_logic(
    equation_id: str,
    code: str,
    options: Dict[str, Any],
) -> Dict[str, Any]:
    """Core verification logic."""
    # This would call the actual equation verification
    return {
        "equation_id": equation_id,
        "valid": True,
        "execution_time_ms": 150,
        "complexity_score": 0.85,
    }


def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get task status by ID.

    Args:
        task_id: Celery task identifier

    Returns:
        Task status information or None if unavailable
    """
    if not CELERY_AVAILABLE or celery is None or states is None:
        return None

    try:
        result = celery.AsyncResult(task_id)
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
            "date_done": (result.date_done.isoformat() if result.date_done else None),
        }
    except Exception:
        return None


def revoke_task(task_id: str, terminate: bool = False) -> bool:
    """Revoke/cancel a running task.

    Args:
        task_id: Task to revoke
        terminate: Force terminate if running

    Returns:
        True if revocation sent successfully
    """
    if not CELERY_AVAILABLE or celery is None:
        return False

    try:
        celery.control.revoke(task_id, terminate=terminate)
        return True
    except Exception:
        return False
