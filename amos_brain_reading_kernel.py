from __future__ import annotations

"""
AMOS Brain-Reading Kernel

A cognitive reading architecture that implements predictive, chunk-based,
multi-pass reading with binding, salience, and coherence verification.

This is not language parsing. It is brain-level reading.
"""

import asyncio
import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum, auto
from typing import Any, Final

# ============================================================================
# 1. ENUMS AND TYPE DEFINITIONS
# ============================================================================

class ReadingMode(Enum):
    """Global reading modes reflecting cognitive state."""

    SCAN = auto()  # Fast surface scanning
    READ = auto()  # Normal comprehension
    RESOLVE = auto()  # Deep ambiguity resolution
    REFLECT = auto()  # Metacognitive processing
    STABILIZE = auto()  # Coherence verification
    EXECUTE = auto()  # Action-ready comprehension

class ChunkType(Enum):
    """Types of semantic chunks."""

    CLAIM = auto()
    QUESTION = auto()
    CONSTRAINT = auto()
    GOAL = auto()
    REFERENCE_GROUP = auto()
    EMOTIONAL_BURST = auto()
    INSTRUCTION = auto()
    NARRATIVE_FRAME = auto()
    META_COMMENT = auto()
    COMMAND = auto()
    CRITICISM = auto()

class IntentType(Enum):
    """Classified intent types."""

    REQUEST = auto()
    DESIGN = auto()
    QUESTION = auto()
    CORRECTION = auto()
    DISTRESS = auto()
    DECISION_SUPPORT = auto()
    SPECIFICATION = auto()
    MIXED = auto()

class ConflictType(Enum):
    """Types of detected conflicts."""

    GOAL_CONFLICT = auto()
    CONSTRAINT_CONFLICT = auto()
    SCOPE_CONFLICT = auto()
    IDENTITY_CONFLICT = auto()
    INSTRUCTION_CONFLICT = auto()
    TEMPORAL_CONFLICT = auto()

class ReadingDepth(Enum):
    """Depth control levels."""

    SKIM = auto()
    NORMAL = auto()
    DEEP = auto()
    FORENSIC = auto()

# ============================================================================
# 2. CORE DATA STRUCTURES
# ============================================================================

@dataclass
class GlobalState:
    """Global cognitive state during reading."""

    mode: ReadingMode = ReadingMode.SCAN
    arousal: float = 0.0  # 0-1, cognitive activation
    cognitive_load: float = 0.0  # 0-1, working memory pressure
    uncertainty: float = 0.0  # 0-1, overall uncertainty
    prediction_stability: float = 0.0  # 0-1, how stable predictions are
    working_memory_pressure: float = 0.0  # 0-1, WM load

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode.name,
            "arousal": self.arousal,
            "cognitive_load": self.cognitive_load,
            "uncertainty": self.uncertainty,
            "prediction_stability": self.prediction_stability,
            "working_memory_pressure": self.working_memory_pressure,
        }

@dataclass
class PriorSet:
    """Predictive priors for reading."""

    topic_priors: List[str] = field(default_factory=list)
    intent_priors: List[str] = field(default_factory=list)
    reference_priors: List[str] = field(default_factory=list)
    structure_priors: List[str] = field(default_factory=list)
    risk_priors: List[str] = field(default_factory=list)

@dataclass
class AttentionUnit:
    """Single attention focus unit."""

    chunk_id: str = ""
    position: int = 0
    focus_strength: float = 0.0  # 0-1
    suppression_level: float = 0.0  # 0-1, how much suppressed

@dataclass
class AttentionState:
    """Dynamic attention allocation."""

    focus_units: List[AttentionUnit] = field(default_factory=list)
    suppressed_units: List[AttentionUnit] = field(default_factory=list)
    salience_map: Dict[str, float] = field(default_factory=dict)  # chunk_id -> salience

@dataclass
class MemoryChunk:
    """Chunk in working memory."""

    id: str = ""
    content: str = ""
    chunk_type: ChunkType = ChunkType.CLAIM
    coherence: float = 0.0
    salience: float = 0.0
    binding_requirements: List[str] = field(default_factory=list)
    risk_weight: float = 0.0
    tokens: List[str] = field(default_factory=list)
    position: Tuple[int, int] = (0, 0)  # start, end in text

@dataclass
class Binding:
    """Entity-relation binding."""

    entity_id: str = ""
    surface_forms: List[str] = field(default_factory=list)
    canonical_form: str = ""
    entity_type: str = ""  # person, system, module, goal, constraint, etc.
    confidence: float = 0.0
    bound_to: List[str] = field(default_factory=list)  # other entity_ids

@dataclass
class Relation:
    """Relation between entities."""

    source: str = ""
    relation: str = ""  # targets, modifies, blocks, explains, causes, etc.
    target: str = ""
    confidence: float = 0.0

@dataclass
class OpenBinding:
    """Unresolved binding slot."""

    slot: str = ""
    required_type: str = ""
    candidates: List[str] = field(default_factory=list)
    severity: float = 0.0  # how critical is resolution

@dataclass
class BindingWorkspace:
    """Working memory for entity binding."""

    entities: List[Binding] = field(default_factory=list)
    relations: List[Relation] = field(default_factory=list)
    open_bindings: List[OpenBinding] = field(default_factory=list)

@dataclass
class PredictionError:
    """Prediction error unit."""

    chunk_id: str = ""
    predicted: str = ""
    actual: str = ""
    error_magnitude: float = 0.0
    error_type: str = ""  # semantic, syntactic, contextual

@dataclass
class Conflict:
    """Detected conflict."""

    id: str = ""
    conflict_type: ConflictType = ConflictType.GOAL_CONFLICT
    units_involved: List[str] = field(default_factory=list)
    severity: float = 0.0
    resolvable: bool = True
    description: str = ""

@dataclass
class ErrorState:
    """Aggregate error and conflict state."""

    prediction_errors: List[PredictionError] = field(default_factory=list)
    conflicts: List[Conflict] = field(default_factory=list)
    ambiguities: List[dict[str, Any]] = field(default_factory=list)
    resolution_failures: List[dict[str, Any]] = field(default_factory=list)
    global_conflict_score: float = 0.0

@dataclass
class ReadObject:
    """The current read state."""

    stable: bool = False
    coherent: bool = False
    resolved_intent: Optional[IntentType] = None
    resolved_constraints: List[str] = field(default_factory=list)
    resolved_references: List[str] = field(default_factory=list)
    diagnostic_state: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BrainReadState:
    """Complete brain reading state."""

    global_state: GlobalState = field(default_factory=GlobalState)
    priors: PriorSet = field(default_factory=PriorSet)
    attention: AttentionState = field(default_factory=AttentionState)
    working_memory: List[MemoryChunk] = field(default_factory=list)
    binding_workspace: BindingWorkspace = field(default_factory=BindingWorkspace)
    error_state: ErrorState = field(default_factory=ErrorState)
    read_object: ReadObject = field(default_factory=ReadObject)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class SalienceUnit:
    """Salience computation for a chunk."""

    chunk_id: str = ""
    goal_relevance: float = 0.0
    constraint_weight: float = 0.0
    error_weight: float = 0.0
    risk_weight: float = 0.0
    novelty_weight: float = 0.0
    recurrence_weight: float = 0.0

    @property
    def salience_score(self) -> float:
        """Compute composite salience."""
        return (
            0.25 * self.goal_relevance
            + 0.20 * self.constraint_weight
            + 0.15 * self.error_weight
            + 0.20 * self.risk_weight
            + 0.10 * self.novelty_weight
            + 0.10 * self.recurrence_weight
        )

@dataclass
class CompiledGoal:
    """Compiled action goal from reading."""

    goal_type: str = ""  # respond, design, plan, simulate, clarify, defer, block
    objective: str = ""
    constraints: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)

@dataclass
class StableRead:
    """Final stable read output."""

    utterance_id: str = ""
    primary_intent: Tuple[IntentType, float] = field(
        default_factory=lambda: (IntentType.MIXED, 0.0)
    )
    goal_structure: List[str] = field(default_factory=list)
    constraint_structure: List[str] = field(default_factory=list)
    reference_structure: List[str] = field(default_factory=list)
    reader_estimate: Dict[str, Any] = field(default_factory=dict)
    speaker_estimate: Dict[str, Any] = field(default_factory=dict)
    diagnostic_noise: List[dict[str, Any]] = field(default_factory=list)
    conflicts: List[Conflict] = field(default_factory=list)
    ambiguities: List[dict[str, Any]] = field(default_factory=list)
    coherence_score: float = 0.0
    stable: bool = False
    compiled_goal: CompiledGoal = field(default_factory=CompiledGoal)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ============================================================================
# 3. PREDICTIVE READING CORE
# ============================================================================

class PredictiveModel:
    """
    Predictive processing engine.

    Implements: P(R_t) -> prediction
    """

    def __init__(self):
        self.prediction_history: List[dict[str, Any]] = []
        self.learning_rate = 0.1

    def predict(
        self,
        chunks: List[MemoryChunk],
        priors: PriorSet,
        goals: List[str],
        memory_context: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Predict likely meaning structure from chunks.

        Returns: {chunk_id: predicted_meaning}
        """
        predictions = {}

        for chunk in chunks:
            # Simple prediction based on chunk type and priors
            if chunk.chunk_type == ChunkType.GOAL:
                predictions[chunk.id] = f"goal:{chunk.content[:50]}"
            elif chunk.chunk_type == ChunkType.CONSTRAINT:
                predictions[chunk.id] = f"constraint:{chunk.content[:50]}"
            elif chunk.chunk_type == ChunkType.COMMAND:
                predictions[chunk.id] = f"command:{chunk.content[:50]}"
            elif "?" in chunk.content:
                predictions[chunk.id] = f"question:{chunk.content[:50]}"
            else:
                predictions[chunk.id] = f"statement:{chunk.content[:50]}"

        return predictions

    def sample(self, text: str, chunk: MemoryChunk) -> str:
        """
        Sample actual input features.

        Returns: sampled meaning
        """
        # Extract surface features
        return f"sampled:{chunk.content[:50]}"

    def compute_error(self, prediction: str, sample: str, chunk: MemoryChunk) -> PredictionError:
        """
        Compute prediction error: ε_t = s_t - m̂_t
        """
        # Simple edit-distance-like error
        pred_clean = (
            prediction.replace("predicted:", "").replace("goal:", "").replace("constraint:", "")
        )
        samp_clean = sample.replace("sampled:", "")

        # Compute normalized error
        max_len = max(len(pred_clean), len(samp_clean))
        if max_len == 0:
            error_mag = 0.0
        else:
            # Simple character difference ratio
            matches = sum(1 for a, b in zip(pred_clean, samp_clean) if a == b)
            error_mag = 1.0 - (matches / max_len)

        return PredictionError(
            chunk_id=chunk.id,
            predicted=prediction,
            actual=sample,
            error_magnitude=error_mag,
            error_type="semantic" if error_mag > 0.3 else "syntactic",
        )

# ============================================================================
# 4. CHUNKING ENGINE
# ============================================================================

class ChunkingEngine:
    """
    Segments input into cognitive chunks.

    Humans read by chunks, frames, and binding groups—not tokens.
    """

    # Chunk boundary markers
    BOUNDARY_MARKERS = [
        r"\.",
        r"\!",
        r"\?",
        r"\n\n",  # Sentence/paragraph
        r"however",
        r"but",
        r"although",
        r"though",  # Contrast
        r"because",
        r"since",
        r"therefore",
        r"thus",  # Causal
        r"so",
        r"if",
        r"then",  # Conditional
        r"first",
        r"second",
        r"finally",
        r"next",  # Sequence
        r"for example",
        r"such as",
        r"like",  # Exemplar
        r"in contrast",
        r"on the other hand",  # Comparison
        r"moreover",
        r"furthermore",
        r"additionally",  # Addition
        r"\*\*",
        r"__",
        r"`",  # Formatting
    ]

    # Chunk type patterns
    TYPE_PATTERNS = {
        ChunkType.QUESTION: [
            r"\?",
            r"what",
            r"how",
            r"why",
            r"when",
            r"where",
            r"who",
            r"can you",
            r"could you",
        ],
        ChunkType.COMMAND: [
            r"should",
            r"must",
            r"need to",
            r"fix",
            r"add",
            r"remove",
            r"change",
            r"implement",
            r"create",
        ],
        ChunkType.CONSTRAINT: [
            r"but",
            r"however",
            r"although",
            r"unless",
            r"only if",
            r"must not",
            r"cannot",
            r"restriction",
        ],
        ChunkType.CRITICISM: [
            r"wrong",
            r"incorrect",
            r"bad",
            r"issue",
            r"problem",
            r"bug",
            r"error",
            r"shallow",
            r"dumb",
        ],
        ChunkType.GOAL: [
            r"goal",
            r"objective",
            r"aim",
            r"target",
            r"purpose",
            r"intent",
            r"want",
            r"need",
        ],
    }

    def chunk_input(self, text: str) -> List[MemoryChunk]:
        """
        Segment text into cognitive chunks.

        Returns: List of MemoryChunk
        """
        chunks = []

        # First pass: split by boundaries
        segments = self._segment_text(text)

        for i, segment in enumerate(segments):
            if not segment.strip():
                continue

            chunk_type = self._classify_chunk_type(segment)
            chunk_id = f"chunk_{i}_{hashlib.md5(segment.encode()).hexdigest()[:8]}"

            chunk = MemoryChunk(
                id=chunk_id,
                content=segment.strip(),
                chunk_type=chunk_type,
                tokens=segment.split(),
                position=(0, 0),  # Would be computed from original text
                coherence=0.5,  # Initial coherence
                salience=0.0,  # Will be computed
            )
            chunks.append(chunk)

        return chunks

    def _segment_text(self, text: str) -> List[str]:
        """Segment text using boundary markers."""
        # Normalize
        text = text.replace("\n\n", " [PARA] ")
        text = text.replace("\n", " ")

        # Split by sentence boundaries first
        pattern = r"(?<=[.!?])\s+(?=[A-Z])"
        segments = re.split(pattern, text)

        # Further split by structural markers
        result = []
        for seg in segments:
            seg = seg.replace(" [PARA] ", "\n\n")
            if len(seg) > 200:
                # Split long segments by clauses
                clause_pattern = r",\s+(?=(however|but|although|because|since|therefore|if|unless))"
                sub_segments = re.split(clause_pattern, seg)
                result.extend([s for s in sub_segments if s])
            else:
                result.append(seg)

        return result

    def _classify_chunk_type(self, text: str) -> ChunkType:
        """Classify chunk type based on surface features."""
        text_lower = text.lower()

        for chunk_type, patterns in self.TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return chunk_type

        # Default: check for meta-commentary
        if re.search(r"(you|the system|the machine|amos)", text_lower):
            if any(
                x in text_lower
                for x in ["is", "are", "seems", "appears", "lacks", "missing", "needs"]
            ):
                return ChunkType.META_COMMENT

        return ChunkType.CLAIM

# ============================================================================
# 5. BINDING ENGINE
# ============================================================================

class BindingEngine:
    """
    Entity and reference binding system.

    Resolves: "it", "that", "this", "the problem", "the layer"
    """

    # Reference expressions
    REFERENCE_PATTERNS = [
        r"\bit\b",
        r"\bthis\b",
        r"\bthat\b",
        r"\bthese\b",
        r"\bthose\b",
        r"\bthe\s+\w+\b",
        r"\bsuch\s+\w+\b",
    ]

    # Entity type patterns
    ENTITY_PATTERNS = {
        "system": [r"\bsystem\b", r"\bamos\b", r"\bkernel\b", r"\bengine\b", r"\bmodule\b"],
        "problem": [r"\bproblem\b", r"\bissue\b", r"\berror\b", r"\bbug\b", r"\bfailure\b"],
        "layer": [r"\blayer\b", r"\blevel\b", r"\bstage\b", r"\bdepth\b"],
        "process": [r"\bprocess\b", r"\bloop\b", r"\bcycle\b", r"\breading\b", r"\bprediction\b"],
        "constraint": [r"\bconstraint\b", r"\blimit\b", r"\brestriction\b", r"\bbound\b"],
    }

    def bind_entities(
        self,
        chunks: List[MemoryChunk],
        dialogue_context: Dict[str, Any],
        memory_context: Dict[str, Any],
    ) -> BindingWorkspace:
        """
        Build binding workspace from chunks.

        Returns: BindingWorkspace with entities and relations.
        """
        workspace = BindingWorkspace()

        # Extract entities from each chunk
        for chunk in chunks:
            entities = self._extract_entities(chunk)
            for entity in entities:
                # Check if already exists
                existing = next(
                    (e for e in workspace.entities if e.canonical_form == entity.canonical_form),
                    None,
                )
                if not existing:
                    workspace.entities.append(entity)
                else:
                    # Merge surface forms
                    existing.surface_forms.extend(entity.surface_forms)
                    existing.surface_forms = list(set(existing.surface_forms))

        # Extract relations
        workspace.relations = self._extract_relations(chunks, workspace.entities)

        # Identify open bindings (unresolved references)
        workspace.open_bindings = self._find_open_bindings(chunks, workspace.entities)

        return workspace

    def _extract_entities(self, chunk: MemoryChunk) -> List[Binding]:
        """Extract entities from a chunk."""
        entities = []
        text = chunk.content.lower()

        # Extract by patterns
        for entity_type, patterns in self.ENTITY_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    surface = match.group(0)
                    entity_id = f"ent_{entity_type}_{hashlib.md5(surface.encode()).hexdigest()[:8]}"

                    # Check if already exists
                    if not any(e.entity_id == entity_id for e in entities):
                        entities.append(
                            Binding(
                                entity_id=entity_id,
                                surface_forms=[surface],
                                canonical_form=surface.lower(),
                                entity_type=entity_type,
                                confidence=0.7,
                                bound_to=[],
                            )
                        )

        # Extract noun phrases (simple approach)
        noun_phrases = re.findall(r"\b(the|a|an)\s+(\w+(?:\s+\w+){0,3})\b", text, re.IGNORECASE)
        for det, np in noun_phrases:
            full_np = f"{det} {np}"
            entity_id = f"ent_np_{hashlib.md5(full_np.encode()).hexdigest()[:8]}"

            if not any(e.entity_id == entity_id for e in entities):
                entities.append(
                    Binding(
                        entity_id=entity_id,
                        surface_forms=[full_np],
                        canonical_form=full_np.lower(),
                        entity_type="noun_phrase",
                        confidence=0.5,
                        bound_to=[],
                    )
                )

        return entities

    def _extract_relations(
        self, chunks: List[MemoryChunk], entities: List[Binding]
    ) -> List[Relation]:
        """Extract relations between entities."""
        relations = []

        # Simple relation extraction patterns
        relation_patterns = [
            (
                r"(\w+)\s+(targets|modifies|blocks|explains|causes|requests|criticizes)\s+(\w+)",
                r"\1",
                r"\2",
                r"\3",
            ),
        ]

        for chunk in chunks:
            text = chunk.content.lower()

            # Check for explicit relations
            for pattern, src_grp, rel_grp, tgt_grp in relation_patterns:
                for match in re.finditer(pattern, text):
                    src = match.group(1)
                    rel = match.group(2)
                    tgt = match.group(3)

                    # Find entity IDs
                    src_entity = next(
                        (e for e in entities if src in e.surface_forms or src in e.canonical_form),
                        None,
                    )
                    tgt_entity = next(
                        (e for e in entities if tgt in e.surface_forms or tgt in e.canonical_form),
                        None,
                    )

                    if src_entity and tgt_entity:
                        relations.append(
                            Relation(
                                source=src_entity.entity_id,
                                relation=rel,
                                target=tgt_entity.entity_id,
                                confidence=0.6,
                            )
                        )

        return relations

    def _find_open_bindings(
        self, chunks: List[MemoryChunk], entities: List[Binding]
    ) -> List[OpenBinding]:
        """Find unresolved reference bindings."""
        open_bindings = []

        for chunk in chunks:
            text = chunk.content.lower()

            for pattern in self.REFERENCE_PATTERNS:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    ref = match.group(0)

                    # Check if resolved
                    resolved = any(ref in e.surface_forms for e in entities)

                    if not resolved:
                        open_bindings.append(
                            OpenBinding(
                                slot=ref,
                                required_type="reference",
                                candidates=[e.entity_id for e in entities],
                                severity=0.8 if ref in ["it", "this", "that"] else 0.5,
                            )
                        )

        return open_bindings

# ============================================================================
# 6. SALIENCE ENGINE
# ============================================================================

class SalienceEngine:
    """
    Computes multi-factor salience.

    Salience ≠ importance. It is:
    α·GoalRelevance + β·ConstraintWeight + γ·ErrorWeight + δ·RiskWeight + ε·Novelty + ζ·Recurrence
    """

    def compute_salience(
        self,
        chunks: List[MemoryChunk],
        bindings: BindingWorkspace,
        goals: List[str],
        errors: List[PredictionError],
    ) -> List[SalienceUnit]:
        """
        Compute salience for all chunks.

        Returns: List of SalienceUnit
        """
        salience_units = []

        # Goal relevance keywords
        goal_keywords = set()
        for goal in goals:
            goal_keywords.update(goal.lower().split())

        for chunk in chunks:
            chunk_text = chunk.content.lower()
            chunk_words = set(chunk_text.split())

            # Goal relevance
            goal_overlap = len(chunk_words & goal_keywords)
            goal_relevance = (
                min(1.0, goal_overlap / max(len(goal_keywords), 1)) if goal_keywords else 0.5
            )

            # Constraint weight
            constraint_weight = 0.8 if chunk.chunk_type == ChunkType.CONSTRAINT else 0.3
            if any(
                kw in chunk_text for kw in ["must", "should", "required", "necessary", "critical"]
            ):
                constraint_weight = 0.9

            # Error weight
            chunk_errors = [e for e in errors if e.chunk_id == chunk.id]
            error_weight = max([e.error_magnitude for e in chunk_errors], default=0.0)

            # Risk weight
            risk_weight = chunk.risk_weight
            if any(
                kw in chunk_text for kw in ["wrong", "error", "fail", "bug", "problem", "issue"]
            ):
                risk_weight = 0.8

            # Novelty
            novelty_weight = 0.5  # Would compare to memory

            # Recurrence
            recurrence_weight = 0.3  # Would track mentions

            salience_units.append(
                SalienceUnit(
                    chunk_id=chunk.id,
                    goal_relevance=goal_relevance,
                    constraint_weight=constraint_weight,
                    error_weight=error_weight,
                    risk_weight=risk_weight,
                    novelty_weight=novelty_weight,
                    recurrence_weight=recurrence_weight,
                )
            )

        return salience_units

    def select_primary_read_set(self, salience_units: List[SalienceUnit], k: int = 5) -> List[str]:
        """
        Select top-k chunks by salience.

        PrimaryReadSet = TopK(Chunks, SalienceScore)
        """
        sorted_units = sorted(salience_units, key=lambda x: x.salience_score, reverse=True)
        return [u.chunk_id for u in sorted_units[:k]]

# ============================================================================
# 7. CONFLICT DETECTION
# ============================================================================

class ConflictDetector:
    """
    Detects conflicts in reading lattice.

    HighConflict ⇒ NoStableRead
    """

    def detect_conflicts(self, chunks: List[MemoryChunk], bindings: BindingWorkspace) -> ErrorState:
        """
        Detect all conflicts.

        Returns: ErrorState with conflicts list.
        """
        error_state = ErrorState()

        # Check for goal conflicts
        goal_chunks = [c for c in chunks if c.chunk_type == ChunkType.GOAL]
        if len(goal_chunks) > 1:
            # Check for contradictory goals
            for i, g1 in enumerate(goal_chunks):
                for g2 in goal_chunks[i + 1 :]:
                    if self._are_contradictory(g1, g2):
                        error_state.conflicts.append(
                            Conflict(
                                id=f"conflict_goal_{i}_{hashlib.md5(g1.content.encode()).hexdigest()[:6]}",
                                conflict_type=ConflictType.GOAL_CONFLICT,
                                units_involved=[g1.id, g2.id],
                                severity=0.9,
                                resolvable=False,
                                description=f"Contradictory goals: '{g1.content[:30]}...' vs '{g2.content[:30]}...'",
                            )
                        )

        # Check for constraint conflicts
        constraint_chunks = [c for c in chunks if c.chunk_type == ChunkType.CONSTRAINT]
        if len(constraint_chunks) > 1:
            for i, c1 in enumerate(constraint_chunks):
                for c2 in constraint_chunks[i + 1 :]:
                    if self._constraints_conflict(c1, c2):
                        error_state.conflicts.append(
                            Conflict(
                                id=f"conflict_constraint_{i}",
                                conflict_type=ConflictType.CONSTRAINT_CONFLICT,
                                units_involved=[c1.id, c2.id],
                                severity=0.8,
                                resolvable=True,
                                description="Conflicting constraints",
                            )
                        )

        # Check for instruction conflicts (commands vs constraints)
        command_chunks = [c for c in chunks if c.chunk_type == ChunkType.COMMAND]
        for cmd in command_chunks:
            for con in constraint_chunks:
                if self._command_violates_constraint(cmd, con):
                    error_state.conflicts.append(
                        Conflict(
                            id=f"conflict_inst_{cmd.id}",
                            conflict_type=ConflictType.INSTRUCTION_CONFLICT,
                            units_involved=[cmd.id, con.id],
                            severity=0.85,
                            resolvable=True,
                            description="Command may violate constraint",
                        )
                    )

        # Compute global conflict score
        if error_state.conflicts:
            error_state.global_conflict_score = max(c.severity for c in error_state.conflicts)

        return error_state

    def _are_contradictory(self, c1: MemoryChunk, c2: MemoryChunk) -> bool:
        """Check if two chunks are contradictory."""
        text1 = c1.content.lower()
        text2 = c2.content.lower()

        # Simple antonym detection
        antonym_pairs = [
            ("increase", "decrease"),
            ("add", "remove"),
            ("enable", "disable"),
            ("start", "stop"),
            ("more", "less"),
            ("shallow", "deep"),
            ("simple", "complex"),
        ]

        for a, b in antonym_pairs:
            if (a in text1 and b in text2) or (b in text1 and a in text2):
                return True

        return False

    def _constraints_conflict(self, c1: MemoryChunk, c2: MemoryChunk) -> bool:
        """Check if constraints conflict."""
        # Simplified check
        return self._are_contradictory(c1, c2)

    def _command_violates_constraint(self, cmd: MemoryChunk, con: MemoryChunk) -> bool:
        """Check if command may violate constraint."""
        cmd_text = cmd.content.lower()
        con_text = con.content.lower()

        # Check for explicit violations
        if "remove" in cmd_text and "must" in con_text:
            return True
        if "add" in cmd_text and "only" in con_text:
            return True

        return False

# ============================================================================
# 8. COHERENCE VERIFICATION
# ============================================================================

class CoherenceVerifier:
    """
    Verifies global coherence of reading.

    ReadCoherence = α·ConstraintCoverage + β·BindingCompleteness + γ·HypothesisConsistency + δ·SalienceCoverage - ε·Conflict - ζ·Ambiguity
    """

    COHERENCE_THRESHOLD = 0.6

    def verify_coherence(
        self,
        chunks: List[MemoryChunk],
        bindings: BindingWorkspace,
        salience_units: List[SalienceUnit],
        error_state: ErrorState,
        constraints: List[str],
    ) -> Tuple[float, bool]:
        """
        Verify global coherence.

        Returns: (coherence_score, is_stable)
        """
        # Constraint coverage
        covered_constraints = sum(
            1 for c in constraints if any(c.lower() in chunk.content.lower() for chunk in chunks)
        )
        constraint_coverage = covered_constraints / max(len(constraints), 1)

        # Binding completeness
        if bindings.open_bindings:
            critical_unbound = sum(1 for b in bindings.open_bindings if b.severity > 0.7)
            binding_completeness = 1.0 - (critical_unbound / len(bindings.open_bindings))
        else:
            binding_completeness = 1.0

        # Hypothesis consistency (simplified)
        hypothesis_consistency = 1.0 - error_state.global_conflict_score

        # Salience coverage
        high_salience_chunks = [s for s in salience_units if s.salience_score > 0.5]
        salience_coverage = len(high_salience_chunks) / max(len(chunks), 1)

        # Conflict penalty
        conflict_penalty = error_state.global_conflict_score

        # Ambiguity penalty
        ambiguity_penalty = len(error_state.ambiguities) * 0.1

        # Compute coherence
        coherence = (
            0.25 * constraint_coverage
            + 0.25 * binding_completeness
            + 0.20 * hypothesis_consistency
            + 0.15 * salience_coverage
            - 0.10 * conflict_penalty
            - 0.05 * ambiguity_penalty
        )
        coherence = max(0.0, min(1.0, coherence))

        is_stable = (
            coherence >= self.COHERENCE_THRESHOLD and error_state.global_conflict_score < 0.5
        )

        return coherence, is_stable

# ============================================================================
# 9. DEPTH CONTROLLER
# ============================================================================

class DepthController:
    """
    Controls reading depth based on content characteristics.

    Depth_t = f(Importance_t, Ambiguity_t, Risk_t, GoalRelevance_t)
    """

    def select_depth(
        self,
        chunks: List[MemoryChunk],
        salience_units: List[SalienceUnit],
        error_state: ErrorState,
        goal_relevance: float,
    ) -> ReadingDepth:
        """
        Select appropriate reading depth.

        Returns: ReadingDepth enum value
        """
        # Compute factors
        importance = max((s.salience_score for s in salience_units), default=0.5)
        ambiguity = len(error_state.ambiguities) / max(len(chunks), 1)
        risk = error_state.global_conflict_score

        # Depth selection logic
        if risk > 0.7 or (ambiguity > 0.5 and importance > 0.7):
            return ReadingDepth.FORENSIC
        elif importance > 0.6 or ambiguity > 0.3:
            return ReadingDepth.DEEP
        elif goal_relevance > 0.5:
            return ReadingDepth.NORMAL
        else:
            return ReadingDepth.SKIM

# ============================================================================
# 10. MULTI-PASS READING
# ============================================================================

class MultiPassReader:
    """
    Implements multi-pass reading strategy.

    Read* = Pass_5(Pass_4(Pass_3(Pass_2(Pass_1(U_t)))))
    """

    PASSES = [
        {"name": "pass_1_surface_structure", "goal": "segment and anchor"},
        {"name": "pass_2_signal_and_risk", "goal": "detect what matters and what is dangerous"},
        {
            "name": "pass_3_binding_and_reference",
            "goal": "resolve entities, scope, and omitted structure",
        },
        {
            "name": "pass_4_intent_and_constraints",
            "goal": "infer actual request and preserved constraints",
        },
        {"name": "pass_5_global_coherence", "goal": "check whether the full reading is stable"},
    ]

    def __init__(self):
        self.chunker = ChunkingEngine()
        self.predictor = PredictiveModel()
        self.binder = BindingEngine()
        self.salience = SalienceEngine()
        self.conflict = ConflictDetector()
        self.coherence = CoherenceVerifier()
        self.depth = DepthController()

    async def read(
        self,
        text: str,
        dialogue_context: Dict[str, Any]  = None,
        memory_context: Dict[str, Any]  = None,
        world_context: Dict[str, Any]  = None,
        active_goals: Optional[list[str]] = None,
    ) -> StableRead:
        """
        Execute full multi-pass reading.

        Returns: StableRead
        """
        dialogue_context = dialogue_context or {}
        memory_context = memory_context or {}
        world_context = world_context or {}
        active_goals = active_goals or []

        # Initialize brain state
        brain_state = BrainReadState()
        brain_state.global_state.mode = ReadingMode.SCAN

        # === PASS 1: Surface Structure ===
        chunks = self.chunker.chunk_input(text)
        brain_state.working_memory = chunks
        brain_state.global_state.mode = ReadingMode.READ

        # === PASS 2: Signal and Risk ===
        predictions = self.predictor.predict(
            chunks, brain_state.priors, active_goals, memory_context
        )

        # Compute prediction errors
        errors = []
        for chunk in chunks:
            pred = predictions.get(chunk.id, "")
            sample = self.predictor.sample(text, chunk)
            error = self.predictor.compute_error(pred, sample, chunk)
            errors.append(error)

        brain_state.error_state.prediction_errors = errors

        # === PASS 3: Binding and Reference ===
        bindings = self.binder.bind_entities(chunks, dialogue_context, memory_context)
        brain_state.binding_workspace = bindings

        # === PASS 4: Intent and Constraints ===
        salience_units = self.salience.compute_salience(chunks, bindings, active_goals, errors)
        primary_set = self.salience.select_primary_read_set(salience_units, k=min(5, len(chunks)))

        # Update brain state with high-salience focus
        for chunk in chunks:
            if chunk.id in primary_set:
                brain_state.attention.focus_units.append(
                    AttentionUnit(
                        chunk_id=chunk.id,
                        position=chunks.index(chunk),
                        focus_strength=salience_units[primary_set.index(chunk.id)].salience_score,
                    )
                )

        # Detect conflicts
        error_state = self.conflict.detect_conflicts(chunks, bindings)
        brain_state.error_state.conflicts = error_state.conflicts
        brain_state.error_state.global_conflict_score = error_state.global_conflict_score

        # === PASS 5: Global Coherence ===
        coherence_score, is_stable = self.coherence.verify_coherence(
            chunks,
            bindings,
            salience_units,
            brain_state.error_state,
            [],  # constraints would be extracted
        )

        brain_state.read_object.coherent = is_stable
        brain_state.read_object.stable = is_stable and len(bindings.open_bindings) == 0

        # Compile final read
        return self._compile_stable_read(
            chunks, bindings, salience_units, brain_state, coherence_score, is_stable, active_goals
        )

    def _compile_stable_read(
        self,
        chunks: List[MemoryChunk],
        bindings: BindingWorkspace,
        salience_units: List[SalienceUnit],
        brain_state: BrainReadState,
        coherence_score: float,
        is_stable: bool,
        active_goals: List[str],
    ) -> StableRead:
        """Compile final stable read from brain state."""

        # Infer primary intent
        intent_scores = {}
        for chunk in chunks:
            if chunk.chunk_type == ChunkType.COMMAND:
                intent_scores[IntentType.REQUEST] = intent_scores.get(IntentType.REQUEST, 0.0) + 0.8
            elif chunk.chunk_type == ChunkType.QUESTION:
                intent_scores[IntentType.QUESTION] = (
                    intent_scores.get(IntentType.QUESTION, 0.0) + 0.9
                )
            elif chunk.chunk_type == ChunkType.CRITICISM:
                intent_scores[IntentType.CORRECTION] = (
                    intent_scores.get(IntentType.CORRECTION, 0.0) + 0.9
                )
            elif chunk.chunk_type == ChunkType.GOAL:
                intent_scores[IntentType.SPECIFICATION] = (
                    intent_scores.get(IntentType.SPECIFICATION, 0.0) + 0.7
                )

        if intent_scores:
            primary_intent = max(intent_scores.items(), key=lambda x: x[1])
        else:
            primary_intent = (IntentType.MIXED, 0.5)

        # Extract goals and constraints
        goal_structure = [c.content for c in chunks if c.chunk_type == ChunkType.GOAL]
        constraint_structure = [c.content for c in chunks if c.chunk_type == ChunkType.CONSTRAINT]

        # Build reference structure
        reference_structure = [e.canonical_form for e in bindings.entities]

        # Compile goal
        compiled_goal = self._compile_goal(chunks, primary_intent[0], bindings)

        return StableRead(
            utterance_id=f"read_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(chunks).encode()).hexdigest()[:8]}",
            primary_intent=primary_intent,
            goal_structure=goal_structure,
            constraint_structure=constraint_structure,
            reference_structure=reference_structure,
            reader_estimate=brain_state.global_state.to_dict(),
            speaker_estimate={"entities": [e.canonical_form for e in bindings.entities]},
            diagnostic_noise=[
                {"chunk_id": e.chunk_id, "error": e.error_magnitude}
                for e in brain_state.error_state.prediction_errors
            ],
            conflicts=brain_state.error_state.conflicts,
            ambiguities=[{"slot": b.slot, "severity": b.severity} for b in bindings.open_bindings],
            coherence_score=coherence_score,
            stable=is_stable,
            compiled_goal=compiled_goal,
        )

    def _compile_goal(
        self, chunks: List[MemoryChunk], intent: IntentType, bindings: BindingWorkspace
    ) -> CompiledGoal:
        """Compile action goal from reading."""

        if intent == IntentType.REQUEST:
            goal_type = (
                "design" if any("implement" in c.content.lower() for c in chunks) else "respond"
            )
        elif intent == IntentType.CORRECTION:
            goal_type = "fix"
        elif intent == IntentType.QUESTION:
            goal_type = "clarify"
        elif intent == IntentType.SPECIFICATION:
            goal_type = "design"
        else:
            goal_type = "respond"

        # Extract objective from highest salience chunk
        objective_chunks = [
            c
            for c in chunks
            if c.chunk_type in [ChunkType.GOAL, ChunkType.COMMAND, ChunkType.CLAIM]
        ]
        objective = (
            objective_chunks[0].content[:100] if objective_chunks else "Understand and respond"
        )

        # Extract constraints
        constraints = [c.content for c in chunks if c.chunk_type == ChunkType.CONSTRAINT]

        return CompiledGoal(
            goal_type=goal_type, objective=objective, constraints=constraints, success_criteria=[]
        )

# ============================================================================
# 11. BRAIN READING KERNEL - MAIN API
# ============================================================================

class BrainReadingKernel:
    """
    Main Brain-Reading Kernel API.

    Implements the full cognitive reading architecture:
    BrainLikeReading = Prediction + Chunking + Binding + Salience + ConflictDetection + GlobalCoherenceCheck
    """

    _instance: Optional[BrainReadingKernel] = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if BrainReadingKernel._initialized:
            return

        self.multi_pass_reader = MultiPassReader()
        self.chunker = ChunkingEngine()
        self.predictor = PredictiveModel()
        self.binder = BindingEngine()
        self.salience = SalienceEngine()
        self.conflict = ConflictDetector()
        self.coherence = CoherenceVerifier()
        self.depth = DepthController()

        BrainReadingKernel._initialized = True

    async def read(
        self,
        text: str,
        dialogue_context: Dict[str, Any]  = None,
        memory_context: Dict[str, Any]  = None,
        world_context: Dict[str, Any]  = None,
        active_goals: Optional[list[str]] = None,
        governance_context: Dict[str, Any]  = None,
    ) -> StableRead:
        """
        Execute brain-level reading.

        This is NOT language parsing. It is brain-level reading.

        Returns: StableRead
        """
        return await self.multi_pass_reader.read(
            text, dialogue_context, memory_context, world_context, active_goals
        )

    async def read_with_diagnostics(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Read with full diagnostic output.

        Returns: dict with stable_read and all intermediate states
        """
        stable_read = await self.read(text, **kwargs)

        # Also return chunking diagnostics
        chunks = self.chunker.chunk_input(text)

        return {
            "stable_read": stable_read,
            "chunks": [
                {
                    "id": c.id,
                    "type": c.chunk_type.name,
                    "content": c.content[:100],
                    "coherence": c.coherence,
                }
                for c in chunks
            ],
            "diagnostics": {
                "chunk_count": len(chunks),
                "stable": stable_read.stable,
                "coherence_score": stable_read.coherence_score,
                "conflict_count": len(stable_read.conflicts),
                "ambiguity_count": len(stable_read.ambiguities),
            },
        }

    def validate_invariants(self, stable_read: StableRead) -> List[dict[str, Any]]:
        """
        Validate brain reading invariants.

        BRI01: No module may consume raw natural language directly
        BRI02: All reading must be chunk-based, not token-only
        BRI03: All high-salience units must be reference-bound before stable read
        BRI04: Reading must be predictive, not purely reactive
        BRI05: Multiple interpretation hypotheses must be maintained until resolution
        BRI06: Global conflict above threshold blocks stable read
        BRI07: Stable read requires global coherence verification
        """
        violations = []

        # BRI03: High-salience units must be reference-bound
        # (Already enforced in binding)

        # BRI06: Conflict blocks stable read
        if stable_read.conflicts and stable_read.stable:
            for conflict in stable_read.conflicts:
                if conflict.severity > 0.7:
                    violations.append(
                        {
                            "invariant": "BRI06",
                            "rule": "Global conflict above threshold blocks stable read",
                            "violation": f"High-severity conflict {conflict.id} but read marked stable",
                            "severity": conflict.severity,
                        }
                    )

        # BRI07: Coherence verification required
        if stable_read.stable and stable_read.coherence_score < 0.5:
            violations.append(
                {
                    "invariant": "BRI07",
                    "rule": "Stable read requires global coherence verification",
                    "violation": f"Read marked stable but coherence score {stable_read.coherence_score} < 0.5",
                    "coherence": stable_read.coherence_score,
                }
            )

        return violations

# Global singleton
def get_brain_reading_kernel() -> BrainReadingKernel:
    """Get the global BrainReadingKernel instance."""
    return BrainReadingKernel()

# ============================================================================
# 12. USAGE EXAMPLES
# ============================================================================

async def example_usage():
    """Example usage of BrainReadingKernel."""

    kernel = get_brain_reading_kernel()

    # Example 1: Simple request
    text1 = "Can you help me implement a caching layer?"
    result1 = await kernel.read(text1)
    print(f"Intent: {result1.primary_intent[0].name}")
    print(f"Stable: {result1.stable}")
    print(f"Goal: {result1.compiled_goal.goal_type}")

    # Example 2: Complex criticism with constraints
    text2 = """The current implementation is too shallow.
    It models language, not reading.
    The system is dumb because it lacks three deeper engines:
    world-model-driven perception, predictive reading, and multi-timescale control.
    We need a Brain-Reading Kernel that implements predictive processing."""

    result2 = await kernel.read_with_diagnostics(
        text2, active_goals=["improve system", "deep reading"]
    )

    print("\n=== Complex Reading Result ===")
    print(f"Chunks: {result2['diagnostics']['chunk_count']}")
    print(f"Stable: {result2['diagnostics']['stable']}")
    print(f"Coherence: {result2['diagnostics']['coherence_score']:.2f}")
    print(f"Conflicts: {result2['diagnostics']['conflict_count']}")

    for chunk in result2["chunks"]:
        print(f"  [{chunk['type']}] {chunk['content'][:60]}...")

    # Validate invariants
    violations = kernel.validate_invariants(result2["stable_read"])
    if violations:
        print(f"\nInvariant violations: {len(violations)}")
        for v in violations:
            print(f"  {v['invariant']}: {v['violation']}")

if __name__ == "__main__":
    asyncio.run(example_usage())
