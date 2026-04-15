"""AMOS Design Engine - UI/UX production with biological constraints."""

from __future__ import annotations

from dataclasses import dataclass, field

from amos_execution import get_execution_kernel

from amos_runtime import get_runtime


@dataclass
class DesignSpec:
    """Specification for design generation."""

    component_type: str
    purpose: str
    user_segments: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    accessibility_required: bool = True


@dataclass
class DesignResult:
    """Result of design generation with AMOS compliance."""

    component_type: str
    design_system: dict
    interaction_flow: list[dict]
    copy_blocks: dict[str, str]
    accessibility_notes: list[str]
    assumptions: list[str]
    gap_acknowledgment: str
    biological_constraints: list[str] = field(default_factory=list)


class InformationArchitectureKernel:
    """Navigation, hierarchy, chunking primitives."""

    def apply(self, spec: DesignSpec) -> dict:
        """Apply IA kernel to generate structure."""
        return {
            "nodes": [
                {"id": "main", "label": spec.purpose, "priority": 1},
                {"id": "secondary", "label": "Support actions", "priority": 2},
            ],
            "links": [{"from": "main", "to": "secondary", "type": "flow"}],
            "navigation_pattern": "hierarchical",
            "chunking_strategy": "by_user_intent",
        }


class VisualSemanticsKernel:
    """Layout, contrast, grouping primitives."""

    def apply(self, spec: DesignSpec) -> dict:
        """Apply visual semantics kernel."""
        return {
            "grid_system": "8px_base",
            "alignment": "left_aligned_content",
            "visual_weight": {
                "primary_action": "high_contrast_button",
                "secondary": "ghost_button",
                "content": "readable_text",
            },
            "grouping": "proximity_by_function",
            "contrast_ratios": {
                "primary": "4.5:1",
                "large_text": "3:1",
            },
        }


class LanguageClarityKernel:
    """Terminology, sentence structures, tone."""

    def apply(self, spec: DesignSpec) -> dict:
        """Apply language clarity kernel."""
        return {
            "terminology": {
                "primary_action": self._get_action_label(spec.component_type),
                "confirmation": "Confirm",
                "cancel": "Cancel",
            },
            "tone": "neutral_helpful",
            "sentence_structure": "imperative_for_actions",
            "register": "professional_accessible",
        }

    def _get_action_label(self, component_type: str) -> str:
        """Get appropriate action label."""
        labels = {
            "form": "Submit",
            "dialog": "Continue",
            "navigation": "Go",
            "card": "View",
        }
        return labels.get(component_type, "Action")


class AccessibilityKernel:
    """a11y, multi-modal, inclusive design."""

    def apply(self, spec: DesignSpec) -> dict:
        """Apply accessibility kernel."""
        if not spec.accessibility_required:
            return {"notes": ["Accessibility not required for this component"]}

        return {
            "aria_roles": ["button", "heading", "region"],
            "keyboard_navigation": "tab_order_logical",
            "screen_reader_support": {
                "announcements": "state_changes",
                "labels": "descriptive_not_visual",
            },
            "assistive_paths": [
                "keyboard_only_navigation",
                "screen_reader_optimized",
                "high_contrast_mode",
            ],
            "wcag_level": "AA",
        }


class AMOSDesignEngine:
    """Unified design engine with 4 kernels following AMOS brain spec."""

    def __init__(self):
        self.runtime = get_runtime()
        self.execution = get_execution_kernel()
        self.ia_kernel = InformationArchitectureKernel()
        self.visual_kernel = VisualSemanticsKernel()
        self.language_kernel = LanguageClarityKernel()
        self.a11y_kernel = AccessibilityKernel()

    def generate_design(self, spec: DesignSpec) -> DesignResult:
        """Generate complete design using all 4 kernels."""
        # Apply all kernels
        ia = self.ia_kernel.apply(spec)
        visual = self.visual_kernel.apply(spec)
        language = self.language_kernel.apply(spec)
        a11y = self.a11y_kernel.apply(spec)

        # Build design system
        design_system = {
            "structure": ia,
            "visual": visual,
            "language": language,
            "accessibility": a11y,
        }

        # Generate interaction flow
        interaction_flow = self._build_interaction_flow(spec, ia)

        # Generate copy blocks
        copy_blocks = self._generate_copy(language, spec)

        # Accessibility notes
        a11y_notes = self._build_a11y_notes(a11y)

        # Biological constraints (UBI alignment)
        bio_constraints = self._get_biological_constraints(spec)

        return DesignResult(
            component_type=spec.component_type,
            design_system=design_system,
            interaction_flow=interaction_flow,
            copy_blocks=copy_blocks,
            accessibility_notes=a11y_notes,
            assumptions=[
                "User has functional vision or screen reader",
                "User can interact with standard input devices",
                "Cognitive load should be minimized",
            ],
            gap_acknowledgment=(
                "GAP: This design is a structural model without user testing, "
                "biometric validation, or real-world usability data. "
                "Human review and testing required."
            ),
            biological_constraints=bio_constraints,
        )

    def _build_interaction_flow(self, spec: DesignSpec, ia: dict) -> list[dict]:
        """Build interaction flow from IA."""
        return [
            {
                "step": 1,
                "action": f"User encounters {spec.component_type}",
                "system_response": "Display primary content",
            },
            {
                "step": 2,
                "action": "User processes information",
                "system_response": "Maintain visual hierarchy",
                "biological_note": "Respect human attention span (~20s max)",
            },
            {
                "step": 3,
                "action": "User takes action",
                "system_response": "Provide clear feedback",
                "biological_note": "Avoid cognitive overload - max 7 options",
            },
        ]

    def _generate_copy(self, language: dict, spec: DesignSpec) -> dict[str, str]:
        """Generate copy blocks from language kernel."""
        terms = language.get("terminology", {})
        return {
            "title": spec.purpose,
            "primary_action": terms.get("primary_action", "Submit"),
            "confirmation": f"{terms.get('confirmation', 'Confirm')} {spec.purpose}?",
            "help_text": f"This {spec.component_type} helps you complete {spec.purpose}.",
            "error": f"Unable to complete {spec.purpose}. Please try again.",
        }

    def _build_a11y_notes(self, a11y: dict) -> list[str]:
        """Build accessibility implementation notes."""
        notes = [
            "Ensure 4.5:1 contrast ratio for all text",
            "Provide keyboard-only navigation path",
            "Add ARIA labels for dynamic content",
        ]
        if "assistive_paths" in a11y:
            notes.extend([f"Support: {path}" for path in a11y["assistive_paths"]])
        return notes

    def _get_biological_constraints(self, spec: DesignSpec) -> list[str]:
        """Get biological constraints per UBI alignment (L6)."""
        return [
            "L6 - UBI Alignment: Design respects human nervous system limits",
            "Attention span: Minimize steps, show progress",
            "Cognitive load: Chunk information (Miller's Law - 7±2 items)",
            "Motor control: Touch targets minimum 44x44px",
            "Visual system: Adequate contrast, readable fonts (16px min)",
            "Memory limits: Don't require recall, provide recognition",
        ]

    def design_component(
        self,
        component_type: str,
        purpose: str,
        user_segments: list[str] | None = None,
        accessibility: bool = True,
    ) -> DesignResult:
        """Quick design generation."""
        spec = DesignSpec(
            component_type=component_type,
            purpose=purpose,
            user_segments=user_segments or ["general"],
            accessibility_required=accessibility,
        )
        return self.generate_design(spec)

    def get_engine_status(self) -> dict:
        """Get design engine status."""
        return {
            "kernels": [
                "InformationArchitecture",
                "VisualSemantics",
                "LanguageClarity",
                "Accessibility",
            ],
            "amos_version": "vInfinity",
            "ubi_aligned": True,
            "creator": "Trang Phan",
        }


# Singleton
_design_engine: AMOSDesignEngine | None = None


def get_design_engine() -> AMOSDesignEngine:
    """Get singleton design engine."""
    global _design_engine
    if _design_engine is None:
        _design_engine = AMOSDesignEngine()
    return _design_engine


def design_amos_component(
    component_type: str,
    purpose: str,
    user_segments: list[str] | None = None,
) -> DesignResult:
    """Quick design generation with AMOS compliance."""
    return get_design_engine().design_component(component_type, purpose, user_segments)


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS DESIGN ENGINE TEST")
    print("=" * 60)

    engine = get_design_engine()

    # Test designs
    test_cases = [
        ("form", "User registration", ["new_users", "mobile"]),
        ("dialog", "Confirm deletion", ["all_users"]),
        ("card", "Product display", ["shoppers", "mobile", "desktop"]),
    ]

    for comp_type, purpose, segments in test_cases:
        print(f"\n{'=' * 40}")
        print(f"Component: {comp_type}")
        print(f"Purpose: {purpose}")
        print("=" * 40)

        result = engine.design_component(comp_type, purpose, segments)

        print("\nDesign System:")
        print(f"  Structure: {result.design_system['structure']['navigation_pattern']}")
        print(f"  Visual: {result.design_system['visual']['grid_system']}")

        print("\nCopy Blocks:")
        for key, text in result.copy_blocks.items():
            print(f"  {key}: '{text}'")

        print("\nBiological Constraints:")
        for constraint in result.biological_constraints[:3]:
            print(f"  {constraint}")

        print(f"\nGap: {result.gap_acknowledgment[:60]}...")

    print("\n" + "=" * 60)
    print("Design Engine: OPERATIONAL")
    print("=" * 60)
