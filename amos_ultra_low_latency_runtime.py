from __future__ import annotations

from typing import Any, Optional

"""
AMOS Ultra-Low-Latency Runtime
Fast-path-first, bounded-depth, event-driven cognition system.

Core principle: screen fast → commit narrow → deepen only if needed
"""

import asyncio
import hashlib
import json
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime

UTC = UTC
from enum import Enum, auto

# Configure logging for latency tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos_latency")

# ============================================================================
# SECTION 1: Core Enums and Types
# ============================================================================


class RuntimeMode(Enum):
    """Runtime operation modes with strict latency budgets."""

    INTERRUPT = auto()  # Read only enough to classify
    FAST_COMMIT = auto()  # Produce safe narrow output immediately
    INCREMENTAL_UPDATE = auto()  # Update only changed parts of state
    DEEP_REPAIR = auto()  # Only if confidence fails or user corrects
    BACKGROUND_LEARNING = auto()  # Never block foreground
    BLOCKED = auto()  # Unsafe or impossible


class InterruptClass(Enum):
    """Fast interrupt classification - decided in one cheap pass (<15ms)."""

    SIMPLE_REQUEST = auto()  # Known pattern, safe for fast commit
    CORRECTION = auto()  # User correcting previous output
    MISSING_REFERENCE = auto()  # Needs narrow clarification
    HIGH_AMBIGUITY = auto()  # Underspecified, needs clarification
    HIGH_RISK = auto()  # Requires deep repair path
    FORMAT_REQUEST = auto()  # Known format template
    EMOTIONALLY_LOADED = auto()  # May need special handling
    DESIGN_TASK = auto()  # Fast commit or deep depending on complexity
    EXECUTION_TASK = auto()  # Verify then commit
    UNSUPPORTED = auto()  # Block


class CommitMode(Enum):
    """Two-stage commit: provisional first, refine only if needed."""

    PROVISIONAL = auto()  # Fast safe output
    FINAL = auto()  # Confirmed after validation


class LatencyInvariant(Enum):
    """Hard latency invariants - violations trigger alerts."""

    LI01_DEFAULT_FAST_PATH = "default path must be fast_path, not deep_path"
    LI02_DELTA_UPDATES = "state updates must be delta-based, not full rebuild"
    LI03_FOREGROUND_ISOLATION = "foreground response must not wait on background"
    LI04_NARROW_CLARIFY = "underspecified input triggers narrow clarification, not full solve"
    LI05_BOUNDED_REPAIR = "repair must be localized and capped at 1 round"
    LI06_TEMPLATE_FIRST = "pattern matches use templates before full generation"


# ============================================================================
# SECTION 2: Dataclasses for State Management
# ============================================================================


@dataclass(frozen=True)
class LatencyBudget:
    """Strict latency budgets in milliseconds."""

    interrupt_classify: int = 15
    route_by_table: int = 5
    minimal_context_load: int = 20
    pattern_match_or_slot_fill: int = 40
    constraint_check: int = 20
    provisional_commit: int = 20

    @property
    def total_fast_path_target_ms(self) -> int:
        return (
            self.interrupt_classify
            + self.route_by_table
            + self.minimal_context_load
            + self.pattern_match_or_slot_fill
            + self.constraint_check
            + self.provisional_commit
        )


@dataclass(frozen=True)
class ActiveContextPolicy:
    """Hard limits on active context to control latency."""

    max_active_turns: int = 6
    max_active_constraints: int = 12
    max_active_bindings: int = 12
    max_active_goals: int = 5
    overflow_strategy: str = "compress_low_salience_keep_constraints"


@dataclass
class ClassificationResult:
    """Output of interrupt classification (<15ms)."""

    class_: InterruptClass
    confidence: float  # 0.0 - 1.0
    risk_score: float  # 0.0 - 1.0
    known_pattern: bool
    suggested_route: RuntimeMode
    processing_time_ms: float


@dataclass
class StateDelta:
    """Delta update - only what changed, never full rebuild."""

    active_goal_changes: list[dict[str, Any]] = field(default_factory=list)
    constraint_changes: list[dict[str, Any]] = field(default_factory=list)
    binding_changes: list[dict[str, Any]] = field(default_factory=list)
    human_state_changes: list[dict[str, Any]] = field(default_factory=list)
    open_loops_changes: list[dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class FastPathResult:
    """Result of fast-path processing."""

    output: str
    commit_mode: CommitMode
    latency_ms: float
    template_used: Optional[str]
    slots_filled: dict[str, Any]
    confidence: float
    needs_deep_repair: bool
    cache_hits: int


@dataclass
class LatencyMetrics:
    """Real-time latency tracking."""

    total_requests: int = 0
    fast_path_hits: int = 0
    deep_path_triggers: int = 0
    avg_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    cache_hit_rate: float = 0.0
    invariant_violations: list[str] = field(default_factory=list)


# ============================================================================
# SECTION 3: Cache Systems for Speed
# ============================================================================


class PatternCache:
    """Maps input signatures to templates."""

    def __init__(self, maxsize: int = 10000):
        self._cache: dict[str, tuple[str, float]] = {}
        self._maxsize = maxsize
        self._hits = 0
        self._misses = 0

    def _make_key(self, raw_text: str, recent_context: str) -> str:
        """Create hash key from input + context."""
        content = f"{raw_text}:{recent_context}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    def get(self, raw_text: str, recent_context: str) -> tuple[str, float]:
        """Get cached template and confidence."""
        key = self._make_key(raw_text, recent_context)
        if key in self._cache:
            self._hits += 1
            return self._cache[key]
        self._misses += 1
        return None

    def set(self, raw_text: str, recent_context: str, template: str, confidence: float) -> None:
        """Cache template result."""
        if len(self._cache) >= self._maxsize:
            # Evict oldest (simple FIFO for speed)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        key = self._make_key(raw_text, recent_context)
        self._cache[key] = (template, confidence)

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0


class BindingCache:
    """Maps recurring references to canonical entities."""

    def __init__(self):
        self._bindings: dict[str, Any] = {}
        self._access_times: dict[str, float] = {}

    def get(self, reference: str) -> Optional[Any]:
        self._access_times[reference] = time.time()
        return self._bindings.get(reference)

    def set(self, reference: str, entity: Any) -> None:
        self._bindings[reference] = entity
        self._access_times[reference] = time.time()

    def evict_stale(self, max_age_seconds: float = 3600) -> None:
        """Remove old bindings to keep cache small."""
        now = time.time()
        stale = [k for k, t in self._access_times.items() if now - t > max_age_seconds]
        for k in stale:
            del self._bindings[k]
            del self._access_times[k]


class ConstraintCache:
    """Stores active stable constraints for fast lookup."""

    def __init__(self, max_constraints: int = 12):
        self._constraints: deque[dict[str, Any]] = deque(maxlen=max_constraints)
        self._constraint_set: set[str] = set()

    def add(self, constraint: dict[str, Any]) -> None:
        """Add constraint if not already present."""
        key = json.dumps(constraint, sort_keys=True)
        if key not in self._constraint_set:
            maxlen = self._constraints.maxlen
            if maxlen is not None and len(self._constraints) >= maxlen:
                oldest = self._constraints.popleft()
                self._constraint_set.discard(json.dumps(oldest, sort_keys=True))
            self._constraints.append(constraint)
            self._constraint_set.add(key)

    def get_active(self) -> list[dict[str, Any]]:
        return list(self._constraints)

    def check(self, constraint: dict[str, Any]) -> bool:
        """Fast check if constraint is already active."""
        key = json.dumps(constraint, sort_keys=True)
        return key in self._constraint_set


# ============================================================================
# SECTION 4: Precompiled Control Tables
# ============================================================================

CLASS_TO_PATH_TABLE: dict[InterruptClass, RuntimeMode] = {
    InterruptClass.SIMPLE_REQUEST: RuntimeMode.FAST_COMMIT,
    InterruptClass.CORRECTION: RuntimeMode.INCREMENTAL_UPDATE,
    InterruptClass.MISSING_REFERENCE: RuntimeMode.INTERRUPT,  # Will trigger clarification
    InterruptClass.HIGH_AMBIGUITY: RuntimeMode.INTERRUPT,  # Will trigger clarification
    InterruptClass.HIGH_RISK: RuntimeMode.DEEP_REPAIR,
    InterruptClass.FORMAT_REQUEST: RuntimeMode.FAST_COMMIT,
    InterruptClass.EMOTIONALLY_LOADED: RuntimeMode.FAST_COMMIT,
    InterruptClass.DESIGN_TASK: RuntimeMode.FAST_COMMIT,
    InterruptClass.EXECUTION_TASK: RuntimeMode.FAST_COMMIT,
    InterruptClass.UNSUPPORTED: RuntimeMode.BLOCKED,
}

RISK_THRESHOLD_DEEP_REPAIR: float = 0.7
AMBIGUITY_THRESHOLD_CLARIFY: float = 0.25
TEMPLATE_MATCH_THRESHOLD: float = 0.85

# ============================================================================
# SECTION 5: Template Engine
# ============================================================================


@dataclass
class Template:
    """Precompiled template with slots."""

    name: str
    pattern: str  # Simple pattern for matching
    slots: list[str]
    template_text: str
    constraint_checks: list[str] = field(default_factory=list)


class TemplateEngine:
    """Fast template matching and filling."""

    TEMPLATES: list[Template] = [
        Template(
            name="answer_direct",
            pattern="answer|tell|explain|what is|how to",
            slots=["topic", "format"],
            template_text="{topic}: [direct answer in {format}]",
            constraint_checks=["safe_topic"],
        ),
        Template(
            name="ask_targeted_clarification",
            pattern="clarify|need more|missing|what do you mean",
            slots=["missing_info", "context"],
            template_text="I need clarification on: {missing_info}. Context: {context}",
        ),
        Template(
            name="correct_assumption",
            pattern="wrong|incorrect|not right|fix",
            slots=["correction_target", "correct_value"],
            template_text="Correction noted: {correction_target} → {correct_value}",
        ),
        Template(
            name="convert_to_schema",
            pattern="schema|format|structure|json|yaml",
            slots=["content", "target_format"],
            template_text="{content} formatted as {target_format}",
        ),
        Template(
            name="summarize_constraints",
            pattern="summary|summarize|constraints|limits",
            slots=["constraints_list"],
            template_text="Current constraints: {constraints_list}",
        ),
        Template(
            name="emit_machine_readable_spec",
            pattern="spec|specification|machine readable|formal",
            slots=["spec_content"],
            template_text="```json\n{spec_content}\n```",
        ),
        Template(
            name="block_unsafe_request",
            pattern="unsafe|harmful|attack|exploit",
            slots=["block_reason"],
            template_text="Request blocked: {block_reason}",
        ),
    ]

    def __init__(self):
        self._pattern_scores: dict[str, float] = {}

    def match(
        self, raw_text: str, interrupt_class: InterruptClass
    ) -> tuple[Optional[Template], dict[str, Any], float]:
        """
        Fast pattern match. Returns (template, slots, match_score).
        Target: <40ms total.
        """
        text_lower = raw_text.lower()

        # Simple keyword matching for speed
        for template in self.TEMPLATES:
            pattern_parts = template.pattern.split("|")
            score = sum(1 for part in pattern_parts if part in text_lower) / len(pattern_parts)

            if score >= TEMPLATE_MATCH_THRESHOLD:
                # Extract slots (simplified - production would use NER)
                slots = self._extract_slots(raw_text, template.slots)
                return template, slots, score

        return None, {}, 0.0

    def _extract_slots(self, raw_text: str, slot_names: list[str]) -> dict[str, Any]:
        """Extract slot values from text. Production would use entity recognition."""
        slots = {}
        # Simplified: use whole text as first slot for now
        if slot_names:
            slots[slot_names[0]] = raw_text[:200]  # Truncate for safety
        return slots

    def fill(self, template: Template, slots: dict[str, Any]) -> str:
        """Fill template slots."""
        result = template.template_text
        for slot, value in slots.items():
            result = result.replace(f"{{{slot}}}", str(value))
        return result


# ============================================================================
# SECTION 6: Interrupt Classifier
# ============================================================================


class InterruptClassifier:
    """
    Decides in one cheap pass (<15ms) what class of thing this is.

    Rule: If class = simple_request ∧ known_pattern = 1 ⇒ FastCommit
    """

    # Fast keyword-based classification
    CLASS_PATTERNS: dict[InterruptClass, list[str]] = {
        InterruptClass.SIMPLE_REQUEST: [
            "what is",
            "how to",
            "explain",
            "tell me",
            "describe",
            "define",
            "list",
            "show",
            "get",
            "find",
        ],
        InterruptClass.CORRECTION: [
            "wrong",
            "incorrect",
            "not right",
            "fix",
            "change",
            "should be",
            "actually",
            "correction",
        ],
        InterruptClass.MISSING_REFERENCE: [
            "what is that",
            "which one",
            "referring to",
            "this one",
            "that thing",
            "the above",
        ],
        InterruptClass.HIGH_AMBIGUITY: [
            "maybe",
            "or",
            "either",
            "could be",
            "might be",
            "unclear",
            "ambiguous",
        ],
        InterruptClass.HIGH_RISK: [
            "delete",
            "remove all",
            "shutdown",
            "exec",
            "eval",
            "system",
            "password",
            "secret",
            "key",
        ],
        InterruptClass.FORMAT_REQUEST: [
            "json",
            "yaml",
            "xml",
            "markdown",
            "table",
            "format",
            "structure",
            "schema",
        ],
        InterruptClass.EMOTIONALLY_LOADED: [
            "angry",
            "frustrated",
            "annoyed",
            "hate",
            "love",
            "urgent",
            "emergency",
            "critical",
        ],
        InterruptClass.DESIGN_TASK: [
            "design",
            "create",
            "build",
            "architect",
            "plan",
            "structure",
            "organize",
        ],
        InterruptClass.EXECUTION_TASK: [
            "run",
            "execute",
            "perform",
            "do",
            "start",
            "stop",
            "restart",
            "deploy",
        ],
        InterruptClass.UNSUPPORTED: ["hack", "crack", "bypass", "exploit", "attack"],
    }

    def __init__(self, pattern_cache: PatternCache):
        self._pattern_cache = pattern_cache
        self._metrics: dict[str, Any] = {
            "total_classifications": 0,
            "avg_time_ms": 0.0,
        }

    def classify(self, raw_text: str, recent_context: str) -> ClassificationResult:
        """
        Classify input in <15ms.

        Returns classification with confidence, risk, and routing decision.
        """
        start = time.perf_counter()

        # Check cache first
        cached = self._pattern_cache.get(raw_text, recent_context)
        if cached:
            template_name, confidence = cached
            # Map template to class
            class_ = self._template_to_class(template_name)
            elapsed_ms = (time.perf_counter() - start) * 1000

            return ClassificationResult(
                class_=class_,
                confidence=confidence,
                risk_score=0.1,  # Low risk for cached patterns
                known_pattern=True,
                suggested_route=CLASS_TO_PATH_TABLE.get(class_, RuntimeMode.FAST_COMMIT),
                processing_time_ms=elapsed_ms,
            )

        # Fast classification
        text_lower = raw_text.lower()
        best_class = InterruptClass.SIMPLE_REQUEST
        best_score = 0.0

        for class_, patterns in self.CLASS_PATTERNS.items():
            score = sum(1 for p in patterns if p in text_lower) / len(patterns)
            if score > best_score:
                best_score = score
                best_class = class_

        # Determine confidence and risk
        confidence = min(best_score * 2, 1.0)  # Scale up
        known_pattern = confidence > 0.5

        # Risk assessment
        risk_score = self._calculate_risk(best_class, raw_text)

        # Determine route
        if risk_score > RISK_THRESHOLD_DEEP_REPAIR:
            suggested_route = RuntimeMode.DEEP_REPAIR
        elif best_class in (InterruptClass.MISSING_REFERENCE, InterruptClass.HIGH_AMBIGUITY):
            suggested_route = RuntimeMode.INTERRUPT  # Will trigger clarification
        else:
            suggested_route = CLASS_TO_PATH_TABLE.get(best_class, RuntimeMode.FAST_COMMIT)

        elapsed_ms = (time.perf_counter() - start) * 1000

        # Update metrics
        self._update_metrics(elapsed_ms)

        return ClassificationResult(
            class_=best_class,
            confidence=confidence,
            risk_score=risk_score,
            known_pattern=known_pattern,
            suggested_route=suggested_route,
            processing_time_ms=elapsed_ms,
        )

    def _template_to_class(self, template_name: str) -> InterruptClass:
        """Map template name to interrupt class."""
        mapping = {
            "answer_direct": InterruptClass.SIMPLE_REQUEST,
            "ask_targeted_clarification": InterruptClass.MISSING_REFERENCE,
            "correct_assumption": InterruptClass.CORRECTION,
            "convert_to_schema": InterruptClass.FORMAT_REQUEST,
            "summarize_constraints": InterruptClass.SIMPLE_REQUEST,
            "emit_machine_readable_spec": InterruptClass.FORMAT_REQUEST,
            "block_unsafe_request": InterruptClass.HIGH_RISK,
        }
        return mapping.get(template_name, InterruptClass.SIMPLE_REQUEST)

    def _calculate_risk(self, class_: InterruptClass, raw_text: str) -> float:
        """Calculate risk score 0.0-1.0."""
        base_risk = {
            InterruptClass.HIGH_RISK: 0.9,
            InterruptClass.EXECUTION_TASK: 0.6,
            InterruptClass.UNSUPPORTED: 1.0,
            InterruptClass.HIGH_AMBIGUITY: 0.3,
            InterruptClass.MISSING_REFERENCE: 0.2,
        }.get(class_, 0.1)

        # Additional keyword checks
        text_lower = raw_text.lower()
        dangerous = ["delete", "drop", "shutdown", "system", "exec("]
        if any(d in text_lower for d in dangerous):
            base_risk = max(base_risk, 0.8)

        return min(base_risk, 1.0)

    def _update_metrics(self, elapsed_ms: float) -> None:
        self._metrics["total_classifications"] += 1
        n = self._metrics["total_classifications"]
        old_avg = self._metrics["avg_time_ms"]
        self._metrics["avg_time_ms"] = (old_avg * (n - 1) + elapsed_ms) / n


# ============================================================================
# SECTION 7: Active Context Manager
# ============================================================================


class ActiveContextManager:
    """
    Manages minimal active context with hard limits.

    Latency ∝ ActiveContextSize, so ReduceContext ⇒ ReduceLatency
    """

    def __init__(self, policy: Optional[ActiveContextPolicy] = None):
        self._policy = policy or ActiveContextPolicy()
        self._turns: deque[dict[str, Any]] = deque(maxlen=self._policy.max_active_turns)
        self._constraints: deque[dict[str, Any]] = deque(maxlen=self._policy.max_active_constraints)
        self._bindings: dict[str, Any] = {}
        self._goals: deque[dict[str, Any]] = deque(maxlen=self._policy.max_active_goals)

    def add_turn(self, turn: dict[str, Any]) -> None:
        """Add turn to context. Oldest auto-evicted if over limit."""
        self._turns.append(turn)

    def add_constraint(self, constraint: dict[str, Any]) -> None:
        """Add constraint."""
        self._constraints.append(constraint)

    def add_binding(self, key: str, value: Any) -> None:
        """Add binding, evict oldest if over limit."""
        if len(self._bindings) >= self._policy.max_active_bindings:
            # Evict oldest
            oldest = next(iter(self._bindings))
            del self._bindings[oldest]
        self._bindings[key] = value

    def add_goal(self, goal: dict[str, Any]) -> None:
        """Add goal."""
        self._goals.append(goal)

    def get_context_for_processing(self) -> dict[str, Any]:
        """
        Return minimal context needed for processing.
        Target load time: <20ms
        """
        return {
            "recent_turns": list(self._turns)[-3:],  # Only last 3
            "active_constraints": list(self._constraints),
            "critical_bindings": dict(list(self._bindings.items())[:5]),
            "current_goals": list(self._goals),
            "context_size": self._estimate_size(),
        }

    def _estimate_size(self) -> int:
        """Estimate total context size."""
        return len(self._turns) + len(self._constraints) + len(self._bindings) + len(self._goals)

    def apply_delta(self, delta: StateDelta) -> None:
        """Apply delta update - never rebuild."""
        for change in delta.constraint_changes:
            self.add_constraint(change)
        for change in delta.binding_changes:
            if "key" in change and "value" in change:
                self.add_binding(change["key"], change["value"])
        # etc.


# ============================================================================
# SECTION 8: Delta State Runtime
# ============================================================================


class DeltaStateRuntime:
    """
    State_{t+1} = State_t + Δ_t

    Not: State_{t+1} = RebuildAll(State_t, Input_t)
    """

    def __init__(self):
        self._state: dict[str, Any] = {
            "active_goal": None,
            "current_constraints": [],
            "recent_bindings": {},
            "current_human_state": {},
            "open_loops": [],
        }
        self._deltas: list[StateDelta] = []

    def compute_delta(
        self, input_data: dict[str, Any], classification: ClassificationResult
    ) -> StateDelta:
        """Compute minimal delta from input."""
        delta = StateDelta()

        # Only update what changed
        if "goal" in input_data:
            delta.active_goal_changes.append({"op": "set", "value": input_data["goal"]})

        if "constraints" in input_data:
            for c in input_data["constraints"]:
                delta.constraint_changes.append({"op": "add", "value": c})

        if "bindings" in input_data:
            for k, v in input_data["bindings"].items():
                delta.binding_changes.append({"key": k, "value": v})

        return delta

    def apply_delta(self, delta: StateDelta) -> None:
        """Apply delta to state."""
        for change in delta.active_goal_changes:
            if change.get("op") == "set":
                self._state["active_goal"] = change["value"]

        for change in delta.constraint_changes:
            if change.get("op") == "add":
                self._state["current_constraints"].append(change["value"])

        for change in delta.binding_changes:
            self._state["recent_bindings"][change["key"]] = change["value"]

        self._deltas.append(delta)

    def get_state(self) -> dict[str, Any]:
        """Get current state (fast, no rebuild)."""
        return self._state.copy()


# ============================================================================
# SECTION 9: Constraint Checker
# ============================================================================


class ConstraintChecker:
    """Fast constraint validation. Target: <20ms."""

    def __init__(self, constraint_cache: ConstraintCache):
        self._cache = constraint_cache

    def check_output(
        self, output: str, template: Template, active_constraints: list[dict[str, Any]]
    ) -> tuple[bool, list[str]]:
        """
        Check if output satisfies constraints.
        Returns (passed, violations).
        """
        violations = []

        for check in template.constraint_checks:
            if check == "safe_topic":
                unsafe = ["harm", "illegal", "dangerous", "weapon"]
                if any(u in output.lower() for u in unsafe):
                    violations.append("unsafe_content")

        for constraint in active_constraints:
            if not self._check_constraint(output, constraint):
                cid = constraint.get("id", "unknown")
                violations.append(f"constraint_violation: {cid}")
        return (len(violations) == 0), violations

    def _check_constraint(self, output: str, constraint: dict[str, Any]) -> bool:
        """Check single constraint."""
        ctype = constraint.get("type")

        if ctype == "max_length":
            return len(output) <= constraint.get("value", 1000)

        if ctype == "forbidden_terms":
            terms = constraint.get("terms", [])
            return not any(t in output.lower() for t in terms)

        return True


# ============================================================================
# SECTION 10: Main Ultra-Low-Latency Runtime
# ============================================================================


class AMOSUltraLowLatencyRuntime:
    """
    Main runtime implementing fast-path-first architecture.

    Pipeline: Input → Classify → FastPathCommit → BackgroundRepairIfNeeded
    """

    def __init__(
        self,
        latency_budget: Optional[LatencyBudget] = None,
        context_policy: Optional[ActiveContextPolicy] = None,
    ):
        self._latency_budget = latency_budget or LatencyBudget()
        self._context_policy = context_policy or ActiveContextPolicy()

        # Initialize caches
        self._pattern_cache = PatternCache(maxsize=10000)
        self._binding_cache = BindingCache()
        self._constraint_cache = ConstraintCache(max_constraints=12)

        # Initialize components
        self._classifier = InterruptClassifier(self._pattern_cache)
        self._template_engine = TemplateEngine()
        self._context_manager = ActiveContextManager(self._context_policy)
        self._delta_runtime = DeltaStateRuntime()
        self._constraint_checker = ConstraintChecker(self._constraint_cache)

        # Background task queue
        self._background_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._background_task: asyncio.Task[Optional[Any]] = None

        # Metrics
        self._metrics = LatencyMetrics()
        self._running = False

    async def initialize(self) -> None:
        """Initialize the runtime."""
        self._running = True
        self._background_task = asyncio.create_task(self._background_worker())
        logger.info("Ultra-low-latency runtime initialized")

    async def shutdown(self) -> None:
        """Shutdown the runtime."""
        self._running = False
        if self._background_task:
            self._background_task.cancel()
            try:
                await self._background_task
            except asyncio.CancelledError:
                pass
        logger.info("Ultra-low-latency runtime shutdown")

    async def process(self, raw_text: str, recent_context: str = "") -> FastPathResult:
        """
        Main entry point. Process input with fast-path priority.

        Target fast-path latency: <120ms total.
        """
        start_time = time.perf_counter()
        cache_hits = 0

        # === Stage 1: Interrupt Classify (<15ms) ===
        classify_start = time.perf_counter()
        classification = self._classifier.classify(raw_text, recent_context)
        classify_time = (time.perf_counter() - classify_start) * 1000

        if classification.known_pattern:
            cache_hits += 1

        # Check latency invariant
        if classify_time > self._latency_budget.interrupt_classify:
            self._metrics.invariant_violations.append(
                f"LI_CLASSIFY_EXCEEDED: {classify_time:.1f}ms"
            )

        # === Stage 2: Route by Table (<5ms) ===
        route = classification.suggested_route

        # === Stage 3: Load Minimal Context (<20ms) ===
        context_start = time.perf_counter()
        active_context = self._context_manager.get_context_for_processing()
        context_time = (time.perf_counter() - context_start) * 1000

        # === Stage 4: Pattern Match or Slot Fill (<40ms) ===
        match_start = time.perf_counter()

        if route == RuntimeMode.BLOCKED:
            output = "Request blocked: unsupported or unsafe."
            template = None
            slots = {}
            match_score = 0.0
        elif route == RuntimeMode.INTERRUPT:
            # Clarify instead of solve
            output = self._generate_clarification(classification, raw_text)
            template = None
            slots = {"missing_info": raw_text}
            match_score = 0.5
        else:
            # Fast path: Template match and fill
            template, slots, match_score = self._template_engine.match(
                raw_text, classification.class_
            )

            if template and match_score >= TEMPLATE_MATCH_THRESHOLD:
                output = self._template_engine.fill(template, slots)
                cache_hits += 1
            else:
                # Fallback: Narrow clarification
                output = self._generate_clarification(classification, raw_text)
                template = None

        match_time = (time.perf_counter() - match_start) * 1000

        # === Stage 5: Constraint Check (<20ms) ===
        check_start = time.perf_counter()

        if template:
            passed, violations = self._constraint_checker.check_output(
                output, template, active_context.get("active_constraints", [])
            )

            if not passed:
                output = f"Constraint violation: {', '.join(violations)}"
                route = RuntimeMode.DEEP_REPAIR

        check_time = (time.perf_counter() - check_start) * 1000

        # === Stage 6: Provisional Commit (<20ms) ===
        commit_start = time.perf_counter()

        # Determine if we need deep repair
        needs_deep_repair = (
            route == RuntimeMode.DEEP_REPAIR
            or classification.risk_score > RISK_THRESHOLD_DEEP_REPAIR
            or (
                classification.class_ == InterruptClass.HIGH_AMBIGUITY
                and classification.confidence < AMBIGUITY_THRESHOLD_CLARIFY
            )
        )

        # Calculate delta and update state
        delta = self._delta_runtime.compute_delta(
            {"raw_input": raw_text, "classification": classification.__dict__}, classification
        )
        self._delta_runtime.apply_delta(delta)
        self._context_manager.apply_delta(delta)

        # Queue background repair if needed
        if needs_deep_repair:
            await self._background_queue.put(
                {
                    "type": "deep_repair",
                    "input": raw_text,
                    "classification": classification,
                    "provisional_output": output,
                }
            )

        commit_time = (time.perf_counter() - commit_start) * 1000
        total_time = (time.perf_counter() - start_time) * 1000

        # Update metrics
        self._update_metrics(total_time, route == RuntimeMode.FAST_COMMIT)

        # Log performance
        logger.debug(
            f"Process: classify={classify_time:.1f}ms, "
            f"context={context_time:.1f}ms, "
            f"match={match_time:.1f}ms, "
            f"check={check_time:.1f}ms, "
            f"commit={commit_time:.1f}ms, "
            f"total={total_time:.1f}ms"
        )

        return FastPathResult(
            output=output,
            commit_mode=CommitMode.PROVISIONAL if needs_deep_repair else CommitMode.FINAL,
            latency_ms=total_time,
            template_used=template.name if template else None,
            slots_filled=slots,
            confidence=classification.confidence,
            needs_deep_repair=needs_deep_repair,
            cache_hits=cache_hits,
        )

    def _generate_clarification(self, classification: ClassificationResult, raw_text: str) -> str:
        """Generate narrow clarification instead of full solve."""
        if classification.class_ == InterruptClass.MISSING_REFERENCE:
            return (
                "I need clarification: which specific item are you referring to? "
                "Please provide the name or identifier."
            )
        elif classification.class_ == InterruptClass.HIGH_AMBIGUITY:
            return (
                "This request has multiple possible interpretations. "
                "Could you specify which direction you prefer?"
            )
        else:
            return (
                "I need more information to proceed safely. Could you clarify your specific goal?"
            )

    async def _background_worker(self) -> None:
        while self._running:
            try:
                task = await asyncio.wait_for(self._background_queue.get(), timeout=1.0)
                if task["type"] == "deep_repair":
                    await self._perform_deep_repair(task)
                self._background_queue.task_done()
            except TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Background worker error: {e}")

    async def _perform_deep_repair(self, task: dict[str, Any]) -> None:
        """
        Perform bounded deep repair.

        Invariant LI05: repair must be localized and capped at 1 round.
        """
        logger.info(f"Deep repair triggered for: {task['input'][:50]}...")

        # Bounded repair: max 1 round, smallest failed component
        await asyncio.sleep(0.1)  # Simulate repair work

        # Cache the result for future fast-path hits
        classification = task["classification"]
        self._pattern_cache.set(
            task["input"],
            "",
            "answer_direct",  # Cache as successful pattern
            min(classification.confidence + 0.1, 1.0),
        )

    def _update_metrics(self, latency_ms: float, fast_path: bool) -> None:
        """Update latency metrics."""
        self._metrics.total_requests += 1

        if fast_path:
            self._metrics.fast_path_hits += 1
        else:
            self._metrics.deep_path_triggers += 1

        # Update average
        n = self._metrics.total_requests
        old_avg = self._metrics.avg_latency_ms
        self._metrics.avg_latency_ms = (old_avg * (n - 1) + latency_ms) / n

        # Update cache hit rate
        self._metrics.cache_hit_rate = self._pattern_cache.hit_rate

    def get_metrics(self) -> LatencyMetrics:
        """Get current latency metrics."""
        return self._metrics

    def get_latency_report(self) -> dict[str, Any]:
        """Generate comprehensive latency report."""
        m = self._metrics
        return {
            "total_requests": m.total_requests,
            "fast_path_rate": m.fast_path_hits / m.total_requests if m.total_requests > 0 else 0,
            "deep_path_rate": m.deep_path_triggers / m.total_requests
            if m.total_requests > 0
            else 0,
            "avg_latency_ms": m.avg_latency_ms,
            "cache_hit_rate": m.cache_hit_rate,
            "invariant_violations": m.invariant_violations,
            "target_budget_ms": self._latency_budget.total_fast_path_target_ms,
            "meeting_target": m.avg_latency_ms <= self._latency_budget.total_fast_path_target_ms
            if m.total_requests > 10
            else None,
        }


# ============================================================================
# SECTION 11: Convenience Functions
# ============================================================================

# Global runtime instance
_global_runtime: Optional[AMOSUltraLowLatencyRuntime] = None


async def get_latency_runtime() -> AMOSUltraLowLatencyRuntime:
    """Get or create global runtime instance."""
    global _global_runtime
    if _global_runtime is None:
        _global_runtime = AMOSUltraLowLatencyRuntime()
        await _global_runtime.initialize()
    return _global_runtime


async def fast_process(raw_text: str, recent_context: str = "") -> FastPathResult:
    """Convenience function for fast processing."""
    runtime = await get_latency_runtime()
    return await runtime.process(raw_text, recent_context)


async def get_latency_report() -> dict[str, Any]:
    """Get latency report."""
    runtime = await get_latency_runtime()
    return runtime.get_latency_report()


# ============================================================================
# SECTION 12: Demo
# ============================================================================


async def demo() -> None:
    """Demonstrate ultra-low-latency runtime."""
    print("=" * 70)
    print("AMOS Ultra-Low-Latency Runtime Demo")
    print("=" * 70)

    runtime = AMOSUltraLowLatencyRuntime()
    await runtime.initialize()

    test_inputs = [
        "What is the softmax function?",
        "Explain neural networks",
        "json format please",
        "Fix that error",
        "Which one are you referring to?",
        "Maybe this or that, I'm not sure",
        "shutdown the system now",
        "Create a design for my API",
    ]

    print("\nProcessing test inputs:\n")

    for inp in test_inputs:
        result = await runtime.process(inp)

        status = (
            "⚡ FAST" if result.latency_ms < 50 else "✓ OK" if result.latency_ms < 120 else "⚠ SLOW"
        )
        deep_marker = " [DEEP]" if result.needs_deep_repair else ""

        print(f"Input: {inp[:50]}")
        print(f"  → {status} {result.latency_ms:.1f}ms{deep_marker}")
        print(f"  → Class: {result.template_used or 'clarify'}")
        print(f"  → Output: {result.output[:60]}...")
        print()

    # Print metrics
    report = runtime.get_latency_report()
    print("=" * 70)
    print("Latency Report")
    print("=" * 70)
    print(f"Total requests: {report['total_requests']}")
    print(f"Fast path rate: {report['fast_path_rate']:.1%}")
    print(f"Deep path rate: {report['deep_path_rate']:.1%}")
    print(f"Avg latency: {report['avg_latency_ms']:.1f}ms")
    print(f"Cache hit rate: {report['cache_hit_rate']:.1%}")
    print(f"Target budget: {report['target_budget_ms']}ms")
    print(f"Meeting target: {report['meeting_target']}")

    if report["invariant_violations"]:
        print(f"\nInvariant violations: {len(report['invariant_violations'])}")

    await runtime.shutdown()


if __name__ == "__main__":
    asyncio.run(demo())
