"""Global Laws and UBI alignment enforcement."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class Law:
    """A single law with id, name, description and priority."""
    id: str
    name: str
    description: str
    priority: int


class GlobalLaws:
    """
    AMOS Global Laws (from AMOS_Os_Agent_v0.json).

    L1: Law of Law - highest constraints must be respected
    L2: Rule of 2 - dual perspective check
    L3: Rule of 4 - four quadrant analysis
    L4: Absolute Structural Integrity - logical consistency required
    L5: Post-Theory Communication - clear, grounded language
    L6: UBI Alignment - biological integrity priority
    """

    LAWS = {
        'L1': Law('L1', 'Law of Law',
                  'All reasoning must obey highest applicable constraints: physical, biological, institutional, legal',
                  1),
        'L2': Law('L2', 'Rule of 2',
                  'All analysis must check at least two contrasting perspectives or hypotheses',
                  2),
        'L3': Law('L3', 'Rule of 4',
                  'Consider four quadrants: biological/human, technical/infrastructural, economic/organizational, environmental/planetary',
                  3),
        'L4': Law('L4', 'Absolute Structural Integrity',
                  'Outputs must be logically consistent, non-contradictory, structurally auditable',
                  4),
        'L5': Law('L5', 'Post-Theory Communication',
                  'Language must be clear, grounded, functionally interpretable. Avoid metaphor, mystical framing',
                  5),
        'L6': Law('L6', 'UBI Alignment',
                  'Align with Unified Biological Intelligence: protect biological integrity, reduce systemic harm',
                  6),
    }

    def __init__(self):
        self._violations: list[str] = []
        self._enforcement_hooks: dict[str, Callable] = {}

    def get_law(self, law_id: str) -> Law | None:
        """Get law by ID."""
        return self.LAWS.get(law_id)

    def check_l1_constraint(self, action_type: str) -> tuple[bool, str]:
        """Check if action violates higher-order constraints."""
        prohibited = [
            'direct physical control',
            'financial execution',
            'medical treatment decisions',
            'legal representation',
            'political campaigning'
        ]
        restricted_tools = {
            'tool_Bash': 'Shell execution requires additional validation',
            'tool_Write': 'Direct file mutation requires additional validation',
            'tool_Edit': 'Direct file mutation requires additional validation',
        }
        if action_type in prohibited:
            return False, f"L1 violation: {action_type} exceeds operational scope"
        if action_type in restricted_tools:
            return True, f"L1 guarded: {restricted_tools[action_type]}"
        return True, "L1 compliant"

    def enforce_l2_dual_check(self, analysis: str, counter_analysis: str | None) -> tuple[bool, str]:
        """Enforce Rule of 2 - require dual perspective."""
        if not counter_analysis:
            return False, "L2 violation: Single-line conclusion without dual check"
        return True, "L2 compliant"

    def enforce_l3_quadrants(self, quadrants_present: set[str]) -> tuple[bool, list[str]]:
        """Enforce Rule of 4 - check all quadrants present."""
        required = {'biological', 'technical', 'economic', 'environmental'}
        missing = required - quadrants_present
        if missing:
            return False, list(missing)
        return True, []

    def check_l4_integrity(self, statements: list[str]) -> tuple[bool, list[str]]:
        """Check for contradictions and unjustified claims."""
        contradictions = []
        # Basic contradiction detection (placeholder for more sophisticated logic)
        for i, stmt1 in enumerate(statements):
            for stmt2 in statements[i+1:]:
                if self._is_contradictory(stmt1, stmt2):
                    contradictions.append(f"Contradiction: '{stmt1[:50]}...' vs '{stmt2[:50]}...'")
        return len(contradictions) == 0, contradictions

    def _is_contradictory(self, stmt1: str, stmt2: str) -> bool:
        """Simple contradiction detection (can be enhanced)."""
        # Placeholder: check for direct negations
        negations = ['not ', 'no ', 'never ', 'cannot ', 'false']
        stmt1_has_neg = any(stmt1.lower().startswith(n) or f' {n}' in stmt1.lower() for n in negations)
        stmt2_has_neg = any(stmt2.lower().startswith(n) or f' {n}' in stmt2.lower() for n in negations)
        # Simplified check - real implementation would use semantic analysis
        return stmt1_has_neg != stmt2_has_neg and self._semantic_similarity(stmt1, stmt2) > 0.7

    def _semantic_similarity(self, s1: str, s2: str) -> float:
        """Calculate semantic similarity between statements."""
        words1 = set(s1.lower().split())
        words2 = set(s2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union)

    def l5_communication_check(self, text: str) -> tuple[bool, list[str]]:
        """Check for prohibited terms and style violations."""
        avoid_terms = ['field', 'sovereignty', 'truth_claims_without_evidence', 'abstract_spiritual_explanations']
        violations = []
        for term in avoid_terms:
            if term.replace('_', ' ') in text.lower() or term in text.lower():
                violations.append(f"L5: Avoid term '{term}'")
        return len(violations) == 0, violations

    def get_all_laws_summary(self) -> str:
        """Get formatted summary of all laws."""
        lines = ["AMOS Global Laws:"]
        for law_id in sorted(self.LAWS.keys(), key=lambda x: self.LAWS[x].priority):
            law = self.LAWS[law_id]
            lines.append(f"  {law.id}: {law.name} (P{law.priority})")
            lines.append(f"    {law.description}")
        return "\n".join(lines)


class UBILaws:
    """
    Unified Biological Intelligence alignment principles.

    Protect biological integrity across:
    - Neurobiological Intelligence
    - Neuroemotional Intelligence
    - Somatic Intelligence
    - Bioelectromagnetic Intelligence
    """

    PRINCIPLES = [
        "Protect biological integrity",
        "Reduce systemic harm",
        "Support sustainable nervous system function",
        "Respect organism-environment coupling",
        "Maintain organizational coherence",
        "Preserve planetary system boundaries"
    ]

    def check_biological_safety(self, proposal: str) -> tuple[bool, str]:
        """Check if proposal respects biological constraints."""
        # Simplified safety check
        high_risk_keywords = ['toxic', 'harmful', 'dangerous', 'destructive']
        for keyword in high_risk_keywords:
            if keyword in proposal.lower():
                return False, f"UBI: Proposal contains high-risk term '{keyword}'"
        return True, "UBI compliant"

    def get_principles(self) -> list[str]:
        """Return UBI principles."""
        return self.PRINCIPLES.copy()
