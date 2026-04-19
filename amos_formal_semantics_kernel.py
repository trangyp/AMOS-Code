from typing import Any

"""AMOS Formal Semantics Kernel (FSK).

The layer that converts equations, invariants, and architecture into
executable semantic objects with operational meaning.

Formalism → Semantics → RuntimeObjects → Checks → ExecutionMeaning

This is the missing understanding layer between Reading/Thinking and Execution.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto

# =============================================================================
# 1. Formula Classification System
# =============================================================================


class FormulaClass(Enum):
    """Semantic classification of formal expressions."""

    STATE_DEFINITION = auto()  # X_t = (...)
    TRANSITION_EQUATION = auto()  # H_{t+1} = Reorganize(...)
    OBJECTIVE_FUNCTION = auto()  # argmax [...]
    SELECTION_RULE = auto()  # B* = argmax [...]
    CONSTRAINT_RULE = auto()  # Ov_t < τ_safe
    INVARIANT_RULE = auto()  # dDependency/dt ≤ 0
    COMMIT_GATE = auto()  # Gate(...)
    UPDATE_RULE = auto()  # X_{t+1} = Evolve(...)
    ARCHITECTURE_DECLARATION = auto()  # Component → Component
    TYPE_DECLARATION = auto()  # τ ::= τ_c | τ_q
    OPERATOR_DEFINITION = auto()  # Φ: (Σ, A) → Σ'
    PROOF_OBLIGATION = auto()  # Must prove: ...


class SymbolRole(Enum):
    """Role of a symbol in the formal system."""

    STATE = auto()
    INPUT = auto()
    OUTPUT = auto()
    PARAMETER = auto()
    OBJECTIVE = auto()
    CONSTRAINT = auto()
    INVARIANT = auto()
    OPERATOR = auto()
    PREDICATE = auto()


class ValueType(Enum):
    """Types for grounded symbols."""

    SCALAR = auto()
    VECTOR = auto()
    TENSOR = auto()
    SET = auto()
    GRAPH = auto()
    FUNCTION = auto()
    PREDICATE = auto()
    STATE_OBJECT = auto()
    OPERATOR = auto()


# =============================================================================
# 2. Core Semantic Data Structures
# =============================================================================


@dataclass
class SymbolTableEntry:
    """Grounded symbol with complete semantic information."""

    name: str
    type: ValueType
    role: SymbolRole
    domain: str = ""
    measurement_rule: str = ""  # How to measure/observe this symbol
    update_rule: str = ""  # How this symbol changes
    allowed_operations: List[str] = field(default_factory=list)
    source: str = ""  # Where this symbol comes from (equation, invariant, etc.)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class TypedASTNode:
    """AST node with type information."""

    node_type: str  # "argmax", "add", "symbol", "apply", etc.
    value: Any = None
    children: List[TypedASTNode] = field(default_factory=list)
    inferred_type: ValueType = ValueType.SCALAR
    free_symbols: List[str] = field(default_factory=list)
    bound_symbols: List[str] = field(default_factory=list)


@dataclass
class OperationalSemantics:
    """Operational meaning of a formal expression."""

    reads: List[str] = field(default_factory=list)  # State it reads
    writes: List[str] = field(default_factory=list)  # State it writes
    mode: str = "evaluate"  # evaluate|optimize|check|define|transition|forbid
    computational_complexity: str = "O(1)"  # Big-O complexity
    side_effects: List[str] = field(default_factory=list)


@dataclass
class FormalExpression:
    """Fully compiled formal expression with semantics."""

    id: str = ""
    kind: FormulaClass = FormulaClass.STATE_DEFINITION
    raw_text: str = ""
    ast: TypedASTNode | None = None
    free_symbols: List[str] = field(default_factory=list)
    bound_symbols: List[str] = field(default_factory=list)
    input_symbols: List[str] = field(default_factory=list)
    output_symbols: List[str] = field(default_factory=list)
    state_dependencies: List[str] = field(default_factory=list)
    type_requirements: Dict[str, ValueType] = field(default_factory=dict)
    operational_semantics: OperationalSemantics = field(default_factory=OperationalSemantics)
    checkability: Dict[str, bool] = field(
        default_factory=lambda: {
            "is_executable": True,
            "is_runtime_checkable": True,
            "requires_solver": False,
            "requires_proof": False,
        }
    )
    compiled_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class Invariant:
    """Compiled invariant with executable predicate."""

    id: str = ""
    predicate: str = ""  # e.g., "dependency_next <= dependency_current"
    predicate_fn: Callable[[dict[str, Any]], bool] = None  # Runtime-checkable
    scope: str = ""  # Where this invariant applies
    severity: str = "critical"  # critical|warning|info
    on_violation: str = ""  # rollback_or_reframe|deny_patch|halt
    description: str = ""
    formal_source: str = ""  # Original LaTeX/text


@dataclass
class Objective:
    """Compiled objective with optimizer semantics."""

    id: str = ""
    optimize_over: str = ""  # Variable to optimize
    operator: str = "argmax"  # argmax|argmin|maximize|minimize
    score_function: str = ""  # Mathematical expression
    score_fn: Callable[..., float] = None  # Executable scoring function
    constraints: List[str] = field(default_factory=list)
    output: str = ""  # Output variable
    formal_source: str = ""


@dataclass
class TransitionRule:
    """Compiled transition rule with state semantics."""

    id: str = ""
    state_in: str = ""  # Input state variable
    operator: str = ""  # e.g., "reorganize", "evolve", "update"
    condition_inputs: List[str] = field(default_factory=list)
    state_out: str = ""  # Output state variable
    writes: List[str] = field(default_factory=list)  # What state is modified
    reads: List[str] = field(default_factory=list)  # What state is read
    transition_fn: Callable[[Any, Any], Any] = None  # Executable transition
    formal_source: str = ""


@dataclass
class ArchitectureComponent:
    """Component in architecture graph."""

    id: str = ""
    type: str = ""  # kernel|engine|memory|verifier|planner|governor|renderer|optimizer
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ArchitectureEdge:
    """Edge in architecture graph."""

    source: str = ""
    relation: str = ""  # feeds|constrains|verifies|updates|stores|routes_to
    target: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ArchitectureGraph:
    """Compiled architecture as executable graph."""

    components: List[ArchitectureComponent] = field(default_factory=list)
    edges: List[ArchitectureEdge] = field(default_factory=list)
    entry_points: List[str] = field(default_factory=list)
    exit_points: List[str] = field(default_factory=list)

    def get_component(self, id: str) -> ArchitectureComponent | None:
        """Get component by ID."""
        for c in self.components:
            if c.id == id:
                return c
        return None

    def get_dependencies(self, component_id: str) -> List[str]:
        """Get components that feed into this component."""
        deps = []
        for e in self.edges:
            if e.target == component_id and e.relation == "feeds":
                deps.append(e.source)
        return deps


@dataclass
class ProofObligation:
    """Proof obligation generated from formal system."""

    id: str = ""
    statement: str = ""
    kind: str = ""  # type_safety|invariant_preservation|constraint_satisfiability|dependency_consistency|transition_validity
    status: str = "open"  # open|proved|failed|unknown
    dependencies: List[str] = field(default_factory=list)
    generated_from: str = ""  # Which expression generated this


# =============================================================================
# 3. Formal Understanding State
# =============================================================================


@dataclass
class FormalUnderstandingState:
    """Measurable state of system understanding."""

    symbols_resolved: float = 0.0  # 0-1
    types_resolved: float = 0.0  # 0-1
    equations_classified: float = 0.0  # 0-1
    invariants_compiled: float = 0.0  # 0-1
    objectives_compiled: float = 0.0  # 0-1
    transitions_compiled: float = 0.0  # 0-1
    architecture_graph_built: float = 0.0  # 0-1
    proof_obligations_generated: float = 0.0  # 0-1
    overall_semantic_integrity: float = 0.0  # 0-1

    def to_dict(self) -> dict[str, float]:
        return {
            "symbols_resolved": self.symbols_resolved,
            "types_resolved": self.types_resolved,
            "equations_classified": self.equations_classified,
            "invariants_compiled": self.invariants_compiled,
            "objectives_compiled": self.objectives_compiled,
            "transitions_compiled": self.transitions_compiled,
            "architecture_graph_built": self.architecture_graph_built,
            "proof_obligations_generated": self.proof_obligations_generated,
            "overall_semantic_integrity": self.overall_semantic_integrity,
        }


# =============================================================================
# 4. Formal Semantics Kernel
# =============================================================================


class FormalSemanticsKernel:
    """
    Core semantic engine that converts formal text into executable objects.

    Implements the pipeline:
    FormalText → FormalAST → TypedSemanticGraph → ExecutableSemantics
    """

    def __init__(self):
        self.symbol_table: Dict[str, SymbolTableEntry] = {}
        self.expressions: Dict[str, FormalExpression] = {}
        self.invariants: Dict[str, Invariant] = {}
        self.objectives: Dict[str, Objective] = {}
        self.transitions: Dict[str, TransitionRule] = {}
        self.architecture: ArchitectureGraph = ArchitectureGraph()
        self.proof_obligations: List[ProofObligation] = []
        self.understanding_state = FormalUnderstandingState()

    # ==========================================================================
    # 4.1 Parsing & Symbol Extraction
    # ==========================================================================

    def parse_formal_text(self, text: str, expr_id: str | None = None) -> FormalExpression:
        """Parse formal mathematical text into structured expression."""
        expr_id = expr_id or f"expr_{len(self.expressions)}"

        # Extract symbols from text
        symbols = self._extract_symbols(text)

        # Build typed AST
        ast = self._build_typed_ast(text, symbols)

        # Classify formula role
        formula_class = self._classify_formula_role(text, ast)

        # Create formal expression
        expr = FormalExpression(
            id=expr_id,
            kind=formula_class,
            raw_text=text,
            ast=ast,
            free_symbols=symbols["free"],
            bound_symbols=symbols["bound"],
            input_symbols=symbols["inputs"],
            output_symbols=symbols["outputs"],
            state_dependencies=symbols["state_deps"],
        )

        self.expressions[expr_id] = expr
        return expr

    def _extract_symbols(self, text: str) -> dict[str, list[str]]:
        """Extract symbols from mathematical text."""
        # Pattern matching for common mathematical notation
        free_symbols: List[str] = []
        bound_symbols = []
        inputs = []
        outputs = []
        state_deps = []

        # Extract state variables (X_t, H_t, etc.)
        state_matches = re.findall(r"\b([A-Z][a-zA-Z]*_\{?t\}?|[A-Z][a-zA-Z]*_\{?t\+1\}?)\b", text)
        for match in state_matches:
            if "t+1" in match:
                outputs.append(match)
            else:
                state_deps.append(match)
                free_symbols.append(match)

        # Extract bound variables (indices)
        bound_matches = re.findall(r"\\argmax_\{(\w+)\}|\\argmin_\{(\w+)\}", text)
        for match in bound_matches:
            bound_symbols.extend([m for m in match if m])

        # Extract input parameters
        input_matches = re.findall(r"\(([^)]+)\)", text)
        for match in input_matches:
            parts = [p.strip() for p in match.split(",")]
            for part in parts:
                if part and part not in free_symbols:
                    inputs.append(part)

        return {
            "free": list(set(free_symbols)),
            "bound": list(set(bound_symbols)),
            "inputs": list(set(inputs)),
            "outputs": list(set(outputs)),
            "state_deps": list(set(state_deps)),
        }

    def _build_typed_ast(self, text: str, symbols: dict[str, list[str]]) -> TypedASTNode:
        """Build typed abstract syntax tree from text."""
        # Simplified parsing - in full implementation would use proper parser
        root = TypedASTNode(node_type="expression", value=text)

        # Detect structure
        if "argmax" in text or "argmin" in text:
            root.node_type = "optimization"
            root.inferred_type = ValueType.FUNCTION

            # Extract optimizer components
            match = re.search(r"\\argmax_\{(\w+)\}\s*\[(.+?)\]", text)
            if match:
                binder = match.group(1)
                body = match.group(2)
                root.children = [
                    TypedASTNode(node_type="binder", value=binder, inferred_type=ValueType.SET),
                    TypedASTNode(node_type="objective", value=body, inferred_type=ValueType.SCALAR),
                ]
                root.bound_symbols = [binder]

        elif "=" in text and "_" in text:
            root.node_type = "equation"
            root.inferred_type = ValueType.STATE_OBJECT

            # Check if state transition
            if "_{t+1}" in text:
                root.node_type = "state_transition"

        return root

    def _classify_formula_role(self, text: str, ast: TypedASTNode) -> FormulaClass:
        """Classify the semantic role of a formula."""
        text_lower = text.lower()

        # Selection rules
        if "argmax" in text_lower or "argmin" in text_lower:
            if "=" in text and ("*" in text or "^" in text or "star" in text_lower):
                return FormulaClass.SELECTION_RULE
            return FormulaClass.OBJECTIVE_FUNCTION

        # Transition rules
        if "reorganize" in text_lower or "evolve" in text_lower or "update" in text_lower:
            return FormulaClass.TRANSITION_EQUATION

        # Invariants
        if "invariant" in text_lower or "ddependency" in text_lower or "drift" in text_lower:
            return FormulaClass.INVARIANT_RULE

        # Constraints
        if "<" in text or ">" in text or "≤" in text or "≥" in text:
            if "constraint" in text_lower or "safe" in text_lower or "τ" in text:
                return FormulaClass.CONSTRAINT_RULE

        # State definitions
        if "=" in text and ("_t" in text or "_0" in text or "state" in text_lower):
            return FormulaClass.STATE_DEFINITION

        # Update rules
        if "_{t+1}" in text and "=" in text:
            return FormulaClass.UPDATE_RULE

        # Architecture
        if "→" in text or "->" in text or "kernel" in text_lower or "engine" in text_lower:
            return FormulaClass.ARCHITECTURE_DECLARATION

        return FormulaClass.STATE_DEFINITION

    # ==========================================================================
    # 4.2 Symbol Binding & Type Inference
    # ==========================================================================

    def bind_symbols(
        self, expr: FormalExpression, context: Dict[str, Any] = None
    ) -> FormalExpression:
        """Bind symbols to their semantic definitions."""
        context = context or {}

        # Create symbol table entries for unbound symbols
        for symbol in expr.free_symbols:
            if symbol not in self.symbol_table:
                # Infer type from name patterns
                symbol_type = self._infer_symbol_type(symbol, expr.kind)
                role = self._infer_symbol_role(symbol, expr.kind)

                entry = SymbolTableEntry(
                    name=symbol,
                    type=symbol_type,
                    role=role,
                    source=expr.id,
                    domain=self._infer_domain(symbol),
                )
                self.symbol_table[symbol] = entry

        # Update type requirements
        for symbol in expr.free_symbols:
            if symbol in self.symbol_table:
                expr.type_requirements[symbol] = self.symbol_table[symbol].type

        return expr

    def _infer_symbol_type(self, symbol: str, formula_class: FormulaClass) -> ValueType:
        """Infer the type of a symbol from its name and context."""
        # Pattern-based type inference
        if "B" in symbol and ("branch" in symbol.lower() or "B_" in symbol):
            return ValueType.SET  # Branch candidates
        if symbol.startswith("H"):
            return ValueType.STATE_OBJECT  # Human state
        if symbol.startswith("Ψ") or symbol.startswith("Psi"):
            return ValueType.STATE_OBJECT  # System state
        if "Value" in symbol or "Risk" in symbol or "Cost" in symbol:
            return ValueType.SCALAR  # Scalar metrics
        if "Q" in symbol and ("_t" in symbol or "state" in symbol.lower()):
            return ValueType.STATE_OBJECT
        if formula_class == FormulaClass.OBJECTIVE_FUNCTION:
            return ValueType.SCALAR
        if formula_class == FormulaClass.TRANSITION_EQUATION:
            return ValueType.STATE_OBJECT
        return ValueType.SCALAR

    def _infer_symbol_role(self, symbol: str, formula_class: FormulaClass) -> SymbolRole:
        """Infer the role of a symbol in the formal system."""
        if "_t" in symbol and "_{t+1}" not in symbol:
            return SymbolRole.STATE
        if "_{t+1}" in symbol:
            return SymbolRole.OUTPUT
        if formula_class == FormulaClass.OBJECTIVE_FUNCTION:
            return SymbolRole.OBJECTIVE
        if formula_class == FormulaClass.CONSTRAINT_RULE:
            return SymbolRole.CONSTRAINT
        if formula_class == FormulaClass.INVARIANT_RULE:
            return SymbolRole.INVARIANT
        return SymbolRole.PARAMETER

    def _infer_domain(self, symbol: str) -> str:
        """Infer the domain of a symbol."""
        if symbol.startswith("H"):
            return "human_cognitive_state"
        if symbol.startswith("Ψ") or symbol.startswith("Psi"):
            return "system_state"
        if "B" in symbol:
            return "branch_candidates"
        if "Value" in symbol:
            return "utility_space"
        return "unknown"

    # ==========================================================================
    # 4.3 Operational Semantics Compilation
    # ==========================================================================

    def compile_operational_semantics(self, expr: FormalExpression) -> FormalExpression:
        """Attach operational semantics to formal expression."""
        semantics = OperationalSemantics()

        if expr.kind == FormulaClass.SELECTION_RULE:
            semantics.reads = expr.state_dependencies
            semantics.writes = expr.output_symbols
            semantics.mode = "optimize"
            semantics.computational_complexity = "O(n)"  # Linear search

        elif expr.kind == FormulaClass.TRANSITION_EQUATION:
            semantics.reads = expr.input_symbols + expr.state_dependencies
            semantics.writes = expr.output_symbols
            semantics.mode = "transition"
            semantics.computational_complexity = "O(1)"  # State update

        elif expr.kind == FormulaClass.INVARIANT_RULE:
            semantics.reads = expr.state_dependencies
            semantics.writes = []
            semantics.mode = "check"
            semantics.computational_complexity = "O(1)"  # Predicate check

        elif expr.kind == FormulaClass.OBJECTIVE_FUNCTION:
            semantics.reads = expr.free_symbols
            semantics.writes = []
            semantics.mode = "evaluate"
            semantics.computational_complexity = "O(n)"

        elif expr.kind == FormulaClass.STATE_DEFINITION:
            semantics.reads = []
            semantics.writes = expr.output_symbols if expr.output_symbols else expr.free_symbols
            semantics.mode = "define"

        expr.operational_semantics = semantics
        return expr

    # ==========================================================================
    # 4.4 Specialized Compilers
    # ==========================================================================

    def compile_invariant(
        self, expr: FormalExpression, invariant_id: str | None = None
    ) -> Invariant:
        """Compile an invariant expression into a runtime-checkable predicate."""
        invariant_id = invariant_id or f"inv_{len(self.invariants)}"

        # Build predicate string from expression
        predicate = self._build_predicate(expr)

        # Compile predicate function
        predicate_fn = self._compile_predicate_fn(predicate, expr)

        # Determine severity and violation policy
        severity = "critical"
        on_violation = "rollback_or_reframe"

        if "dependency" in expr.raw_text.lower():
            on_violation = "rollback_or_reframe"
        elif "drift" in expr.raw_text.lower():
            on_violation = "deny_patch"
        elif "identity" in expr.raw_text.lower():
            on_violation = "deny_patch"

        invariant = Invariant(
            id=invariant_id,
            predicate=predicate,
            predicate_fn=predicate_fn,
            scope=expr.operational_semantics.reads[0]
            if expr.operational_semantics.reads
            else "global",
            severity=severity,
            on_violation=on_violation,
            description=f"Invariant: {expr.raw_text[:100]}...",
            formal_source=expr.raw_text,
        )

        self.invariants[invariant_id] = invariant
        return invariant

    def _build_predicate(self, expr: FormalExpression) -> str:
        """Build a predicate string from expression."""
        text = expr.raw_text

        # Convert common patterns
        if "dDependency/dt" in text or "≤ 0" in text:
            return "dependency_next <= dependency_current"
        if "Drift" in text and "δ" in text:
            return "identity_distance(identity_t, identity_t1) <= delta_id"
        if "<" in text or ">" in text:
            # Extract inequality
            match = re.search(r"(\w+)\s*([<>≤≥])\s*(\w+)", text)
            if match:
                return f"{match.group(1)} {match.group(2)} {match.group(3)}"

        return f"check({', '.join(expr.free_symbols)})"

    def _compile_predicate_fn(
        self, predicate: str, expr: FormalExpression
    ) -> Callable[[dict[str, Any]], bool]:
        """Compile predicate string into executable function."""
        try:
            # Create a lambda that evaluates the predicate
            # This is a simplified version - full version would use proper AST compilation
            def predicate_fn(state: Dict[str, Any]) -> bool:
                try:
                    # Simple predicate evaluation
                    if "<=" in predicate:
                        parts = predicate.split("<=")
                        if len(parts) == 2:
                            left = parts[0].strip()
                            right = parts[1].strip()
                            left_val = state.get(left, 0)
                            right_val = state.get(right, float("inf"))
                            return left_val <= right_val
                    return True
                except Exception:
                    return False

            return predicate_fn
        except Exception:
            return None

    def compile_objective(
        self, expr: FormalExpression, objective_id: str | None = None
    ) -> Objective:
        """Compile an objective expression into optimizer-ready structure."""
        objective_id = objective_id or f"obj_{len(self.objectives)}"

        # Extract optimizer components from AST
        optimize_over = ""
        operator = "argmax"
        score_function = expr.raw_text

        if expr.ast and expr.ast.children:
            for child in expr.ast.children:
                if child.node_type == "binder":
                    optimize_over = str(child.value)
                if child.node_type == "objective":
                    score_function = str(child.value)

        # Determine operator
        if "argmax" in expr.raw_text:
            operator = "argmax"
        elif "argmin" in expr.raw_text:
            operator = "argmin"
        elif "maximize" in expr.raw_text.lower():
            operator = "maximize"
        elif "minimize" in expr.raw_text.lower():
            operator = "minimize"

        objective = Objective(
            id=objective_id,
            optimize_over=optimize_over,
            operator=operator,
            score_function=score_function,
            constraints=[],  # Would extract from context
            output=f"best_{optimize_over}" if optimize_over else "result",
            formal_source=expr.raw_text,
        )

        self.objectives[objective_id] = objective
        return objective

    def compile_transition_rule(
        self, expr: FormalExpression, rule_id: str | None = None
    ) -> TransitionRule:
        """Compile a transition equation into state semantics."""
        rule_id = rule_id or f"trans_{len(self.transitions)}"

        # Extract state components
        state_in = ""
        state_out = ""
        operator = ""

        # Pattern matching for transition structure
        if "=" in expr.raw_text:
            parts = expr.raw_text.split("=")
            if len(parts) == 2:
                lhs = parts[0].strip()
                rhs = parts[1].strip()

                # LHS is output state
                state_out = lhs

                # Extract operator from RHS
                if "Reorganize" in rhs:
                    operator = "reorganize"
                elif "Evolve" in rhs:
                    operator = "evolve"
                elif "Update" in rhs:
                    operator = "update"
                else:
                    operator = "transform"

        # Extract input state from dependencies
        state_in = expr.state_dependencies[0] if expr.state_dependencies else "state_t"

        transition = TransitionRule(
            id=rule_id,
            state_in=state_in,
            operator=operator,
            condition_inputs=expr.input_symbols,
            state_out=state_out,
            writes=expr.output_symbols,
            reads=expr.input_symbols + expr.state_dependencies,
            formal_source=expr.raw_text,
        )

        self.transitions[rule_id] = transition
        return transition

    def compile_architecture_graph(
        self, components: List[str], edges: list[tuple[str, str, str]]
    ) -> ArchitectureGraph:
        """Compile architecture declaration into component graph."""
        graph = ArchitectureGraph()

        # Create components
        for comp_id in components:
            comp_type = self._infer_component_type(comp_id)
            component = ArchitectureComponent(
                id=comp_id,
                type=comp_type,
            )
            graph.components.append(component)

        # Create edges
        for source, relation, target in edges:
            edge = ArchitectureEdge(
                source=source,
                relation=relation,
                target=target,
            )
            graph.edges.append(edge)

        self.architecture = graph
        return graph

    def _infer_component_type(self, comp_id: str) -> str:
        """Infer component type from ID."""
        comp_lower = comp_id.lower()
        if "kernel" in comp_lower:
            return "kernel"
        if "engine" in comp_lower:
            return "engine"
        if "memory" in comp_lower or "store" in comp_lower:
            return "memory"
        if "verif" in comp_lower:
            return "verifier"
        if "plan" in comp_lower:
            return "planner"
        if "govern" in comp_lower:
            return "governor"
        if "render" in comp_lower:
            return "renderer"
        if "optim" in comp_lower:
            return "optimizer"
        return "engine"

    # ==========================================================================
    # 4.5 Proof Obligation Generation
    # ==========================================================================

    def generate_proof_obligations(self) -> List[ProofObligation]:
        """Generate proof obligations from compiled formal system."""
        obligations = []

        # Type safety obligations
        for symbol_name, entry in self.symbol_table.items():
            if entry.type == ValueType.SCALAR and not entry.domain:
                obligations.append(
                    ProofObligation(
                        id=f"po_type_{symbol_name}",
                        statement=f"Symbol {symbol_name} has scalar type but no domain constraint",
                        kind="type_safety",
                        generated_from=entry.source,
                    )
                )

        # Invariant preservation obligations
        for trans_id, transition in self.transitions.items():
            for inv_id, invariant in self.invariants.items():
                if invariant.scope in transition.reads:
                    obligations.append(
                        ProofObligation(
                            id=f"po_inv_{trans_id}_{inv_id}",
                            statement=f"Transition {trans_id} preserves invariant {inv_id}",
                            kind="invariant_preservation",
                            dependencies=[trans_id, inv_id],
                            generated_from=transition.formal_source,
                        )
                    )

        # Constraint satisfiability obligations
        for obj_id, objective in self.objectives.items():
            if objective.constraints:
                obligations.append(
                    ProofObligation(
                        id=f"po_sat_{obj_id}",
                        statement=f"Objective {obj_id} constraints are satisfiable",
                        kind="constraint_satisfiability",
                        dependencies=[obj_id],
                        generated_from=objective.formal_source,
                    )
                )

        # Dependency consistency
        for comp in self.architecture.components:
            deps = self.architecture.get_dependencies(comp.id)
            for dep in deps:
                obligations.append(
                    ProofObligation(
                        id=f"po_dep_{comp.id}_{dep}",
                        statement=f"Component {comp.id} can receive input from {dep}",
                        kind="dependency_consistency",
                        dependencies=[comp.id, dep],
                    )
                )

        self.proof_obligations.extend(obligations)
        return obligations

    # ==========================================================================
    # 4.6 Semantic Integrity Evaluation
    # ==========================================================================

    def evaluate_semantic_integrity(self) -> FormalUnderstandingState:
        """Evaluate how well the formal system is understood."""
        state = FormalUnderstandingState()

        # Symbols resolved
        if self.symbol_table:
            typed_symbols = sum(
                1 for s in self.symbol_table.values() if s.type != ValueType.SCALAR or s.domain
            )
            state.symbols_resolved = typed_symbols / len(self.symbol_table)
            state.types_resolved = typed_symbols / len(self.symbol_table)

        # Equations classified
        if self.expressions:
            classified = sum(
                1 for e in self.expressions.values() if e.kind != FormulaClass.STATE_DEFINITION
            )
            state.equations_classified = classified / len(self.expressions)

        # Invariants compiled
        if self.expressions:
            invariant_exprs = [
                e for e in self.expressions.values() if e.kind == FormulaClass.INVARIANT_RULE
            ]
            if invariant_exprs:
                compiled = sum(1 for inv in self.invariants.values() if inv.predicate_fn)
                state.invariants_compiled = compiled / len(invariant_exprs)
            else:
                state.invariants_compiled = 1.0 if not invariant_exprs else 0.0

        # Objectives compiled
        objective_exprs = [
            e for e in self.expressions.values() if e.kind == FormulaClass.OBJECTIVE_FUNCTION
        ]
        if objective_exprs:
            compiled = len(self.objectives)
            state.objectives_compiled = compiled / len(objective_exprs)
        else:
            state.objectives_compiled = 1.0

        # Transitions compiled
        transition_exprs = [
            e for e in self.expressions.values() if e.kind == FormulaClass.TRANSITION_EQUATION
        ]
        if transition_exprs:
            compiled = len(self.transitions)
            state.transitions_compiled = compiled / len(transition_exprs)
        else:
            state.transitions_compiled = 1.0

        # Architecture graph
        state.architecture_graph_built = 1.0 if self.architecture.components else 0.0

        # Proof obligations
        state.proof_obligations_generated = min(
            1.0, len(self.proof_obligations) / max(1, len(self.expressions))
        )

        # Overall integrity
        state.overall_semantic_integrity = (
            state.symbols_resolved * 0.15
            + state.types_resolved * 0.15
            + state.equations_classified * 0.15
            + state.invariants_compiled * 0.15
            + state.objectives_compiled * 0.10
            + state.transitions_compiled * 0.10
            + state.architecture_graph_built * 0.10
            + state.proof_obligations_generated * 0.10
        )

        self.understanding_state = state
        return state

    # ==========================================================================
    # 4.7 Full Compilation Pipeline
    # ==========================================================================

    def compile_formal_system(self, expressions: List[str]) -> Dict[str, Any]:
        """
        Run full semantic compilation pipeline on formal expressions.

        Pipeline:
        parse_formal_text → bind_symbols → compile_operational_semantics →
        [compile_invariant|compile_objective|compile_transition] →
        generate_proof_obligations → evaluate_semantic_integrity
        """
        results: Dict[str, Any] = {
            "expressions": {},
            "invariants": {},
            "objectives": {},
            "transitions": {},
            "proof_obligations": [],
            "understanding_state": None,
        }

        # Phase 1: Parse and bind all expressions
        for i, text in enumerate(expressions):
            expr_id = f"expr_{i}"
            expr = self.parse_formal_text(text, expr_id)
            expr = self.bind_symbols(expr)
            expr = self.compile_operational_semantics(expr)
            results["expressions"][expr_id] = expr

        # Phase 2: Compile specialized forms
        for expr_id, expr in results["expressions"].items():
            if expr.kind == FormulaClass.INVARIANT_RULE:
                inv = self.compile_invariant(expr)
                results["invariants"][inv.id] = inv

            elif expr.kind in (FormulaClass.OBJECTIVE_FUNCTION, FormulaClass.SELECTION_RULE):
                obj = self.compile_objective(expr)
                results["objectives"][obj.id] = obj

            elif expr.kind == FormulaClass.TRANSITION_EQUATION:
                trans = self.compile_transition_rule(expr)
                results["transitions"][trans.id] = trans

        # Phase 3: Generate proof obligations
        obligations = self.generate_proof_obligations()
        results["proof_obligations"] = obligations

        # Phase 4: Evaluate semantic integrity
        state = self.evaluate_semantic_integrity()
        results["understanding_state"] = state

        return results

    def to_dict(self) -> Dict[str, Any]:
        """Export entire formal semantics state as dictionary."""
        return {
            "symbol_table": {
                name: {
                    "name": entry.name,
                    "type": entry.type.name,
                    "role": entry.role.name,
                    "domain": entry.domain,
                    "source": entry.source,
                }
                for name, entry in self.symbol_table.items()
            },
            "expressions": {
                eid: {
                    "id": e.id,
                    "kind": e.kind.name,
                    "raw_text": e.raw_text,
                    "free_symbols": e.free_symbols,
                    "bound_symbols": e.bound_symbols,
                    "type_requirements": {k: v.name for k, v in e.type_requirements.items()},
                    "operational_semantics": {
                        "reads": e.operational_semantics.reads,
                        "writes": e.operational_semantics.writes,
                        "mode": e.operational_semantics.mode,
                    },
                }
                for eid, e in self.expressions.items()
            },
            "invariants": {
                iid: {
                    "id": inv.id,
                    "predicate": inv.predicate,
                    "scope": inv.scope,
                    "severity": inv.severity,
                    "on_violation": inv.on_violation,
                }
                for iid, inv in self.invariants.items()
            },
            "objectives": {
                oid: {
                    "id": obj.id,
                    "optimize_over": obj.optimize_over,
                    "operator": obj.operator,
                    "score_function": obj.score_function,
                    "output": obj.output,
                }
                for oid, obj in self.objectives.items()
            },
            "transitions": {
                tid: {
                    "id": trans.id,
                    "state_in": trans.state_in,
                    "operator": trans.operator,
                    "state_out": trans.state_out,
                    "reads": trans.reads,
                    "writes": trans.writes,
                }
                for tid, trans in self.transitions.items()
            },
            "architecture": {
                "components": [{"id": c.id, "type": c.type} for c in self.architecture.components],
                "edges": [
                    {"source": e.source, "relation": e.relation, "target": e.target}
                    for e in self.architecture.edges
                ],
            },
            "proof_obligations": [
                {
                    "id": po.id,
                    "statement": po.statement,
                    "kind": po.kind,
                    "status": po.status,
                }
                for po in self.proof_obligations
            ],
            "understanding_state": self.understanding_state.to_dict(),
        }


# =============================================================================
# 5. Global Access Functions
# =============================================================================

_kernel_instance: FormalSemanticsKernel | None = None


def get_formal_semantics_kernel() -> FormalSemanticsKernel:
    """Get or create global formal semantics kernel (singleton)."""
    global _kernel_instance
    if _kernel_instance is None:
        _kernel_instance = FormalSemanticsKernel()
    return _kernel_instance


def reset_formal_semantics_kernel() -> None:
    """Reset the global kernel instance."""
    global _kernel_instance
    _kernel_instance = None


# =============================================================================
# 6. Demonstration
# =============================================================================


def demo() -> FormalSemanticsKernel:
    """Demonstrate formal semantics kernel capabilities."""
    kernel = FormalSemanticsKernel()

    # Example equations and invariants from the AMOS specification
    formal_texts = [
        # State definition
        r"\Psi_t = (V_t, E_t, S_t, \Lambda_t)",
        # Objective function
        r"B^\star = \arg\max_{B_i}[Value_i - Risk_i - Cost_i + Control_i]",
        # Invariant
        r"\frac{dDependency}{dt} \le 0",
        # Transition rule
        r"H_{t+1} = Reorganize(H_t \mid Cond_t)",
        # Constraint
        r"Ov_t < \tau_{safe}",
    ]

    print("=" * 70)
    print("AMOS Formal Semantics Kernel - Compilation Demo")
    print("=" * 70)

    # Compile all expressions
    results = kernel.compile_formal_system(formal_texts)

    # Display results
    print("\n📊 FORMAL EXPRESSIONS COMPILED:")
    for expr_id, expr in results["expressions"].items():
        print(f"\n  [{expr_id}] {expr.kind.name}")
        print(f"    Text: {expr.raw_text[:60]}...")
        print(f"    Free symbols: {', '.join(expr.free_symbols)}")
        print(f"    Mode: {expr.operational_semantics.mode}")

    print("\n🔒 INVARIANTS:")
    for inv_id, inv in results["invariants"].items():
        print(f"\n  [{inv_id}]")
        print(f"    Predicate: {inv.predicate}")
        print(f"    Severity: {inv.severity}")
        print(f"    On violation: {inv.on_violation}")

    print("\n🎯 OBJECTIVES:")
    for obj_id, obj in results["objectives"].items():
        print(f"\n  [{obj_id}]")
        print(f"    Optimize: {obj.operator} over {obj.optimize_over}")
        print(f"    Score: {obj.score_function[:60]}...")

    print("\n🔄 TRANSITIONS:")
    for trans_id, trans in results["transitions"].items():
        print(f"\n  [{trans_id}]")
        print(f"    {trans.state_in} --[{trans.operator}]--> {trans.state_out}")

    print("\n📋 PROOF OBLIGATIONS:")
    for po in results["proof_obligations"][:5]:  # Show first 5
        print(f"  [{po.id}] {po.kind}: {po.statement[:50]}...")

    print("\n📈 SEMANTIC INTEGRITY:")
    state = results["understanding_state"]
    for key, value in state.to_dict().items():
        bar = "█" * int(value * 20) + "░" * (20 - int(value * 20))
        print(f"  {key:30} [{bar}] {value * 100:.1f}%")

    print("\n" + "=" * 70)
    print("Formal semantics compilation complete.")
    print("=" * 70)

    return kernel


if __name__ == "__main__":
    demo()
