"""AMOS Symbolic Core - Symbolic computation with SymPy.

Usage:
    from amos_symbolic_core import SymbolicEquationEngine
    engine = SymbolicEquationEngine()
    latex_str = engine.to_latex("kinetic_energy")
    derivative = engine.symbolic_diff("kinetic_energy", "v")
"""

from typing import Any

try:
    import sympy as sp
    from sympy import (
        Max,
        Rational,
        Symbol,
        cos,
        diff,
        exp,
        integrate,
        latex,
        log,
        pi,
        simplify,
        sin,
        solve,
        sqrt,
        symbols,
        sympify,
        tan,
    )

    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False


from amos_equation_massive import MassiveEquationKernel


class SymbolicEquationEngine:
    """Symbolic computation engine for AMOS equations."""

    def __init__(self) -> None:
        self._kernel = MassiveEquationKernel()
        self._symbolic_registry = self._build_registry()

    def is_available(self) -> bool:
        return SYMPY_AVAILABLE

    def _build_registry(self) -> Dict[str, Any]:
        """Build symbolic equation registry."""
        if not SYMPY_AVAILABLE:
            return {}

        m, v, h, g, k, x, F, a, r = symbols("m v h g k x F a r", real=True, positive=True)

        return {
            "kinetic_energy": lambda: Rational(1, 2) * m * v**2,
            "potential_energy": lambda: m * g * h,
            "spring_energy": lambda: Rational(1, 2) * k * x**2,
            "newtons_second": lambda: m * a,
            "work_done": lambda: F * Symbol("d"),
            "momentum": lambda: m * v,
            "power_energy": lambda: Symbol("E") / Symbol("t"),
            "impulse": lambda: F * Symbol("dt"),
            "centripetal_force": lambda: m * v**2 / r,
            "angular_velocity": lambda: Symbol("theta") / Symbol("t"),
            "torque": lambda: F * r * sin(Symbol("theta")),
            "pressure": lambda: F / Symbol("A"),
            "buoyant_force": lambda: Symbol("rho") * Symbol("V") * g,
            "escape_velocity": lambda: sqrt(2 * Symbol("G") * Symbol("M") / Symbol("R")),
            "pendulum_period": lambda: 2 * pi * sqrt(Symbol("L") / g),
            "sigmoid": lambda: 1 / (1 + exp(-x)),
            "tanh": lambda: (exp(x) - exp(-x)) / (exp(x) + exp(-x)),
            "relu": lambda: Max(0, x),
            "gelu": lambda: Rational(1, 2)
            * x
            * (1 + tanh(sqrt(2 / pi) * (x + Rational(44715, 1000000) * x**3))),
            "swish": lambda: x / (1 + exp(-Symbol("beta") * x)),
            "mse_loss": lambda: (Symbol("y_true") - Symbol("y_pred")) ** 2,
            "mae_loss": lambda: sp.Abs(Symbol("y_true") - Symbol("y_pred")),
            "littles_law": lambda: Symbol("lam") * Symbol("W"),
            "snr_db": lambda: 10 * log(Symbol("signal_power") / Symbol("noise_power")) / log(10),
            "nyquist_rate": lambda: 2 * Symbol("max_freq"),
            "perplexity_ml": lambda: exp(Symbol("loss")),
        }

    def get_symbolic(self, equation_name: str) -> Any:
        """Get symbolic representation of an equation."""
        if not SYMPY_AVAILABLE or equation_name not in self._symbolic_registry:
            return None
        try:
            return self._symbolic_registry[equation_name]()
        except Exception:
            return None

    def symbolic_diff(self, equation_name: str, var: str) -> Any:
        """Compute symbolic derivative."""
        if not SYMPY_AVAILABLE:
            return None
        try:
            # Create fresh symbols for differentiation
            var_sym = Symbol(var, real=True)
            # Rebuild expression with fresh symbols to ensure proper differentiation
            expr_str = str(self.get_symbolic(equation_name))
            if expr_str and expr_str != "None":
                expr = sympify(expr_str)
                return diff(expr, var_sym)
        except Exception:
            pass
        return None

    def symbolic_integrate(self, equation_name: str, var: str) -> Any:
        """Compute symbolic integral."""
        if not SYMPY_AVAILABLE:
            return None
        expr = self.get_symbolic(equation_name)
        if expr is None:
            return None
        try:
            return integrate(expr, Symbol(var))
        except Exception:
            return None

    def simplify(self, expression: str) -> Any:
        """Simplify a mathematical expression."""
        if not SYMPY_AVAILABLE:
            return None
        try:
            return simplify(sympify(expression))
        except Exception:
            return None

    def to_latex(self, equation_name: str) -> str:
        """Convert equation to LaTeX string."""
        if not SYMPY_AVAILABLE:
            return f"{equation_name}"
        expr = self.get_symbolic(equation_name)
        if expr is None:
            return f"{equation_name}"
        try:
            return latex(expr)
        except Exception:
            return f"{equation_name}"

    def get_gradient(self, equation_name: str, variables: list[str]) -> Dict[str, Any]:
        """Compute gradient (partial derivatives)."""
        if not SYMPY_AVAILABLE:
            return {}
        expr = self.get_symbolic(equation_name)
        if expr is None:
            return {}
        return {var: diff(expr, Symbol(var)) for var in variables}

    def list_symbolic_equations(self) -> list[str]:
        """List all equations with symbolic representations."""
        return list(self._symbolic_registry.keys())

    def pattern_analysis(self, equation_name: str) -> Dict[str, Any]:
        """Analyze symbolic patterns in an equation."""
        if not SYMPY_AVAILABLE:
            return {"error": "SymPy not available"}
        expr = self.get_symbolic(equation_name)
        if expr is None:
            return {"error": "Equation not found"}
        return {
            "equation": equation_name,
            "symbolic_form": str(expr),
            "latex": self.to_latex(equation_name),
            "free_symbols": [str(s) for s in expr.free_symbols],
        }


def get_symbolic_engine() -> SymbolicEquationEngine:
    """Get or create the global symbolic engine instance."""
    return SymbolicEquationEngine()


if __name__ == "__main__":
    print("AMOS Symbolic Equation Engine")
    print("=" * 50)

    engine = get_symbolic_engine()
    print(f"\nSymPy Available: {engine.is_available()}")

    if engine.is_available():
        print(f"\nSymbolic Equations: {len(engine.list_symbolic_equations())}")

        print("\n--- Sample Equations ---")
        for eq_name in ["kinetic_energy", "sigmoid", "littles_law"]:
            latex_str = engine.to_latex(eq_name)
            print(f"{eq_name}: ${latex_str}$")

        print("\n--- Symbolic Differentiation ---")
        dKE = engine.symbolic_diff("kinetic_energy", "v")
        print(f"d(KE)/dv = {dKE}")

        print("\n--- Pattern Analysis ---")
        analysis = engine.pattern_analysis("kinetic_energy")
        print(f"Equation: {analysis['equation']}")
        print(f"Form: {analysis['symbolic_form']}")
        print(f"Variables: {analysis['free_symbols']}")
    else:
        print("SymPy not installed. Run: pip install sympy")
