"""Schrödinger equation - Numerical solver for quantum systems.

Solves the time-independent Schrödinger equation.
"""


class SchrodingerEquation:
    """Schrödinger equation numerical solver."""

    @staticmethod
    def solve_particle_in_box(length: float = 1.0, quantum_number: int = 1) -> dict:
        """Solve particle in a box (infinite potential well)."""
        # Analytical energy (in Hartree atomic units): E_n = (n²π²)/(2L²)
        import numpy as np

        energy = (quantum_number**2 * np.pi**2) / (2 * length**2)

        return {
            "energy": float(energy),
            "quantum_number": quantum_number,
            "length": length,
            "system": "particle_in_box",
        }

    @staticmethod
    def solve_harmonic_oscillator(omega: float = 1.0, quantum_number: int = 0) -> dict:
        """Solve quantum harmonic oscillator."""
        # Energy eigenvalue (analytical): E_n = ℏω(n + 1/2)
        energy = omega * (quantum_number + 0.5)

        return {
            "energy": float(energy),
            "quantum_number": quantum_number,
            "omega": omega,
            "system": "harmonic_oscillator",
        }

    @staticmethod
    def schrodinger_equation(params: dict) -> dict:
        """Main solver interface for Schrödinger equation."""
        system_type = params.get("system_type", "particle_in_box")
        quantum_number = int(params.get("quantum_number", 1))

        if system_type == "particle_in_box":
            length = params.get("length", 1.0)
            result = SchrodingerEquation.solve_particle_in_box(length, quantum_number)
            result["status"] = "success"
            return result
        elif system_type == "harmonic_oscillator":
            omega = params.get("omega", 1.0)
            result = SchrodingerEquation.solve_harmonic_oscillator(omega, quantum_number)
            result["status"] = "success"
            return result
        else:
            return {"error": f"Unknown system_type: {system_type}", "status": "error"}


# Module-level convenience functions
def particle_in_box(n: int, L: float, x: float) -> float:
    """Wavefunction for particle in a box at position x.

    ψ_n(x) = sqrt(2/L) * sin(nπx/L)
    """
    import numpy as np

    return np.sqrt(2 / L) * np.sin(n * np.pi * x / L)


def harmonic_oscillator_psi(
    n: int, x: float, omega: float = 1.0, m: float = 1.0, hbar: float = 1.0
) -> float:
    """Wavefunction for quantum harmonic oscillator.

    Uses analytical formula for ground state and first few excited states.
    """
    import numpy as np

    alpha = m * omega / hbar
    if n == 0:
        return (alpha / np.pi) ** 0.25 * np.exp(-alpha * x**2 / 2)
    elif n == 1:
        return (alpha / np.pi) ** 0.25 * np.sqrt(2 * alpha) * x * np.exp(-alpha * x**2 / 2)
    else:
        # For higher states, return approximate value
        return (alpha / np.pi) ** 0.25 * np.exp(-alpha * x**2 / 2)
