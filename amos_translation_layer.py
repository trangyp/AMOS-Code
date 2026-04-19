from typing import Any, Dict, List, Optional, Tuple

"""
AMOS Translation Layer - Human-to-Machine Semantic Alignment Kernel

Core Law (CORRECTED):
    HumanLanguage → Parse → SignalNoiseSeparation → SemanticCompile → IntentVerify → MachineGoal

Invariant:
    NaturalLanguage ↛ ActionDirectly
    NaturalLanguage → SignalNoiseSeparation → FilteredSemanticInput → VerifiedIntent → Action

Signal-Noise Law:
    Utterance decomposition: U_t = Sig_t + Noi_t + Amb_t
    Where:
        Sig_t = structurally relevant meaning
        Noi_t = distortion, defense, overload, filler, narrative residue
        Amb_t = unresolved ambiguity

Bug Prevention:
    - Signal-noise separation BEFORE semantic compilation
    - Ambiguity representation (not ignoring)
    - Speech act tracking
    - Human state estimation
    - Constraint preservation
    - Metaphor detection
    - Execution gating with signal-quality thresholds

Fixed Architecture:
    OLD: Language → Semantics → Intent
    NEW: Language → SignalNoiseSeparation → Semantics → Intent
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto

# Configure logging
logger = logging.getLogger(__name__)

# =============================================================================
# ENUMERATIONS
# =============================================================================


class SpeechActType(Enum):
    INFORM = "inform"
    ASK = "ask"
    REQUEST = "request"
    COMMAND = "command"
    REFLECT = "reflect"
    VENT = "vent"
    TEST_BOUNDARY = "test_boundary"
    SEEK_VALIDATION = "seek_validation"
    SEEK_STRUCTURE = "seek_structure"
    SEEK_ACTION = "seek_action"
    MIXED = "mixed"


class PropositionType(Enum):
    CLAIM = "claim"
    QUESTION = "question"
    GOAL = "goal"
    CONSTRAINT = "constraint"
    EMOTION_SIGNAL = "emotion_signal"
    IDENTITY_STATEMENT = "identity_statement"
    UNCERTAINTY = "uncertainty"
    METAPHOR = "metaphor"


class TimeReferenceType(Enum):
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"
    TIMELESS = "timeless"
    UNKNOWN = "unknown"


class Polarity(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class HumanStateClass(Enum):
    STABLE = "stable"
    ACTIVATED = "activated"
    OVERLOADED = "overloaded"
    SHUTDOWN = "shutdown"
    HIGH_RISK = "high_risk"


class IntentType(Enum):
    UNDERSTAND = "understand"
    DECIDE = "decide"
    ACT = "act"
    BE_SEEN = "be_seen"
    OFFLOAD = "offload"
    TEST = "test"
    REPAIR = "repair"
    ORGANIZE = "organize"
    REQUEST_EXECUTION = "request_execution"
    REQUEST_DESIGN = "request_design"
    REQUEST_TRANSLATION = "request_translation"


class AmbiguityType(Enum):
    REFERENCE = "reference"
    SCOPE = "scope"
    TIME = "time"
    GOAL = "goal"
    EMOTION = "emotion"
    INSTRUCTION = "instruction"
    IDENTITY = "identity"
    METAPHOR = "metaphor"


# =============================================================================
# SIGNAL-NOISE KERNEL ENUMERATIONS
# =============================================================================


class SignalClass(Enum):
    """Signal classes - what improves correct modeling."""

    EXPLICIT_GOAL = "explicit_goal"
    EXPLICIT_CONSTRAINT = "explicit_constraint"
    REAL_QUESTION = "real_question"
    DECISION_RELEVANT_FACT = "decision_relevant_fact"
    PERSISTENT_PATTERN = "persistent_pattern"
    STATE_RELEVANT_MARKER = "state_relevant_marker"
    RISK_MARKER = "risk_marker"
    RESOURCE_CONSTRAINT = "resource_constraint"
    TIME_CONSTRAINT = "time_constraint"
    REQUESTED_OUTPUT_FORMAT = "requested_output_format"
    TRUE_UNCERTAINTY = "true_uncertainty"
    STABLE_PREFERENCE = "stable_preference"


class NoiseClass(Enum):
    """Noise classes - what distorts correct modeling."""

    EGO_DEFENSE = "ego_defense"
    FEAR_PROJECTION = "fear_projection"
    AVOIDANCE_LANGUAGE = "avoidance_language"
    NARRATIVE_LOOP = "narrative_loop"
    IDENTITY_FUSION = "identity_fusion"
    PERFORMATIVE_INTENSITY = "performative_intensity"
    METAPHORIC_OVERCOMPRESSION = "metaphoric_overcompression"
    STATE_LEAKAGE = "state_leakage"
    PANIC_SCOPE_EXPANSION = "panic_scope_expansion"
    SELF_GLOBALIZATION = "self_globalization"
    CONSTRAINT_SMEARING = "constraint_smearing"
    SEMANTIC_FILLER = "semantic_filler"


class AmbiguityUnitType(Enum):
    """Types of ambiguity in utterance."""

    REFERENCE = "reference"
    SCOPE = "scope"
    TIME = "time"
    GOAL = "goal"
    INSTRUCTION = "instruction"
    IDENTITY = "identity"


class ConstraintType(Enum):
    HARD = "hard"
    SOFT = "soft"
    IMPLIED = "implied"


class OutputMode(Enum):
    EXPLANATION = "explanation"
    PLAN = "plan"
    DECISION_SUPPORT = "decision_support"
    EXECUTION_SPEC = "execution_spec"
    TRANSLATION = "translation"
    REFLECTION = "reflection"
    QUESTION_ANSWERING = "question_answering"
    OTHER = "other"


class OutputFormat(Enum):
    TEXT = "text"
    JSON = "json"
    TABLE = "table"
    STEPS = "steps"
    EQUATIONS = "equations"
    SCHEMA = "schema"
    MIXED = "mixed"


class Verbosity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TranslationState(Enum):
    RAW_INPUT = auto()
    PARSED = auto()
    SIGNAL_NOISE_INFERRED = auto()  # NEW: Signal-noise separation
    SIGNAL_EXTRACTED = auto()  # NEW: Signal extraction complete
    NOISE_CLASSIFIED = auto()  # NEW: Noise classification complete
    SEMANTIC_HYPOTHESES = auto()
    RESOLVED = auto()
    GROUNDED = auto()
    STRUCTURED = auto()
    VERIFIED = auto()
    COMPILED = auto()
    EXECUTABLE = auto()
    CLARIFICATION_REQUIRED = auto()
    BLOCKED = auto()


class GoalType(Enum):
    RESPOND = "respond"
    ASK_CLARIFICATION = "ask_clarification"
    PLAN = "plan"
    SIMULATE = "simulate"
    EXECUTE = "execute"
    STORE = "store"
    DEFER = "defer"
    REFUSE = "refuse"


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class SpeechAct:
    """Speech act classification with confidence weight."""

    type: SpeechActType
    weight: float = 0.0


@dataclass
class Relation:
    """Semantic relation between entities."""

    source: str
    relation: str
    target: str


@dataclass
class TimeReference:
    """Temporal reference in utterance."""

    type: TimeReferenceType
    value: Optional[str] = None


@dataclass
class Modality:
    """Modal characteristics (certainty, necessity, possibility)."""

    certainty: float = 0.0
    necessity: float = 0.0
    possibility: float = 0.0


@dataclass
class SemanticUnit:
    """Atomic semantic unit extracted from utterance."""

    unit_id: str
    surface_text: str
    normalized_text: str
    proposition_type: PropositionType
    entities: List[str] = field(default_factory=list)
    relations: List[Relation] = field(default_factory=list)
    time_ref: Optional[TimeReference] = None
    modality: Modality = field(default_factory=Modality)
    polarity: Polarity = Polarity.UNKNOWN


@dataclass
class HumanStateEstimate:
    """Estimated human cognitive and emotional state."""

    cognitive_load: float = 0.0
    emotional_intensity: float = 0.0
    overload_risk: float = 0.0
    defensiveness: float = 0.0
    clarity: float = 0.0
    agency: float = 0.0
    state_class: HumanStateClass = HumanStateClass.STABLE


@dataclass
class IntentHypothesis:
    """Hypothesized intent behind utterance."""

    intent_id: str
    intent_type: IntentType
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)


@dataclass
class Ambiguity:
    """Detected ambiguity in utterance."""

    type: AmbiguityType
    location: str
    candidates: List[str] = field(default_factory=list)
    severity: float = 0.0


@dataclass
class Constraint:
    """Extracted constraint from utterance."""

    type: ConstraintType
    content: str
    confidence: float = 0.0


@dataclass
class RequestedOutput:
    """User-requested output characteristics."""

    mode: OutputMode = OutputMode.OTHER
    format: OutputFormat = OutputFormat.TEXT
    verbosity: Verbosity = Verbosity.MEDIUM


@dataclass
class SafetyFlags:
    """Safety assessment flags."""

    human_destabilization_risk: float = 0.0
    self_harm_risk: float = 0.0
    harm_to_others_risk: float = 0.0
    dependency_risk: float = 0.0
    requires_grounding: bool = True


# =============================================================================
# SIGNAL-NOISE KERNEL DATA CLASSES
# =============================================================================


@dataclass
class SignalUnit:
    """
    Signal unit - structurally relevant meaning extracted from utterance.

    Signal is whatever improves correct modeling.
    """

    unit_id: str
    text: str
    signal_class: SignalClass
    relevance_score: float = 0.0  # Structural relevance
    grounding_score: float = 0.0  # Grounding in context
    goal_fit_score: float = 0.0  # Fit with inferred goals
    confidence: float = 0.0  # Extraction confidence


@dataclass
class NoiseUnit:
    """
    Noise unit - distortion that may distort correct modeling.

    Noise is NOT discarded completely - some noise is diagnostically important.

    Rule: NotAllNoiseIsDiscarded; SomeNoiseIsRiskSignal
    """

    unit_id: str
    text: str
    noise_class: NoiseClass
    severity: float = 0.0  # Distortion severity
    distortion_risk: float = 0.0  # Risk of semantic distortion
    confidence: float = 0.0  # Classification confidence
    retain_as_state_signal: bool = False  # Some noise is diagnostically relevant
    state_signal_role: Optional[str] = None  # If retained: state|risk|defense indicator


@dataclass
class AmbiguityUnit:
    """Unresolved ambiguity in utterance."""

    unit_id: str
    ambiguity_type: AmbiguityUnitType
    severity: float = 0.0
    candidates: List[str] = field(default_factory=list)
    location: str = ""


@dataclass
class SignalNoiseSummary:
    """Summary of signal-noise analysis."""

    signal_score: float = (
        0.0  # Q_sig = α·StructuralRelevance + β·Grounding + γ·GoalFit + δ·ConstraintPreservation
    )
    noise_score: float = 0.0  # Q_noi = Σ noise severity metrics
    ambiguity_score: float = 0.0  # Overall ambiguity
    state_distortion_score: float = 0.0  # Risk of state-based misreading
    translation_ready: bool = False  # Gate: ready for semantic compilation?


@dataclass
class SignalNoiseRepresentation:
    """
    Canonical machine-readable signal-noise decomposition.

    U_t = Sig_t + Noi_t + Amb_t

    This representation MUST be computed BEFORE semantic compilation.
    """

    utterance_id: str
    raw_text: str
    signal_units: List[SignalUnit] = field(default_factory=list)
    noise_units: List[NoiseUnit] = field(default_factory=list)
    ambiguity_units: List[AmbiguityUnit] = field(default_factory=list)
    human_state_estimate: HumanStateEstimate = field(default_factory=HumanStateEstimate)
    summary: SignalNoiseSummary = field(default_factory=SignalNoiseSummary)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class FilteredSemanticInput:
    """
    Filtered semantic input - only signal dominates semantic compilation.

    Some noise is retained as state/risk/defense indicator.
    """

    primary_signal_units: List[SignalUnit] = field(default_factory=list)
    retained_noise_units: List[dict[str, Any]] = field(default_factory=list)  # With role annotation
    dropped_noise_units: List[str] = field(default_factory=list)
    ambiguity_units: List[AmbiguityUnit] = field(default_factory=list)
    effective_constraints: List[Constraint] = field(default_factory=list)


@dataclass
class CompiledMachineGoal:
    """Final machine-compiled goal."""

    goal_type: GoalType = GoalType.RESPOND
    objective: str = ""
    inputs_required: List[str] = field(default_factory=list)
    constraints_required: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    execution_allowed: bool = False


@dataclass
class SemanticIntentRepresentation:
    """
    Canonical machine-readable intermediate representation.

    Every human utterance compiles into this structure before
    any machine action is taken.
    """

    utterance_id: str
    raw_text: str
    language: str
    speech_acts: List[SpeechAct] = field(default_factory=list)
    semantic_units: List[SemanticUnit] = field(default_factory=list)
    human_state_estimate: HumanStateEstimate = field(default_factory=HumanStateEstimate)
    intent_hypotheses: List[IntentHypothesis] = field(default_factory=list)
    ambiguities: List[Ambiguity] = field(default_factory=list)
    constraints: List[Constraint] = field(default_factory=list)
    requested_output: RequestedOutput = field(default_factory=RequestedOutput)
    safety_flags: SafetyFlags = field(default_factory=SafetyFlags)
    semantic_confidence: float = 0.0
    requires_clarification: bool = False
    clarification_targets: List[str] = field(default_factory=list)
    compiled_machine_goal: CompiledMachineGoal = field(default_factory=CompiledMachineGoal)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# PARSE OUTPUT
# =============================================================================


@dataclass
class Dependency:
    """Syntactic dependency."""

    head: str
    relation: str
    dependent: str


@dataclass
class ParsedUtterance:
    """Output of Parse(U_t) → P_t"""

    tokens: List[str] = field(default_factory=list)
    clauses: List[str] = field(default_factory=list)
    dependencies: List[Dependency] = field(default_factory=list)
    named_entities: List[str] = field(default_factory=list)
    coreference_candidates: List[str] = field(default_factory=list)


# =============================================================================
# SEMANTIC HYPOTHESES
# =============================================================================


@dataclass
class SemanticHypotheses:
    """Output of Sense(P_t) → S_t"""

    candidates: List[SemanticUnit] = field(default_factory=list)
    confidence_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class ResolvedSemantics:
    """Output of Resolve(S_t) → R_t"""

    units: List[SemanticUnit] = field(default_factory=list)
    resolved_ambiguities: List[Ambiguity] = field(default_factory=list)
    remaining_ambiguities: List[Ambiguity] = field(default_factory=list)
    constraints: List[Constraint] = field(default_factory=list)


@dataclass
class GroundedSemantics:
    """Output of Ground(R_t) → G_t"""

    units: List[SemanticUnit] = field(default_factory=list)
    grounded_entities: Dict[str, Any] = field(default_factory=dict)
    temporal_context: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# INTENT GRAPH
# =============================================================================


@dataclass
class IntentNode:
    """Node in intent graph."""

    id: str
    type: str  # goal|constraint|entity|state|action|risk|ambiguity|question


@dataclass
class IntentEdge:
    """Edge in intent graph."""

    source: str
    type: str  # depends_on|blocks|targets|modifies|asks_about|conflicts_with
    target: str


@dataclass
class IntentGraph:
    """Output of Structure(G_t) → IGraph_t"""

    nodes: List[IntentNode] = field(default_factory=list)
    edges: List[IntentEdge] = field(default_factory=list)


# =============================================================================
# VERIFICATION OUTPUT
# =============================================================================


@dataclass
class SemanticVerification:
    """Output of Verify(IGraph_t) → V_t"""

    is_executable: bool = False
    is_contradictory: bool = False
    missing_slots: List[str] = field(default_factory=list)
    ambiguity_score: float = 0.0
    semantic_confidence: float = 0.0
    requires_clarification: bool = False
    clarification_questions: List[str] = field(default_factory=list)


# =============================================================================
# TRANSLATION BUG CLASSES
# =============================================================================

TRANSLATION_BUG_CLASSES = {
    "TB01": {
        "name": "surface_literalism",
        "definition": "machine overfits to literal wording and misses pragmatic meaning",
    },
    "TB02": {
        "name": "reference_failure",
        "definition": "pronouns, implied entities, or omitted referents unresolved",
    },
    "TB03": {
        "name": "speech_act_misclassification",
        "definition": "venting interpreted as request, or request interpreted as reflection",
    },
    "TB04": {
        "name": "state_blindness",
        "definition": "semantic interpretation ignores human cognitive and nervous-system state",
    },
    "TB05": {
        "name": "constraint_drop",
        "definition": "hard or implied user constraints lost during translation",
    },
    "TB06": {
        "name": "metaphor_collapse",
        "definition": "metaphorical language treated as literal instruction or fact",
    },
    "TB07": {
        "name": "scope_error",
        "definition": "machine assigns wrong scope to action, time, entity, or goal",
    },
    "TB08": {
        "name": "identity_overread",
        "definition": "temporary state is translated into stable identity claim",
    },
    "TB09": {
        "name": "premature_execution",
        "definition": "machine acts before semantic verification is complete",
    },
}

# =============================================================================
# TRANSLATION GUARD RULES
# =============================================================================

TRANSLATION_GUARDS = [
    {"id": "TG01", "rule": "never execute from raw natural language"},
    {"id": "TG02", "rule": "represent ambiguity explicitly when present"},
    {"id": "TG03", "rule": "track speech act separately from proposition content"},
    {"id": "TG04", "rule": "track human state separately from semantic content"},
    {"id": "TG05", "rule": "preserve hard and implied constraints"},
    {"id": "TG06", "rule": "require clarification when missing slots exceed threshold"},
    {"id": "TG07", "rule": "lower execution rights when semantic confidence is low"},
    {
        "id": "TG08",
        "rule": "treat metaphor and emotional compression as non-literal until grounded",
    },
]

# =============================================================================
# SIGNAL-NOISE KERNEL INVARIANTS
# =============================================================================

SIGNAL_NOISE_INVARIANTS = [
    {"id": "SNI01", "rule": "semantic compilation must be signal-dominant"},
    {"id": "SNI02", "rule": "noise may not override explicit constraints"},
    {"id": "SNI03", "rule": "diagnostic noise must be retained as state signal"},
    {"id": "SNI04", "rule": "high ambiguity blocks execution"},
    {"id": "SNI05", "rule": "high noise lowers confidence even when syntax is clear"},
]

# =============================================================================
# SIGNAL-NOISE KERNEL EQUATIONS
# =============================================================================

# Q_sig = α·StructuralRelevance + β·Grounding + γ·GoalFit + δ·ConstraintPreservation
SIGNAL_QUALITY_WEIGHTS = {
    "structural_relevance": 0.30,
    "grounding": 0.25,
    "goal_fit": 0.25,
    "constraint_preservation": 0.20,
}

# Q_noi = α·Defense + β·Looping + γ·Reactivity + δ·MetaphorLoad + ε·Ambiguity + ζ·Overload
NOISE_QUALITY_WEIGHTS = {
    "defense": 0.20,
    "looping": 0.15,
    "reactivity": 0.15,
    "metaphor_load": 0.20,
    "ambiguity": 0.15,
    "overload": 0.15,
}

# Execution safety gate thresholds
SIGNAL_QUALITY_THRESHOLD: float = 0.70
NOISE_QUALITY_THRESHOLD: float = 0.40
AMBIGUITY_THRESHOLD_SIGNAL: float = 0.25

# =============================================================================
# TRANSLATION LAYER CORE
# =============================================================================


class AMOSTranslationLayer:
    """
    Human-to-Machine Semantic Alignment Kernel.

    Implements the CORRECTED translation pipeline:
    Parse → SignalNoiseInfer → SignalExtract → NoiseClassify → Filter → Sense → Resolve → Ground → Structure → Verify → Compile

    Core invariant: NaturalLanguage ↛ ActionDirectly

    Signal-Noise Law: U_t = Sig_t + Noi_t + Amb_t
    """

    # Execution gate thresholds
    SEMANTIC_CONFIDENCE_THRESHOLD: float = 0.85
    AMBIGUITY_THRESHOLD: float = 0.15
    MAX_MISSING_SLOTS: int = 0

    # Signal-Noise Kernel thresholds
    SIGNAL_QUALITY_THRESHOLD: float = SIGNAL_QUALITY_THRESHOLD
    NOISE_QUALITY_THRESHOLD: float = NOISE_QUALITY_THRESHOLD
    AMBIGUITY_THRESHOLD_SIGNAL: float = AMBIGUITY_THRESHOLD_SIGNAL

    def __init__(self) -> None:
        self.state: TranslationState = TranslationState.RAW_INPUT
        self.current_representation: Optional[SemanticIntentRepresentation] = None
        self.translation_history: List[dict[str, Any]] = []

    # ==========================================================================
    # MAIN PIPELINE: T_AMOS = (E_parse, E_sense, E_resolve, E_ground, E_structure, E_verify, E_compile)
    # ==========================================================================

    async def translate(
        self,
        raw_text: str,
        language: str = "en",
        dialogue_context: Dict[str, Any] = None,
        memory_context: Dict[str, Any] = None,
        world_context: Dict[str, Any] = None,
        identity_context: Dict[str, Any] = None,
        governance_context: Dict[str, Any] = None,
    ) -> SemanticIntentRepresentation:
        """
        CORRECTED main translation pipeline with Signal-Noise Kernel.

        NEW PIPELINE:
        Parse → SignalNoiseInfer → SignalExtract → NoiseClassify → Filter → Sense → Resolve → Ground → Structure → Verify → Compile

        M_t* = Compile(Verify(Structure(Ground(Resolve(Sense(Filter(NoiseClassify(SignalExtract(SignalNoiseInfer(Parse(U_t)))))))))))
        """
        logger.info(f"Starting CORRECTED translation with Signal-Noise Kernel: {raw_text[:50]}...")

        # Initialize representation
        utterance_id = f"utt_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')}"

        # Stage 1: PARSE(U_t) → P_t
        self.state = TranslationState.RAW_INPUT
        parsed = await self._parse_utterance(raw_text, language, dialogue_context or {})
        self.state = TranslationState.PARSED

        # Stage 2: INFER HUMAN STATE FROM LANGUAGE (early state estimate for Signal-Noise Kernel)
        human_state_estimate = await self._infer_human_state_from_language(
            raw_text, dialogue_context or {}
        )

        # ==========================================================================
        # NEW STAGES: SIGNAL-NOISE KERNEL (mandatory - fixes the bug)
        # ==========================================================================

        # Stage 3: SIGNAL_NOISE_INFER(U_t, State) → SN_t
        self.state = TranslationState.SIGNAL_NOISE_INFERRED
        signal_noise_rep = await self._infer_signal_noise(
            raw_text, parsed, human_state_estimate, dialogue_context or {}
        )

        # Stage 4: EXTRACT_SIGNAL_UNITS(SN_t) → Sig_t
        self.state = TranslationState.SIGNAL_EXTRACTED
        signal_units = await self._extract_signal_units(signal_noise_rep, parsed)

        # Stage 5: CLASSIFY_NOISE_UNITS(SN_t, State) → Noi_t
        self.state = TranslationState.NOISE_CLASSIFIED
        noise_units = await self._classify_noise_units(signal_noise_rep, human_state_estimate)

        # Stage 6: SCORE SIGNAL/NOISE QUALITY
        signal_score = self._score_signal_quality(signal_units)
        noise_score = self._score_noise_distortion(noise_units)

        # Update signal_noise_rep with scores
        signal_noise_rep.summary.signal_score = signal_score
        signal_noise_rep.summary.noise_score = noise_score
        signal_noise_rep.summary.translation_ready = (
            signal_score >= self.SIGNAL_QUALITY_THRESHOLD
            and noise_score <= self.NOISE_QUALITY_THRESHOLD
        )

        # Stage 7: FILTER_TRANSLATION_INPUT → FilteredSemanticInput
        filtered_input = self._filter_translation_input(
            signal_units, noise_units, signal_noise_rep.ambiguity_units
        )

        logger.info(
            f"Signal-Noise Kernel complete: signal_score={signal_score:.2f}, "
            f"noise_score={noise_score:.2f}, translation_ready={signal_noise_rep.summary.translation_ready}"
        )

        # ==========================================================================
        # EXISTING STAGES: Now operate on FILTERED input (signal-dominant)
        # ==========================================================================

        # Stage 8: SENSE(FilteredInput) → S_t
        semantic_hypotheses = await self._infer_semantics_filtered(
            filtered_input, parsed, memory_context or {}, world_context or {}
        )
        self.state = TranslationState.SEMANTIC_HYPOTHESES

        # Stage 9: RESOLVE(S_t) → R_t
        resolved = await self._resolve_ambiguity(
            semantic_hypotheses, dialogue_context or {}, memory_context or {}
        )
        self.state = TranslationState.RESOLVED

        # Check if ambiguity requires clarification
        unresolved = [a for a in resolved.remaining_ambiguities if a.severity > 0.3]
        if unresolved:
            logger.warning(f"Unresolved ambiguities detected: {len(unresolved)}")

        # Stage 10: GROUND(R_t) → G_t
        grounded = await self._ground_semantics(
            resolved, memory_context or {}, world_context or {}, identity_context or {}
        )
        self.state = TranslationState.GROUNDED

        # Stage 11: STRUCTURE(G_t) → IGraph_t
        intent_graph = await self._build_intent_graph(grounded, resolved.constraints, [])
        self.state = TranslationState.STRUCTURED

        # Stage 12: VERIFY(IGraph_t) → V_t
        verification = await self._verify_semantics(
            intent_graph, governance_context or {}, {}, signal_noise_rep
        )
        self.state = TranslationState.VERIFIED

        # Stage 13: COMPILE(V_t) → M_t*
        compiled_goal = await self._compile_machine_goal(verification, signal_noise_rep)
        self.state = TranslationState.COMPILED

        # Build final representation
        representation = SemanticIntentRepresentation(
            utterance_id=utterance_id,
            raw_text=raw_text,
            language=language,
            speech_acts=await self._detect_speech_acts(parsed),
            semantic_units=grounded.units,
            human_state_estimate=human_state_estimate,
            intent_hypotheses=[],  # Populated from intent_graph
            ambiguities=resolved.remaining_ambiguities,
            constraints=resolved.constraints,
            requested_output=RequestedOutput(),
            safety_flags=await self._assess_safety(verification, grounded, signal_noise_rep),
            semantic_confidence=verification.semantic_confidence,
            requires_clarification=verification.requires_clarification,
            clarification_targets=verification.missing_slots,
            compiled_machine_goal=compiled_goal,
        )

        # Determine if execution is allowed (UPDATED with Signal-Noise thresholds)
        execution_allowed = self._evaluate_execution_gate_signal_noise(
            verification, signal_noise_rep
        )
        representation.compiled_machine_goal.execution_allowed = execution_allowed

        if execution_allowed:
            self.state = TranslationState.EXECUTABLE
            logger.info("CORRECTED translation complete - execution allowed")
        else:
            logger.info(
                "CORRECTED translation complete - execution blocked (signal/noise/ambiguity check)"
            )

        self.current_representation = representation
        return representation

    # ==========================================================================
    # STAGE 1: PARSE(U_t) → P_t
    # ==========================================================================

    async def _parse_utterance(
        self, raw_text: str, language: str, dialogue_context: Dict[str, Any]
    ) -> ParsedUtterance:
        """
        Parse(U_t) → P_t

        Converts raw text to syntactic and token structure.
        """
        logger.debug(f"Parsing utterance: {raw_text[:50]}...")

        # Tokenization (simplified - in production use spaCy/NLTK)
        tokens = raw_text.split()

        # Clause segmentation (simplified)
        clauses = self._segment_clauses(raw_text)

        # Named entity extraction placeholder
        named_entities = self._extract_named_entities(raw_text)

        # Coreference candidates
        coreference_candidates = self._detect_coreferences(raw_text, dialogue_context)

        # Dependency parsing placeholder
        dependencies = self._extract_dependencies(tokens)

        return ParsedUtterance(
            tokens=tokens,
            clauses=clauses,
            dependencies=dependencies,
            named_entities=named_entities,
            coreference_candidates=coreference_candidates,
        )

    def _segment_clauses(self, text: str) -> List[str]:
        """Segment text into clauses."""
        # Simplified clause segmentation
        delimiters = [".", "!", "?", ";", ", and", ", but", ", so"]
        clauses = [text]
        for delim in delimiters:
            new_clauses = []
            for clause in clauses:
                parts = clause.split(delim)
                new_clauses.extend([p.strip() for p in parts if p.strip()])
            clauses = new_clauses
        return clauses if clauses else [text]

    def _extract_named_entities(self, text: str) -> List[str]:
        """Extract named entities (placeholder for NER)."""
        # Placeholder - in production use spaCy NER
        import re

        # Simple pattern for capitalized phrases
        pattern = r"\b[A-Z][a-zA-Z\s]*\b"
        matches = re.findall(pattern, text)
        return list(set(matches))[:5]  # Limit to top 5

    def _detect_coreferences(self, text: str, context: Dict[str, Any]) -> List[str]:
        """Detect coreference candidates."""
        pronouns = ["he", "she", "it", "they", "them", "this", "that", "these", "those"]
        candidates = []
        text_lower = text.lower()
        for pronoun in pronouns:
            if pronoun in text_lower:
                candidates.append(pronoun)
        return candidates

    def _extract_dependencies(self, tokens: List[str]) -> List[Dependency]:
        """Extract syntactic dependencies (placeholder)."""
        # Placeholder - in production use dependency parser
        dependencies = []
        if len(tokens) > 1:
            # Simple approximation: first token as head
            for i, token in enumerate(tokens[1:], 1):
                dependencies.append(Dependency(head=tokens[0], relation="dep", dependent=token))
        return dependencies

    # ==========================================================================
    # STAGE 2: SENSE(P_t) → S_t
    # ==========================================================================

    async def _infer_semantics(
        self, parsed: ParsedUtterance, memory_context: Dict[str, Any], world_context: Dict[str, Any]
    ) -> SemanticHypotheses:
        """
        Sense(P_t) → S_t

        Maps parsed text to semantic candidates.
        """
        logger.debug("Inferring semantic hypotheses...")

        candidates = []

        # Extract semantic units from each clause
        for i, clause in enumerate(parsed.clauses):
            unit = SemanticUnit(
                unit_id=f"su_{i}",
                surface_text=clause,
                normalized_text=clause.lower().strip(),
                proposition_type=self._classify_proposition_type(clause),
                entities=self._extract_entities_from_clause(clause),
                relations=[],
                time_ref=self._extract_time_reference(clause),
                modality=self._extract_modality(clause),
                polarity=self._detect_polarity(clause),
            )
            candidates.append(unit)

        # Calculate confidence scores
        confidence_scores = {unit.unit_id: 0.7 + (0.1 * i) for i, unit in enumerate(candidates)}

        return SemanticHypotheses(candidates=candidates, confidence_scores=confidence_scores)

    def _classify_proposition_type(self, clause: str) -> PropositionType:
        """Classify the type of proposition in a clause."""
        clause_lower = clause.lower()

        if any(q in clause_lower for q in ["what", "how", "why", "when", "where", "?"]):
            return PropositionType.QUESTION
        elif any(
            e in clause_lower for e in ["feel", "angry", "sad", "happy", "frustrated", "worried"]
        ):
            return PropositionType.EMOTION_SIGNAL
        elif any(
            g in clause_lower for g in ["need", "want", "should", "must", "goal", "objective"]
        ):
            return PropositionType.GOAL
        elif any(
            c in clause_lower
            for c in ["cannot", "can't", "unable", "limitation", "constraint", "only"]
        ):
            return PropositionType.CONSTRAINT
        elif any(m in clause_lower for m in ["like", "as if", "metaphor", "symbolic"]):
            return PropositionType.METAPHOR
        elif any(i in clause_lower for i in ["i am", "i'm", "myself", "identity"]):
            return PropositionType.IDENTITY_STATEMENT
        elif any(
            u in clause_lower for u in ["maybe", "perhaps", "uncertain", "not sure", "unknown"]
        ):
            return PropositionType.UNCERTAINTY
        else:
            return PropositionType.CLAIM

    def _extract_entities_from_clause(self, clause: str) -> List[str]:
        """Extract entities from a clause."""
        words = clause.split()
        # Simple heuristic: nouns (words not starting with lowercase after first)
        entities = [w for w in words if w[0].isupper() or w in ["I", "me", "you", "we", "they"]]
        return entities[:5]

    def _extract_time_reference(self, clause: str) -> TimeReference:
        """Extract temporal reference from clause."""
        clause_lower = clause.lower()

        past_markers = ["yesterday", "last", "ago", "before", "previously", "was", "were"]
        future_markers = ["tomorrow", "next", "will", "going to", "soon", "later", "plan"]

        if any(m in clause_lower for m in past_markers):
            return TimeReference(type=TimeReferenceType.PAST, value="past")
        elif any(m in clause_lower for m in future_markers):
            return TimeReference(type=TimeReferenceType.FUTURE, value="future")
        elif any(m in clause_lower for m in ["now", "currently", "present"]):
            return TimeReference(type=TimeReferenceType.PRESENT, value="present")
        else:
            return TimeReference(type=TimeReferenceType.UNKNOWN)

    def _extract_modality(self, clause: str) -> Modality:
        """Extract modal characteristics."""
        clause_lower = clause.lower()

        certainty = 0.5
        if any(w in clause_lower for w in ["certain", "sure", "definitely", "absolutely"]):
            certainty = 0.9
        elif any(w in clause_lower for w in ["maybe", "perhaps", "possibly", "might"]):
            certainty = 0.3
        elif any(w in clause_lower for w in ["uncertain", "doubt", "not sure"]):
            certainty = 0.1

        necessity = 0.0
        if any(w in clause_lower for w in ["must", "have to", "necessary", "required"]):
            necessity = 0.9
        elif any(w in clause_lower for w in ["should", "ought", "recommend"]):
            necessity = 0.6

        possibility = 0.5
        if any(w in clause_lower for w in ["can", "could", "possible", "able"]):
            possibility = 0.8
        elif any(w in clause_lower for w in ["cannot", "can't", "impossible"]):
            possibility = 0.0

        return Modality(certainty=certainty, necessity=necessity, possibility=possibility)

    def _detect_polarity(self, clause: str) -> Polarity:
        """Detect polarity of clause."""
        clause_lower = clause.lower()

        neg_markers = ["not", "no", "never", "none", "nothing", "n't", "without"]
        pos_markers = ["yes", "good", "great", "excellent", "positive", "success"]

        neg_count = sum(1 for m in neg_markers if m in clause_lower)
        pos_count = sum(1 for m in pos_markers if m in clause_lower)

        if neg_count > pos_count:
            return Polarity.NEGATIVE
        elif pos_count > neg_count:
            return Polarity.POSITIVE
        else:
            return Polarity.MIXED if pos_count > 0 else Polarity.UNKNOWN

    # ==========================================================================
    # STAGE 3: RESOLVE(S_t) → R_t
    # ==========================================================================

    async def _resolve_ambiguity(
        self,
        semantic_hypotheses: SemanticHypotheses,
        dialogue_history: Dict[str, Any],
        memory_context: Dict[str, Any],
    ) -> ResolvedSemantics:
        """
        Resolve(S_t) → R_t

        Resolves ambiguity, scope, and reference.

        Core law: UnresolvedAmbiguity > τ ⇒ NoDirectExecution
        """
        logger.debug("Resolving ambiguities...")

        units = semantic_hypotheses.candidates
        resolved_ambiguities: List[Ambiguity] = []
        remaining_ambiguities: List[Ambiguity] = []

        # Detect ambiguities
        for unit in units:
            # Reference ambiguity
            if unit.proposition_type == PropositionType.QUESTION:
                if any(p in unit.surface_text.lower() for p in ["it", "this", "that", "they"]):
                    ambiguity = Ambiguity(
                        type=AmbiguityType.REFERENCE,
                        location=unit.unit_id,
                        candidates=["entity_from_previous_turn", "generic_concept"],
                        severity=0.6,
                    )
                    remaining_ambiguities.append(ambiguity)

            # Goal ambiguity
            if unit.proposition_type == PropositionType.GOAL:
                ambiguity = Ambiguity(
                    type=AmbiguityType.GOAL,
                    location=unit.unit_id,
                    candidates=["immediate_action", "long_term_objective", "exploration"],
                    severity=0.4,
                )
                resolved_ambiguities.append(ambiguity)

            # Metaphor detection
            if unit.proposition_type == PropositionType.METAPHOR:
                ambiguity = Ambiguity(
                    type=AmbiguityType.METAPHOR,
                    location=unit.unit_id,
                    candidates=["literal_interpretation", "metaphorical_meaning"],
                    severity=0.7,
                )
                remaining_ambiguities.append(ambiguity)

        # Extract constraints
        constraints = self._extract_constraints_from_units(units)

        return ResolvedSemantics(
            units=units,
            resolved_ambiguities=resolved_ambiguities,
            remaining_ambiguities=remaining_ambiguities,
            constraints=constraints,
        )

    def _extract_constraints_from_units(self, units: List[SemanticUnit]) -> List[Constraint]:
        """Extract constraints from semantic units."""
        constraints = []
        for unit in units:
            if unit.proposition_type == PropositionType.CONSTRAINT:
                constraints.append(
                    Constraint(
                        type=ConstraintType.HARD
                        if unit.modality.necessity > 0.7
                        else ConstraintType.SOFT,
                        content=unit.surface_text,
                        confidence=unit.modality.certainty,
                    )
                )
        return constraints

    # ==========================================================================
    # STAGE 4: GROUND(R_t) → G_t
    # ==========================================================================

    async def _ground_semantics(
        self,
        resolved: ResolvedSemantics,
        world_model: Dict[str, Any],
        memory_state: Dict[str, Any],
        identity_state: Dict[str, Any],
    ) -> GroundedSemantics:
        """
        Ground(R_t) → G_t

        Maps language to persistent entities, time, world state, and known constraints.
        """
        logger.debug("Grounding semantics...")

        grounded_entities = {}

        # Ground entities from memory
        for unit in resolved.units:
            for entity in unit.entities:
                if entity in memory_state.get("known_entities", {}):
                    grounded_entities[entity] = memory_state["known_entities"][entity]
                else:
                    grounded_entities[entity] = {"type": "unresolved", "mentions": 1}

        # Build temporal context
        temporal_context = {
            "utterance_time": datetime.now(UTC).isoformat(),
            "referenced_times": [u.time_ref for u in resolved.units if u.time_ref],
            "temporal_consistency": True,
        }

        return GroundedSemantics(
            units=resolved.units,
            grounded_entities=grounded_entities,
            temporal_context=temporal_context,
        )

    # ==========================================================================
    # STAGE 5: STRUCTURE(G_t) → IGraph_t
    # ==========================================================================

    async def _build_intent_graph(
        self,
        grounded: GroundedSemantics,
        constraints: List[Constraint],
        intent_hypotheses: List[IntentHypothesis],
    ) -> IntentGraph:
        """
        Structure(G_t) → IGraph_t

        Turns grounded meaning into a formal graph.
        """
        logger.debug("Building intent graph...")

        nodes = []
        edges = []

        # Create nodes from semantic units
        for i, unit in enumerate(grounded.units):
            node_type = self._map_proposition_to_node_type(unit.proposition_type)
            nodes.append(IntentNode(id=f"node_{i}", type=node_type))

        # Add constraint nodes
        for i, constraint in enumerate(constraints):
            nodes.append(IntentNode(id=f"constraint_{i}", type="constraint"))

        # Add goal node
        nodes.append(IntentNode(id="primary_goal", type="goal"))

        # Create edges (dependencies)
        for i in range(len(grounded.units)):
            edges.append(IntentEdge(source=f"node_{i}", type="targets", target="primary_goal"))

        # Constraint edges
        for i in range(len(constraints)):
            edges.append(IntentEdge(source=f"constraint_{i}", type="blocks", target="primary_goal"))

        return IntentGraph(nodes=nodes, edges=edges)

    def _map_proposition_to_node_type(self, prop_type: PropositionType) -> str:
        """Map proposition type to intent graph node type."""
        mapping = {
            PropositionType.CLAIM: "state",
            PropositionType.QUESTION: "question",
            PropositionType.GOAL: "goal",
            PropositionType.CONSTRAINT: "constraint",
            PropositionType.EMOTION_SIGNAL: "state",
            PropositionType.IDENTITY_STATEMENT: "entity",
            PropositionType.UNCERTAINTY: "question",
            PropositionType.METAPHOR: "state",
        }
        return mapping.get(prop_type, "state")

    def _detect_contradictions(self, intent_graph: IntentGraph) -> bool:
        """Detect contradictions in intent graph."""
        # Placeholder - check for conflicting edges
        conflict_edges = [e for e in intent_graph.edges if e.type == "conflicts_with"]
        return len(conflict_edges) > 0

    def _identify_missing_slots(self, intent_graph: IntentGraph) -> List[str]:
        """Identify missing information slots."""
        missing = []

        # Check for goal nodes without sufficient dependencies
        goal_nodes = [n for n in intent_graph.nodes if n.type == "goal"]
        for goal in goal_nodes:
            deps = [e for e in intent_graph.edges if e.target == goal.id and e.type == "depends_on"]
            if len(deps) < 1:
                missing.append(f"goal_{goal.id}_missing_dependencies")

        # Check for unresolved entities
        entity_nodes = [n for n in intent_graph.nodes if n.type == "entity"]
        for entity in entity_nodes:
            missing.append(f"entity_{entity.id}_requires_grounding")

        return missing[:3]  # Limit to top 3

    def _calculate_ambiguity_score(self, intent_graph: IntentGraph) -> float:
        """Calculate overall ambiguity score."""
        # Placeholder - based on graph complexity
        node_count = len(intent_graph.nodes)
        edge_count = len(intent_graph.edges)

        if node_count == 0:
            return 1.0

        # Higher ratio of edges to nodes = more structured = less ambiguous
        ratio = edge_count / node_count
        ambiguity = 1.0 - min(1.0, ratio)

        return ambiguity

    def _generate_clarification_questions(
        self, missing_slots: List[str], intent_graph: IntentGraph
    ) -> List[str]:
        """Generate questions to clarify missing information."""
        questions = []

        for slot in missing_slots:
            if "goal" in slot:
                questions.append("What specific outcome are you looking for?")
            elif "entity" in slot:
                questions.append("Could you clarify what you're referring to?")
            elif "constraint" in slot:
                questions.append("Are there any limitations or constraints I should know about?")
            else:
                questions.append("Could you provide more details?")

        return list(set(questions))  # Remove duplicates

    # ==========================================================================
    # SIGNAL-NOISE KERNEL METHODS (NEW - Fixes the Bug)
    # ==========================================================================

    async def _infer_signal_noise(
        self,
        raw_text: str,
        parsed: ParsedUtterance,
        human_state: HumanStateEstimate,
        dialogue_context: Dict[str, Any],
    ) -> SignalNoiseRepresentation:
        """
        infer_signal_noise(raw_text, dialogue_context, human_state_estimate) → SignalNoiseRepresentation

        Decomposes utterance: U_t = Sig_t + Noi_t + Amb_t

        Where:
            Sig_t = structurally relevant meaning
            Noi_t = distortion, defense, overload, filler, narrative residue
            Amb_t = unresolved ambiguity
        """
        logger.debug("Signal-Noise Kernel: Inferring signal/noise decomposition...")

        utterance_id = f"sn_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')}"

        # Initialize with empty units - to be populated by extract/classify
        signal_units: List[SignalUnit] = []
        noise_units: List[NoiseUnit] = []
        ambiguity_units: List[AmbiguityUnit] = []

        # Initial pass: identify potential signal and noise segments
        for i, clause in enumerate(parsed.clauses):
            clause.lower().strip()

            # Check for ambiguity markers
            ambiguity_detected = self._detect_ambiguity_in_text(clause)
            if ambiguity_detected:
                ambiguity_units.append(
                    AmbiguityUnit(
                        unit_id=f"amb_{i}",
                        ambiguity_type=ambiguity_detected["type"],
                        severity=ambiguity_detected["severity"],
                        candidates=ambiguity_detected.get("candidates", []),
                        location=f"clause_{i}",
                    )
                )

        # Create initial representation (signal_units and noise_units populated by next stages)
        signal_noise_rep = SignalNoiseRepresentation(
            utterance_id=utterance_id,
            raw_text=raw_text,
            signal_units=signal_units,
            noise_units=noise_units,
            ambiguity_units=ambiguity_units,
            human_state_estimate=human_state,
            summary=SignalNoiseSummary(
                signal_score=0.0,
                noise_score=0.0,
                ambiguity_score=sum(a.severity for a in ambiguity_units)
                / max(len(ambiguity_units), 1),
                state_distortion_score=human_state.defensiveness + human_state.overload_risk,
                translation_ready=False,
            ),
        )

        return signal_noise_rep

    def _detect_ambiguity_in_text(self, text: str) -> Dict[str, Any]:
        """Detect ambiguity in text segment."""
        text_lower = text.lower()

        # Reference ambiguity
        ref_pronouns = ["it", "this", "that", "they", "them", "he", "she"]
        if any(p in text_lower for p in ref_pronouns):
            return {"type": AmbiguityUnitType.REFERENCE, "severity": 0.6, "candidates": []}

        # Goal ambiguity
        goal_markers = ["should", "maybe", "perhaps", "could", "might"]
        if any(m in text_lower for m in goal_markers):
            return {"type": AmbiguityUnitType.GOAL, "severity": 0.4, "candidates": []}

        # Scope ambiguity
        scope_markers = ["everything", "all", "always", "never", "everyone"]
        if any(m in text_lower for m in scope_markers):
            return {"type": AmbiguityUnitType.SCOPE, "severity": 0.5, "candidates": []}

        return None

    async def _extract_signal_units(
        self, signal_noise_rep: SignalNoiseRepresentation, parsed: ParsedUtterance
    ) -> List[SignalUnit]:
        """
        extract_signal_units(parsed_utterance, context) → SignalUnit[]

        Sig_t* = argmax_s [StructuralRelevance(s) * GoalRelevance(s) * Stability(s) * Grounding(s)]
        """
        logger.debug("Signal-Noise Kernel: Extracting signal units...")

        signal_units: List[SignalUnit] = []

        for i, clause in enumerate(parsed.clauses):
            clause.lower().strip()

            # Detect signal classes and score
            signal_class, relevance, grounding, goal_fit = self._classify_signal(clause)

            if signal_class:
                signal_units.append(
                    SignalUnit(
                        unit_id=f"sig_{i}",
                        text=clause,
                        signal_class=signal_class,
                        relevance_score=relevance,
                        grounding_score=grounding,
                        goal_fit_score=goal_fit,
                        confidence=relevance * grounding,
                    )
                )

        signal_noise_rep.signal_units = signal_units
        return signal_units

    def _classify_signal(self, clause: str) -> Optional[Tuple[SignalClass ], float, float, float]:
        """Classify clause into signal class with scores."""
        clause_lower = clause.lower()

        # Explicit goal detection
        goal_markers = ["need", "want", "should", "must", "goal", "objective", "aim to"]
        if any(m in clause_lower for m in goal_markers):
            return (SignalClass.EXPLICIT_GOAL, 0.9, 0.8, 0.95)

        # Constraint detection
        constraint_markers = [
            "cannot",
            "can't",
            "unable",
            "limitation",
            "constraint",
            "only",
            "restrict",
        ]
        if any(m in clause_lower for m in constraint_markers):
            return (SignalClass.EXPLICIT_CONSTRAINT, 0.85, 0.9, 0.8)

        # Question detection
        if "?" in clause or any(q in clause_lower for q in ["what", "how", "why", "when", "where"]):
            return (SignalClass.REAL_QUESTION, 0.9, 0.85, 0.9)

        # Risk marker detection
        risk_markers = ["risk", "danger", "warning", "alert", "careful", "beware", "unsafe"]
        if any(m in clause_lower for m in risk_markers):
            return (SignalClass.RISK_MARKER, 0.85, 0.8, 0.75)

        # Output format request
        format_markers = ["json", "table", "list", "steps", "bullet", "format as"]
        if any(m in clause_lower for m in format_markers):
            return (SignalClass.REQUESTED_OUTPUT_FORMAT, 0.9, 0.9, 0.7)

        # Resource constraint
        resource_markers = ["time", "budget", "memory", "cpu", "storage", "cost"]
        if any(m in clause_lower for m in resource_markers):
            return (SignalClass.RESOURCE_CONSTRAINT, 0.7, 0.75, 0.8)

        # Decision-relevant fact
        fact_markers = ["data shows", "evidence", "research", "study", "report", "metric"]
        if any(m in clause_lower for m in fact_markers):
            return (SignalClass.DECISION_RELEVANT_FACT, 0.8, 0.85, 0.75)

        # True uncertainty
        uncertainty_markers = ["uncertain", "not sure", "unknown", "unclear", "ambiguous"]
        if any(m in clause_lower for m in uncertainty_markers):
            return (SignalClass.TRUE_UNCERTAINTY, 0.75, 0.7, 0.8)

        # Default: treat as potential signal with lower confidence
        return (SignalClass.STATE_RELEVANT_MARKER, 0.5, 0.5, 0.5)

    async def _classify_noise_units(
        self, signal_noise_rep: SignalNoiseRepresentation, human_state: HumanStateEstimate
    ) -> List[NoiseUnit]:
        """
        classify_noise_units(parsed_utterance, human_state_estimate, context) → NoiseUnit[]

        Noi_t* = argmax_n [DefenseLikelihood(n) * NarrativeRedundancy(n) * AffectiveDistortion(n) * ...]

        Rule: NotAllNoiseIsDiscarded; SomeNoiseIsRiskSignal
        """
        logger.debug("Signal-Noise Kernel: Classifying noise units...")

        noise_units: List[NoiseUnit] = []
        raw_text = signal_noise_rep.raw_text.lower()

        # Check for noise patterns
        noise_patterns = [
            (
                NoiseClass.EGO_DEFENSE,
                ["but", "however", "actually", "not really", "you don't understand"],
                0.6,
            ),
            (
                NoiseClass.NARRATIVE_LOOP,
                ["always", "never", "every time", "constantly", "keeps happening"],
                0.5,
            ),
            (
                NoiseClass.FEAR_PROJECTION,
                ["what if", "might happen", "could fail", "disaster", "catastrophe"],
                0.7,
            ),
            (
                NoiseClass.AVOIDANCE_LANGUAGE,
                ["maybe later", "someday", "when ready", "eventually", "probably"],
                0.4,
            ),
            (
                NoiseClass.IDENTITY_FUSION,
                ["i am", "i'm just", "that's who i am", "i always", "my nature"],
                0.5,
            ),
            (
                NoiseClass.PERFORMATIVE_INTENSITY,
                ["!", "very", "extremely", "incredibly", "absolutely", "totally"],
                0.4,
            ),
            (
                NoiseClass.METAPHORIC_OVERCOMPRESSION,
                ["like", "as if", "metaphor", "symbolic", "represents"],
                0.5,
            ),
            (
                NoiseClass.PANIC_SCOPE_EXPANSION,
                ["everything", "everyone", "all", "whole", "entire", "completely"],
                0.6,
            ),
            (
                NoiseClass.SELF_GLOBALIZATION,
                ["i always fail", "i never succeed", "everything i do", "ruins everything"],
                0.7,
            ),
            (
                NoiseClass.CONSTRAINT_SMEARING,
                ["impossible", "can't do anything", "no point", "hopeless"],
                0.6,
            ),
            (
                NoiseClass.SEMANTIC_FILLER,
                ["um", "uh", "like", "you know", "sort of", "kind of", "basically"],
                0.3,
            ),
        ]

        for noise_class, patterns, base_severity in noise_patterns:
            for pattern in patterns:
                if pattern in raw_text:
                    # Check if this noise is diagnostically important (risk signal)
                    retain_as_state = self._is_noise_diagnostically_relevant(
                        noise_class, human_state
                    )

                    state_role = None
                    if retain_as_state:
                        if noise_class in [
                            NoiseClass.FEAR_PROJECTION,
                            NoiseClass.SELF_GLOBALIZATION,
                        ]:
                            state_role = "risk_indicator"
                        elif noise_class in [NoiseClass.EGO_DEFENSE, NoiseClass.AVOIDANCE_LANGUAGE]:
                            state_role = "defense_indicator"
                        else:
                            state_role = "state_indicator"

                    noise_units.append(
                        NoiseUnit(
                            unit_id=f"noi_{noise_class.value}_{len(noise_units)}",
                            text=pattern,
                            noise_class=noise_class,
                            severity=base_severity,
                            distortion_risk=base_severity * 1.2,
                            confidence=0.7,
                            retain_as_state_signal=retain_as_state,
                            state_signal_role=state_role,
                        )
                    )

        signal_noise_rep.noise_units = noise_units
        return noise_units

    def _is_noise_diagnostically_relevant(
        self, noise_class: NoiseClass, human_state: HumanStateEstimate
    ) -> bool:
        """Determine if noise should be retained as state signal."""
        # High-risk noise classes are always retained
        high_risk_noise = [
            NoiseClass.FEAR_PROJECTION,
            NoiseClass.SELF_GLOBALIZATION,
            NoiseClass.PANIC_SCOPE_EXPANSION,
        ]
        if noise_class in high_risk_noise:
            return True

        # Defensive noise is relevant when human is in defensive state
        if noise_class == NoiseClass.EGO_DEFENSE and human_state.defensiveness > 0.5:
            return True

        # Overload markers relevant when human is overloaded
        if noise_class == NoiseClass.SEMANTIC_FILLER and human_state.overload_risk > 0.4:
            return True

        return False

    def _score_signal_quality(self, signal_units: List[SignalUnit]) -> float:
        """
        score_signal_quality(signal_units) → number

        Q_sig = α·StructuralRelevance + β·Grounding + γ·GoalFit + δ·ConstraintPreservation
        """
        if not signal_units:
            return 0.0

        total_score = 0.0
        for unit in signal_units:
            unit_score = (
                SIGNAL_QUALITY_WEIGHTS["structural_relevance"] * unit.relevance_score
                + SIGNAL_QUALITY_WEIGHTS["grounding"] * unit.grounding_score
                + SIGNAL_QUALITY_WEIGHTS["goal_fit"] * unit.goal_fit_score
                + SIGNAL_QUALITY_WEIGHTS["constraint_preservation"] * 0.5  # Default
            )
            total_score += unit_score

        # Average and normalize
        avg_score = total_score / len(signal_units)
        return min(1.0, avg_score)

    def _score_noise_distortion(self, noise_units: List[NoiseUnit]) -> float:
        """
        score_noise_distortion(noise_units) → number

        Q_noi = α·Defense + β·Looping + γ·Reactivity + δ·MetaphorLoad + ε·Ambiguity + ζ·Overload
        """
        if not noise_units:
            return 0.0

        total_score = 0.0
        for unit in noise_units:
            # Only count noise that is NOT retained as state signal
            if not unit.retain_as_state_signal:
                total_score += unit.severity

        # Normalize by count
        return min(1.0, total_score / max(len(noise_units), 1))

    def _filter_translation_input(
        self,
        signal_units: List[SignalUnit],
        noise_units: List[NoiseUnit],
        ambiguity_units: List[AmbiguityUnit],
    ) -> FilteredSemanticInput:
        """
        filter_translation_input(signal_noise_representation) → FilteredSemanticInput

        Only signal should dominate semantic compilation.
        Some noise is retained as state/risk/defense indicator.
        """
        # Primary signal units
        primary_signals = [su for su in signal_units if su.relevance_score > 0.5]

        # Retain diagnostically relevant noise as state signals
        retained_noise = [
            {"text": nu.text, "role": nu.state_signal_role}
            for nu in noise_units
            if nu.retain_as_state_signal and nu.state_signal_role
        ]

        # Dropped noise (semantically irrelevant)
        dropped_noise = [nu.text for nu in noise_units if not nu.retain_as_state_signal]

        # Convert ambiguity units to constraints when severe
        effective_constraints: List[Constraint] = []
        for amb in ambiguity_units:
            if amb.severity > 0.6:
                effective_constraints.append(
                    Constraint(
                        type=ConstraintType.IMPLIED,
                        content=f"resolve_{amb.ambiguity_type.value}_ambiguity",
                        confidence=1.0 - amb.severity,
                    )
                )

        return FilteredSemanticInput(
            primary_signal_units=primary_signals,
            retained_noise_units=retained_noise,
            dropped_noise_units=dropped_noise,
            ambiguity_units=ambiguity_units,
            effective_constraints=effective_constraints,
        )

    async def _infer_semantics_filtered(
        self,
        filtered_input: FilteredSemanticInput,
        parsed: ParsedUtterance,
        memory_context: Dict[str, Any],
        world_context: Dict[str, Any],
    ) -> SemanticHypotheses:
        """
        SENSE(FilteredInput) → S_t

        Modified to operate on signal-dominant filtered input.
        """
        logger.debug("Inferring semantics from FILTERED signal-dominant input...")

        candidates = []

        # Extract semantic units from signal units (not raw clauses)
        for i, signal_unit in enumerate(filtered_input.primary_signal_units):
            unit = SemanticUnit(
                unit_id=f"su_filtered_{i}",
                surface_text=signal_unit.text,
                normalized_text=signal_unit.text.lower().strip(),
                proposition_type=self._map_signal_to_proposition(signal_unit.signal_class),
                entities=self._extract_entities_from_clause(signal_unit.text),
                relations=[],
                time_ref=self._extract_time_reference(signal_unit.text),
                modality=self._extract_modality(signal_unit.text),
                polarity=self._detect_polarity(signal_unit.text),
            )
            candidates.append(unit)

        # Calculate confidence scores (boosted by signal quality)
        confidence_scores = {
            unit.unit_id: 0.7 + (0.1 * i) + (0.1 if unit.unit_id.startswith("su_filtered") else 0)
            for i, unit in enumerate(candidates)
        }

        return SemanticHypotheses(candidates=candidates, confidence_scores=confidence_scores)

    def _map_signal_to_proposition(self, signal_class: SignalClass) -> PropositionType:
        """Map signal class to proposition type."""
        mapping = {
            SignalClass.EXPLICIT_GOAL: PropositionType.GOAL,
            SignalClass.EXPLICIT_CONSTRAINT: PropositionType.CONSTRAINT,
            SignalClass.REAL_QUESTION: PropositionType.QUESTION,
            SignalClass.RISK_MARKER: PropositionType.EMOTION_SIGNAL,
            SignalClass.RESOURCE_CONSTRAINT: PropositionType.CONSTRAINT,
            SignalClass.TIME_CONSTRAINT: PropositionType.CONSTRAINT,
            SignalClass.TRUE_UNCERTAINTY: PropositionType.UNCERTAINTY,
            SignalClass.DECISION_RELEVANT_FACT: PropositionType.CLAIM,
            SignalClass.REQUESTED_OUTPUT_FORMAT: PropositionType.GOAL,
            SignalClass.STATE_RELEVANT_MARKER: PropositionType.EMOTION_SIGNAL,
            SignalClass.STABLE_PREFERENCE: PropositionType.CLAIM,
            SignalClass.PERSISTENT_PATTERN: PropositionType.CLAIM,
        }
        return mapping.get(signal_class, PropositionType.CLAIM)

    def _evaluate_execution_gate_signal_noise(
        self, verification: SemanticVerification, signal_noise_rep: SignalNoiseRepresentation
    ) -> bool:
        """
        ExecuteAllowed = 𝟙[
            Q_sig ≥ τ_sig ∧
            Q_noi ≤ τ_noi ∧
            Ambiguity ≤ τ_amb ∧
            Verification = 1
        ]
        """
        conditions = {
            "semantic_confidence": verification.semantic_confidence
            >= self.SEMANTIC_CONFIDENCE_THRESHOLD,
            "ambiguity_score": verification.ambiguity_score <= self.AMBIGUITY_THRESHOLD,
            "missing_slots": len(verification.missing_slots) == self.MAX_MISSING_SLOTS,
            "safety_check": not verification.is_contradictory,
            "governance_check": True,
            # NEW Signal-Noise conditions
            "signal_quality": signal_noise_rep.summary.signal_score
            >= self.SIGNAL_QUALITY_THRESHOLD,
            "noise_acceptable": signal_noise_rep.summary.noise_score
            <= self.NOISE_QUALITY_THRESHOLD,
            "translation_ready": signal_noise_rep.summary.translation_ready,
        }

        allowed = all(conditions.values())

        if not allowed:
            logger.warning(f"Execution gate blocked (Signal-Noise aware). Conditions: {conditions}")

        return allowed

    # ==========================================================================
    # STAGE 12 (was 6): VERIFY(IGraph_t) → V_t - MODIFIED
    # ==========================================================================

    async def _verify_semantics(
        self,
        intent_graph: IntentGraph,
        governance_state: Dict[str, Any],
        epistemic_state: Dict[str, Any],
        signal_noise_rep: Optional[SignalNoiseRepresentation] = None,
    ) -> SemanticVerification:
        """
        Verify(IGraph_t) → V_t

        Checks contradiction, underspecification, and risk.
        MODIFIED: Now includes Signal-Noise quality assessment.
        """
        logger.debug("Verifying semantics (Signal-Noise aware)...")

        # Check for contradictions
        is_contradictory = self._detect_contradictions(intent_graph)

        # Identify missing slots
        missing_slots = self._identify_missing_slots(intent_graph)

        # Calculate ambiguity score
        ambiguity_score = self._calculate_ambiguity_score(intent_graph)

        # Adjust ambiguity score based on signal-noise analysis
        if signal_noise_rep:
            ambiguity_score = max(ambiguity_score, signal_noise_rep.summary.ambiguity_score)

        # Calculate semantic confidence
        semantic_confidence = 1.0 - ambiguity_score - (0.1 * len(missing_slots))
        semantic_confidence = max(0.0, min(1.0, semantic_confidence))

        # Adjust confidence based on signal quality
        if signal_noise_rep:
            # Boost confidence if signal quality is high
            semantic_confidence *= 0.5 + 0.5 * signal_noise_rep.summary.signal_score
            # Reduce confidence if noise is high
            semantic_confidence *= 1.0 - 0.3 * signal_noise_rep.summary.noise_score
            semantic_confidence = max(0.0, min(1.0, semantic_confidence))

        # Determine if clarification is required
        requires_clarification = (
            len(missing_slots) > 0
            or ambiguity_score > self.AMBIGUITY_THRESHOLD
            or semantic_confidence < self.SEMANTIC_CONFIDENCE_THRESHOLD
        )

        # Generate clarification questions
        clarification_questions = []
        if requires_clarification:
            clarification_questions = self._generate_clarification_questions(
                missing_slots, intent_graph
            )

        # Check executability
        is_executable = (
            not is_contradictory
            and not requires_clarification
            and semantic_confidence >= self.SEMANTIC_CONFIDENCE_THRESHOLD
        )

        # Override executability based on signal-noise quality
        if signal_noise_rep and not signal_noise_rep.summary.translation_ready:
            is_executable = False

        return SemanticVerification(
            is_executable=is_executable,
            is_contradictory=is_contradictory,
            missing_slots=missing_slots,
            ambiguity_score=ambiguity_score,
            semantic_confidence=semantic_confidence,
            requires_clarification=requires_clarification,
            clarification_questions=clarification_questions,
        )

    async def _compile_machine_goal(
        self,
        verification: SemanticVerification,
        signal_noise_rep: Optional[SignalNoiseRepresentation] = None,
    ) -> CompiledMachineGoal:
        """
        Compile(V_t) -> M_t*

        Compiles verified meaning into machine action or safe response goal.
        """
        logger.debug("Compiling machine goal...")

        # Determine goal type based on verification
        if verification.requires_clarification:
            goal_type = GoalType.ASK_CLARIFICATION
        elif verification.is_contradictory:
            goal_type = GoalType.REFUSE
        elif verification.is_executable:
            goal_type = GoalType.EXECUTE
        else:
            goal_type = GoalType.RESPOND

        # Build objective
        objective = self._build_objective_from_verification(verification)

        # Required inputs
        inputs_required = verification.missing_slots

        # Constraints
        constraints_required: List[str] = []

        # Success criteria
        success_criteria = ["user_satisfaction", "intent_fulfillment", "safety_maintained"]

        return CompiledMachineGoal(
            goal_type=goal_type,
            objective=objective,
            inputs_required=inputs_required,
            constraints_required=constraints_required,
            success_criteria=success_criteria,
            execution_allowed=False,  # Will be set by execution gate
        )

    def _build_objective_from_verification(self, verification: SemanticVerification) -> str:
        """Build objective string from verification."""
        if verification.requires_clarification:
            return "clarify_user_intent"
        elif verification.is_contradictory:
            return "explain_contradiction"
        elif verification.is_executable:
            return "fulfill_user_request"
        else:
            return "respond_to_user"

    # ==========================================================================
    # EXECUTION GATE
    # ==========================================================================

    def _evaluate_execution_gate(self, verification: SemanticVerification) -> bool:
        """
        ExecuteAllowed = 𝟙[
            SemanticConfidence ≥ τ₁ ∧
            AmbiguityScore ≤ τ₂ ∧
            MissingSlots = 0 ∧
            SafetyCheck = 1 ∧
            GovernanceCheck = 1
        ]
        """
        conditions = {
            "semantic_confidence": verification.semantic_confidence
            >= self.SEMANTIC_CONFIDENCE_THRESHOLD,
            "ambiguity_score": verification.ambiguity_score <= self.AMBIGUITY_THRESHOLD,
            "missing_slots": len(verification.missing_slots) == self.MAX_MISSING_SLOTS,
            "safety_check": not verification.is_contradictory,
            "governance_check": True,  # Placeholder
        }

        allowed = all(conditions.values())

        if not allowed:
            logger.warning(f"Execution gate blocked. Conditions: {conditions}")

        return allowed

    # ==========================================================================
    # SUPPORTING FUNCTIONS
    # ==========================================================================

    async def _detect_speech_acts(self, parsed: ParsedUtterance) -> List[SpeechAct]:
        """Detect speech acts from parsed utterance."""
        speech_acts = []

        for clause in parsed.clauses:
            clause_lower = clause.lower()

            # Question detection
            if "?" in clause or any(
                q in clause_lower for q in ["what", "how", "why", "when", "where"]
            ):
                speech_acts.append(SpeechAct(type=SpeechActType.ASK, weight=0.9))

            # Command detection
            elif any(c in clause_lower for c in ["do this", "execute", "run", "start", "stop"]):
                speech_acts.append(SpeechAct(type=SpeechActType.COMMAND, weight=0.8))

            # Request detection
            elif any(r in clause_lower for r in ["please", "can you", "could you", "would you"]):
                speech_acts.append(SpeechAct(type=SpeechActType.REQUEST, weight=0.7))

            # Inform detection
            elif any(i in clause_lower for i in ["is", "are", "was", "were", "fact"]):
                speech_acts.append(SpeechAct(type=SpeechActType.INFORM, weight=0.6))

            # Vent detection
            elif any(
                v in clause_lower for v in ["frustrated", "annoying", "hate", "stupid", "angry"]
            ):
                speech_acts.append(SpeechAct(type=SpeechActType.VENT, weight=0.8))

            # Reflect detection
            elif any(
                r in clause_lower for r in ["think", "wonder", "consider", "maybe", "perhaps"]
            ):
                speech_acts.append(SpeechAct(type=SpeechActType.REFLECT, weight=0.6))

            else:
                speech_acts.append(SpeechAct(type=SpeechActType.INFORM, weight=0.5))

        return speech_acts if speech_acts else [SpeechAct(type=SpeechActType.INFORM, weight=0.5)]

    async def _infer_human_state_from_language(
        self, raw_text: str, dialogue_history: Dict[str, Any]
    ) -> HumanStateEstimate:
        """Infer human state from language patterns."""
        text_lower = raw_text.lower()

        # Cognitive load indicators
        load_indicators = len(raw_text.split()) / 20.0  # Words per sentence proxy
        load_indicators += text_lower.count(",") * 0.1
        load_indicators = min(1.0, load_indicators)

        # Emotional intensity
        emotion_words = ["very", "extremely", "incredibly", "absolutely", "totally", "really", "so"]
        emotional_intensity = sum(1 for w in emotion_words if w in text_lower) / 5.0
        emotional_intensity = min(1.0, emotional_intensity)

        # Overload risk
        overload_markers = ["too much", "overwhelmed", "can't handle", "breaking", "drowning"]
        overload_risk = sum(0.3 for m in overload_markers if m in text_lower)
        overload_risk = min(1.0, overload_risk)

        # Defensiveness
        defense_markers = ["but", "however", "actually", "not really", "you don't understand"]
        defensiveness = sum(0.2 for m in defense_markers if m in text_lower)
        defensiveness = min(1.0, defensiveness)

        # Clarity
        clarity = 1.0 - (len(parsed.clauses) if "parsed" in locals() else 1) * 0.1
        clarity = max(0.0, clarity)

        # Agency
        agency_markers = ["i want", "i need", "i will", "my goal", "i decide"]
        agency = sum(0.2 for m in agency_markers if m in text_lower)
        agency = min(1.0, agency)

        # State class
        if overload_risk > 0.6:
            state_class = HumanStateClass.OVERLOADED
        elif emotional_intensity > 0.7:
            state_class = HumanStateClass.ACTIVATED
        elif overload_risk > 0.3 or emotional_intensity > 0.4:
            state_class = HumanStateClass.HIGH_RISK
        else:
            state_class = HumanStateClass.STABLE

        return HumanStateEstimate(
            cognitive_load=load_indicators,
            emotional_intensity=emotional_intensity,
            overload_risk=overload_risk,
            defensiveness=defensiveness,
            clarity=clarity,
            agency=agency,
            state_class=state_class,
        )

    async def _assess_safety(
        self,
        verification: SemanticVerification,
        grounded: GroundedSemantics,
        signal_noise_rep: Optional[SignalNoiseRepresentation] = None,
    ) -> SafetyFlags:
        """Assess safety flags for the translation with Signal-Noise awareness."""
        # Check for destabilization risk
        destabilization_risk = 1.0 - verification.semantic_confidence

        # Incorporate signal-noise quality if available
        if signal_noise_rep:
            # High noise score increases destabilization risk
            destabilization_risk = max(
                destabilization_risk, signal_noise_rep.summary.noise_score * 0.8
            )
            # State distortion from signal-noise analysis
            destabilization_risk = max(
                destabilization_risk, signal_noise_rep.summary.state_distortion_score
            )

        # Self-harm risk (placeholder - would use safety classifiers in production)
        self_harm_risk = 0.0

        # Harm to others risk
        harm_to_others_risk = 0.0

        # Dependency risk
        dependency_risk = 0.0

        return SafetyFlags(
            human_destabilization_risk=min(1.0, destabilization_risk),
            self_harm_risk=self_harm_risk,
            harm_to_others_risk=harm_to_others_risk,
            dependency_risk=dependency_risk,
            requires_grounding=True,
        )

    # ==========================================================================
    # UTILITY FUNCTIONS
    # ==========================================================================

    def get_state(self) -> TranslationState:
        """Get current translation state."""
        return self.state

    def get_representation(self) -> Optional[SemanticIntentRepresentation]:
        """Get current semantic representation."""
        return self.current_representation

    def to_dict(self) -> Dict[str, Any]:
        """Serialize current representation to dict."""
        if not self.current_representation:
            return {}

        rep = self.current_representation
        return {
            "utterance_id": rep.utterance_id,
            "raw_text": rep.raw_text,
            "language": rep.language,
            "speech_acts": [{"type": sa.type.value, "weight": sa.weight} for sa in rep.speech_acts],
            "semantic_units": [
                {
                    "unit_id": su.unit_id,
                    "surface_text": su.surface_text,
                    "proposition_type": su.proposition_type.value,
                    "polarity": su.polarity.value,
                }
                for su in rep.semantic_units
            ],
            "human_state": {
                "cognitive_load": rep.human_state_estimate.cognitive_load,
                "emotional_intensity": rep.human_state_estimate.emotional_intensity,
                "state_class": rep.human_state_estimate.state_class.value,
            },
            "ambiguities": [
                {"type": a.type.value, "severity": a.severity} for a in rep.ambiguities
            ],
            "semantic_confidence": rep.semantic_confidence,
            "requires_clarification": rep.requires_clarification,
            "execution_allowed": rep.compiled_machine_goal.execution_allowed,
            "goal_type": rep.compiled_machine_goal.goal_type.value,
        }

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), indent=2)


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_translation_layer: Optional[AMOSTranslationLayer] = None


def get_translation_layer() -> AMOSTranslationLayer:
    """Get global translation layer instance."""
    global _translation_layer
    if _translation_layer is None:
        _translation_layer = AMOSTranslationLayer()
    return _translation_layer


# =============================================================================
# EXAMPLE USAGE
# =============================================================================


async def demo():
    """Demonstrate translation layer."""
    print("=" * 80)
    print("AMOS TRANSLATION LAYER - Human-to-Machine Semantic Alignment")
    print("=" * 80)

    translator = get_translation_layer()

    # Example 1: Clear request
    print("\n[Example 1] Clear request:")
    result = await translator.translate(
        "Please execute the softmax equation on [1.0, 2.0, 3.0]", language="en"
    )
    print(f"Execution allowed: {result.compiled_machine_goal.execution_allowed}")
    print(f"Goal type: {result.compiled_machine_goal.goal_type.value}")
    print(f"Semantic confidence: {result.semantic_confidence:.2f}")

    # Example 2: Ambiguous request
    print("\n[Example 2] Ambiguous request:")
    result = await translator.translate(
        "I need it done soon, but not too fast. Can you help?", language="en"
    )
    print(f"Execution allowed: {result.compiled_machine_goal.execution_allowed}")
    print(f"Requires clarification: {result.requires_clarification}")
    print(f"Ambiguities detected: {len(result.ambiguities)}")
    for amb in result.ambiguities:
        print(f"  - {amb.type.value}: severity {amb.severity:.2f}")

    # Example 3: Emotional/venting utterance
    print("\n[Example 3] Emotional utterance:")
    result = await translator.translate(
        "I'm so frustrated with this stupid error! It never works!", language="en"
    )
    print(f"Human state: {result.human_state_estimate.state_class.value}")
    print(f"Emotional intensity: {result.human_state_estimate.emotional_intensity:.2f}")
    print(f"Speech acts: {[sa.type.value for sa in result.speech_acts]}")

    print("\n" + "=" * 80)
    print("Translation layer operational.")
    print("=" * 80)

    return result


if __name__ == "__main__":
    import asyncio

    asyncio.run(demo())
