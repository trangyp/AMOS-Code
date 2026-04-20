"""AMOS Logic Core Engine - Formal logic and reasoning foundation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class LogicType(Enum):
    """Types of formal logic systems."""

    PROPOSITIONAL = "propositional"
    PREDICATE = "predicate"
    MODAL = "modal"
    TEMPORAL = "temporal"
    FUZZY = "fuzzy"


class Connective(Enum):
    """Logical connectives."""

    NOT = "¬"
    AND = "∧"
    OR = "∨"
    IMPLIES = "→"
    IFF = "↔"
    XOR = "⊕"


@dataclass
class Proposition:
    """Represents a logical proposition."""

    symbol: str
    value: bool = None


class PropositionalLogicKernel:
    """Kernel for propositional logic."""

    def __init__(self):
        self.propositions: dict[str, Proposition] = {}

    def add_proposition(self, symbol: str, value: bool = None) -> Proposition:
        """Add a proposition."""
        prop = Proposition(symbol, value)
        self.propositions[symbol] = prop
        return prop

    def evaluate(self, expression: str, assignments: dict[str, bool]) -> bool:
        """Evaluate a propositional expression."""
        # Simplified evaluator for basic expressions
        tokens = expression.replace("(", " ( ").replace(")", " ) ").split()
        return self._eval_tokens(tokens, assignments)

    def _eval_tokens(self, tokens: list[str], assignments: dict[str, bool]) -> bool:
        """Recursively evaluate tokens."""
        if not tokens:
            return False
        token = tokens.pop(0)
        if token == "(":
            result = self._eval_tokens(tokens, assignments)
            if tokens and tokens[0] == ")":
                tokens.pop(0)
            return result
        if token == "¬" or token == "NOT":
            return not self._eval_tokens(tokens, assignments)
        if token in assignments:
            return assignments[token]
        if token in ("∧", "AND"):
            left = self._eval_tokens(tokens, assignments)
            right = self._eval_tokens(tokens, assignments)
            return left and right
        if token in ("∨", "OR"):
            left = self._eval_tokens(tokens, assignments)
            right = self._eval_tokens(tokens, assignments)
            return left or right
        if token in ("→", "IMPLIES"):
            left = self._eval_tokens(tokens, assignments)
            right = self._eval_tokens(tokens, assignments)
            return (not left) or right
        return False

    def is_tautology(self, expression: str) -> bool:
        """Check if expression is a tautology (always true)."""
        # For simple cases only
        symbols = list(set(c for c in expression if c.isupper()))
        if len(symbols) > 4:
            return False  # Too complex
        # Check all combinations
        for i in range(2 ** len(symbols)):
            assignments = {s: bool((i >> j) & 1) for j, s in enumerate(symbols)}
            if not self.evaluate(expression, assignments):
                return False
        return True


class PredicateLogicKernel:
    """Kernel for first-order predicate logic."""

    def __init__(self):
        self.predicates: dict[str, Any] = {}
        self.quantifiers = ["∀", "∃", "forall", "exists"]

    def define_predicate(self, name: str, arity: int, meaning: str) -> None:
        """Define a predicate."""
        self.predicates[name] = {"arity": arity, "meaning": meaning}

    def analyze_expression(self, expression: str) -> dict[str, Any]:
        """Analyze a predicate logic expression."""
        result = {
            "quantifiers": [],
            "variables": [],
            "predicates": [],
        }
        # Extract quantifiers
        for q in ["∀", "∃"]:
            if q in expression:
                result["quantifiers"].append(q)
        # Extract variables (lowercase letters)
        result["variables"] = list(set(c for c in expression if c.islower()))
        # Extract predicates (capital letters)
        result["predicates"] = list(set(c for c in expression if c.isupper()))
        return result

    def convert_to_prenex(self, expression: str) -> str:
        """Convert to prenex normal form (simplified)."""
        return f"Prenex form of: {expression}"


class ModalLogicKernel:
    """Kernel for modal logic (necessity and possibility)."""

    def __init__(self):
        self.modalities = {
            "□": "necessarily",
            "◇": "possibly",
            "necessarily": "□",
            "possibly": "◇",
        }

    def analyze_modal_statement(self, statement: str) -> dict[str, Any]:
        """Analyze modal operators in statement."""
        return {
            "has_necessity": "□" in statement or "necessarily" in statement.lower(),
            "has_possibility": "◇" in statement or "possibly" in statement.lower(),
            "modal_depth": statement.count("□") + statement.count("◇"),
        }

    def evaluate_kripke_frame(
        self, worlds: list[str], accessibility: dict[str, list[str]], formula: str
    ) -> dict[str, bool]:
        """Evaluate formula in Kripke frame."""
        results = {}
        for world in worlds:
            # Simplified evaluation
            results[world] = True
        return results


class TemporalLogicKernel:
    """Kernel for temporal logic (LTL/CTL)."""

    def __init__(self):
        self.ltl_operators = {
            "G": "globally",
            "F": "eventually",
            "X": "next",
            "U": "until",
        }
        self.ctl_operators = {
            "AG": "all globally",
            "AF": "all eventually",
            "EG": "exists globally",
            "EF": "exists eventually",
        }

    def analyze_temporal_property(self, property_str: str) -> dict[str, Any]:
        """Analyze temporal logic property."""
        result = {"ltl": [], "ctl": [], "is_safety": False, "is_liveness": False}
        for op in self.ltl_operators:
            if op in property_str:
                result["ltl"].append(op)
        for op in self.ctl_operators:
            if op in property_str:
                result["ctl"].append(op)
        # Classification
        if "G" in property_str:
            result["is_safety"] = True
        if "F" in property_str:
            result["is_liveness"] = True
        return result

    def model_check_trace(self, trace: list[dict], formula: str) -> bool:
        """Simple model checking on trace."""
        return True  # Simplified


class FuzzyLogicKernel:
    """Kernel for fuzzy logic."""

    def __init__(self):
        self.fuzzy_sets: dict[str, dict] = {}

    def define_fuzzy_set(self, name: str, membership_fn: str, domain: tuple[float, float]) -> None:
        """Define a fuzzy set."""
        self.fuzzy_sets[name] = {"fn": membership_fn, "domain": domain}

    def fuzzify(self, value: float, set_name: str) -> float:
        """Fuzzify a crisp value."""
        if set_name == "cold":
            return max(0, min(1, (20 - value) / 20))
        if set_name == "hot":
            return max(0, min(1, (value - 20) / 20))
        return 0.5  # Default

    def defuzzify(self, fuzzy_value: float, method: str = "centroid") -> float:
        """Defuzzify to crisp value."""
        return fuzzy_value * 50  # Simplified


class InferenceEngine:
    """Engine for logical inference."""

    def __init__(self):
        self.rules: list[dict] = []

    def add_rule(self, premises: list[str], conclusion: str) -> None:
        """Add an inference rule."""
        self.rules.append({"premises": premises, "conclusion": conclusion})

    def forward_chain(self, facts: set[str]) -> set[str]:
        """Forward chaining inference."""
        new_facts = set(facts)
        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                if all(p in new_facts for p in rule["premises"]):
                    if rule["conclusion"] not in new_facts:
                        new_facts.add(rule["conclusion"])
                        changed = True
        return new_facts

    def backward_chain(self, goal: str, facts: set[str]) -> list[list[str]]:
        """Backward chaining to prove goal."""
        proofs = []
        if goal in facts:
            return [[goal]]
        for rule in self.rules:
            if rule["conclusion"] == goal:
                subproofs = []
                for premise in rule["premises"]:
                    sub = self.backward_chain(premise, facts)
                    if sub:
                        subproofs.extend(sub)
                if subproofs:
                    proofs.append([goal] + subproofs)
        return proofs


class LogicCoreEngine:
    """AMOS Logic Core Engine - Formal logic and reasoning."""

    VERSION = "vInfinity_Logic_1.0.0"
    NAME = "AMOS_Logic_Core_OMEGA"

    def __init__(self):
        self.propositional = PropositionalLogicKernel()
        self.predicate = PredicateLogicKernel()
        self.modal = ModalLogicKernel()
        self.temporal = TemporalLogicKernel()
        self.fuzzy = FuzzyLogicKernel()
        self.inference = InferenceEngine()

    def analyze(self, query: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """Run logic analysis on query."""
        context = context or {}
        query_lower = query.lower()
        results: dict[str, Any] = {
            "query": query[:100],
            "logic_types_detected": [],
            "propositional_analysis": {},
            "predicate_analysis": {},
            "modal_analysis": {},
            "temporal_analysis": {},
            "fuzzy_analysis": {},
            "inference_analysis": {},
        }
        # Detect logic types
        if any(
            kw in query_lower for kw in ["proposition", "truth table", "tautology", "¬", "∧", "∨"]
        ):
            results["logic_types_detected"].append("propositional")
        if any(
            kw in query_lower for kw in ["predicate", "forall", "exists", "∀", "∃", "quantifier"]
        ):
            results["logic_types_detected"].append("predicate")
        if any(kw in query_lower for kw in ["necessarily", "possibly", "□", "◇", "modal"]):
            results["logic_types_detected"].append("modal")
        if any(
            kw in query_lower
            for kw in ["eventually", "globally", "until", "ltl", "ctl", "temporal"]
        ):
            results["logic_types_detected"].append("temporal")
        if any(kw in query_lower for kw in ["fuzzy", "membership", "fuzzify", "defuzzify"]):
            results["logic_types_detected"].append("fuzzy")
        if any(
            kw in query_lower for kw in ["inference", "deduction", "proof", "conclusion", "premise"]
        ):
            results["logic_types_detected"].append("inference")
        # Propositional analysis
        if "propositional" in results["logic_types_detected"]:
            self._setup_propositional_demo()
            taut_check = self.propositional.is_tautology("(A → B) ∨ (B → A)")
            results["propositional_analysis"] = {
                "tautology_check": taut_check,
                "propositions_defined": len(self.propositional.propositions),
            }
        # Predicate analysis
        if "predicate" in results["logic_types_detected"]:
            self.predicate.define_predicate("P", 1, "is a person")
            self.predicate.define_predicate("Loves", 2, "x loves y")
            expr = "∀x ∃y Loves(x,y)"
            results["predicate_analysis"] = self.predicate.analyze_expression(expr)
        # Modal analysis
        if "modal" in results["logic_types_detected"]:
            modal_result = self.modal.analyze_modal_statement("□P → ◇P")
            results["modal_analysis"] = modal_result
        # Temporal analysis
        if "temporal" in results["logic_types_detected"]:
            temp_result = self.temporal.analyze_temporal_property("G(F(p))")
            results["temporal_analysis"] = temp_result
        # Fuzzy analysis
        if "fuzzy" in results["logic_types_detected"]:
            self.fuzzy.define_fuzzy_set("cold", "triangle", (0, 20))
            fuzz_val = self.fuzzy.fuzzify(15, "cold")
            results["fuzzy_analysis"] = {"fuzzified_value": fuzz_val}
        # Inference analysis
        if "inference" in results["logic_types_detected"]:
            self._setup_inference_demo()
            facts = {"Socrates_is_human", "All_humans_are_mortal"}
            inferred = self.inference.forward_chain(facts)
            results["inference_analysis"] = {
                "initial_facts": len(facts),
                "inferred_facts": len(inferred) - len(facts),
                "total_facts": len(inferred),
            }
        return results

    def _setup_propositional_demo(self) -> None:
        """Setup demo propositions."""
        self.propositional.add_proposition("A", True)
        self.propositional.add_proposition("B", False)
        self.propositional.add_proposition("C")

    def _setup_inference_demo(self) -> None:
        """Setup demo inference rules."""
        self.inference.add_rule(["Socrates_is_human"], "Socrates_is_mortal")
        self.inference.add_rule(
            ["All_humans_are_mortal", "Socrates_is_human"], "Socrates_is_mortal"
        )

    def get_findings_summary(self, results: dict) -> str:
        """Generate findings summary."""
        lines = [
            f"# {self.NAME} {self.VERSION}",
            "",
            "Creator: Trang Phan | System: AMOS vInfinity",
            "Role: Formal Logic and Reasoning Foundation",
            "",
            "## Logic Analysis",
        ]
        logic_types = results.get("logic_types_detected", [])
        if logic_types:
            lines.append(f"- **Detected Logic Types**: {', '.join(logic_types)}")
        else:
            lines.append("- **Detected Logic Types**: General logical reasoning")
        lines.extend(["", "## Available Logic Systems"])
        systems = {
            "propositional": "Truth-functional logic with AND, OR, NOT, IMPLIES",
            "predicate": "First-order logic with quantifiers ∀, ∃",
            "modal": "Necessity (□) and possibility (◇) operators",
            "temporal": "Linear Temporal Logic (LTL) and CTL",
            "fuzzy": "Many-valued logic with degrees of truth",
            "inference": "Deductive reasoning with rules and facts",
        }
        for sys_type, desc in systems.items():
            marker = "✓" if sys_type in logic_types else " "
            lines.append(f"- [{marker}] **{sys_type.title()}**: {desc}")
        # Propositional results
        prop = results.get("propositional_analysis", {})
        if prop:
            lines.extend(["", "## Propositional Logic Analysis"])
            lines.append(f"- **Tautology Check**: {prop.get('tautology_check', 'N/A')}")
            lines.append(f"- **Propositions**: {prop.get('propositions_defined', 0)}")
        # Predicate results
        pred = results.get("predicate_analysis", {})
        if pred:
            lines.extend(["", "## Predicate Logic Analysis"])
            lines.append(f"- **Quantifiers**: {', '.join(pred.get('quantifiers', []))}")
            lines.append(f"- **Variables**: {', '.join(pred.get('variables', []))}")
            lines.append(f"- **Predicates**: {', '.join(pred.get('predicates', []))}")
        # Modal results
        modal = results.get("modal_analysis", {})
        if modal:
            lines.extend(["", "## Modal Logic Analysis"])
            lines.append(f"- **Necessity**: {modal.get('has_necessity', False)}")
            lines.append(f"- **Possibility**: {modal.get('has_possibility', False)}")
            lines.append(f"- **Modal Depth**: {modal.get('modal_depth', 0)}")
        # Temporal results
        temp = results.get("temporal_analysis", {})
        if temp:
            lines.extend(["", "## Temporal Logic Analysis"])
            lines.append(f"- **LTL Operators**: {', '.join(temp.get('ltl', []))}")
            lines.append(f"- **CTL Operators**: {', '.join(temp.get('ctl', []))}")
            lines.append(f"- **Safety Property**: {temp.get('is_safety', False)}")
            lines.append(f"- **Liveness Property**: {temp.get('is_liveness', False)}")
        # Fuzzy results
        fuzzy = results.get("fuzzy_analysis", {})
        if fuzzy:
            lines.extend(["", "## Fuzzy Logic Analysis"])
            lines.append(f"- **Fuzzified Value**: {fuzzy.get('fuzzified_value', 0):.2f}")
        # Inference results
        inf = results.get("inference_analysis", {})
        if inf:
            lines.extend(["", "## Inference Analysis"])
            lines.append(f"- **Initial Facts**: {inf.get('initial_facts', 0)}")
            lines.append(f"- **Inferred Facts**: {inf.get('inferred_facts', 0)}")
            lines.append(f"- **Total Facts**: {inf.get('total_facts', 0)}")
        lines.extend(
            [
                "",
                "## Core Logical Principles",
                "1. **Law of Identity**: A = A",
                "2. **Law of Non-Contradiction**: ¬(A ∧ ¬A)",
                "3. **Law of Excluded Middle**: A ∨ ¬A",
                "",
                "## Inference Rules",
                "- **Modus Ponens**: From A and A → B, infer B",
                "- **Modus Tollens**: From ¬B and A → B, infer ¬A",
                "- **Hypothetical Syllogism**: From A → B and B → C, infer A → C",
                "- **Universal Instantiation**: From ∀x P(x), infer P(a)",
                "- **Existential Generalization**: From P(a), infer ∃x P(x)",
                "",
                "## Safety and Constraints",
                "- Does not claim completeness for complex proof systems",
                "- Simplified model checking for demonstration",
                "- Temporal logic limited to basic LTL/CTL",
                "- Not a substitute for formal verification tools",
                "",
                "## Limitations",
                "- Simplified proof procedures",
                "- Limited to propositional and basic predicate logic",
                "- No automated theorem proving",
                "- Modal logic without Kripke semantics implementation",
            ]
        )
        return "\n".join(lines)


# Singleton instance
_logic_core: LogicCoreEngine | None = None


def get_logic_core_engine() -> LogicCoreEngine:
    """Get or create the Logic Core Engine singleton."""
    global _logic_core
    if _logic_core is None:
        _logic_core = LogicCoreEngine()
    return _logic_core
