import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workers import WORKER_REGISTRY, WorkerResponse

BASE_DIR = Path(__file__).resolve().parent
BRAIN_FILE = BASE_DIR / "AMOS.brain"
CONFIG_FILE = BASE_DIR / "AMOS.config.json"
LOGS_DIR = BASE_DIR / "logs"
MEMORY_DIR = BASE_DIR / "memory"


@dataclass
class AmosEvent:
    timestamp: str
    event_type: str
    payload: dict[str, Any]


def _load_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    except UnicodeDecodeError:
        return ""


def _parse_brain(raw: str) -> dict[str, dict[str, str]]:
    sections: dict[str, dict[str, str]] = {}
    current: str | None = None
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1].strip()
            sections.setdefault(current, {})
            continue
        if current is None:
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            sections[current][key.strip()] = value.strip().strip('"')
    return sections


def _load_config() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _ensure_dirs() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def _log_event(event: AmosEvent) -> None:
    _ensure_dirs()
    log_path = LOGS_DIR / "amos.log"
    line = json.dumps(asdict(event), ensure_ascii=False)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def _pick_next_action(brain: dict[str, dict[str, str]]) -> str:
    nxt = brain.get("NEXT_ACTION", {}).get("next_action", "")
    return nxt or "map_global_requirements"


def _run_planner(brain: dict[str, dict[str, str]]) -> WorkerResponse:
    identity = brain.get("IDENTITY", {})
    goals = brain.get("GOALS", {})
    goal = goals.get("1", "Clarify system mission.")
    payload = {
        "goal": goal,
        "horizon": "medium-term",
        "identity": identity,
    }
    worker = WORKER_REGISTRY["planner"]
    return worker("generate_plan", payload)


def _run_analyst(brain: dict[str, dict[str, str]]) -> WorkerResponse:
    topic = _pick_next_action(brain)
    worker = WORKER_REGISTRY["analyst"]
    return worker("analyze_topic", {"topic": topic})


def _run_auditor(plan_resp: WorkerResponse) -> WorkerResponse:
    worker = WORKER_REGISTRY["auditor"]
    plan = plan_resp.details.get("plan") if isinstance(plan_resp.details, dict) else None
    return worker("audit_plan", {"plan": plan})


def main() -> None:
    print("=== AMOS Designer OS ===")
    print(f"Base directory: {BASE_DIR}")
    brain_raw = _load_text_file(BRAIN_FILE)
    if not brain_raw:
        print("AMOS.brain not found or empty.")
        return
    brain = _parse_brain(brain_raw)
    cfg = _load_config()
    print("Loaded brain sections:", ", ".join(sorted(brain.keys())))
    print("Loaded worker roles:", ", ".join(sorted(WORKER_REGISTRY.keys())))
    event = AmosEvent(
        timestamp=datetime.now(timezone.utc).isoformat(),
        event_type="startup",
        payload={
            "identity": brain.get("IDENTITY", {}),
            "goals": brain.get("GOALS", {}),
            "constraints": brain.get("CONSTRAINTS", {}),
        },
    )
    _log_event(event)

    print("\n[1/3] Planner generating plan from GOALS[1] ...")
    plan_resp = _run_planner(brain)
    print("Planner summary:", plan_resp.summary)

    print("\n[2/3] Analyst expanding NEXT_ACTION ...")
    analyst_resp = _run_analyst(brain)
    print("Analyst summary:", analyst_resp.summary)

    print("\n[3/3] Auditor checking plan ...")
    audit_resp = _run_auditor(plan_resp)
    print("Auditor summary:", audit_resp.summary)

    _ensure_dirs()
    growth_path = MEMORY_DIR / "growth.log"
    with growth_path.open("a", encoding="utf-8") as f:
        f.write(
            f"[{datetime.now(timezone.utc).isoformat()}] "
            f"NEXT_ACTION={_pick_next_action(brain)} | "
            f"plan_steps={len(plan_resp.details.get('plan', [])) if isinstance(plan_resp.details, dict) else 0}\n"
        )

    _log_event(
        AmosEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type="run_summary",
            payload={
                "planner": asdict(plan_resp),
                "analyst": asdict(analyst_resp),
                "auditor": asdict(audit_resp),
            },
        )
    )
    print("\nRun complete. Logs are in ./logs and ./memory.")


if __name__ == "__main__":
    main()
