#!/usr/bin/env python3
"""AMOS Session Logger
====================
Tracks AMOS Brain usage and analytics for measuring value.

Usage:
    python amos_session_logger.py [command]

Commands:
    start       Start a new logged session
    log         Log an AMOS interaction
    stats       Show session statistics
    report      Generate usage report
    export      Export session data to JSON
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class AMOSInteraction:
    """Record of a single AMOS interaction."""

    timestamp: str
    interaction_type: str  # 'skill', 'tool', 'reasoning', 'command'
    name: str
    input_hash: str
    output_summary: str
    engines_used: list[str] = field(default_factory=list)
    laws_applied: list[str] = field(default_factory=list)
    duration_ms: int = 0
    success: bool = True


@dataclass
class AMOSSession:
    """Complete AMOS usage session."""

    session_id: str
    start_time: str
    end_time: str | None = None
    interactions: list[AMOSInteraction] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_interaction(self, interaction: AMOSInteraction):
        """Add an interaction to the session."""
        self.interactions.append(interaction)

    def get_stats(self) -> dict[str, Any]:
        """Calculate session statistics."""
        if not self.interactions:
            return {"total_interactions": 0}

        types: dict[str, int] = {}
        engines = set()
        laws = set()
        total_duration = 0
        success_count = 0

        for i in self.interactions:
            # Handle both dataclass and dict (when loaded from JSON)
            if isinstance(i, dict):
                itype = i.get("interaction_type", "unknown")
                iengines = i.get("engines_used", [])
                ilaws = i.get("laws_applied", [])
                iduration = i.get("duration_ms", 0)
                isuccess = i.get("success", True)
            else:
                itype = i.interaction_type
                iengines = i.engines_used
                ilaws = i.laws_applied
                iduration = i.duration_ms
                isuccess = i.success

            types[itype] = types.get(itype, 0) + 1
            engines.update(iengines)
            laws.update(ilaws)
            total_duration += iduration
            if isuccess:
                success_count += 1

        return {
            "session_id": self.session_id,
            "duration_minutes": self._get_duration_minutes(),
            "total_interactions": len(self.interactions),
            "interactions_by_type": types,
            "unique_engines_used": len(engines),
            "unique_laws_applied": len(laws),
            "avg_response_time_ms": total_duration / len(self.interactions),
            "success_rate": success_count / len(self.interactions),
        }

    def _get_duration_minutes(self) -> float:
        """Calculate session duration in minutes."""
        start = datetime.fromisoformat(self.start_time)
        end = datetime.now() if self.end_time is None else datetime.fromisoformat(self.end_time)
        return (end - start).total_seconds() / 60


class AMOSSessionLogger:
    """Logger for AMOS Brain sessions."""

    LOG_DIR = Path(__file__).parent / "amos_logs"

    def __init__(self):
        self.current_session: AMOSSession | None = None
        self.LOG_DIR.mkdir(exist_ok=True)

    def start_session(self, metadata: dict[str, Any] | None = None) -> str:
        """Start a new logging session."""
        session_id = self._generate_session_id()
        self.current_session = AMOSSession(
            session_id=session_id, start_time=datetime.now().isoformat(), metadata=metadata or {}
        )
        # Save immediately so other processes can load it
        self._save_session()
        return session_id

    def end_session(self) -> dict[str, Any]:
        """End current session and return stats."""
        if not self.current_session:
            return {"error": "No active session"}

        self.current_session.end_time = datetime.now().isoformat()
        stats = self.current_session.get_stats()

        # Save to file
        self._save_session()

        self.current_session = None
        return stats

    def log_interaction(
        self,
        interaction_type: str,
        name: str,
        input_data: str,
        output_data: str,
        engines_used: list[str] | None = None,
        laws_applied: list[str] | None = None,
        duration_ms: int = 0,
        success: bool = True,
    ) -> bool:
        """Log a single AMOS interaction."""
        if not self.current_session:
            return False

        interaction = AMOSInteraction(
            timestamp=datetime.now().isoformat(),
            interaction_type=interaction_type,
            name=name,
            input_hash=self._hash_input(input_data),
            output_summary=output_data[:200] + "..." if len(output_data) > 200 else output_data,
            engines_used=engines_used or [],
            laws_applied=laws_applied or [],
            duration_ms=duration_ms,
            success=success,
        )

        self.current_session.add_interaction(interaction)
        # Save session after each interaction
        self._save_session()
        return True

    def get_current_stats(self) -> dict[str, Any]:
        """Get stats for current session."""
        if not self.current_session:
            return {"error": "No active session"}
        return self.current_session.get_stats()

    def generate_report(self, session_id: str | None = None) -> str:
        """Generate a text report."""
        if session_id and self.current_session and self.current_session.session_id == session_id:
            session = self.current_session
        elif session_id:
            session = self._load_session(session_id)
        else:
            session = self.current_session

        if not session:
            return "No session data available"

        stats = session.get_stats()
        report = f"""
AMOS SESSION REPORT
{"=" * 50}
Session ID: {stats["session_id"]}
Duration: {stats["duration_minutes"]:.1f} minutes
Total Interactions: {stats["total_interactions"]}

Breakdown by Type:
"""
        for t, count in stats["interactions_by_type"].items():
            report += f"  - {t}: {count}\n"

        report += f"""
Cognitive Coverage:
  - Engines Used: {stats["unique_engines_used"]}
  - Laws Applied: {stats["unique_laws_applied"]}

Performance:
  - Avg Response Time: {stats["avg_response_time_ms"]:.0f}ms
  - Success Rate: {stats["success_rate"] * 100:.1f}%
"""
        return report

    def export_session(self, session_id: str | None = None, filepath: str | None = None) -> str:
        """Export session to JSON file."""
        if session_id and self.current_session and self.current_session.session_id == session_id:
            session = self.current_session
        elif session_id:
            session = self._load_session(session_id)
        else:
            session = self.current_session

        if not session:
            return "No session to export"

        filepath = filepath or str(self.LOG_DIR / f"{session.session_id}.json")

        data = {"session": asdict(session), "stats": session.get_stats()}

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)

        return filepath

    def list_sessions(self) -> list[dict[str, Any]]:
        """List all saved sessions."""
        sessions = []
        for f in self.LOG_DIR.glob("*.json"):
            try:
                with open(f) as file:
                    data = json.load(file)
                    sessions.append(
                        {
                            "session_id": data["session"]["session_id"],
                            "start_time": data["session"]["start_time"],
                            "interactions": len(data["session"]["interactions"]),
                            "file": str(f),
                        }
                    )
            except Exception:
                continue
        return sorted(sessions, key=lambda x: x["start_time"], reverse=True)

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rand = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:6]
        return f"amos_{timestamp}_{rand}"

    def _hash_input(self, data: str) -> str:
        """Hash input data for privacy."""
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _save_session(self):
        """Save current session to file."""
        if not self.current_session:
            return
        filepath = self.LOG_DIR / f"{self.current_session.session_id}.json"
        self.export_session(filepath=str(filepath))

    def _load_session(self, session_id: str) -> AMOSSession | None:
        """Load a session from file."""
        filepath = self.LOG_DIR / f"{session_id}.json"
        if not filepath.exists():
            return None

        try:
            with open(filepath) as f:
                data = json.load(f)
            session_data = data["session"]
            return AMOSSession(**session_data)
        except Exception:
            return None


def main():
    parser = argparse.ArgumentParser(description="AMOS Session Logger")
    parser.add_argument(
        "command", choices=["start", "end", "log", "stats", "report", "list", "export"]
    )
    parser.add_argument("--session-id", help="Session ID for operations")
    parser.add_argument("--type", default="command", help="Interaction type")
    parser.add_argument("--name", default="unknown", help="Interaction name")
    parser.add_argument("--input", default="", help="Input data")
    parser.add_argument("--output", default="", help="Output data")
    parser.add_argument("--file", help="Export file path")
    args = parser.parse_args()

    logger = AMOSSessionLogger()

    if args.command == "start":
        sid = logger.start_session()
        print(f"Started session: {sid}")
        # Save session ID to temp file for reference
        with open("/tmp/amos_current_session", "w") as f:
            f.write(sid)

    elif args.command == "end":
        # Try to load current session
        try:
            with open("/tmp/amos_current_session") as f:
                sid = f.read().strip()
            logger.current_session = logger._load_session(sid)
        except Exception:
            pass
        stats = logger.end_session()
        print(json.dumps(stats, indent=2))

    elif args.command == "log":
        # Try to get session ID from temp file
        try:
            with open("/tmp/amos_current_session") as f:
                sid = f.read().strip()
            logger.current_session = logger._load_session(sid)
        except Exception:
            pass

        success = logger.log_interaction(args.type, args.name, args.input, args.output)
        print("Logged" if success else "No active session")

    elif args.command == "stats":
        # Try to load current session
        try:
            with open("/tmp/amos_current_session") as f:
                sid = f.read().strip()
            logger.current_session = logger._load_session(sid)
        except Exception:
            pass
        stats = logger.get_current_stats()
        print(json.dumps(stats, indent=2))

    elif args.command == "report":
        # Try to load current session if no ID provided
        if not args.session_id:
            try:
                with open("/tmp/amos_current_session") as f:
                    sid = f.read().strip()
                logger.current_session = logger._load_session(sid)
            except Exception:
                pass
        report = logger.generate_report(args.session_id)
        print(report)

    elif args.command == "list":
        sessions = logger.list_sessions()
        for s in sessions:
            print(f"{s['session_id']}: {s['start_time']} ({s['interactions']} interactions)")

    elif args.command == "export":
        path = logger.export_session(args.session_id, args.file)
        print(f"Exported to: {path}")


if __name__ == "__main__":
    sys.exit(main())
