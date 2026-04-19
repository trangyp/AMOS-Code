"""AMOS Expression Translation - Decodes human expression into structured logic."""

import re
from dataclasses import dataclass


@dataclass
class TranslatedExpression:
    """Result of expression translation."""

    original: str
    structured_logic: str
    detected_domains: list[str]
    emotional_tone: str
    implicit_constraints: list[str]
    suggested_kernels: list[str]


class ExpressionTranslator:
    """Translates human expression into AMOS-compatible structured logic.

    Based on AMOS_EXPRESSION_TRANSLATION_vInfinity specification.
    """

    # Domain detection patterns
    DOMAIN_PATTERNS = {
        "software": [
            r"\b(code|program|function|class|bug|fix|implement|refactor|debug)\b",
            r"\b(python|javascript|typescript|java|cpp|rust|go|rust)\b",
            r"\b(api|endpoint|database|server|client|frontend|backend)\b",
        ],
        "ai_ml": [
            r"\b(model|train|inference|llm|neural|predict|embedding|fine.?tune)\b",
            r"\b(gradient|loss|optimization|dataset|training)\b",
        ],
        "design": [
            r"\b(ui|ux|interface|design|mockup|wireframe|prototype|figma)\b",
            r"\b(user experience|visual|layout|component|style)\b",
        ],
        "architecture": [
            r"\b(architecture|system|infrastructure|scalability|performance)\b",
            r"\b(microservice|monolith|distributed|cloud|aws|azure|gcp)\b",
        ],
        "analysis": [
            r"\b(analyze|research|investigate|understand|explore|study)\b",
            r"\b(data|metric|kpi|analytics|dashboard|report)\b",
        ],
        "ubi": [
            r"\b(biological|nervous|somatic|neuro|health|wellness|body)\b",
            r"\b(stress|sleep|nutrition|exercise|mindfulness|meditation)\b",
        ],
        "business": [
            r"\b(strategy|business|market|customer|revenue|profit|growth)\b",
            r"\b(stakeholder|investor|partner|competitor|industry)\b",
        ],
    }

    # Emotional tone detection
    EMOTION_PATTERNS = {
        "urgent": [r"\b(urgent|asap|immediately|critical|emergency)\b"],
        "frustrated": [r"\b(frustrated|annoyed|angry|pissed|fed up)\b"],
        "uncertain": [r"\b(unsure|confused|unclear|lost|don't understand)\b"],
        "excited": [r"\b(excited|thrilled|amazing|awesome|love)\b"],
        "concerned": [r"\b(worried|concerned|nervous|anxious|afraid)\b"],
        "curious": [r"\b(curious|wondering|interested|learn|know more)\b"],
    }

    # Implicit constraint detection
    CONSTRAINT_PATTERNS = {
        "time_limited": r"\b(by|before|until|deadline)\b.*\d+\s*(day|hour|minute|week)",
        "budget_limited": r"\b(cheap|affordable|budget|cost.?effective|low cost)\b",
        "quality_focused": r"\b(high quality|robust|reliable|production.grade|professional)\b",
        "simple": r"\b(simple|easy|basic|minimal|lightweight|quick)\b",
        "comprehensive": r"\b(comprehensive|complete|thorough|detailed|extensive)\b",
    }

    def translate(self, expression: str) -> TranslatedExpression:
        """Translate human expression into structured logic."""
        # Detect domains
        domains = self._detect_domains(expression)

        # Detect emotional tone
        emotion = self._detect_emotion(expression)

        # Detect implicit constraints
        constraints = self._detect_constraints(expression)

        # Build structured logic representation
        structured = self._build_structured_logic(expression, domains, emotion, constraints)

        # Suggest appropriate kernels
        kernels = self._suggest_kernels(domains, constraints)

        return TranslatedExpression(
            original=expression,
            structured_logic=structured,
            detected_domains=domains,
            emotional_tone=emotion,
            implicit_constraints=constraints,
            suggested_kernels=kernels,
        )

    def _detect_domains(self, text: str) -> list[str]:
        """Detect relevant cognitive domains."""
        text_lower = text.lower()
        detected = []

        for domain, patterns in self.DOMAIN_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    detected.append(domain)
                    break

        return detected if detected else ["general"]

    def _detect_emotion(self, text: str) -> str:
        """Detect emotional tone if present."""
        text_lower = text.lower()

        for emotion, patterns in self.EMOTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return emotion

        return None

    def _detect_constraints(self, text: str) -> list[str]:
        """Detect implicit constraints."""
        text_lower = text.lower()
        constraints = []

        for constraint, pattern in self.CONSTRAINT_PATTERNS.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                constraints.append(constraint)

        return constraints

    def _build_structured_logic(
        self,
        original: str,
        domains: list[str],
        emotion: str,
        constraints: list[str],
    ) -> str:
        """Build structured logic representation."""
        lines = ["# Structured Logic Representation", ""]

        # Core intent
        lines.append(f"Input Intent: {original}")
        lines.append("")

        # Domains
        lines.append(f"Relevant Domains: {', '.join(domains)}")

        # Emotional context (if detected)
        if emotion:
            lines.append(f"Detected Tone: {emotion} (informational only)")

        # Constraints
        if constraints:
            lines.append(f"Implicit Constraints: {', '.join(constraints)}")

        lines.append("")
        lines.append("# Translation Notes")
        lines.append("- Original meaning preserved")
        lines.append("- Ambiguity flagged where present")
        lines.append("- Structural precision prioritized")

        return "\n".join(lines)

    def _suggest_kernels(self, domains: list[str], constraints: list[str]) -> list[str]:
        """Suggest appropriate AMOS kernels."""
        kernel_map = {
            "software": "K_TECH_ENGINE",
            "ai_ml": "K_AI_ML",
            "design": "K_DESIGN",
            "architecture": "K_SYSTEM_ARCH",
            "analysis": "K_META_LOGIC",
            "ubi": "K_BIOLOGY",
            "business": "K_BIZFIN",
        }

        kernels = []
        for domain in domains:
            if domain in kernel_map:
                kernels.append(kernel_map[domain])

        # Always include meta logic
        if "K_META_LOGIC" not in kernels:
            kernels.insert(0, "K_META_LOGIC")

        return kernels

    def quick_translate(self, expression: str) -> str:
        """Quick translation for inline use."""
        result = self.translate(expression)
        return result.structured_logic


def translate_expression(expression: str) -> TranslatedExpression:
    """Convenience function for expression translation."""
    translator = ExpressionTranslator()
    return translator.translate(expression)


def get_translation_summary(expression: str) -> str:
    """Get a brief translation summary for logging."""
    result = translate_expression(expression)
    return (
        f"[Expression Translation] "
        f"Domains: {', '.join(result.detected_domains)} | "
        f"Tone: {result.emotional_tone or 'neutral'} | "
        f"Kernels: {', '.join(result.suggested_kernels)}"
    )
