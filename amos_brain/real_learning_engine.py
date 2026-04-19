"""AMOS Real Learning Engine — Procedure / Pattern / Decision Memory

NO CHAT MEMORY • NO LOG STORAGE • NO EMBEDDING SPAM • REAL SKILL ACQUISITION

CORE PRINCIPLE: The system learns ONLY if it:
- extracts patterns
- builds reusable procedures
- applies them automatically next time

This is NOT a conversation memory system.
This IS a self-improving procedure engine.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from pathlib import Path
from typing import Any


@dataclass
class Procedure:
    """A reusable procedure extracted from a successful task.

    Stored after EVERY successful task execution.
    Contains the distilled method, not the conversation.
    """

    procedure_id: str
    name: str  # e.g., "fix_import_error", "optimize_slow_query"
    trigger_condition: str  # When to apply this procedure
    required_inputs: list[str]  # What inputs are needed
    execution_steps: list[str]  # Step-by-step method
    expected_outcome: str  # What success looks like
    verification_method: str  # How to verify it worked
    pattern_signature: str  # Hash of the problem pattern this solves
    success_count: int = 0
    failure_count: int = 0
    avg_execution_time_ms: float = 0.0
    created_at: str = ""
    last_used: str = ""
    evolution_history: list[dict] = field(default_factory=list)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.last_used:
            self.last_used = self.created_at

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0

    @property
    def confidence(self) -> float:
        """Confidence based on success rate and usage."""
        base = self.success_rate
        usage_bonus = min(0.2, self.success_count / 100)  # Cap at 0.2
        return min(1.0, base + usage_bonus)


@dataclass
class Pattern:
    """A detected problem pattern with extraction logic."""

    pattern_id: str
    pattern_type: str  # e.g., "import_error", "performance_issue"
    signature: str  # Hash identifying this pattern
    detection_rules: list[str]  # How to detect this pattern
    indicators: list[str]  # Key indicators in task description
    related_procedures: list[str]  # IDs of procedures that solve this
    frequency: int = 1
    first_seen: str = ""
    last_seen: str = ""

    def __post_init__(self):
        if not self.first_seen:
            self.first_seen = datetime.now(timezone.utc).isoformat()
        if not self.last_seen:
            self.last_seen = self.first_seen


@dataclass
class Decision:
    """A recorded decision with its rationale and outcome."""

    decision_id: str
    context_hash: str  # Hash of the decision context
    decision_type: str  # e.g., "tool_selection", "approach_choice"
    chosen_option: str
    rejected_options: list[str]
    rationale: str  # WHY this choice worked
    context_summary: str  # Key context (not full log)
    outcome: str  # "success" or "failure"
    outcome_reason: str  # Why it succeeded or failed
    procedure_used: str = None  # Which procedure was applied
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class FailurePattern:
    """What did NOT work and why - to avoid repeating mistakes."""

    failure_id: str
    pattern_signature: str  # Hash of the failure conditions
    failure_type: str  # e.g., "wrong_approach", "missing_dependency"
    what_was_tried: str  # Brief description of the failed approach
    why_it_failed: str  # Root cause analysis
    conditions: dict[str, Any]  # When this failure occurs
    avoidance_procedure: str = None  # Procedure to use instead
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class TaskClassification:
    """Classification of a task for pattern matching."""

    task_hash: str
    task_type: str  # e.g., "bug_fix", "optimization", "integration"
    key_indicators: list[str]  # Extracted from task description
    complexity: str  # "simple", "medium", "complex"
    domain: str  # e.g., "api", "database", "frontend"
    matched_pattern: str = None
    matched_procedure: str = None
    classification_time_ms: float = 0.0


class ProcedureExtractor:
    """Extracts reusable procedures from successful task executions."""

    def __init__(self, learning_engine: RealLearningEngine):
        self.engine = learning_engine

    def extract_procedure(
        self,
        task_description: str,
        solution_steps: list[str],
        outcome: dict[str, Any],
        execution_time_ms: float,
    ) -> Optional[Procedure]:
        """Extract a reusable procedure from a successful task.

        Called automatically after EVERY successful task.
        """
        if not outcome.get("success", False):
            return None  # Only learn from success

        # Generate pattern signature from task
        pattern_sig = self._generate_signature(task_description)

        # Determine procedure name from task type
        proc_name = self._classify_procedure_name(task_description)

        # Extract trigger condition
        trigger = self._extract_trigger(task_description)

        # Identify required inputs
        inputs = self._extract_inputs(task_description, solution_steps)

        # Create procedure
        procedure = Procedure(
            procedure_id=f"proc_{proc_name}_{pattern_sig[:8]}",
            name=proc_name,
            trigger_condition=trigger,
            required_inputs=inputs,
            execution_steps=solution_steps,
            expected_outcome=outcome.get("summary", "Task completed successfully"),
            verification_method=outcome.get("verification", "Verify no errors"),
            pattern_signature=pattern_sig,
            success_count=1,
            avg_execution_time_ms=execution_time_ms,
        )

        return procedure

    def _generate_signature(self, text: str) -> str:
        """Generate a hash signature for pattern matching."""
        normalized = re.sub(r"\s+", " ", text.lower().strip())
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def _classify_procedure_name(self, task_description: str) -> str:
        """Classify task into procedure name."""
        desc_lower = task_description.lower()

        if "import" in desc_lower:
            return "fix_import_error"
        elif "slow" in desc_lower or "performance" in desc_lower or "optimize" in desc_lower:
            return "optimize_performance"
        elif "merge" in desc_lower or "duplicate" in desc_lower:
            return "merge_duplicate_files"
        elif "routing" in desc_lower or "route" in desc_lower:
            return "fix_routing_bug"
        elif "connect" in desc_lower or "integration" in desc_lower:
            return "connect_tool"
        elif "latency" in desc_lower:
            return "reduce_latency"
        elif "repair" in desc_lower or "broken" in desc_lower:
            return "repair_broken_integration"
        else:
            return f"generic_{self._generate_signature(task_description)[:6]}"

    def _extract_trigger(self, task_description: str) -> str:
        """Extract the trigger condition from task."""
        # Extract key error patterns or indicators
        indicators = []
        desc_lower = task_description.lower()

        if "import" in desc_lower:
            indicators.append("ImportError or ModuleNotFoundError")
        if "slow" in desc_lower:
            indicators.append("Response time > threshold")
        if "404" in desc_lower or "not found" in desc_lower:
            indicators.append("HTTP 404 errors")
        if "500" in desc_lower:
            indicators.append("HTTP 500 errors")

        return " AND ".join(indicators) if indicators else "Task matches pattern signature"

    def _extract_inputs(self, task_description: str, steps: list[str]) -> list[str]:
        """Extract required inputs from task and steps."""
        inputs = []

        # Look for file paths
        file_matches = re.findall(r"[\w/]+\.py|\w+\.json|\w+\.yml", task_description)
        if file_matches:
            inputs.append("file_paths")

        # Look for module names
        if "import" in task_description.lower():
            inputs.append("module_name")

        # Look for configuration needs
        if "config" in task_description.lower() or "setting" in task_description.lower():
            inputs.append("configuration")

        return inputs if inputs else ["task_context"]


class PatternDetector:
    """Detects patterns in tasks for matching against known procedures."""

    def __init__(self, learning_engine: RealLearningEngine):
        self.engine = learning_engine

    def detect_pattern(self, task_description: str, context: dict[str, Any]) -> Optional[Pattern]:
        """Detect what pattern a task matches."""
        desc_lower = task_description.lower()

        # Check against known patterns
        for pattern in self.engine.patterns.values():
            if self._matches_pattern(desc_lower, pattern):
                pattern.frequency += 1
                pattern.last_seen = datetime.now(timezone.utc).isoformat()
                return pattern

        # Create new pattern if no match
        return self._create_new_pattern(task_description, context)

    def _matches_pattern(self, task_lower: str, pattern: Pattern) -> bool:
        """Check if task matches a pattern."""
        # Check indicators
        for indicator in pattern.indicators:
            if indicator.lower() in task_lower:
                return True

        # Check detection rules
        for rule in pattern.detection_rules:
            if self._evaluate_rule(rule, task_lower):
                return True

        return False

    def _evaluate_rule(self, rule: str, task_lower: str) -> bool:
        """Evaluate a detection rule against task."""
        # Simple rule evaluation
        parts = rule.lower().split(" and ")
        return all(part.strip() in task_lower for part in parts)

    def _create_new_pattern(self, task_description: str, context: dict[str, Any]) -> Pattern:
        """Create a new pattern from a task."""
        sig = hashlib.sha256(task_description.lower().encode()).hexdigest()[:16]

        # Extract indicators
        indicators = self._extract_indicators(task_description)

        # Determine pattern type
        pattern_type = self._classify_pattern_type(task_description)

        pattern = Pattern(
            pattern_id=f"pat_{pattern_type}_{sig[:8]}",
            pattern_type=pattern_type,
            signature=sig,
            detection_rules=[f"contains: {ind}" for ind in indicators[:3]],
            indicators=indicators,
            related_procedures=[],
        )

        self.engine.patterns[pattern.pattern_id] = pattern
        return pattern

    def _extract_indicators(self, task_description: str) -> list[str]:
        """Extract key indicators from task."""
        desc_lower = task_description.lower()
        indicators = []

        # Common patterns
        keywords = [
            "error",
            "bug",
            "fix",
            "slow",
            "optimize",
            "connect",
            "import",
            "merge",
            "duplicate",
            "routing",
            "latency",
            "repair",
            "broken",
            "integration",
            "memory",
            "performance",
        ]

        for kw in keywords:
            if kw in desc_lower:
                indicators.append(kw)

        return indicators if indicators else ["generic"]

    def _classify_pattern_type(self, task_description: str) -> str:
        """Classify the pattern type."""
        desc_lower = task_description.lower()

        if "import" in desc_lower:
            return "import_error"
        elif "slow" in desc_lower or "performance" in desc_lower:
            return "performance_issue"
        elif "bug" in desc_lower or "error" in desc_lower:
            return "bug_fix"
        elif "connect" in desc_lower or "integration" in desc_lower:
            return "integration_task"
        else:
            return "general"


class AutoReuseEngine:
    """Automatically reuses known procedures without re-analysis."""

    def __init__(self, learning_engine: RealLearningEngine):
        self.engine = learning_engine
        self.reuse_stats = {"procedures_reused": 0, "time_saved_ms": 0}

    def attempt_reuse(self, task_description: str, context: dict[str, Any]) -> dict:
        """Attempt to reuse a known procedure for this task.

        Returns execution plan if match found, None if needs fresh analysis.
        """
        start_time = datetime.now(timezone.utc)

        # Detect pattern
        pattern = self.engine.pattern_detector.detect_pattern(task_description, context)
        if not pattern:
            return None

        # Find matching procedure
        procedure = self._find_matching_procedure(pattern, task_description)
        if not procedure:
            return None

        # Calculate time saved (vs full analysis)
        end_time = datetime.now(timezone.utc)
        time_ms = (end_time - start_time).total_seconds() * 1000
        self.reuse_stats["time_saved_ms"] += 1000 - time_ms  # Assume 1s for analysis
        self.reuse_stats["procedures_reused"] += 1

        # Update procedure
        procedure.last_used = datetime.now(timezone.utc).isoformat()

        return {
            "reused": True,
            "procedure_id": procedure.procedure_id,
            "procedure_name": procedure.name,
            "steps": procedure.execution_steps,
            "expected_outcome": procedure.expected_outcome,
            "verification": procedure.verification_method,
            "confidence": procedure.confidence,
            "pattern_matched": pattern.pattern_id,
            "bypass_analysis": True,  # Skip re-analysis
        }

    def _find_matching_procedure(self, pattern: Pattern, task_desc: str) -> Optional[Procedure]:
        """Find best matching procedure for a pattern."""
        candidates = []

        # Check related procedures
        for proc_id in pattern.related_procedures:
            if proc_id in self.engine.procedures:
                proc = self.engine.procedures[proc_id]
                candidates.append((proc.confidence, proc))

        # Also check by signature match
        task_sig = hashlib.sha256(task_desc.lower().encode()).hexdigest()[:16]
        for proc in self.engine.procedures.values():
            if proc.pattern_signature[:8] == task_sig[:8]:
                candidates.append((proc.confidence, proc))

        if not candidates:
            return None

        # Return highest confidence procedure
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1] if candidates[0][0] > 0.5 else None


class DecisionRecorder:
    """Records decisions with rationale for future learning."""

    def __init__(self, learning_engine: RealLearningEngine):
        self.engine = learning_engine

    def record_decision(
        self,
        decision_type: str,
        context: dict[str, Any],
        chosen_option: str,
        rejected_options: list[str],
        rationale: str,
        outcome: dict[str, Any],
        procedure_used: str = None,
    ) -> Decision:
        """Record a decision and its outcome."""
        # Create context summary (not full log)
        context_summary = self._summarize_context(context)
        context_hash = hashlib.sha256(json.dumps(context, sort_keys=True).encode()).hexdigest()[:16]

        decision = Decision(
            decision_id=f"dec_{decision_type}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            context_hash=context_hash,
            decision_type=decision_type,
            chosen_option=chosen_option,
            rejected_options=rejected_options,
            rationale=rationale,
            context_summary=context_summary,
            outcome="success" if outcome.get("success", False) else "failure",
            outcome_reason=outcome.get("reason", "Unknown"),
            procedure_used=procedure_used,
        )

        self.engine.decisions[decision.decision_id] = decision
        return decision

    def get_decision_rationale(self, decision_type: str, context: dict[str, Any]) -> str:
        """Retrieve rationale for similar past decisions."""
        context_hash = hashlib.sha256(json.dumps(context, sort_keys=True).encode()).hexdigest()[:16]

        # Find similar decisions
        for decision in self.engine.decisions.values():
            if decision.decision_type == decision_type and decision.outcome == "success":
                if decision.context_hash == context_hash:
                    return decision.rationale

        return None

    def _summarize_context(self, context: dict[str, Any]) -> str:
        """Create minimal context summary (no bloat)."""
        # Extract only key fields
        summary_parts = []

        if "task_type" in context:
            summary_parts.append(f"type:{context['task_type']}")
        if "error_type" in context:
            summary_parts.append(f"error:{context['error_type']}")
        if "tools_available" in context:
            summary_parts.append(f"tools:{len(context['tools_available'])}")

        return "|".join(summary_parts) if summary_parts else "minimal"


class FailureMemory:
    """Records failure patterns to avoid repeating mistakes."""

    def __init__(self, learning_engine: RealLearningEngine):
        self.engine = learning_engine

    def record_failure(
        self,
        what_was_tried: str,
        why_it_failed: str,
        conditions: dict[str, Any],
        alternative_procedure: str = None,
    ) -> FailurePattern:
        """Record a failure pattern."""
        conditions_hash = hashlib.sha256(
            json.dumps(conditions, sort_keys=True).encode()
        ).hexdigest()[:16]

        failure = FailurePattern(
            failure_id=f"fail_{conditions_hash}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            pattern_signature=conditions_hash,
            failure_type=self._classify_failure_type(why_it_failed),
            what_was_tried=what_was_tried,
            why_it_failed=why_it_failed,
            conditions=conditions,
            avoidance_procedure=alternative_procedure,
        )

        self.engine.failures[failure.failure_id] = failure
        return failure

    def check_avoidance(self, approach: str, conditions: dict[str, Any]) -> str:
        """Check if an approach should be avoided."""
        conditions_hash = hashlib.sha256(
            json.dumps(conditions, sort_keys=True).encode()
        ).hexdigest()[:16]

        for failure in self.engine.failures.values():
            if failure.pattern_signature == conditions_hash:
                if approach.lower() in failure.what_was_tried.lower():
                    return f"Avoid: {failure.why_it_failed}. Use: {failure.avoidance_procedure or 'alternative'}"

        return None

    def _classify_failure_type(self, reason: str) -> str:
        """Classify the type of failure."""
        reason_lower = reason.lower()

        if "timeout" in reason_lower or "slow" in reason_lower:
            return "timeout"
        elif "import" in reason_lower or "module" in reason_lower:
            return "import_error"
        elif "permission" in reason_lower or "access" in reason_lower:
            return "permission_denied"
        elif "memory" in reason_lower:
            return "out_of_memory"
        else:
            return "general"


class ProcedureEvolutionEngine:
    """Evolves procedures when better solutions are found."""

    def __init__(self, learning_engine: RealLearningEngine):
        self.engine = learning_engine

    def evolve_procedure(
        self, procedure_id: str, improved_steps: list[str], improvement_rationale: str
    ) -> Optional[Procedure]:
        """Evolve an existing procedure with improved steps."""
        if procedure_id not in self.engine.procedures:
            return None

        old_proc = self.engine.procedures[procedure_id]

        # Create evolved version
        new_proc = Procedure(
            procedure_id=f"{procedure_id}_v{len(old_proc.evolution_history) + 2}",
            name=old_proc.name,
            trigger_condition=old_proc.trigger_condition,
            required_inputs=old_proc.required_inputs,
            execution_steps=improved_steps,
            expected_outcome=old_proc.expected_outcome,
            verification_method=old_proc.verification_method,
            pattern_signature=old_proc.pattern_signature,
            success_count=0,  # Reset for new version
            failure_count=0,
            created_at=datetime.now(timezone.utc).isoformat(),
            evolution_history=old_proc.evolution_history
            + [
                {
                    "from_version": procedure_id,
                    "improvement": improvement_rationale,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        )

        self.engine.procedures[new_proc.procedure_id] = new_proc

        # Update pattern to point to new version
        for pattern in self.engine.patterns.values():
            if procedure_id in pattern.related_procedures:
                pattern.related_procedures.remove(procedure_id)
                pattern.related_procedures.append(new_proc.procedure_id)

        return new_proc

    def merge_procedures(self, procedure_ids: list[str]) -> Optional[Procedure]:
        """Merge multiple similar procedures into one optimized version."""
        if len(procedure_ids) < 2:
            return None

        # Collect all unique steps
        all_steps = []
        common_trigger = None

        for pid in procedure_ids:
            if pid in self.engine.procedures:
                proc = self.engine.procedures[pid]
                all_steps.extend(proc.execution_steps)
                if common_trigger is None:
                    common_trigger = proc.trigger_condition

        # Remove duplicates while preserving order
        seen = set()
        unique_steps = []
        for step in all_steps:
            step_key = step.lower().strip()
            if step_key not in seen:
                seen.add(step_key)
                unique_steps.append(step)

        # Create merged procedure
        merged = Procedure(
            procedure_id=f"proc_merged_{hashlib.sha256(json.dumps(procedure_ids).encode()).hexdigest()[:8]}",
            name=f"merged_{len(procedure_ids)}_variants",
            trigger_condition=common_trigger or "merged_conditions",
            required_inputs=["task_context"],
            execution_steps=unique_steps,
            expected_outcome="Task completed via merged procedure",
            verification_method="Verify all merged conditions satisfied",
            pattern_signature=hashlib.sha256(common_trigger.encode()).hexdigest()[:16]
            if common_trigger
            else "",
            evolution_history=[
                {"merged_from": procedure_ids, "timestamp": datetime.now(timezone.utc).isoformat()}
            ],
        )

        self.engine.procedures[merged.procedure_id] = merged
        return merged


class TaskPatternClassifier:
    """Classifies tasks for fast pattern matching."""

    def __init__(self, learning_engine: RealLearningEngine):
        self.engine = learning_engine

    def classify_task(self, task_description: str, context: dict[str, Any]) -> TaskClassification:
        """Classify a task for fast matching."""
        start_time = datetime.now(timezone.utc)

        # Extract key indicators
        indicators = self._extract_indicators(task_description)

        # Determine type
        task_type = self._determine_task_type(task_description)

        # Assess complexity
        complexity = self._assess_complexity(task_description, context)

        # Determine domain
        domain = self._determine_domain(task_description, context)

        # Generate hash
        task_hash = hashlib.sha256(task_description.lower().encode()).hexdigest()[:16]

        # Check for existing pattern match
        matched_pattern = None
        matched_procedure = None

        for pattern in self.engine.patterns.values():
            if any(ind in pattern.indicators for ind in indicators):
                matched_pattern = pattern.pattern_id
                if pattern.related_procedures:
                    matched_procedure = pattern.related_procedures[0]
                break

        end_time = datetime.now(timezone.utc)
        time_ms = (end_time - start_time).total_seconds() * 1000

        return TaskClassification(
            task_hash=task_hash,
            task_type=task_type,
            key_indicators=indicators,
            complexity=complexity,
            domain=domain,
            matched_pattern=matched_pattern,
            matched_procedure=matched_procedure,
            classification_time_ms=time_ms,
        )

    def _extract_indicators(self, task_description: str) -> list[str]:
        """Extract classification indicators."""
        desc_lower = task_description.lower()
        indicators = []

        keywords = {
            "fix": "repair",
            "bug": "repair",
            "error": "repair",
            "optimize": "optimize",
            "slow": "optimize",
            "performance": "optimize",
            "connect": "integrate",
            "integration": "integrate",
            "import": "import",
            "merge": "organize",
            "duplicate": "organize",
            "implement": "create",
            "create": "create",
            "add": "create",
            "test": "verify",
            "verify": "verify",
        }

        for kw, category in keywords.items():
            if kw in desc_lower:
                indicators.append(category)

        return list(set(indicators)) if indicators else ["general"]

    def _determine_task_type(self, task_description: str) -> str:
        """Determine the task type."""
        desc_lower = task_description.lower()

        if any(w in desc_lower for w in ["fix", "bug", "error", "repair"]):
            return "bug_fix"
        elif any(w in desc_lower for w in ["optimize", "slow", "performance", "improve"]):
            return "optimization"
        elif any(w in desc_lower for w in ["connect", "integrate", "bridge"]):
            return "integration"
        elif any(w in desc_lower for w in ["implement", "create", "add"]):
            return "implementation"
        else:
            return "general"

    def _assess_complexity(self, task_description: str, context: dict[str, Any]) -> str:
        """Assess task complexity."""
        # Simple heuristic based on description length and keywords
        length = len(task_description)

        if length < 50:
            return "simple"
        elif length < 200:
            return "medium"
        else:
            return "complex"

    def _determine_domain(self, task_description: str, context: dict[str, Any]) -> str:
        """Determine the domain."""
        desc_lower = task_description.lower()

        if any(w in desc_lower for w in ["api", "endpoint", "route", "http"]):
            return "api"
        elif any(w in desc_lower for w in ["database", "db", "query", "sql"]):
            return "database"
        elif any(w in desc_lower for w in ["frontend", "ui", "component", "html"]):
            return "frontend"
        elif any(w in desc_lower for w in ["import", "module", "package"]):
            return "module_system"
        else:
            return "general"


class RealLearningEngine:
    """AMOS Real Learning Engine — The Core Learning System.

    NO CHAT MEMORY • NO LOG STORAGE • NO EMBEDDING SPAM

    Stores ONLY:
    - Distilled procedures
    - Patterns
    - Decisions

    Enables:
    - Pattern matching before solving
    - Automatic procedure reuse
    - Failure avoidance
    - Continuous evolution
    """

    def __init__(self, storage_path: str = "./amos_learning"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Core registries (minimal, no bloat)
        self.procedures: dict[str, Procedure] = {}
        self.patterns: dict[str, Pattern] = {}
        self.decisions: dict[str, Decision] = {}
        self.failures: dict[str, FailurePattern] = {}

        # Subsystems
        self.procedure_extractor = ProcedureExtractor(self)
        self.pattern_detector = PatternDetector(self)
        self.auto_reuse_engine = AutoReuseEngine(self)
        self.decision_recorder = DecisionRecorder(self)
        self.failure_memory = FailureMemory(self)
        self.procedure_evolution = ProcedureEvolutionEngine(self)
        self.task_classifier = TaskPatternClassifier(self)

        # Statistics
        self.stats = {
            "procedures_learned": 0,
            "patterns_detected": 0,
            "decisions_recorded": 0,
            "failures_avoided": 0,
            "procedures_reused": 0,
            "time_saved_ms": 0,
            "learning_start": datetime.now(timezone.utc).isoformat(),
        }

        # Load existing learning
        self._load_learning()

    def learn_from_success(
        self,
        task_description: str,
        solution_steps: list[str],
        outcome: dict[str, Any],
        execution_time_ms: float = 0,
        context: dict[str, Any] = None,
    ) -> Optional[Procedure]:
        """Learn from a successful task execution.

        Called automatically after EVERY successful task.
        Extracts reusable procedure and updates patterns.
        """
        # Extract procedure
        procedure = self.procedure_extractor.extract_procedure(
            task_description, solution_steps, outcome, execution_time_ms
        )

        if not procedure:
            return None

        # Store procedure
        self.procedures[procedure.procedure_id] = procedure
        self.stats["procedures_learned"] += 1

        # Detect/associate pattern
        pattern = self.pattern_detector.detect_pattern(task_description, context or {})
        if pattern and procedure.procedure_id not in pattern.related_procedures:
            pattern.related_procedures.append(procedure.procedure_id)

        self.stats["patterns_detected"] = len(self.patterns)

        # Persist
        self._save_learning()

        return procedure

    def attempt_reuse(self, task_description: str, context: dict[str, Any] = None) -> dict:
        """Attempt to reuse known procedure for this task.

        BEFORE solving any task, call this.
        If match found → execute stored procedure directly.
        If no match → solve and learn.
        """
        # Classify task first
        classification = self.task_classifier.classify_task(task_description, context or {})

        # Check for direct procedure match
        if classification.matched_procedure:
            proc = self.procedures.get(classification.matched_procedure)
            if proc and proc.confidence > 0.5:
                self.stats["procedures_reused"] += 1
                proc.last_used = datetime.now(timezone.utc).isoformat()
                return {
                    "reused": True,
                    "procedure_id": proc.procedure_id,
                    "procedure_name": proc.name,
                    "steps": proc.execution_steps,
                    "expected_outcome": proc.expected_outcome,
                    "verification": proc.verification_method,
                    "confidence": proc.confidence,
                    "classification": classification,
                    "bypass_analysis": True,
                }

        # Try pattern-based reuse
        reuse_result = self.auto_reuse_engine.attempt_reuse(task_description, context or {})

        if reuse_result:
            self.stats["procedures_reused"] += 1
            self.stats["time_saved_ms"] += reuse_result.get("time_saved_ms", 0)

        return reuse_result

    def record_decision(
        self,
        decision_type: str,
        context: dict[str, Any],
        chosen_option: str,
        rejected_options: list[str],
        rationale: str,
        outcome: dict[str, Any],
        procedure_used: str = None,
    ) -> Decision:
        """Record a decision for future learning."""
        decision = self.decision_recorder.record_decision(
            decision_type,
            context,
            chosen_option,
            rejected_options,
            rationale,
            outcome,
            procedure_used,
        )
        self.stats["decisions_recorded"] += 1
        self._save_learning()
        return decision

    def record_failure(
        self,
        what_was_tried: str,
        why_it_failed: str,
        conditions: dict[str, Any],
        alternative_procedure: str = None,
    ) -> FailurePattern:
        """Record a failure to avoid repeating it."""
        failure = self.failure_memory.record_failure(
            what_was_tried, why_it_failed, conditions, alternative_procedure
        )
        self._save_learning()
        return failure

    def check_failure_avoidance(self, approach: str, conditions: dict[str, Any]) -> str:
        """Check if an approach should be avoided."""
        return self.failure_memory.check_avoidance(approach, conditions)

    def evolve_procedure(
        self, procedure_id: str, improved_steps: list[str], improvement_rationale: str
    ) -> Optional[Procedure]:
        """Evolve a procedure with a better solution."""
        evolved = self.procedure_evolution.evolve_procedure(
            procedure_id, improved_steps, improvement_rationale
        )
        if evolved:
            self._save_learning()
        return evolved

    def get_learning_state(self) -> dict[str, Any]:
        """Get current learning state (minimal, no bloat)."""
        # Calculate procedure success rates
        success_rates = [p.success_rate for p in self.procedures.values()]
        avg_success = sum(success_rates) / len(success_rates) if success_rates else 0.0

        # Top procedures by confidence
        top_procedures = sorted(self.procedures.values(), key=lambda p: p.confidence, reverse=True)[
            :5
        ]

        return {
            "procedures_stored": len(self.procedures),
            "patterns_stored": len(self.patterns),
            "decisions_stored": len(self.decisions),
            "failures_recorded": len(self.failures),
            "avg_procedure_confidence": round(avg_success, 2),
            "procedures_reused": self.stats["procedures_reused"],
            "time_saved_ms": self.stats["time_saved_ms"],
            "learning_active_since": self.stats["learning_start"],
            "top_procedures": [
                {"name": p.name, "confidence": round(p.confidence, 2), "uses": p.success_count}
                for p in top_procedures
            ],
        }

    def _save_learning(self):
        """Persist learning to minimal storage."""
        learning_data = {
            "procedures": {k: asdict(v) for k, v in self.procedures.items()},
            "patterns": {k: asdict(v) for k, v in self.patterns.items()},
            "decisions": {k: asdict(v) for k, v in self.decisions.items()},
            "failures": {k: asdict(v) for k, v in self.failures.items()},
            "stats": self.stats,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }

        storage_file = self.storage_path / "learning_store.json"
        with open(storage_file, "w") as f:
            json.dump(learning_data, f, indent=2)

    def _load_learning(self):
        """Load existing learning from storage."""
        storage_file = self.storage_path / "learning_store.json"
        if not storage_file.exists():
            return

        try:
            with open(storage_file) as f:
                data = json.load(f)

            # Restore procedures
            for proc_id, proc_data in data.get("procedures", {}).items():
                self.procedures[proc_id] = Procedure(**proc_data)

            # Restore patterns
            for pat_id, pat_data in data.get("patterns", {}).items():
                self.patterns[pat_id] = Pattern(**pat_data)

            # Restore decisions
            for dec_id, dec_data in data.get("decisions", {}).items():
                self.decisions[dec_id] = Decision(**dec_data)

            # Restore failures
            for fail_id, fail_data in data.get("failures", {}).items():
                self.failures[fail_id] = FailurePattern(**fail_data)

            # Restore stats
            self.stats.update(data.get("stats", {}))

        except Exception:
            # If load fails, start fresh (no bloat recovery)
            pass


# Global learning engine instance
_learning_engine: Optional[RealLearningEngine] = None


def get_learning_engine(storage_path: str = "./amos_learning") -> RealLearningEngine:
    """Get or create the global learning engine."""
    global _learning_engine
    if _learning_engine is None:
        _learning_engine = RealLearningEngine(storage_path)
    return _learning_engine


def learn_from_task(
    task_description: str,
    solution_steps: list[str],
    outcome: dict[str, Any],
    execution_time_ms: float = 0,
    context: dict[str, Any] = None,
) -> Optional[Procedure]:
    """Convenience function: learn from a successful task."""
    engine = get_learning_engine()
    return engine.learn_from_success(
        task_description, solution_steps, outcome, execution_time_ms, context
    )


def attempt_procedure_reuse(task_description: str, context: dict[str, Any] = None) -> dict:
    """Convenience function: attempt to reuse a procedure."""
    engine = get_learning_engine()
    return engine.attempt_reuse(task_description, context)
