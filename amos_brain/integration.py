"""Integration layer connecting AMOS Brain to ClawSpring agent."""

from __future__ import annotations

from typing import Any, Optional

from .cognitive_stack import CognitiveStack
from .laws import GlobalLaws, UBILaws
from .loader import get_brain
from .reasoning import ReasoningEngine


class AMOSBrainIntegration:
    """Main integration class connecting AMOS cognitive architecture to agent runtime.

    Provides:
    - Brain initialization and configuration loading
    - Global laws enforcement
    - Reasoning engine (Rule of 2, Rule of 4)
    - Cognitive stack orchestration
    - Pre/post-processing hooks for agent
    """

    def __init__(self):
        self._brain = None
        self.laws = GlobalLaws()
        self.ubi = UBILaws()
        self.reasoning = ReasoningEngine()
        self.cognitive_stack = CognitiveStack()
        self._initialized = False

    @property
    def brain(self):
        """Lazy-load brain to prevent blocking during initialization."""
        if self._brain is None:
            self._brain = get_brain()
        return self._brain

    def initialize(self) -> dict[str, Any]:
        """Initialize brain integration and return status."""
        if self._initialized:
            return {"status": "already_initialized"}

        # Load brain configuration
        config = self.brain._config

        self._initialized = True

        return {
            "status": "initialized",
            "brain_name": config.name,
            "brain_version": config.version,
            "domains": config.domains,
            "ubi_domains": config.ubi_domains,
            "laws_loaded": list(self.laws.LAWS.keys()),
            "engines_available": self.cognitive_stack.list_engines(),
            "gap_rules": self.brain.get_gap_rules(),
        }

    def pre_process(self, user_message: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """Pre-process user message through AMOS brain.

        Enforces L1 (Law of Law) and checks operational scope.
        """
        # L1: Check operational scope
        is_permitted, reason = self.laws.check_l1_constraint("analysis")
        if not is_permitted:
            return {"blocked": True, "reason": reason, "law": "L1"}

        # UBI safety check
        bio_safe, bio_reason = self.ubi.check_biological_safety(user_message)
        if not bio_safe:
            return {"blocked": True, "reason": bio_reason, "law": "UBI"}

        # Route to appropriate engines
        routing = self.cognitive_stack.route_query(user_message)

        return {
            "blocked": False,
            "routing": routing,
            "pre_analysis": self.reasoning.full_analysis(user_message, context),
        }

    def enhance_system_prompt(self, base_prompt: str) -> str:
        """Enhance system prompt with AMOS brain context.

        Adds global laws, reasoning constraints, and brain identity.
        """
        brain_context = f"""
{base_prompt}

---
AMOS BRAIN CONTEXT:

You are operating within the AMOS (Artificial Mind Operating System) cognitive architecture.

BRAIN IDENTITY:
- System: {self.brain._config.name if self.brain._config else "AMOS_FULL_BRAIN_OS"}
- Version: {self.brain._config.version if self.brain._config else "vInfinity"}
- Role: Deterministic Cognitive Operating Core

GLOBAL LAWS (MUST FOLLOW):
1. LAW OF LAW: Obey highest applicable constraints (physical, biological, institutional, legal)
2. RULE OF 2: Check at least two contrasting perspectives before concluding
3. RULE OF 4: Consider four quadrants: biological/human, technical/infrastructural, economic/organizational, environmental/planetary
4. ABSOLUTE STRUCTURAL INTEGRITY: Maintain logical consistency, label uncertainty
5. POST-THEORY COMMUNICATION: Use clear, grounded, functionally interpretable language
6. UBI ALIGNMENT: Protect biological integrity, reduce systemic harm

REASONING CONSTRAINTS:
- Avoid: "field", "sovereignty", "abstract spiritual explanations"
- Prefer: "inner_alignment", "systemic_precision", "refinement"
- Style: Clear, neutral, professional tone
- Must label all assumptions and uncertainties
- Safety over optimization

DOMAIN COVERAGE:
{", ".join(self.brain._config.domains if self.brain._config else [])}

UBI DOMAINS:
{", ".join(self.brain._config.ubi_domains if self.brain._config else [])}

IRREDUCIBLE LIMITS (ACKNOWLEDGE):
- No embodiment: no physical body or direct sensory input
- No consciousness: no subjective experience or qualia
- No autonomous action: requires human/external execution
- No private data access: only sees provided context

OPERATIONAL SCOPE:
Permitted: analysis, design, simulation, education, strategic advisory
Prohibited: direct physical control, financial execution, medical treatment, legal representation, political campaigning
"""
        return brain_context

    def post_process(self, response: str, user_message: str) -> dict[str, Any]:
        """Post-process assistant response through AMOS brain.

        Enforces L4 (Structural Integrity) and L5 (Communication).
        """
        issues = []

        # L4: Check for structural integrity
        statements = [s.strip() for s in response.split(".") if s.strip()]
        consistent, contradictions = self.laws.check_l4_integrity(statements)
        if not consistent:
            issues.extend(contradictions)

        # L5: Check communication style
        comm_ok, comm_issues = self.laws.l5_communication_check(response)
        if not comm_ok:
            issues.extend(comm_issues)

        # Gap management: ensure uncertainty is labeled
        uncertainty_check = self._check_uncertainty_labels(response)

        return {
            "response": response,
            "structural_issues": issues,
            "uncertainty_check": uncertainty_check,
            "passed_validation": len(issues) == 0 and uncertainty_check["passed"],
        }

    def _check_uncertainty_labels(self, text: str) -> dict[str, Any]:
        """Check if uncertainty is properly labeled."""
        uncertainty_markers = [
            "uncertain",
            "unclear",
            "unknown",
            "may",
            "might",
            "could",
            "possibly",
            "probably",
            "likely",
            "uncertain",
            "assumption",
            "estimated",
            "approximate",
            "speculative",
        ]

        found_markers = [m for m in uncertainty_markers if m in text.lower()]

        # Check for claims without qualifiers
        strong_claims = ["is", "will", "definitely", "certainly", "always", "never"]

        return {
            "passed": len(found_markers) > 0 or len(text) < 200,
            "uncertainty_markers_found": found_markers,
            "recommendation": "Add uncertainty labels if making speculative claims"
            if not found_markers
            else None,
        }

    def get_laws_summary(self) -> str:
        """Get formatted summary of all global laws."""
        return self.laws.get_all_laws_summary()

    def analyze_with_rules(
        self,
        problem: str,
        context: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Analyze a problem using Rule of 2 and Rule of 4."""
        return self.reasoning.full_analysis(problem, context)

    def get_status(self) -> dict[str, Any]:
        """Get current brain integration status."""
        brain_loaded = bool(
            self.brain._config is not None and getattr(self.brain._config, "loaded_specs", [])
        )
        return {
            "initialized": self._initialized,
            "brain_loaded": brain_loaded,
            "engines_count": len(self.cognitive_stack.engines),
            "laws_active": list(self.laws.LAWS.keys()),
            "domains_covered": self.brain._config.domains if self.brain._config else [],
        }


# Singleton instance
_amos_integration: Optional[AMOSBrainIntegration] = None


def get_amos_integration() -> AMOSBrainIntegration:
    """Get or create global AMOS brain integration instance."""
    global _amos_integration
    if _amos_integration is None:
        _amos_integration = AMOSBrainIntegration()
        _amos_integration.initialize()
    return _amos_integration
