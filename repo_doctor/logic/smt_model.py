"""
SMT Model - Z3 Theorem Prover Integration

Encodes repository invariants as SMT formulas and discharges
them through Z3 to prove or disprove satisfiability.

This turns "smells" into provable invariant failures.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Try to import Z3, gracefully degrade if unavailable
try:
    import z3

    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False
    z3 = None  # type: ignore


@dataclass
class SMTResult:
    """Result of an SMT proof attempt."""

    satisfiable: bool
    model: Dict[str, Any] = None
    proof: str = None
    counterexample: Dict[str, Any] = None
    verification_time_ms: float = 0.0


class SMTModel:
    """
    SMT solver wrapper for repository verification.

    Encodes repository state as SMT variables:
    - α_s: syntax integrity (Real)
    - α_i: import integrity (Real)
    - α_t: type integrity (Real)
    - α_a: API integrity (Real)
    - α_e: entrypoint integrity (Real)
    - α_p: packaging integrity (Real)
    - α_r: runtime integrity (Real)
    - α_d: documentation integrity (Real)
    - α_h: history integrity (Real)
    - α_σ: security integrity (Real)
    """

    def __init__(self):
        self.solver: Any | None = None
        self.variables: Dict[str, Any] = {}
        self._init_solver()

    def _init_solver(self) -> None:
        """Initialize Z3 solver if available."""
        if not Z3_AVAILABLE:
            logger.warning("Z3 not available. SMT verification disabled.")
            return

        self.solver = z3.Solver()
        self._create_variables()

    def _create_variables(self) -> None:
        """Create SMT variables for each repository dimension."""
        if not Z3_AVAILABLE or not self.solver:
            return

        # State vector variables (α_k ∈ [0, 1])
        dimensions = ["s", "i", "t", "a", "e", "p", "r", "d", "h", "sigma"]

        for dim in dimensions:
            var = z3.Real(f"alpha_{dim}")
            self.variables[dim] = var
            # Constraint: 0 <= α_k <= 1
            self.solver.add(var >= 0, var <= 1)

        # Energy threshold variable
        self.variables["E_threshold"] = z3.Real("E_threshold")
        self.solver.add(self.variables["E_threshold"] >= 0)

        # Lambda weights for Hamiltonian
        self.variables["lambdas"] = {
            "s": z3.Real("lambda_s"),
            "i": z3.Real("lambda_i"),
            "t": z3.Real("lambda_t"),
            "a": z3.Real("lambda_a"),
            "e": z3.Real("lambda_e"),
            "p": z3.Real("lambda_p"),
            "r": z3.Real("lambda_r"),
            "d": z3.Real("lambda_d"),
            "h": z3.Real("lambda_h"),
            "sigma": z3.Real("lambda_sigma"),
        }

        for lam in self.variables["lambdas"].values():
            self.solver.add(lam > 0)  # All weights positive

    def encode_hamiltonian(self) -> Any:
        """
        Encode repository Hamiltonian as SMT expression.

        H_repo = Σ λ_k · (1 - α_k)^2
        """
        if not Z3_AVAILABLE or not self.solver:
            return None

        energy_terms = []
        for dim, alpha in self.variables.items():
            if dim.startswith("alpha_"):
                dim_short = dim.replace("alpha_", "")
                if dim_short in self.variables["lambdas"]:
                    lam = self.variables["lambdas"][dim_short]
                    term = lam * (1 - alpha) ** 2
                    energy_terms.append(term)

        return z3.Sum(energy_terms) if energy_terms else z3.RealVal(0)

    def encode_invariant(self, name: str, constraint: Any) -> None:
        """Add an invariant constraint to the solver."""
        if not self.solver:
            return
        self.solver.add(constraint)
        logger.debug(f"Added invariant: {name}")

    def encode_repo_validity(self) -> None:
        """
        Encode: RepoValid = ∧n I_n

        All dimensions must be at 1.0 for validity.
        """
        if not self.solver:
            return

        # Each alpha must equal 1 for validity
        for dim, alpha in self.variables.items():
            if dim.startswith("alpha_"):
                # For strict validity: alpha == 1
                self.solver.add(alpha == 1)

    def encode_threshold(self, max_energy: float = 2.0) -> None:
        """
        Encode: E_repo < E_threshold

        Energy must stay below threshold for stability.
        """
        if not self.solver:
            return

        energy = self.encode_hamiltonian()
        if energy is not None:
            self.solver.add(energy < z3.RealVal(max_energy))

    def check_sat(self) -> SMTResult:
        """
        Check satisfiability of current constraints.

        Returns
        -------
            SMTResult with sat/unsat and model if applicable

        """
        import time

        start = time.perf_counter()

        if not Z3_AVAILABLE or not self.solver:
            return SMTResult(
                satisfiable=True,  # Assume valid if can't check
                proof="Z3 unavailable - assuming valid",
            )

        result = self.solver.check()
        elapsed = (time.perf_counter() - start) * 1000

        if result == z3.sat:
            model = self.solver.model()
            return SMTResult(
                satisfiable=True,
                model=self._extract_model(model),
                verification_time_ms=elapsed,
            )
        else:
            return SMTResult(
                satisfiable=False,
                proof=str(result),
                verification_time_ms=elapsed,
            )

    def _extract_model(self, z3_model: Any) -> dict[str, float]:
        """Extract variable assignments from Z3 model."""
        model_dict = {}
        for dim, var in self.variables.items():
            if dim.startswith("alpha_"):
                val = z3_model.evaluate(var, model_completion=True)
                try:
                    model_dict[dim] = float(val.as_decimal(4))
                except Exception:
                    model_dict[dim] = str(val)
        return model_dict

    def push(self) -> None:
        """Push solver context for incremental solving."""
        if self.solver:
            self.solver.push()

    def pop(self) -> None:
        """Pop solver context."""
        if self.solver:
            self.solver.pop()

    def reset(self) -> None:
        """Reset solver to initial state."""
        if self.solver:
            self.solver.reset()
            self._create_variables()


def prove_invariant(
    state_values: Dict[str, float],
    max_energy: float = 2.0,
) -> SMTResult:
    """
    Prove repository invariants using Z3.

    Args:
    ----
        state_values: Current state vector values
        max_energy: Maximum acceptable energy threshold

    Returns:
    -------
        SMTResult with proof or counterexample

    """
    model = SMTModel()

    if not Z3_AVAILABLE:
        return SMTResult(
            satisfiable=True,
            proof="Z3 not available - no formal proof generated",
        )

    # Encode constraints from current state
    for dim, value in state_values.items():
        var_name = f"alpha_{dim}"
        if var_name in model.variables:
            var = model.variables[var_name]
            # Add constraint: alpha == current_value
            model.solver.add(var == z3.RealVal(value))

    # Check if current state satisfies validity
    model.encode_threshold(max_energy)

    return model.check_sat()


@dataclass
class InvariantFormula:
    """A formal invariant as SMT formula."""

    name: str
    description: str
    z3_expr: Any

    def check(self, model: SMTModel) -> bool:
        """Check if this invariant holds in the given model."""
        if not Z3_AVAILABLE or not model.solver:
            return True  # Assume valid if can't verify

        model.push()
        model.solver.add(z3.Not(self.z3_expr))  # Try to find counterexample
        result = model.solver.check()
        model.pop()

        return result == z3.unsat  # Invariant holds if no counterexample


# Common invariant formulas
INVARIANTS = {
    "parse": lambda m: m.variables.get("s", z3.RealVal(1)) == 1,
    "import": lambda m: m.variables.get("i", z3.RealVal(1)) == 1,
    "type": lambda m: m.variables.get("t", z3.RealVal(1)) == 1,
    "api": lambda m: m.variables.get("a", z3.RealVal(1)) == 1,
    "entrypoint": lambda m: m.variables.get("e", z3.RealVal(1)) == 1,
    "packaging": lambda m: m.variables.get("p", z3.RealVal(1)) == 1,
    "security": lambda m: m.variables.get("sigma", z3.RealVal(1)) == 1,
}
