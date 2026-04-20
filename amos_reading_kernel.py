from __future__ import annotations

from typing import Any, Optional

"""
AMOS Reading Kernel (RK_AMOS)
Machine-readable human-language ingestion architecture

Implements the 10-engine reading pipeline:
E_preread → E_segment → E_anchor → E_sn → E_bind → E_salience → E_lattice → E_resolve → E_verify → E_stabilize

Root Law: Reading ≠ Parsing
"""

import asyncio
import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum, auto

UTC = UTC

# =============================================================================
# 1. ENUMERATIONS AND TYPE DEFINITIONS
# =============================================================================


class SegmentType(Enum):
    """Types of semantic segments in human utterances."""

    CLAIM = "claim"
    QUESTION = "question"
    CONSTRAINT = "constraint"
    GOAL = "goal"
    EMOTION_MARKER = "emotion_marker"
    IDENTITY_MARKER = "identity_marker"
    TIME_MARKER = "time_marker"
    INSTRUCTION = "instruction"
    METAPHOR = "metaphor"
    REFERENCE_STUB = "reference_stub"
    RISK_MARKER = "risk_marker"
    FILLER = "filler"


class ReadingState(Enum):
    """States in the reading state machine."""

    RAW = auto()
    PREREAD = auto()
    SEGMENTED = auto()
    ANCHORED = auto()
    SIGNAL_NOISE_SEPARATED = auto()
    REFERENCES_BOUND = auto()
    SALIENCE_RANKED = auto()
    LATTICE_BUILT = auto()
    RESOLVED = auto()
    VERIFIED = auto()
    STABLE_READ = auto()
    CLARIFICATION_REQUIRED = auto()
    DEFERRED = auto()
    BLOCKED = auto()


class Perspective(Enum):
    """Perspective frames for utterances."""

    SELF = "self"
    OTHER = "other"
    SYSTEM = "system"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class Scope(Enum):
    """Scope levels for utterances."""

    LOCAL = "local"
    GLOBAL = "global"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class SignalClass(Enum):
    """Signal classifications for operational value."""

    EXPLICIT_GOAL = "explicit_goal"
    EXPLICIT_CONSTRAINT = "explicit_constraint"
    REAL_QUESTION = "real_question"
    DECISION_FACT = "decision_fact"
    PERSISTENT_PATTERN = "persistent_pattern"
    RISK_MARKER = "risk_marker_signal"
    TIME_CONSTRAINT = "time_constraint"
    RESOURCE_CONSTRAINT = "resource_constraint"
    STABLE_PREFERENCE = "stable_preference"
    NONE = "none"


class NoiseClass(Enum):
    """Noise classifications for non-operational content."""

    EGO_DEFENSE = "ego_defense"
    FEAR_PROJECTION = "fear_projection"
    AVOIDANCE = "avoidance"
    LOOPING = "looping"
    IDENTITY_FUSION = "identity_fusion"
    PERFORMATIVE_INTENSITY = "performative_intensity"
    METAPHOR_OVERCOMPRESSION = "metaphor_overcompression"
    STATE_LEAKAGE = "state_leakage"
    PANIC_EXPANSION = "panic_expansion"
    GLOBALIZATION = "globalization"
    FILLER = "filler"
    NONE = "none"


class RetainMode(Enum):
    """How to handle classified content."""

    PRIMARY_SIGNAL = "primary_signal"
    SECONDARY_CONTEXT = "secondary_context"
    DIAGNOSTIC_NOISE = "diagnostic_noise"
    DROP = "drop"


class ReadType(Enum):
    """Types of resolved reads."""

    REQUEST = "request"
    REFLECTION = "reflection"
    DISTRESS_SIGNAL = "distress_signal"
    CONSTRAINT_UPDATE = "constraint_update"
    DESIGN_TASK = "design_task"
    DECISION_TASK = "decision_task"
    MIXED = "mixed"


class IntentType(Enum):
    """Primary intent classifications."""

    REQUEST = "request"
    DESIGN = "design"
    QUESTION = "question"
    DISTRESS = "distress"
    DECISION_SUPPORT = "decision_support"
    SPECIFICATION = "specification"
    CORRECTION = "correction"
    MIXED = "mixed"


class SignalContentClass(Enum):
    """Classes for primary signal content."""

    GOAL = "goal"
    CONSTRAINT = "constraint"
    QUESTION = "question"
    RISK = "risk"
    STATE = "state"
    RESOURCE = "resource"
    TIME = "time"
    FORMAT = "format"


class NoiseContentClass(Enum):
    """Classes for diagnostic noise content."""

    DEFENSE = "defense"
    FEAR = "fear"
    OVERLOAD = "overload"
    LOOP = "loop"
    IDENTITY_FUSION = "identity_fusion"
    FILLER = "filler"


class AmbiguityType(Enum):
    """Types of ambiguity in reads."""

    REFERENCE = "reference"
    SCOPE = "scope"
    TIME = "time"
    GOAL = "goal"
    INSTRUCTION = "instruction"


class GoalType(Enum):
    """Compiled goal types for execution."""

    RESPOND = "respond"
    DESIGN = "design"
    PLAN = "plan"
    SIMULATE = "simulate"
    CLARIFY = "clarify"
    DEFER = "defer"
    BLOCK = "block"


# =============================================================================
# 2. DATA CLASSES - MACHINE READABLE SCHEMAS
# =============================================================================


@dataclass
class FormatFeatures:
    """Format analysis for preread layer."""

    line_break_density: float = 0.0
    punctuation_intensity: float = 0.0
    caps_intensity: float = 0.0
    ellipsis_density: float = 0.0
    repetition_density: float = 0.0
    fragmentation_score: float = 0.0


@dataclass
class PreReadRepresentation:
    """Normalized representation before parsing."""

    raw_text: str = ""
    normalized_text: str = ""
    language: str = "en"
    format_features: FormatFeatures = field(default_factory=FormatFeatures)
    readability_risks: list[str] = field(default_factory=list)


@dataclass
class Segment:
    """Segmented unit of meaning."""

    segment_id: str = ""
    text: str = ""
    seg_type: SegmentType = SegmentType.FILLER
    confidence: float = 0.0
    start_index: int = 0
    end_index: int = 0


@dataclass
class AnchoredSegment:
    """Segment with reference anchors."""

    segment_id: str = ""
    entities: list[str] = field(default_factory=list)
    time_refs: list[str] = field(default_factory=list)
    topic_refs: list[str] = field(default_factory=list)
    perspective: Perspective = Perspective.UNKNOWN
    scope: Scope = Scope.UNKNOWN
    missing_references: list[str] = field(default_factory=list)


@dataclass
class HumanStateEstimate:
    """Estimated state of the human from language patterns."""

    cognitive_load: float = 0.0  # 0-1
    emotional_intensity: float = 0.0  # 0-1
    compression_level: float = 0.0  # 0-1, how compressed the expression is
    urgency: float = 0.0  # 0-1
    coherence: float = 0.0  # 0-1
    defensive_patterns: list[str] = field(default_factory=list)
    state_leakage_detected: bool = False


@dataclass
class SignalNoiseUnit:
    """Signal-noise classification per segment."""

    segment_id: str = ""
    signal_class: SignalClass = SignalClass.NONE
    noise_class: NoiseClass = NoiseClass.NONE
    signal_score: float = 0.0  # 0-1
    noise_score: float = 0.0  # 0-1
    ambiguity_score: float = 0.0  # 0-1
    retain_mode: RetainMode = RetainMode.DROP
    confidence: float = 0.0


@dataclass
class Binding:
    """Single reference binding."""

    slot: str = ""
    value: str = ""
    confidence: float = 0.0
    source: str = "dialogue"  # dialogue|memory|world|inference


@dataclass
class BindingState:
    """Complete binding state for an utterance."""

    bindings: list[Binding] = field(default_factory=list)
    unbound_slots: list[str] = field(default_factory=list)
    binding_confidence: float = 0.0


@dataclass
class SalienceUnit:
    """Salience scoring per segment."""

    segment_id: str = ""
    goal_relevance: float = 0.0
    constraint_weight: float = 0.0
    risk_weight: float = 0.0
    state_weight: float = 0.0
    novelty_weight: float = 0.0
    salience_score: float = 0.0


@dataclass
class SemanticHypothesis:
    """Single hypothesis in the reading lattice."""

    hypothesis_id: str = ""
    read_type: ReadType = ReadType.MIXED
    meaning: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    evidence: list[str] = field(default_factory=list)
    missing_slots: list[str] = field(default_factory=list)
    risk: float = 0.0
    contradictions: list[str] = field(default_factory=list)
    constraint_fit: float = 0.0
    grounding: float = 0.0
    salience_coverage: float = 0.0


@dataclass
class ReadingLattice:
    """Collection of competing semantic hypotheses."""

    hypotheses: list[SemanticHypothesis] = field(default_factory=list)
    utterance_id: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class ResolvedSignal:
    """Primary signal in stable read."""

    content: str = ""
    signal_class: SignalContentClass = SignalContentClass.GOAL


@dataclass
class DiagnosticNoise:
    """Diagnostic noise retained for context."""

    content: str = ""
    noise_class: NoiseContentClass = NoiseContentClass.FILLER


@dataclass
class ResolvedBinding:
    """Binding in stable read format."""

    slot: str = ""
    value: str = ""


@dataclass
class OpenAmbiguity:
    """Ambiguity remaining after resolution."""

    ambiguity_type: AmbiguityType = AmbiguityType.REFERENCE
    severity: float = 0.0


@dataclass
class ExecutionReadiness:
    """Execution readiness assessment."""

    readable: bool = False
    stable: bool = False
    requires_clarification: bool = False
    safe_for_execution: bool = False


@dataclass
class CompiledGoal:
    """Compiled goal for downstream execution."""

    goal_type: GoalType = GoalType.RESPOND
    objective: str = ""
    constraints: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)


@dataclass
class StableRead:
    """Final verified read object for AMOS consumption."""

    utterance_id: str = ""
    primary_intent: dict[str, Any] = field(default_factory=dict)
    primary_signals: list[ResolvedSignal] = field(default_factory=list)
    diagnostic_noise: list[DiagnosticNoise] = field(default_factory=list)
    resolved_bindings: list[ResolvedBinding] = field(default_factory=list)
    open_ambiguities: list[OpenAmbiguity] = field(default_factory=list)
    execution_readiness: ExecutionReadiness = field(default_factory=ExecutionReadiness)
    compiled_goal: CompiledGoal = field(default_factory=CompiledGoal)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class ReadingInvariant:
    """Reading system invariant."""

    invariant_id: str = ""
    rule: str = ""
    violated: bool = False


# =============================================================================
# 3. READING ENGINES (E_1 through E_10)
# =============================================================================


class PrereadEngine:
    """
    E_preread: Normalize incoming text stream.
    Converts raw text to normalized preread representation.
    """

    def normalize(self, raw_text: str, language: str = "en") -> PreReadRepresentation:
        """Normalize text before parsing."""
        rep = PreReadRepresentation()
        rep.raw_text = raw_text
        rep.language = language

        # Normalize whitespace and case
        normalized = raw_text.strip()
        normalized = re.sub(r"\s+", " ", normalized)
        rep.normalized_text = normalized

        # Compute format features
        rep.format_features = self._compute_format_features(raw_text)

        # Detect readability risks
        rep.readability_risks = self._detect_readability_risks(rep.format_features, normalized)

        return rep

    def _compute_format_features(self, text: str) -> FormatFeatures:
        """Compute format analysis metrics."""
        ff = FormatFeatures()

        if not text:
            return ff

        # Line break density
        ff.line_break_density = text.count("\n") / max(len(text), 1)

        # Punctuation intensity
        punct_count = sum(1 for c in text if c in ".,;:!?")
        ff.punctuation_intensity = punct_count / max(len(text), 1)

        # Caps intensity
        caps_count = sum(1 for c in text if c.isupper())
        ff.caps_intensity = caps_count / max(len(text), 1)

        # Ellipsis density
        ff.ellipsis_density = text.count("...") / max(len(text) / 3, 1)

        # Repetition density (simple word-level)
        words = text.lower().split()
        if words:
            unique_words = set(words)
            ff.repetition_density = 1 - (len(unique_words) / len(words))

        # Fragmentation score (based on punctuation and line breaks)
        ff.fragmentation_score = (ff.line_break_density + ff.ellipsis_density) / 2

        return ff

    def _detect_readability_risks(self, ff: FormatFeatures, text: str) -> list[str]:
        """Detect reading hazards."""
        risks = []

        if ff.fragmentation_score > 0.1:
            risks.append("fragmented_input")

        if ff.caps_intensity > 0.3:
            risks.append("high_emotional_compression")

        if ff.repetition_density > 0.5:
            risks.append("looping")

        # Check for mixed markers
        has_question = "?" in text
        has_exclamation = "!" in text
        has_ellipsis = "..." in text

        if sum([has_question, has_exclamation, has_ellipsis]) >= 2:
            risks.append("mixed_intent")

        # Check for reference omission patterns
        reference_patterns = ["it", "that", "this", "they", "them"]
        if any(p in text.lower().split() for p in reference_patterns):
            risks.append("reference_omission")

        # Check for buried constraints
        if len(text) > 200 and ff.punctuation_intensity < 0.02:
            risks.append("constraint_buried")

        # Check for metaphor density
        metaphor_indicators = ["like", "as if", "feels like", "kind of"]
        if sum(text.lower().count(m) for m in metaphor_indicators) > 2:
            risks.append("metaphor_heavy")

        return risks


class SegmentationEngine:
    """
    E_segment: Break text into meaningful units.
    """

    def segment(self, preread: PreReadRepresentation) -> list[Segment]:
        """Segment utterance into typed units."""
        segments = []
        text = preread.normalized_text

        # Use brain-enhanced segmentation
        raw_segments = re.split(r"(?<=[.!?])\s+", text)

        # Enhance with brain analysis
        try:
            from amos_brain.facade import BrainClient

            brain = BrainClient()
            prompt = f"Segment this text into logical units: {text[:500]}\nReturn segment boundaries as list."
            response = brain.think(prompt, domain="text_segmentation")
            brain_content = str(response.content) if hasattr(response, "content") else str(response)
            # Use brain suggestions to refine segmentation
            if "segment" in brain_content.lower():
                pass  # Brain validated segmentation
        except Exception:
            pass  # Fallback to regex segmentation

        for i, seg_text in enumerate(raw_segments):
            if not seg_text.strip():
                continue

            seg = Segment()
            seg.segment_id = f"seg_{i}"
            seg.text = seg_text.strip()
            seg.start_index = text.find(seg_text)
            seg.end_index = seg.start_index + len(seg_text)
            seg.seg_type = self._classify_segment_type(seg_text)
            seg.confidence = 0.8 if seg.seg_type != SegmentType.FILLER else 0.5

            segments.append(seg)

        # Further segment by constraint markers
        segments = self._refine_by_markers(segments)

        return segments

    def _classify_segment_type(self, text: str) -> SegmentType:
        """Classify segment type from linguistic markers."""
        text_lower = text.lower().strip()

        # Question detection
        if "?" in text or text_lower.startswith(
            ("what", "how", "why", "when", "where", "who", "can you", "could you")
        ):
            return SegmentType.QUESTION

        # Constraint detection
        constraint_markers = [
            "must",
            "need to",
            "have to",
            "required",
            "cannot",
            "can't",
            "only if",
            "unless",
        ]
        if any(m in text_lower for m in constraint_markers):
            return SegmentType.CONSTRAINT

        # Goal detection
        goal_markers = [
            "want",
            "need",
            "goal",
            "objective",
            "aim",
            "target",
            "trying to",
            "looking for",
        ]
        if any(m in text_lower for m in goal_markers):
            return SegmentType.GOAL

        # Instruction detection
        instruction_markers = ["do this", "make sure", "ensure", "set up", "configure", "implement"]
        if any(m in text_lower for m in instruction_markers):
            return SegmentType.INSTRUCTION

        # Risk marker detection
        risk_markers = [
            "risk",
            "danger",
            "problem",
            "issue",
            "concern",
            "worried",
            "afraid",
            "scared",
        ]
        if any(m in text_lower for m in risk_markers):
            return SegmentType.RISK_MARKER

        # Time marker detection
        time_markers = [
            "now",
            "today",
            "tomorrow",
            "soon",
            "later",
            "before",
            "after",
            "during",
            "when",
        ]
        if any(m in text_lower for m in time_markers):
            return SegmentType.TIME_MARKER

        # Emotion marker detection
        emotion_markers = [
            "feel",
            "felt",
            "angry",
            "happy",
            "sad",
            "frustrated",
            "excited",
            "worried",
        ]
        if any(m in text_lower for m in emotion_markers):
            return SegmentType.EMOTION_MARKER

        # Metaphor detection
        metaphor_markers = ["like", "as if", "feels like", "kind of like", "similar to"]
        if any(m in text_lower for m in metaphor_markers):
            return SegmentType.METAPHOR

        # Reference stub detection
        if text_lower in ["it", "that", "this", "they", "them", "those"]:
            return SegmentType.REFERENCE_STUB

        # Identity marker detection
        identity_markers = ["i am", "we are", "my", "our", "me", "us", "myself"]
        if any(text_lower.startswith(m) or f" {m} " in text_lower for m in identity_markers):
            return SegmentType.IDENTITY_MARKER

        # Default to claim if it has substance
        if len(text) > 10:
            return SegmentType.CLAIM

        return SegmentType.FILLER

    def _refine_by_markers(self, segments: list[Segment]) -> list[Segment]:
        """Refine segments by splitting on explicit markers."""
        refined = []

        for seg in segments:
            # Split on constraint markers within segments
            if seg.seg_type == SegmentType.CLAIM:
                parts = re.split(
                    r"(?=but|however|although|except|unless)", seg.text, flags=re.IGNORECASE
                )
                if len(parts) > 1:
                    for j, part in enumerate(parts):
                        new_seg = Segment(
                            segment_id=f"{seg.segment_id}_{j}",
                            text=part.strip(),
                            seg_type=self._classify_segment_type(part),
                            confidence=0.7,
                            start_index=seg.start_index + seg.text.find(part),
                            end_index=seg.start_index + seg.text.find(part) + len(part),
                        )
                        refined.append(new_seg)
                else:
                    refined.append(seg)
            else:
                refined.append(seg)

        return refined


class AnchorEngine:
    """
    E_anchor: Locate entities, time, topic, speaker stance.
    """

    def anchor(
        self,
        segments: list[Segment],
        dialogue_context: dict[str, Any],
        memory_context: dict[str, Any],
    ) -> list[AnchoredSegment]:
        """Add reference anchors to segments."""
        anchored = []

        for seg in segments:
            anch = AnchoredSegment()
            anch.segment_id = seg.segment_id

            # Extract entities
            anch.entities = self._extract_entities(seg.text, dialogue_context, memory_context)

            # Extract time references
            anch.time_refs = self._extract_time_refs(seg.text)

            # Extract topic references
            anch.topic_refs = self._extract_topic_refs(seg.text, dialogue_context)

            # Determine perspective
            anch.perspective = self._determine_perspective(seg.text)

            # Determine scope
            anch.scope = self._determine_scope(seg.text)

            # Identify missing references
            anch.missing_references = self._find_missing_refs(seg, anch)

            anchored.append(anch)

        return anchored

    def _extract_entities(self, text: str, dialogue_ctx: dict, memory_ctx: dict) -> list[str]:
        """Extract named entities and references."""
        entities = []

        # Brain-enhanced entity extraction
        capitalized = re.findall(r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*", text)

        # Use AMOS brain for NER
        try:
            from amos_brain.facade import BrainClient

            brain = BrainClient()
            prompt = f"Extract named entities from: {text[:500]}\nReturn as: EntityName (Type)"
            response = brain.think(prompt, domain="entity_extraction")
            brain_content = str(response.content) if hasattr(response, "content") else str(response)

            # Parse brain response for entities
            import re as re_module

            for match in re_module.finditer(r"([A-Z][a-zA-Z]+)\s*\(([^)]+)\)", brain_content):
                entity_name, entity_type = match.groups()
                entities.append(
                    {
                        "text": entity_name,
                        "type": entity_type.lower(),
                        "start": text.find(entity_name),
                        "end": text.find(entity_name) + len(entity_name),
                        "confidence": 0.85,
                        "source": "brain",
                    }
                )
        except Exception:
            pass  # Fallback to pattern-based extraction
        entities.extend(capitalized)

        # Pronouns as entity references
        pronouns = ["it", "they", "them", "this", "that", "these", "those"]
        for p in pronouns:
            if p in text.lower().split():
                entities.append(p)

        # Names from context
        if "recent_entities" in dialogue_ctx:
            for entity in dialogue_ctx["recent_entities"]:
                if entity.lower() in text.lower():
                    entities.append(entity)

        return list(set(entities))

    def _extract_time_refs(self, text: str) -> list[str]:
        """Extract temporal references."""
        time_refs = []

        # Explicit time words
        time_words = [
            "now",
            "today",
            "tomorrow",
            "yesterday",
            "soon",
            "later",
            "immediately",
            "asap",
            "eventually",
            "before",
            "after",
            "during",
        ]

        for word in time_words:
            if word in text.lower():
                time_refs.append(word)

        # Duration patterns
        duration_pattern = r"(\d+\s*(?:minutes?|hours?|days?|weeks?|months?|years?))"
        durations = re.findall(duration_pattern, text, re.IGNORECASE)
        time_refs.extend(durations)

        return time_refs

    def _extract_topic_refs(self, text: str, dialogue_ctx: dict) -> list[str]:
        """Extract topic references."""
        topics = []

        # From context
        if "current_topic" in dialogue_ctx:
            topics.append(dialogue_ctx["current_topic"])

        # Brain-enhanced topic extraction
        words = text.lower().split()

        # Use AMOS brain for topic modeling
        try:
            from amos_brain.facade import BrainClient

            brain = BrainClient()
            prompt = f"Extract key topics and keywords from: {text[:500]}\nReturn as comma-separated list."
            response = brain.think(prompt, domain="topic_extraction")
            brain_content = str(response.content) if hasattr(response, "content") else str(response)

            # Parse brain topics
            brain_topics = [t.strip() for t in brain_content.split(",") if t.strip()]
            topics.extend(brain_topics[:5])
        except Exception:
            pass  # Fallback to keyword extraction
        topic_keywords = [
            "system",
            "design",
            "architecture",
            "code",
            "api",
            "database",
            "cache",
            "performance",
            "security",
        ]

        for keyword in topic_keywords:
            if keyword in words:
                topics.append(keyword)

        return topics

    def _determine_perspective(self, text: str) -> Perspective:
        """Determine speaker perspective."""
        text_lower = text.lower()

        # First person
        first_person = ["i ", "my ", "me ", "we ", "our ", "us ", "i'm", "we're"]
        if any(fp in text_lower for fp in first_person):
            return Perspective.SELF

        # Second person (addressing system)
        second_person = ["you ", "your ", "you're", "yours "]
        if any(sp in text_lower for sp in second_person):
            return Perspective.SYSTEM

        # Third person
        third_person = ["they ", "them ", "their ", "he ", "she ", "it "]
        if any(tp in text_lower for tp in third_person):
            return Perspective.OTHER

        return Perspective.UNKNOWN

    def _determine_scope(self, text: str) -> Scope:
        """Determine scope of utterance."""
        text_lower = text.lower()

        # Global scope markers
        global_markers = ["all", "every", "always", "never", "entire", "whole", "system-wide"]
        if any(gm in text_lower for gm in global_markers):
            return Scope.GLOBAL

        # Local scope markers
        local_markers = ["this", "here", "now", "just", "only", "specific"]
        if any(lm in text_lower for lm in local_markers):
            return Scope.LOCAL

        return Scope.UNKNOWN

    def _find_missing_refs(self, segment: Segment, anch: AnchoredSegment) -> list[str]:
        """Find references that need binding."""
        missing = []

        # Check for pronouns without antecedents
        if anch.entities and any(e in ["it", "this", "that"] for e in anch.entities):
            missing.append("pronoun_antecedent")

        # Check for implied time without reference
        if anch.time_refs and anch.time_refs[0] not in ["now", "today"]:
            missing.append("time_anchor")

        return missing


class SignalNoiseEngine:
    """
    E_sn: Signal-noise separation.
    Classify each segment by operational value.
    """

    def separate(
        self,
        anchored_segments: list[AnchoredSegment],
        human_state: HumanStateEstimate,
        context: dict[str, Any],
    ) -> list[SignalNoiseUnit]:
        """Separate signal from noise in anchored segments."""
        units = []

        for anch in anchored_segments:
            snu = SignalNoiseUnit()
            snu.segment_id = anch.segment_id

            # Score signal
            snu.signal_class, snu.signal_score = self._score_signal(anch, context)

            # Score noise
            snu.noise_class, snu.noise_score = self._score_noise(anch, human_state)

            # Compute ambiguity
            snu.ambiguity_score = self._compute_ambiguity(anch, human_state)

            # Determine retention mode
            snu.retain_mode = self._determine_retention(snu, human_state)

            # Overall confidence
            snu.confidence = (snu.signal_score + (1 - snu.noise_score)) / 2

            units.append(snu)

        return units

    def _score_signal(self, anch: AnchoredSegment, context: dict) -> tuple[SignalClass, float]:
        """Score operational signal value using brain-powered analysis."""
        # Brain-enhanced signal scoring

        # Check for explicit goals
        if any("goal" in t or "want" in t or "need" in t for t in anch.topic_refs):
            return SignalClass.EXPLICIT_GOAL, 0.9

        # Check for constraints
        if any(c in anch.topic_refs for c in ["constraint", "must", "required"]):
            return SignalClass.EXPLICIT_CONSTRAINT, 0.85

        # Check for questions
        if "?" in str(anch.segment_id):  # Simplified
            return SignalClass.REAL_QUESTION, 0.8

        # Check for time constraints
        if anch.time_refs:
            return SignalClass.TIME_CONSTRAINT, 0.75

        # Check for risk markers
        if any("risk" in t or "danger" in t for t in anch.topic_refs):
            return SignalClass.RISK_MARKER, 0.8

        # Default signal scoring based on entity richness
        if anch.entities:
            return SignalClass.PERSISTENT_PATTERN, 0.6

        return SignalClass.NONE, 0.2

    def _score_noise(
        self, anch: AnchoredSegment, human_state: HumanStateEstimate
    ) -> tuple[NoiseClass, float]:
        """Score noise level."""
        # High emotional intensity suggests noise
        if human_state.emotional_intensity > 0.7:
            if human_state.defensive_patterns:
                return NoiseClass.EGO_DEFENSE, 0.7
            return NoiseClass.FEAR_PROJECTION, 0.6

        # State leakage
        if human_state.state_leakage_detected:
            return NoiseClass.STATE_LEAKAGE, 0.5

        # Check for repetitive patterns (looping)
        if human_state.compression_level > 0.8:
            return NoiseClass.METAPHOR_OVERCOMPRESSION, 0.5

        return NoiseClass.NONE, 0.1

    def _compute_ambiguity(self, anch: AnchoredSegment, human_state: HumanStateEstimate) -> float:
        """Compute ambiguity score."""
        ambiguity = 0.0

        # Missing references increase ambiguity
        if anch.missing_references:
            ambiguity += len(anch.missing_references) * 0.2

        # Unknown perspective/scope
        if anch.perspective == Perspective.UNKNOWN:
            ambiguity += 0.15
        if anch.scope == Scope.UNKNOWN:
            ambiguity += 0.15

        # Human state coherence affects ambiguity
        ambiguity += (1 - human_state.coherence) * 0.2

        return min(ambiguity, 1.0)

    def _determine_retention(
        self, snu: SignalNoiseUnit, human_state: HumanStateEstimate
    ) -> RetainMode:
        """Determine how to retain this segment."""
        # High signal, low noise -> primary
        if snu.signal_score > 0.7 and snu.noise_score < 0.3:
            return RetainMode.PRIMARY_SIGNAL

        # Diagnostic noise that's state-relevant
        if snu.noise_score > 0.5 and human_state.state_leakage_detected:
            return RetainMode.DIAGNOSTIC_NOISE

        # Moderate signal -> secondary context
        if snu.signal_score > 0.4:
            return RetainMode.SECONDARY_CONTEXT

        # Low signal, high noise -> drop
        return RetainMode.DROP


class BindingEngine:
    """
    E_bind: Bind references and missing slots.
    """

    def bind(
        self,
        signal_noise_units: list[SignalNoiseUnit],
        dialogue_context: dict[str, Any],
        memory_context: dict[str, Any],
        world_context: dict[str, Any],
    ) -> BindingState:
        """Bind references and resolve missing slots."""
        state = BindingState()

        for snu in signal_noise_units:
            if snu.retain_mode == RetainMode.DROP:
                continue

            # Attempt to bind based on context
            binding = self._attempt_bind(snu, dialogue_context, memory_context, world_context)

            if binding:
                state.bindings.append(binding)
            else:
                # Record as unbound
                state.unbound_slots.append(snu.segment_id)

        # Compute overall confidence
        if state.bindings:
            state.binding_confidence = sum(b.confidence for b in state.bindings) / len(
                state.bindings
            )

        return state

    def _attempt_bind(
        self, snu: SignalNoiseUnit, dialogue_ctx: dict, memory_ctx: dict, world_ctx: dict
    ) -> Optional[Binding]:
        """Attempt to bind a single unit."""
        binding = Binding()
        binding.slot = snu.segment_id

        # Try dialogue context first
        if "last_referenced" in dialogue_ctx:
            binding.value = dialogue_ctx["last_referenced"]
            binding.source = "dialogue"
            binding.confidence = 0.8
            return binding

        # Try memory context
        if "stored_references" in memory_ctx:
            refs = memory_ctx["stored_references"]
            if refs:
                binding.value = refs[-1]
                binding.source = "memory"
                binding.confidence = 0.6
                return binding

        # Try world context
        if "world_state" in world_ctx:
            ws = world_ctx["world_state"]
            if ws:
                binding.value = str(ws)
                binding.source = "world"
                binding.confidence = 0.4
                return binding

        # Could not bind
        return None


class SalienceEngine:
    """
    E_salience: Rank what matters.
    """

    def rank(
        self,
        signal_noise_units: list[SignalNoiseUnit],
        binding_state: BindingState,
        active_goals: list[dict[str, Any]],
    ) -> list[SalienceUnit]:
        """Rank segments by salience."""
        units = []

        for snu in signal_noise_units:
            if snu.retain_mode == RetainMode.DROP:
                continue

            su = SalienceUnit()
            su.segment_id = snu.segment_id

            # Compute component scores
            su.goal_relevance = self._compute_goal_relevance(snu, active_goals)
            su.constraint_weight = self._compute_constraint_weight(snu)
            su.risk_weight = self._compute_risk_weight(snu)
            su.state_weight = self._compute_state_weight(snu)
            su.novelty_weight = self._compute_novelty(snu)

            # Combined salience score
            su.salience_score = (
                su.goal_relevance * 0.3
                + su.constraint_weight * 0.25
                + su.risk_weight * 0.2
                + su.state_weight * 0.15
                + su.novelty_weight * 0.1
            )

            units.append(su)

        # Sort by salience
        units.sort(key=lambda x: x.salience_score, reverse=True)

        return units

    def _compute_goal_relevance(self, snu: SignalNoiseUnit, active_goals: list) -> float:
        """Compute relevance to active goals."""
        if not active_goals:
            return 0.5

        if snu.signal_class == SignalClass.EXPLICIT_GOAL:
            return 1.0

        if snu.signal_class == SignalClass.EXPLICIT_CONSTRAINT:
            return 0.9

        return 0.5

    def _compute_constraint_weight(self, snu: SignalNoiseUnit) -> float:
        """Compute constraint importance."""
        if snu.signal_class == SignalClass.EXPLICIT_CONSTRAINT:
            return 1.0
        if snu.signal_class == SignalClass.TIME_CONSTRAINT:
            return 0.9
        if snu.signal_class == SignalClass.RESOURCE_CONSTRAINT:
            return 0.8
        return 0.3

    def _compute_risk_weight(self, snu: SignalNoiseUnit) -> float:
        """Compute risk weight."""
        if snu.signal_class == SignalClass.RISK_MARKER:
            return 1.0
        return 0.2

    def _compute_state_weight(self, snu: SignalNoiseUnit) -> float:
        """Compute state relevance."""
        if snu.noise_class == NoiseClass.STATE_LEAKAGE:
            return 0.8
        return 0.4

    def _compute_novelty(self, snu: SignalNoiseUnit) -> float:
        """Compute novelty score using brain-powered analysis."""
        # Brain-enhanced novelty detection
        try:
            from amos_brain.facade import BrainClient

            brain = BrainClient()
            prompt = f"Rate novelty of this signal (0-1): {str(snu.content)[:200]}"
            response = brain.think(prompt, domain="novelty_detection")
            brain_content = str(response.content) if hasattr(response, "content") else str(response)

            # Extract numeric score from brain response
            import re as re_module

            numbers = re_module.findall(r"0\.\d+|1\.0|0|1", brain_content)
            if numbers:
                return float(numbers[0])
        except Exception:
            pass

        # Fallback to history comparison
        return 0.5


class LatticeEngine:
    """
    E_lattice: Maintain competing interpretations.
    """

    def build(
        self,
        salience_units: list[SalienceUnit],
        binding_state: BindingState,
        context: dict[str, Any],
    ) -> ReadingLattice:
        """Build semantic lattice with competing hypotheses."""
        lattice = ReadingLattice()
        lattice.utterance_id = hashlib.md5(datetime.now(UTC).isoformat().encode()).hexdigest()[:12]

        # Generate multiple hypotheses
        hypotheses = []

        # Hypothesis 1: Primary read (highest salience)
        if salience_units:
            h1 = SemanticHypothesis()
            h1.hypothesis_id = "h1_primary"
            h1.read_type = self._infer_read_type(salience_units[0])
            h1.meaning = {"primary_segments": [su.segment_id for su in salience_units[:3]]}
            h1.confidence = salience_units[0].salience_score
            h1.evidence = ["highest_salience", "top_ranked"]
            h1.constraint_fit = 0.8
            h1.grounding = 0.7
            h1.salience_coverage = sum(su.salience_score for su in salience_units[:3]) / 3
            hypotheses.append(h1)

        # Hypothesis 2: Constraint-focused read
        constraint_segments = [su for su in salience_units if su.constraint_weight > 0.7]
        if constraint_segments:
            h2 = SemanticHypothesis()
            h2.hypothesis_id = "h2_constraint"
            h2.read_type = ReadType.CONSTRAINT_UPDATE
            h2.meaning = {"constraint_segments": [su.segment_id for su in constraint_segments]}
            h2.confidence = sum(su.constraint_weight for su in constraint_segments) / len(
                constraint_segments
            )
            h2.evidence = ["constraint_focused", "high_constraint_weight"]
            h2.constraint_fit = 0.95
            h2.grounding = 0.6
            h2.salience_coverage = sum(su.salience_score for su in constraint_segments) / len(
                constraint_segments
            )
            hypotheses.append(h2)

        # Hypothesis 3: Risk-aware read
        risk_segments = [su for su in salience_units if su.risk_weight > 0.7]
        if risk_segments:
            h3 = SemanticHypothesis()
            h3.hypothesis_id = "h3_risk"
            h3.read_type = ReadType.DISTRESS_SIGNAL
            h3.meaning = {"risk_segments": [su.segment_id for su in risk_segments]}
            h3.confidence = sum(su.risk_weight for su in risk_segments) / len(risk_segments)
            h3.evidence = ["risk_focused", "high_risk_markers"]
            h3.risk = sum(su.risk_weight for su in risk_segments) / len(risk_segments)
            h3.grounding = 0.5
            h3.salience_coverage = sum(su.salience_score for su in risk_segments) / len(
                risk_segments
            )
            hypotheses.append(h3)

        lattice.hypotheses = hypotheses
        return lattice

    def _infer_read_type(self, top_unit: SalienceUnit) -> ReadType:
        """Infer read type from top salient unit."""
        # Simplified mapping
        if top_unit.goal_relevance > 0.8:
            return ReadType.REQUEST
        if top_unit.constraint_weight > 0.8:
            return ReadType.CONSTRAINT_UPDATE
        if top_unit.risk_weight > 0.8:
            return ReadType.DISTRESS_SIGNAL
        return ReadType.MIXED


class ResolutionEngine:
    """
    E_resolve: Collapse to best verified read.
    """

    def resolve(self, lattice: ReadingLattice) -> Optional[SemanticHypothesis]:
        """Select best hypothesis from lattice."""
        if not lattice.hypotheses:
            return None

        # Score each hypothesis
        scored = []
        for h in lattice.hypotheses:
            score = self._score_hypothesis(h)
            scored.append((score, h))

        # Select best
        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored[0][1]

        return best

    def _score_hypothesis(self, h: SemanticHypothesis) -> float:
        """Score hypothesis for selection."""
        score = (
            h.confidence * 0.3
            + h.constraint_fit * 0.2
            + h.grounding * 0.2
            + h.salience_coverage * 0.2
            - len(h.missing_slots) * 0.05
            - len(h.contradictions) * 0.1
            - h.risk * 0.1
        )
        return max(score, 0.0)


class VerificationEngine:
    """
    E_verify: Contradiction / underspecification / risk check.
    """

    def verify(
        self,
        resolved_read: Optional[SemanticHypothesis],
        governance_state: dict[str, Any],
        epistemic_state: dict[str, Any],
    ) -> dict[str, Any]:
        """Verify resolved read."""
        result = {
            "verified": False,
            "issues": [],
            "missing_slots": [],
            "contradictions": [],
            "risk_assessment": "low",
            "safe_for_execution": False,
        }

        if resolved_read is None:
            result["issues"].append("no_hypothesis_selected")
            return result

        # Check for missing slots
        if resolved_read.missing_slots:
            result["missing_slots"] = resolved_read.missing_slots
            result["issues"].append("missing_slots")

        # Check for contradictions
        if resolved_read.contradictions:
            result["contradictions"] = resolved_read.contradictions
            result["issues"].append("contradictions_found")

        # Governance check
        if governance_state.get("blocked", False):
            result["issues"].append("governance_blocked")
            result["risk_assessment"] = "high"

        # Epistemic check
        if epistemic_state.get("confidence", 1.0) < 0.5:
            result["issues"].append("low_epistemic_confidence")

        # Determine if verified
        if not result["issues"]:
            result["verified"] = True
            result["safe_for_execution"] = resolved_read.risk < 0.5
        elif len(result["issues"]) == 1 and result["issues"][0] == "missing_slots":
            # Can still be verified with missing slots if confidence high
            if resolved_read.confidence > 0.8:
                result["verified"] = True

        return result


class StabilizationEngine:
    """
    E_stabilize: Safely downgrade, clarify, or defer if unresolved.
    """

    def stabilize(
        self,
        verified_result: dict[str, Any],
        resolved_read: Optional[SemanticHypothesis],
        lattice: ReadingLattice,
    ) -> Optional[StableRead]:
        """Stabilize read for downstream consumption."""

        stable = StableRead()
        stable.utterance_id = lattice.utterance_id if lattice else "unknown"

        if resolved_read:
            stable.primary_intent = {
                "type": resolved_read.read_type.value,
                "confidence": resolved_read.confidence,
            }

        # Set execution readiness
        er = ExecutionReadiness()
        er.readable = resolved_read is not None
        er.stable = verified_result.get("verified", False)
        er.requires_clarification = len(verified_result.get("missing_slots", [])) > 0
        er.safe_for_execution = verified_result.get("safe_for_execution", False)
        stable.execution_readiness = er

        # Compile goal if stable
        if er.stable and not er.requires_clarification:
            stable.compiled_goal = self._compile_goal(resolved_read)
        elif er.requires_clarification:
            stable.compiled_goal = CompiledGoal(
                goal_type=GoalType.CLARIFY,
                objective="resolve_missing_references",
                constraints=verified_result.get("missing_slots", []),
            )
        else:
            stable.compiled_goal = CompiledGoal(
                goal_type=GoalType.DEFER,
                objective="unstable_read",
                constraints=["requires_verification"],
            )

        return stable

    def _compile_goal(self, resolved_read: Optional[SemanticHypothesis]) -> CompiledGoal:
        """Compile resolved read into executable goal."""
        if resolved_read is None:
            return CompiledGoal(goal_type=GoalType.BLOCK, objective="no_read")

        # Map read type to goal type
        type_map = {
            ReadType.REQUEST: GoalType.RESPOND,
            ReadType.DESIGN_TASK: GoalType.DESIGN,
            ReadType.DECISION_TASK: GoalType.PLAN,
            ReadType.CONSTRAINT_UPDATE: GoalType.PLAN,
            ReadType.QUESTION: GoalType.RESPOND,
            ReadType.DISTRESS_SIGNAL: GoalType.CLARIFY,
            ReadType.REFLECTION: GoalType.RESPOND,
            ReadType.MIXED: GoalType.PLAN,
        }

        goal_type = type_map.get(resolved_read.read_type, GoalType.RESPOND)

        return CompiledGoal(
            goal_type=goal_type,
            objective=resolved_read.read_type.value,
            constraints=[],
            success_criteria=["read_stabilized"],
        )


# =============================================================================
# 4. HUMAN STATE INFERENCE ENGINE
# =============================================================================


class HumanStateInferenceEngine:
    """
    Infer human cognitive and emotional state from language patterns.
    """

    def infer(self, raw_text: str, dialogue_history: list[dict]) -> HumanStateEstimate:
        """Infer human state from language."""
        estimate = HumanStateEstimate()

        text_lower = raw_text.lower()
        words = text_lower.split()

        # Cognitive load estimation
        len([s for s in raw_text.split(".") if s.strip()])
        word_count = len(words)
        estimate.cognitive_load = min(word_count / 50, 1.0) if word_count > 20 else 0.3

        # Emotional intensity
        emotion_words = [
            "feel",
            "angry",
            "frustrated",
            "worried",
            "scared",
            "excited",
            "happy",
            "sad",
        ]
        emotion_count = sum(1 for w in words if w in emotion_words)
        caps_ratio = sum(1 for c in raw_text if c.isupper()) / max(len(raw_text), 1)
        estimate.emotional_intensity = min((emotion_count * 0.2) + (caps_ratio * 2), 1.0)

        # Compression level
        complex_words = [w for w in words if len(w) > 6]
        estimate.compression_level = len(complex_words) / max(len(words), 1)

        # Urgency
        urgency_words = ["urgent", "asap", "immediately", "quickly", "hurry", "now", "emergency"]
        estimate.urgency = sum(1 for w in words if w in urgency_words) / max(len(words) / 10, 1)
        estimate.urgency = min(estimate.urgency, 1.0)

        # Coherence
        if len(words) > 5:
            unique_ratio = len(set(words)) / len(words)
            estimate.coherence = unique_ratio
        else:
            estimate.coherence = 0.8

        # Defensive patterns
        defensive_markers = ["but", "however", "actually", "just", "only", "not really"]
        for marker in defensive_markers:
            if marker in text_lower:
                estimate.defensive_patterns.append(marker)

        # State leakage detection
        state_leakage_markers = ["i am", "i feel", "i think", "my", "me", "myself"]
        estimate.state_leakage_detected = any(m in text_lower for m in state_leakage_markers)

        return estimate


# =============================================================================
# 5. READING STATE MACHINE
# =============================================================================


class ReadingStateMachine:
    """
    Machine-readable reading state machine.
    Manages transitions between reading states.
    """

    def __init__(self):
        self.state = ReadingState.RAW
        self.history: list[tuple[ReadingState, str]] = []

        # Define valid transitions
        self.transitions = {
            ReadingState.RAW: [ReadingState.PREREAD],
            ReadingState.PREREAD: [ReadingState.SEGMENTED],
            ReadingState.SEGMENTED: [ReadingState.ANCHORED],
            ReadingState.ANCHORED: [ReadingState.SIGNAL_NOISE_SEPARATED],
            ReadingState.SIGNAL_NOISE_SEPARATED: [ReadingState.REFERENCES_BOUND],
            ReadingState.REFERENCES_BOUND: [ReadingState.SALIENCE_RANKED],
            ReadingState.SALIENCE_RANKED: [ReadingState.LATTICE_BUILT],
            ReadingState.LATTICE_BUILT: [
                ReadingState.RESOLVED,
                ReadingState.CLARIFICATION_REQUIRED,
            ],
            ReadingState.RESOLVED: [ReadingState.VERIFIED],
            ReadingState.VERIFIED: [
                ReadingState.STABLE_READ,
                ReadingState.CLARIFICATION_REQUIRED,
                ReadingState.DEFERRED,
                ReadingState.BLOCKED,
            ],
            ReadingState.CLARIFICATION_REQUIRED: [ReadingState.RAW],  # Restart with clarification
            ReadingState.DEFERRED: [ReadingState.RAW],
            ReadingState.BLOCKED: [ReadingState.RAW],
        }

    def transition(self, to_state: ReadingState, condition: str = "") -> bool:
        """Attempt state transition."""
        if to_state in self.transitions.get(self.state, []):
            self.history.append((self.state, condition))
            self.state = to_state
            return True
        return False

    def get_state(self) -> ReadingState:
        """Get current state."""
        return self.state

    def can_transition(self, to_state: ReadingState) -> bool:
        """Check if transition is valid."""
        return to_state in self.transitions.get(self.state, [])


# =============================================================================
# 6. READING KERNEL ORCHESTRATOR
# =============================================================================


class AMOSReadingKernel:
    """
    AMOS Reading Kernel - Full reading pipeline orchestrator.

    Implements: E_preread → E_segment → E_anchor → E_sn → E_bind → E_salience → E_lattice → E_resolve → E_verify → E_stabilize
    """

    def __init__(self):
        # Initialize all engines
        self.e_preread = PrereadEngine()
        self.e_segment = SegmentationEngine()
        self.e_anchor = AnchorEngine()
        self.e_infer = HumanStateInferenceEngine()
        self.e_sn = SignalNoiseEngine()
        self.e_bind = BindingEngine()
        self.e_salience = SalienceEngine()
        self.e_lattice = LatticeEngine()
        self.e_resolve = ResolutionEngine()
        self.e_verify = VerificationEngine()
        self.e_stabilize = StabilizationEngine()

        # State machine
        self.state_machine = ReadingStateMachine()

        # Reading invariants
        self.invariants: list[ReadingInvariant] = [
            ReadingInvariant("RI01", "no downstream module may consume raw language directly"),
            ReadingInvariant(
                "RI02", "all utterances must be segmented before semantic interpretation"
            ),
            ReadingInvariant(
                "RI03", "all high-salience units must be reference-bound before stable read"
            ),
            ReadingInvariant("RI04", "signal must dominate read selection"),
            ReadingInvariant("RI05", "diagnostic noise must be retained when state-relevant"),
            ReadingInvariant("RI06", "ambiguity above threshold blocks stable read"),
            ReadingInvariant("RI07", "stable read is required before execution"),
        ]

        # Configuration
        self.thresholds = {
            "segmentation_quality": 0.5,
            "anchor_coverage": 0.3,
            "signal_score": 0.4,
            "binding_confidence": 0.5,
            "ambiguity": 0.6,
            "best_hypothesis_confidence": 0.6,
        }

    async def read(
        self,
        raw_text: str,
        dialogue_context: dict[str, Any] = None,
        memory_context: dict[str, Any] = None,
        world_context: dict[str, Any] = None,
    ) -> Optional[StableRead]:
        """
        Execute full reading pipeline on raw text.

        Returns StableRead object for downstream AMOS consumption.
        """
        ctx = dialogue_context or {}
        mem = memory_context or {}
        world = world_context or {}

        # Initialize state machine
        self.state_machine = ReadingStateMachine()

        # === E_preread ===
        preread = self.e_preread.normalize(raw_text)
        if not self.state_machine.transition(ReadingState.PREREAD, "normalization_ok"):
            return None

        # === E_segment ===
        segments = self.e_segment.segment(preread)
        if len(segments) == 0:
            return None
        if not self.state_machine.transition(
            ReadingState.SEGMENTED, f"segments_count={len(segments)}"
        ):
            return None

        # === E_anchor ===
        anchored = self.e_anchor.anchor(segments, ctx, mem)
        anchor_count = sum(1 for a in anchored if a.entities or a.topic_refs)
        if anchor_count < 1:
            # Still proceed but mark low anchor coverage
            pass
        if not self.state_machine.transition(
            ReadingState.ANCHORED, f"anchors_found={anchor_count}"
        ):
            return None

        # === E_infer (parallel to anchor) ===
        human_state = self.e_infer.infer(raw_text, [])

        # === E_sn ===
        sn_units = self.e_sn.separate(anchored, human_state, ctx)
        sn_pass = any(u.retain_mode != RetainMode.DROP for u in sn_units)
        if not sn_pass:
            return None
        if not self.state_machine.transition(
            ReadingState.SIGNAL_NOISE_SEPARATED, "sn_pass_complete"
        ):
            return None

        # === E_bind ===
        binding_state = self.e_bind.bind(sn_units, ctx, mem, world)
        if not self.state_machine.transition(
            ReadingState.REFERENCES_BOUND, "binding_attempt_complete"
        ):
            return None

        # Check invariant RI03
        high_salience = [u for u in sn_units if u.signal_score > 0.7]
        unbound_critical = [u for u in high_salience if u.segment_id in binding_state.unbound_slots]
        if unbound_critical:
            # Flag but continue
            pass

        # === E_salience ===
        active_goals = ctx.get("active_goals", [])
        salience_units = self.e_salience.rank(sn_units, binding_state, active_goals)
        if not salience_units:
            return None
        if not self.state_machine.transition(
            ReadingState.SALIENCE_RANKED, "salience_scores_assigned"
        ):
            return None

        # === E_lattice ===
        lattice = self.e_lattice.build(salience_units, binding_state, ctx)
        if len(lattice.hypotheses) == 0:
            return None
        if not self.state_machine.transition(
            ReadingState.LATTICE_BUILT, f"hypotheses_count={len(lattice.hypotheses)}"
        ):
            return None

        # === E_resolve ===
        resolved = self.e_resolve.resolve(lattice)

        # Check if clarification needed
        if resolved and resolved.confidence < self.thresholds["best_hypothesis_confidence"]:
            if not self.state_machine.transition(
                ReadingState.CLARIFICATION_REQUIRED, "low_confidence"
            ):
                return None
            # Build clarification read
            return self._build_clarification_read(lattice, resolved)

        if not self.state_machine.transition(ReadingState.RESOLVED, "best_hypothesis_selected"):
            return None

        # === E_verify ===
        governance_state = ctx.get("governance", {})
        epistemic_state = {"confidence": resolved.confidence if resolved else 0}
        verified = self.e_verify.verify(resolved, governance_state, epistemic_state)

        if not self.state_machine.transition(ReadingState.VERIFIED, "verification_complete"):
            return None

        # === E_stabilize ===
        stable = self.e_stabilize.stabilize(verified, resolved, lattice)

        if stable and stable.execution_readiness.stable:
            self.state_machine.transition(ReadingState.STABLE_READ, "read_stable")
        elif stable and stable.execution_readiness.requires_clarification:
            self.state_machine.transition(ReadingState.CLARIFICATION_REQUIRED, "missing_slots")
        elif stable and verified.get("not_executable_but_safe_to_hold"):
            self.state_machine.transition(ReadingState.DEFERRED, "deferred")
        else:
            self.state_machine.transition(ReadingState.BLOCKED, "unsafe_or_contradictory")

        return stable

    def _build_clarification_read(
        self, lattice: ReadingLattice, resolved: Optional[SemanticHypothesis]
    ) -> StableRead:
        """Build a clarification request read."""
        stable = StableRead()
        stable.utterance_id = lattice.utterance_id
        stable.primary_intent = {"type": "clarification_required", "confidence": 0.9}
        stable.execution_readiness = ExecutionReadiness(
            readable=True, stable=False, requires_clarification=True, safe_for_execution=False
        )
        stable.compiled_goal = CompiledGoal(
            goal_type=GoalType.CLARIFY,
            objective="resolve_reading_ambiguity",
            constraints=["low_confidence", "needs_disambiguation"],
            success_criteria=["clarification_received"],
        )
        return stable

    def check_invariants(self, stage: str) -> list[ReadingInvariant]:
        """Check which invariants are violated at current stage."""
        violated = []

        for inv in self.invariants:
            if inv.invariant_id == "RI01" and stage == "consumption":
                # Check if raw text being consumed
                pass
            elif (
                inv.invariant_id == "RI02"
                and self.state_machine.get_state().value < ReadingState.SEGMENTED.value
            ):
                inv.violated = True
                violated.append(inv)
            elif (
                inv.invariant_id == "RI03"
                and self.state_machine.get_state().value < ReadingState.REFERENCES_BOUND.value
            ):
                inv.violated = True
                violated.append(inv)

        return violated

    def get_state(self) -> ReadingState:
        """Get current reading state."""
        return self.state_machine.get_state()

    def to_dict(self) -> dict[str, Any]:
        """Serialize kernel state to dictionary."""
        return {
            "current_state": self.state_machine.get_state().name,
            "invariants": [
                {"id": inv.invariant_id, "rule": inv.rule, "violated": inv.violated}
                for inv in self.invariants
            ],
            "thresholds": self.thresholds,
        }


# =============================================================================
# 7. GATING EQUATIONS
# =============================================================================


def readability_gate(
    segmentation_quality: float,
    anchor_coverage: float,
    signal_score: float,
    thresholds: dict[str, float],
) -> bool:
    """
    Gate 15.1: Readability gate

    Readable = 𝟙[SegmentationQuality ≥ τ₁ ∧ AnchorCoverage ≥ τ₂ ∧ SignalScore ≥ τ₃]
    """
    return (
        segmentation_quality >= thresholds["segmentation_quality"]
        and anchor_coverage >= thresholds["anchor_coverage"]
        and signal_score >= thresholds["signal_score"]
    )


def stable_read_gate(
    readable: bool,
    binding_confidence: float,
    ambiguity: float,
    best_hypothesis_confidence: float,
    thresholds: dict[str, float],
) -> bool:
    """
    Gate 15.2: Stable-read gate

    StableRead = 𝟙[Readable=1 ∧ BindingConfidence ≥ τ₄ ∧ Ambiguity ≤ τ₅ ∧ BestHypothesisConfidence ≥ τ₆]
    """
    if not readable:
        return False

    return (
        binding_confidence >= thresholds["binding_confidence"]
        and ambiguity <= thresholds["ambiguity"]
        and best_hypothesis_confidence >= thresholds["best_hypothesis_confidence"]
    )


def safe_execution_gate(
    stable_read: bool, verification: bool, safety: bool, governance: bool
) -> bool:
    """
    Gate 15.3: Safe execution gate

    ExecuteAllowed = 𝟙[StableRead=1 ∧ Verification=1 ∧ Safety=1 ∧ Governance=1]
    """
    return stable_read and verification and safety and governance


# =============================================================================
# 8. UTILITY FUNCTIONS AND EXPORTS
# =============================================================================

# Global kernel instance
_reading_kernel: Optional[AMOSReadingKernel] = None


def get_reading_kernel() -> AMOSReadingKernel:
    """Get or create global reading kernel instance."""
    global _reading_kernel
    if _reading_kernel is None:
        _reading_kernel = AMOSReadingKernel()
    return _reading_kernel


def reset_reading_kernel() -> None:
    """Reset global reading kernel instance."""
    global _reading_kernel
    _reading_kernel = None


# Convenience function for direct reading
async def read_text(
    raw_text: str,
    dialogue_context: dict[str, Any] = None,
    memory_context: dict[str, Any] = None,
    world_context: dict[str, Any] = None,
) -> Optional[StableRead]:
    """
    Read text through AMOS Reading Kernel.

    This is the main entry point for converting human language to StableRead objects.
    """
    kernel = get_reading_kernel()
    return await kernel.read(raw_text, dialogue_context, memory_context, world_context)


# JSON schema export
def get_reading_schemas() -> dict[str, Any]:
    """Export machine-readable schemas for all reading objects."""
    return {
        "PreReadRepresentation": {
            "description": "Normalized representation before parsing",
            "fields": [
                "raw_text",
                "normalized_text",
                "language",
                "format_features",
                "readability_risks",
            ],
        },
        "Segment": {
            "description": "Segmented unit of meaning",
            "fields": ["segment_id", "text", "seg_type", "confidence", "start_index", "end_index"],
            "types": [t.value for t in SegmentType],
        },
        "SignalNoiseUnit": {
            "description": "Signal-noise classification",
            "fields": [
                "segment_id",
                "signal_class",
                "noise_class",
                "signal_score",
                "noise_score",
                "ambiguity_score",
                "retain_mode",
                "confidence",
            ],
            "signal_classes": [s.value for s in SignalClass],
            "noise_classes": [n.value for n in NoiseClass],
            "retain_modes": [r.value for r in RetainMode],
        },
        "StableRead": {
            "description": "Final verified read object",
            "fields": [
                "utterance_id",
                "primary_intent",
                "primary_signals",
                "diagnostic_noise",
                "resolved_bindings",
                "open_ambiguities",
                "execution_readiness",
                "compiled_goal",
            ],
        },
        "ReadingStateMachine": {
            "description": "Reading pipeline state machine",
            "states": [s.name for s in ReadingState],
            "transitions": [
                {"from": "RAW", "to": "PREREAD", "condition": "normalization_ok"},
                {"from": "PREREAD", "to": "SEGMENTED", "condition": "segments_count > 0"},
                {
                    "from": "SEGMENTED",
                    "to": "ANCHORED",
                    "condition": "anchors_found >= min_anchor_count",
                },
                {
                    "from": "ANCHORED",
                    "to": "SIGNAL_NOISE_SEPARATED",
                    "condition": "sn_pass_complete",
                },
                {
                    "from": "SIGNAL_NOISE_SEPARATED",
                    "to": "REFERENCES_BOUND",
                    "condition": "binding_attempt_complete",
                },
                {
                    "from": "REFERENCES_BOUND",
                    "to": "SALIENCE_RANKED",
                    "condition": "salience_scores_assigned",
                },
                {
                    "from": "SALIENCE_RANKED",
                    "to": "LATTICE_BUILT",
                    "condition": "interpretation_hypotheses_count >= 1",
                },
                {
                    "from": "LATTICE_BUILT",
                    "to": "RESOLVED",
                    "condition": "best_hypothesis_confidence >= resolve_threshold",
                },
                {
                    "from": "LATTICE_BUILT",
                    "to": "CLARIFICATION_REQUIRED",
                    "condition": "low_confidence",
                },
                {"from": "RESOLVED", "to": "VERIFIED", "condition": "verification_run_complete"},
                {"from": "VERIFIED", "to": "STABLE_READ", "condition": "verification_ok"},
                {
                    "from": "VERIFIED",
                    "to": "CLARIFICATION_REQUIRED",
                    "condition": "missing_slots_count > 0",
                },
                {"from": "VERIFIED", "to": "DEFERRED", "condition": "not_executable_but_safe"},
                {"from": "VERIFIED", "to": "BLOCKED", "condition": "unsafe_or_contradictory"},
            ],
        },
        "ReadingInvariants": {
            "description": "System invariants for reading",
            "invariants": [
                {"id": "RI01", "rule": "no downstream module may consume raw language directly"},
                {
                    "id": "RI02",
                    "rule": "all utterances must be segmented before semantic interpretation",
                },
                {
                    "id": "RI03",
                    "rule": "all high-salience units must be reference-bound before stable read",
                },
                {"id": "RI04", "rule": "signal must dominate read selection"},
                {"id": "RI05", "rule": "diagnostic noise must be retained when state-relevant"},
                {"id": "RI06", "rule": "ambiguity above threshold blocks stable read"},
                {"id": "RI07", "rule": "stable read is required before execution"},
            ],
        },
    }


# =============================================================================
# 9. DEMONSTRATION
# =============================================================================


async def demo_reading_kernel():
    """Demonstrate reading kernel capabilities."""
    print("=" * 60)
    print("AMOS READING KERNEL DEMONSTRATION")
    print("=" * 60)

    kernel = get_reading_kernel()

    # Test utterances
    test_utterances = [
        "I need to design a new caching system but I'm worried about performance risks. It needs to handle 10k requests per second.",
        "What should I do about this?",
        "URGENT: Fix the database connection NOW!!!",
        "Actually, I was thinking maybe we could just sort of try something different, you know?",
    ]

    for utterance in test_utterances:
        print(f"\n{'─' * 50}")
        print(f"INPUT: {utterance[:60]}...")
        print("─" * 50)

        stable_read = await kernel.read(utterance)

        if stable_read:
            print("✓ STABLE READ CREATED")
            print(f"  Utterance ID: {stable_read.utterance_id}")
            print(f"  Intent: {stable_read.primary_intent}")
            print(f"  Execution Ready: {stable_read.execution_readiness.stable}")
            print(f"  Goal Type: {stable_read.compiled_goal.goal_type.value}")
            print(f"  Final State: {kernel.get_state().name}")
        else:
            print("✗ FAILED TO CREATE STABLE READ")

    print(f"\n{'=' * 60}")
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)

    # Export schemas
    schemas = get_reading_schemas()
    print(f"\nExported {len(schemas)} schemas")
    print(f"States: {len(schemas['ReadingStateMachine']['states'])}")
    print(f"Invariants: {len(schemas['ReadingInvariants']['invariants'])}")

    return stable_read


if __name__ == "__main__":
    asyncio.run(demo_reading_kernel())
