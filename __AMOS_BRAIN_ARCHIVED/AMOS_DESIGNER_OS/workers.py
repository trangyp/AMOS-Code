from dataclasses import dataclass
from typing import Any


@dataclass
class WorkerResponse:
    role: str
    action: str
    summary: str
    details: dict[str, Any]


def _ensure_text(payload: dict[str, Any], key: str, default: str = "") -> str:
    value = payload.get(key, default)
    return str(value)


def code_worker(action: str, payload: dict[str, Any]) -> WorkerResponse:
    description = _ensure_text(payload, "description", "")
    context = _ensure_text(payload, "context", "")
    return WorkerResponse(
        role="code_worker",
        action=action,
        summary="Proposed high-level code change (no files touched).",
        details={
            "description": description,
            "context": context,
            "pseudo_code": [
                "# TODO: implement this change in actual code with a developer or AI pair.",
                "# This is a safe, non-destructive draft.",
            ],
        },
    )


def analyst_worker(action: str, payload: dict[str, Any]) -> WorkerResponse:
    topic = _ensure_text(payload, "topic", "")
    return WorkerResponse(
        role="analyst",
        action=action,
        summary="Multi-step breakdown for topic.",
        details={
            "topic": topic,
            "steps": [
                "Clarify the main question.",
                "List known constraints and invariants.",
                "Map actors, systems, and time horizons.",
                "Identify missing data or uncertainties.",
                "Propose a simple, testable plan.",
            ],
        },
    )


def auditor_worker(action: str, payload: dict[str, Any]) -> WorkerResponse:
    plan = payload.get("plan") or []
    findings: list[str] = []
    if not plan:
        findings.append("No plan provided for audit.")
    else:
        findings.append(f"Plan has {len(plan)} step(s). Basic structure OK.")
        findings.append("Check that each step is reversible and logged.")
    return WorkerResponse(
        role="auditor",
        action=action,
        summary="Audit of reasoning or plan.",
        details={
            "findings": findings,
            "risk_flags": [],
            "invariants_checked": [
                "reversibility",
                "logging_required",
                "no irreversible action without human confirmation",
            ],
        },
    )


def planner_worker(action: str, payload: dict[str, Any]) -> WorkerResponse:
    goal = _ensure_text(payload, "goal", "")
    horizon = _ensure_text(payload, "horizon", "short-term")
    return WorkerResponse(
        role="planner",
        action=action,
        summary="Structured plan generated from goal.",
        details={
            "goal": goal,
            "horizon": horizon,
            "plan": [
                "Step 1: Clarify desired end-state in natural language.",
                "Step 2: Identify constraints and non-negotiables.",
                "Step 3: Enumerate 3–5 minimal actions.",
                "Step 4: Define success metrics.",
                "Step 5: Decide review schedule and audit criteria.",
            ],
        },
    )


WORKER_REGISTRY = {
    "code_worker": code_worker,
    "analyst": analyst_worker,
    "auditor": auditor_worker,
    "planner": planner_worker,
}
