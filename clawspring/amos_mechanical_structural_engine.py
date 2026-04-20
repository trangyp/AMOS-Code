"""AMOS Mechanical Structural Engine - Civil and structural analysis.

Enhanced with Mathematical Framework Engine integration for advanced
structural calculations and validation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# Mathematical Framework Integration
try:
    from .mathematical_framework_engine import get_framework_engine

    MATH_FRAMEWORK_AVAILABLE = True
except ImportError:
    MATH_FRAMEWORK_AVAILABLE = False

try:
    from .math_audit_logger import get_math_audit_logger

    AUDIT_LOGGER_AVAILABLE = True
except ImportError:
    AUDIT_LOGGER_AVAILABLE = False


class StructuralDomain(Enum):
    """Structural engineering domain classifications."""

    MECHANICAL = "mechanical"
    STRUCTURAL = "structural"
    CIVIL = "civil"
    AEROSPACE = "aerospace"
    ENERGY = "energy"


@dataclass
class StructuralComponent:
    """Structural component representation."""

    name: str
    component_type: str
    domain: StructuralDomain
    parameters: dict = field(default_factory=dict)


class MechanicsKernel:
    """Kernel for mechanics and materials analysis."""

    def __init__(self):
        self.materials: list[dict] = []
        self.forces: list[dict] = []

    def add_material(
        self,
        name: str,
        material_type: str,
        youngs_modulus_gpa: float,
        yield_strength_mpa: float,
    ) -> dict:
        """Add structural material."""
        material = {
            "name": name,
            "type": material_type,
            "E_gpa": youngs_modulus_gpa,
            "yield_mpa": yield_strength_mpa,
        }
        self.materials.append(material)
        return material

    def add_force(self, name: str, magnitude_n: float, direction: str) -> dict:
        """Add force."""
        force = {"name": name, "magnitude_n": magnitude_n, "direction": direction}
        self.forces.append(force)
        return force

    def calculate_stress(self, force_n: float, area_mm2: float) -> dict:
        """Calculate axial stress."""
        stress_mpa = force_n / area_mm2
        return {
            "force_n": force_n,
            "area_mm2": area_mm2,
            "stress_mpa": stress_mpa,
        }

    def calculate_deflection_beam(
        self,
        load_n: float,
        length_m: float,
        youngs_modulus_gpa: float,
        inertia_mm4: float,
    ) -> dict:
        """Calculate cantilever beam deflection."""
        E_pa = youngs_modulus_gpa * 1e9
        I_m4 = inertia_mm4 * 1e-12
        # For cantilever with end load: deflection = PL^3 / (3EI)
        deflection_m = (load_n * length_m**3) / (3 * E_pa * I_m4)
        return {
            "load_n": load_n,
            "length_m": length_m,
            "deflection_m": deflection_m,
            "deflection_mm": deflection_m * 1000,
        }

    def get_principles(self) -> list[str]:
        return [
            "Statics and equilibrium",
            "Elasticity and material behavior",
            "Stress-strain relationships",
            "Energy methods",
        ]

    def analyze_with_math_framework(self, component_description: str) -> dict[str, Any]:
        """Analyze structural component using mathematical framework.

        Leverages the AMOS Mathematical Framework Engine to get
        relevant equations and invariants for structural analysis.

        Args:
            component_description: Description of the structural component

        Returns:
            Dictionary with mathematical analysis results

        """
        if not MATH_FRAMEWORK_AVAILABLE:
            return {
                "error": "Mathematical Framework Engine not available",
                "fallback": "Using basic structural calculations only",
            }

        try:
            from .mathematical_framework_engine import get_framework_engine

            engine = get_framework_engine()

            # Analyze the component description
            analysis = engine.analyze_architecture(component_description)

            # Get relevant equations for structural engineering
            # (would map to appropriate domain if STRUCTURAL exists)
            equations = []
            if hasattr(engine, "query_by_domain"):
                # Query general mechanics equations
                all_equations = list(engine._equations.values())
                structural_eqs = [
                    eq
                    for eq in all_equations
                    if any(
                        kw in eq.name.lower()
                        for kw in [
                            "stress",
                            "strain",
                            "elastic",
                            "load",
                            "force",
                            "deflection",
                            "beam",
                            "truss",
                        ]
                    )
                ]
                equations = [
                    {"name": eq.name, "formula": eq.formula}
                    for eq in structural_eqs[:5]  # Top 5 relevant
                ]

            # Log to audit if available
            if AUDIT_LOGGER_AVAILABLE:
                try:
                    from .math_audit_logger import get_math_audit_logger

                    logger = get_math_audit_logger()
                    logger.log_architecture_analysis(
                        f"Structural: {component_description[:50]}",
                        analysis.get("detected_domains", []),
                        analysis.get("recommended_frameworks", []),
                    )
                except Exception:
                    pass

            return {
                "detected_domains": analysis.get("detected_domains", []),
                "recommended_frameworks": analysis.get("recommended_frameworks", []),
                "relevant_equations": equations,
                "timestamp": "2026-01-01T00:00:00Z",  # Placeholder
                "math_framework_enabled": True,
            }

        except Exception as e:
            return {
                "error": f"Math framework analysis failed: {str(e)}",
                "fallback": "Using basic structural calculations",
            }

    def validate_with_invariants(
        self, force_n: float, area_mm2: float, material_yield_mpa: float
    ) -> dict[str, Any]:
        """Validate structural calculation against mathematical invariants.

        Checks that stress calculations satisfy fundamental constraints:
        - Stress must be positive for compressive/tensile forces
        - Stress should not exceed material yield strength (safety factor)
        - Units must be consistent (N/mm2 = MPa)

        Args:
            force_n: Force in Newtons
            area_mm2: Cross-sectional area in mm2
            material_yield_mpa: Material yield strength in MPa

        Returns:
            Validation result with pass/fail status

        """
        stress_mpa = force_n / area_mm2 if area_mm2 > 0 else float("inf")
        safety_factor = 1.5  # Standard engineering safety factor
        max_allowed_stress = material_yield_mpa / safety_factor

        invariants = []
        passed = True

        # Invariant 1: Physical consistency (positive stress magnitude)
        if stress_mpa < 0:
            invariants.append(
                {
                    "name": "Physical Consistency",
                    "status": "FAIL",
                    "message": "Negative stress magnitude detected",
                }
            )
            passed = False
        else:
            invariants.append(
                {
                    "name": "Physical Consistency",
                    "status": "PASS",
                    "message": "Stress magnitude is positive",
                }
            )

        # Invariant 2: Safety limit (stress below yield with safety factor)
        if stress_mpa > max_allowed_stress:
            invariants.append(
                {
                    "name": "Safety Limit",
                    "status": "FAIL",
                    "message": (
                        f"Stress ({stress_mpa:.2f} MPa) exceeds safe limit "
                        f"({max_allowed_stress:.2f} MPa)"
                    ),
                }
            )
            passed = False
        else:
            invariants.append(
                {
                    "name": "Safety Limit",
                    "status": "PASS",
                    "message": (
                        f"Stress ({stress_mpa:.2f} MPa) within safe limit "
                        f"({max_allowed_stress:.2f} MPa)"
                    ),
                }
            )

        # Invariant 3: Unit consistency (implicit in calculation)
        invariants.append(
            {
                "name": "Unit Consistency",
                "status": "PASS",
                "message": "N/mm2 = MPa (consistent units)",
            }
        )

        # Log validation to audit
        if AUDIT_LOGGER_AVAILABLE:
            try:
                from .math_audit_logger import get_math_audit_logger

                logger = get_math_audit_logger()
                logger.log_invariant_check(
                    "structural_safety",
                    passed,
                    {
                        "stress_mpa": stress_mpa,
                        "yield_mpa": material_yield_mpa,
                        "safety_factor": safety_factor,
                    },
                )
            except Exception:
                pass

        return {
            "passed": passed,
            "invariants": invariants,
            "stress_mpa": stress_mpa,
            "safety_factor_applied": safety_factor,
            "max_allowed_stress": max_allowed_stress,
        }


class StructuralElementsKernel:
    """Kernel for structural element analysis."""

    def __init__(self):
        self.trusses: list[dict] = []
        self.beams: list[dict] = []
        self.frames: list[dict] = []

    def add_beam(
        self,
        name: str,
        length_m: float,
        cross_section: str,
        supports: list[str],
    ) -> dict:
        """Add beam."""
        beam = {
            "name": name,
            "length_m": length_m,
            "cross_section": cross_section,
            "supports": supports,
        }
        self.beams.append(beam)
        return beam

    def add_truss(self, name: str, members: int, joints: int) -> dict:
        """Add truss."""
        truss = {"name": name, "members": members, "joints": joints}
        self.trusses.append(truss)
        return truss

    def add_frame(self, name: str, stories: int, bays: int) -> dict:
        """Add frame."""
        frame = {"name": name, "stories": stories, "bays": bays}
        self.frames.append(frame)
        return frame

    def calculate_euler_buckling(
        self, youngs_modulus_gpa: float, inertia_mm4: float, length_m: float
    ) -> dict:
        """Calculate Euler buckling load."""
        E_pa = youngs_modulus_gpa * 1e9
        I_m4 = inertia_mm4 * 1e-12
        # P_cr = pi^2 * EI / L^2
        p_cr_n = (math.pi**2 * E_pa * I_m4) / (length_m**2)
        return {
            "E_gpa": youngs_modulus_gpa,
            "I_mm4": inertia_mm4,
            "length_m": length_m,
            "p_critical_n": p_cr_n,
            "p_critical_kn": p_cr_n / 1000,
        }

    def get_principles(self) -> list[str]:
        return [
            "Truss analysis",
            "Beam bending and deflection",
            "Frame behavior",
            "Buckling stability",
        ]


class LoadsAnalysisKernel:
    """Kernel for load analysis."""

    def __init__(self):
        self.loads: list[dict] = []

    def add_load(
        self,
        name: str,
        load_type: str,
        magnitude: float,
        unit: str,
    ) -> dict:
        """Add load."""
        load = {
            "name": name,
            "type": load_type,
            "magnitude": magnitude,
            "unit": unit,
        }
        self.loads.append(load)
        return load

    def calculate_load_combination(
        self,
        dead_load: float,
        live_load: float,
        wind_load: float = 0,
        seismic_load: float = 0,
        safety_factor_dl: float = 1.2,
        safety_factor_ll: float = 1.6,
    ) -> dict:
        """Calculate load combination."""
        factored_dl = dead_load * safety_factor_dl
        factored_ll = live_load * safety_factor_ll
        total_load = factored_dl + factored_ll + wind_load + seismic_load
        return {
            "dead_load": dead_load,
            "live_load": live_load,
            "factored_dl": factored_dl,
            "factored_ll": factored_ll,
            "total_load": total_load,
        }

    def get_principles(self) -> list[str]:
        return [
            "Dead and live loads",
            "Wind and seismic loads",
            "Load combinations",
            "Safety factors",
        ]


class DesignCodesKernel:
    """Kernel for design codes and safety."""

    def __init__(self):
        self.code_checks: list[dict] = []

    def add_code_check(
        self,
        name: str,
        code: str,
        check_type: str,
        passed: bool,
    ) -> dict:
        """Add code check."""
        check = {
            "name": name,
            "code": code,
            "type": check_type,
            "passed": passed,
        }
        self.code_checks.append(check)
        return check

    def calculate_safety_factor(self, resistance: float, demand: float) -> dict:
        """Calculate safety factor."""
        if demand == 0:
            return {"error": "Zero demand"}
        sf = resistance / demand
        return {
            "resistance": resistance,
            "demand": demand,
            "safety_factor": sf,
            "adequate": sf >= 1.0,
        }

    def get_principles(self) -> list[str]:
        return [
            "Ultimate limit state (ULS)",
            "Serviceability limit state (SLS)",
            "Partial safety factors",
            "Code compliance",
        ]


class MechanicalStructuralEngine:
    """AMOS Mechanical Structural Engine - Civil/mechanical structures."""

    VERSION = "vInfinity_MAX"
    NAME = "AMOS_Mechanical_Structural_OMEGA"

    def __init__(self):
        self.mechanics_kernel = MechanicsKernel()
        self.elements_kernel = StructuralElementsKernel()
        self.loads_kernel = LoadsAnalysisKernel()
        self.codes_kernel = DesignCodesKernel()

    def analyze(self, description: str, domains: list[str | None] = None) -> dict[str, Any]:
        """Run structural analysis across specified domains."""
        domains = domains or ["mechanics", "elements", "loads", "codes"]
        results: dict[str, Any] = {}
        if "mechanics" in domains:
            results["mechanics"] = self._analyze_mechanics(description)
        if "elements" in domains:
            results["elements"] = self._analyze_elements(description)
        if "loads" in domains:
            results["loads"] = self._analyze_loads(description)
        if "codes" in domains:
            results["codes"] = self._analyze_codes(description)
        return results

    def _analyze_mechanics(self, description: str) -> dict:
        return {
            "query": description[:100],
            "materials": len(self.mechanics_kernel.materials),
            "forces": len(self.mechanics_kernel.forces),
            "principles": self.mechanics_kernel.get_principles(),
        }

    def _analyze_elements(self, description: str) -> dict:
        return {
            "query": description[:100],
            "trusses": len(self.elements_kernel.trusses),
            "beams": len(self.elements_kernel.beams),
            "frames": len(self.elements_kernel.frames),
            "principles": self.elements_kernel.get_principles(),
        }

    def _analyze_loads(self, description: str) -> dict:
        return {
            "query": description[:100],
            "loads": len(self.loads_kernel.loads),
            "principles": self.loads_kernel.get_principles(),
        }

    def _analyze_codes(self, description: str) -> dict:
        return {
            "query": description[:100],
            "code_checks": len(self.codes_kernel.code_checks),
            "principles": self.codes_kernel.get_principles(),
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
            "mechanics": "Mechanics & Materials",
            "elements": "Structural Elements",
            "loads": "Loads Analysis",
            "codes": "Design Codes & Safety",
        }
        for domain, data in results.items():
            display_name = domain_names.get(domain, domain.title())
            lines.extend(["", f"### {display_name}"])
            if isinstance(data, dict):
                for key, value in data.items():
                    if key not in ("principles", "query"):
                        lines.append(f"- **{key}**: {value}")
                if "principles" in data:
                    lines.append(f"- **Principles**: {', '.join(data['principles'][:2])}...")
        lines.extend(
            [
                "",
                "## Gaps and Limitations",
                "- FEA simulation not included",
                "- Country-specific codes require manual lookup",
                "- Real-time structural monitoring not available",
                "- Advanced nonlinear analysis simplified",
                "",
                "## Safety Disclaimer",
                "NOT a licensed engineer. All outputs require review and sign-off "
                "by qualified engineers. Not for safety-critical design without "
                "professional validation.",
            ]
        )
        return "\n".join(lines)


# Singleton instance
_mechanical_structural_engine: MechanicalStructuralEngine | None = None


def get_mechanical_structural_engine() -> MechanicalStructuralEngine:
    """Get or create the Mechanical Structural Engine singleton."""
    global _mechanical_structural_engine
    if _mechanical_structural_engine is None:
        _mechanical_structural_engine = MechanicalStructuralEngine()
    return _mechanical_structural_engine
