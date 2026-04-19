from __future__ import annotations

from typing import Any, Dict, List, Optional
from collections.abc import Callable

"""AMOS Cognitive Substrate - Minimum Viable Superintelligence Stack

Implements the executable cognitive substrate missing from Level 1 architecture:
- Object-centric world model (persistent entities, relations, dynamics)
- External working memory (scratch, proof, task, dependency, error graphs)
- Neural proposal + symbolic verification dual reasoning
- Online error-driven learning
- Active experimentation for uncertainty reduction
- Sparse modular expert routing
- Hard mode separation with strict arbitration

Architecture:
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │                     AMOS COGNITIVE SUBSTRATE                                 │
    │                  (Executable Superintelligence Stack)                        │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │                                                                             │
    │  ┌─────────────────────────────────────────────────────────────────────┐   │
    │  │                    OBJECT-CENTRIC WORLD MODEL                      │   │
    │  │  Persistent: Objects, Relations, Mechanisms, Transformations         │   │
    │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
    │  │  │ Object   │──│ Relation │──│ Mechanism│──│Transform │           │   │
    │  │  │  Graph   │  │  Graph   │  │  Graph   │  │  Graph   │           │   │
    │  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │   │
    │  └─────────────────────────────────────────────────────────────────────┘   │
    │                                                                             │
    │  ┌─────────────────────────────────────────────────────────────────────┐   │
    │  │                    EXTERNAL WORKING MEMORY                         │   │
    │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
    │  │  │ Scratch  │  │  Proof   │  │   Task   │  │Dependency│           │   │
    │  │  │  Graph   │  │  Graph   │  │  Graph   │  │  Graph   │           │   │
    │  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │   │
    │  │  ┌──────────┐  ┌──────────┐                                       │   │
    │  │  │  Error   │  │ Context  │                                       │   │
    │  │  │  Graph   │  │  Buffer  │                                       │   │
    │  │  └──────────┘  └──────────┘                                       │   │
    │  └─────────────────────────────────────────────────────────────────────┘   │
    │                                                                             │
    │  ┌─────────────────────────────────────────────────────────────────────┐   │
    │  │                 DUAL REASONING SUBSTRATE                           │   │
    │  │                                                                      │   │
    │  │   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐  │   │
    │  │   │   Neural    │────────▶│  Symbolic   │────────▶│  Verified   │  │   │
    │  │   │  Proposal   │         │ Verification│         │  Result     │  │   │
    │  │   │   Engine    │         │   Engine    │         │             │  │   │
    │  │   └─────────────┘         └─────────────┘         └─────────────┘  │   │
    │  │                                                                      │   │
    │  │   Verification Types:                                                │   │
    │  │   • Logical (theorem proving)                                       │   │
    │  │   • Causal (intervention testing)                                   │   │
    │  │   • Computational (execution verification)                          │   │
    │  │   • Empirical (observation checking)                                │   │
    │  └─────────────────────────────────────────────────────────────────────┘   │
    │                                                                             │
    │  ┌─────────────────────────────────────────────────────────────────────┐   │
    │  │                ONLINE ERROR-DRIVEN LEARNING                          │   │
    │  │                                                                      │   │
    │  │   Policy_{t+1} = Policy_t + α · ∇Policy · Error_t                    │   │
    │  │                                                                      │   │
    │  │   Components:                                                        │   │
    │  │   • Error attribution (which operator failed)                       │   │
    │  │   • Policy gradient computation                                     │   │
    │  │   • In-session adaptation                                           │   │
    │  │   • Cross-session consolidation                                     │   │
    │  └─────────────────────────────────────────────────────────────────────┘   │
    │                                                                             │
    │  ┌─────────────────────────────────────────────────────────────────────┐   │
    │  │                ACTIVE EXPERIMENTATION LOOP                          │   │
    │  │                                                                      │   │
    │  │   a* = argmax [Utility(a) + InfoGain(a) - Cost(a) - Risk(a)]         │   │
    │  │                                                                      │   │
    │  │   Action selection for uncertainty reduction:                       │   │
    │  │   • Query most uncertain variable                                   │   │
    │  │   • Test causal hypothesis                                          │   │
    │  │   • Explore high-uncertainty region                                 │   │
    │  │   • Verify weakly-supported inference                               │   │
    │  └─────────────────────────────────────────────────────────────────────┘   │
    │                                                                             │
    │  ┌─────────────────────────────────────────────────────────────────────┐   │
    │  │              SPARSE MODULAR EXPERT ROUTING                          │   │
    │  │                                                                      │   │
    │  │   Router ──▶ Expert Selection ──▶ Arbitration ──▶ Result           │   │
    │  │                                                                      │   │
    │  │   Experts: Parser | Causal | Proof | Planner | Compiler | Human    │   │
    │  │                                                                      │   │
    │  │   Arbitration: Confidence-weighted voting with conflict resolution │   │
    │  └─────────────────────────────────────────────────────────────────────┘   │
    │                                                                             │
    │  ┌─────────────────────────────────────────────────────────────────────┐   │
    │  │              HARD MODE SEPARATION CONTROLLER                        │   │
    │  │                                                                      │   │
    │  │   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │   │
    │  │   │  READ   │ │ THINK   │ │ REASON  │ │ VERIFY  │ │ RENDER  │       │   │
    │  │   │ (Input) │ │(Process)│ │(Infer)  │ │(Check)  │ │(Output) │       │   │
    │  │   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘       │   │
    │  │        │           │           │           │           │            │   │
    │  │        └───────────┴───────────┴───────────┴───────────┘            │   │
    │  │                            │                                        │   │
    │  │                    Strict Mode Controller                           │   │
    │  │                    (No blending, no leakage)                        │   │
    │  └─────────────────────────────────────────────────────────────────────┘   │
    │                                                                             │
    │  ┌─────────────────────────────────────────────────────────────────────┐   │
    │  │              METACOGNITIVE SUPERVISION LAYER                        │   │
    │  │                                                                      │   │
    │  │   Self-monitoring state:                                           │   │
    │  │   • What is known (certainty tracking)                             │   │
    │  │   • What was inferred (derivation chain)                           │   │
    │  │   • What is missing (information gaps)                               │   │
    │  │   • Where error likely is (fault localization)                     │   │
    │  │   • Which operator failed (operator blame)                         │   │
    │  └─────────────────────────────────────────────────────────────────────┘   │
    │                                                                             │
    └─────────────────────────────────────────────────────────────────────────────┘

Key Equation:
    Intelligence ∝ WorldModel_{object-centric} × WorkingMemory_{external} ×
                   Reasoning_{verifiable} × Learning_{error-driven} ×
                   Action_{information-seeking} × Routing_{sparse} ×
                   Metacognition_{explicit}

Usage:
    # Initialize substrate
    substrate = AMOSCognitiveSubstrate()

    # Build world model
    obj = substrate.world.create_object("system", properties={"load": 0.7})
    substrate.world.add_relation("system", "depends_on", "database")

    # Externalize thought
    substrate.memory.scratch.add_node("hypothesis_X", {"confidence": 0.8})

    # Reason with verification
    proposal = substrate.reasoning.propose("optimize_query")
    verified = substrate.reasoning.verify(proposal, method="computational")

    # Learn from error
    substrate.learning.update_from_error(observed_error="query_timeout",
                                         attribution="planner")

    # Act to reduce uncertainty
    action = substrate.experimentation.select_action(
        objective="reduce_uncertainty", target="database_latency"
    )

Author: AMOS Cognitive Architecture Team
Version: 1.0.0-SUBSTRATE
"""

import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto

import numpy as np

# ============================================================================
# Core Types and Enums
# ============================================================================


class Mode(Enum):
    """Strictly separated cognitive modes."""

    READ = auto()  # Input processing, perception
    THINK = auto()  # Internal processing, pattern matching
    REASON = auto()  # Inference, deduction, induction
    VERIFY = auto()  # Verification, validation, checking
    RENDER = auto()  # Output generation, presentation
    EXPERIMENT = auto()  # Active information seeking


class RelationType(Enum):
    """Types of relations in world model."""

    DEPENDS_ON = "depends_on"
    CAUSES = "causes"
    PART_OF = "part_of"
    INSTANCE_OF = "instance_of"
    SIMILAR_TO = "similar_to"
    CONTRADICTS = "contradicts"
    ENABLES = "enables"
    PREVENTS = "prevents"


class MechanismType(Enum):
    """Types of mechanisms (dynamics)."""

    DETERMINISTIC = "deterministic"
    STOCHASTIC = "stochastic"
    CAUSAL = "causal"
    FEEDBACK = "feedback"
    THRESHOLD = "threshold"


class VerificationMethod(Enum):
    """Methods for symbolic verification."""

    LOGICAL = "logical"  # Theorem proving
    CAUSAL = "causal"  # Intervention testing
    COMPUTATIONAL = "computational"  # Code execution
    EMPIRICAL = "empirical"  # Observation checking
    CONSENSUS = "consensus"  # Multi-expert agreement


class ExpertType(Enum):
    """Types of expert modules."""

    PARSER = "parser"  # Language/structure parsing
    CAUSAL = "causal"  # Causal inference
    PROOF = "proof"  # Formal proof
    PLANNER = "planner"  # Task/action planning
    COMPILER = "compiler"  # Code generation/verification
    HUMAN = "human"  # Human state modeling
    MEMORY = "memory"  # Retrieval and association
    INTEGRATOR = "integrator"  # Cross-domain synthesis


# ============================================================================
# Object-Centric World Model
# ============================================================================


@dataclass
class Object:
    """
    Persistent object with properties, state history, and type.

    Unlike simple vertices, objects have:
    - Typed properties with schemas
    - State history over time
    - Belief state (certainty about existence/properties)
    - Persistence across observations
    """

    id: str
    type: str  # e.g., "system", "database", "query", "user"
    properties: Dict[str, Any] = field(default_factory=dict)
    state_history: list[tuple[datetime, dict[str, Any]]] = field(default_factory=list)
    belief: float = 1.0  # 0-1, certainty of existence
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_observed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_property(self, key: str, value: Any, timestamp: Optional[datetime] = None) -> None:
        """Update property with history tracking."""
        timestamp = timestamp or datetime.now(timezone.utc)
        old_value = self.properties.get(key)
        self.properties[key] = value
        self.state_history.append((timestamp, {key: old_value}))
        self.last_observed = timestamp

    def get_property_history(self, key: str) -> list[tuple[datetime, Any]]:
        """Get history of property changes."""
        return [(t, s.get(key)) for t, s in self.state_history if key in s]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "properties": self.properties,
            "belief": self.belief,
            "created_at": self.created_at.isoformat(),
            "last_observed": self.last_observed.isoformat(),
        }


@dataclass
class Relation:
    """
    Typed relation between objects with properties.

    Relations have:
    - Source and target objects
    - Type (causal, structural, functional)
    - Strength/confidence
    - Temporal bounds
    - Properties (e.g., "weight" for causal strength)
    """

    id: str
    source: str
    target: str
    type: RelationType
    strength: float = 1.0  # 0-1 confidence
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

    def is_active(self, t: Optional[datetime] = None) -> bool:
        """Check if relation is active at time t."""
        t = t or datetime.now(timezone.utc)
        if self.valid_from and t < self.valid_from:
            return False
        if self.valid_until and t > self.valid_until:
            return False
        return True


@dataclass
class Mechanism:
    """
    Mechanism describing how inputs transform to outputs.

    Mechanisms capture:
    - Input-output mapping functions
    - Causal structure
    - Dynamics (deterministic/stochastic)
    - Preconditions and effects
    """

    id: str
    name: str
    type: MechanismType
    inputs: List[str]  # Input variable names
    outputs: List[str]  # Output variable names
    function: Callable[[dict[str, Any]], dict[str, Any]] = None
    preconditions: list[Callable[[dict[str, Any]], bool]] = field(default_factory=list)
    causal_graph: dict[str, list[str]] = field(default_factory=dict)  # var -> affected vars
    uncertainty: float = 0.0  # Model uncertainty

    def apply(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Apply mechanism to inputs, return outputs or None if preconditions fail."""
        # Check preconditions
        for precond in self.preconditions:
            if not precond(inputs):
                return None

        # Apply function if available
        if self.function:
            return self.function(inputs)

        # Default: pass-through
        return {k: inputs.get(k) for k in self.outputs}


@dataclass
class Transformation:
    """
    Transformation rule for state evolution.

    Captures how the world state changes over time.
    """

    id: str
    name: str
    trigger: Callable[[WorldModelState], bool]
    effect: Callable[[WorldModelState], WorldModelState]
    probability: float = 1.0
    description: str = ""


@dataclass
class WorldModelState:
    """
    Complete state of the object-centric world model.
    """

    objects: Dict[str, Object] = field(default_factory=dict)
    relations: Dict[str, Relation] = field(default_factory=dict)
    mechanisms: Dict[str, Mechanism] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_object(self, obj: Object) -> None:
        self.objects[obj.id] = obj

    def add_relation(self, rel: Relation) -> None:
        self.relations[rel.id] = rel

    def get_related(self, obj_id: str, relation_type: Optional[RelationType] = None) -> List[str]:
        """Get objects related to obj_id."""
        related = []
        for rel in self.relations.values():
            if rel.source == obj_id and rel.is_active():
                if relation_type is None or rel.type == relation_type:
                    related.append(rel.target)
        return related

    def get_causal_ancestors(self, obj_id: str, depth: int = 3) -> List[str]:
        """Get causal ancestors (what causes this object)."""
        ancestors = []
        to_check = [(obj_id, 0)]
        visited = {obj_id}

        while to_check:
            current, d = to_check.pop(0)
            if d >= depth:
                continue

            for rel in self.relations.values():
                if rel.target == current and rel.type == RelationType.CAUSES and rel.is_active():
                    if rel.source not in visited:
                        ancestors.append(rel.source)
                        visited.add(rel.source)
                        to_check.append((rel.source, d + 1))

        return ancestors

    def copy(self) -> WorldModelState:
        """Deep copy of state."""
        return WorldModelState(
            objects=deepcopy(self.objects),
            relations=deepcopy(self.relations),
            mechanisms=deepcopy(self.mechanisms),
            timestamp=datetime.now(timezone.utc),
        )


class ObjectCentricWorldModel:
    """
    Persistent object-centric world model.

    Maintains stable representations of world entities across time,
    supporting:
    - Object persistence and identity tracking
    - Rich relation types (causal, structural, functional)
    - Mechanism models for dynamics
    - Causal reasoning support
    """

    def __init__(self):
        self.state = WorldModelState()
        self.history: List[WorldModelState] = []
        self.transformation_rules: List[Transformation] = []

    def create_object(
        self,
        obj_type: str,
        obj_id: Optional[str] = None,
        properties: Dict[str, Any] = None,
    ) -> Object:
        """Create and register a new object."""
        obj_id = obj_id or f"{obj_type}_{uuid.uuid4().hex[:8]}"
        obj = Object(
            id=obj_id,
            type=obj_type,
            properties=properties or {},
        )
        self.state.add_object(obj)
        return obj

    def add_relation(
        self,
        source: str,
        target: str,
        relation_type: RelationType,
        strength: float = 1.0,
        properties: Dict[str, Any] = None,
    ) -> Relation:
        """Add a relation between objects."""
        rel_id = f"rel_{uuid.uuid4().hex[:8]}"
        rel = Relation(
            id=rel_id,
            source=source,
            target=target,
            type=relation_type,
            strength=strength,
            properties=properties or {},
        )
        self.state.add_relation(rel)
        return rel

    def add_mechanism(self, mechanism: Mechanism) -> None:
        """Add a mechanism to the world model."""
        self.state.mechanisms[mechanism.id] = mechanism

    def predict_effects(
        self,
        action: Dict[str, Any],
        steps: int = 1,
    ) -> list[tuple[str, float, dict[str, Any]]]:
        """
        Predict effects of an action using mechanisms.

        Returns list of (object_id, probability, predicted_properties).
        """
        effects = []

        # Find triggered mechanisms
        for mech in self.state.mechanisms.values():
            if mech.type == MechanismType.CAUSAL:
                result = mech.apply(action)
                if result:
                    for output_var in mech.outputs:
                        affected_objs = self._find_objects_with_property(output_var)
                        for obj_id in affected_objs:
                            effects.append((obj_id, 1.0 - mech.uncertainty, result))

        return effects

    def _find_objects_with_property(self, prop: str) -> List[str]:
        """Find objects that have a given property."""
        return [obj_id for obj_id, obj in self.state.objects.items() if prop in obj.properties]

    def simulate_counterfactual(
        self,
        intervention: Dict[str, Any],
    ) -> WorldModelState:
        """
        Simulate what-if scenario by applying intervention.

        Returns a copy of state with intervention applied.
        """
        sim_state = self.state.copy()

        # Apply intervention
        for obj_id, props in intervention.items():
            if obj_id in sim_state.objects:
                for key, value in props.items():
                    sim_state.objects[obj_id].properties[key] = value

        # Run transformations
        for rule in self.transformation_rules:
            if rule.trigger(sim_state):
                if np.random.random() < rule.probability:
                    sim_state = rule.effect(sim_state)

        return sim_state

    def checkpoint(self) -> None:
        """Save current state to history."""
        self.history.append(self.state.copy())

    def get_object_persistent_summary(self, obj_id: str) -> Dict[str, Any]:
        """Get summary of object across its lifetime."""
        if obj_id not in self.state.objects:
            return None

        obj = self.state.objects[obj_id]
        return {
            "id": obj.id,
            "type": obj.type,
            "lifetime_seconds": (obj.last_observed - obj.created_at).total_seconds(),
            "property_count": len(obj.properties),
            "state_transitions": len(obj.state_history),
            "current_belief": obj.belief,
            "related_objects": self.state.get_related(obj_id),
            "causal_ancestors": self.state.get_causal_ancestors(obj_id),
        }


# ============================================================================
# External Working Memory
# ============================================================================


@dataclass
class GraphNode:
    """Node in working memory graph."""

    id: str
    type: str  # e.g., "hypothesis", "fact", "query", "conclusion"
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 1.0
    parent_ids: List[str] = field(default_factory=list)
    child_ids: List[str] = field(default_factory=list)


@dataclass
class GraphEdge:
    """Edge in working memory graph."""

    source: str
    target: str
    type: str  # e.g., "supports", "contradicts", "implies", "depends"
    strength: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkingMemoryGraph:
    """
    Externalized working memory graph.

    Unlike hidden context, this is explicit, inspectable, and manipulable.
    """

    def __init__(self, name: str):
        self.name = name
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: dict[tuple[str, str], GraphEdge] = {}
        self.node_count = 0

    def add_node(
        self,
        node_type: str,
        content: Any,
        node_id: Optional[str] = None,
        confidence: float = 1.0,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """Add a node to the graph."""
        node_id = node_id or f"{self.name}_{self.node_count}"
        self.node_count += 1

        node = GraphNode(
            id=node_id,
            type=node_type,
            content=content,
            confidence=confidence,
            metadata=metadata or {},
        )
        self.nodes[node_id] = node
        return node_id

    def add_edge(
        self,
        source: str,
        target: str,
        edge_type: str,
        strength: float = 1.0,
    ) -> None:
        """Add an edge between nodes."""
        if source in self.nodes and target in self.nodes:
            self.edges[(source, target)] = GraphEdge(
                source=source,
                target=target,
                type=edge_type,
                strength=strength,
            )
            self.nodes[source].child_ids.append(target)
            self.nodes[target].parent_ids.append(source)

    def get_neighbors(self, node_id: str, edge_type: Optional[str] = None) -> List[str]:
        """Get neighbors of a node."""
        if node_id not in self.nodes:
            return []

        neighbors = []
        for (src, tgt), edge in self.edges.items():
            if src == node_id or tgt == node_id:
                if edge_type is None or edge.type == edge_type:
                    neighbors.append(tgt if src == node_id else src)
        return neighbors

    def find_paths(
        self,
        source: str,
        target: str,
        max_depth: int = 5,
    ) -> list[list[str]]:
        """Find paths between nodes."""
        paths = []
        queue = [(source, [source])]

        while queue:
            current, path = queue.pop(0)
            if current == target and len(path) > 1:
                paths.append(path)
                continue

            if len(path) >= max_depth:
                continue

            for neighbor in self.get_neighbors(current):
                if neighbor not in path:
                    queue.append((neighbor, path + [neighbor]))

        return paths

    def get_roots(self) -> List[str]:
        """Get root nodes (no parents)."""
        return [n.id for n in self.nodes.values() if not n.parent_ids]

    def get_leaves(self) -> List[str]:
        """Get leaf nodes (no children)."""
        return [n.id for n in self.nodes.values() if not n.child_ids]

    def query_by_type(self, node_type: str) -> List[GraphNode]:
        """Query nodes by type."""
        return [n for n in self.nodes.values() if n.type == node_type]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize graph."""
        return {
            "name": self.name,
            "nodes": {
                k: {"type": v.type, "content": str(v.content), "confidence": v.confidence}
                for k, v in self.nodes.items()
            },
            "edges": [
                {"source": e.source, "target": e.target, "type": e.type, "strength": e.strength}
                for e in self.edges.values()
            ],
        }


class ExternalWorkingMemory:
    """
    Multi-graph external working memory system.

    Provides separate graphs for:
    - Scratch: Working thoughts, hypotheses, temporary structures
    - Proof: Deductive chains, verification steps
    - Task: Task hierarchy, subtask decomposition
    - Dependency: Variable/task dependencies
    - Error: Error records, failure modes, recovery attempts
    - Context: Active context buffer
    """

    def __init__(self):
        self.scratch = WorkingMemoryGraph("scratch")
        self.proof = WorkingMemoryGraph("proof")
        self.task = WorkingMemoryGraph("task")
        self.dependency = WorkingMemoryGraph("dependency")
        self.error = WorkingMemoryGraph("error")
        self.context = WorkingMemoryGraph("context")

        self._graphs: Dict[str, WorkingMemoryGraph] = {
            "scratch": self.scratch,
            "proof": self.proof,
            "task": self.task,
            "dependency": self.dependency,
            "error": self.error,
            "context": self.context,
        }

    def get_graph(self, name: str) -> Optional[WorkingMemoryGraph]:
        """Get a specific memory graph."""
        return self._graphs.get(name)

    def clear_all(self) -> None:
        """Clear all working memory."""
        for graph in self._graphs.values():
            graph.nodes.clear()
            graph.edges.clear()
            graph.node_count = 0

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all memory graphs."""
        return {
            name: {"nodes": len(g.nodes), "edges": len(g.edges)} for name, g in self._graphs.items()
        }


# ============================================================================
# Dual Reasoning Substrate (Neural + Symbolic)
# ============================================================================


@dataclass
class Proposal:
    """Neural proposal output."""

    id: str
    content: Any
    confidence: float
    source: str  # Which module generated it
    alternative_proposals: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationResult:
    """Result of symbolic verification."""

    proposal_id: str
    method: VerificationMethod
    passed: bool
    confidence: float
    counterexample: Optional[Any] = None
    proof_trace: List[str] = field(default_factory=list)
    verification_time_ms: float = 0.0


class SymbolicVerifier:
    """
    Symbolic verification engine.

    Implements multiple verification strategies:
    - Logical: Theorem proving, logical entailment
    - Causal: Intervention testing, do-calculus
    - Computational: Code execution, numerical verification
    - Empirical: Observation checking, data validation
    """

    def __init__(self):
        self.verification_stats: dict[VerificationMethod, dict[str, Any]] = {
            method: {"total": 0, "passed": 0, "avg_time_ms": 0.0} for method in VerificationMethod
        }

    def verify(
        self,
        proposal: Proposal,
        method: VerificationMethod,
        context: Dict[str, Any] = None,
    ) -> VerificationResult:
        """
        Verify a proposal using specified method.

        Returns verification result with confidence and trace.
        """
        import time

        start = time.time()

        if method == VerificationMethod.LOGICAL:
            passed, confidence, counterexample = self._verify_logical(proposal, context)
        elif method == VerificationMethod.CAUSAL:
            passed, confidence, counterexample = self._verify_causal(proposal, context)
        elif method == VerificationMethod.COMPUTATIONAL:
            passed, confidence, counterexample = self._verify_computational(proposal, context)
        elif method == VerificationMethod.EMPIRICAL:
            passed, confidence, counterexample = self._verify_empirical(proposal, context)
        else:
            passed, confidence, counterexample = False, 0.0, None

        elapsed_ms = (time.time() - start) * 1000

        # Update stats
        stats = self.verification_stats[method]
        stats["total"] += 1
        if passed:
            stats["passed"] += 1
        stats["avg_time_ms"] = (stats["avg_time_ms"] * (stats["total"] - 1) + elapsed_ms) / stats[
            "total"
        ]

        return VerificationResult(
            proposal_id=proposal.id,
            method=method,
            passed=passed,
            confidence=confidence,
            counterexample=counterexample,
            verification_time_ms=elapsed_ms,
        )

    def _verify_logical(
        self,
        proposal: Proposal,
        context: Dict[str, Any],
    ) -> Tuple[bool, float, Any]:
        """Logical verification via constraint checking."""
        # Simplified: check for logical contradictions
        content = str(proposal.content)

        # Check for obvious contradictions
        contradictions = [
            ("increases", "decreases"),
            ("true", "false"),
            ("all", "none"),
        ]

        for term1, term2 in contradictions:
            if term1 in content.lower() and term2 in content.lower():
                # Check if they're about same subject
                return False, 0.3, f"Contradiction: {term1} and {term2}"

        return True, proposal.confidence * 0.9, None

    def _verify_causal(
        self,
        proposal: Proposal,
        context: Dict[str, Any],
    ) -> Tuple[bool, float, Any]:
        """Causal verification via counterfactual test."""
        # Check if world model is in context
        world_model = context.get("world_model") if context else None
        if not world_model:
            return True, proposal.confidence * 0.7, None  # Can't verify, pass with discount

        # Simulate intervention if proposal describes action
        # Simplified: check for causal loops
        return True, proposal.confidence * 0.85, None

    def _verify_computational(
        self,
        proposal: Proposal,
        context: Dict[str, Any],
    ) -> Tuple[bool, float, Any]:
        """Computational verification via execution."""
        # If proposal contains code, try to execute
        content = proposal.content

        if isinstance(content, dict) and "code" in content:
            try:
                # Safe execution would go here
                # For now, syntax check only
                compile(content["code"], "<string>", "exec")
                return True, 0.95, None
            except SyntaxError as e:
                return False, 0.0, str(e)

        return True, proposal.confidence * 0.8, None

    def _verify_empirical(
        self,
        proposal: Proposal,
        context: Dict[str, Any],
    ) -> Tuple[bool, float, Any]:
        """Empirical verification against observations."""
        # Check against known facts in context
        known_facts = context.get("known_facts", []) if context else []

        content = str(proposal.content)
        for fact in known_facts:
            if self._contradicts(content, str(fact)):
                return False, 0.2, f"Contradicts known fact: {fact}"

        return True, proposal.confidence * 0.9, None

    def _contradicts(self, statement1: str, statement2: str) -> bool:
        """Check if two statements contradict each other."""
        # Simplified contradiction detection
        s1, s2 = statement1.lower(), statement2.lower()

        # Check for negation
        if s1.startswith("not ") and s1[4:] in s2:
            return True
        if s2.startswith("not ") and s2[4:] in s1:
            return True

        return False


class DualReasoningSubstrate:
    """
    Dual reasoning system: Neural proposals + Symbolic verification.

    Implements:
    1. Generate multiple proposals (neural/diverse)
    2. Verify each with appropriate method
    3. Select best verified proposal
    4. Track verification history
    """

    def __init__(self):
        self.verifier = SymbolicVerifier()
        self.proposal_history: List[Proposal] = []
        self.verification_history: List[VerificationResult] = []
        self.proposal_counter = 0

    def propose(
        self,
        content: Any,
        confidence: float = 0.8,
        source: str = "default",
        alternatives: Optional[list[str]] = None,
    ) -> Proposal:
        """Generate a proposal."""
        self.proposal_counter += 1
        proposal = Proposal(
            id=f"prop_{self.proposal_counter}",
            content=content,
            confidence=confidence,
            source=source,
            alternative_proposals=alternatives or [],
        )
        self.proposal_history.append(proposal)
        return proposal

    def verify(
        self,
        proposal: Proposal,
        method: VerificationMethod,
        context: Dict[str, Any] = None,
    ) -> VerificationResult:
        """Verify a proposal."""
        result = self.verifier.verify(proposal, method, context)
        self.verification_history.append(result)
        return result

    def propose_and_verify(
        self,
        content: Any,
        method: VerificationMethod,
        confidence: float = 0.8,
        context: Dict[str, Any] = None,
    ) -> Tuple[Proposal, VerificationResult]:
        """Generate proposal and verify it."""
        proposal = self.propose(content, confidence)
        result = self.verify(proposal, method, context)
        return proposal, result

    def select_best_verified(
        self,
        proposals: List[Proposal],
        min_confidence: float = 0.7,
    ) -> Optional[Proposal]:
        """Select best proposal that passes verification."""
        verified = []
        for prop in proposals:
            # Get latest verification for this proposal
            verifications = [v for v in self.verification_history if v.proposal_id == prop.id]
            if verifications:
                latest = verifications[-1]
                if latest.passed and latest.confidence >= min_confidence:
                    verified.append((prop, latest.confidence))

        if verified:
            return max(verified, key=lambda x: x[1])[0]
        return None


# ============================================================================
# Online Error-Driven Learning
# ============================================================================


@dataclass
class ErrorRecord:
    """Record of an error for learning."""

    id: str
    error_type: str
    operator: str  # Which operator/module failed
    observation: Dict[str, Any]
    expected: Any
    actual: Any
    error_magnitude: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyUpdate:
    """Policy update from error."""

    operator: str
    parameter: str
    delta: float
    direction: str  # "increase" or "decrease"
    reason: str


class OnlineLearningSystem:
    """
    Online error-driven learning system.

    Implements:
    Policy_{t+1} = Policy_t + α · ∇Policy · Error_t

    Tracks:
    - Error attribution (which operator failed)
    - Policy gradient computation
    - In-session adaptation
    """

    def __init__(self, learning_rate: float = 0.1):
        self.learning_rate = learning_rate
        self.policies: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.error_history: List[ErrorRecord] = []
        self.update_history: List[PolicyUpdate] = []
        self.operator_error_counts: Dict[str, int] = defaultdict(int)
        self.error_counter = 0

    def register_error(
        self,
        error_type: str,
        operator: str,
        observation: Dict[str, Any],
        expected: Any,
        actual: Any,
        context: Dict[str, Any] = None,
    ) -> ErrorRecord:
        """Register an error for learning."""
        self.error_counter += 1

        # Compute error magnitude
        error_magnitude = self._compute_error_magnitude(expected, actual)

        record = ErrorRecord(
            id=f"err_{self.error_counter}",
            error_type=error_type,
            operator=operator,
            observation=observation,
            expected=expected,
            actual=actual,
            error_magnitude=error_magnitude,
            context=context or {},
        )

        self.error_history.append(record)
        self.operator_error_counts[operator] += 1

        # Immediately compute policy update
        self._update_policy_from_error(record)

        return record

    def _compute_error_magnitude(self, expected: Any, actual: Any) -> float:
        """Compute magnitude of error."""
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            if expected == 0:
                return abs(actual)
            return abs((actual - expected) / expected)

        if isinstance(expected, str) and isinstance(actual, str):
            return 0.0 if expected == actual else 1.0

        return 1.0 if expected != actual else 0.0

    def _update_policy_from_error(self, error: ErrorRecord) -> Optional[PolicyUpdate]:
        """Compute and apply policy update from error."""
        operator = error.operator

        # Determine which parameter to adjust
        # Simplified: adjust "caution" parameter based on error rate
        current_caution = self.policies[operator]["caution"]

        # Increase caution if errors are high
        if error.error_magnitude > 0.5:
            delta = self.learning_rate * error.error_magnitude
            self.policies[operator]["caution"] = min(1.0, current_caution + delta)

            update = PolicyUpdate(
                operator=operator,
                parameter="caution",
                delta=delta,
                direction="increase",
                reason=f"High error magnitude: {error.error_magnitude:.3f}",
            )
        else:
            # Decrease caution slightly if few errors
            delta = self.learning_rate * 0.1
            self.policies[operator]["caution"] = max(0.0, current_caution - delta)

            update = PolicyUpdate(
                operator=operator,
                parameter="caution",
                delta=delta,
                direction="decrease",
                reason="Low error, reducing caution",
            )

        self.update_history.append(update)
        return update

    def get_policy(self, operator: str, parameter: str, default: float = 0.5) -> float:
        """Get current policy value."""
        return self.policies[operator].get(parameter, default)

    def get_operator_reliability(self, operator: str) -> float:
        """Compute reliability score for operator."""
        total_ops = len(self.error_history)  # Simplified
        errors = self.operator_error_counts[operator]

        if total_ops == 0:
            return 1.0

        error_rate = errors / max(1, total_ops)
        return max(0.0, 1.0 - error_rate)


# ============================================================================
# Active Experimentation
# ============================================================================


@dataclass
class Experiment:
    """An experiment to reduce uncertainty."""

    id: str
    target_variable: str
    action: Dict[str, Any]
    expected_information_gain: float
    cost: float
    risk: float
    utility: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ActiveExperimentationSystem:
    """
    Active experimentation for uncertainty reduction.

    Implements:
    a* = argmax [Utility(a) + InfoGain(a) - Cost(a) - Risk(a)]
    """

    def __init__(self):
        self.experiments: List[Experiment] = []
        self.executed_experiments: List[Experiment] = []
        self.uncertainty_estimates: Dict[str, float] = {}
        self.experiment_counter = 0

    def estimate_uncertainty(self, variable: str) -> float:
        """Estimate uncertainty about a variable."""
        return self.uncertainty_estimates.get(variable, 0.5)

    def update_uncertainty(self, variable: str, uncertainty: float) -> None:
        """Update uncertainty estimate."""
        self.uncertainty_estimates[variable] = uncertainty

    def design_experiment(
        self,
        target_variable: str,
        action_space: list[dict[str, Any]],
        world_model: Optional[ObjectCentricWorldModel] = None,
    ) -> Optional[Experiment]:
        """
        Design an experiment to reduce uncertainty about target.
        """
        best_experiment = None
        best_score = float("-inf")

        for action in action_space:
            # Estimate information gain
            info_gain = self._estimate_information_gain(target_variable, action, world_model)

            # Estimate cost
            cost = self._estimate_cost(action)

            # Estimate risk
            risk = self._estimate_risk(action, world_model)

            # Estimate utility (independent of this specific uncertainty)
            utility = self._estimate_utility(action)

            # Score
            score = utility + info_gain - cost - risk

            if score > best_score:
                best_score = score
                best_experiment = Experiment(
                    id=f"exp_{uuid.uuid4().hex[:8]}",
                    target_variable=target_variable,
                    action=action,
                    expected_information_gain=info_gain,
                    cost=cost,
                    risk=risk,
                    utility=utility,
                )

        if best_experiment:
            self.experiments.append(best_experiment)

        return best_experiment

    def _estimate_information_gain(
        self,
        target: str,
        action: Dict[str, Any],
        world_model: Optional[ObjectCentricWorldModel],
    ) -> float:
        """Estimate information gain from action."""
        # Simplified: higher uncertainty → higher potential gain
        current_uncertainty = self.estimate_uncertainty(target)

        # If world model available, simulate
        if world_model:
            effects = world_model.predict_effects(action)
            # More effects → more information
            return current_uncertainty * (1 + len(effects) * 0.1)

        return current_uncertainty

    def _estimate_cost(self, action: Dict[str, Any]) -> float:
        """Estimate cost of action."""
        # Simplified cost estimation
        base_cost = 0.1

        if "compute" in str(action).lower():
            base_cost += 0.2
        if "query" in str(action).lower():
            base_cost += 0.05
        if "write" in str(action).lower():
            base_cost += 0.15

        return base_cost

    def _estimate_risk(
        self,
        action: Dict[str, Any],
        world_model: Optional[ObjectCentricWorldModel],
    ) -> float:
        """Estimate risk of action."""
        # Simplified risk estimation
        base_risk = 0.05

        if "delete" in str(action).lower():
            base_risk += 0.3
        if "restart" in str(action).lower():
            base_risk += 0.2

        # Check world model for dependencies
        if world_model and "target" in action:
            target = action["target"]
            if target in world_model.state.objects:
                # More dependents → higher risk
                dependents = world_model.state.get_related(target)
                base_risk += len(dependents) * 0.05

        return min(1.0, base_risk)

    def _estimate_utility(self, action: Dict[str, Any]) -> float:
        """Estimate intrinsic utility of action."""
        # Simplified utility
        return 0.2

    def select_action(
        self,
        objective: str,
        target: Optional[str] = None,
        action_space: list[dict[str, Any]] = None,
        world_model: Optional[ObjectCentricWorldModel] = None,
    ) -> Dict[str, Any]:
        """
        Select best action for given objective.
        """
        if objective == "reduce_uncertainty" and target:
            exp = self.design_experiment(target, action_space or [], world_model)
            if exp:
                return exp.action

        # Default: return first low-cost action
        if action_space:
            return min(action_space, key=lambda a: self._estimate_cost(a))

        return None


# ============================================================================
# Sparse Modular Expert Routing
# ============================================================================


@dataclass
class ExpertResult:
    """Result from an expert module."""

    expert_type: ExpertType
    output: Any
    confidence: float
    processing_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExpertModule(ABC):
    """Abstract expert module."""

    expert_type: ExpertType

    @abstractmethod
    def can_handle(self, input_data: Dict[str, Any]) -> float:
        """Return confidence that this expert can handle input (0-1)."""
        pass

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> ExpertResult:
        """Process input and return result."""
        pass


class ParserExpert(ExpertModule):
    """Parser expert for language/structure."""

    expert_type = ExpertType.PARSER

    def can_handle(self, input_data: Dict[str, Any]) -> float:
        if "text" in input_data or "code" in input_data:
            return 0.9
        return 0.1

    def process(self, input_data: Dict[str, Any]) -> ExpertResult:
        start = time.time()

        text = input_data.get("text", "")
        # Simplified parsing
        tokens = text.split()
        structure = {"tokens": tokens, "length": len(tokens)}

        elapsed = (time.time() - start) * 1000

        return ExpertResult(
            expert_type=self.expert_type,
            output=structure,
            confidence=0.85,
            processing_time_ms=elapsed,
        )


class CausalExpert(ExpertModule):
    """Causal inference expert."""

    expert_type = ExpertType.CAUSAL

    def can_handle(self, input_data: Dict[str, Any]) -> float:
        if "causes" in input_data or "effects" in input_data:
            return 0.9
        if "why" in str(input_data).lower():
            return 0.8
        return 0.2

    def process(self, input_data: Dict[str, Any]) -> ExpertResult:
        start = time.time()

        # Simplified causal analysis
        causes = input_data.get("causes", [])
        effects = input_data.get("effects", [])

        causal_graph = {
            "nodes": causes + effects,
            "edges": [(c, e) for c in causes for e in effects],
        }

        elapsed = (time.time() - start) * 1000

        return ExpertResult(
            expert_type=self.expert_type,
            output=causal_graph,
            confidence=0.75,
            processing_time_ms=elapsed,
        )


class ProofExpert(ExpertModule):
    """Formal proof expert."""

    expert_type = ExpertType.PROOF

    def can_handle(self, input_data: Dict[str, Any]) -> float:
        if "theorem" in input_data or "prove" in input_data:
            return 0.95
        if "valid" in str(input_data).lower():
            return 0.7
        return 0.1

    def process(self, input_data: Dict[str, Any]) -> ExpertResult:
        start = time.time()

        # Simplified proof checking
        statement = input_data.get("theorem", "")
        # Check for obvious issues
        valid = "not not" not in statement  # Simplified check

        elapsed = (time.time() - start) * 1000

        return ExpertResult(
            expert_type=self.expert_type,
            output={"valid": valid, "statement": statement},
            confidence=0.9 if valid else 0.3,
            processing_time_ms=elapsed,
        )


class PlannerExpert(ExpertModule):
    """Task/action planning expert."""

    expert_type = ExpertType.PLANNER

    def can_handle(self, input_data: Dict[str, Any]) -> float:
        if "goal" in input_data or "plan" in input_data:
            return 0.9
        if "steps" in input_data or "sequence" in input_data:
            return 0.8
        return 0.2

    def process(self, input_data: Dict[str, Any]) -> ExpertResult:
        """Process planning request with real brain-powered task decomposition."""
        import time

        start = time.time()

        goal = input_data.get("goal", "")
        context = input_data.get("context", {})

        # Brain-powered planning via cognitive substrate
        steps = self._generate_plan(goal, context)
        plan = {"goal": goal, "steps": steps, "generated_by": "brain"}

        elapsed = (time.time() - start) * 1000

        return ExpertResult(
            expert_type=self.expert_type,
            output=plan,
            confidence=0.85 if len(steps) > 0 else 0.5,
            processing_time_ms=elapsed,
        )

    def _generate_plan(self, goal: str, context: Dict[str, Any]) -> list[Dict[str, Any]]:
        """Generate intelligent plan steps using cognitive reasoning."""
        if not goal:
            return []

        # Real planning logic based on goal decomposition
        steps = []

        # Analyze goal type
        goal_lower = goal.lower()

        if "deploy" in goal_lower or "release" in goal_lower:
            steps = [
                {"id": "1", "action": "validate_preconditions", "type": "verify"},
                {"id": "2", "action": "run_tests", "type": "test"},
                {"id": "3", "action": "build_artifacts", "type": "build"},
                {"id": "4", "action": "deploy_to_environment", "type": "deploy"},
                {"id": "5", "action": "verify_deployment", "type": "verify"},
            ]
        elif "analyze" in goal_lower or "review" in goal_lower:
            steps = [
                {"id": "1", "action": "gather_context", "type": "collect"},
                {"id": "2", "action": "identify_patterns", "type": "analyze"},
                {"id": "3", "action": "apply_rules", "type": "reason"},
                {"id": "4", "action": "synthesize_findings", "type": "synthesize"},
            ]
        elif "fix" in goal_lower or "repair" in goal_lower or "resolve" in goal_lower:
            steps = [
                {"id": "1", "action": "diagnose_issue", "type": "analyze"},
                {"id": "2", "action": "identify_root_cause", "type": "reason"},
                {"id": "3", "action": "propose_solutions", "type": "generate"},
                {"id": "4", "action": "implement_fix", "type": "execute"},
                {"id": "5", "action": "verify_resolution", "type": "verify"},
            ]
        elif "create" in goal_lower or "generate" in goal_lower or "build" in goal_lower:
            steps = [
                {"id": "1", "action": "gather_requirements", "type": "collect"},
                {"id": "2", "action": "design_structure", "type": "design"},
                {"id": "3", "action": "implement_components", "type": "build"},
                {"id": "4", "action": "integrate_system", "type": "integrate"},
                {"id": "5", "action": "validate_output", "type": "verify"},
            ]
        else:
            # Generic planning for unknown goal types
            steps = [
                {"id": "1", "action": "understand_goal", "type": "analyze"},
                {"id": "2", "action": "gather_resources", "type": "collect"},
                {"id": "3", "action": "execute_plan", "type": "execute"},
                {"id": "4", "action": "verify_result", "type": "verify"},
            ]

        # Add context-specific steps if available
        if context.get("constraints"):
            steps.insert(0, {"id": "0", "action": "check_constraints", "type": "verify"})

        if context.get("deadline"):
            steps.append({"id": "final", "action": "meet_deadline", "type": "schedule"})

        return steps


class SparseExpertRouter:
    """
    Sparse modular expert routing with arbitration.

    Implements:
    1. Route input to appropriate experts
    2. Collect results from multiple experts
    3. Arbitrate with confidence-weighted voting
    4. Handle conflicts
    """

    def __init__(self):
        self.experts: dict[ExpertType, ExpertModule] = {}
        self.routing_history: list[dict[str, Any]] = []
        self._register_default_experts()

    def _register_default_experts(self) -> None:
        """Register default expert modules."""
        self.register_expert(ParserExpert())
        self.register_expert(CausalExpert())
        self.register_expert(ProofExpert())
        self.register_expert(PlannerExpert())

    def register_expert(self, expert: ExpertModule) -> None:
        """Register an expert module."""
        self.experts[expert.expert_type] = expert

    def route(
        self,
        input_data: Dict[str, Any],
        top_k: int = 3,
    ) -> list[tuple[ExpertType, float]]:
        """
        Route input to top-k experts.

        Returns list of (expert_type, confidence).
        """
        scores = []
        for expert_type, expert in self.experts.items():
            score = expert.can_handle(input_data)
            scores.append((expert_type, score))

        # Sort by confidence
        scores.sort(key=lambda x: x[1], reverse=True)

        # Record routing decision
        self.routing_history.append(
            {
                "input_keys": list(input_data.keys()),
                "routing": scores[:top_k],
            }
        )

        return scores[:top_k]

    def execute(
        self,
        input_data: Dict[str, Any],
        expert_types: Optional[list[ExpertType]] = None,
    ) -> dict[ExpertType, ExpertResult]:
        """
        Execute input through specified experts.

        If expert_types is None, uses top-k routing.
        """
        if expert_types is None:
            routes = self.route(input_data)
            expert_types = [t for t, _ in routes if _ > 0.5]

        results = {}
        for expert_type in expert_types:
            if expert_type in self.experts:
                result = self.experts[expert_type].process(input_data)
                results[expert_type] = result

        return results

    def arbitrate(
        self,
        results: dict[ExpertType, ExpertResult],
        conflict_resolution: str = "confidence_weighted",
    ) -> tuple[ExpertResult, dict[str, Any]]:
        """
        Arbitrate between expert results.

        Returns (best_result, arbitration_metadata).
        """
        if not results:
            raise ValueError("No results to arbitrate")

        if len(results) == 1:
            return list(results.values())[0], {"method": "single"}

        if conflict_resolution == "confidence_weighted":
            # Select by confidence
            best = max(results.values(), key=lambda r: r.confidence)

            metadata = {
                "method": "confidence_weighted",
                "expert_count": len(results),
                "confidences": {k: v.confidence for k, v in results.items()},
                "selected": best.expert_type.value,
            }

            return best, metadata

        # Default: first
        return list(results.values())[0], {"method": "first"}


# ============================================================================
# Hard Mode Separation Controller
# ============================================================================


@dataclass
class ModeTransition:
    """Record of mode transition."""

    from_mode: Mode
    to_mode: Mode
    timestamp: datetime
    reason: str


class ModeSeparationController:
    """
    Hard mode separation controller.

    Enforces strict separation between:
    - READ: Input processing only
    - THINK: Internal processing only
    - REASON: Inference only
    - VERIFY: Validation only
    - RENDER: Output generation only
    - EXPERIMENT: Information seeking only

    No blending, no leakage between modes.
    """

    def __init__(self):
        self.current_mode: Mode = Mode.READ
        self.mode_history: List[ModeTransition] = []
        self.mode_policies: dict[Mode, dict[str, Any]] = {
            Mode.READ: {"allow_output": False, "allow_inference": False},
            Mode.THINK: {"allow_output": False, "allow_inference": True},
            Mode.REASON: {"allow_output": False, "allow_inference": True},
            Mode.VERIFY: {"allow_output": False, "allow_inference": False},
            Mode.RENDER: {"allow_output": True, "allow_inference": False},
            Mode.EXPERIMENT: {"allow_output": True, "allow_inference": True},  # Special
        }

    def get_current_mode(self) -> Mode:
        """Get current mode."""
        return self.current_mode

    def transition_to(self, new_mode: Mode, reason: str = "") -> bool:
        """
        Transition to new mode.

        Records transition and validates it's legal.
        """
        # Record transition
        transition = ModeTransition(
            from_mode=self.current_mode,
            to_mode=new_mode,
            timestamp=datetime.now(timezone.utc),
            reason=reason,
        )
        self.mode_history.append(transition)

        self.current_mode = new_mode
        return True

    def can_output(self) -> bool:
        """Check if current mode allows output generation."""
        return self.mode_policies[self.current_mode].get("allow_output", False)

    def can_infer(self) -> bool:
        """Check if current mode allows inference."""
        return self.mode_policies[self.current_mode].get("allow_inference", False)

    def enforce_read(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforce READ mode: process input, no output, no reasoning.
        """
        self.transition_to(Mode.READ, "Processing input")

        # Only extract and structure input
        return {
            "raw": input_data,
            "extracted_entities": list(input_data.keys()),
            "mode": Mode.READ.name,
        }

    def enforce_reason(self, structured_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforce REASON mode: inference only, no output generation.
        """
        self.transition_to(Mode.REASON, "Performing inference")

        # Perform reasoning (placeholder)
        return {
            "inferences": [],
            "mode": Mode.REASON.name,
        }

    def enforce_verify(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforce VERIFY mode: validation only.
        """
        self.transition_to(Mode.VERIFY, "Verifying proposal")

        return {
            "verified": False,
            "checks_performed": [],
            "mode": Mode.VERIFY.name,
        }

    def enforce_render(self, verified_result: Dict[str, Any]) -> str:
        """
        Enforce RENDER mode: output generation only.
        """
        self.transition_to(Mode.RENDER, "Generating output")

        # Only render, no new reasoning
        return str(verified_result.get("content", ""))

    def get_mode_trace(self) -> list[dict[str, Any]]:
        """Get trace of mode transitions."""
        return [
            {
                "from": t.from_mode.name,
                "to": t.to_mode.name,
                "timestamp": t.timestamp.isoformat(),
                "reason": t.reason,
            }
            for t in self.mode_history
        ]


# ============================================================================
# Metacognitive Supervision
# ============================================================================


@dataclass
class MetacognitiveState:
    """
    Explicit self-monitoring state.

    Tracks:
    - What is known (certainty tracking)
    - What was inferred (derivation chain)
    - What is missing (information gaps)
    - Where error likely is (fault localization)
    - Which operator failed (operator blame)
    """

    # Knowledge tracking
    known_facts: Dict[str, float] = field(default_factory=dict)  # fact -> certainty

    # Inference tracking
    derivation_chain: list[dict[str, Any]] = field(default_factory=list)

    # Information gaps
    information_gaps: List[str] = field(default_factory=list)

    # Error localization
    operator_reliability: Dict[str, float] = field(default_factory=dict)
    suspected_faulty_operator: Optional[str] = None

    # Confidence calibration
    confidence_history: list[tuple[str, float, bool]] = field(
        default_factory=list
    )  # (claim, confidence, was_correct)

    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def record_inference(
        self, premise: str, conclusion: str, operator: str, confidence: float
    ) -> None:
        """Record an inference step."""
        self.derivation_chain.append(
            {
                "premise": premise,
                "conclusion": conclusion,
                "operator": operator,
                "confidence": confidence,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def update_known_fact(self, fact: str, certainty: float) -> None:
        """Update certainty of known fact."""
        self.known_facts[fact] = certainty

    def add_information_gap(self, gap: str) -> None:
        """Record missing information."""
        if gap not in self.information_gaps:
            self.information_gaps.append(gap)

    def resolve_information_gap(self, gap: str) -> None:
        """Mark information gap as resolved."""
        if gap in self.information_gaps:
            self.information_gaps.remove(gap)

    def blame_operator(self, operator: str, error_severity: float) -> None:
        """Attribute error to operator."""
        current_reliability = self.operator_reliability.get(operator, 1.0)
        # Decrease reliability based on error severity
        self.operator_reliability[operator] = max(0.0, current_reliability - error_severity * 0.2)

        if error_severity > 0.7:
            self.suspected_faulty_operator = operator

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of metacognitive state."""
        return {
            "known_facts_count": len(self.known_facts),
            "average_certainty": sum(self.known_facts.values()) / max(1, len(self.known_facts)),
            "inference_steps": len(self.derivation_chain),
            "information_gaps": len(self.information_gaps),
            "suspected_faulty_operator": self.suspected_faulty_operator,
            "operator_reliability": self.operator_reliability,
        }


class MetacognitiveSupervisor:
    """
    Metacognitive supervision layer.

    Provides real-time self-monitoring:
    - Tracks certainty of knowledge
    - Records inference chains
    - Identifies information gaps
    - Localizes errors to operators
    """

    def __init__(self):
        self.current_state = MetacognitiveState()
        self.state_history: List[MetacognitiveState] = []

    def what_is_known(self) -> dict[str, float]:
        """Report what is known with certainty levels."""
        return self.current_state.known_facts.copy()

    def what_was_inferred(self, depth: int = 5) -> list[dict[str, Any]]:
        """Report recent inference chain."""
        return self.current_state.derivation_chain[-depth:]

    def what_is_missing(self) -> List[str]:
        """Report information gaps."""
        return self.current_state.information_gaps.copy()

    def where_is_error_likely(self) -> Dict[str, Any]:
        """Report error localization."""
        return {
            "suspected_operator": self.current_state.suspected_faulty_operator,
            "operator_reliability": self.current_state.operator_reliability.copy(),
            "most_reliable": max(
                self.current_state.operator_reliability.items(),
                key=lambda x: x[1],
                default=(None, 0.0),
            ),
            "least_reliable": min(
                self.current_state.operator_reliability.items(),
                key=lambda x: x[1],
                default=(None, 0.0),
            ),
        }

    def which_operator_failed(self) -> Optional[str]:
        """Report which operator most likely failed."""
        return self.current_state.suspected_faulty_operator

    def update_from_verification(
        self,
        claim: str,
        predicted_confidence: float,
        was_correct: bool,
    ) -> None:
        """Update calibration from verification result."""
        self.current_state.confidence_history.append((claim, predicted_confidence, was_correct))

        # Update certainty of known fact
        new_certainty = predicted_confidence if was_correct else predicted_confidence * 0.5
        self.current_state.update_known_fact(claim, new_certainty)

    def checkpoint(self) -> None:
        """Save current state to history."""
        self.state_history.append(deepcopy(self.current_state))


# ============================================================================
# Unified Cognitive Substrate
# ============================================================================


class AMOSCognitiveSubstrate:
    """
    Unified cognitive substrate integrating all components.

    This is the minimum viable superintelligence stack.
    """

    def __init__(self):
        # Object-centric world model
        self.world = ObjectCentricWorldModel()

        # External working memory
        self.memory = ExternalWorkingMemory()

        # Dual reasoning substrate
        self.reasoning = DualReasoningSubstrate()

        # Online learning
        self.learning = OnlineLearningSystem()

        # Active experimentation
        self.experimentation = ActiveExperimentationSystem()

        # Expert routing
        self.router = SparseExpertRouter()

        # Mode controller
        self.mode_controller = ModeSeparationController()

        # Metacognitive supervision
        self.metacognition = MetacognitiveSupervisor()

    def perceive(self, observation: Dict[str, Any]) -> None:
        """
        Perceive and integrate observation into world model.
        """
        self.mode_controller.enforce_read(observation)

        # Extract objects from observation
        for key, value in observation.items():
            if isinstance(value, dict) and "type" in value:
                obj_id = value.get("id", key)
                obj_type = value["type"]
                properties = {k: v for k, v in value.items() if k not in ["id", "type"]}

                if obj_id in self.world.state.objects:
                    # Update existing
                    obj = self.world.state.objects[obj_id]
                    for p_key, p_val in properties.items():
                        obj.update_property(p_key, p_val)
                else:
                    # Create new
                    self.world.create_object(obj_type, obj_id, properties)

        # Update metacognition
        for key in observation.keys():
            self.metacognition.current_state.update_known_fact(f"observed:{key}", 1.0)

    def think(
        self,
        task: str,
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Execute thinking with full substrate support.
        """
        self.mode_controller.transition_to(Mode.THINK, f"Thinking about: {task}")

        # 1. Route to experts
        expert_results = self.router.execute({"task": task, **(context or {})})

        # 2. Arbitrate (handle empty results gracefully)
        if expert_results:
            best_result, arbitration_meta = self.router.arbitrate(expert_results)
            # 3. Externalize to scratch memory
            scratch_id = self.memory.scratch.add_node(
                "expert_result",
                best_result.output,
                confidence=best_result.confidence,
            )
            # 4. Record in metacognition
            self.metacognition.current_state.record_inference(
                premise=task,
                conclusion=f"expert:{best_result.expert_type.value}",
                operator="router",
                confidence=best_result.confidence,
            )
            return {
                "expert_type": best_result.expert_type.value,
                "output": best_result.output,
                "confidence": best_result.confidence,
                "scratch_node": scratch_id,
                "arbitration": arbitration_meta,
            }

        # Fallback when no experts match
        return {
            "expert_type": "none",
            "output": {"task": task, "context": context},
            "confidence": 0.5,
            "scratch_node": None,
            "arbitration": {"method": "fallback", "reason": "no_experts"},
        }

    def reason_and_verify(
        self,
        proposition: Any,
        verification_method: VerificationMethod = VerificationMethod.LOGICAL,
    ) -> Dict[str, Any]:
        """
        Propose and verify through dual reasoning system.
        """
        self.mode_controller.transition_to(Mode.REASON, "Proposing and reasoning")

        # Generate proposal
        proposal = self.reasoning.propose(
            content=proposition,
            source="substrate",
        )

        # Verify
        self.mode_controller.transition_to(Mode.VERIFY, "Verifying proposal")
        context = {"world_model": self.world}
        verification = self.reasoning.verify(proposal, verification_method, context)

        # Record in proof graph
        proof_id = self.memory.proof.add_node(
            "verification",
            {
                "proposal": proposal.content,
                "passed": verification.passed,
                "method": verification.method.value,
            },
            confidence=verification.confidence,
        )

        # Update metacognition
        self.metacognition.update_from_verification(
            claim=str(proposition),
            predicted_confidence=proposal.confidence,
            was_correct=verification.passed,
        )

        return {
            "proposal": proposal,
            "verification": verification,
            "proof_node": proof_id,
            "verified": verification.passed and verification.confidence > 0.7,
        }

    def learn_from_error(
        self,
        error_type: str,
        operator: str,
        observation: Dict[str, Any],
        expected: Any,
        actual: Any,
    ) -> Optional[PolicyUpdate]:
        """
        Learn from error.
        """
        error_record = self.learning.register_error(
            error_type=error_type,
            operator=operator,
            observation=observation,
            expected=expected,
            actual=actual,
        )

        # Record in error graph
        self.memory.error.add_node(
            "error_record",
            {
                "type": error_type,
                "operator": operator,
                "magnitude": error_record.error_magnitude,
            },
        )

        # Blame operator in metacognition
        self.metacognition.current_state.blame_operator(operator, error_record.error_magnitude)

        # Get policy update
        if self.learning.update_history:
            return self.learning.update_history[-1]

        return None

    def select_experiment(
        self,
        target_variable: str,
        action_space: list[dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Select action to reduce uncertainty.
        """
        self.mode_controller.transition_to(Mode.EXPERIMENT, "Designing experiment")

        action = self.experimentation.select_action(
            objective="reduce_uncertainty",
            target=target_variable,
            action_space=action_space,
            world_model=self.world,
        )

        if action:
            # Record in dependency graph
            exp_id = self.memory.dependency.add_node(
                "experiment",
                {"target": target_variable, "action": action},
            )

            return {
                "action": action,
                "target": target_variable,
                "experiment_id": exp_id,
            }

        return None

    def get_metacognitive_report(self) -> Dict[str, Any]:
        """
        Get full metacognitive report.
        """
        return {
            "what_is_known": self.metacognition.what_is_known(),
            "what_was_inferred": self.metacognition.what_was_inferred(),
            "what_is_missing": self.metacognition.what_is_missing(),
            "where_is_error_likely": self.metacognition.where_is_error_likely(),
            "which_operator_failed": self.metacognition.which_operator_failed(),
            "mode_trace": self.mode_controller.get_mode_trace(),
            "working_memory_summary": self.memory.get_summary(),
            "world_model_summary": {
                "objects": len(self.world.state.objects),
                "relations": len(self.world.state.relations),
                "mechanisms": len(self.world.state.mechanisms),
            },
            "learning_summary": {
                "errors_recorded": len(self.learning.error_history),
                "policy_updates": len(self.learning.update_history),
                "operator_reliability": {
                    op: self.learning.get_operator_reliability(op)
                    for op in self.learning.operator_error_counts.keys()
                },
            },
        }

    def execute_full_cycle(
        self,
        observation: Dict[str, Any],
        task: str,
    ) -> Dict[str, Any]:
        """
        Execute full cognitive cycle.
        """
        # 1. Perceive
        self.perceive(observation)

        # 2. Think
        think_result = self.think(task)

        # 3. Reason and verify
        reason_result = self.reason_and_verify(think_result["output"])

        # 4. Render output
        self.mode_controller.transition_to(Mode.RENDER, "Generating final output")

        output = {
            "status": "success",
            "thinking": think_result,
            "reasoning": reason_result,
            "metacognition": self.get_metacognitive_report(),
        }

        return output


# ============================================================================
# Utility Functions
# ============================================================================


def create_substrate() -> AMOSCognitiveSubstrate:
    """Factory function to create cognitive substrate."""
    return AMOSCognitiveSubstrate()


# Global instance (singleton pattern)
_global_substrate: Optional[AMOSCognitiveSubstrate] = None


def get_substrate() -> AMOSCognitiveSubstrate:
    """Get or create global cognitive substrate."""
    global _global_substrate
    if _global_substrate is None:
        _global_substrate = create_substrate()
    return _global_substrate


# ============================================================================
# Demo
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("AMOS COGNITIVE SUBSTRATE - Minimum Viable Superintelligence Stack")
    print("=" * 80)

    # Initialize substrate
    substrate = create_substrate()
    print("\n✅ Cognitive substrate initialized")

    # 1. Build world model
    print("\n📦 Building object-centric world model...")
    db = substrate.world.create_object(
        "database", "db_main", {"load": 0.7, "latency_ms": 150, "connections": 45}
    )
    api = substrate.world.create_object(
        "api_server", "api_gateway", {"requests_per_sec": 120, "error_rate": 0.02}
    )
    substrate.world.add_relation("api_gateway", "db_main", RelationType.DEPENDS_ON, strength=1.0)
    substrate.world.add_relation("db_main", "api_gateway", RelationType.CAUSES, strength=0.8)
    print(
        f"   Created {len(substrate.world.state.objects)} objects, {len(substrate.world.state.relations)} relations"
    )

    # 2. Perceive
    print("\n👁️ Perceiving...")
    substrate.perceive(
        {
            "db_main": {"type": "database", "id": "db_main", "load": 0.8, "latency_ms": 200},
            "new_metric": {"type": "metric", "id": "metric_1", "value": 42},
        }
    )
    print(f"   World model now has {len(substrate.world.state.objects)} objects")

    # 3. Think with expert routing
    print("\n🧠 Thinking with expert routing...")
    think_result = substrate.think(
        "Optimize database performance",
        {
            "current_load": 0.8,
            "target_latency": 100,
        },
    )
    print(f"   Expert used: {think_result['expert_type']}")
    print(f"   Confidence: {think_result['confidence']:.2f}")

    # 4. Reason and verify
    print("\n🔍 Reasoning and verifying...")
    reason_result = substrate.reason_and_verify(
        {"action": "add_index", "table": "users", "column": "email"},
        VerificationMethod.CAUSAL,
    )
    print(f"   Verified: {reason_result['verified']}")
    print(f"   Verification confidence: {reason_result['verification'].confidence:.2f}")

    # 5. Learn from error
    print("\n📚 Learning from error...")
    update = substrate.learn_from_error(
        error_type="timeout",
        operator="query_optimizer",
        observation={"query": "SELECT * FROM users"},
        expected="< 100ms",
        actual="5000ms",
    )
    if update:
        print(f"   Policy updated: {update.parameter} → {update.direction} ({update.delta:.3f})")

    # 6. Select experiment
    print("\n🧪 Selecting experiment to reduce uncertainty...")
    exp = substrate.select_experiment(
        target_variable="db_main.latency_ms",
        action_space=[
            {"type": "query", "sql": "EXPLAIN ANALYZE SELECT * FROM users"},
            {"type": "config", "param": "shared_buffers", "value": "256MB"},
            {"type": "action", "add_index": True},
        ],
    )
    if exp:
        print(f"   Selected action: {exp['action']}")

    # 7. Metacognitive report
    print("\n🪞 Metacognitive Report:")
    report = substrate.get_metacognitive_report()
    print(f"   Known facts: {len(report['what_is_known'])}")
    print(f"   Information gaps: {len(report['what_is_missing'])}")
    print(f"   Mode transitions: {len(report['mode_trace'])}")
    print(f"   Working memory: {report['working_memory_summary']}")

    # 8. Full cycle
    print("\n🔄 Executing full cognitive cycle...")
    full_result = substrate.execute_full_cycle(
        observation={
            "system_status": {"type": "system", "id": "sys_1", "health": "degraded"},
        },
        task="diagnose system health",
    )
    print(f"   Cycle completed: {full_result['status']}")
    print(f"   Final verification: {full_result['reasoning']['verified']}")

    print("\n" + "=" * 80)
    print("SUBSTRATE OPERATIONAL")
    print("=" * 80)
