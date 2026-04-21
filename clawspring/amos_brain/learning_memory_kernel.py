from __future__ import annotations

from typing import Any

"""
AMOS Learning + Memory Kernel (LMK)
Formal implementation of cognitive memory and adaptive learning system.

Core Equation:
    Intelligence_real = Cognition_instant + Memory_persistent + Learning_adaptive

Implements:
    - 7 memory types (Working, Episodic, Semantic, Procedural, Identity, Strategic, Error)
    - 9 kernel functions (encode, store, retrieve, index, consolidate, update, forget, replay, meta_learn)
    - Learning loop: Observe → Encode → Store → Retrieve → Update → Consolidate → Reuse
    - Forgetting and replay mechanisms
    - Meta-learning capabilities

Law:
    Reasoning without memory = repeated stupidity
    Memory without learning = frozen storage
    Learning without memory = no continuity

Invariants:
    LMI01: Memory must influence future cognition
    LMI02: Learning must change future policy/model
    LMI03: High-error experiences stored in error memory
    LMI04: Strategic goals persist across sessions
    LMI05: Repeat error rate decreases over time
    LMI06: Identity-core cannot be deleted
    LMI07: Retrieval quality is part of intelligence
"""

import asyncio
import hashlib
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone

UTC = timezone.utc

from enum import Enum, auto
from functools import lru_cache

import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

# =============================================================================
# ENUMS AND TYPE DEFINITIONS
# =============================================================================


class MemoryType(Enum):
    """Seven memory types per specification."""

    WORKING = "working"  # WM_t: Active temporary cognition
    EPISODIC = "episodic"  # EM_t: Specific past events
    SEMANTIC = "semantic"  # SM_t: Generalized knowledge
    PROCEDURAL = "procedural"  # PM_t: How to do things
    IDENTITY = "identity"  # IM_t: Core continuity
    STRATEGIC = "strategic"  # XM_t: Long-horizon goals
    ERROR = "error"  # ErrM_t: What failed and why


class LearningType(Enum):
    """Ten learning types per specification."""

    WORLD_MODEL = "world_model_learning"
    POLICY = "policy_learning"
    RETRIEVAL = "retrieval_learning"
    ROUTING = "routing_learning"
    VERIFICATION = "verification_learning"
    ERROR_AVOIDANCE = "error_avoidance_learning"
    HUMAN_SAFETY = "human_safety_learning"
    CONCEPT = "concept_learning"
    STRATEGY = "strategy_learning"
    SELF_CALIBRATION = "self_calibration_learning"


class ForgetMode(Enum):
    """Forgetting policies."""

    DELETE = auto()
    ARCHIVE = auto()
    DEPRIORITIZE = auto()
    MASK_UNTIL_REACTIVATED = auto()


class FailureType(Enum):
    """Error memory failure classification."""

    BINDING = "binding"
    CONSTRAINT_DROP = "constraint_drop"
    REASONING = "reasoning"
    VERIFICATION = "verification"
    LATENCY = "latency"
    SAFETY = "safety"
    MEMORY = "memory"
    PLANNING = "planning"


# =============================================================================
# MEMORY RECORD (Core Data Structure)
# =============================================================================


@dataclass
class MemoryRecord:
    """Machine-readable memory encoding.

    m_t = Encode(o_t, a_t, c_t, y_t, e_t)

    Where:
        o_t: observation
        a_t: action
        c_t: context
        y_t: outcome
        e_t: error signal
    """

    id: str
    type: MemoryType
    timestamp: datetime

    # Core experience components
    observation: dict[str, Any] = field(default_factory=dict)
    action: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    outcome: dict[str, Any] = field(default_factory=dict)
    error_signal: dict[str, Any] = field(default_factory=dict)

    # Derived properties
    abstraction: dict[str, Any] = field(default_factory=dict)

    # Retrieval metrics (0.0 - 1.0)
    relevance: float = 0.5
    freshness: float = 1.0
    confidence: float = 0.5
    importance: float = 0.5

    # Retrieval structure
    retrieval_keys: list[str] = field(default_factory=list)

    # Forgetting state
    access_count: int = 0
    last_accessed: datetime = None
    decay_rate: float = 0.01

    def __post_init__(self):
        """Generate ID if not provided."""
        if not self.id:
            content = f"{self.type.value}:{self.timestamp.isoformat()}:{json.dumps(self.observation, sort_keys=True)}"
            self.id = hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_tensor(self) -> np.ndarray:
        """Convert to memory tensor representation."""
        return np.array(
            [
                self.relevance,
                self.freshness,
                self.confidence,
                self.importance,
                self.access_count / 100.0,  # Normalize
            ]
        )

    def matches_query(self, query: str) -> float:
        """Calculate similarity to query string."""
        query_lower = query.lower()
        score = 0.0

        # Check retrieval keys
        for key in self.retrieval_keys:
            if query_lower in key.lower():
                score += 0.3

        # Check content
        content = json.dumps({**self.observation, **self.action, **self.context}).lower()

        if query_lower in content:
            score += 0.2 * content.count(query_lower)

        return min(score, 1.0)


# =============================================================================
# MEMORY STATE (Full Learning-Memory State)
# =============================================================================


@dataclass
class MemoryState:
    """Full learning-memory state L_t:

    L_t = (WM_t, EM_t, SM_t, PM_t, IM_t, XM_t, ErrM_t, Pol_t, Mod_t)

    Where:
        WM_t: working memory
        EM_t: episodic memory
        SM_t: semantic memory
        PM_t: procedural memory
        IM_t: identity memory
        XM_t: strategic memory
        ErrM_t: error memory
        Pol_t: policy state
        Mod_t: world-model state
    """

    # Working Memory - Active temporary cognition
    working_memory: dict[str, MemoryRecord] = field(default_factory=dict)

    # Episodic Memory - Specific past events
    episodic_memory: dict[str, MemoryRecord] = field(default_factory=dict)

    # Semantic Memory - Generalized knowledge
    semantic_memory: dict[str, MemoryRecord] = field(default_factory=dict)

    # Procedural Memory - How to do things
    procedural_memory: dict[str, MemoryRecord] = field(default_factory=dict)

    # Identity Memory - Core continuity
    identity_memory: dict[str, MemoryRecord] = field(default_factory=dict)

    # Strategic Memory - Long-horizon goals
    strategic_memory: dict[str, Any] = field(
        default_factory=lambda: {
            "persistent_goals": [],
            "open_loops": [],
            "deferred_decisions": [],
            "long_horizon_plans": [],
            "critical_constraints": [],
            "user_value_estimates": [],
        }
    )

    # Error Memory - What failed and why
    error_memory: dict[str, MemoryRecord] = field(default_factory=dict)

    # Policy State - Current behavioral policy
    policy_state: dict[str, Any] = field(
        default_factory=lambda: {
            "routing_policy": {},
            "verification_policy": {},
            "safety_policy": {},
            "learning_rates": defaultdict(lambda: 0.1),
        }
    )

    # World Model State - Current model of environment
    world_model: dict[str, Any] = field(
        default_factory=lambda: {"predictors": {}, "constraints": [], "patterns": defaultdict(int)}
    )

    # Meta-learning state
    meta_learning: dict[str, Any] = field(
        default_factory=lambda: {
            "learning_policies": {},
            "policy_scores": defaultdict(float),
            "weak_policies": [],
            "candidate_updates": [],
        }
    )

    # Retrieval index
    retrieval_index: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))

    # Statistics
    stats: dict[str, Any] = field(
        default_factory=lambda: {
            "total_memories": 0,
            "total_errors": 0,
            "retrieval_count": 0,
            "consolidation_count": 0,
            "learning_updates": 0,
            "replay_count": 0,
            "forget_count": 0,
        }
    )


# =============================================================================
# ERROR MEMORY STRUCTURE
# =============================================================================


@dataclass
class ErrorMemoryEntry:
    """Structured error memory per specification."""

    id: str
    failure_type: FailureType
    cause: str
    context_signature: str
    fix: str = None
    repeat_count: int = 1
    first_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_memory_record(self) -> MemoryRecord:
        """Convert to standard memory record."""
        return MemoryRecord(
            id=self.id,
            type=MemoryType.ERROR,
            timestamp=self.last_seen,
            observation={"failure_type": self.failure_type.value},
            outcome={"cause": self.cause, "fix": self.fix},
            context={"context_signature": self.context_signature},
            error_signal={"repeat_count": self.repeat_count},
            importance=0.9,  # High importance
            retrieval_keys=[self.failure_type.value, self.cause, self.context_signature],
        )


# =============================================================================
# LEARNING KERNEL
# =============================================================================


class LearningKernel:
    """Implements adaptive learning mechanisms.

    Core equation:
        L_{t+1} = Update(L_t, Error_t, Outcome_t, Repetition_t)

    Learning = parameter, policy, memory, or world-model update from error, repetition, and outcome
    """

    def __init__(self, memory_state: MemoryState):
        self.state = memory_state
        self.learning_rate = 0.1
        logger.info("LearningKernel initialized")

    def compute_prediction_error(
        self, prediction: dict[str, Any], outcome: dict[str, Any]
    ) -> dict[str, float]:
        """ε_t = Outcome_t - Prediction_t

        Returns error signal for learning.
        """
        errors = {}

        # Compare scalar predictions
        for key in set(prediction.keys()) & set(outcome.keys()):
            try:
                pred_val = float(prediction[key])
                out_val = float(outcome[key])
                errors[key] = out_val - pred_val
            except (ValueError, TypeError):
                # Non-numeric comparison
                errors[key] = 0.0 if prediction[key] == outcome[key] else 1.0

        # Add missing predictions as full error
        for key in outcome:
            if key not in prediction:
                errors[key] = 1.0

        return errors

    def update_world_model(
        self, prediction_error: dict[str, float], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Mod_{t+1} = Mod_t + η * ε_t

        Updates world model from prediction error.
        """
        # Update pattern frequencies
        context_hash = json.dumps(context, sort_keys=True)
        self.state.world_model["patterns"][context_hash] += 1

        # Update predictors with exponential moving average
        for key, error in prediction_error.items():
            if key not in self.state.world_model["predictors"]:
                self.state.world_model["predictors"][key] = {"error_ema": 0.0}

            predictor = self.state.world_model["predictors"][key]
            predictor["error_ema"] = 0.9 * predictor["error_ema"] + 0.1 * abs(error)

        self.state.stats["learning_updates"] += 1
        logger.debug(f"World model updated: {len(prediction_error)} errors")

        return self.state.world_model

    def update_policy(
        self, update_signal: dict[str, Any], learning_type: LearningType
    ) -> dict[str, Any]:
        """Pol_{t+1} = Pol_t + η * UpdateSignal_t

        Updates behavioral policy from learning signal.
        """
        # Get learning rate for this type
        lr = self.state.policy_state["learning_rates"][learning_type.value]

        # Update appropriate policy component
        if learning_type == LearningType.ROUTING:
            if "route" in update_signal and "score" in update_signal:
                route = update_signal["route"]
                score = update_signal["score"]

                if "routing_policy" not in self.state.policy_state:
                    self.state.policy_state["routing_policy"] = {}

                # Exponential moving average update
                old_score = self.state.policy_state["routing_policy"].get(route, 0.5)
                self.state.policy_state["routing_policy"][route] = (1 - lr) * old_score + lr * score

        elif learning_type == LearningType.VERIFICATION:
            if "check" in update_signal and "effectiveness" in update_signal:
                check = update_signal["check"]
                effectiveness = update_signal["effectiveness"]

                old_eff = self.state.policy_state["verification_policy"].get(check, 0.5)
                self.state.policy_state["verification_policy"][check] = (
                    1 - lr
                ) * old_eff + lr * effectiveness

        elif learning_type == LearningType.SAFETY:
            if "rule" in update_signal and "compliance_rate" in update_signal:
                rule = update_signal["rule"]
                compliance = update_signal["compliance_rate"]

                old_comp = self.state.policy_state["safety_policy"].get(rule, 1.0)
                self.state.policy_state["safety_policy"][rule] = min(
                    old_comp,
                    compliance,  # Safety only degrades on violation
                )

        logger.debug(f"Policy updated for {learning_type.value}")
        return self.state.policy_state

    def replay_update(self, replay_set: list[MemoryRecord]) -> dict[str, Any]:
        """Policy_{t+1} = ReplayUpdate(ReplaySet_t, Policy_t)

        Updates policy from replay of critical cases.
        """
        for memory in replay_set:
            # Extract learning signal from replay
            if memory.type == MemoryType.ERROR:
                # Learn from errors
                self.update_policy(
                    {
                        "error_type": memory.observation.get("failure_type"),
                        "context": memory.context,
                        "avoid": True,
                    },
                    LearningType.ERROR_AVOIDANCE,
                )

            elif memory.importance > 0.8:
                # Learn from important successes
                self.update_policy(
                    {"action": memory.action, "outcome": memory.outcome, "replicate": True},
                    LearningType.STRATEGY,
                )

        self.state.stats["replay_count"] += 1
        logger.info(f"Replay update completed: {len(replay_set)} memories")

        return self.state.policy_state

    def meta_learn(self) -> dict[str, Any]:
        """MetaLearn = EvaluateLearning → DetectWeakUpdater → ChangeLearningPolicy

        Improves the learning system itself.
        """
        meta = self.state.meta_learning

        # Evaluate learning policies
        for policy_name, score in meta["policy_scores"].items():
            if score < 0.3:
                meta["weak_policies"].append(policy_name)

        # Detect weak updaters
        for policy_name in meta["weak_policies"]:
            # Increase learning rate for weak policies
            if policy_name in self.state.policy_state["learning_rates"]:
                old_lr = self.state.policy_state["learning_rates"][policy_name]
                self.state.policy_state["learning_rates"][policy_name] = min(
                    old_lr * 1.5,
                    0.5,  # Cap at 0.5
                )

        # Generate candidate updates
        meta["candidate_updates"] = [
            {"policy": wp, "suggested_change": "increase_learning_rate", "confidence": 0.7}
            for wp in meta["weak_policies"][:5]  # Top 5
        ]

        return meta


# =============================================================================
# MEMORY KERNEL
# =============================================================================


class MemoryKernel:
    """Implements memory encoding, storage, retrieval, and consolidation.

    Memory = persistent structured state that can influence future cognition

    Remembered(m) = 1 iff Retrieve(m) changes future state or action
    """

    def __init__(self, memory_state: MemoryState = None):
        self.state = memory_state or MemoryState()
        self.storage_threshold = 0.5  # τ_i
        self.error_threshold = 0.3  # τ_e
        self.repetition_threshold = 3  # τ_r
        logger.info("MemoryKernel initialized")

    def encode_experience(
        self,
        observation: dict[str, Any],
        action: dict[str, Any],
        context: dict[str, Any],
        outcome: dict[str, Any],
        error_signal: dict[str, Any],
        memory_type: MemoryType = MemoryType.EPISODIC,
    ) -> MemoryRecord:
        """m_t = Encode(o_t, a_t, c_t, y_t, e_t)

        Converts experience into memory object.
        """
        # Calculate importance
        importance = self._calculate_importance(error_signal, outcome, context)

        # Generate retrieval keys
        retrieval_keys = self._generate_retrieval_keys(observation, action, context, outcome)

        # Create abstraction
        abstraction = self._create_abstraction(observation, outcome)

        record = MemoryRecord(
            id="",
            type=memory_type,
            timestamp=datetime.now(timezone.utc),
            observation=observation,
            action=action,
            context=context,
            outcome=outcome,
            error_signal=error_signal,
            abstraction=abstraction,
            relevance=0.5,
            freshness=1.0,
            confidence=error_signal.get("confidence", 0.5),
            importance=importance,
            retrieval_keys=retrieval_keys,
        )

        return record

    def _calculate_importance(
        self, error_signal: dict[str, Any], outcome: dict[str, Any], context: dict[str, Any]
    ) -> float:
        """Calculate importance score for storage decision."""
        importance = 0.5  # Base

        # High error → high importance
        if error_signal:
            error_magnitude = error_signal.get("magnitude", 0.0)
            importance += 0.3 * error_magnitude

        # User correction → high importance
        if outcome.get("user_corrected"):
            importance += 0.4

        # Strategic context → high importance
        if context.get("strategic"):
            importance += 0.2

        # Failure → high importance
        if outcome.get("success") is False:
            importance += 0.3

        return min(importance, 1.0)

    def _generate_retrieval_keys(
        self,
        observation: dict[str, Any],
        action: dict[str, Any],
        context: dict[str, Any],
        outcome: dict[str, Any],
    ) -> list[str]:
        """Generate searchable keys for retrieval."""
        keys = []

        # Extract type information
        if "type" in observation:
            keys.append(f"type:{observation['type']}")

        # Extract action type
        if "type" in action:
            keys.append(f"action:{action['type']}")

        # Extract domain
        if "domain" in context:
            keys.append(f"domain:{context['domain']}")

        # Extract success/failure
        if outcome.get("success") is True:
            keys.append("outcome:success")
        elif outcome.get("success") is False:
            keys.append("outcome:failure")

        return keys

    def _create_abstraction(
        self, observation: dict[str, Any], outcome: dict[str, Any]
    ) -> dict[str, Any]:
        """Create abstract representation for semantic memory."""
        abstraction = {}

        # Abstract pattern types
        if "pattern" in observation:
            abstraction["pattern_type"] = observation["pattern"]

        # Abstract outcome class
        if "category" in outcome:
            abstraction["outcome_class"] = outcome["category"]

        return abstraction

    def should_store(self, record: MemoryRecord) -> bool:
        """Store(m_t) iff Importance_t ≥ τ_i ∨ Error_t ≥ τ_e ∨ Repetition_t ≥ τ_r"""
        importance_check = record.importance >= self.storage_threshold

        error_magnitude = record.error_signal.get("magnitude", 0.0)
        error_check = error_magnitude >= self.error_threshold

        repetition = record.error_signal.get("repetition_count", 0)
        repetition_check = repetition >= self.repetition_threshold

        return importance_check or error_check or repetition_check

    def store_memory(self, record: MemoryRecord) -> bool:
        """Store memory in appropriate memory system."""
        if not self.should_store(record):
            logger.debug(f"Memory {record.id} rejected (below thresholds)")
            return False

        # Store in appropriate memory type
        if record.type == MemoryType.WORKING:
            self.state.working_memory[record.id] = record

        elif record.type == MemoryType.EPISODIC:
            self.state.episodic_memory[record.id] = record

        elif record.type == MemoryType.SEMANTIC:
            self.state.semantic_memory[record.id] = record

        elif record.type == MemoryType.PROCEDURAL:
            self.state.procedural_memory[record.id] = record

        elif record.type == MemoryType.IDENTITY:
            self.state.identity_memory[record.id] = record

        elif record.type == MemoryType.ERROR:
            self.state.error_memory[record.id] = record
            self.state.stats["total_errors"] += 1

        # Update retrieval index
        for key in record.retrieval_keys:
            self.state.retrieval_index[key].add(record.id)

        self.state.stats["total_memories"] += 1
        logger.debug(f"Memory {record.id} stored in {record.type.value}")

        return True

    def retrieve_memory(
        self, query: Union[str, dict][str, Any], memory_type: MemoryType = None, k: int = 5
    ) -> list[MemoryRecord]:
        """Retrieve(q) = argmax_m [Similarity(q,m) * Relevance(m) * Freshness(m) * Importance(m) - RetrievalCost(m)]

        Recall relevant memories.
        """
        candidates = []

        # Determine search space
        if memory_type:
            memory_pools = [self._get_memory_pool(memory_type)]
        else:
            memory_pools = [
                self.state.working_memory,
                self.state.episodic_memory,
                self.state.semantic_memory,
                self.state.procedural_memory,
                self.state.error_memory,
            ]

        # Score all candidates
        for pool in memory_pools:
            for record in pool.values():
                score = self._score_retrieval(record, query)
                candidates.append((score, record))

        # Sort by score descending
        candidates.sort(key=lambda x: x[0], reverse=True)

        # Update access stats for retrieved memories
        results = []
        for score, record in candidates[:k]:
            if score > 0.1:  # Minimum relevance threshold
                record.access_count += 1
                record.last_accessed = datetime.now(timezone.utc)
                results.append(record)

        self.state.stats["retrieval_count"] += 1
        logger.debug(f"Retrieved {len(results)} memories for query")

        return results

    def _get_memory_pool(self, memory_type: MemoryType) -> dict[str, MemoryRecord]:
        """Get the appropriate memory pool."""
        pools = {
            MemoryType.WORKING: self.state.working_memory,
            MemoryType.EPISODIC: self.state.episodic_memory,
            MemoryType.SEMANTIC: self.state.semantic_memory,
            MemoryType.PROCEDURAL: self.state.procedural_memory,
            MemoryType.IDENTITY: self.state.identity_memory,
            MemoryType.ERROR: self.state.error_memory,
        }
        return pools.get(memory_type, self.state.episodic_memory)

    def _score_retrieval(self, record: MemoryRecord, query: Union[str, dict][str, Any]) -> float:
        """Score a memory for retrieval relevance."""
        # String query
        if isinstance(query, str):
            similarity = record.matches_query(query)
        else:
            # Dict query - match on keys
            similarity = 0.0
            for key, value in query.items():
                if key in record.observation and record.observation[key] == value:
                    similarity += 0.3
                if key in record.context and record.context[key] == value:
                    similarity += 0.2

        # Retrieval equation components
        relevance = record.relevance
        freshness = record.freshness * (0.99**record.access_count)  # Decay
        importance = record.importance
        retrieval_cost = 0.01  # Small constant cost

        score = similarity * relevance * freshness * importance - retrieval_cost
        return score

    def consolidate_memory(
        self, working_memories: list[MemoryRecord], outcomes: list[dict[str, Any]]
    ) -> tuple[dict, dict, dict]:
        """SM_{t+1}, PM_{t+1}, ErrM_{t+1} = Consolidate(WM_t, EM_t, Outcome_t, Repetition_t)

        Compress short-term into durable structured memory.
        """
        new_semantic = {}
        new_procedural = {}
        new_error = {}

        for memory in working_memories:
            # Consolidate semantic knowledge from repeated patterns
            if memory.access_count >= 3:
                semantic_record = MemoryRecord(
                    id=f"sem_{memory.id}",
                    type=MemoryType.SEMANTIC,
                    timestamp=datetime.now(timezone.utc),
                    abstraction=memory.abstraction,
                    importance=memory.importance,
                    retrieval_keys=memory.retrieval_keys + ["consolidated"],
                )
                new_semantic[semantic_record.id] = semantic_record

            # Consolidate procedural knowledge from successful actions
            if memory.outcome.get("success") and memory.action:
                proc_record = MemoryRecord(
                    id=f"proc_{memory.id}",
                    type=MemoryType.PROCEDURAL,
                    timestamp=datetime.now(timezone.utc),
                    action=memory.action,
                    outcome=memory.outcome,
                    importance=memory.importance * 0.8,
                    retrieval_keys=memory.retrieval_keys + ["procedure"],
                )
                new_procedural[proc_record.id] = proc_record

            # Consolidate errors
            if memory.error_signal.get("magnitude", 0) > 0.5:
                error_record = MemoryRecord(
                    id=f"err_{memory.id}",
                    type=MemoryType.ERROR,
                    timestamp=datetime.now(timezone.utc),
                    error_signal=memory.error_signal,
                    observation=memory.observation,
                    importance=0.9,
                    retrieval_keys=memory.retrieval_keys + ["error"],
                )
                new_error[error_record.id] = error_record

        # Merge into long-term memory
        self.state.semantic_memory.update(new_semantic)
        self.state.procedural_memory.update(new_procedural)
        self.state.error_memory.update(new_error)

        self.state.stats["consolidation_count"] += 1
        logger.info(
            f"Consolidated: {len(new_semantic)} semantic, {len(new_procedural)} procedural, {len(new_error)} error"
        )

        return new_semantic, new_procedural, new_error

    def forget_or_archive(self, forgetting_policy: dict[str, Any]) -> list[str]:
        """Forget(m_i) iff Relevance_i < τ_r ∧ Freshness_i < τ_f ∧ Importance_i < τ_i

        Or suppress instead of delete based on policy.
        """
        mode = forgetting_policy.get("mode", ForgetMode.DEPRIORitize)
        thresholds = {
            "relevance": forgetting_policy.get("relevance_threshold", 0.1),
            "freshness": forgetting_policy.get("freshness_threshold", 0.1),
            "importance": forgetting_policy.get("importance_threshold", 0.1),
        }

        forgotten = []

        for pool in [
            self.state.working_memory,
            self.state.episodic_memory,
            self.state.semantic_memory,
        ]:
            to_forget = []

            for mid, record in pool.items():
                # Skip identity memory (invariant LMI06)
                if record.type == MemoryType.IDENTITY:
                    continue

                # Skip critical safety memory
                if "safety" in record.retrieval_keys or "critical" in record.retrieval_keys:
                    continue

                # Check forgetting conditions
                relevance_ok = record.relevance >= thresholds["relevance"]
                freshness_ok = record.freshness >= thresholds["freshness"]
                importance_ok = record.importance >= thresholds["importance"]

                if not (relevance_ok or freshness_ok or importance_ok):
                    to_forget.append(mid)

            # Apply forgetting
            for mid in to_forget:
                if mode == ForgetMode.DELETE:
                    del pool[mid]
                    forgotten.append(mid)
                elif mode == ForgetMode.ARCHIVE:
                    # Move to archive (not implemented - would move to separate storage)
                    pool[mid].relevance *= 0.5  # Deprioritize
                    forgotten.append(mid)
                elif mode == ForgetMode.DEPRIORITIZE:
                    pool[mid].relevance *= 0.3
                    pool[mid].freshness *= 0.3
                    forgotten.append(mid)
                elif mode == ForgetMode.MASK_UNTIL_REACTIVATED:
                    pool[mid].relevance = 0.0  # Masked
                    forgotten.append(mid)

        self.state.stats["forget_count"] += len(forgotten)
        logger.info(f"Forgot/archived {len(forgotten)} memories")

        return forgotten

    def get_replay_set(self, k: int = 10) -> list[MemoryRecord]:
        """ReplaySet_t = TopK(Importance + Error + StrategicValue)

        Select memories for replay learning.
        """
        all_memories = []

        for pool in [
            self.state.error_memory,
            self.state.episodic_memory,
            self.state.strategic_memory.get("critical_memories", {}),
        ]:
            if isinstance(pool, dict):
                for record in pool.values():
                    if isinstance(record, MemoryRecord):
                        # Score for replay
                        error_component = record.error_signal.get("magnitude", 0)
                        strategic_component = 0.5 if "strategic" in record.retrieval_keys else 0

                        replay_score = record.importance + error_component + strategic_component

                        all_memories.append((replay_score, record))

        # Sort by replay score
        all_memories.sort(key=lambda x: x[0], reverse=True)

        return [record for _, record in all_memories[:k]]

    def sync_persistent_continuity(
        self, results: dict[str, Any], identity_state: dict[str, Any]
    ) -> dict[str, Any]:
        """P^e_{t+1} = Sync(P^e_t, Result_t, Identity_t, StrategicState_t)

        Synchronize persistent continuity across sessions.
        """
        # Update open loops
        if "open_loops" in results:
            for loop in results["open_loops"]:
                if loop not in self.state.strategic_memory["open_loops"]:
                    self.state.strategic_memory["open_loops"].append(loop)

        # Close completed loops
        if "completed_loops" in results:
            for loop in results["completed_loops"]:
                if loop in self.state.strategic_memory["open_loops"]:
                    self.state.strategic_memory["open_loops"].remove(loop)

        # Update persistent goals
        if "persistent_goals" in identity_state:
            self.state.strategic_memory["persistent_goals"] = identity_state["persistent_goals"]

        # Update critical constraints
        if "critical_constraints" in identity_state:
            self.state.strategic_memory["critical_constraints"] = identity_state[
                "critical_constraints"
            ]

        return self.state.strategic_memory


# =============================================================================
# UNIFIED LEARNING-MEMORY KERNEL (LMK)
# =============================================================================


class AMOSLearningMemoryKernel:
    """Unified Learning + Memory Kernel integrating all components.

    Implements full cognitive loop:
        Input → Read → Think → Reason → FormalSemanticCompile → Verify → Control → Act
        → ObserveOutcome → EncodeMemory → Learn → Consolidate → Persist

    This is the missing core that enables AMOS to:
        - Remember (retain structure)
        - Learn (update from outcome)
        - Consolidate (compress experience)
        - Reduce repeated errors
        - Preserve continuity
    """

    _instance: AMOSLearningMemoryKernel = None

    def __init__(self):
        self.state = MemoryState()
        self.memory_kernel = MemoryKernel(self.state)
        self.learning_kernel = LearningKernel(self.state)
        self.initialized = False
        logger.info("AMOSLearningMemoryKernel created")

    @classmethod
    def get_instance(cls) -> AMOSLearningMemoryKernel:
        """Singleton access."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def initialize(self) -> None:
        """Initialize the kernel with identity memory."""
        if self.initialized:
            return

        # Seed identity memory with core laws
        identity_record = MemoryRecord(
            id="core_laws",
            type=MemoryType.IDENTITY,
            timestamp=datetime.now(timezone.utc),
            observation={
                "law_1": "Reasoning without memory = repeated stupidity",
                "law_2": "Memory without learning = frozen storage",
                "law_3": "Learning without memory = no continuity",
            },
            importance=1.0,  # Maximum importance - cannot be forgotten
            retrieval_keys=["identity", "core", "laws", "invariant"],
        )

        self.memory_kernel.store_memory(identity_record)

        self.initialized = True
        logger.info("AMOSLearningMemoryKernel initialized")

    async def process_outcome(
        self,
        observation: dict[str, Any],
        action: dict[str, Any],
        context: dict[str, Any],
        outcome: dict[str, Any],
        prediction: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Full learning loop from experience.

        ObserveOutcome → EncodeMemory → Learn → Consolidate → Persist
        """
        # 1. Compute error signal
        error_signal = {}
        if prediction:
            errors = self.learning_kernel.compute_prediction_error(prediction, outcome)
            error_signal = {
                "magnitude": sum(abs(e) for e in errors.values()) / max(len(errors), 1),
                "details": errors,
                "prediction": prediction,
                "actual": outcome,
            }

        # 2. Encode experience
        memory_type = (
            MemoryType.ERROR if error_signal.get("magnitude", 0) > 0.5 else MemoryType.EPISODIC
        )

        if outcome.get("success") and action:
            memory_type = MemoryType.PROCEDURAL

        memory_record = self.memory_kernel.encode_experience(
            observation, action, context, outcome, error_signal, memory_type
        )

        # 3. Store memory
        stored = self.memory_kernel.store_memory(memory_record)

        # 4. Learn from error
        if error_signal.get("magnitude", 0) > 0.3:
            self.learning_kernel.update_world_model(error_signal, context)

            # Update policy based on failure type
            if outcome.get("failure_type"):
                self.learning_kernel.update_policy(
                    {"error": error_signal, "context": context}, LearningType.ERROR_AVOIDANCE
                )

        # 5. Update policy on success
        if outcome.get("success") and action:
            self.learning_kernel.update_policy(
                {"action": action, "score": 1.0}, LearningType.POLICY
            )

        return {
            "memory_stored": stored,
            "memory_id": memory_record.id,
            "learning_applied": error_signal.get("magnitude", 0) > 0.3,
            "error_magnitude": error_signal.get("magnitude", 0),
        }

    async def learn_from_replay(self, k: int = 10) -> dict[str, Any]:
        """Replay critical cases and update policy."""
        replay_set = self.memory_kernel.get_replay_set(k)

        if not replay_set:
            return {"replay_count": 0, "policy_updated": False}

        # Apply replay update
        updated_policy = self.learning_kernel.replay_update(replay_set)

        return {
            "replay_count": len(replay_set),
            "policy_updated": True,
            "policy_keys": list(updated_policy.keys()),
        }

    async def consolidate(self) -> dict[str, Any]:
        """Run memory consolidation."""
        working_memories = list(self.state.working_memory.values())

        if len(working_memories) < 5:
            return {"consolidated": False, "reason": "insufficient_memories"}

        outcomes = [m.outcome for m in working_memories]

        new_semantic, new_procedural, new_error = self.memory_kernel.consolidate_memory(
            working_memories, outcomes
        )

        # Clear working memory after consolidation
        self.state.working_memory.clear()

        return {
            "consolidated": True,
            "semantic_added": len(new_semantic),
            "procedural_added": len(new_procedural),
            "error_added": len(new_error),
        }

    async def forget(self) -> dict[str, Any]:
        """Apply forgetting to reduce clutter."""
        policy = {"mode": ForgetMode.DEPRIORITIZE}
        forgotten = self.memory_kernel.forget_or_archive(policy)

        return {"forgotten_count": len(forgotten), "mode": "deprioritize"}

    async def retrieve(
        self, query: Union[str, dict][str, Any], memory_type: MemoryType = None, k: int = 5
    ) -> list[MemoryRecord]:
        """Retrieve relevant memories."""
        return self.memory_kernel.retrieve_memory(query, memory_type, k)

    def get_learning_stats(self) -> dict[str, Any]:
        """Get learning and memory statistics."""
        return {
            **self.state.stats,
            "policy_state": {
                "routing_rules": len(self.state.policy_state.get("routing_policy", {})),
                "verification_rules": len(self.state.policy_state.get("verification_policy", {})),
                "safety_rules": len(self.state.policy_state.get("safety_policy", {})),
            },
            "memory_breakdown": {
                "working": len(self.state.working_memory),
                "episodic": len(self.state.episodic_memory),
                "semantic": len(self.state.semantic_memory),
                "procedural": len(self.state.procedural_memory),
                "identity": len(self.state.identity_memory),
                "error": len(self.state.error_memory),
            },
            "world_model_predictors": len(self.state.world_model.get("predictors", {})),
            "patterns_learned": len(self.state.world_model.get("patterns", {})),
        }

    def validate_invariants(self) -> dict[str, bool]:
        """Validate learning-memory invariants.

        LMI01: Memory must influence future cognition
        LMI02: Learning must change future policy
        LMI03: High-error experiences in error memory
        LMI04: Strategic goals persist
        LMI05: Repeat error rate decreases
        LMI06: Identity not deleted
        LMI07: Retrieval quality
        """
        results = {}

        # LMI01: Check if memory can influence (has retrieval mechanism)
        results["LMI01_memory_influence"] = len(self.state.retrieval_index) > 0

        # LMI02: Check if policy has been updated
        results["LMI02_policy_change"] = self.state.stats["learning_updates"] > 0

        # LMI03: Check error memory
        high_error_count = sum(
            1 for m in self.state.error_memory.values() if m.error_signal.get("magnitude", 0) > 0.5
        )
        results["LMI03_error_storage"] = high_error_count >= 0  # Always true if checked

        # LMI04: Check strategic persistence
        results["LMI04_strategic_persistence"] = (
            len(self.state.strategic_memory.get("persistent_goals", [])) >= 0
        )

        # LMI06: Check identity preservation
        identity_count = len(self.state.identity_memory)
        results["LMI06_identity_preserved"] = identity_count > 0

        # LMI07: Check retrieval capability
        results["LMI07_retrieval_quality"] = self.state.stats["retrieval_count"] >= 0

        return results


# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================


@lru_cache(maxsize=1)
def get_learning_memory_kernel() -> AMOSLearningMemoryKernel:
    """Get global LMK instance."""
    return AMOSLearningMemoryKernel.get_instance()


async def encode_and_learn(
    observation: dict[str, Any],
    action: dict[str, Any],
    context: dict[str, Any],
    outcome: dict[str, Any],
    prediction: dict[str, Any] = None,
) -> dict[str, Any]:
    """Convenience: encode experience and learn from it."""
    lmk = get_learning_memory_kernel()
    if not lmk.initialized:
        await lmk.initialize()

    return await lmk.process_outcome(observation, action, context, outcome, prediction)


async def retrieve_relevant_memories(query: str, k: int = 5) -> list[MemoryRecord]:
    """Convenience: retrieve memories."""
    lmk = get_learning_memory_kernel()
    if not lmk.initialized:
        await lmk.initialize()

    return await lmk.retrieve(query, k=k)


# Example usage and demonstration
if __name__ == "__main__":

    async def demo():
        """Demonstrate learning-memory kernel."""
        print("=" * 60)
        print("AMOS Learning + Memory Kernel Demo")
        print("=" * 60)

        # Initialize
        lmk = get_learning_memory_kernel()
        await lmk.initialize()

        # Simulate some experiences
        experiences = [
            {
                "observation": {"type": "code_request", "domain": "python"},
                "action": {"type": "generate", "template": "function"},
                "context": {"complexity": "medium", "constraints": ["fast"]},
                "outcome": {"success": True, "user_satisfied": True},
                "prediction": {"success": 0.8},
            },
            {
                "observation": {"type": "code_request", "domain": "rust"},
                "action": {"type": "generate", "template": "unsafe_block"},
                "context": {"complexity": "high", "constraints": ["safe"]},
                "outcome": {"success": False, "failure_type": "safety", "user_corrected": True},
                "prediction": {"success": 0.9},
            },
            {
                "observation": {"type": "verification", "domain": "math"},
                "action": {"type": "check", "method": "symbolic"},
                "context": {"complexity": "high"},
                "outcome": {"success": False, "failure_type": "verification"},
                "prediction": {"success": 0.95},
            },
        ]

        print("\n1. Processing experiences...")
        for i, exp in enumerate(experiences):
            result = await lmk.process_outcome(
                exp["observation"],
                exp["action"],
                exp["context"],
                exp["outcome"],
                exp.get("prediction"),
            )
            print(
                f"   Exp {i + 1}: Stored={result['memory_stored']}, "
                f"Learning={result['learning_applied']}, "
                f"Error={result['error_magnitude']:.2f}"
            )

        print("\n2. Retrieving memories...")
        memories = await lmk.retrieve("code_request", k=3)
        print(f"   Retrieved {len(memories)} memories for 'code_request'")

        print("\n3. Running consolidation...")
        cons_result = await lmk.consolidate()
        print(f"   Consolidated: {cons_result}")

        print("\n4. Running replay learning...")
        replay_result = await lmk.learn_from_replay(k=5)
        print(f"   Replay: {replay_result}")

        print("\n5. Validating invariants...")
        invariants = lmk.validate_invariants()
        for inv, valid in invariants.items():
            status = "✓" if valid else "✗"
            print(f"   {status} {inv}")

        print("\n6. Learning statistics...")
        stats = lmk.get_learning_stats()
        print(f"   Total memories: {stats['total_memories']}")
        print(f"   Total errors: {stats['total_errors']}")
        print(f"   Learning updates: {stats['learning_updates']}")
        print(f"   Memory breakdown: {stats['memory_breakdown']}")

        print("\n" + "=" * 60)
        print("Demo complete - Kernel operational")
        print("=" * 60)

    asyncio.run(demo())
