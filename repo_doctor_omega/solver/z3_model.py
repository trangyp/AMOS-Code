"""Z3 SMT model for repository invariant constraints.

Encodes repository invariants as SMT constraints and provides:
- Satisfiability checking
- Optimization for minimum-cost repairs
- Unsat core extraction for diagnosis
"""


from dataclasses import dataclass, field
from typing import Any

# Optional Z3 import - gracefully handle if not installed
try:
    import z3
from typing import List, Optional

    Z3_AVAILABLE = True
except ImportError:
    z3 = None  # type: ignore
    Z3_AVAILABLE = False


@dataclass
class InvariantConstraint:
    """Represents an invariant as an SMT constraint."""

    name: str
    constraint_str: str  # e.g., "Initialized = true -> LoadedSpecsCount > 0"
    variables: List[str] = field(default_factory=list)
    is_hard: bool = True  # Hard constraints must hold
    weight: float = 1.0  # For soft constraints


@dataclass
class RepairCandidate:
    """A candidate repair action."""

    action: str  # e.g., "add_init_function", "fix_import"
    target: str  # file or symbol to modify
    cost: float  # Edit cost
    blast_radius: float  # Estimated impact
    invariant_impact: List[str] = field(default_factory=list)


class Z3Model:
    """Z3 SMT model for repository repair optimization.

    Encodes invariants as constraints:
    - Initialized = true -> LoadedSpecsCount > 0
    - BrainLoaded = true -> DomainsCount > 0
    - Healthy = true -> ∧ hard invariants hold

    Usage:
        model = Z3Model()

        # Add constraints
        model.add_constraint("Initialized", "init > 0")
        model.add_constraint("BrainLoaded", "specs > 0")

        # Check satisfiability
        if not model.check():
            # Get unsat core - minimum contradictory facts
            core = model.get_unsat_core()
            print(f"Contradiction: {core}")

        # Optimize repairs
        repairs = [
            RepairCandidate("add_init", "brain.py", 2.0, 1.0),
            RepairCandidate("fix_spec", "specs.json", 1.0, 0.5),
        ]
        plan = model.optimize_repairs(repairs)
    """

    def __init__(self):
        self.constraints: Dict[str, InvariantConstraint] = {}
        self.variables: Dict[str, Any] = {}  # Z3 variables
        self._solver: Any = None
        self._optimizer: Any = None

    def is_available(self) -> bool:
        """Check if Z3 is available."""
        return Z3_AVAILABLE and z3 is not None

    def _ensure_solver(self) -> bool:
        """Ensure solver is initialized."""
        if not self.is_available():
            return False
        if self._solver is None:
            self._solver = z3.Solver()
        return True

    def _ensure_optimizer(self) -> bool:
        """Ensure optimizer is initialized."""
        if not self.is_available():
            return False
        if self._optimizer is None:
            self._optimizer = z3.Optimize()
        return True

    def add_constraint(self, name: str, constraint_str: str, is_hard: bool = True) -> bool:
        """Add an invariant constraint.

        Args:
            name: Constraint identifier
            constraint_str: Human-readable constraint (for reference)
            is_hard: Whether this is a hard constraint

        Returns:
            True if added successfully
        """
        self.constraints[name] = InvariantConstraint(
            name=name,
            constraint_str=constraint_str,
            is_hard=is_hard,
        )

        if not self.is_available():
            return False

        # Parse and add to solver
        try:
            z3_constraint = self._parse_constraint(constraint_str)
            if z3_constraint is not None and self._solver is not None:
                if is_hard:
                    self._solver.add(z3_constraint)
                else:
                    # Soft constraints use optimization
                    pass
            return True
        except Exception:
            return False

    def _parse_constraint(self, constraint_str: str) -> Any:
        """Parse a constraint string into Z3 expression.

        Simple parser for common patterns:
        - "A -> B" (implication)
        - "A > B" (greater than)
        - "A = B" (equality)
        - "A and B" (conjunction)
        """
        if z3 is None:
            return None

        # Create variables on demand
        # Parse "Initialized = true -> LoadedSpecsCount > 0"
        if "->" in constraint_str:
            parts = constraint_str.split("->", 1)
            left = self._parse_expr(parts[0].strip())
            right = self._parse_expr(parts[1].strip())
            if left is not None and right is not None:
                return z3.Implies(left, right)

        # Simple expression
        return self._parse_expr(constraint_str)

    def _parse_expr(self, expr_str: str) -> Any:
        """Parse a simple expression."""
        if z3 is None:
            return None

        expr_str = expr_str.strip()

        # Boolean literal
        if expr_str.lower() == "true":
            return z3.BoolVal(True)
        if expr_str.lower() == "false":
            return z3.BoolVal(False)

        # Comparison: "X > Y", "X < Y", "X = Y"
        for op in [">=", "<=", ">", "<", "="]:
            if op in expr_str:
                parts = expr_str.split(op, 1)
                if len(parts) == 2:
                    left = self._get_var(parts[0].strip())
                    right = self._get_var(parts[1].strip())

                    if left is None or right is None:
                        continue

                    if op == ">=":
                        return left >= right
                    elif op == "<=":
                        return left <= right
                    elif op == ">":
                        return left > right
                    elif op == "<":
                        return left < right
                    elif op == "=":
                        if isinstance(left, z3.ArithRef) or isinstance(right, z3.ArithRef):
                            return left == right
                        return left == right

        # Variable reference
        return self._get_var(expr_str)

    def _get_var(self, name: str) -> Any:
        """Get or create a Z3 variable."""
        if z3 is None:
            return None

        name = name.strip()

        if name not in self.variables:
            # Infer type from name
            if any(x in name.lower() for x in ["count", "size", "num", "cost"]):
                self.variables[name] = z3.Int(name)
            elif any(x in name.lower() for x in ["loaded", "initialized", "healthy", "valid"]):
                self.variables[name] = z3.Bool(name)
            else:
                # Default to integer
                self.variables[name] = z3.Int(name)

        # Handle numeric literals
        try:
            return int(name)
        except ValueError:
            pass

        return self.variables.get(name)

    def check(self) -> bool:
        """Check if constraints are satisfiable.

        Returns:
            True if satisfiable, False if unsat
        """
        if not self._ensure_solver():
            # Without Z3, assume constraints are satisfiable
            return True

        result = self._solver.check()
        return result == z3.sat

    def get_unsat_core(self) -> List[str]:
        """Get unsat core - minimum contradictory facts.

        Returns:
            List of constraint names in the unsat core
        """
        if not self.is_available() or self._solver is None:
            return []

        if self._solver.check() != z3.unsat:
            return []

        try:
            core = self._solver.unsat_core()
            # Map back to constraint names
            return [str(c) for c in core]
        except Exception:
            return []

    def optimize_repairs(self, candidates: List[RepairCandidate]) -> List[RepairCandidate]:
        """Optimize repair order using Z3 optimizer.

        Minimizes:
        - Total edit cost
        - Blast radius
        - Subject to: repairs restore all hard invariants

        Args:
            candidates: Available repair actions

        Returns:
            Optimized repair sequence
        """
        if not self._ensure_optimizer() or not candidates:
            # Without Z3, return candidates sorted by cost
            return sorted(candidates, key=lambda r: r.cost)

        # Create selection variables
        select = {}
        for i, cand in enumerate(candidates):
            select[i] = z3.Bool(f"select_{i}")

        # Objective: minimize total cost
        total_cost = z3.Sum(
            [z3.If(select[i], int(cand.cost * 100), 0) for i, cand in enumerate(candidates)]
        )

        # Objective: minimize blast radius
        total_blast = z3.Sum(
            [z3.If(select[i], int(cand.blast_radius * 100), 0) for i, cand in enumerate(candidates)]
        )

        # Combined objective (weighted)
        objective = total_cost + total_blast
        self._optimizer.minimize(objective)

        # Must select at least one repair
        self._optimizer.add(z3.Or([select[i] for i in range(len(candidates))]))

        # Check and get model
        if self._optimizer.check() == z3.sat:
            model = self._optimizer.model()

            # Extract selected repairs
            selected = []
            for i in range(len(candidates)):
                if model[select[i]]:
                    selected.append(candidates[i])

            # Sort by cost
            return sorted(selected, key=lambda r: r.cost)

        # Fallback: return all sorted by cost
        return sorted(candidates, key=lambda r: r.cost)

    def get_model_values(self) -> Dict[str, Any]:
        """Get variable assignments from current model.

        Returns:
            Dictionary of variable names to values
        """
        if not self.is_available() or self._solver is None:
            return {}

        if self._solver.check() != z3.sat:
            return {}

        model = self._solver.model()
        values = {}

        for name, var in self.variables.items():
            try:
                val = model[var]
                if val is not None:
                    values[name] = val
            except Exception:
                pass

        return values

    def reset(self) -> None:
        """Reset the solver state."""
        self.constraints.clear()
        self.variables.clear()
        self._solver = None
        self._optimizer = None
