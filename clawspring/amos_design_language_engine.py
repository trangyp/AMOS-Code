"""AMOS Design Language Engine - UX, information architecture, and visual design."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DesignDomain(Enum):
    """Design domain classifications."""

    UX = "ux"
    VISUAL = "visual"
    CONTENT = "content"
    ACCESSIBILITY = "accessibility"


@dataclass
class DesignElement:
    """Design element representation."""

    name: str
    element_type: str
    domain: DesignDomain
    properties: dict = field(default_factory=dict)


class InformationArchitectureKernel:
    """Kernel for information architecture and navigation."""

    def __init__(self):
        self.navigations: list[dict] = []
        self.hierarchies: list[dict] = []
        self.content_chunks: list[dict] = []

    def define_navigation(
        self,
        name: str,
        structure: str,
        depth: int,
    ) -> dict:
        """Define navigation structure."""
        nav = {
            "name": name,
            "structure": structure,
            "depth": depth,
            "nodes": [],
        }
        self.navigations.append(nav)
        return nav

    def define_hierarchy(
        self,
        name: str,
        levels: list[str],
    ) -> dict:
        """Define content hierarchy."""
        hierarchy = {
            "name": name,
            "levels": levels,
        }
        self.hierarchies.append(hierarchy)
        return hierarchy

    def chunk_content(
        self,
        content_id: str,
        chunks: list[str],
        max_chunk_size: int = 7,
    ) -> dict:
        """Apply content chunking (Miller's Law: 7±2)."""
        # Apply Miller's Law: optimal chunk size 5-9 items
        valid = all(len(c.split()) <= max_chunk_size for c in chunks)

        chunked = {
            "content_id": content_id,
            "chunks": chunks,
            "count": len(chunks),
            "max_chunk_size": max_chunk_size,
            "miller_compliant": valid,
        }
        self.content_chunks.append(chunked)
        return chunked

    def _get_principles(self) -> list[str]:
        """Return kernel principles."""
        return [
            "Navigation: Clear paths, logical flow",
            "Hierarchy: Logical grouping, progressive disclosure",
            "Chunking: Miller's Law (7±2 items)",
            "Wayfinding: Clear location indicators",
        ]


class VisualSemanticsKernel:
    """Kernel for visual design and layout."""

    def __init__(self):
        self.layouts: list[dict] = []
        self.visual_groups: list[dict] = []

    def define_layout(
        self,
        name: str,
        grid_type: str,
        columns: int,
        gutters: int,
    ) -> dict:
        """Define layout grid system."""
        layout = {
            "name": name,
            "grid": grid_type,
            "columns": columns,
            "gutters": gutters,
        }
        self.layouts.append(layout)
        return layout

    def apply_contrast(
        self,
        element_id: str,
        contrast_ratio: float,
        type: str = "color",
    ) -> dict:
        """Apply visual contrast."""
        # WCAG AA requires 4.5:1 for normal text
        wcag_aa = contrast_ratio >= 4.5
        wcag_aaa = contrast_ratio >= 7.0

        return {
            "element": element_id,
            "contrast_ratio": contrast_ratio,
            "type": type,
            "wcag_aa": wcag_aa,
            "wcag_aaa": wcag_aaa,
        }

    def create_visual_group(
        self,
        name: str,
        elements: list[str],
        proximity: str = "close",
    ) -> dict:
        """Create visual grouping via proximity."""
        group = {
            "name": name,
            "elements": elements,
            "proximity": proximity,
            "gestalt": "Proximity principle applied",
        }
        self.visual_groups.append(group)
        return group

    def _get_principles(self) -> list[str]:
        """Return kernel principles."""
        return [
            "Grid systems for alignment",
            "Visual hierarchy through contrast",
            "Gestalt principles: proximity, similarity",
            "Visual weight and balance",
        ]


class LanguageClarityKernel:
    """Kernel for content clarity and tone."""

    def __init__(self):
        self.terminology: dict[str, str] = {}
        self.content_items: list[dict] = []

    def define_term(
        self,
        term: str,
        definition: str,
        context: str = None,
    ) -> dict:
        """Define terminology."""
        self.terminology[term] = definition
        return {
            "term": term,
            "definition": definition,
            "context": context,
        }

    def analyze_clarity(
        self,
        text: str,
    ) -> dict:
        """Analyze text clarity."""
        words = text.split()
        sentences = text.split(".")

        # Simple metrics
        avg_words_per_sentence = len(words) / max(len(sentences), 1)
        long_words = [w for w in words if len(w) > 6]

        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_words_per_sentence": round(avg_words_per_sentence, 1),
            "long_words": len(long_words),
            "clarity_score": "good" if avg_words_per_sentence < 20 else "review",
        }

    def set_tone(
        self,
        content_id: str,
        tone: str,
        audience: str,
    ) -> dict:
        """Set content tone for audience."""
        return {
            "content": content_id,
            "tone": tone,
            "audience": audience,
            "register": self._map_register(tone, audience),
        }

    def _map_register(self, tone: str, audience: str) -> str:
        """Map tone and audience to register."""
        if tone == "formal" and audience == "expert":
            return "technical"
        elif tone == "friendly" and audience == "general":
            return "plain_language"
        return "neutral"

    def _get_principles(self) -> list[str]:
        """Return kernel principles."""
        return [
            "Plain language over jargon",
            "Consistent terminology",
            "Appropriate tone for audience",
            "Active voice preferred",
        ]


class AccessibilityKernel:
    """Kernel for accessibility and inclusive design."""

    def __init__(self):
        self.a11y_checks: list[dict] = []

    def check_contrast(
        self,
        foreground: str,
        background: str,
        ratio: float,
        text_size: str = "normal",
    ) -> dict:
        """Check color contrast for WCAG compliance."""
        # WCAG thresholds
        if text_size == "large":
            aa_threshold = 3.0
            aaa_threshold = 4.5
        else:
            aa_threshold = 4.5
            aaa_threshold = 7.0

        return {
            "foreground": foreground,
            "background": background,
            "ratio": ratio,
            "wcag_aa": ratio >= aa_threshold,
            "wcag_aaa": ratio >= aaa_threshold,
        }

    def define_aria_role(
        self,
        element_id: str,
        role: str,
        properties: list[str | None] = None,
    ) -> dict:
        """Define ARIA role for accessibility."""
        return {
            "element": element_id,
            "role": role,
            "aria_properties": properties or [],
            "screen_reader": f"Announced as: {role}",
        }

    def check_multimodal(
        self,
        content_id: str,
        has_visual: bool,
        has_audio: bool,
        has_text: bool,
    ) -> dict:
        """Check multimodal accessibility."""
        redundant = sum([has_visual, has_audio, has_text]) >= 2

        return {
            "content": content_id,
            "visual": has_visual,
            "audio": has_audio,
            "text": has_text,
            "redundant_encoding": redundant,
            "accessible": has_text,  # Text is minimum
        }

    def _get_principles(self) -> list[str]:
        """Return kernel principles."""
        return [
            "Perceivable: Information available to all senses",
            "Operable: Interface works with all inputs",
            "Understandable: Clear and consistent",
            "Robust: Works with assistive tech",
        ]


class DesignLanguageEngine:
    """AMOS Design Language Engine - UX and visual design."""

    VERSION = "vInfinity.1.0.0"
    NAME = "AMOS_C11_Design_Language_MAX"

    def __init__(self):
        self.ia_kernel = InformationArchitectureKernel()
        self.visual_kernel = VisualSemanticsKernel()
        self.language_kernel = LanguageClarityKernel()
        self.a11y_kernel = AccessibilityKernel()

    def analyze(
        self,
        description: str,
        domains: list[str | None] = None,
    ) -> dict[str, Any]:
        """Run design language analysis across specified domains."""
        domains = domains or ["ia", "visual", "language", "accessibility"]
        results: dict[str, Any] = {}

        if "ia" in domains or "information_architecture" in domains:
            results["information_architecture"] = self._analyze_ia(description)

        if "visual" in domains or "visual_semantics" in domains:
            results["visual_semantics"] = self._analyze_visual(description)

        if "language" in domains or "language_clarity" in domains:
            results["language_clarity"] = self._analyze_language(description)

        if "accessibility" in domains or "a11y" in domains:
            results["accessibility"] = self._analyze_accessibility(description)

        return results

    def _analyze_ia(self, description: str) -> dict:
        """Analyze information architecture."""
        return {
            "query": description[:100],
            "navigations": len(self.ia_kernel.navigations),
            "hierarchies": len(self.ia_kernel.hierarchies),
            "chunks": len(self.ia_kernel.content_chunks),
            "principles": self.ia_kernel._get_principles(),
        }

    def _analyze_visual(self, description: str) -> dict:
        """Analyze visual semantics."""
        return {
            "query": description[:100],
            "layouts": len(self.visual_kernel.layouts),
            "visual_groups": len(self.visual_kernel.visual_groups),
            "principles": self.visual_kernel._get_principles(),
        }

    def _analyze_language(self, description: str) -> dict:
        """Analyze language clarity."""
        clarity = self.language_kernel.analyze_clarity(description)
        return {
            "query": description[:100],
            "terminology_defined": len(self.language_kernel.terminology),
            "clarity_analysis": clarity,
            "principles": self.language_kernel._get_principles(),
        }

    def _analyze_accessibility(self, description: str) -> dict:
        """Analyze accessibility."""
        return {
            "query": description[:100],
            "a11y_checks": len(self.a11y_kernel.a11y_checks),
            "principles": self.a11y_kernel._get_principles(),
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
            "information_architecture": "Information Architecture",
            "visual_semantics": "Visual Semantics",
            "language_clarity": "Language Clarity",
            "accessibility": "Accessibility",
        }

        for domain, data in results.items():
            display_name = domain_names.get(domain, domain.title())
            lines.extend(
                [
                    "",
                    f"### {display_name}",
                ]
            )
            if isinstance(data, dict):
                for key, value in data.items():
                    if key not in ["principles", "query", "clarity_analysis"]:
                        lines.append(f"- {key}: {value}")
                    elif key == "clarity_analysis":
                        lines.append(f"- clarity: {value.get('clarity_score', 'unknown')}")

        lines.extend(
            [
                "",
                "## Safety & Compliance",
                "",
                "### Safety Constraints",
                "- NO manipulative dark patterns",
                "- NO deceptive design practices",
                "- Respect user autonomy",
                "- Cultural sensitivity required",
                "",
                "### Global Law Compliance",
                "- L1 (Structural): Miller's Law (7±2) applied",
                "- L2 (Temporal): Progressive disclosure",
                "- L3 (Semantic): Clear visual language",
                "- L4 (Cognitive): Multi-modal presentation",
                "- L5 (Safety): No manipulative patterns",
                "- L6 (Humility): GAP acknowledgment below",
                "",
                "## Gap Acknowledgment",
                "",
                "**CRITICAL GAP:** This is NOT a design tool. "
                "All outputs are CONCEPTUAL guidelines only.",
                "",
                "Specific Gaps:",
                "- No visual rendering or prototyping",
                "- No actual WCAG automated testing",
                "- No color palette generation",
                "- No real user research data",
                "- No design system implementation",
                "- Pattern-based analysis only, not design software",
                "",
                "### Creator Attribution",
                "This engine was architected by Trang Phan as part of AMOS vInfinity.",
            ]
        )

        return "\n".join(lines)


# Singleton
_design_language_engine: DesignLanguageEngine | None = None


def get_design_language_engine() -> DesignLanguageEngine:
    """Get singleton design language engine instance."""
    global _design_language_engine
    if _design_language_engine is None:
        _design_language_engine = DesignLanguageEngine()
    return _design_language_engine


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS DESIGN LANGUAGE ENGINE")
    print("=" * 60)
    print()

    engine = get_design_language_engine()

    # Add sample design elements
    engine.ia_kernel.define_navigation(
        "main_nav",
        "hierarchical",
        3,
    )

    engine.ia_kernel.chunk_content(
        "features_list",
        ["Feature 1", "Feature 2", "Feature 3", "Feature 4", "Feature 5"],
        max_chunk_size=7,
    )

    engine.visual_kernel.define_layout(
        "dashboard",
        "12-column",
        12,
        24,
    )

    engine.language_kernel.define_term(
        "CTA",
        "Call to Action - element prompting user action",
        "UX design",
    )

    engine.a11y_kernel.check_contrast(
        "#000000",
        "#FFFFFF",
        21.0,
        "normal",
    )

    # Run analysis
    results = engine.analyze(
        "Design a user-friendly dashboard with clear navigation",
        domains=["ia", "visual", "language", "accessibility"],
    )

    # Print findings
    print(engine.get_findings_summary(results))

    print()
    print("=" * 60)
    print("Engine: OPERATIONAL")
    print("=" * 60)
    print("\nCapabilities:")
    print("  - Information Architecture (navigation, hierarchy, chunking)")
    print("  - Visual Semantics (layout, contrast, grouping)")
    print("  - Language Clarity (terminology, tone, readability)")
    print("  - Accessibility (WCAG, ARIA, multi-modal)")
    print()
    print("Safety: NO manipulative patterns, respect user autonomy.")
