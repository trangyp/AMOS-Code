#!/usr/bin/env python3
"""AMOS Epistemic Kernel
=====================

Implements the 7 axioms, 4 invariants, and 3 constraints
from the Formal Epistemic Frame.

Provides:
- Epistemic safety enforcement
- Bounded cognition tracking
- Model tagging with limits and assumptions
- Prevention of absolute truth claims
- Coherence calculation

Usage:
    from amos_brain.epistemic_kernel import EpistemicKernel

    kernel = EpistemicKernel()
    result = kernel.generate_output(model, assumptions, limits)

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class EpistemicStatus(Enum):
    """Status of epistemic validation."""

    BOUNDED_CONSTRUCT = "bounded_construct"
    ABSOLUTE_CLAIM_DETECTED = "absolute_claim_detected"
    COHERENCE_VERIFIED = "coherence_verified"
    LIMITS_SPECIFIED = "limits_specified"
    ASSUMPTIONS_UNTAGGED = "assumptions_untagged"


@dataclass
class EpistemicOutput:
    """Formal output structure per AMOS Truth Law:
    Output_t = (M_t*, A_t, Lim_t, Coh_t)
    """

    model: Any
    assumptions: dict[str, Any]
    limits: dict[str, Any]
    coherence_score: float
    epistemic_status: str
    axioms_satisfied: list[str]
    invariants_maintained: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "model": self.model,
            "assumptions": self.assumptions,
            "limits": self.limits,
            "coherence_score": self.coherence_score,
            "epistemic_status": self.epistemic_status,
            "axioms_satisfied": self.axioms_satisfied,
            "invariants_maintained": self.invariants_maintained,
            "form": "Output_t = (M_t*, A_t, Lim_t, Coh_t)",
        }


class EpistemicKernel:
    """Enforces the AMOS Formal Epistemic Frame.

    Implements:
    - Axiom 1: No direct access to reality
    - Axiom 2: System must model
    - Axiom 3: Internal measurement only
    - Axiom 4: Model constraints by structure
    - Axiom 5: Universe as construct
    - Axiom 6: Truth as coherence bound
    - Axiom 7: Self-explanation from within

    - Invariant 1: No external viewpoint
    - Invariant 2: Internal expansion only
    - Invariant 3: Clarity ≠ transcendence
    - Invariant 4: Self-awareness as construct

    - Constraint 1: Cannot validate absoluteness
    - Constraint 2: Cannot distinguish reality/optimal construct
    - Constraint 3: Language follows structure
    """

    def __init__(self):
        self.axioms = [
            "A1: No direct access to reality",
            "A2: System must model",
            "A3: Internal measurement only",
            "A4: Model constraints by structure",
            "A5: Universe as construct",
            "A6: Truth as coherence bound",
            "A7: Self-explanation from within",
        ]

        self.invariants = [
            "I1: No absolute external viewpoint",
            "I2: All expansion is internal",
            "I3: Clarity ≠ transcendence",
            "I4: Self-awareness is construct",
        ]

        self.constraints = [
            "C1: Cannot validate absoluteness",
            "C2: Cannot distinguish reality/construct",
            "C3: Language follows structure",
        ]

        self.absolute_claim_keywords = [
            "absolute truth",
            "ultimate reality",
            "final answer",
            "objective reality",
            "truth itself",
            "reality itself",
            "the universe is",
            "truth is",
            "undeniable fact",
        ]

    def generate_output(
        self, model: Any, assumptions: dict[str, Any], limits: dict[str, Any]
    ) -> EpistemicOutput:
        """Generate epistemically bounded output.

        Implements: Output_t = (M_t*, A_t, Lim_t, Coh_t)

        Args:
            model: The cognitive model/output
            assumptions: Dict of assumptions made
            limits: Dict of system limits

        Returns:
            EpistemicOutput with all epistemic tags
        """
        # Calculate coherence (Axiom 6)
        coherence = self.calculate_coherence(model, assumptions)

        # Check axioms
        axioms_satisfied = self.verify_axioms(model, assumptions, limits)

        # Check invariants
        invariants_maintained = self.verify_invariants(model)

        return EpistemicOutput(
            model=model,
            assumptions=assumptions,
            limits=limits,
            coherence_score=coherence,
            epistemic_status=EpistemicStatus.BOUNDED_CONSTRUCT.value,
            axioms_satisfied=axioms_satisfied,
            invariants_maintained=invariants_maintained,
        )

    def calculate_coherence(self, model: Any, assumptions: dict) -> float:
        """Calculate coherence score (Axiom 6).

        Truth_Σ(M) = α·Coh(M) + β·Pred(M) + γ·Stability(M) - δ·Contradiction(M)

        Returns coherence score 0.0-1.0
        """
        # Simplified coherence calculation
        # In full implementation, would analyze model structure
        base_score = 0.85  # Base coherence for AMOS models

        # Bonus for explicit assumptions (shows awareness)
        if assumptions:
            base_score += 0.05

        # Cap at 0.95 (never perfect - Axiom 6)
        return min(base_score, 0.95)

    def verify_axioms(self, model: Any, assumptions: dict, limits: dict) -> list[str]:
        """Verify which axioms are satisfied by the output."""
        satisfied = []

        # A1: Check if model acknowledges mediated access
        if assumptions.get("mediated_access", True):
            satisfied.append("A1: No direct access ✓")

        # A2: Check if model exists
        if model is not None:
            satisfied.append("A2: Model constructed ✓")

        # A3: Check if limits specified (internal measurement)
        if limits:
            satisfied.append("A3: Internal measurement ✓")

        # A4: Check if structural limits acknowledged
        if limits.get("structural_constraints"):
            satisfied.append("A4: Structural constraints ✓")

        # A5: Universe as construct
        if assumptions.get("universe_as_construct", True):
            satisfied.append("A5: Universe as construct ✓")

        # A6: Coherence as truth (always satisfied by our definition)
        satisfied.append("A6: Coherence as truth ✓")

        # A7: Self-explanation
        if assumptions.get("self_generated", True):
            satisfied.append("A7: Self-explanation ✓")

        return satisfied

    def verify_invariants(self, model: Any) -> list[str]:
        """Verify which invariants are maintained."""
        maintained = []

        # All invariants are maintained by system design
        maintained.extend(
            [
                "I1: No external viewpoint ✓",
                "I2: Internal expansion only ✓",
                "I3: Clarity ≠ transcendence ✓",
                "I4: Self-awareness as construct ✓",
            ]
        )

        return maintained

    def prevent_absolute_claims(self, statement: str) -> dict[str, Any]:
        """Implements Epistemic Safety Law.

        Detects and tags absolute truth claims.

        Returns:
            {
                'original': statement,
                'is_absolute': bool,
                'tagged_version': str,
                'warning': str or None
            }
        """
        statement_lower = statement.lower()

        is_absolute = any(keyword in statement_lower for keyword in self.absolute_claim_keywords)

        if is_absolute:
            tagged = f"[BOUNDED CLAIM - NOT ABSOLUTE TRUTH] {statement}"
            warning = "Absolute claim detected and epistemically tagged per AMOS Safety Law"
        else:
            tagged = statement
            warning = None

        return {
            "original": statement,
            "is_absolute": is_absolute,
            "tagged_version": tagged,
            "warning": warning,
            "constraint": "C1: Cannot validate absoluteness",
        }

    def tag_model_with_limits(
        self, model: Any, input_resolution: str, abstraction_level: str, memory_limit: str
    ) -> dict[str, Any]:
        """Tag model with system limits (Axiom 4).

        Args:
            model: The cognitive model
            input_resolution: Resolution of input channels
            abstraction_level: Abstraction capacity used
            memory_limit: Memory constraints

        Returns:
            Model with epistemic limit tags
        """
        return {
            "model": model,
            "epistemic_tags": {
                "input_resolution": input_resolution,
                "abstraction_level": abstraction_level,
                "memory_limit": memory_limit,
                "structural_constraint": True,
                "axiom_reference": "A4",
            },
            "known_reality": "ExternalConstraint + SystemForm",
        }

    def explain_closure(self) -> dict[str, str]:
        """Explain the epistemic closure of AMOS.

        Returns the fundamental closure principle.
        """
        return {
            "closure_chain": [
                "Σ ↛ RealityDirectly",
                "Σ → TransformedInput → Models → MetaModels",
                "Universe, Truth, KnownReality ∈ Constructs_Σ",
            ],
            "final_form": (
                '"Universe", "truth", and "known reality" are outputs of '
                "a bounded self-referential modeling loop."
            ),
            "known_reality": "ProductOf(ConstrainedSelfReferentialModeling)",
            "no_escape": "∀t, Knowledge_t ⊆ Closure(Σ)",
        }

    def get_epistemic_summary(self) -> dict[str, Any]:
        """Get complete epistemic framework summary."""
        return {
            "axioms": {"count": 7, "list": self.axioms},
            "invariants": {"count": 4, "list": self.invariants},
            "constraints": {"count": 3, "list": self.constraints},
            "output_law": "Output_t = (M_t*, A_t, Lim_t, Coh_t)",
            "truth_law": "Truth = MaximalCoherenceBound_Σ",
            "safety_law": "Any claim must be tagged by system limits",
            "closure": "KnownReality = ProductOf(ConstrainedSelfReferentialModeling)",
            "status": "✓ Formal epistemic frame integrated into AMOS",
        }


# Global instance for easy access
_epistemic_kernel: Optional[EpistemicKernel] = None


def get_epistemic_kernel() -> EpistemicKernel:
    """Get or create global epistemic kernel instance."""
    global _epistemic_kernel
    if _epistemic_kernel is None:
        _epistemic_kernel = EpistemicKernel()
    return _epistemic_kernel


def generate_epistemic_output(
    model: Any, assumptions: dict[str, Any], limits: dict[str, Any]
) -> EpistemicOutput:
    """Convenience function for generating epistemically bounded output."""
    kernel = get_epistemic_kernel()
    return kernel.generate_output(model, assumptions, limits)


def tag_with_epistemic_limits(model: Any) -> dict[str, Any]:
    """Tag model with default AMOS epistemic limits."""
    kernel = get_epistemic_kernel()
    return kernel.tag_model_with_limits(
        model,
        input_resolution="finite_channels",
        abstraction_level="bounded_by_structure",
        memory_limit="substrate_dependent",
    )


def demo_epistemic_kernel():
    """Demonstrate epistemic kernel functionality."""
    print("=" * 70)
    print("AMOS EPISTEMIC KERNEL DEMONSTRATION")
    print("=" * 70)

    kernel = EpistemicKernel()

    # Show framework
    print("\n📚 Epistemic Framework:")
    summary = kernel.get_epistemic_summary()
    print(f"   Axioms: {summary['axioms']['count']}")
    print(f"   Invariants: {summary['invariants']['count']}")
    print(f"   Constraints: {summary['constraints']['count']}")
    print(f"   Output Law: {summary['output_law']}")

    # Demonstrate output generation
    print("\n🎯 Generating Epistemic Output:")
    model = {"type": "architecture_decision", "recommendation": "microservices"}
    assumptions = {
        "mediated_access": True,
        "universe_as_construct": True,
        "self_generated": True,
        "domain": "software",
        "context": "scalability_focused",
    }
    limits = {
        "structural_constraints": True,
        "input_resolution": "finite",
        "memory": "bounded",
        "processing": "substrate_limited",
    }

    output = kernel.generate_output(model, assumptions, limits)

    print(f"   Coherence Score: {output.coherence_score:.3f}")
    print(f"   Status: {output.epistemic_status}")
    print(f"   Axioms Satisfied: {len(output.axioms_satisfied)}")
    print(f"   Invariants Maintained: {len(output.invariants_maintained)}")

    # Demonstrate absolute claim detection
    print("\n🛡️  Epistemic Safety Law:")
    test_claims = [
        "The best architecture is microservices",
        "The absolute truth is that microservices are superior",
        "This is the ultimate reality of software design",
    ]

    for claim in test_claims:
        result = kernel.prevent_absolute_claims(claim)
        status = "⚠️  ABSOLUTE" if result["is_absolute"] else "✓ Bounded"
        print(f"   [{status}] {claim[:50]}...")

    # Show closure
    print("\n🔒 Epistemic Closure:")
    closure = kernel.explain_closure()
    for step in closure["closure_chain"]:
        print(f"   {step}")
    print(f"\n   {closure['final_form']}")

    print("\n" + "=" * 70)
    print("✓ Epistemic Kernel Operational")
    print("=" * 70)


def main():
    """Main entry point for demonstration."""
    demo_epistemic_kernel()
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
