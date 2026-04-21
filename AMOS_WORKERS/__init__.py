#!/usr/bin/env python3
"""AMOS Workers - Task Execution Units

Specialized execution units responsible for task categories.
Analogous to specialized cells or subsystems in biological systems.

Workers:
- code_worker: Code generation and refactoring
- analyst: Breakdown complex questions  
- auditor: Check reasoning and enforce invariants
- planner: Create stepwise plans
"""

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class WorkerResponse:
    """Response from a worker execution."""
    role: str
    action: str
    summary: str
    details: dict[str, Any]


class WorkerRegistry:
    """Registry of available workers."""
    
    def __init__(self):
        self._workers: dict[str, Callable] = {}
        
    def register(self, name: str, func: Callable) -> None:
        """Register a worker function."""
        self._workers[name] = func
        
    def get(self, name: str) -> Callable | None:
        """Get a worker by name."""
        return self._workers.get(name)
        
    def list_workers(self) -> list[str]:
        """List all registered workers."""
        return list(self._workers.keys())


# Global registry
WORKER_REGISTRY = WorkerRegistry()


def code_worker(action: str, payload: dict[str, Any]) -> WorkerResponse:
    """Code generation and refactoring worker."""
    return WorkerResponse(
        role="code_worker",
        action=action,
        summary="Proposed code changes",
        details={
            "action": action,
            "payload": payload,
            "status": "draft"
        }
    )


def analyst_worker(action: str, payload: dict[str, Any]) -> WorkerResponse:
    """Analysis worker for complex questions."""
    return WorkerResponse(
        role="analyst",
        action=action,
        summary="Multi-step analysis",
        details={
            "steps": [
                "Clarify main question",
                "List constraints and invariants",
                "Map actors and systems",
                "Identify uncertainties",
                "Propose testable plan"
            ],
            "payload": payload
        }
    )


def auditor_worker(action: str, payload: dict[str, Any]) -> WorkerResponse:
    """Audit worker for reasoning validation."""
    return WorkerResponse(
        role="auditor",
        action=action,
        summary="Reasoning check",
        details={
            "checks": [
                "Structural integrity",
                "Invariant compliance",
                "Risk assessment",
                "Decision traceability"
            ],
            "payload": payload
        }
    )


def planner_worker(action: str, payload: dict[str, Any]) -> WorkerResponse:
    """Planning worker for goal decomposition."""
    return WorkerResponse(
        role="planner",
        action=action,
        summary="Stepwise plan created",
        details={
            "plan_structure": [
                "Goal definition",
                "Dependency mapping",
                "Resource allocation",
                "Timeline estimation",
                "Checkpoint definition"
            ],
            "payload": payload
        }
    )


# Register workers
WORKER_REGISTRY.register("code", code_worker)
WORKER_REGISTRY.register("analyst", analyst_worker)
WORKER_REGISTRY.register("auditor", auditor_worker)
WORKER_REGISTRY.register("planner", planner_worker)
