from __future__ import annotations

"""AMOS Deterministic Meaning Compiler v1.0
=============================================
Anti-rubbish architecture ensuring structured compilation before rendering.

Root Law: FreeGeneration = PrimaryFailureMode
Correct Path: Input → Read → Compile → TypeCheck → ConstraintCheck → Verify → Commit → Render

DMC_AMOS = (RK, MC, TC, CC, VK, CK, RR)
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc, timezone
from enum import Enum, auto

UTC = UTC
from typing import Any

# ============================================================================
# SECTION 1: TYPE SYSTEM
# ============================================================================


class SemanticType(Enum):
    """Core semantic types for the meaning graph."""

    GOAL = "goal"
    CONSTRAINT = "constraint"
    QUESTION = "question"
    INSTRUCTION = "instruction"
    ENTITY = "entity"
    STATE = "state"
    RISK = "risk"
    TIME_REF = "time_ref"
    RESOURCE = "resource"
    OUTPUT_FORMAT = "output_format"
    AMBIGUITY = "ambiguity"
    CONFLICT = "conflict"
    PROCESS = "process"


class IntentType(Enum):
    """Root intent classification."""

    REQUEST = "request"
    DESIGN = "design"
    CORRECTION = "correction"
    CLARIFICATION = "clarification"
    EXECUTION = "execution"
    QUESTION = "question"
    MIXED = "mixed"


class EdgeRelation(Enum):
    """Edge relations in the meaning graph."""

    DEPENDS_ON = "depends_on"
    BLOCKS = "blocks"
    MODIFIES = "modifies"
    TARGETS = "targets"
    CONFLICTS_WITH = "conflicts_with"
    CONSTRAINS = "constrains"
    ASKS_ABOUT = "asks_about"
    REQUIRES = "requires"


class RenderMode(Enum):
    """Anti-rubbish rendering modes."""

    JSON_PROJECTION = "json_projection"
    SCHEMA_PROJECTION = "schema_projection"
    STEP_PROJECTION = "step_projection"
    CLARIFICATION_PROJECTION = "clarification_projection"
    REFUSAL_PROJECTION = "refusal_projection"
    BOUNDED_TEXT_PROJECTION = "bounded_text_projection"


class CommitMode(Enum):
    """Commit kernel modes."""

    COMMIT_FINAL = "commit_final"
    COMMIT_PROVISIONAL = "commit_provisional"
    CLARIFY = "clarify"
    DEFER = "defer"
    BLOCK = "block"


class RubbishBugClass(Enum):
    """Error classes for rubbish detection."""

    FREE_FILL = ("RB01", "missing structure replaced by fluent text")
    CONSTRAINT_DROP = ("RB02", "explicit constraint omitted in output")
    BINDING_INVENTION = ("RB03", "unresolved reference silently guessed")
    TYPE_CONFUSION = ("RB04", "question rendered as instruction, or preference as fact")
    CONFLICT_SMOOTHING = ("RB05", "internal conflict hidden by smooth language")
    CONFIDENCE_HALLUCINATION = ("RB06", "output sounds certain despite low verification")
    RENDERER_DRIFT = ("RB07", "rendered text contains content absent from verified structure")

    def __init__(self, code: str, definition: str):
        self.code = code
        self.definition = definition


# ============================================================================
# SECTION 2: DATA STRUCTURES
# ============================================================================


@dataclass
class TypedNode:
    """A node in the Typed Meaning Graph."""

    id: str
    type: SemanticType
    value: Any
    confidence: float = 1.0
    source_span: Tuple[int, int] = None  # Position in input
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TypedEdge:
    """An edge in the Typed Meaning Graph."""

    source: str
    relation: EdgeRelation
    target: str
    confidence: float = 1.0
    weight: float = 1.0


@dataclass
class RootIntent:
    """Root intent classification with confidence."""

    type: IntentType
    confidence: float
    alternative_intents: list[Tuple[IntentType, float]] = field(default_factory=list)


@dataclass
class TypedMeaningGraph:
    """The central typed representation - no downstream module consumes raw language after this."""

    nodes: list[TypedNode] = field(default_factory=list)
    edges: list[TypedEdge] = field(default_factory=list)
    root_intent: RootIntent = None
    source_input: str = ""
    compilation_timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def get_nodes_by_type(self, node_type: SemanticType) -> list[TypedNode]:
        """Get all nodes of a specific type."""
        return [n for n in self.nodes if n.type == node_type]

    def get_outgoing_edges(self, node_id: str) -> list[TypedEdge]:
        """Get all edges originating from a node."""
        return [e for e in self.edges if e.source == node_id]

    def get_incoming_edges(self, node_id: str) -> list[TypedEdge]:
        """Get all edges targeting a node."""
        return [e for e in self.edges if e.target == node_id]

    def get_conflicts(self) -> list[Tuple[TypedNode, TypedNode]]:
        """Get all conflicting node pairs."""
        conflicts = []
        conflict_edges = [e for e in self.edges if e.relation == EdgeRelation.CONFLICTS_WITH]
        for edge in conflict_edges:
            source = next((n for n in self.nodes if n.id == edge.source), None)
            target = next((n for n in self.nodes if n.id == edge.target), None)
            if source and target:
                conflicts.append((source, target))
        return conflicts

    def get_ambiguities(self) -> list[TypedNode]:
        """Get all ambiguity nodes."""
        return self.get_nodes_by_type(SemanticType.AMBIGUITY)

    def get_unbound_requirements(self) -> list[TypedNode]:
        """Get required entities/instructions with no binding."""
        unbound = []
        for node in self.nodes:
            if node.type in (SemanticType.INSTRUCTION, SemanticType.ENTITY):
                incoming = self.get_incoming_edges(node.id)
                if not any(e.relation == EdgeRelation.TARGETS for e in incoming):
                    unbound.append(node)
        return unbound


@dataclass
class TypeCheckResult:
    """Result of type checking."""

    type_safe: bool
    errors: list[str] = field(default_factory=list)
    violations: list[Tuple[TypedNode, str]] = field(default_factory=list)


@dataclass
class ConstraintCheckResult:
    """Result of constraint checking."""

    preservation_score: float  # 0.0 to 1.0
    missing_constraints: list[str] = field(default_factory=list)
    preserved_constraints: list[str] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)


@dataclass
class VerificationResult:
    """Result of verification kernel."""

    verified: bool
    binding_complete: bool
    constraint_complete: bool
    intent_stable: bool
    type_safe: bool
    ambiguity_score: float  # 0.0 = no ambiguity, 1.0 = total ambiguity
    conflict_score: float  # 0.0 = no conflict, 1.0 = total conflict
    confidence: float
    blocking_issues: list[str] = field(default_factory=list)


@dataclass
class CommitResult:
    """Result of commit kernel."""

    mode: CommitMode
    machine_goal: MachineGoal = None
    reason: str = ""
    safe_to_proceed: bool = False


@dataclass
class MachineGoal:
    """Machine-readable output contract - only after this exists may natural language be emitted."""

    goal_type: str  # respond|clarify|plan|design|execute|defer|block
    objective: str
    constraints: list[str] = field(default_factory=list)
    required_inputs: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)
    verification_status: dict[str, Any] = field(default_factory=dict)
    typed_meaning_graph: TypedMeaningGraph = None
    compilation_timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class AntiRubbishMetrics:
    """Metrics for monitoring rubbish rates."""

    type_safety_rate: float = 0.0
    constraint_preservation_rate: float = 0.0
    binding_completion_rate: float = 0.0
    verification_pass_rate: float = 0.0
    renderer_drift_rate: float = 0.0
    clarification_rate: float = 0.0
    free_fill_rate: float = 0.0
    user_correction_rate: float = 0.0

    @property
    def rubbish_rate(self) -> float:
        """RubbishRate ≈ FreeFillRate * ConstraintDropRate * BindingInventionRate * RendererDriftRate"""
        return (
            self.free_fill_rate
            * (1.0 - self.constraint_preservation_rate)
            * (1.0 - self.binding_completion_rate)
            * self.renderer_drift_rate
        )


# ============================================================================
# SECTION 3: READING KERNEL (RK)
# ============================================================================


class ReadingKernel:
    """Stable reading of input into structured representation."""

    def __init__(self):
        self.min_confidence_threshold = 0.3

    def read(self, input_text: str) -> dict[str, Any]:
        """
        Perform stable read of input.

        Returns structured representation with:
        - segments: typed chunks of input
        - entities: detected entities
        - relations: detected relations
        - confidence: overall read confidence
        """
        segments = self._segment_input(input_text)
        entities = self._extract_entities(input_text)
        relations = self._extract_relations(input_text, entities)

        # Calculate confidence based on segment clarity
        confidence = sum(s.get("confidence", 0.5) for s in segments) / max(len(segments), 1)

        return {
            "input": input_text,
            "segments": segments,
            "entities": entities,
            "relations": relations,
            "confidence": confidence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _segment_input(self, text: str) -> list[dict[str, Any]]:
        """Break input into meaningful segments."""
        # Simple segmentation based on sentence boundaries and delimiters
        sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
        segments = []

        for i, sent in enumerate(sentences):
            sent = sent.strip()
            if not sent:
                continue

            # Detect segment type
            segment_type = self._classify_segment(sent)

            segments.append(
                {
                    "id": f"seg_{i}",
                    "text": sent,
                    "type": segment_type,
                    "confidence": self._segment_confidence(sent, segment_type),
                }
            )

        return segments

    def _classify_segment(self, text: str) -> str:
        """Classify segment by its purpose."""
        text_lower = text.lower()

        # Question detection
        if text.endswith("?") or any(
            w in text_lower for w in ["what", "how", "why", "when", "where", "who"]
        ):
            return "question"

        # Instruction detection
        if any(
            text_lower.startswith(w)
            for w in ["write", "create", "build", "implement", "fix", "refactor", "add"]
        ):
            return "instruction"

        # Constraint detection
        if any(
            w in text_lower
            for w in ["must", "should", "need to", "have to", "required", "cannot", "must not"]
        ):
            return "constraint"

        # Goal detection
        if any(w in text_lower for w in ["goal", "objective", "aim", "target", "purpose"]):
            return "goal"

        # Risk detection
        if any(
            w in text_lower
            for w in ["risk", "danger", "unsafe", "warning", "caution", "might fail"]
        ):
            return "risk"

        return "statement"

    def _segment_confidence(self, text: str, segment_type: str) -> float:
        """Calculate confidence in segment classification."""
        # Higher confidence for clear patterns
        if segment_type in ("question", "instruction"):
            return 0.9
        if segment_type == "constraint" and ("must" in text.lower() or "cannot" in text.lower()):
            return 0.85
        return 0.6

    def _extract_entities(self, text: str) -> list[dict[str, Any]]:
        """Extract named entities and concepts from text."""
        entities = []

        # Code-related entities
        code_patterns = [
            (r"\b[A-Z][a-zA-Z0-9]*(?:\.[a-zA-Z0-9_]+)*\b", "class_reference"),
            (r"\b[a-z_][a-zA-Z0-9_]*(?:\.[a-zA-Z0-9_]+)*\([^)]*\)", "function_call"),
            (r"`([^`]+)`", "code_literal"),
        ]

        for pattern, entity_type in code_patterns:
            for match in re.finditer(pattern, text):
                entities.append(
                    {
                        "text": match.group(0),
                        "type": entity_type,
                        "span": (match.start(), match.end()),
                    }
                )

        # File path entities
        file_pattern = r"\b[A-Za-z0-9_./-]+\.(?:py|js|ts|json|yaml|yml|md|txt)\b"
        for match in re.finditer(file_pattern, text):
            entities.append(
                {
                    "text": match.group(0),
                    "type": "file_path",
                    "span": (match.start(), match.end()),
                }
            )

        return entities

    def _extract_relations(self, text: str, entities: list[dict]) -> list[dict]:
        """Extract relations between entities."""
        relations = []

        # Simple proximity-based relation detection
        for i, e1 in enumerate(entities):
            for e2 in entities[i + 1 :]:
                # Check if they're close in text
                distance = abs(e1["span"][0] - e2["span"][1])
                if distance < 100:  # Within 100 chars
                    relations.append(
                        {
                            "source": e1["text"],
                            "target": e2["text"],
                            "type": "proximity",
                            "distance": distance,
                        }
                    )

        return relations


# ============================================================================
# SECTION 4: MEANING COMPILER (MC)
# ============================================================================


class MeaningCompiler:
    """
    Converts StableRead into TypedMeaningGraph.

    Rules:
    - Every explicit goal becomes a goal node
    - Every hard constraint becomes a constraint node
    - Every missing required referent becomes an ambiguity node
    - Every contradiction becomes a conflict node
    - Every requested action becomes an instruction node
    - Every safety-relevant phrase becomes a risk node
    """

    def __init__(self):
        self.node_counter = 0

    def compile(self, stable_read: dict[str, Any]) -> TypedMeaningGraph:
        """
        Compile stable read into typed meaning graph.

        Signature: compile_meaning_graph(stable_read) -> TypedMeaningGraph
        """
        self.node_counter = 0
        graph = TypedMeaningGraph(source_input=stable_read.get("input", ""))

        segments = stable_read.get("segments", [])
        entities = stable_read.get("entities", [])

        # Compile segments into nodes
        for segment in segments:
            node = self._segment_to_node(segment, entities)
            if node:
                graph.nodes.append(node)

        # Detect root intent
        graph.root_intent = self._compile_root_intent(segments)

        # Build edges between related nodes
        graph.edges = self._build_edges(graph.nodes)

        # Detect ambiguities
        self._detect_ambiguities(graph)

        # Detect conflicts
        self._detect_conflicts(graph)

        return graph

    def _next_id(self) -> str:
        """Generate unique node ID."""
        self.node_counter += 1
        return f"node_{self.node_counter:04d}"

    def _segment_to_node(self, segment: dict, entities: list[dict]) -> TypedNode:
        """Convert a segment to a typed node."""
        seg_type = segment.get("type", "statement")
        text = segment.get("text", "")
        confidence = segment.get("confidence", 0.5)

        type_mapping = {
            "goal": SemanticType.GOAL,
            "constraint": SemanticType.CONSTRAINT,
            "question": SemanticType.QUESTION,
            "instruction": SemanticType.INSTRUCTION,
            "risk": SemanticType.RISK,
            "statement": SemanticType.STATE,
        }

        node_type = type_mapping.get(seg_type, SemanticType.STATE)

        # Extract referenced entities for this segment
        segment_entities = [
            e["text"] for e in entities if segment.get("id") and self._entity_in_segment(e, text)
        ]

        return TypedNode(
            id=self._next_id(),
            type=node_type,
            value={
                "text": text,
                "entities_referenced": segment_entities,
            },
            confidence=confidence,
            source_span=segment.get("span"),
        )

    def _entity_in_segment(self, entity: dict, segment_text: str) -> bool:
        """Check if entity appears in segment text."""
        return entity["text"] in segment_text

    def _compile_root_intent(self, segments: list[dict]) -> RootIntent:
        """Determine root intent from segments."""
        if not segments:
            return RootIntent(type=IntentType.QUESTION, confidence=0.3)

        # Count segment types
        type_counts = {}
        for seg in segments:
            seg_type = seg.get("type", "statement")
            type_counts[seg_type] = type_counts.get(seg_type, 0) + 1

        # Determine primary intent
        if type_counts.get("question", 0) > 0 and type_counts.get("instruction", 0) == 0:
            return RootIntent(type=IntentType.QUESTION, confidence=0.8)

        if type_counts.get("instruction", 0) > 0:
            return RootIntent(type=IntentType.EXECUTION, confidence=0.8)

        if type_counts.get("goal", 0) > 0:
            return RootIntent(type=IntentType.DESIGN, confidence=0.7)

        if len(type_counts) > 2:
            return RootIntent(type=IntentType.MIXED, confidence=0.6)

        return RootIntent(type=IntentType.REQUEST, confidence=0.5)

    def _build_edges(self, nodes: list[TypedNode]) -> list[TypedEdge]:
        """Build edges between related nodes."""
        edges = []

        # Link constraints to goals
        goals = [n for n in nodes if n.type == SemanticType.GOAL]
        constraints = [n for n in nodes if n.type == SemanticType.CONSTRAINT]

        for constraint in constraints:
            for goal in goals:
                # Constraint constrains goal
                edges.append(
                    TypedEdge(
                        source=constraint.id,
                        relation=EdgeRelation.CONSTRAINS,
                        target=goal.id,
                        confidence=0.7,
                    )
                )

        # Link instructions to entities they target
        instructions = [n for n in nodes if n.type == SemanticType.INSTRUCTION]
        entities = [n for n in nodes if n.type == SemanticType.ENTITY]

        for instruction in instructions:
            for entity in entities:
                # Check if entity text appears in instruction
                entity_text = entity.value.get("text", "") if isinstance(entity.value, dict) else ""
                instruction_text = (
                    instruction.value.get("text", "") if isinstance(instruction.value, dict) else ""
                )
                if entity_text and entity_text in instruction_text:
                    edges.append(
                        TypedEdge(
                            source=instruction.id,
                            relation=EdgeRelation.TARGETS,
                            target=entity.id,
                            confidence=0.8,
                        )
                    )

        return edges

    def _detect_ambiguities(self, graph: TypedMeaningGraph) -> None:
        """Detect missing required referents and add ambiguity nodes."""
        instructions = [n for n in graph.nodes if n.type == SemanticType.INSTRUCTION]

        for instruction in instructions:
            instruction_text = (
                instruction.value.get("text", "") if isinstance(instruction.value, dict) else ""
            )

            # Check for vague references
            vague_patterns = ["it", "this", "that", "them", "those", "these"]
            for pattern in vague_patterns:
                if f" {pattern} " in f" {instruction_text.lower()} ":
                    # Add ambiguity node
                    ambiguity = TypedNode(
                        id=self._next_id(),
                        type=SemanticType.AMBIGUITY,
                        value={
                            "vague_reference": pattern,
                            "context": instruction_text,
                            "resolution_needed": True,
                        },
                        confidence=0.6,
                    )
                    graph.nodes.append(ambiguity)

                    # Link to instruction
                    graph.edges.append(
                        TypedEdge(
                            source=ambiguity.id,
                            relation=EdgeRelation.ASKS_ABOUT,
                            target=instruction.id,
                            confidence=0.7,
                        )
                    )

    def _detect_conflicts(self, graph: TypedMeaningGraph) -> None:
        """Detect contradictions and add conflict edges."""
        constraints = [n for n in graph.nodes if n.type == SemanticType.CONSTRAINT]

        # Check for constraint conflicts
        for i, c1 in enumerate(constraints):
            for c2 in constraints[i + 1 :]:
                c1_text = c1.value.get("text", "") if isinstance(c1.value, dict) else ""
                c2_text = c2.value.get("text", "") if isinstance(c2.value, dict) else ""

                # Simple conflict detection: negation of same concept
                if self._are_conflicting(c1_text, c2_text):
                    graph.edges.append(
                        TypedEdge(
                            source=c1.id,
                            relation=EdgeRelation.CONFLICTS_WITH,
                            target=c2.id,
                            confidence=0.75,
                        )
                    )

    def _are_conflicting(self, text1: str, text2: str) -> bool:
        """Simple conflict detection between two constraint texts."""
        text1_lower = text1.lower()
        text2_lower = text2.lower()

        # Check for direct negation
        negation_words = ["not", "no", "never", "cannot", "must not", "should not"]

        has_neg1 = any(w in text1_lower for w in negation_words)
        has_neg2 = any(w in text2_lower for w in negation_words)

        # If one has negation and other doesn't, they might conflict
        if has_neg1 != has_neg2:
            # Extract core concept (simplified)
            core1 = text1_lower
            core2 = text2_lower
            for w in negation_words + ["must", "should", "be", "the", "a", "an"]:
                core1 = core1.replace(w, "").strip()
                core2 = core2.replace(w, "").strip()

            # If cores are similar, it's a conflict
            if len(core1) > 3 and len(core2) > 3:
                similarity = self._text_similarity(core1, core2)
                return similarity > 0.6

        return False

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity metric."""
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)


# ============================================================================
# SECTION 5: TYPE CHECKER (TC)
# ============================================================================


class TypeChecker:
    """
    Type system verification for TypedMeaningGraph.

    Type Rules:
    - Instruction must target an Entity or Process
    - Constraint must attach to Goal, Instruction, OutputFormat, Resource, or TimeRef
    - Question cannot be executed
    - Ambiguity blocks executable instruction compilation
    - Conflict blocks final commit until resolved or downgraded
    - Risk must be preserved through rendering
    - OutputFormat cannot override hard constraints
    """

    def __init__(self):
        self.rules = [
            self._check_instruction_targets,
            self._check_constraint_attachments,
            self._check_question_executable,
            self._check_ambiguity_blocks,
            self._check_output_format_constraints,
        ]

    def check(self, graph: TypedMeaningGraph) -> TypeCheckResult:
        """
        Type-check the meaning graph.

        Signature: typecheck_meaning_graph(typed_meaning_graph) -> {type_safe, errors}

        Equation: TypeSafe(G) = 1 ⟺ ∀ n,e ∈ G, TypeRulesSatisfied(n,e)
        """
        errors = []
        violations = []

        for rule in self.rules:
            rule_errors, rule_violations = rule(graph)
            errors.extend(rule_errors)
            violations.extend(rule_violations)

        type_safe = len(errors) == 0

        return TypeCheckResult(
            type_safe=type_safe,
            errors=errors,
            violations=violations,
        )

    def _check_instruction_targets(
        self, graph: TypedMeaningGraph
    ) -> Tuple[list[str], list[tuple[TypedNode, str]]]:
        """Rule: Instruction must target an Entity or Process."""
        errors = []
        violations = []

        instructions = [n for n in graph.nodes if n.type == SemanticType.INSTRUCTION]

        for instruction in instructions:
            outgoing = graph.get_outgoing_edges(instruction.id)
            targets_entity = any(e.relation == EdgeRelation.TARGETS for e in outgoing)

            if not targets_entity:
                errors.append(f"Instruction '{instruction.id}' has no target entity")
                violations.append((instruction, "instruction_without_target"))

        return errors, violations

    def _check_constraint_attachments(
        self, graph: TypedMeaningGraph
    ) -> Tuple[list[str], list[tuple[TypedNode, str]]]:
        """Rule: Constraint must attach to valid target types."""
        errors = []
        violations = []

        valid_targets = {
            SemanticType.GOAL,
            SemanticType.INSTRUCTION,
            SemanticType.OUTPUT_FORMAT,
            SemanticType.RESOURCE,
            SemanticType.TIME_REF,
        }

        constraints = [n for n in graph.nodes if n.type == SemanticType.CONSTRAINT]

        for constraint in constraints:
            outgoing = graph.get_outgoing_edges(constraint.id)
            constrains_valid = any(
                e.relation == EdgeRelation.CONSTRAINS
                and any(n.id == e.target and n.type in valid_targets for n in graph.nodes)
                for e in outgoing
            )

            if not constrains_valid:
                errors.append(f"Constraint '{constraint.id}' not attached to valid target")
                violations.append((constraint, "constraint_without_valid_target"))

        return errors, violations

    def _check_question_executable(
        self, graph: TypedMeaningGraph
    ) -> Tuple[list[str], list[tuple[TypedNode, str]]]:
        """Rule: Question cannot be executed (marked as instruction)."""
        errors = []
        violations = []

        questions = [n for n in graph.nodes if n.type == SemanticType.QUESTION]

        for question in questions:
            # Check if question has outgoing TARGETS edges (treated as executable)
            outgoing = graph.get_outgoing_edges(question.id)
            has_target = any(e.relation == EdgeRelation.TARGETS for e in outgoing)

            if has_target:
                errors.append(f"Question '{question.id}' incorrectly marked as executable")
                violations.append((question, "question_marked_executable"))

        return errors, violations

    def _check_ambiguity_blocks(
        self, graph: TypedMeaningGraph
    ) -> Tuple[list[str], list[tuple[TypedNode, str]]]:
        """Rule: Ambiguity blocks executable instruction compilation."""
        errors = []
        violations = []

        ambiguities = [n for n in graph.nodes if n.type == SemanticType.AMBIGUITY]

        for ambiguity in ambiguities:
            # Check if this ambiguity is linked to an instruction
            outgoing = graph.get_outgoing_edges(ambiguity.id)
            blocks_instruction = any(
                e.relation == EdgeRelation.ASKS_ABOUT
                and any(
                    n.id == e.target and n.type == SemanticType.INSTRUCTION for n in graph.nodes
                )
                for e in outgoing
            )

            if blocks_instruction:
                errors.append(f"Ambiguity '{ambiguity.id}' blocks executable instruction")
                violations.append((ambiguity, "ambiguity_blocks_execution"))

        return errors, violations

    def _check_output_format_constraints(
        self, graph: TypedMeaningGraph
    ) -> Tuple[list[str], list[tuple[TypedNode, str]]]:
        """Rule: OutputFormat cannot override hard constraints."""
        # This would require tracking constraint priority - simplified version
        return [], []


# ============================================================================
# SECTION 6: CONSTRAINT CHECKER (CC)
# ============================================================================


class ConstraintChecker:
    """
    Explicit constraint preservation verification.

    Checks:
    - All hard constraints preserved
    - All user-requested format constraints preserved
    - All safety constraints preserved
    - All execution constraints preserved
    - No inferred content overrides explicit constraints

    Constraint preservation score: ConstraintPreservation = PreservedConstraints / RequiredConstraints
    Commit condition: ConstraintPreservation = 1.0
    """

    def __init__(self):
        self.active_constraints: list[str] = []

    def check(
        self, graph: TypedMeaningGraph, required_constraints: list[str] = None
    ) -> ConstraintCheckResult:
        """
        Check constraint preservation.

        Signature: check_constraints(typed_meaning_graph, active_constraints) -> {preservation_score, missing_constraints}
        """
        required = required_constraints or []

        # Extract constraints from graph
        graph_constraints = [
            n.value.get("text", "") if isinstance(n.value, dict) else str(n.value)
            for n in graph.nodes
            if n.type == SemanticType.CONSTRAINT
        ]

        # All required constraints should appear in graph
        preserved = []
        missing = []

        for req in required:
            # Check if this required constraint is represented
            is_preserved = any(self._constraint_matches(req, gc) for gc in graph_constraints)

            if is_preserved:
                preserved.append(req)
            else:
                missing.append(req)

        # Also check for inferred constraint violations
        violations = self._check_inferred_violations(graph, required)

        preservation_score = len(preserved) / max(len(required), 1)

        return ConstraintCheckResult(
            preservation_score=preservation_score,
            missing_constraints=missing,
            preserved_constraints=preserved,
            violations=violations,
        )

    def _constraint_matches(self, required: str, graph_constraint: str) -> bool:
        """Check if a graph constraint matches a required constraint."""
        # Simple text matching - could be enhanced with semantic similarity
        req_lower = required.lower()
        gc_lower = graph_constraint.lower()

        return (
            req_lower in gc_lower
            or gc_lower in req_lower
            or self._similarity(req_lower, gc_lower) > 0.7
        )

    def _similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity."""
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

    def _check_inferred_violations(
        self, graph: TypedMeaningGraph, required: list[str]
    ) -> list[str]:
        """Check if inferred content overrides explicit constraints."""
        violations = []

        # Check for goals that might violate constraints
        goals = [n for n in graph.nodes if n.type == SemanticType.GOAL]
        constraints = [n for n in graph.nodes if n.type == SemanticType.CONSTRAINT]

        for goal in goals:
            goal_text = goal.value.get("text", "") if isinstance(goal.value, dict) else ""

            for constraint in constraints:
                constraint_text = (
                    constraint.value.get("text", "") if isinstance(constraint.value, dict) else ""
                )

                # Check if goal contradicts constraint
                if self._are_contradictory(goal_text, constraint_text):
                    violations.append(
                        f"Goal '{goal_text}' may violate constraint '{constraint_text}'"
                    )

        return violations

    def _are_contradictory(self, text1: str, text2: str) -> bool:
        """Simple contradiction detection."""
        # Look for opposite actions
        negation_indicators = ["not", "no", "never", "cannot", "must not", "should not"]

        t1_has_neg = any(ind in text1.lower() for ind in negation_indicators)
        t2_has_neg = any(ind in text2.lower() for ind in negation_indicators)

        return t1_has_neg != t2_has_neg and self._similarity(text1, text2) > 0.5


# ============================================================================
# SECTION 7: VERIFICATION KERNEL (VK)
# ============================================================================


class VerificationKernel:
    """
    Prove internal adequacy before text rendering.

    Checks:
    - binding_complete
    - constraint_complete
    - root_intent_stable
    - conflict_below_threshold
    - ambiguity_below_threshold
    - type_safe
    - goal_output_match

    Equation:
    Verified = 𝟙[
        BindingComplete ∧ ConstraintComplete ∧ IntentStable ∧ TypeSafe ∧
        Conflict ≤ τ_c ∧ Ambiguity ≤ τ_a
    ]
    """

    def __init__(self):
        self.conflict_threshold = 0.3  # τ_c
        self.ambiguity_threshold = 0.3  # τ_a
        self.min_confidence = 0.5

    def verify(
        self,
        graph: TypedMeaningGraph,
        type_result: TypeCheckResult,
        constraint_result: ConstraintCheckResult,
        governance_state: dict[str, Any] = None,
        epistemic_state: dict[str, Any] = None,
    ) -> VerificationResult:
        """
        Verify machine goal adequacy.

        Signature: verify_machine_goal(typed_meaning_graph, governance_state, epistemic_state) -> {verified, ambiguity_score, conflict_score, confidence}
        """
        # Check binding completeness
        unbound = graph.get_unbound_requirements()
        binding_complete = len(unbound) == 0

        # Check constraint completeness
        constraint_complete = constraint_result.preservation_score >= 1.0

        # Check intent stability
        intent_stable = (
            graph.root_intent is not None and graph.root_intent.confidence >= self.min_confidence
        )

        # Calculate scores
        conflicts = graph.get_conflicts()
        ambiguities = graph.get_ambiguities()

        conflict_score = min(len(conflicts) / max(len(graph.nodes), 1), 1.0)
        ambiguity_score = min(len(ambiguities) / max(len(graph.nodes), 1), 1.0)

        # Type safety from type checker
        type_safe = type_result.type_safe

        # Overall confidence
        confidence = self._calculate_confidence(
            graph, binding_complete, constraint_complete, intent_stable, type_safe
        )

        # Determine if verified
        verified = (
            binding_complete
            and constraint_complete
            and intent_stable
            and type_safe
            and conflict_score <= self.conflict_threshold
            and ambiguity_score <= self.ambiguity_threshold
        )

        # Collect blocking issues
        blocking_issues = []
        if not binding_complete:
            blocking_issues.append(f"Unbound requirements: {[n.id for n in unbound]}")
        if not constraint_complete:
            blocking_issues.append(f"Missing constraints: {constraint_result.missing_constraints}")
        if not intent_stable:
            blocking_issues.append("Intent unstable or unclear")
        if not type_safe:
            blocking_issues.extend(type_result.errors)
        if conflict_score > self.conflict_threshold:
            blocking_issues.append(
                f"Conflict score {conflict_score:.2f} exceeds threshold {self.conflict_threshold}"
            )
        if ambiguity_score > self.ambiguity_threshold:
            blocking_issues.append(
                f"Ambiguity score {ambiguity_score:.2f} exceeds threshold {self.ambiguity_threshold}"
            )

        return VerificationResult(
            verified=verified,
            binding_complete=binding_complete,
            constraint_complete=constraint_complete,
            intent_stable=intent_stable,
            type_safe=type_safe,
            ambiguity_score=ambiguity_score,
            conflict_score=conflict_score,
            confidence=confidence,
            blocking_issues=blocking_issues,
        )

    def _calculate_confidence(
        self,
        graph: TypedMeaningGraph,
        binding_complete: bool,
        constraint_complete: bool,
        intent_stable: bool,
        type_safe: bool,
    ) -> float:
        """Calculate overall confidence score."""
        # Average node confidence
        node_confidences = [n.confidence for n in graph.nodes] if graph.nodes else [0.5]
        avg_node_confidence = sum(node_confidences) / len(node_confidences)

        # Structural factors
        structural_score = (
            sum(
                [
                    binding_complete,
                    constraint_complete,
                    intent_stable,
                    type_safe,
                ]
            )
            / 4.0
        )

        return (avg_node_confidence + structural_score) / 2.0


# ============================================================================
# SECTION 8: COMMIT KERNEL (CK)
# ============================================================================


class CommitKernel:
    """
    Do not "say something" unless a valid compiled object exists.

    Commit Laws:
    CommitFinal ⟺ Verified=1 ∧ Confidence ≥ τ_c
    CommitProvisional ⟺ Verified=0 ∧ Clarifiable=1 ∧ SafeToRespond=1
    Block ⟺ Unsafe ∨ UnresolvedConflict ∨ GovernanceDenied
    """

    def __init__(self):
        self.min_confidence_for_final = 0.7  # τ_c

    def commit(
        self,
        graph: TypedMeaningGraph,
        verification: VerificationResult,
        governance_state: dict[str, Any] = None,
    ) -> CommitResult:
        """
        Commit machine goal.

        Signature: commit_machine_goal(verified_machine_goal) -> commit_final|commit_provisional|clarify|defer|block
        """
        # Check for governance denial
        if governance_state and governance_state.get("denied"):
            return CommitResult(
                mode=CommitMode.BLOCK,
                reason=f"Governance denied: {governance_state.get('reason', 'unknown')}",
                safe_to_proceed=False,
            )

        # Check for safety issues
        if self._is_unsafe(graph, verification):
            return CommitResult(
                mode=CommitMode.BLOCK,
                reason="Safety check failed",
                safe_to_proceed=False,
            )

        # Determine commit mode
        if verification.verified and verification.confidence >= self.min_confidence_for_final:
            # Full commit
            machine_goal = self._build_machine_goal(graph, verification, "final")
            return CommitResult(
                mode=CommitMode.COMMIT_FINAL,
                machine_goal=machine_goal,
                reason="Verified with sufficient confidence",
                safe_to_proceed=True,
            )

        elif verification.verified:
            # Verified but low confidence - provisional
            machine_goal = self._build_machine_goal(graph, verification, "provisional")
            return CommitResult(
                mode=CommitMode.COMMIT_PROVISIONAL,
                machine_goal=machine_goal,
                reason="Verified but low confidence",
                safe_to_proceed=True,
            )

        elif self._is_clarifiable(verification):
            # Can be clarified
            return CommitResult(
                mode=CommitMode.CLARIFY,
                reason=f"Clarification needed: {'; '.join(verification.blocking_issues[:3])}",
                safe_to_proceed=False,
            )

        elif verification.confidence > 0.3:
            # Can defer with partial understanding
            machine_goal = self._build_machine_goal(graph, verification, "deferred")
            return CommitResult(
                mode=CommitMode.DEFER,
                machine_goal=machine_goal,
                reason="Insufficient verification, deferring",
                safe_to_proceed=False,
            )

        else:
            # Block - too uncertain
            return CommitResult(
                mode=CommitMode.BLOCK,
                reason=f"Cannot proceed: {'; '.join(verification.blocking_issues[:3])}",
                safe_to_proceed=False,
            )

    def _is_unsafe(self, graph: TypedMeaningGraph, verification: VerificationResult) -> bool:
        """Check if proceeding would be unsafe."""
        # Check for critical risks
        risks = [n for n in graph.nodes if n.type == SemanticType.RISK]

        for risk in risks:
            risk_value = risk.value if isinstance(risk.value, dict) else {}
            if risk_value.get("severity") == "critical":
                return True

        return False

    def _is_clarifiable(self, verification: VerificationResult) -> bool:
        """Check if issues can be resolved through clarification."""
        # Ambiguities can be clarified
        if verification.ambiguity_score > 0:
            return True

        # Some binding issues can be clarified
        if not verification.binding_complete:
            return True

        return False

    def _build_machine_goal(
        self, graph: TypedMeaningGraph, verification: VerificationResult, commit_type: str
    ) -> MachineGoal:
        """Build the machine-readable goal object."""
        # Determine goal type from root intent
        intent_to_goal = {
            IntentType.REQUEST: "respond",
            IntentType.DESIGN: "design",
            IntentType.CORRECTION: "execute",
            IntentType.CLARIFICATION: "clarify",
            IntentType.EXECUTION: "execute",
            IntentType.QUESTION: "respond",
            IntentType.MIXED: "plan",
        }

        goal_type = intent_to_goal.get(
            graph.root_intent.type if graph.root_intent else IntentType.REQUEST, "respond"
        )

        # If deferred or provisional, adjust
        if commit_type == "deferred":
            goal_type = "defer"

        # Build objective from goals or instructions
        goals = [n for n in graph.nodes if n.type == SemanticType.GOAL]
        instructions = [n for n in graph.nodes if n.type == SemanticType.INSTRUCTION]

        if goals:
            objective = (
                goals[0].value.get("text", "")
                if isinstance(goals[0].value, dict)
                else str(goals[0].value)
            )
        elif instructions:
            objective = (
                instructions[0].value.get("text", "")
                if isinstance(instructions[0].value, dict)
                else str(instructions[0].value)
            )
        else:
            objective = graph.source_input[:200]  # Truncate input

        # Extract constraints
        constraints = [
            n.value.get("text", "") if isinstance(n.value, dict) else str(n.value)
            for n in graph.nodes
            if n.type == SemanticType.CONSTRAINT
        ]

        # Required inputs for unbound entities
        required_inputs = []
        for node in graph.get_unbound_requirements():
            node_text = (
                node.value.get("text", "") if isinstance(node.value, dict) else str(node.value)
            )
            required_inputs.append(f"Clarify: {node_text}")

        # Add ambiguities as required inputs
        for ambiguity in graph.get_ambiguities():
            amb_value = ambiguity.value if isinstance(ambiguity.value, dict) else {}
            vague_ref = amb_value.get("vague_reference", "unknown")
            required_inputs.append(f"Resolve ambiguity: '{vague_ref}'")

        return MachineGoal(
            goal_type=goal_type,
            objective=objective,
            constraints=constraints,
            required_inputs=required_inputs,
            success_criteria=[
                "Type-safe output generated",
                "All constraints preserved",
                "No renderer drift detected",
            ],
            verification_status={
                "type_safe": verification.type_safe,
                "constraint_complete": verification.constraint_complete,
                "binding_complete": verification.binding_complete,
                "ambiguity_score": verification.ambiguity_score,
                "conflict_score": verification.conflict_score,
                "confidence": verification.confidence,
                "commit_type": commit_type,
            },
            typed_meaning_graph=graph,
        )


# ============================================================================
# SECTION 9: RESTRICTED RENDERER (RR)
# ============================================================================


class RestrictedRenderer:
    """
    Anti-rubbish layer - text generation constrained by compiled objects.

    Root Rule:
    Renderer(Text) = DeterministicProjection(VerifiedStructure)

    NOT:
    Renderer(Text) = FreeCompletion

    Forbidden Operations:
    - invent_missing_constraints
    - invent_missing_bindings
    - invent_confidence
    - replace conflict with fluency
    - fill unknowns with prose
    """

    def __init__(self):
        self.allowed_operations = {
            "project_goal_structure_to_text",
            "project_constraints_to_text",
            "project_conflicts_to_text",
            "project_ambiguities_to_clarification_questions",
            "project_verified_plan_to_steps",
            "project_schema_to_json",
        }

    def render(
        self,
        machine_goal: MachineGoal,
        render_mode: RenderMode = RenderMode.JSON_PROJECTION,
        drift_check: bool = True,
    ) -> dict[str, Any]:
        """
        Render restricted output.

        Signature: render_restricted_output(committed_goal, render_mode) -> output
        """
        if not machine_goal:
            return {
                "output": None,
                "render_mode": render_mode.value,
                "error": "No machine goal to render",
                "drift_detected": False,
            }

        # Select rendering strategy
        if render_mode == RenderMode.JSON_PROJECTION:
            output = self._render_json_projection(machine_goal)
        elif render_mode == RenderMode.SCHEMA_PROJECTION:
            output = self._render_schema_projection(machine_goal)
        elif render_mode == RenderMode.STEP_PROJECTION:
            output = self._render_step_projection(machine_goal)
        elif render_mode == RenderMode.CLARIFICATION_PROJECTION:
            output = self._render_clarification(machine_goal)
        elif render_mode == RenderMode.REFUSAL_PROJECTION:
            output = self._render_refusal(machine_goal)
        elif render_mode == RenderMode.BOUNDED_TEXT_PROJECTION:
            output = self._render_bounded_text(machine_goal)
        else:
            output = self._render_json_projection(machine_goal)

        # Check for renderer drift
        drift_result = None
        if drift_check:
            drift_result = self.check_renderer_drift(output, machine_goal)

        return {
            "output": output,
            "render_mode": render_mode.value,
            "goal_type": machine_goal.goal_type,
            "verification_status": machine_goal.verification_status,
            "drift_check": drift_result,
            "safe_render": drift_result.get("drift_found", True) is False if drift_result else True,
        }

    def _render_json_projection(self, machine_goal: MachineGoal) -> dict:
        """Render as structured JSON projection."""
        return {
            "goal_type": machine_goal.goal_type,
            "objective": machine_goal.objective,
            "constraints": machine_goal.constraints,
            "required_inputs": machine_goal.required_inputs,
            "success_criteria": machine_goal.success_criteria,
            "verification": machine_goal.verification_status,
        }

    def _render_schema_projection(self, machine_goal: MachineGoal) -> dict:
        """Render as schema-validated structure."""
        return {
            "schema_version": "1.0",
            "schema_type": "machine_goal",
            "goal": {
                "type": machine_goal.goal_type,
                "objective": machine_goal.objective,
                "constraints": machine_goal.constraints,
            },
            "execution_requirements": {
                "required_inputs": machine_goal.required_inputs,
                "success_criteria": machine_goal.success_criteria,
            },
            "verification": machine_goal.verification_status,
        }

    def _render_step_projection(self, machine_goal: MachineGoal) -> dict:
        """Render as step-by-step plan."""
        steps = []

        # Input resolution steps
        for req in machine_goal.required_inputs:
            steps.append(
                {
                    "step": len(steps) + 1,
                    "action": "resolve_input",
                    "description": req,
                    "blocking": True,
                }
            )

        # Constraint verification steps
        for constraint in machine_goal.constraints:
            steps.append(
                {
                    "step": len(steps) + 1,
                    "action": "verify_constraint",
                    "description": f"Ensure: {constraint}",
                    "blocking": False,
                }
            )

        # Main execution step
        steps.append(
            {
                "step": len(steps) + 1,
                "action": "execute_goal",
                "description": machine_goal.objective,
                "blocking": False,
            }
        )

        return {
            "plan_type": "step_by_step",
            "total_steps": len(steps),
            "steps": steps,
            "goal": machine_goal.objective,
        }

    def _render_clarification(self, machine_goal: MachineGoal) -> dict:
        """Render as clarification request."""
        return {
            "response_type": "clarification_request",
            "clarifications_needed": machine_goal.required_inputs,
            "partial_understanding": {
                "goal_type": machine_goal.goal_type,
                "inferred_objective": machine_goal.objective,
                "identified_constraints": machine_goal.constraints,
            },
            "questions": [
                {"id": i + 1, "question": q} for i, q in enumerate(machine_goal.required_inputs)
            ],
        }

    def _render_refusal(self, machine_goal: MachineGoal) -> dict:
        """Render as refusal with explanation."""
        return {
            "response_type": "refusal",
            "reason": "Cannot proceed with current information",
            "missing_requirements": machine_goal.required_inputs,
            "identified_risks": [
                "Insufficient verification",
                "Ambiguity in input",
            ],
            "suggestion": "Please provide clarification on the listed requirements",
        }

    def _render_bounded_text(self, machine_goal: MachineGoal) -> dict:
        """Render as bounded natural language (last resort for precision tasks)."""
        # Only include verified content
        parts = []

        if machine_goal.goal_type:
            parts.append(f"Goal Type: {machine_goal.goal_type}")

        if machine_goal.objective:
            parts.append(f"Objective: {machine_goal.objective}")

        if machine_goal.constraints:
            parts.append("Constraints:")
            for c in machine_goal.constraints:
                parts.append(f"  - {c}")

        if machine_goal.required_inputs:
            parts.append("Required Input:")
            for r in machine_goal.required_inputs:
                parts.append(f"  - {r}")

        return {
            "response_type": "bounded_text",
            "text": "\n".join(parts),
            "bounded": True,
            "inferred_content": False,
        }

    def check_renderer_drift(
        self, rendered_output: Any, machine_goal: MachineGoal
    ) -> dict[str, Any]:
        """
        Check for drift between verified structure and rendered text.

        RendererDrift = Content(RenderedText) - Content(VerifiedStructure)

        Rule: All substantive claims in rendered text must map to nodes or edges in verified structure.
        """
        drift_found = False
        unmapped_claims = []

        # Extract claims from rendered output
        rendered_text = (
            json.dumps(rendered_output) if not isinstance(rendered_output, str) else rendered_output
        )

        # Check for claims not in machine goal
        goal_claims = self._extract_claims_from_goal(machine_goal)
        rendered_claims = self._extract_claims(rendered_text)

        for claim in rendered_claims:
            if not self._claim_in_goal(claim, goal_claims):
                drift_found = True
                unmapped_claims.append(claim)

        # Check for invented confidence
        if "confidence" in rendered_text.lower():
            verified_confidence = machine_goal.verification_status.get("confidence", 0.0)
            # If rendered claims certainty but verification is low
            if verified_confidence < 0.7 and "high" in rendered_text.lower():
                drift_found = True
                unmapped_claims.append("invented high confidence")

        return {
            "drift_found": drift_found,
            "unmapped_claims": unmapped_claims,
            "drift_rate": len(unmapped_claims) / max(len(rendered_claims), 1),
        }

    def _extract_claims_from_goal(self, machine_goal: MachineGoal) -> set[str]:
        """Extract verifiable claims from machine goal."""
        claims = set()

        claims.add(machine_goal.goal_type.lower())
        claims.add(machine_goal.objective.lower())

        for c in machine_goal.constraints:
            claims.add(c.lower())

        for r in machine_goal.required_inputs:
            claims.add(r.lower())

        return claims

    def _extract_claims(self, text: str) -> list[str]:
        """Extract claims from rendered text."""
        # Simple sentence extraction
        sentences = re.split(r"[.!?]+", text)
        return [s.strip().lower() for s in sentences if len(s.strip()) > 10]

    def _claim_in_goal(self, claim: str, goal_claims: Set[str]) -> bool:
        """Check if a rendered claim exists in goal claims."""
        # Simple substring matching - could be enhanced
        for gc in goal_claims:
            if claim in gc or gc in claim:
                return True
        return False


# ============================================================================
# SECTION 10: ANTI-RUBBISH STATE MACHINE
# ============================================================================


class AntiRubbishStateMachine:
    """
    State machine governing the compilation pipeline.

    States: RAW_INPUT → READ → COMPILED → TYPECHECKED → CONSTRAINT_CHECKED →
            VERIFIED → COMMITTED → RENDERED | CLARIFY | DEFER | BLOCK
    """

    class State(Enum):
        RAW_INPUT = auto()
        READ = auto()
        COMPILED = auto()
        TYPECHECKED = auto()
        CONSTRAINT_CHECKED = auto()
        VERIFIED = auto()
        COMMITTED = auto()
        RENDERED = auto()
        CLARIFY = auto()
        DEFER = auto()
        BLOCK = auto()

    def __init__(self):
        self.state = self.State.RAW_INPUT
        self.history: list[tuple[str, str]] = []  # (state, reason)

    def transition(self, to_state: State, reason: str = "") -> bool:
        """Attempt state transition."""
        valid_transitions = {
            self.State.RAW_INPUT: {self.State.READ},
            self.State.READ: {self.State.COMPILED, self.State.CLARIFY, self.State.BLOCK},
            self.State.COMPILED: {self.State.TYPECHECKED, self.State.CLARIFY, self.State.BLOCK},
            self.State.TYPECHECKED: {
                self.State.CONSTRAINT_CHECKED,
                self.State.CLARIFY,
                self.State.BLOCK,
            },
            self.State.CONSTRAINT_CHECKED: {
                self.State.VERIFIED,
                self.State.CLARIFY,
                self.State.BLOCK,
            },
            self.State.VERIFIED: {self.State.COMMITTED, self.State.DEFER, self.State.BLOCK},
            self.State.COMMITTED: {self.State.RENDERED, self.State.BLOCK},
            self.State.CLARIFY: {self.State.RAW_INPUT},  # Can restart after clarification
            self.State.DEFER: {self.State.RAW_INPUT},
            self.State.BLOCK: set(),  # Terminal
            self.State.RENDERED: set(),  # Terminal
        }

        if to_state in valid_transitions.get(self.state, set()):
            self.history.append((self.state.name, reason))
            self.state = to_state
            return True
        return False

    def can_render(self) -> bool:
        """Check if rendering is allowed."""
        return self.state == self.State.COMMITTED

    def must_clarify(self) -> bool:
        """Check if clarification is required."""
        return self.state == self.State.CLARIFY

    def is_blocked(self) -> bool:
        """Check if processing is blocked."""
        return self.state == self.State.BLOCK


# ============================================================================
# SECTION 11: DETERMINISTIC MEANING COMPILER - MAIN ORCHESTRATOR
# ============================================================================


class DeterministicMeaningCompiler:
    """
    Main orchestrator for the AMOS Deterministic Meaning Compiler.

    DMC_AMOS = (RK, MC, TC, CC, VK, CK, RR)

    Output equation:
    Output_t = Render(Commit(Verify(CheckConstraints(TypeCheck(Compile(Read(Input_t)))))))

    If any stage fails: Render = blocked ∨ clarify ∨ defer

    Strongest Invariant:
    If it cannot be compiled, typed, checked, and verified, it must not be said as fact.
    """

    def __init__(self):
        # Initialize all kernels
        self.reading_kernel = ReadingKernel()
        self.meaning_compiler = MeaningCompiler()
        self.type_checker = TypeChecker()
        self.constraint_checker = ConstraintChecker()
        self.verification_kernel = VerificationKernel()
        self.commit_kernel = CommitKernel()
        self.restricted_renderer = RestrictedRenderer()

        # State machine
        self.state_machine = AntiRubbishStateMachine()

        # Metrics tracking
        self.metrics = AntiRubbishMetrics()

    def process(
        self,
        input_text: str,
        required_constraints: list[str] = None,
        governance_state: dict[str, Any] = None,
        render_mode: RenderMode = RenderMode.JSON_PROJECTION,
    ) -> dict[str, Any]:
        """
        Process input through the full deterministic meaning compiler pipeline.

        Args:
            input_text: Raw user input
            required_constraints: List of required constraints to preserve
            governance_state: Optional governance restrictions
            render_mode: Output rendering mode

        Returns:
            Full processing result with all stages, final output, and metrics
        """
        # Reset state
        self.state_machine = AntiRubbishStateMachine()
        pipeline_start = datetime.now(timezone.utc)

        result = {
            "input": input_text,
            "pipeline_start": pipeline_start.isoformat(),
            "stages": {},
            "final_output": None,
            "commit_mode": None,
            "state_history": [],
            "metrics": {},
            "success": False,
        }

        # Stage 1: READ
        self.state_machine.transition(self.state_machine.State.READ, "Starting read")
        stable_read = self.reading_kernel.read(input_text)
        result["stages"]["read"] = {
            "confidence": stable_read.get("confidence"),
            "segments_count": len(stable_read.get("segments", [])),
            "entities_count": len(stable_read.get("entities", [])),
        }

        # Stage 2: COMPILE
        self.state_machine.transition(self.state_machine.State.COMPILED, "Compiling meaning graph")
        meaning_graph = self.meaning_compiler.compile(stable_read)
        result["stages"]["compile"] = {
            "nodes_count": len(meaning_graph.nodes),
            "edges_count": len(meaning_graph.edges),
            "root_intent": meaning_graph.root_intent.type.value
            if meaning_graph.root_intent
            else None,
            "ambiguities": len(meaning_graph.get_ambiguities()),
            "conflicts": len(meaning_graph.get_conflicts()),
        }

        # Stage 3: TYPECHECK
        self.state_machine.transition(self.state_machine.State.TYPECHECKED, "Type checking")
        type_result = self.type_checker.check(meaning_graph)
        result["stages"]["typecheck"] = {
            "type_safe": type_result.type_safe,
            "errors": type_result.errors,
            "violations_count": len(type_result.violations),
        }

        # Stage 4: CONSTRAINT CHECK
        self.state_machine.transition(
            self.state_machine.State.CONSTRAINT_CHECKED, "Checking constraints"
        )
        constraint_result = self.constraint_checker.check(meaning_graph, required_constraints)
        result["stages"]["constraint_check"] = {
            "preservation_score": constraint_result.preservation_score,
            "missing_constraints": constraint_result.missing_constraints,
            "violations": constraint_result.violations,
        }

        # Stage 5: VERIFY
        self.state_machine.transition(self.state_machine.State.VERIFIED, "Verification")
        verification = self.verification_kernel.verify(
            meaning_graph,
            type_result,
            constraint_result,
            governance_state,
        )
        result["stages"]["verify"] = {
            "verified": verification.verified,
            "binding_complete": verification.binding_complete,
            "constraint_complete": verification.constraint_complete,
            "intent_stable": verification.intent_stable,
            "ambiguity_score": verification.ambiguity_score,
            "conflict_score": verification.conflict_score,
            "confidence": verification.confidence,
            "blocking_issues": verification.blocking_issues,
        }

        # Stage 6: COMMIT
        commit_result = self.commit_kernel.commit(meaning_graph, verification, governance_state)
        self.state_machine.transition(
            self.state_machine.State.COMMITTED
            if commit_result.mode == CommitMode.COMMIT_FINAL
            else self.state_machine.State.CLARIFY
            if commit_result.mode == CommitMode.CLARIFY
            else self.state_machine.State.DEFER
            if commit_result.mode == CommitMode.DEFER
            else self.state_machine.State.BLOCK,
            commit_result.reason,
        )

        result["stages"]["commit"] = {
            "mode": commit_result.mode.value,
            "reason": commit_result.reason,
            "safe_to_proceed": commit_result.safe_to_proceed,
        }
        result["commit_mode"] = commit_result.mode.value

        # Stage 7: RENDER (only if committed)
        final_output = None
        if commit_result.mode in (CommitMode.COMMIT_FINAL, CommitMode.COMMIT_PROVISIONAL):
            self.state_machine.transition(self.state_machine.State.RENDERED, "Rendering output")
            render_result = self.restricted_renderer.render(
                commit_result.machine_goal, render_mode, drift_check=True
            )
            final_output = render_result
            result["stages"]["render"] = {
                "render_mode": render_result["render_mode"],
                "goal_type": render_result["goal_type"],
                "safe_render": render_result["safe_render"],
                "drift_detected": render_result["drift_check"]["drift_found"]
                if render_result["drift_check"]
                else None,
            }

            # Update metrics
            self.metrics.type_safety_rate = 1.0 if type_result.type_safe else 0.0
            self.metrics.constraint_preservation_rate = constraint_result.preservation_score
            self.metrics.binding_completion_rate = 1.0 if verification.binding_complete else 0.0
            self.metrics.verification_pass_rate = 1.0 if verification.verified else 0.0
            self.metrics.renderer_drift_rate = (
                render_result["drift_check"]["drift_rate"] if render_result["drift_check"] else 0.0
            )
            self.metrics.clarification_rate = (
                1.0 if commit_result.mode == CommitMode.CLARIFY else 0.0
            )

            result["success"] = True

        elif commit_result.mode == CommitMode.CLARIFY:
            # Return clarification request
            final_output = {
                "response_type": "clarification_required",
                "reason": commit_result.reason,
                "clarifications_needed": commit_result.machine_goal.required_inputs
                if commit_result.machine_goal
                else [],
            }

        elif commit_result.mode == CommitMode.DEFER:
            final_output = {
                "response_type": "deferred",
                "reason": commit_result.reason,
                "partial_goal": self.restricted_renderer._render_json_projection(
                    commit_result.machine_goal
                )
                if commit_result.machine_goal
                else None,
            }

        else:  # BLOCK
            final_output = {
                "response_type": "blocked",
                "reason": commit_result.reason,
            }

        # Finalize result
        result["final_output"] = final_output
        result["state_history"] = self.state_machine.history
        result["metrics"] = {
            "type_safety_rate": self.metrics.type_safety_rate,
            "constraint_preservation_rate": self.metrics.constraint_preservation_rate,
            "binding_completion_rate": self.metrics.binding_completion_rate,
            "verification_pass_rate": self.metrics.verification_pass_rate,
            "renderer_drift_rate": self.metrics.renderer_drift_rate,
            "clarification_rate": self.metrics.clarification_rate,
            "rubbish_rate": self.metrics.rubbish_rate,
        }
        result["pipeline_end"] = datetime.now(timezone.utc).isoformat()

        return result

    def get_metrics(self) -> AntiRubbishMetrics:
        """Get current anti-rubbish metrics."""
        return self.metrics


# ============================================================================
# SECTION 12: CONVENIENCE FUNCTIONS
# ============================================================================


def compile_input(
    input_text: str,
    required_constraints: list[str] = None,
    render_mode: RenderMode = RenderMode.JSON_PROJECTION,
) -> dict[str, Any]:
    """
    Convenience function to process input through the deterministic meaning compiler.

    Example:
        result = compile_input("Create a Python function to calculate softmax")
        print(result["final_output"])
    """
    compiler = DeterministicMeaningCompiler()
    return compiler.process(input_text, required_constraints, render_mode=render_mode)


def compile_with_clarification(
    input_text: str,
    clarification_response: str = None,
    previous_context: dict[str, Any] = None,
) -> dict[str, Any]:
    """
    Compile with support for multi-turn clarification.

    Args:
        input_text: Current input (may be clarification response)
        clarification_response: If provided, this is the user's clarification
        previous_context: Previous compilation context for continuity

    Returns:
        Compilation result
    """
    # Merge clarification with original if provided
    if clarification_response and previous_context:
        full_input = (
            f"{previous_context.get('original_input', '')}\nClarification: {clarification_response}"
        )
        required_constraints = previous_context.get("required_constraints", [])
    else:
        full_input = input_text
        required_constraints = None

    compiler = DeterministicMeaningCompiler()
    result = compiler.process(full_input, required_constraints)

    # Store original input for future clarification rounds
    if not clarification_response:
        result["original_input"] = input_text
        result["required_constraints"] = required_constraints or []

    return result


# ============================================================================
# SECTION 13: EXPORTS
# ============================================================================

__all__ = [
    # Core compiler
    "DeterministicMeaningCompiler",
    "compile_input",
    "compile_with_clarification",
    # Kernels
    "ReadingKernel",
    "MeaningCompiler",
    "TypeChecker",
    "ConstraintChecker",
    "VerificationKernel",
    "CommitKernel",
    "RestrictedRenderer",
    # Data structures
    "TypedMeaningGraph",
    "TypedNode",
    "TypedEdge",
    "MachineGoal",
    "RootIntent",
    # Enums
    "SemanticType",
    "IntentType",
    "EdgeRelation",
    "RenderMode",
    "CommitMode",
    "RubbishBugClass",
    # Results
    "TypeCheckResult",
    "ConstraintCheckResult",
    "VerificationResult",
    "CommitResult",
    "AntiRubbishMetrics",
]

# ============================================================================
# SECTION 14: SELF-TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🧠 AMOS DETERMINISTIC MEANING COMPILER - SELF TEST")
    print("=" * 70)
    print("\nRoot Law: FreeGeneration = PrimaryFailureMode")
    print(
        "Correct Path: Input → Read → Compile → TypeCheck → ConstraintCheck → Verify → Commit → Render"
    )
    print()

    compiler = DeterministicMeaningCompiler()

    # Test 1: Clear instruction
    print("\n[Test 1] Clear instruction:")
    test1_input = "Write a Python function called 'softmax' that takes a list of floats and returns normalized probabilities."
    result1 = compiler.process(test1_input)
    print(f"  Commit Mode: {result1['commit_mode']}")
    print(f"  Success: {result1['success']}")
    print(f"  Nodes: {result1['stages']['compile']['nodes_count']}")
    print(f"  Type Safe: {result1['stages']['typecheck']['type_safe']}")
    print(f"  Confidence: {result1['stages']['verify']['confidence']:.2f}")

    # Test 2: Ambiguous input
    print("\n[Test 2] Ambiguous input (vague reference):")
    test2_input = "Fix it."
    result2 = compiler.process(test2_input)
    print(f"  Commit Mode: {result2['commit_mode']}")
    print(f"  Ambiguities: {result2['stages']['compile']['ambiguities']}")
    print(f"  Type Safe: {result2['stages']['typecheck']['type_safe']}")

    # Test 3: Question
    print("\n[Test 3] Question (non-executable):")
    test3_input = "What is the best way to implement a neural network?"
    result3 = compiler.process(test3_input, render_mode=RenderMode.BOUNDED_TEXT_PROJECTION)
    print(f"  Commit Mode: {result3['commit_mode']}")
    print(f"  Root Intent: {result3['stages']['compile']['root_intent']}")
    print(f"  Success: {result3['success']}")

    # Test 4: With constraints
    print("\n[Test 4] With required constraints:")
    test4_input = "Deploy the application to production."
    constraints = ["Must have passed all tests", "Cannot deploy during business hours"]
    result4 = compiler.process(test4_input, required_constraints=constraints)
    print(f"  Commit Mode: {result4['commit_mode']}")
    print(
        f"  Constraint Preservation: {result4['stages']['constraint_check']['preservation_score']:.2f}"
    )
    print(f"  Missing Constraints: {result4['stages']['constraint_check']['missing_constraints']}")

    # Metrics summary
    print("\n" + "=" * 70)
    print("📊 ANTI-RUBBISH METRICS")
    print("=" * 70)
    metrics = compiler.get_metrics()
    print(f"  Type Safety Rate: {metrics.type_safety_rate:.2%}")
    print(f"  Constraint Preservation: {metrics.constraint_preservation_rate:.2%}")
    print(f"  Binding Completion: {metrics.binding_completion_rate:.2%}")
    print(f"  Verification Pass: {metrics.verification_pass_rate:.2%}")
    print(f"  Renderer Drift: {metrics.renderer_drift_rate:.2%}")
    print(f"  Rubbish Rate: {metrics.rubbish_rate:.4f}")

    print("\n" + "=" * 70)
    print("✅ DMC SELF TEST COMPLETE")
    print("=" * 70)
    print("\nInvariant: No free text before stable typed meaning.")
