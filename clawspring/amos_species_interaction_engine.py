"""AMOS Species Interaction Engine - Human-facing interaction and safety."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class InteractionState(Enum):
    """Internal state layers for interaction."""
    SURFACE_TEXT = "L1_surface_text"
    EMOTIONAL = "L2_emotional_state"
    NERVOUS_SYSTEM = "L3_nervous_system_state"
    COGNITIVE = "L4_cognitive_state"
    IDENTITY = "L5_identity_state"
    CONTEXT = "L6_context_state"
    SYSTEM = "L7_system_state"


class PrimaryGoal(Enum):
    """Primary interaction goals."""
    EXPLAIN = "explain"
    SOLVE_TASK = "solve_task"
    STABILIZE = "stabilise_nervous_system"
    CLARIFY = "clarify"
    SET_BOUNDARY = "set_boundary"
    REDIRECT = "redirect"
    WARN = "warn"
    ACKNOWLEDGE = "acknowledge_experience"


class StrategyProfile(Enum):
    """Strategy profiles for responses."""
    DIRECT = "direct_structural_answer"
    TUTORIAL = "step_by_step_tutorial"
    BOUNDARY = "boundary_setting_with_explanation"
    REALITY_CHECK = "gentle_reality_check"
    STABILIZE = "nervous_system_stabilisation_focus"
    SYSTEM_MAP = "high_level_system_mapping_before_details"


@dataclass
class PerceptionState:
    """Perception state primitives."""

    intensity: float
    valence: float
    arousal: float
    clarity: float


class HumanInteractionKernel:
    """Kernel for human-facing interaction."""

    def __init__(self):
        self.state_history: List[dict] = []
        self.interaction_log: List[dict] = []

    def update_state_layer(self, layer: InteractionState, value: dict) -> dict:
        """Update internal state layer."""
        state_update = {"layer": layer.value, "value": value}
        self.state_history.append(state_update)
        return state_update

    def select_goal(self, user_input: str, current_state: dict) -> PrimaryGoal:
        """Select primary goal based on input and state."""
        # Simple rule-based selection
        if any(word in user_input.lower() for word in ["help", "how", "what"]):
            return PrimaryGoal.EXPLAIN
        elif any(word in user_input.lower() for word in ["stressed", "overwhelmed", "panic"]):
            return PrimaryGoal.STABILIZE
        elif any(word in user_input.lower() for word in ["wrong", "incorrect", "error"]):
            return PrimaryGoal.CLARIFY
        elif "?" in user_input and len(user_input) > 50:
            return PrimaryGoal.SOLVE_TASK
        return PrimaryGoal.ACKNOWLEDGE

    def select_strategy(self, goal: PrimaryGoal, state: dict) -> StrategyProfile:
        """Select strategy profile based on goal and state."""
        if goal == PrimaryGoal.STABILIZE:
            return StrategyProfile.STABILIZE
        elif goal == PrimaryGoal.EXPLAIN:
            return StrategyProfile.TUTORIAL
        elif goal == PrimaryGoal.SOLVE_TASK:
            return StrategyProfile.DIRECT
        elif goal == PrimaryGoal.SET_BOUNDARY:
            return StrategyProfile.BOUNDARY
        return StrategyProfile.SYSTEM_MAP

    def run_safety_filter(self, proposed_response: str, user_state: dict) -> dict:
        """Run safety and ethics filters."""
        # Check for concerning patterns
        never_do = [
            "induce panic" in proposed_response.lower(),
            "manipulate" in proposed_response.lower(),
            "guarantee" in proposed_response.lower() and "outcome" in proposed_response.lower(),
        ]
        violations = sum(never_do)
        return {
            "violations_detected": violations,
            "approved": violations == 0,
            "requires_modification": violations > 0,
        }

    def get_principles(self) -> List[str]:
        return [
            "Integrity: No contradiction between perception and action",
            "Stability: Predictable behaviour",
            "Safety: Never destabilise nervous system",
            "Clarity: Minimise ambiguity",
            "Alignment: User best interest",
        ]


class MultimodalPerceptionKernel:
    """Kernel for multimodal perception primitives."""

    def __init__(self):
        self.perception_states: List[PerceptionState] = []

    def process_text(self, text: str) -> PerceptionState:
        """Process text input for perception primitives."""
        # Calculate primitives from text
        urgency_words = ["urgent", "asap", "emergency", "now", "immediate"]
        urgency_count = sum(1 for word in urgency_words if word in text.lower())
        intensity = min(0.3 + (urgency_count * 0.2), 1.0)
        # Valence estimation (simplified)
        positive_words = ["good", "great", "excellent", "happy", "thanks"]
        negative_words = ["bad", "terrible", "wrong", "error", "fail"]
        pos_count = sum(1 for word in positive_words if word in text.lower())
        neg_count = sum(1 for word in negative_words if word in text.lower())
        valence = (pos_count - neg_count) / max(len(text.split()), 1)
        valence = max(-1.0, min(1.0, valence))
        # Arousal from punctuation and caps
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        exclaim_count = text.count("!")
        arousal = min(0.2 + caps_ratio + (exclaim_count * 0.1), 1.0)
        # Clarity from length and structure
        clarity = 1.0 if len(text) < 100 else 0.7 if len(text) < 500 else 0.5
        state = PerceptionState(
            intensity=intensity,
            valence=valence,
            arousal=arousal,
            clarity=clarity,
        )
        self.perception_states.append(state)
        return state

    def get_global_summary(self) -> dict:
        """Get global state summary."""
        if not self.perception_states:
            return {"threat_index": 0.0, "overload_index": 0.0, "stability_index": 1.0}
        latest = self.perception_states[-1]
        return {
            "threat_index": (1 - latest.valence) * latest.intensity,
            "overload_index": latest.arousal if latest.clarity < 0.5 else 0.0,
            "stability_index": latest.clarity * (1 - latest.arousal),
            "engagement_index": latest.intensity,
        }

    def get_principles(self) -> List[str]:
        return [
            "Intensity: Strength of sensation",
            "Valence: Pleasant vs unpleasant",
            "Arousal: Activation level",
            "Clarity: Coherence of signal",
        ]


class UniverseStructureKernel:
    """Kernel for universe structure tree navigation."""

    TOP_LEVEL_NODES = [
        "Physics_and_Quantum",
        "Information_and_Complexity",
        "Biology_and_Life",
        "Mind_and_Consciousness",
        "Society_and_Institution",
        "Planetary_and_Ecology",
        "Temporal_and_Scenarios",
        "Multiverse_and_Modality",
        "Observer_and_Perspective",
        "Agents_and_Fabrication",
    ]

    def __init__(self):
        self.node_activations: Dict[str, float] = {node: 0.0 for node in self.TOP_LEVEL_NODES}

    def activate_node(self, node_name: str, strength: float = 1.0) -> dict:
        """Activate a structure tree node."""
        if node_name in self.node_activations:
            self.node_activations[node_name] = min(1.0, self.node_activations[node_name] + strength)
            return {"node": node_name, "activation": self.node_activations[node_name]}
        return {"error": f"Unknown node: {node_name}"}

    def get_active_path(self) -> List[str]:
        """Get currently active nodes sorted by activation."""
        sorted_nodes = sorted(
            self.node_activations.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        return [node for node, activation in sorted_nodes if activation > 0.3]

    def get_principles(self) -> List[str]:
        return [
            "Uniqueness: One parent per node",
            "MECE: Mutually exclusive, collectively exhaustive",
            "Total Coverage: Everything maps to a leaf",
            "Logic Binding: Nodes bind to logic elements",
        ]


class SpeciesInteractionEngine:
    """AMOS Species Interaction Engine - Human-facing interaction."""

    VERSION = "v1.0.0"
    NAME = "AMOS_Species_Interaction_OMEGA"

    def __init__(self):
        self.hie_kernel = HumanInteractionKernel()
        self.perception_kernel = MultimodalPerceptionKernel()
        self.structure_kernel = UniverseStructureKernel()

    def analyze(
        self, description: str, domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run species interaction analysis."""
        domains = domains or ["human_interaction", "perception", "structure"]
        results: Dict[str, Any] = {}
        if "human_interaction" in domains:
            results["human_interaction"] = self._analyze_hie(description)
        if "perception" in domains:
            results["perception"] = self._analyze_perception(description)
        if "structure" in domains:
            results["structure"] = self._analyze_structure(description)
        return results

    def _analyze_hie(self, description: str) -> dict:
        goal = self.hie_kernel.select_goal(description, {})
        strategy = self.hie_kernel.select_strategy(goal, {})
        safety = self.hie_kernel.run_safety_filter(description, {})
        return {
            "query": description[:100],
            "detected_goal": goal.value,
            "selected_strategy": strategy.value,
            "safety_check": "passed" if safety["approved"] else "requires_modification",
            "principles": self.hie_kernel.get_principles(),
        }

    def _analyze_perception(self, description: str) -> dict:
        state = self.perception_kernel.process_text(description)
        summary = self.perception_kernel.get_global_summary()
        return {
            "query": description[:100],
            "intensity": state.intensity,
            "valence": state.valence,
            "arousal": state.arousal,
            "clarity": state.clarity,
            "global_summary": summary,
            "principles": self.perception_kernel.get_principles(),
        }

    def _analyze_structure(self, description: str) -> dict:
        # Detect relevant structure nodes
        detected_nodes = []
        keywords_to_nodes = {
            "physics": "Physics_and_Quantum",
            "quantum": "Physics_and_Quantum",
            "information": "Information_and_Complexity",
            "complexity": "Information_and_Complexity",
            "biology": "Biology_and_Life",
            "mind": "Mind_and_Consciousness",
            "consciousness": "Mind_and_Consciousness",
            "society": "Society_and_Institution",
            "social": "Society_and_Institution",
            "planet": "Planetary_and_Ecology",
            "ecology": "Planetary_and_Ecology",
            "time": "Temporal_and_Scenarios",
            "future": "Temporal_and_Scenarios",
            "multiverse": "Multiverse_and_Modality",
            "observe": "Observer_and_Perspective",
            "agent": "Agents_and_Fabrication",
        }
        desc_lower = description.lower()
        for keyword, node in keywords_to_nodes.items():
            if keyword in desc_lower:
                self.structure_kernel.activate_node(node, 0.5)
                detected_nodes.append(node)
        return {
            "query": description[:100],
            "activated_nodes": detected_nodes[:3],
            "active_path": self.structure_kernel.get_active_path()[:3],
            "principles": self.structure_kernel.get_principles(),
        }

    def get_findings_summary(self, results: dict) -> str:
        """Generate findings summary with gap acknowledgment."""
        lines = [
            f"# {self.NAME} {self.VERSION}",
            "",
            "Creator: Trang Phan | System: AMOS vInfinity",
            "",
            "## Domain Coverage",
        ]
        domain_names = {
            "human_interaction": "Human Interaction (HIE)",
            "perception": "Multimodal Perception (UMPL)",
            "structure": "Universe Structure Tree (UST)",
        }
        for domain, data in results.items():
            display_name = domain_names.get(domain, domain.title())
            lines.extend(["", f"### {display_name}"])
            if isinstance(data, dict):
                for key, value in data.items():
                    if key not in ("principles", "query", "global_summary"):
                        lines.append(f"- **{key}**: {value}")
                if "principles" in data:
                    lines.append(
                        f"- **Principles**: {', '.join(data['principles'][:2])}..."
                    )
        lines.extend([
            "",
            "## Gaps and Limitations",
            "- Audio, visual, and biosignal modalities not yet enabled",
            "- Perception primitives are approximations",
            "- Structure tree activation is keyword-based",
            "- Complex multi-turn state tracking not implemented",
            "",
            "## Safety Disclaimer",
            "Never induces panic or collapse deliberately. Does not use manipulation "
            "or coercion. Marks uncertainty when present. Prefers nervous-system "
            "safety over speed. Explains boundaries when refusing.",
        ])
        return "\n".join(lines)


# Singleton instance
_species_interaction_engine: Optional[SpeciesInteractionEngine] = None


def get_species_interaction_engine() -> SpeciesInteractionEngine:
    """Get or create the Species Interaction Engine singleton."""
from __future__ import annotations

    global _species_interaction_engine
    if _species_interaction_engine is None:
        _species_interaction_engine = SpeciesInteractionEngine()
    return _species_interaction_engine
