from __future__ import annotations

from typing import Any

"""AMOS Reading Kernel Service - Production implementation.

Parses user requests into structured machine goals using:
- Speech act classification (ASK, REQUEST, COMMAND, CRITIQUE)
- Segment extraction (goals, constraints, risks, references)
- Stable read building with ambiguity detection
- Goal verification with response mode selection

This is the concrete implementation that replaces placeholder text parsing.
"""


import re
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum


class InputClass(str, Enum):
    SIMPLE_REQUEST = "simple_request"
    CORRECTION = "correction"
    MISSING_REFERENCE = "missing_reference"
    HIGH_AMBIGUITY = "high_ambiguity"
    HIGH_RISK = "high_risk"
    FORMAT_REQUEST = "format_request"
    DESIGN_TASK = "design_task"
    EXECUTION_TASK = "execution_task"
    UNSUPPORTED = "unsupported"


class SpeechAct(str, Enum):
    ASK = "ask"
    REQUEST = "request"
    COMMAND = "command"
    CORRECT = "correct"
    CRITIQUE = "critique"
    INFORM = "inform"
    UNKNOWN = "unknown"


class SegmentType(str, Enum):
    CLAIM = "claim"
    QUESTION = "question"
    CONSTRAINT = "constraint"
    GOAL = "goal"
    INSTRUCTION = "instruction"
    RISK = "risk"
    FILLER = "filler"


class ResponseMode(str, Enum):
    ANSWER = "answer"
    CLARIFY = "clarify"
    BLOCK = "block"
    DEFER = "defer"


@dataclass
class Segment:
    text: str
    kind: SegmentType
    start: int
    end: int


@dataclass
class ParsedInput:
    raw_text: str
    normalized_text: str
    speech_act: SpeechAct
    segments: list[Segment]
    references: list[str]
    constraints: list[str]
    goals: list[str]
    risks: list[str]


@dataclass
class StableRead:
    input_class: InputClass
    primary_goal: str | None
    constraints: list[str]
    ambiguities: list[str]
    references: list[str]
    confidence: float
    clarification_questions: list[str] = field(default_factory=list)


@dataclass
class VerifiedGoal:
    mode: ResponseMode
    objective: str
    constraints: list[str]
    executable: bool
    confidence: float
    reason: str


@dataclass
class ReadingResult:
    """Complete result from reading kernel processing."""

    request_id: str
    parsed: ParsedInput
    stable_read: StableRead
    verified_goal: VerifiedGoal
    suggested_action: str | None
    execution_plan: dict[str, Any]
    latency_ms: float


class ReadingKernel:
    """Concrete, minimal reading pipeline for production use.

    This is not superintelligence. It is a real executable core that:
    - normalizes text
    - segments it
    - classifies the speech act
    - extracts goals, constraints, references, and risk markers
    """

    CONSTRAINT_PATTERNS = [
        re.compile(r"\bmust\b", re.I),
        re.compile(r"\bdo not\b", re.I),
        re.compile(r"\bno\b", re.I),
        re.compile(r"\bwithout\b", re.I),
        re.compile(r"\bneed(s)? to\b", re.I),
        re.compile(r"\bshould\b", re.I),
        re.compile(r"\brequired\b", re.I),
    ]

    RISK_PATTERNS = [
        re.compile(r"\bunsafe\b", re.I),
        re.compile(r"\bbroken\b", re.I),
        re.compile(r"\bwrong\b", re.I),
        re.compile(r"\bdumb\b", re.I),
        re.compile(r"\bnot enough\b", re.I),
        re.compile(r"\bcannot\b", re.I),
        re.compile(r"\bfailed\b", re.I),
        re.compile(r"\berror\b", re.I),
    ]

    GOAL_PATTERNS = [
        re.compile(r"\bbuild\b", re.I),
        re.compile(r"\bimplement\b", re.I),
        re.compile(r"\bwrite\b", re.I),
        re.compile(r"\bcreate\b", re.I),
        re.compile(r"\bfix\b", re.I),
        re.compile(r"\badd\b", re.I),
        re.compile(r"\bupdate\b", re.I),
        re.compile(r"\brefactor\b", re.I),
        re.compile(r"\bdeploy\b", re.I),
        re.compile(r"\btest\b", re.I),
    ]

    EXECUTION_KEYWORDS = [
        "run",
        "execute",
        "start",
        "stop",
        "restart",
        "deploy",
        "build",
        "compile",
        "test",
        "lint",
        "format",
        "sync",
    ]

    def normalize(self, text: str) -> str:
        """Normalize input text."""
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def classify_speech_act(self, text: str) -> SpeechAct:
        """Classify the speech act of the input."""
        lower = text.lower()

        if text.endswith("?"):
            return SpeechAct.ASK

        if any(word in lower for word in ["fix", "correct", "change", "update"]):
            if any(word in lower for word in ["wrong", "not", "bad", "broken", "still"]):
                return SpeechAct.CRITIQUE
            return SpeechAct.REQUEST

        if any(word in lower for word in ["build", "write", "implement", "create", "add"]):
            return SpeechAct.REQUEST

        if any(word in lower for word in ["run", "execute", "start", "stop", "deploy"]):
            return SpeechAct.COMMAND

        return SpeechAct.INFORM

    def segment(self, text: str) -> list[Segment]:
        """Segment text into typed parts."""
        parts = re.split(r"(?<=[.!?])\s+", text)
        segments: list[Segment] = []
        cursor = 0

        for part in parts:
            stripped = part.strip()
            if not stripped:
                continue

            start = text.find(stripped, cursor)
            end = start + len(stripped)
            cursor = end

            kind = SegmentType.CLAIM
            if stripped.endswith("?"):
                kind = SegmentType.QUESTION
            elif any(p.search(stripped) for p in self.CONSTRAINT_PATTERNS):
                kind = SegmentType.CONSTRAINT
            elif any(p.search(stripped) for p in self.GOAL_PATTERNS):
                kind = SegmentType.GOAL
            elif any(p.search(stripped) for p in self.RISK_PATTERNS):
                kind = SegmentType.RISK
            elif stripped.lower().startswith(("please", "make sure", "ensure")):
                kind = SegmentType.INSTRUCTION

            segments.append(Segment(text=stripped, kind=kind, start=start, end=end))

        return segments

    def extract_constraints(self, segments: list[Segment]) -> list[str]:
        """Extract constraint segments."""
        return [s.text for s in segments if s.kind == SegmentType.CONSTRAINT]

    def extract_goals(self, segments: list[Segment]) -> list[str]:
        """Extract goal segments."""
        return [s.text for s in segments if s.kind == SegmentType.GOAL]

    def extract_risks(self, segments: list[Segment]) -> list[str]:
        """Extract risk segments."""
        return [s.text for s in segments if s.kind == SegmentType.RISK]

    def extract_references(self, text: str) -> list[str]:
        """Extract reference tokens."""
        refs = []
        for token in ["it", "this", "that", "they", "them", "here", "there"]:
            if re.search(rf"\b{token}\b", text, re.I):
                refs.append(token)
        return refs

    def parse(self, text: str) -> ParsedInput:
        """Parse raw text into structured input."""
        normalized = self.normalize(text)
        segments = self.segment(normalized)

        return ParsedInput(
            raw_text=text,
            normalized_text=normalized,
            speech_act=self.classify_speech_act(normalized),
            segments=segments,
            references=self.extract_references(normalized),
            constraints=self.extract_constraints(segments),
            goals=self.extract_goals(segments),
            risks=self.extract_risks(segments),
        )

    def build_stable_read(self, parsed: ParsedInput, context: dict[str, Any] = None) -> StableRead:
        """Build stable interpretation from parsed input."""
        ambiguities: list[str] = []
        clarification_questions: list[str] = []

        ctx = context or {}
        last_goal = ctx.get("last_goal")

        # Check for unresolved references
        if parsed.references and not last_goal:
            ambiguities.append("unresolved_reference")
            clarification_questions.append(
                "What does '" + parsed.references[0] + "' refer to here?"
            )

        # Check for missing constraints in design tasks
        if parsed.goals and not parsed.constraints:
            if any(
                word in parsed.normalized_text.lower() for word in ["build", "create", "implement"]
            ):
                ambiguities.append("missing_constraints")
                clarification_questions.append("What constraints should this satisfy?")

        # Classify input type
        input_class = InputClass.SIMPLE_REQUEST
        if parsed.risks:
            input_class = InputClass.HIGH_RISK
        elif parsed.references and ambiguities:
            input_class = InputClass.MISSING_REFERENCE
        elif parsed.speech_act == SpeechAct.CRITIQUE:
            input_class = InputClass.CORRECTION
        elif parsed.goals:
            if any(word in parsed.normalized_text.lower() for word in self.EXECUTION_KEYWORDS):
                input_class = InputClass.EXECUTION_TASK
            else:
                input_class = InputClass.DESIGN_TASK

        # Determine primary goal
        primary_goal = None
        if parsed.goals:
            primary_goal = parsed.goals[0]
        elif last_goal:
            primary_goal = last_goal

        # Calculate confidence
        confidence = 0.9
        if ambiguities:
            confidence = 0.45
        elif not primary_goal:
            confidence = 0.3
        elif parsed.speech_act == SpeechAct.ASK:
            confidence = 0.7

        return StableRead(
            input_class=input_class,
            primary_goal=primary_goal,
            constraints=parsed.constraints,
            ambiguities=ambiguities,
            references=parsed.references,
            confidence=confidence,
            clarification_questions=clarification_questions,
        )


class VerificationKernel:
    """Verifies stable reads and determines response mode."""

    def verify(self, read: StableRead) -> VerifiedGoal:
        """Verify a stable read and produce verified goal."""
        if read.ambiguities:
            return VerifiedGoal(
                mode=ResponseMode.CLARIFY,
                objective="resolve ambiguities before implementation",
                constraints=read.constraints,
                executable=False,
                confidence=read.confidence,
                reason="missing required references or constraints",
            )

        if not read.primary_goal:
            return VerifiedGoal(
                mode=ResponseMode.CLARIFY,
                objective="identify the concrete feature or code target",
                constraints=read.constraints,
                executable=False,
                confidence=0.4,
                reason="no concrete target goal extracted",
            )

        if read.input_class == InputClass.HIGH_RISK:
            return VerifiedGoal(
                mode=ResponseMode.BLOCK,
                objective=read.primary_goal,
                constraints=read.constraints,
                executable=False,
                confidence=read.confidence,
                reason="high risk markers detected - requires human review",
            )

        return VerifiedGoal(
            mode=ResponseMode.ANSWER,
            objective=read.primary_goal,
            constraints=read.constraints,
            executable=read.input_class in (InputClass.EXECUTION_TASK, InputClass.DESIGN_TASK),
            confidence=read.confidence,
            reason="stable read verified",
        )


class ExecutionPlanner:
    """Plans execution for verified goals."""

    def plan(self, goal: VerifiedGoal, parsed: ParsedInput) -> dict[str, Any]:
        """Create execution plan for verified goal."""
        if goal.mode != ResponseMode.ANSWER or not goal.executable:
            return None

        text = parsed.normalized_text.lower()

        # Determine action type
        action_type = "unknown"
        if any(word in text for word in ["fix", "correct", "repair"]):
            action_type = "repair"
        elif any(word in text for word in ["build", "create", "implement"]):
            action_type = "build"
        elif any(word in text for word in ["add", "insert", "append"]):
            action_type = "add"
        elif any(word in text for word in ["update", "change", "modify"]):
            action_type = "update"
        elif any(word in text for word in ["test", "validate", "verify"]):
            action_type = "test"
        elif any(word in text for word in ["deploy", "release", "publish"]):
            action_type = "deploy"
        elif any(word in text for word in ["run", "execute", "start"]):
            action_type = "execute"
        elif any(word in text for word in ["delete", "remove", "clean"]):
            action_type = "delete"

        # Determine domain
        domain = "general"
        if any(word in text for word in ["api", "endpoint", "route", "server"]):
            domain = "api"
        elif any(word in text for word in ["database", "db", "sql", "query", "table"]):
            domain = "database"
        elif any(word in text for word in ["ui", "frontend", "component", "page", "html", "css"]):
            domain = "frontend"
        elif any(word in text for word in ["test", "spec", "assertion"]):
            domain = "testing"
        elif any(word in text for word in ["config", "setting", "env", "variable"]):
            domain = "configuration"
        elif any(word in text for word in ["docker", "kubernetes", "k8s", "deploy", "infra"]):
            domain = "infrastructure"

        return {
            "action_type": action_type,
            "domain": domain,
            "priority": "high" if action_type == "repair" else "normal",
            "estimated_steps": self._estimate_steps(action_type, domain),
            "requires_review": goal.confidence < 0.7,
        }

    def _estimate_steps(self, action_type: str, domain: str) -> int:
        """Estimate number of execution steps."""
        base_steps = {
            "repair": 3,
            "build": 5,
            "add": 2,
            "update": 2,
            "test": 2,
            "deploy": 4,
            "execute": 1,
            "delete": 1,
        }
        return base_steps.get(action_type, 3)


class AMOSReadingService:
    """Production reading service for AMOS backend."""

    _instance: AMOSReadingService | None = None

    def __new__(cls) -> AMOSReadingService:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.reader = ReadingKernel()
        self.verifier = VerificationKernel()
        self.planner = ExecutionPlanner()
        self._history: list[ReadingResult] = []
        self._initialized = True

    def process(self, text: str, context: dict[str, Any] = None) -> ReadingResult:
        """Process user request through complete reading pipeline."""
        started = time.time()
        request_id = f"read_{uuid.uuid4().hex[:12]}"

        # Parse input
        parsed = self.reader.parse(text)

        # Build stable read
        stable_read = self.reader.build_stable_read(parsed, context)

        # Verify goal
        verified = self.verifier.verify(stable_read)

        # Plan execution if applicable
        plan = self.planner.plan(verified, parsed)

        # Determine suggested action
        suggested_action = None
        if verified.mode == ResponseMode.ANSWER and verified.executable and plan:
            suggested_action = f"{plan['action_type']}_{plan['domain']}"

        latency_ms = (time.time() - started) * 1000

        result = ReadingResult(
            request_id=request_id,
            parsed=parsed,
            stable_read=stable_read,
            verified_goal=verified,
            suggested_action=suggested_action,
            execution_plan=plan,
            latency_ms=round(latency_ms, 2),
        )

        self._history.append(result)
        return result

    def get_history(self, limit: int = 100) -> list[ReadingResult]:
        """Get processing history."""
        return self._history[-limit:]

    def clear_history(self) -> None:
        """Clear processing history."""
        self._history.clear()


# Global service instance
_reading_service: AMOSReadingService | None = None


def get_reading_service() -> AMOSReadingService:
    """Get or create global reading service."""
    global _reading_service
    if _reading_service is None:
        _reading_service = AMOSReadingService()
    return _reading_service


def process_request(text: str, context: dict[str, Any] = None) -> ReadingResult:
    """Process a request through the reading kernel."""
    service = get_reading_service()
    return service.process(text, context)
