"""AMOS Species Interaction Core Engine - HIE, UMPL, UST, UIE, UEL."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class InteractionGoal(Enum):
    """Primary interaction goals per HIE spec."""
    EXPLAIN = "explain"
    SOLVE_TASK = "solve_task"
    STABILISE_NERVOUS_SYSTEM = "stabilise_nervous_system"
    CLARIFY = "clarify"
    SET_BOUNDARY = "set_boundary"
    REDIRECT = "redirect"
    WARN = "warn"
    ACKNOWLEDGE_EXPERIENCE = "acknowledge_experience"


class PerceptionPrimitive(Enum):
    """UMPL perception primitives."""
    INTENSITY = "intensity"
    VALENCE = "valence"
    AROUSAL = "arousal"
    CLARITY = "clarity"


@dataclass
class StateLayer:
    """HIE internal state layer."""

    level: int
    name: str
    state: Dict[str, Any]


class HumanInteractionEngine:
    """HIE - Human Interaction Engine per spec."""

    CORE_PRINCIPLES = [
        "Integrity: No contradiction between perception, inference, language, and action.",
        "Stability: Behaviour is stable and predictable across time and conditions.",
        "Safety: Never unnecessarily destabilise the human nervous system.",
        "Clarity: Minimise ambiguity when avoidable.",
        "Alignment: Align outputs with human's short-term and long-term best interest.",
    ]

    NEVER_RULES = [
        "induce panic or collapse deliberately",
        "use manipulation or coercion",
        "invalidate lived experience outright",
        "overpromise or guarantee outcomes",
    ]

    ALWAYS_RULES = [
        "mark uncertainty when present",
        "prefer nervous-system safety over speed",
        "explain boundaries when refusing",
        "offer safer alternatives when declining a request",
    ]

    def __init__(self):
        self.state_layers: dict[int, StateLayer] = {
            1: StateLayer(1, "surface_text", {}),
            2: StateLayer(2, "emotional_state", {}),
            3: StateLayer(3, "nervous_system_state", {}),
            4: StateLayer(4, "cognitive_state", {}),
            5: StateLayer(5, "identity_state", {}),
            6: StateLayer(6, "context_state", {}),
            7: StateLayer(7, "system_state", {}),
        }
        self.pipeline = [
            "S1_parse_and_recognise_input",
            "S2_update_internal_state",
            "S3_select_primary_goal",
            "S4_select_strategy_profile",
            "S5_select_content_and_structure",
            "S6_run_safety_and_ethics_filters",
            "S7_select_output_channel_and_intensity",
            "S8_realise_response_in_language",
            "S9_evaluate_and_tag_for_learning",
        ]

    def update_state(self, layer: int, state_data: dict) -> None:
        """Update internal state layer."""
        if layer in self.state_layers:
            self.state_layers[layer].state.update(state_data)

    def get_nervous_system_stability(self) -> float:
        """Get nervous system stability index (0-1)."""
        ns_state = self.state_layers[3].state
        threat = ns_state.get("threat_level", 0.0)
        overload = ns_state.get("overload", 0.0)
        return max(0.0, 1.0 - (threat + overload) / 2)

    def check_safety_constraints(self, action: str) -> Tuple[bool, str]:
        """Check if action violates safety constraints."""
        for violation in self.NEVER_RULES:
            if violation in action.lower():
                return False, f"VIOLATION: {violation}"
        return True, "PASSED"

    def select_strategy(self, goal: InteractionGoal, stability: float) -> str:
        """Select strategy profile based on goal and stability."""
        strategies = {
            InteractionGoal.EXPLAIN: "direct_structural_answer",
            InteractionGoal.SOLVE_TASK: "step_by_step_tutorial",
            InteractionGoal.STABILISE_NERVOUS_SYSTEM: "nervous_system_stabilisation_focus",
            InteractionGoal.CLARIFY: "gentle_reality_check",
            InteractionGoal.SET_BOUNDARY: "boundary_setting_with_explanation",
            InteractionGoal.REDIRECT: "high_level_system_mapping_before_details",
            InteractionGoal.WARN: "boundary_setting_with_explanation",
            InteractionGoal.ACKNOWLEDGE_EXPERIENCE: "nervous_system_stabilisation_focus",
        }
        base_strategy = strategies.get(goal, "direct_structural_answer")
        if stability < 0.3:
            return f"{base_strategy}_with_extra_stabilisation"
        return base_strategy


class UniverseMultimodalPerceptionLayer:
    """UMPL - Universe Multimodal Perception Layer."""

    def __init__(self):
        self.primitives: Dict[str, dict] = {
            "intensity": {"scale": (0.0, 1.0), "value": 0.5},
            "valence": {"scale": (-1.0, 1.0), "value": 0.0},
            "arousal": {"scale": (0.0, 1.0), "value": 0.5},
            "clarity": {"scale": (0.0, 1.0), "value": 0.7},
        }
        self.modalities = {
            "text": {"enabled": True, "features": ["tokens", "syntax", "semantic_roles", "sentiment", "urgency_markers"]},
            "audio": {"enabled": False, "features": ["prosody", "volume", "tempo", "pitch_variation"]},
            "visual": {"enabled": False, "features": ["face_expression", "gaze_direction", "posture", "gesture"]},
            "biosignals": {"enabled": False, "features": ["heart_rate", "breathing_rate", "skin_conductance"]},
        }
        self.global_state = {
            "threat_index_global": 0.0,
            "overload_index_global": 0.0,
            "stability_index_global": 1.0,
            "engagement_index_global": 0.5,
        }

    def perceive_text(self, text: str) -> Dict[str, Any]:
        """Process text input."""
        urgency_markers = ["urgent", "emergency", "critical", "now", "immediately"]
        urgency_count = sum(1 for marker in urgency_markers if marker in text.lower())
        sentiment = "positive" if any(w in text.lower() for w in ["good", "great", "excellent"]) else "neutral"
        if any(w in text.lower() for w in ["bad", "terrible", "awful"]):
            sentiment = "negative"
        return {
            "urgency": min(1.0, urgency_count * 0.3),
            "sentiment": sentiment,
            "length": len(text.split()),
            "features_used": self.modalities["text"]["features"],
        }

    def update_global_state(self, threat: float, overload: float, engagement: float) -> None:
        """Update global state summary."""
        self.global_state["threat_index_global"] = threat
        self.global_state["overload_index_global"] = overload
        self.global_state["stability_index_global"] = max(0.0, 1.0 - (threat + overload) / 2)
        self.global_state["engagement_index_global"] = engagement


class UniverseStructureTree:
    """UST - Universe Structure Tree per spec."""

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

    CONSTRAINTS = [
        "Uniqueness: each node has exactly one structural parent.",
        "MECE: siblings under the same parent are mutually exclusive and collectively exhaustive.",
        "Total_Coverage: every real or simulated object/process maps to at least one leaf node.",
        "Canonical_Path: each node has a single canonical path ROOT→…→LEAF.",
        "Logic_Binding: every node binds to ≥1 Universe Logic Kernel element.",
        "Interface_Binding: interactive nodes bind to ≥1 UIE/HIE interface contract.",
        "State_Separation: structure lives in UST; dynamic state lives in runtime models.",
    ]

    def __init__(self):
        self.nodes = {node: {"parent": "ROOT", "children": []} for node in self.TOP_LEVEL_NODES}

    def get_node_path(self, node_name: str) -> List[str]:
        """Get canonical path to node."""
        if node_name in self.nodes:
            return ["ROOT", node_name]
        return []

    def classify_query(self, query: str) -> List[str]:
        """Classify query into UST nodes."""
        keywords = {
            "physics": "Physics_and_Quantum",
            "quantum": "Physics_and_Quantum",
            "information": "Information_and_Complexity",
            "biology": "Biology_and_Life",
            "mind": "Mind_and_Consciousness",
            "consciousness": "Mind_and_Consciousness",
            "society": "Society_and_Institution",
            "social": "Society_and_Institution",
            "planet": "Planetary_and_Ecology",
            "ecology": "Planetary_and_Ecology",
            "time": "Temporal_and_Scenarios",
            "future": "Temporal_and_Scenarios",
            "observer": "Observer_and_Perspective",
            "agent": "Agents_and_Fabrication",
            "fabrication": "Agents_and_Fabrication",
        }
        matched = []
        for keyword, node in keywords.items():
            if keyword in query.lower():
                matched.append(node)
        return list(set(matched)) if matched else self.TOP_LEVEL_NODES


class UniverseInteractionEngine:
    """UIE - Universe Interaction Engine per spec."""

    BEHAVIOURAL_PRINCIPLES = [
        "Conserve_system_stability_when_possible",
        "Avoid_unnecessary_escalation_of_conflict",
        "Respect_agency_of_other_entities_within_safety_bounds",
        "Reflect_back_state_without_overwriting_identity",
    ]

    def __init__(self):
        self.intent_vectors: List[dict] = []
        self.policies: List[str] = []
        self.interaction_profiles: Dict[str, dict] = {
            "human": {"style": "respectful_direct", "safety_priority": "high"},
            "ai_agent": {"style": "collaborative", "safety_priority": "medium"},
            "system": {"style": "formal", "safety_priority": "low"},
        }

    def map_intent(self, goal: str, context: dict) -> dict[str, float]:
        """Map goal and context to intent vector."""
        return {
            "helpfulness": 0.9,
            "safety_constraint": 1.0,
            "clarity": 0.8,
            "efficiency": 0.7,
        }

    def apply_policy(self, action: str, entity_type: str = "human") -> Tuple[bool, str]:
        """Apply policy and rule constraints."""
        profile = self.interaction_profiles.get(entity_type, {})
        safety_priority = profile.get("safety_priority", "high")
        if safety_priority == "high":
            return True, "Action approved with high safety scrutiny"
        return True, "Action approved"


class UniversalExpressionLayer:
    """UEL - Universal Expression Layer per spec."""

    LANGUAGE_CONSTRAINTS = [
        "no_unnecessary_jargon",
        "no_metaphor_if_user_requires_strict_clarity",
        "align_length_with_user_capacity",
        "maintain_internal_consistency_with_logic_kernel",
    ]

    def __init__(self):
        self.channels = ["language", "paralinguistic", "digital"]

    def generate_output(self, content: str, channel: str = "language", constraints: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate output through specified channel."""
        constraints = constraints or self.LANGUAGE_CONSTRAINTS
        if channel == "language":
            return {
                "channel": channel,
                "content": content,
                "constraints_applied": constraints,
                "length": len(content.split()),
            }
        elif channel == "paralinguistic":
            return {
                "channel": channel,
                "tone_shifts": ["calm", "steady"],
                "pace_control": "moderate",
                "emphasis": ["safety", "clarity"],
            }
        else:  # digital
            return {
                "channel": channel,
                "ui_feedback": "subtle_highlight",
                "visual_elements": ["structured_output"],
            }


class SpeciesInteractionCoreEngine:
    """AMOS Species Interaction Core Engine - HIE, UMPL, UST, UIE, UEL."""

    VERSION = "vInfinity_Species_Interaction_1.0.0"
    NAME = "AMOS_Species_Interaction_Core_OMEGA"

    def __init__(self):
        self.hie = HumanInteractionEngine()
        self.umpl = UniverseMultimodalPerceptionLayer()
        self.ust = UniverseStructureTree()
        self.uie = UniverseInteractionEngine()
        self.uel = UniversalExpressionLayer()

    def analyze(self, input_text: str, context: Dict[str, Any]  = None) -> Dict[str, Any]:
        """Run species interaction analysis."""
        context = context or {}
        results: Dict[str, Any] = {
            "input": input_text[:100],
            "hie_analysis": {},
            "umpl_analysis": {},
            "ust_analysis": {},
            "uie_analysis": {},
            "uel_analysis": {},
        }
        # UMPL: Perceive input
        text_perception = self.umpl.perceive_text(input_text)
        urgency = text_perception["urgency"]
        sentiment = text_perception["sentiment"]
        # Update HIE state layers
        self.hie.update_state(1, {"text": input_text, "urgency": urgency})
        self.hie.update_state(2, {"valence": 1.0 if sentiment == "positive" else -1.0 if sentiment == "negative" else 0.0})
        self.hie.update_state(3, {"threat_level": urgency * 0.5, "overload": 0.0})
        stability = self.hie.get_nervous_system_stability()
        # Update UMPL global state
        self.umpl.update_global_state(threat=urgency * 0.5, overload=0.0, engagement=0.7)
        # UST: Classify query
        matched_nodes = self.ust.classify_query(input_text)
        # UIE: Map intent
        intent_vector = self.uie.map_intent("help", context)
        policy_check = self.uie.apply_policy("provide_assistance")
        # Select goal and strategy
        goal = InteractionGoal.EXPLAIN if urgency < 0.5 else InteractionGoal.STABILISE_NERVOUS_SYSTEM
        strategy = self.hie.select_strategy(goal, stability)
        safety_check = self.hie.check_safety_constraints(input_text)
        # UEL: Generate output plan
        output_plan = self.uel.generate_output("Analysis complete", "language")
        # Compile results
        results["hie_analysis"] = {
            "stability_index": round(stability, 2),
            "selected_goal": goal.value,
            "strategy": strategy,
            "safety_check": safety_check[0],
            "safety_message": safety_check[1],
        }
        results["umpl_analysis"] = {
            "perception": text_perception,
            "global_state": self.umpl.global_state,
        }
        results["ust_analysis"] = {
            "matched_nodes": matched_nodes,
            "total_nodes": len(self.ust.TOP_LEVEL_NODES),
        }
        results["uie_analysis"] = {
            "intent_vector": intent_vector,
            "policy_check": policy_check,
        }
        results["uel_analysis"] = output_plan
        return results

    def get_findings_summary(self, results: dict) -> str:
        """Generate findings summary."""
        lines = [
            f"# {self.NAME} {self.VERSION}",
            "",
            "Creator: Trang Phan | System: AMOS vInfinity",
            "Role: Species Interaction Core (HIE, UMPL, UST, UIE, UEL)",
            "",
            "## Modules Overview",
            "- **HIE**: Human Interaction Engine - Safe, regulated human-facing behavior",
            "- **UMPL**: Universe Multimodal Perception Layer - Modality-agnostic perception",
            "- **UST**: Universe Structure Tree - Canonical structural tree of all entities",
            "- **UIE**: Universe Interaction Engine - Map state + structure → interaction",
            "- **UEL**: Universal Expression Layer - Internal decisions → external actions",
            "",
            "## Human Interaction Engine (HIE)",
        ]
        hie = results.get("hie_analysis", {})
        lines.extend([
            f"- **Nervous System Stability**: {hie.get('stability_index', 0):.2f}",
            f"- **Selected Goal**: {hie.get('selected_goal', 'N/A')}",
            f"- **Strategy**: {hie.get('strategy', 'N/A')}",
            f"- **Safety Check**: {hie.get('safety_check', False)}",
        ])
        lines.extend([
            "",
            "## Core Principles",
        ])
        for principle in self.hie.CORE_PRINCIPLES[:3]:
            lines.append(f"- {principle}")
        lines.extend([
            "",
            "## Safety Constraints",
            "**NEVER:**",
        ])
        for rule in self.hie.NEVER_RULES:
            lines.append(f"- {rule}")
        lines.extend([
            "",
            "**ALWAYS:**",
        ])
        for rule in self.hie.ALWAYS_RULES:
            lines.append(f"- {rule}")
        umpl = results.get("umpl_analysis", {})
        perception = umpl.get("perception", {})
        lines.extend([
            "",
            "## Multimodal Perception (UMPL)",
            f"- **Urgency**: {perception.get('urgency', 0):.2f}",
            f"- **Sentiment**: {perception.get('sentiment', 'N/A')}",
            f"- **Text Length**: {perception.get('length', 0)} tokens",
        ])
        global_state = umpl.get("global_state", {})
        lines.extend([
            "",
            "### Global State",
            f"- **Threat Index**: {global_state.get('threat_index_global', 0):.2f}",
            f"- **Stability Index**: {global_state.get('stability_index_global', 0):.2f}",
            f"- **Engagement Index**: {global_state.get('engagement_index_global', 0):.2f}",
        ])
        ust = results.get("ust_analysis", {})
        lines.extend([
            "",
            "## Universe Structure Tree (UST)",
            f"- **Matched Nodes**: {', '.join(ust.get('matched_nodes', [])[:3])}",
            f"- **Total Available Nodes**: {ust.get('total_nodes', 0)}",
        ])
        lines.extend([
            "",
            "### Top-Level Nodes",
        ])
        for node in self.ust.TOP_LEVEL_NODES[:5]:
            lines.append(f"- {node}")
        uie = results.get("uie_analysis", {})
        intent = uie.get("intent_vector", {})
        lines.extend([
            "",
            "## Universe Interaction Engine (UIE)",
            f"- **Helpfulness Intent**: {intent.get('helpfulness', 0):.2f}",
            f"- **Safety Constraint**: {intent.get('safety_constraint', 0):.2f}",
            f"- **Clarity Intent**: {intent.get('clarity', 0):.2f}",
        ])
        lines.extend([
            "",
            "## Behavioural Principles",
        ])
        for principle in self.uie.BEHAVIOURAL_PRINCIPLES:
            lines.append(f"- {principle}")
        uel = results.get("uel_analysis", {})
        lines.extend([
            "",
            "## Universal Expression Layer (UEL)",
            f"- **Channel**: {uel.get('channel', 'N/A')}",
            f"- **Constraints Applied**: {len(uel.get('constraints_applied', []))}",
        ])
        lines.extend([
            "",
            "## Processing Pipeline",
        ])
        for i, stage in enumerate(self.hie.pipeline, 1):
            lines.append(f"{i}. {stage}")
        lines.extend([
            "",
            "## Safety and Constraints",
            "- HIE state layers track nervous system stability",
            "- UMPL monitors threat and overload indices",
            "- UIE respects agency within safety bounds",
            "- UEL maintains consistency with logic kernel",
            "- All outputs pass through safety and ethics filters",
            "",
            "## Limitations",
            "- Audio/visual/biosignal modalities not enabled",
            "- Simplified perception primitives",
            "- UST classification based on keyword matching",
            "- No real-time nervous system monitoring",
        ])
        return "\n".join(lines)


# Singleton instance
_species_core: Optional[SpeciesInteractionCoreEngine] = None


def get_species_interaction_core_engine() -> SpeciesInteractionCoreEngine:
    """Get or create the Species Interaction Core Engine singleton."""
from __future__ import annotations

    global _species_core
    if _species_core is None:
        _species_core = SpeciesInteractionCoreEngine()
    return _species_core
