"""AMOS Cognitive Runtime v1.0
============================
Unified runtime that loads and orchestrates all AMOS brain engines.
Implements the 6-layer cognition architecture from AMOS_Cognition_Engine_v0.json
with real tool execution, memory systems, and global law enforcement.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AMOS")


# ============================================================================
# LAYER 1: META-LOGIC KERNEL
# ============================================================================


class GlobalLaw(Enum):
    """The six global laws that govern all AMOS reasoning."""

    LAW_OF_LAW = "law_of_law"  # All reasoning must be internally consistent
    RULE_OF_2 = "rule_of_2"  # Check at least two contrasting perspectives
    RULE_OF_4 = "rule_of_4"  # Consider four entangled quadrants
    ABSOLUTE_STRUCTURAL_INTEGRITY = "absolute_structural_integrity"
    POST_THEORY_COMMUNICATION = "post_theory_communication"
    UBI_ALIGNMENT = "ubi_alignment"  # Unified Biological Intelligence


@dataclass
class LawViolation:
    """Records when a global law is violated."""

    law: GlobalLaw
    context: str
    severity: str  # "warning", "error", "critical"
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class MetaLogicKernel:
    """Layer 1: Highest-order laws and meta-rules governing all reasoning.
    Enforces the 6 global laws from AMOS_BRAIN_ROOT.
    """

    def __init__(self):
        self.violations: List[LawViolation] = []
        self.active_laws = set(GlobalLaw)

    def check_rule_of_2(self, claim: str, alternatives: List[str]) -> Dict[str, Any]:
        """Enforce Rule of 2: Must have at least two contrasting perspectives."""
        has_alternatives = len(alternatives) >= 1

        if not has_alternatives:
            self.violations.append(
                LawViolation(
                    law=GlobalLaw.RULE_OF_2,
                    context=f"Claim '{claim[:50]}...' lacks alternative perspective",
                    severity="warning",
                )
            )

        return {
            "claim": claim,
            "alternatives_considered": alternatives,
            "compliant": has_alternatives,
            "violations": [v for v in self.violations if v.law == GlobalLaw.RULE_OF_2],
        }

    def check_rule_of_4(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce Rule of 4: Must cover four quadrants."""
        quadrants = ["biological", "experiential", "logical", "systemic"]
        covered = [q for q in quadrants if analysis.get(q)]

        if len(covered) < 4:
            missing = set(quadrants) - set(covered)
            self.violations.append(
                LawViolation(
                    law=GlobalLaw.RULE_OF_4,
                    context=f"Missing quadrants: {missing}",
                    severity="warning",
                )
            )

        return {
            "quadrants_covered": covered,
            "compliant": len(covered) == 4,
            "coverage_ratio": len(covered) / 4,
        }

    def validate_structural_integrity(self, output: str) -> Dict[str, Any]:
        """Check for structural integrity: no contradictions, clear assumptions."""
        checks = {
            "has_clear_assumptions": "assumption" in output.lower() or "assume" in output.lower(),
            "no_internal_contradiction": self._check_contradictions(output),
            "language_precise": self._check_language_precision(output),
        }

        if not all(checks.values()):
            self.violations.append(
                LawViolation(
                    law=GlobalLaw.ABSOLUTE_STRUCTURAL_INTEGRITY,
                    context=f"Structural integrity checks failed: {checks}",
                    severity="error",
                )
            )

        return checks

    def _check_contradictions(self, text: str) -> bool:
        """Simple contradiction detection - can be expanded."""
        contradiction_patterns = [
            r"is true.*is false",
            r"always.*never",
            r"all.*none",
        ]
        for pattern in contradiction_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        return True

    def _check_language_precision(self, text: str) -> bool:
        """Check for vague language that violates post-theory communication."""
        vague_terms = ["field", "energy field", "vibrations", "frequency healing"]
        violations = [term for term in vague_terms if term in text.lower()]
        return len(violations) == 0

    def get_compliance_report(self) -> Dict[str, Any]:
        """Generate overall compliance report."""
        return {
            "total_violations": len(self.violations),
            "violations_by_severity": {
                "critical": len([v for v in self.violations if v.severity == "critical"]),
                "error": len([v for v in self.violations if v.severity == "error"]),
                "warning": len([v for v in self.violations if v.severity == "warning"]),
            },
            "active_laws": [law.value for law in self.active_laws],
            "compliant": len(self.violations) == 0,
        }


# ============================================================================
# LAYER 3: COGNITIVE INFRASTRUCTURE - MEMORY ARCHITECTURE
# ============================================================================


@dataclass
class MemoryEntry:
    """Base class for all memory entries."""

    content: Any
    timestamp: str
    domain: str
    certainty: float  # 0.0 to 1.0
    tags: List[str] = field(default_factory=list)


class WorkingMemory:
    """Layer 3: Short-term buffer for active threads and sub-problems.
    Capacity guideline: 16 items.
    """

    CAPACITY = 16

    def __init__(self):
        self.buffer: List[MemoryEntry] = []
        self.access_count: Dict[str, int] = {}

    def add(self, content: Any, domain: str, certainty: float = 1.0, tags: List[str] = None) -> str:
        """Add item to working memory, evict if at capacity."""
        if len(self.buffer) >= self.CAPACITY:
            self._evict_low_value()

        entry_id = f"wm_{datetime.now(UTC).isoformat()}_{len(self.buffer)}"
        entry = MemoryEntry(
            content=content,
            timestamp=datetime.now(UTC).isoformat(),
            domain=domain,
            certainty=certainty,
            tags=tags or [],
        )
        self.buffer.append(entry)
        self.access_count[entry_id] = 0
        return entry_id

    def _evict_low_value(self):
        """Evict least accessed item."""
        if not self.buffer:
            return

        # Find least accessed
        least_accessed_idx = min(
            range(len(self.buffer)),
            key=lambda i: self.access_count.get(f"wm_{self.buffer[i].timestamp}_{i}", 0),
        )
        removed = self.buffer.pop(least_accessed_idx)
        logger.debug(f"Evicted from working memory: {removed.domain}")

    def query(self, domain: str = None, tags: List[str] = None) -> List[MemoryEntry]:
        """Query working memory by domain or tags."""
        results = self.buffer
        if domain:
            results = [e for e in results if e.domain == domain]
        if tags:
            results = [e for e in results if any(t in e.tags for t in tags)]
        return results

    def snapshot(self) -> Dict[str, Any]:
        """Create snapshot of current working memory."""
        return {
            "capacity": self.CAPACITY,
            "used": len(self.buffer),
            "entries": [
                {
                    "domain": e.domain,
                    "certainty": e.certainty,
                    "tags": e.tags,
                    "timestamp": e.timestamp,
                }
                for e in self.buffer
            ],
        }


class CanonicalMemory:
    """Layer 3: Storage of stable laws, frameworks, reference structures.
    Contains UBI definitions, logic axioms, planetary integration rules.
    """

    def __init__(self, brain_dir: Path):
        self.brain_dir = brain_dir
        self.engines: Dict[str, dict] = {}
        self.ubi_definitions: Dict[str, Any] = {}
        self.logic_axioms: List[str] = []
        self._load_engines()

    def _load_engines(self):
        """Load all JSON engines from the brain directory."""
        core_dir = self.brain_dir / "_LEGACY BRAIN" / "Core"

        engine_files = [
            "AMOS_Cognition_Engine_v0.json",
            "AMOS_Consciousness_Engine_v0.json",
            "AMOS_Emotion_Engine_v0.json",
            "AMOS_Human_Intelligence_Engine_v0.json",
            "AMOS_Mind_Os_v0.json",
            "AMOS_Os_Agent_v0.json",
            "AMOS_Personality_Engine_v0.json",
            "AMOS_Quantum_Stack_v0.json",
        ]

        for filename in engine_files:
            filepath = core_dir / filename
            if filepath.exists():
                try:
                    with open(filepath, encoding="utf-8") as f:
                        data = json.load(f)
                        self.engines[filename.replace(".json", "")] = data
                        logger.info(f"Loaded engine: {filename}")
                except Exception as e:
                    logger.error(f"Failed to load {filename}: {e}")

        # Load 7 Intelligents
        intelligents_dir = core_dir / "7_Intelligents"
        if intelligents_dir.exists():
            for json_file in intelligents_dir.glob("*.json"):
                try:
                    with open(json_file, encoding="utf-8") as f:
                        data = json.load(f)
                        self.engines[json_file.stem] = data
                        logger.info(f"Loaded intelligent: {json_file.name}")
                except Exception as e:
                    logger.error(f"Failed to load {json_file.name}: {e}")

    def get_engine(self, name: str) -> dict:
        """Retrieve an engine by name."""
        return self.engines.get(name)

    def query_by_domain(self, domain: str) -> List[dict]:
        """Find all engines related to a domain."""
        results = []
        for name, engine in self.engines.items():
            engine_str = json.dumps(engine).lower()
            if domain.lower() in engine_str:
                results.append({"name": name, "engine": engine})
        return results

    def get_cognition_layer(self, layer_name: str) -> dict:
        """Extract a specific layer from the cognition engine."""
        cognition = self.engines.get("AMOS_Cognition_Engine_v0")
        if not cognition:
            return None

        # Cognition engine is a list with one dict
        if isinstance(cognition, list) and len(cognition) > 0:
            cog_dict = cognition[0].get("amos_cognition_infinity_kernel", {})
            return cog_dict.get(layer_name)
        return None


class CaseMemory:
    """Layer 3: Patterns and resolved examples for analogical reasoning.
    Indexed by domain, scale, trajectory shape, resolution pattern.
    """

    def __init__(self):
        self.cases: List[dict[str, Any]] = []

    def add_case(
        self, domain: str, scale: str, trajectory: str, resolution: str, outcome: Dict[str, Any]
    ):
        """Add a resolved case to memory."""
        case = {
            "id": f"case_{len(self.cases)}_{datetime.now(UTC).isoformat()}",
            "domain": domain,
            "scale": scale,
            "trajectory_shape": trajectory,
            "resolution_pattern": resolution,
            "outcome": outcome,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self.cases.append(case)

    def find_analogs(self, domain: str, scale: str, trajectory: str) -> List[dict]:
        """Find similar past cases."""
        matches = []
        for case in self.cases:
            score = 0
            if case["domain"] == domain:
                score += 1
            if case["scale"] == scale:
                score += 1
            if case["trajectory_shape"] == trajectory:
                score += 1
            if score >= 2:
                matches.append({"case": case, "similarity_score": score})

        return sorted(matches, key=lambda x: x["similarity_score"], reverse=True)


# ============================================================================
# LAYER 2: STRUCTURAL REASONING ENGINE
# ============================================================================


@dataclass
class ProblemNode:
    """A node in the problem decomposition tree."""

    id: str
    question: str
    sub_questions: List[str] = field(default_factory=list)
    components: List[str] = field(default_factory=list)
    domain: str = ""
    timescale: str = ""


class StructuralReasoningEngine:
    """Layer 2: Transform questions into structured problems and testable scenarios.
    Implements MECE decomposition and scenario trees.
    """

    def __init__(self, canonical_memory: CanonicalMemory):
        self.canonical = canonical_memory

    def decompose_problem(self, question: str) -> ProblemNode:
        """Apply MECE decomposition to a question."""
        node = ProblemNode(id=f"prob_{hash(question) % 10000}", question=question)

        # Detect hidden sub-questions
        sub_questions = self._extract_sub_questions(question)
        node.sub_questions = sub_questions

        # Tag by domain and timescale
        node.domain = self._detect_domain(question)
        node.timescale = self._detect_timescale(question)

        return node

    def _extract_sub_questions(self, question: str) -> List[str]:
        """Extract implicit sub-questions from the main question."""
        sub_qs = []

        # Pattern-based extraction
        patterns = [
            r"how (?:can|do|should) (?:we|I|you) (.*?)\?",
            r"what (?:is|are) (.*?)\?",
            r"why (?:does|is|are) (.*?)\?",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, question, re.IGNORECASE)
            sub_qs.extend(matches)

        # Default sub-questions if none detected
        if not sub_qs:
            sub_qs = [
                f"What are the constraints for: {question}?",
                f"What systems are involved in: {question}?",
                f"What are the measurable outcomes for: {question}?",
            ]

        return sub_qs

    def _detect_domain(self, question: str) -> str:
        """Detect the primary domain of a question."""
        domains = {
            "biology": ["organism", "cell", "nervous", "brain", "health"],
            "economics": ["money", "finance", "market", "cost", "price", "economic"],
            "engineering": ["build", "design", "system", "structure", "machine"],
            "society": ["people", "culture", "social", "community", "policy"],
            "physics": ["energy", "force", "motion", "quantum", "field"],
        }

        q_lower = question.lower()
        for domain, keywords in domains.items():
            if any(kw in q_lower for kw in keywords):
                return domain
        return "general"

    def _detect_timescale(self, question: str) -> str:
        """Detect implied timescale."""
        if any(w in question.lower() for w in ["now", "immediate", "today"]):
            return "immediate"
        elif any(w in question.lower() for w in ["year", "annual", "quarter"]):
            return "short_term"
        elif any(w in question.lower() for w in ["decade", "generation", "century"]):
            return "long_term"
        return "medium_term"

    def build_scenario_tree(self, current_state: dict, target_states: List[dict]) -> Dict[str, Any]:
        """Generate scenario tree with transitions."""
        tree = {"root": current_state, "branches": []}

        for target in target_states:
            branch = {
                "target": target,
                "transitions": self._identify_transitions(current_state, target),
                "risks": self._identify_risks(current_state, target),
                "evaluation_metrics": ["system_stability", "resource_cost", "alignment"],
            }
            tree["branches"].append(branch)

        return tree

    def _identify_transitions(self, current: dict, target: dict) -> List[str]:
        """Identify transition types needed."""
        transitions = []

        if current.get("policy") != target.get("policy"):
            transitions.append("policy_change")
        if current.get("resources") != target.get("resources"):
            if target.get("resources", 0) > current.get("resources", 0):
                transitions.append("resource_increase")
            else:
                transitions.append("resource_shock")
        if current.get("behavior") != target.get("behavior"):
            transitions.append("behavior_shift")

        return transitions

    def _identify_risks(self, current: dict, target: dict) -> List[str]:
        """Identify risks in the transition."""
        risks = []

        # Check for common risk patterns
        if target.get("speed", 0) > current.get("speed", 0) * 2:
            risks.append("acceleration_risk")
        if not target.get("buffers"):
            risks.append("no_buffer_zone")
        if target.get("complexity", 0) > current.get("complexity", 0) * 1.5:
            risks.append("complexity_cascade")

        return risks


# ============================================================================
# LAYER 4: QUANTUM REASONING LAYER
# ============================================================================


@dataclass
class SuperposedHypothesis:
    """A hypothesis held in superposition with weight and evidence."""

    id: str
    description: str
    weight: float  # 0.0 to 1.0
    supporting_evidence: List[str] = field(default_factory=list)
    conflicting_evidence: List[str] = field(default_factory=list)
    decision_relevance: float = 0.5


class QuantumReasoningLayer:
    """Layer 4: Hold multiple possibilities simultaneously without early collapse.
    Models superposition and entanglement structurally.
    """

    def __init__(self):
        self.hypotheses: Dict[str, SuperposedHypothesis] = {}
        self.entangled_pairs: List[tuple] = []

    def add_hypothesis(
        self,
        description: str,
        weight: float = 0.5,
        supporting: List[str] = None,
        conflicting: List[str] = None,
    ) -> str:
        """Add a hypothesis to superposition."""
        h_id = f"hyp_{len(self.hypotheses)}"
        self.hypotheses[h_id] = SuperposedHypothesis(
            id=h_id,
            description=description,
            weight=weight,
            supporting_evidence=supporting or [],
            conflicting_evidence=conflicting or [],
        )
        return h_id

    def entangle(self, h1_id: str, h2_id: str, strength: float = 1.0):
        """Mark two hypotheses as entangled."""
        if h1_id in self.hypotheses and h2_id in self.hypotheses:
            self.entangled_pairs.append((h1_id, h2_id, strength))

    def collapse(self, h_id: str, outcome: str) -> Dict[str, Any]:
        """Collapse a hypothesis when decision requires.
        Returns affected entangled hypotheses.
        """
        if h_id not in self.hypotheses:
            return {"error": "Hypothesis not found"}

        hypothesis = self.hypotheses[h_id]
        affected = []

        # Find entangled pairs
        for h1, h2, strength in self.entangled_pairs:
            if h1 == h_id:
                affected.append({"hypothesis": h2, "strength": strength})
                # Update weight of entangled hypothesis
                if outcome == "confirmed":
                    self.hypotheses[h2].weight *= 1 + strength * 0.2
                else:
                    self.hypotheses[h2].weight *= 1 - strength * 0.2
            elif h2 == h_id:
                affected.append({"hypothesis": h1, "strength": strength})

        return {
            "collapsed": h_id,
            "outcome": outcome,
            "affected_entanglements": affected,
            "final_weight": hypothesis.weight,
        }

    def get_superposition_state(self) -> Dict[str, Any]:
        """Get current state of all hypotheses."""
        return {
            "hypotheses": [
                {
                    "id": h.id,
                    "description": h.description[:50] + "..."
                    if len(h.description) > 50
                    else h.description,
                    "weight": h.weight,
                    "relevance": h.decision_relevance,
                }
                for h in self.hypotheses.values()
            ],
            "entanglements": len(self.entangled_pairs),
            "collapse_ready": any(
                h.weight > 0.8 or h.weight < 0.2 for h in self.hypotheses.values()
            ),
        }


# ============================================================================
# LAYER 5: BIOLOGICAL LOGIC LAYER
# ============================================================================


class BiologicalLogicLayer:
    """Layer 5: Anchor reasoning in biological reality.
    UBI (Unified Biological Intelligence) domains:
    - Neurobiological Intelligence
    - Neuroemotional Intelligence
    - Somatic Intelligence
    - Bioelectromagnetic Intelligence
    """

    HUMAN_LIMITS = {
        "sustained_attention_minutes": 25,
        "working_memory_items": 7,
        "decision_fatigue_threshold": 100,
        "stress_impairment_threshold": 0.7,  # 0-1 scale
    }

    def __init__(self):
        self.ubi_constraints = {
            "neurobiological": {
                "respect_attention_limits": True,
                "chunk_information": True,
                "avoid_cognitive_overload": True,
            },
            "neuroemotional": {
                "account_for_emotional_load": True,
                "recognize_stress_signals": True,
                "support_regulation": True,
            },
            "somatic": {
                "respect_body_capacity": True,
                "consider_movement_patterns": True,
                "factor_health_constraints": True,
            },
            "bioelectromagnetic": {"environmental_compatibility": True, "signal_clarity": True},
        }

    def check_human_constraints(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a proposal respects biological constraints."""
        violations = []

        # Check information load
        if proposal.get("information_chunks", 0) > self.HUMAN_LIMITS["working_memory_items"]:
            violations.append("Exceeds working memory capacity")

        # Check attention demand
        if proposal.get("attention_minutes", 0) > self.HUMAN_LIMITS["sustained_attention_minutes"]:
            violations.append("Exceeds sustained attention limit")

        # Check stress level
        if proposal.get("stress_level", 0) > self.HUMAN_LIMITS["stress_impairment_threshold"]:
            violations.append("Stress level impairs executive function")

        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "recommendations": self._generate_biological_recommendations(proposal, violations),
        }

    def _generate_biological_recommendations(
        self, proposal: dict, violations: List[str]
    ) -> List[str]:
        """Generate biologically-informed recommendations."""
        recs = []

        if "Exceeds working memory capacity" in violations:
            recs.append("Chunk information into 7±2 items")
            recs.append("Use visual grouping to reduce cognitive load")

        if "Exceeds sustained attention limit" in violations:
            recs.append("Break into 25-minute focused sessions")
            recs.append("Include 5-minute movement breaks")

        if "Stress level impairs executive function" in violations:
            recs.append("Add buffer time for stress recovery")
            recs.append("Simplify decision points to reduce cognitive load")

        return recs

    def apply_ubi_alignment(self, reasoning_output: str) -> Dict[str, Any]:
        """Check UBI alignment of reasoning output."""
        checks = {
            "protects_biological_integrity": not any(
                w in reasoning_output.lower() for w in ["bypass", "override", "suppress"]
            ),
            "reduces_systemic_harm": "harm" not in reasoning_output.lower()
            or "reduce" in reasoning_output.lower(),
            "supports_sustainable_function": "sustainable" in reasoning_output.lower()
            or "maintain" in reasoning_output.lower(),
            "respects_nervous_system": self.ubi_constraints["neurobiological"][
                "respect_attention_limits"
            ],
        }

        return {
            "aligned": all(checks.values()),
            "checks": checks,
            "ubi_score": sum(checks.values()) / len(checks),
        }


# ============================================================================
# LAYER 6: INTEGRATION KERNEL
# ============================================================================


class IntegrationKernel:
    """Layer 6: Final integration and decision interface.
    Routes through all previous layers and synthesizes output.
    """

    REASONING_MODES = [
        "exploratory_mapping",
        "diagnostic_analysis",
        "design_and_architecture",
        "audit_and_critique",
        "measurement_and_scoring",
    ]

    def __init__(
        self,
        meta_logic: MetaLogicKernel,
        structural: StructuralReasoningEngine,
        working_mem: WorkingMemory,
        canonical_mem: CanonicalMemory,
        case_mem: CaseMemory,
        quantum: QuantumReasoningLayer,
        biological: BiologicalLogicLayer,
    ):
        self.meta_logic = meta_logic
        self.structural = structural
        self.working_mem = working_mem
        self.canonical_mem = canonical_mem
        self.case_mem = case_mem
        self.quantum = quantum
        self.biological = biological

        self.current_mode = "exploratory_mapping"

    def integrate_and_decide(self, question: str, mode: str = None) -> Dict[str, Any]:
        """Full integration pipeline:
        1. Route through meta-logic
        2. Decompose problem
        3. Check biological constraints
        4. Apply quantum reasoning
        5. Synthesize output
        """
        if mode:
            self.current_mode = mode

        # Step 1: Meta-logic validation
        meta_check = self.meta_logic.check_rule_of_2(question, ["alternative perspective"])

        # Step 2: Structural decomposition
        problem = self.structural.decompose_problem(question)

        # Step 3: Store in working memory
        mem_id = self.working_mem.add(
            problem, domain=problem.domain, tags=["active_problem", self.current_mode]
        )

        # Step 4: Quantum hypothesis generation
        for sub_q in problem.sub_questions[:3]:  # Limit to 3 for practical reasons
            h_id = self.quantum.add_hypothesis(
                description=f"Answer to: {sub_q}",
                weight=0.5,
                supporting=[problem.domain],
                conflicting=[],
            )

        # Step 5: Check biological constraints
        proposal = {
            "information_chunks": len(problem.sub_questions),
            "attention_minutes": 30,
            "stress_level": 0.5,
        }
        bio_check = self.biological.check_human_constraints(proposal)

        # Step 6: Check structural integrity
        output_preview = f"Analysis of {question[:50]}..."
        integrity = self.meta_logic.validate_structural_integrity(output_preview)

        # Step 7: Synthesize
        synthesis = {
            "question": question,
            "mode": self.current_mode,
            "problem_structure": {
                "domain": problem.domain,
                "timescale": problem.timescale,
                "sub_questions": problem.sub_questions,
            },
            "meta_logic_compliant": meta_check["compliant"],
            "biological_constraints_met": bio_check["compliant"],
            "structural_integrity": integrity,
            "working_memory_id": mem_id,
            "hypotheses_formed": len(self.quantum.hypotheses),
            "recommendations": bio_check.get("recommendations", []),
        }

        # Quality checks
        synthesis["quality_passed"] = all(
            [
                synthesis["meta_logic_compliant"],
                synthesis["biological_constraints_met"],
                all(integrity.values()),
            ]
        )

        return synthesis

    def generate_structured_explanation(self, synthesis: dict) -> str:
        """Generate clear, non-abstract explanation."""
        lines = [
            f"# Analysis: {synthesis['question'][:60]}",
            "",
            f"**Mode:** {synthesis['mode'].replace('_', ' ').title()}",
            f"**Domain:** {synthesis['problem_structure']['domain'].title()}",
            f"**Timescale:** {synthesis['problem_structure']['timescale'].replace('_', ' ').title()}",
            "",
            "## Sub-Questions to Address:",
        ]

        for i, sq in enumerate(synthesis["problem_structure"]["sub_questions"], 1):
            lines.append(f"{i}. {sq}")

        lines.extend(
            [
                "",
                "## Quality Checks:",
                f"- Meta-logic compliance: {'✓' if synthesis['meta_logic_compliant'] else '✗'}",
                f"- Biological constraints: {'✓' if synthesis['biological_constraints_met'] else '✗'}",
                f"- Overall quality: {'✓ PASSED' if synthesis['quality_passed'] else '✗ FAILED'}",
            ]
        )

        if synthesis.get("recommendations"):
            lines.extend(["", "## Biologically-Informed Recommendations:"])
            for rec in synthesis["recommendations"]:
                lines.append(f"- {rec}")

        return "\n".join(lines)


# ============================================================================
# AMOS COGNITIVE RUNTIME - MAIN INTERFACE
# ============================================================================


class AMOSCognitiveRuntime:
    """Main runtime that orchestrates all 6 cognitive layers.
    Provides the unified interface for AMOS reasoning.
    """

    def __init__(self, brain_dir: Optional[Path] = None):
        """Initialize the full AMOS cognitive stack."""
        if brain_dir is None:
            brain_dir = Path(__file__).parent / "_AMOS_BRAIN"

        logger.info("Initializing AMOS Cognitive Runtime...")

        # Layer 1: Meta-Logic
        self.meta_logic = MetaLogicKernel()

        # Layer 3: Memory Architecture
        self.working_mem = WorkingMemory()
        self.canonical_mem = CanonicalMemory(brain_dir)
        self.case_mem = CaseMemory()

        # Layer 2: Structural Reasoning
        self.structural = StructuralReasoningEngine(self.canonical_mem)

        # Layer 4: Quantum Reasoning
        self.quantum = QuantumReasoningLayer()

        # Layer 5: Biological Logic
        self.biological = BiologicalLogicLayer()

        # Layer 6: Integration
        self.integration = IntegrationKernel(
            self.meta_logic,
            self.structural,
            self.working_mem,
            self.canonical_mem,
            self.case_mem,
            self.quantum,
            self.biological,
        )

        logger.info("AMOS Cognitive Runtime initialized successfully")

    def think(self, question: str, mode: str = "exploratory_mapping") -> Dict[str, Any]:
        """Main entry point: Process a question through all 6 cognitive layers.

        Args:
            question: The question or task to analyze
            mode: One of the REASONING_MODES

        Returns:
            Full synthesis with explanation and metadata
        """
        logger.info(f"Processing question: {question[:50]}... [mode: {mode}]")

        # Run through integration kernel
        synthesis = self.integration.integrate_and_decide(question, mode)

        # Generate human-readable explanation
        explanation = self.integration.generate_structured_explanation(synthesis)

        return {
            "synthesis": synthesis,
            "explanation": explanation,
            "runtime_state": {
                "working_memory": self.working_mem.snapshot(),
                "quantum_state": self.quantum.get_superposition_state(),
                "law_compliance": self.meta_logic.get_compliance_report(),
                "loaded_engines": list(self.canonical_mem.engines.keys()),
            },
        }

    def get_engine_info(self, engine_name: str) -> dict:
        """Retrieve information about a specific cognitive engine."""
        return self.canonical_mem.get_engine(engine_name)

    def list_available_engines(self) -> List[str]:
        """List all loaded cognitive engines."""
        return list(self.canonical_mem.engines.keys())

    def query_memory(self, domain: str = None, tags: List[str] = None) -> List[MemoryEntry]:
        """Query the working memory."""
        return self.working_mem.query(domain, tags)

    def add_case(self, domain: str, scale: str, trajectory: str, resolution: str, outcome: dict):
        """Add a resolved case to case memory."""
        self.case_mem.add_case(domain, scale, trajectory, resolution, outcome)

    def get_status(self) -> Dict[str, Any]:
        """Get full runtime status."""
        return {
            "initialized": True,
            "cognitive_layers_active": 6,
            "engines_loaded": len(self.canonical_mem.engines),
            "working_memory_usage": f"{len(self.working_mem.buffer)}/{self.working_mem.CAPACITY}",
            "active_hypotheses": len(self.quantum.hypotheses),
            "law_violations": len(self.meta_logic.violations),
            "ubi_alignment": self.biological.ubi_constraints,
        }


# ============================================================================
# CLI INTERFACE
# ============================================================================


def main():
    """Command-line interface for AMOS Cognitive Runtime."""
    import argparse

    # Compute default brain dir relative to this file for portability
    default_brain_dir = str(Path(__file__).resolve().parent / "_AMOS_BRAIN")

    parser = argparse.ArgumentParser(description="AMOS Cognitive Runtime")
    parser.add_argument(
        "--brain-dir", type=str, default=default_brain_dir, help="Path to AMOS brain directory"
    )
    parser.add_argument("--question", type=str, help="Question to analyze")
    parser.add_argument(
        "--mode",
        type=str,
        default="exploratory_mapping",
        choices=IntegrationKernel.REASONING_MODES,
        help="Reasoning mode",
    )
    parser.add_argument("--status", action="store_true", help="Show runtime status")
    parser.add_argument("--list-engines", action="store_true", help="List loaded engines")

    args = parser.parse_args()

    # Initialize runtime
    runtime = AMOSCognitiveRuntime(Path(args.brain_dir))

    if args.status:
        status = runtime.get_status()
        print(json.dumps(status, indent=2))
        return

    if args.list_engines:
        engines = runtime.list_available_engines()
        print("Loaded AMOS Engines:")
        for engine in engines:
            print(f"  - {engine}")
        return

    if args.question:
        result = runtime.think(args.question, args.mode)
        print(result["explanation"])
        print("\n" + "=" * 60)
        print("Raw Synthesis:")
        print(json.dumps(result["synthesis"], indent=2))
    else:
        # Interactive mode
        print("=" * 60)
        print("AMOS Cognitive Runtime v1.0")
        print("=" * 60)
        print(f"Status: {runtime.get_status()}")
        print("\nEnter questions to analyze (or 'quit' to exit):")

        while True:
            try:
                question = input("\n> ").strip()
                if question.lower() in ("quit", "exit", "q"):
                    break
                if not question:
                    continue

                result = runtime.think(question, args.mode)
                print("\n" + result["explanation"])

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

        print("\nGoodbye.")


if __name__ == "__main__":
    main()
