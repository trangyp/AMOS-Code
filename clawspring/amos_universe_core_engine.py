"""AMOS Universe Core Engine - Universal physics and cosmology foundation."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class PhysicalDomain(Enum):
    """Fundamental physical domains."""
    GRAVITATION = "gravitation"
    ELECTROMAGNETISM = "electromagnetism"
    WEAK_FORCE = "weak_force"
    STRONG_FORCE = "strong_force"
    QUANTUM_FIELD = "quantum_field"
    THERMODYNAMICS = "thermodynamics"


@dataclass
class UniversalConstant:
    """Physical constant with metadata."""

    name: str
    symbol: str
    value: float
    units: str
    uncertainty: float
    domain: str


class FundamentalConstantsKernel:
    """Kernel for fundamental physical constants."""

    CONSTANTS: Dict[str, UniversalConstant] = {
        "G": UniversalConstant(
            "Newtonian constant of gravitation",
            "G",
            6.67430e-11,
            "m^3 kg^-1 s^-2",
            1.5e-15,
            "gravitation",
        ),
        "c": UniversalConstant(
            "Speed of light in vacuum",
            "c",
            299792458.0,
            "m s^-1",
            0.0,
            "electromagnetism",
        ),
        "h": UniversalConstant(
            "Planck constant",
            "h",
            6.62607015e-34,
            "J s",
            0.0,
            "quantum",
        ),
        "hbar": UniversalConstant(
            "Reduced Planck constant",
            "ℏ",
            1.054571817e-34,
            "J s",
            0.0,
            "quantum",
        ),
        "e": UniversalConstant(
            "Elementary charge",
            "e",
            1.602176634e-19,
            "C",
            0.0,
            "electromagnetism",
        ),
        "k_B": UniversalConstant(
            "Boltzmann constant",
            "k_B",
            1.380649e-23,
            "J K^-1",
            0.0,
            "thermodynamics",
        ),
        "N_A": UniversalConstant(
            "Avogadro constant",
            "N_A",
            6.02214076e23,
            "mol^-1",
            0.0,
            "thermodynamics",
        ),
        "alpha": UniversalConstant(
            "Fine-structure constant",
            "α",
            7.2973525693e-3,
            "dimensionless",
            1.1e-12,
            "quantum",
        ),
    }

    def get_constant(self, symbol: str) -> Optional[UniversalConstant]:
        """Get constant by symbol."""
        return self.CONSTANTS.get(symbol)

    def get_by_domain(self, domain: str) -> List[UniversalConstant]:
        """Get constants by physical domain."""
        return [c for c in self.CONSTANTS.values() if c.domain == domain]

    def calculate_plank_scale(self) -> dict[str, float]:
        """Calculate Planck scale quantities."""
        G = self.CONSTANTS["G"].value
        c = self.CONSTANTS["c"].value
        hbar = self.CONSTANTS["hbar"].value
        # Planck length
        l_p = (hbar * G / c**3) ** 0.5
        # Planck time
        t_p = (hbar * G / c**5) ** 0.5
        # Planck mass
        m_p = (hbar * c / G) ** 0.5
        # Planck temperature
        k_B = self.CONSTANTS["k_B"].value
        T_p = m_p * c**2 / k_B
        return {
            "length": l_p,
            "time": t_p,
            "mass": m_p,
            "temperature": T_p,
        }


class CosmologicalModelKernel:
    """Kernel for cosmological models and parameters."""

    def __init__(self):
        self.parameters = {
            "H0": 70.0,  # Hubble constant km/s/Mpc
            "Omega_m": 0.315,  # Matter density parameter
            "Omega_lambda": 0.685,  # Dark energy density parameter
            "Omega_r": 9.1e-5,  # Radiation density parameter
            "Omega_k": 0.0,  # Curvature (flat universe)
            "age": 13.8e9,  # Age of universe in years
            "CMB_T": 2.725,  # CMB temperature in K
        }

    def get_critical_density(self) -> float:
        """Calculate critical density of universe."""
        G = 6.67430e-11  # m^3 kg^-1 s^-2
        H0 = self.parameters["H0"] * 1000 / 3.086e22  # Convert to s^-1
        rho_c = 3 * H0**2 / (8 * 3.14159 * G)
        return rho_c

    def scale_factor_age_relation(self, z: float) -> float:
        """Age of universe at redshift z (simplified)."""
        # Simplified matter-dominated approximation
        H0 = self.parameters["H0"]
        Omega_m = self.parameters["Omega_m"]
        age_gyr = 2 / (3 * H0 * Omega_m**0.5 * (1 + z)**1.5)
        return age_gyr  # in Gyr

    def get_composition(self) -> dict[str, float]:
        """Get universe composition percentages."""
        return {
            "dark_energy": self.parameters["Omega_lambda"] * 100,
            "dark_matter": (self.parameters["Omega_m"] - 0.05) * 100,
            "ordinary_matter": 5.0,
            "radiation": self.parameters["Omega_r"] * 100,
        }


class SpacetimeGeometryKernel:
    """Kernel for spacetime geometry concepts."""

    GEOMETRIES = {
        "flat": {"curvature": 0, "topology": "Euclidean", "volume": "infinite"},
        "spherical": {"curvature": 1, "topology": "Closed", "volume": "finite"},
        "hyperbolic": {"curvature": -1, "topology": "Open", "volume": "infinite"},
    }

    def get_geometry_type(self, omega_k: float) -> str:
        """Determine geometry from curvature parameter."""
        if abs(omega_k) < 0.01:
            return "flat"
        elif omega_k > 0:
            return "spherical"
        else:
            return "hyperbolic"

    def schwarzschild_radius(self, mass_kg: float) -> float:
        """Calculate Schwarzschild radius for mass."""
        G = 6.67430e-11
        c = 299792458.0
        return 2 * G * mass_kg / c**2

    def horizon_distance(self, age_years: float) -> float:
        """Calculate particle horizon distance."""
        c = 299792458.0  # m/s
        age_sec = age_years * 3.154e7
        return c * age_sec / 3.086e16  # Convert to Mpc


class QuantumGravityKernel:
    """Kernel for quantum gravity concepts."""

    def __init__(self):
        self.approaches = [
            "String Theory",
            "Loop Quantum Gravity",
            "Causal Dynamical Triangulation",
            "Asymptotic Safety",
            "Emergent Gravity",
        ]

    def get_unification_energy(self) -> float:
        """Estimate GUT scale energy in GeV."""
        return 1e16  # Approximate Grand Unification scale

    def black_hole_entropy(self, mass_kg: float) -> float:
        """Calculate Bekenstein-Hawking entropy."""
        k_B = 1.380649e-23
        hbar = 1.054571817e-34
        G = 6.67430e-11
        c = 299792458.0
        # S = k_B * A / (4 * l_p^2) where A is horizon area
        r_s = 2 * G * mass_kg / c**2
        A = 4 * 3.14159 * r_s**2
        l_p = (hbar * G / c**3) ** 0.5
        return k_B * A / (4 * l_p**2)

    def hawking_temperature(self, mass_kg: float) -> float:
        """Calculate Hawking temperature."""
        hbar = 1.054571817e-34
        c = 299792458.0
        G = 6.67430e-11
        k_B = 1.380649e-23
        # T = ℏ c^3 / (8 π G M k_B)
        return hbar * c**3 / (8 * 3.14159 * G * mass_kg * k_B)


class UniverseCoreEngine:
    """AMOS Universe Core Engine - Universal physics foundation."""

    VERSION = "vInfinity_Universe_1.0.0"
    NAME = "AMOS_Universe_Core_OMEGA"

    def __init__(self):
        self.constants = FundamentalConstantsKernel()
        self.cosmology = CosmologicalModelKernel()
        self.spacetime = SpacetimeGeometryKernel()
        self.quantum_gravity = QuantumGravityKernel()

    def analyze(
        self, query: str, context: Dict[str, Any]  = None
    ) -> Dict[str, Any]:
        """Run universe core analysis."""
        context = context or {}
        results: Dict[str, Any] = {
            "query": query[:100],
            "fundamental_constants": {},
            "cosmological_parameters": {},
            "spacetime_analysis": {},
            "quantum_gravity": {},
        }
        # Analyze for constant references
        query_lower = query.lower()
        constants_found = []
        for symbol, const in self.constants.CONSTANTS.items():
            if symbol.lower() in query_lower or const.name.lower() in query_lower:
                constants_found.append({
                    "symbol": symbol,
                    "name": const.name,
                    "value": const.value,
                    "units": const.units,
                })
        results["fundamental_constants"] = {
            "found": constants_found,
            "total_available": len(self.constants.CONSTANTS),
        }
        # Planck scale
        results["planck_scale"] = self.constants.calculate_plank_scale()
        # Cosmology
        results["cosmological_parameters"] = {
            "H0": self.cosmology.parameters["H0"],
            "critical_density_kg_m3": self.cosmology.get_critical_density(),
            "composition": self.cosmology.get_composition(),
            "age_Gyr": self.cosmology.parameters["age"] / 1e9,
        }
        # Geometry
        omega_k = self.cosmology.parameters["Omega_k"]
        geometry = self.spacetime.get_geometry_type(omega_k)
        results["spacetime_analysis"] = {
            "geometry_type": geometry,
            "curvature_parameter": omega_k,
            "geometry_properties": self.spacetime.GEOMETRIES.get(geometry, {}),
            "particle_horizon_Mpc": self.spacetime.horizon_distance(
                self.cosmology.parameters["age"]
            ),
        }
        # Quantum gravity
        results["quantum_gravity"] = {
            "approaches": self.quantum_gravity.approaches,
            "unification_scale_GeV": self.quantum_gravity.get_unification_energy(),
        }
        return results

    def get_findings_summary(self, results: dict) -> str:
        """Generate findings summary."""
        lines = [
            f"# {self.NAME} {self.VERSION}",
            "",
            "Creator: Trang Phan | System: AMOS vInfinity",
            "Role: Universal Physics and Cosmology Foundation",
            "",
            "## Fundamental Physical Constants",
        ]
        constants = results.get("fundamental_constants", {})
        found = constants.get("found", [])
        if found:
            lines.append(f"Found {len(found)} constants in query:")
            for c in found[:5]:
                lines.append(f"- **{c['symbol']}** ({c['name']}): {c['value']} {c['units']}")
        else:
            lines.append("Key constants available:")
            for symbol, const in list(self.constants.CONSTANTS.items())[:5]:
                lines.append(f"- **{symbol}**: {const.name}")
        lines.extend([
            "",
            "## Planck Scale (Quantum Gravity Regime)",
        ])
        planck = results.get("planck_scale", {})
        lines.extend([
            f"- **Planck Length**: {planck.get('length', 0):.2e} m",
            f"- **Planck Time**: {planck.get('time', 0):.2e} s",
            f"- **Planck Mass**: {planck.get('mass', 0):.2e} kg",
            f"- **Planck Temperature**: {planck.get('temperature', 0):.2e} K",
        ])
        cosmo = results.get("cosmological_parameters", {})
        lines.extend([
            "",
            "## Cosmological Model (Lambda-CDM)",
            f"- **Hubble Constant (H0)**: {cosmo.get('H0', 0)} km/s/Mpc",
            f"- **Critical Density**: {cosmo.get('critical_density_kg_m3', 0):.2e} kg/m³",
            f"- **Universe Age**: {cosmo.get('age_Gyr', 0):.1f} Gyr",
            "",
            "### Universe Composition",
        ])
        comp = cosmo.get("composition", {})
        for component, percentage in comp.items():
            lines.append(f"- **{component.replace('_', ' ').title()}**: {percentage:.1f}%")
        spacetime = results.get("spacetime_analysis", {})
        lines.extend([
            "",
            "## Spacetime Geometry",
            f"- **Geometry Type**: {spacetime.get('geometry_type', 'unknown')}",
            f"- **Curvature Parameter**: {spacetime.get('curvature_parameter', 0)}",
            f"- **Particle Horizon**: {spacetime.get('particle_horizon_Mpc', 0):.0f} Mpc",
        ])
        qg = results.get("quantum_gravity", {})
        lines.extend([
            "",
            "## Quantum Gravity Approaches",
            f"- **Unification Scale**: {qg.get('unification_scale_GeV', 0):.0e} GeV",
            "- **Candidate Theories**:",
        ])
        for approach in qg.get("approaches", [])[:3]:
            lines.append(f"  - {approach}")
        lines.extend([
            "",
            "## Key Universal Principles",
            "1. **Principle of Relativity**: Physical laws same in all inertial frames",
            "2. **Uncertainty Principle**: ℏ/2 limit on conjugate variable precision",
            "3. **Cosmological Principle**: Universe homogeneous and isotropic at large scales",
            "4. **Second Law**: Entropy increases in isolated systems",
            "5. **Equivalence Principle**: Gravitational and inertial mass equivalent",
            "",
            "## Safety Constraints",
            "- Does not predict beyond established physics",
            "- Quantum gravity theories are speculative - marked accordingly",
            "- Cosmological parameters subject to observational updates",
            "- Not a substitute for specialized astrophysics calculations",
            "",
            "## Limitations",
            "- Dark energy nature remains unexplained",
            "- Quantum gravity unification unsolved",
            "- Initial conditions of universe unknown",
            "- Multiverse hypotheses excluded from calculations",
        ])
        return "\n".join(lines)


# Singleton instance
_universe_core: Optional[UniverseCoreEngine] = None


def get_universe_core_engine() -> UniverseCoreEngine:
    """Get or create the Universe Core Engine singleton."""
from __future__ import annotations

    global _universe_core
    if _universe_core is None:
        _universe_core = UniverseCoreEngine()
    return _universe_core
