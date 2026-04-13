"""AMOS Brain Cognitive State Manager - Persistent reasoning memory."""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class ReasoningStep:
    """Single step in a reasoning chain."""
    step_id: str
    timestamp: str
    description: str
    perspective: str
    law_compliance: dict[str, bool]
    kernel_activations: list[str]
    input_context: dict
    output_result: str
    confidence: str


@dataclass
class WorkflowSession:
    """Complete reasoning workflow session."""
    session_id: str
    created_at: str
    updated_at: str
    goal: str
    domain: str
    reasoning_chain: list[ReasoningStep] = field(default_factory=list)
    law_violations: list[dict] = field(default_factory=list)
    kernel_history: list[str] = field(default_factory=list)
    quadrant_coverage: dict[str, int] = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    
    def add_step(self, step: ReasoningStep):
        """Add a reasoning step to the chain."""
        self.reasoning_chain.append(step)
        self.updated_at = datetime.now().isoformat()

        # Update kernel history
        for kernel in step.kernel_activations:
            if kernel not in self.kernel_history:
                self.kernel_history.append(kernel)

        # Update quadrant coverage from step context when present
        quadrants = step.input_context.get("quadrants_checked") or step.input_context.get("quadrants") or []
        if isinstance(quadrants, dict):
            quadrants = list(quadrants.keys())
        for quadrant in quadrants:
            self.quadrant_coverage[quadrant] = self.quadrant_coverage.get(quadrant, 0) + 1


class CognitiveStateManager:
    """
    AMOS Brain Cognitive State Manager.
    
    Provides persistent reasoning memory across multi-step workflows:
    - Tracks reasoning evolution across task sequences
    - Maintains law compliance history
    - Maintains kernel activation context
    - Enables reasoning replay and audit trails
    - Supports recursive self-analysis
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".amos_brain" / "sessions"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self._active_sessions: dict[str, WorkflowSession] = {}
        self._current_session: Optional[WorkflowSession] = None
    
    def start_session(
        self,
        goal: str,
        domain: str = "general",
        metadata: Optional[dict] = None
    ) -> str:
        """
        Start a new reasoning workflow session.
        
        Args:
            goal: The objective of this reasoning workflow
            domain: Domain context (software, logic, ubi, etc.)
            metadata: Optional session metadata
            
        Returns:
            session_id: Unique identifier for the session
        """
        session_id = f"AMOS-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now().isoformat()
        
        session = WorkflowSession(
            session_id=session_id,
            created_at=now,
            updated_at=now,
            goal=goal,
            domain=domain,
            metadata=metadata or {}
        )
        
        self._active_sessions[session_id] = session
        self._current_session = session
        
        return session_id
    
    def record_reasoning_step(
        self,
        description: str,
        perspective: str,
        law_compliance: dict[str, bool],
        kernel_activations: list[str],
        input_context: dict,
        output_result: str,
        confidence: str,
        session_id: Optional[str] = None
    ) -> str:
        """
        Record a reasoning step in the current or specified session.
        
        Args:
            description: What reasoning was performed
            perspective: Which perspective (Rule of 2)
            law_compliance: Dict of law_id -> compliant
            kernel_activations: Which kernels were active
            input_context: Input data for this step
            output_result: Result of the reasoning
            confidence: High/medium/low
            session_id: Optional specific session (uses current if None)
            
        Returns:
            step_id: Unique identifier for this step
        """
        session = self._get_session(session_id)
        if not session:
            # Auto-start session if none exists
            session_id = self.start_session(
                goal="Auto-generated from reasoning step",
                domain="general"
            )
            session = self._active_sessions[session_id]
        
        step_id = f"{session.session_id}-S{len(session.reasoning_chain)+1:03d}"
        
        step = ReasoningStep(
            step_id=step_id,
            timestamp=datetime.now().isoformat(),
            description=description,
            perspective=perspective,
            law_compliance=law_compliance,
            kernel_activations=kernel_activations,
            input_context=input_context,
            output_result=output_result,
            confidence=confidence
        )
        
        session.add_step(step)
        
        return step_id
    
    def get_session_context(self, session_id: Optional[str] = None) -> dict:
        """
        Get the accumulated context from a session.
        
        Returns:
            Dict with reasoning summary, law compliance, kernel history
        """
        session = self._get_session(session_id)
        if not session:
            return {}
        
        # Calculate compliance statistics
        law_stats = {}
        for step in session.reasoning_chain:
            for law_id, compliant in step.law_compliance.items():
                if law_id not in law_stats:
                    law_stats[law_id] = {"total": 0, "compliant": 0}
                law_stats[law_id]["total"] += 1
                if compliant:
                    law_stats[law_id]["compliant"] += 1
        
        return {
            "session_id": session.session_id,
            "goal": session.goal,
            "domain": session.domain,
            "steps_count": len(session.reasoning_chain),
            "duration_minutes": self._calculate_duration(session),
            "law_compliance": {
                law_id: f"{stats['compliant']}/{stats['total']}"
                for law_id, stats in law_stats.items()
            },
            "kernels_activated": session.kernel_history,
            "quadrant_coverage": session.quadrant_coverage,
            "latest_confidence": (
                session.reasoning_chain[-1].confidence
                if session.reasoning_chain else "unknown"
            ),
        }
    
    def replay_reasoning(
        self,
        session_id: Optional[str] = None,
        format_type: str = "text"
    ) -> str:
        """
        Replay the reasoning chain for analysis or audit.
        
        Args:
            session_id: Session to replay (current if None)
            format_type: text, json, or markdown
            
        Returns:
            Formatted reasoning replay
        """
        session = self._get_session(session_id)
        if not session:
            return "No session found."
        
        if format_type == "json":
            return json.dumps(
                {
                    "session": asdict(session),
                    "summary": self.get_session_context(session_id)
                },
                indent=2,
                default=str
            )
        
        lines = [
            f"# AMOS Reasoning Replay: {session.session_id}",
            f"Goal: {session.goal}",
            f"Domain: {session.domain}",
            f"Started: {session.created_at}",
            f"Steps: {len(session.reasoning_chain)}",
            "",
            "## Reasoning Chain",
            ""
        ]
        
        for i, step in enumerate(session.reasoning_chain, 1):
            lines.extend([
                f"### Step {i}: {step.step_id}",
                f"**Time:** {step.timestamp}",
                f"**Description:** {step.description}",
                f"**Perspective:** {step.perspective}",
                f"**Confidence:** {step.confidence}",
                f"**Kernels:** {', '.join(step.kernel_activations)}",
                f"**Law Compliance:** {', '.join([f'{k}={v}' for k, v in step.law_compliance.items()])}",
                f"**Result:** {step.output_result[:100]}...",
                ""
            ])
        
        return "\n".join(lines)
    
    def analyze_compliance_trend(self, session_id: Optional[str] = None) -> dict:
        """
        Analyze law compliance trend across the reasoning chain.
        
        Returns:
            Compliance trend analysis
        """
        session = self._get_session(session_id)
        if not session:
            return {}
        
        trends = {}
        law_ids = ["L1", "L2", "L3", "L4", "L5", "L6"]
        
        for law_id in law_ids:
            compliance_over_time = []
            for step in session.reasoning_chain:
                compliant = step.law_compliance.get(law_id, True)
                compliance_over_time.append(1 if compliant else 0)
            
            if compliance_over_time:
                avg_compliance = sum(compliance_over_time) / len(compliance_over_time)
                if compliance_over_time[-1] > compliance_over_time[0]:
                    trend = "improving"
                elif compliance_over_time[-1] < compliance_over_time[0]:
                    trend = "declining"
                else:
                    trend = "stable"
                trends[law_id] = {
                    "average": f"{avg_compliance:.0%}",
                    "trend": trend,
                    "violations": len(compliance_over_time) - sum(compliance_over_time)
                }
        
        return trends
    
    def save_session(self, session_id: Optional[str] = None) -> Path:
        """
        Persist a session to storage.
        
        Returns:
            Path to saved file
        """
        session = self._get_session(session_id)
        if not session:
            raise ValueError("No session to save")
        
        filepath = self.storage_path / f"{session.session_id}.json"
        
        with open(filepath, 'w') as f:
            json.dump(asdict(session), f, indent=2, default=str)
        
        return filepath
    
    def load_session(self, session_id: str) -> Optional[WorkflowSession]:
        """Load a session from storage."""
        filepath = self.storage_path / f"{session_id}.json"
        
        if not filepath.exists():
            return None
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Reconstruct session
        session = WorkflowSession(**data)
        
        # Reconstruct reasoning steps
        session.reasoning_chain = [
            ReasoningStep(**step_data)
            for step_data in data.get("reasoning_chain", [])
        ]
        
        self._active_sessions[session_id] = session
        return session
    
    def list_sessions(self) -> list[dict]:
        """List all stored sessions."""
        sessions = []
        
        for filepath in self.storage_path.glob("*.json"):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                sessions.append({
                    "session_id": data["session_id"],
                    "goal": data["goal"][:50],
                    "domain": data["domain"],
                    "steps": len(data.get("reasoning_chain", [])),
                    "created": data["created_at"]
                })
            except Exception:
                pass
        
        return sorted(sessions, key=lambda x: x["created"], reverse=True)
    
    def close_session(self, session_id: Optional[str] = None) -> Path:
        """Close and save a session."""
        session = self._get_session(session_id)
        if not session:
            raise ValueError("No session to close")
        
        filepath = self.save_session(session.session_id)
        
        # Remove from active sessions
        if session.session_id in self._active_sessions:
            del self._active_sessions[session.session_id]
        
        if self._current_session and self._current_session.session_id == session.session_id:
            self._current_session = None
        
        return filepath
    
    def _get_session(self, session_id: Optional[str]) -> Optional[WorkflowSession]:
        """Get a session by ID or current session."""
        if session_id:
            session = self._active_sessions.get(session_id)
            if session is not None:
                return session
            return self.load_session(session_id)
        return self._current_session
    
    def _calculate_duration(self, session: WorkflowSession) -> float:
        """Calculate session duration in minutes."""
        try:
            created = datetime.fromisoformat(session.created_at)
            updated = datetime.fromisoformat(session.updated_at)
            return (updated - created).total_seconds() / 60
        except Exception:
            return 0.0


# Global state manager instance
_state_manager: Optional[CognitiveStateManager] = None


def get_state_manager() -> CognitiveStateManager:
    """Get or create global state manager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = CognitiveStateManager()
    return _state_manager
