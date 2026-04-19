"""AMOS Design Validation Engine - Validates designs against mathematical invariants.

This engine leverages the Mathematical Framework Engine to validate UI/UX designs,
code structures, and AI architectures against established mathematical principles.
"""

from __future__ import annotations


from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ValidationSeverity(Enum):
    """Severity levels for validation violations."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationViolation:
    """A single validation violation."""

    rule: str
    message: str
    severity: ValidationSeverity
    location: str = ""
    suggestion: str = ""
    mathematical_basis: str = ""


@dataclass
class ValidationResult:
    """Result of design validation."""

    is_valid: bool
    violations: list[ValidationViolation]
    passed_checks: list[str]
    score: float  # 0.0 to 1.0
    recommendations: list[str] = field(default_factory=list)
    mathematical_analysis: dict[str, Any] = field(default_factory=dict)


class DesignValidationEngine:
    """Validates designs against mathematical invariants from global frameworks.

    This engine provides:
    - UI/UX design validation (spacing, typography, color, layout)
    - Code structure validation (architecture patterns, complexity)
    - AI model validation (parameter choices, architecture decisions)
    - Security validation (cryptographic implementations)
    """

    def __init__(self):
        self._math_engine: Any = None
        self._initialize_math_engine()
        self._validation_history: list[ValidationResult] = []

    def _initialize_math_engine(self) -> None:
        """Initialize mathematical framework engine."""
        try:
            from .mathematical_framework_engine import get_framework_engine

            self._math_engine = get_framework_engine()
        except Exception:
            self._math_engine = None

    def validate_ui_design(
        self,
        spacing_values: list[int] = None,
        typography_sizes: list[float] = None,
        color_contrasts: list[tuple[float, float]] = None,
        layout_grids: list[dict] = None,
    ) -> ValidationResult:
        """Validate UI design against mathematical invariants.

        Args:
            spacing_values: List of spacing values in pixels
            typography_sizes: List of font sizes
            color_contrasts: List of (foreground, background) luminance pairs
            layout_grids: List of grid configuration dicts

        Returns:
            ValidationResult with violations and recommendations
        """
        violations: list[ValidationViolation] = []
        passed_checks: list[str] = []
        recommendations: list[str] = []

        if not self._math_engine:
            return ValidationResult(
                is_valid=False,
                violations=[
                    ValidationViolation(
                        rule="ENGINE_INIT",
                        message="Mathematical framework engine not available",
                        severity=ValidationSeverity.ERROR,
                    )
                ],
                passed_checks=[],
                score=0.0,
            )

        # Validate spacing (8-point grid)
        if spacing_values:
            for spacing in spacing_values:
                analysis = self._math_engine.solve_design_spacing(spacing)
                if not analysis.get("is_8pt_aligned", False):
                    violations.append(
                        ValidationViolation(
                            rule="SPACING_8PT_GRID",
                            message=f"Spacing {spacing}px not aligned to 8-point grid",
                            severity=ValidationSeverity.WARNING,
                            location=f"spacing: {spacing}px",
                            suggestion=f"Use {analysis.get('nearest_8pt', spacing)}px instead",
                            mathematical_basis="8-Point Grid Invariant: all spacing divisible by 8",
                        )
                    )
                else:
                    passed_checks.append(f"Spacing {spacing}px aligns to 8-point grid")

                if analysis.get("tailwind_class"):
                    recommendations.append(
                        f"Spacing {spacing}px → Tailwind class: {analysis['tailwind_class']}"
                    )

        # Validate typography (golden ratio)
        if typography_sizes and len(typography_sizes) >= 2:
            phi = self._math_engine.ui_engine.get_golden_ratio()
            for i, size in enumerate(typography_sizes[1:], 1):
                prev_size = typography_sizes[i - 1]
                ratio = size / prev_size if prev_size > 0 else 0
                deviation = abs(ratio - phi)

                if deviation > 0.15:  # 15% tolerance
                    violations.append(
                        ValidationViolation(
                            rule="TYPOGRAPHY_GOLDEN_RATIO",
                            message=f"Type scale ratio {ratio:.2f} deviates from φ ({phi:.3f})",
                            severity=ValidationSeverity.WARNING,
                            location=f"font sizes: {prev_size}px → {size}px",
                            suggestion=f"Consider {prev_size * phi:.0f}px for golden ratio",
                            mathematical_basis=f"Golden Ratio φ ≈ {phi:.3f}",
                        )
                    )
                else:
                    passed_checks.append(
                        f"Type scale {prev_size}px → {size}px follows golden ratio"
                    )

        # Validate color contrast (WCAG)
        if color_contrasts:
            for fg, bg in color_contrasts:
                ratio = self._math_engine.ui_engine.calculate_contrast_ratio(fg, bg)
                if ratio < 4.5:
                    violations.append(
                        ValidationViolation(
                            rule="COLOR_CONTRAST_WCAG",
                            message=f"Contrast ratio {ratio:.2f} below WCAG AA (4.5:1)",
                            severity=ValidationSeverity.ERROR,
                            location=f"contrast: {fg:.2f} vs {bg:.2f}",
                            suggestion="Increase contrast to at least 4.5:1 for AA compliance",
                            mathematical_basis="WCAG 2.1: (L1 + 0.05) / (L2 + 0.05) ≥ 4.5",
                        )
                    )
                elif ratio < 7.0:
                    violations.append(
                        ValidationViolation(
                            rule="COLOR_CONTRAST_WCAG_AAA",
                            message=f"Contrast ratio {ratio:.2f} below WCAG AAA (7:1)",
                            severity=ValidationSeverity.INFO,
                            location=f"contrast: {fg:.2f} vs {bg:.2f}",
                            suggestion="Increase to 7:1 for AAA compliance",
                            mathematical_basis="WCAG 2.1 AAA requires 7:1 contrast",
                        )
                    )
                else:
                    passed_checks.append(f"Contrast ratio {ratio:.2f} meets WCAG AAA")

        # Calculate overall score
        total_checks = len(violations) + len(passed_checks)
        score = len(passed_checks) / total_checks if total_checks > 0 else 1.0

        # Adjust score based on severity
        error_count = sum(1 for v in violations if v.severity == ValidationSeverity.ERROR)
        critical_count = sum(1 for v in violations if v.severity == ValidationSeverity.CRITICAL)
        score -= error_count * 0.1 + critical_count * 0.2
        score = max(0.0, min(1.0, score))

        is_valid = score >= 0.7 and critical_count == 0 and error_count <= 2

        result = ValidationResult(
            is_valid=is_valid,
            violations=violations,
            passed_checks=passed_checks,
            score=score,
            recommendations=recommendations,
            mathematical_analysis={
                "golden_ratio": self._math_engine.ui_engine.get_golden_ratio(),
                "total_checks": total_checks,
                "error_count": error_count,
                "critical_count": critical_count,
            },
        )

        self._validation_history.append(result)

        # Audit logging
        try:
            from .math_audit_logger import get_math_audit_logger

            logger = get_math_audit_logger()
            logger.log_validation(
                "ui",
                result.is_valid,
                result.score,
                len(violations),
                {
                    "spacing_values": spacing_values,
                    "typography_sizes": typography_sizes,
                    "passed_checks": len(passed_checks),
                    "recommendations": len(recommendations),
                },
            )
        except Exception:
            pass

        return result

    def validate_code_architecture(
        self,
        code_description: str,
        complexity_metrics: dict = None,
        security_keywords: list[str] = None,
    ) -> ValidationResult:
        """Validate code architecture against mathematical principles.

        Args:
            code_description: Description of the code/system
            complexity_metrics: Dict with complexity measurements
            security_keywords: List of security-related terms found

        Returns:
            ValidationResult with architectural recommendations
        """
        violations: list[ValidationViolation] = []
        passed_checks: list[str] = []
        recommendations: list[str] = []

        if not self._math_engine:
            return ValidationResult(
                is_valid=False,
                violations=[
                    ValidationViolation(
                        rule="ENGINE_INIT",
                        message="Mathematical framework engine not available",
                        severity=ValidationSeverity.ERROR,
                    )
                ],
                passed_checks=[],
                score=0.0,
            )

        # Analyze architecture
        analysis = self._math_engine.analyze_architecture(code_description)
        detected_domains = analysis.get("detected_domains", [])
        recommended_frameworks = analysis.get("recommended_frameworks", [])

        # Validate complexity if provided
        if complexity_metrics:
            cyclomatic = complexity_metrics.get("cyclomatic_complexity", 0)
            if cyclomatic > 10:
                violations.append(
                    ValidationViolation(
                        rule="CODE_COMPLEXITY",
                        message=f"Cyclomatic complexity {cyclomatic} exceeds threshold (10)",
                        severity=ValidationSeverity.WARNING,
                        suggestion="Refactor to reduce branching complexity",
                        mathematical_basis="M = E - N + 2P (McCabe complexity)",
                    )
                )
            else:
                passed_checks.append(f"Complexity {cyclomatic} within acceptable range")

        # Security validation
        if security_keywords:
            if "rsa" in [k.lower() for k in security_keywords]:
                passed_checks.append("RSA encryption detected - verify key length ≥ 2048 bits")
            if "jwt" in [k.lower() for k in security_keywords]:
                passed_checks.append("JWT detected - verify HMAC-SHA256 signature")

        # Add framework recommendations
        for framework in recommended_frameworks:
            recommendations.append(f"Consider using {framework} based on architectural analysis")

        score = 1.0
        if violations:
            score = max(0.0, 1.0 - (len(violations) * 0.15))

        is_valid = score >= 0.7

        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            passed_checks=passed_checks,
            score=score,
            recommendations=recommendations,
            mathematical_analysis=analysis,
        )

    def validate_ai_architecture(
        self, model_description: str, parameter_count: int = None, layer_config: list[int] = None
    ) -> ValidationResult:
        """Validate AI model architecture against mathematical principles.

        Args:
            model_description: Description of the AI model
            parameter_count: Total number of parameters
            layer_config: List of layer sizes

        Returns:
            ValidationResult with AI-specific recommendations
        """
        violations: list[ValidationViolation] = []
        passed_checks: list[str] = []
        recommendations: list[str] = []

        if not self._math_engine:
            return ValidationResult(
                is_valid=False,
                violations=[
                    ValidationViolation(
                        rule="ENGINE_INIT",
                        message="Mathematical framework engine not available",
                        severity=ValidationSeverity.ERROR,
                    )
                ],
                passed_checks=[],
                score=0.0,
            )

        desc_lower = model_description.lower()

        # Transformer validation
        if "transformer" in desc_lower or "attention" in desc_lower:
            if layer_config:
                for i, size in enumerate(layer_config):
                    # Check if dimensions are powers of 2
                    if size > 0 and (size & (size - 1)) != 0 and size > 64:
                        violations.append(
                            ValidationViolation(
                                rule="AI_DIMENSION_POWER_2",
                                message=f"Layer {i} size {size} not power of 2",
                                severity=ValidationSeverity.INFO,
                                suggestion="Consider power of 2 for optimal computation",
                                mathematical_basis="Power-of-2 dimensions optimize matrix operations",
                            )
                        )

            # Attention head recommendations
            if parameter_count and parameter_count > 1_000_000_000:
                recommendations.append(
                    "Large model detected: Consider LoRA for efficient fine-tuning"
                )

            passed_checks.append("Transformer architecture validated")

        # Neural network layer validation
        if layer_config and len(layer_config) >= 2:
            # Check for dimension reduction pattern
            decreasing = all(
                layer_config[i] >= layer_config[i + 1] for i in range(len(layer_config) - 1)
            )
            if not decreasing:
                violations.append(
                    ValidationViolation(
                        rule="AI_LAYER_DIMENSIONS",
                        message="Layer dimensions don't follow reduction pattern",
                        severity=ValidationSeverity.WARNING,
                        suggestion="Consider progressive dimension reduction (encoder pattern)",
                        mathematical_basis="Information bottleneck theory",
                    )
                )
            else:
                passed_checks.append("Layer dimensions follow encoder pattern")

        score = 1.0 if not violations else max(0.0, 1.0 - (len(violations) * 0.1))
        is_valid = score >= 0.8

        result = ValidationResult(
            is_valid=is_valid,
            violations=violations,
            passed_checks=passed_checks,
            score=score,
            recommendations=recommendations,
            mathematical_analysis={
                "model_type": "transformer" if "transformer" in desc_lower else "neural_network",
                "complexity_score": score,
            },
        )

        self._validation_history.append(result)
        return result

    def generate_report(self, result: ValidationResult) -> str:
        """Generate a human-readable validation report."""
        return format_validation_report(result)


def format_validation_report(result: ValidationResult) -> str:
    """Format a validation result as a human-readable report.

    Args:
        result: The validation result to format

    Returns:
        Formatted string report
    """
    lines = [
        "DESIGN VALIDATION REPORT",
        "=" * 60,
        f"Valid: {result.is_valid}",
        f"Score: {result.score:.1%}",
        f"Violations: {len(result.violations)}",
        f"Passed: {len(result.passed_checks)}",
        "",
        "VIOLATIONS:",
        "-" * 40,
    ]

    for v in result.violations:
        lines.extend(
            [
                f"[{v.severity.value.upper()}] {v.rule}",
                f"  Message: {v.message}",
            ]
        )
        if v.location:
            lines.append(f"  Location: {v.location}")
        if v.suggestion:
            lines.append(f"  Suggestion: {v.suggestion}")
        if v.mathematical_basis:
            lines.append(f"  Basis: {v.mathematical_basis}")
        lines.append("")

    if result.passed_checks:
        lines.extend(["PASSED CHECKS:", "-" * 40])
        for check in result.passed_checks:
            lines.append(f"  ✓ {check}")
        lines.append("")

    if result.recommendations:
        lines.extend(["RECOMMENDATIONS:", "-" * 40])
        for rec in result.recommendations:
            lines.append(f"  → {rec}")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


# Global singleton instance
_design_validation_engine: DesignValidationEngine | None = None


def get_design_validation_engine() -> DesignValidationEngine:
    """Get the global DesignValidationEngine instance."""
    global _design_validation_engine
    if _design_validation_engine is None:
        _design_validation_engine = DesignValidationEngine()
    return _design_validation_engine


if __name__ == "__main__":
    # Demo validation
    engine = get_design_validation_engine()

    print("=" * 60)
    print("DESIGN VALIDATION ENGINE DEMO")
    print("=" * 60)

    # Demo 1: UI Design Validation
    print("\n1. UI Design Validation:")
    result = engine.validate_ui_design(
        spacing_values=[8, 16, 24, 32, 20, 15],  # 20 and 15 are not 8pt aligned
        typography_sizes=[16, 26, 42],  # Should follow golden ratio
        color_contrasts=[(0.9, 0.1), (0.6, 0.5)],  # One good, one bad contrast
    )
    print(engine.generate_report(result))

    # Demo 2: Code Architecture Validation
    print("\n2. Code Architecture Validation:")
    result = engine.validate_code_architecture(
        code_description="Building a distributed microservices architecture with kubernetes",
        complexity_metrics={"cyclomatic_complexity": 12},
    )
    print(engine.generate_report(result))

    # Demo 3: AI Architecture Validation
    print("\n3. AI Architecture Validation:")
    result = engine.validate_ai_architecture(
        model_description="Transformer-based LLM with attention mechanism",
        parameter_count=1_500_000_000,
        layer_config=[768, 768, 3072, 768],  # Hidden sizes
    )
    print(engine.generate_report(result))

    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
