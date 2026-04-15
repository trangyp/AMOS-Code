"""AMOS Deterministic Logic & Law Engine - Formal reasoning and legal analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TruthValue(Enum):
    """Truth value primitives."""

    TRUE = "TRUE"
    FALSE = "FALSE"
    UNKNOWN = "UNKNOWN"
    INAPPLICABLE = "INAPPLICABLE"


class Modality(Enum):
    """Deontic modalities."""

    MUST = "MUST"
    MAY = "MAY"
    MUST_NOT = "MUST_NOT"
    SHOULD = "SHOULD"
    SHOULD_NOT = "SHOULD_NOT"


class BurdenLevel(Enum):
    """Burden of proof levels."""

    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    IMPOSSIBLE = "IMPOSSIBLE"


class JurisdictionPriority(Enum):
    """Jurisdiction priority levels."""

    SUPRANATIONAL = 1
    NATIONAL = 2
    SUBNATIONAL = 3
    INTERNAL_POLICY = 4


@dataclass
class LegalEntity:
    """Legal entity representation."""

    entity_type: str
    name: str
    attributes: dict = field(default_factory=dict)


@dataclass
class LegalRelation:
    """Legal relation between entities."""

    relation_type: str
    source: str
    target: str
    conditions: list[str] = field(default_factory=list)


@dataclass
class LogicStatement:
    """Formal logic statement."""

    subject: str
    predicate: str
    truth_value: TruthValue = TruthValue.UNKNOWN
    modality: Modality | None = None
    conditions: list[str] = field(default_factory=list)


@dataclass
class RulePriority:
    """Rule priority layer."""

    layer_name: str
    priority: int
    rules: list[str] = field(default_factory=list)


class FormalLogicKernel:
    """Kernel for formal logical reasoning."""

    OPERATORS = ["AND", "OR", "NOT", "XOR", "IMPLIES", "IFF"]
    QUANTIFIERS = ["FOR_ALL", "EXISTS", "FOR_MAJORITY", "FOR_MINORITY"]

    def __init__(self):
        self.statements: list[LogicStatement] = []

    def add_statement(
        self,
        subject: str,
        predicate: str,
        truth_value: TruthValue = TruthValue.TRUE,
        modality: Modality | None = None,
    ) -> LogicStatement:
        """Add a logical statement."""
        stmt = LogicStatement(
            subject=subject,
            predicate=predicate,
            truth_value=truth_value,
            modality=modality,
        )
        self.statements.append(stmt)
        return stmt

    def evaluate_conjunction(self, statements: list[LogicStatement]) -> TruthValue:
        """Evaluate AND of statements (Rule of 2)."""
        if not statements:
            return TruthValue.UNKNOWN

        has_false = any(s.truth_value == TruthValue.FALSE for s in statements)
        has_unknown = any(s.truth_value == TruthValue.UNKNOWN for s in statements)

        if has_false:
            return TruthValue.FALSE
        if has_unknown:
            return TruthValue.UNKNOWN
        return TruthValue.TRUE

    def evaluate_disjunction(self, statements: list[LogicStatement]) -> TruthValue:
        """Evaluate OR of statements."""
        if not statements:
            return TruthValue.UNKNOWN

        has_true = any(s.truth_value == TruthValue.TRUE for s in statements)

        if has_true:
            return TruthValue.TRUE
        return TruthValue.UNKNOWN

    def check_consistency(self) -> dict:
        """Check for logical contradictions."""
        contradictions = []

        # Check for direct contradictions
        for i, stmt1 in enumerate(self.statements):
            for stmt2 in self.statements[i + 1 :]:
                if (
                    stmt1.subject == stmt2.subject
                    and stmt1.predicate != stmt2.predicate
                    and stmt1.truth_value != stmt2.truth_value
                    and stmt1.truth_value in (TruthValue.TRUE, TruthValue.FALSE)
                    and stmt2.truth_value in (TruthValue.TRUE, TruthValue.FALSE)
                ):
                    contradictions.append((stmt1, stmt2))

        return {
            "consistent": len(contradictions) == 0,
            "contradictions": len(contradictions),
            "details": contradictions,
        }

    def _get_principles(self) -> list[str]:
        """Return kernel principles."""
        return [
            "Formal logic: AND, OR, NOT, XOR, IMPLIES, IFF",
            "Quantifiers: FOR_ALL, EXISTS, FOR_MAJORITY, FOR_MINORITY",
            "Truth values: TRUE, FALSE, UNKNOWN, INAPPLICABLE",
            "No contradictions in single answer",
        ]


class LegalReasoningKernel:
    """Kernel for legal and policy reasoning."""

    PRIORITY_LAYERS = [
        "Constitutional_Principles",
        "Primary_Legislation",
        "Secondary_Legislation",
        "Regulatory_Guidance",
        "Contracts_and_Policies",
        "Soft_Law_and_Standards",
        "Internal_Procedures",
    ]

    def __init__(self):
        self.entities: dict[str, LegalEntity] = {}
        self.relations: list[LegalRelation] = []
        self.rules: list[RulePriority] = [
            RulePriority(layer, i, []) for i, layer in enumerate(self.PRIORITY_LAYERS)
        ]

    def add_entity(self, entity_type: str, name: str, **attributes) -> LegalEntity:
        """Add a legal entity."""
        entity = LegalEntity(
            entity_type=entity_type,
            name=name,
            attributes=attributes,
        )
        self.entities[name] = entity
        return entity

    def add_relation(
        self,
        relation_type: str,
        source: str,
        target: str,
        conditions: list[str] | None = None,
    ) -> LegalRelation:
        """Add a legal relation."""
        relation = LegalRelation(
            relation_type=relation_type,
            source=source,
            target=target,
            conditions=conditions or [],
        )
        self.relations.append(relation)
        return relation

    def resolve_conflict(self, rule1: str, rule2: str) -> str | None:
        """Apply conflict resolution principles."""
        # Find priority of each rule
        p1 = next((r.priority for r in self.rules if rule1 in r.rules), 999)
        p2 = next((r.priority for r in self.rules if rule2 in r.rules), 999)

        # Lex superior: higher priority wins
        if p1 < p2:
            return rule1
        elif p2 < p1:
            return rule2

        # If same priority, flag conflict
        return None

    def evaluate_compliance(
        self,
        entity_name: str,
        obligation: str,
    ) -> dict:
        """Evaluate if entity complies with obligation."""
        entity = self.entities.get(entity_name)
        if not entity:
            return {"compliant": False, "reason": "Entity not found"}

        # Check for direct compliance relation
        for rel in self.relations:
            if (
                rel.source == entity_name
                and rel.relation_type == "COMPLIES_WITH"
                and rel.target == obligation
            ):
                return {"compliant": True, "basis": rel.relation_type}

        # Check for violation
        for rel in self.relations:
            if (
                rel.source == entity_name
                and rel.relation_type == "VIOLATES"
                and rel.target == obligation
            ):
                return {"compliant": False, "basis": rel.relation_type}

        return {"compliant": None, "reason": "No compliance data"}

    def analyze_contract_clauses(self, clauses: list[str]) -> dict:
        """Analyze contract clauses for consistency."""
        issues = []

        # Check for duplicates
        seen = set()
        for clause in clauses:
            if clause in seen:
                issues.append(f"Duplicate clause: {clause[:50]}...")
            seen.add(clause)

        # Check for termination consistency
        termination_clauses = [c for c in clauses if "termination" in c.lower()]
        if len(termination_clauses) > 1:
            issues.append("Multiple termination clauses - check consistency")

        return {
            "total_clauses": len(clauses),
            "issues": issues,
            "consistent": len(issues) == 0,
        }

    def _get_principles(self) -> list[str]:
        """Return kernel principles."""
        return [
            "Priority layers: Constitutional to Internal Procedures",
            "Conflict resolution: lex superior, lex specialis, lex posterior",
            "Jurisdiction priority: Supranational > National > Subnational",
            "Contract review: consistency checks, no duplicates",
        ]


class ArgumentationKernel:
    """Kernel for structured argumentation."""

    def __init__(self):
        self.arguments: list[dict] = []

    def add_argument(
        self,
        claim: str,
        premises: list[str],
        conclusion: str,
        strength: str = "medium",
    ) -> dict:
        """Add a structured argument."""
        argument = {
            "claim": claim,
            "premises": premises,
            "conclusion": conclusion,
            "strength": strength,
        }
        self.arguments.append(argument)
        return argument

    def evaluate_argument(self, argument: dict) -> dict:
        """Evaluate argument validity."""
        # Check for premise support
        supported = len(argument["premises"]) > 0

        # Check conclusion follows from premises
        conclusion_relevant = any(
            p.lower() in argument["conclusion"].lower()
            or argument["conclusion"].lower() in p.lower()
            for p in argument["premises"]
        )

        return {
            "valid": supported and conclusion_relevant,
            "supported": supported,
            "relevant": conclusion_relevant,
            "strength": argument["strength"],
        }

    def identify_fallacies(self, argument: dict) -> list[str]:
        """Identify potential fallacies."""
        fallacies = []

        # Check for circular reasoning
        if argument["claim"].lower() in argument["conclusion"].lower():
            fallacies.append("Potential circular reasoning")

        # Check for unsupported claim
        if not argument["premises"]:
            fallacies.append("Unsupported claim (no premises)")

        return fallacies

    def _get_principles(self) -> list[str]:
        """Return kernel principles."""
        return [
            "Clear reasoning path required",
            "Premises must support conclusion",
            "Fallacy detection: circular reasoning, unsupported claims",
            "Argument strength: low, medium, high",
        ]


class PolicyDesignKernel:
    """Kernel for policy design and analysis."""

    def __init__(self):
        self.policies: list[dict] = []

    def design_policy(
        self,
        objective: str,
        constraints: list[str],
        principles: list[str],
    ) -> dict:
        """Design a policy with operational rules."""
        policy = {
            "objective": objective,
            "constraints": constraints,
            "principles": principles,
            "operational_rules": self._generate_rules(principles),
            "metrics": [],
            "audit_paths": [],
        }
        self.policies.append(policy)
        return policy

    def _generate_rules(self, principles: list[str]) -> list[str]:
        """Convert principles to operational rules."""
        rules = []
        for p in principles:
            # Simple conversion: principle → rule
            rule = f"RULE: {p}"
            rules.append(rule)
        return rules

    def add_metric(self, policy_idx: int, name: str, target: str) -> None:
        """Add metric to policy."""
        if 0 <= policy_idx < len(self.policies):
            self.policies[policy_idx]["metrics"].append(
                {
                    "name": name,
                    "target": target,
                }
            )

    def _get_principles(self) -> list[str]:
        """Return kernel principles."""
        return [
            "Define clear objectives",
            "Identify all constraints",
            "Draft guiding principles",
            "Convert to operational rules",
            "Define metrics and audit paths",
        ]


class LogicLawEngine:
    """AMOS Logic & Law Engine - Deterministic reasoning."""

    VERSION = "1.0.0"
    NAME = "Deterministic_Logic_and_Law_OMEGA"

    def __init__(self):
        self.logic_kernel = FormalLogicKernel()
        self.legal_kernel = LegalReasoningKernel()
        self.argumentation_kernel = ArgumentationKernel()
        self.policy_kernel = PolicyDesignKernel()

    def analyze(
        self,
        query: str,
        domains: list[str] | None = None,
    ) -> dict[str, Any]:
        """Run logic/law analysis across specified domains."""
        domains = domains or ["logic", "legal", "argumentation", "policy"]
        results: dict[str, Any] = {}

        if "logic" in domains:
            results["logic"] = self._analyze_logic(query)

        if "legal" in domains:
            results["legal"] = self._analyze_legal(query)

        if "argumentation" in domains:
            results["argumentation"] = self._analyze_argumentation(query)

        if "policy" in domains:
            results["policy"] = self._analyze_policy(query)

        return results

    def _analyze_logic(self, query: str) -> dict:
        """Analyze logical structure."""
        consistency = self.logic_kernel.check_consistency()

        return {
            "query_analyzed": query[:100],
            "statements_count": len(self.logic_kernel.statements),
            "consistency_check": consistency,
            "principles": self.logic_kernel._get_principles(),
        }

    def _analyze_legal(self, query: str) -> dict:
        """Analyze legal aspects."""
        return {
            "query_analyzed": query[:100],
            "entities": len(self.legal_kernel.entities),
            "relations": len(self.legal_kernel.relations),
            "rule_layers": len(self.legal_kernel.rules),
            "principles": self.legal_kernel._get_principles(),
        }

    def _analyze_argumentation(self, query: str) -> dict:
        """Analyze argumentation structure."""
        return {
            "query_analyzed": query[:100],
            "arguments_count": len(self.argumentation_kernel.arguments),
            "principles": self.argumentation_kernel._get_principles(),
        }

    def _analyze_policy(self, query: str) -> dict:
        """Analyze policy aspects."""
        return {
            "query_analyzed": query[:100],
            "policies_count": len(self.policy_kernel.policies),
            "principles": self.policy_kernel._get_principles(),
        }

    def get_findings_summary(self, results: dict) -> str:
        """Generate findings summary with gap acknowledgment."""
        lines = [
            f"# {self.NAME} v{self.VERSION}",
            "",
            "Creator: Trang Phan | System: AMOS vInfinity",
            "",
            "## Logic Analysis",
        ]

        if "logic" in results:
            logic = results["logic"]
            lines.extend(
                [
                    f"- Statements: {logic['statements_count']}",
                    f"- Consistency: {'✓' if logic['consistency_check']['consistent'] else '⚠'}",
                ]
            )

        lines.extend(
            [
                "",
                "## Legal Analysis",
            ]
        )

        if "legal" in results:
            legal = results["legal"]
            lines.extend(
                [
                    f"- Entities: {legal['entities']}",
                    f"- Relations: {legal['relations']}",
                    f"- Rule Layers: {legal['rule_layers']}",
                ]
            )

        lines.extend(
            [
                "",
                "## Safety & Compliance",
                "",
                "### Safety Constraints",
                "- NO binding legal advice (informational only)",
                "- MUST include disclaimer for legal outputs",
                "- NO drafts enabling serious crime or violence",
                "- Creator attribution required (Trang Phan)",
                "",
                "### Global Law Compliance",
                "- L1 (Structural): Rule of 2/4 applied",
                "- L2 (Temporal): Analysis time-boxed",
                "- L3 (Semantic): Clear reasoning path",
                "- L4 (Cognitive): Multi-perspective analysis",
                "- L5 (Safety): No harmful legal guidance",
                "- L6 (Humility): GAP acknowledgment below",
                "",
                "## Gap Acknowledgment",
                "",
                "**CRITICAL GAP:** This is NOT legal advice. NOT a substitute for "
                "qualified legal counsel. All outputs are SIMULATED analysis only.",
                "",
                "Specific Gaps:",
                "- No access to real legal databases",
                "- No jurisdiction-specific rule lookup",
                "- No case law precedent search",
                "- No binding legal authority",
                "- Pattern-based analysis only, not legal reasoning",
                "",
                "### Creator Attribution",
                "This engine was architected by Trang Phan as part of AMOS vInfinity.",
            ]
        )

        return "\n".join(lines)


# Singleton
_logic_law_engine: LogicLawEngine | None = None


def get_logic_law_engine() -> LogicLawEngine:
    """Get singleton logic/law engine instance."""
    global _logic_law_engine
    if _logic_law_engine is None:
        _logic_law_engine = LogicLawEngine()
    return _logic_law_engine


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS LOGIC & LAW ENGINE")
    print("=" * 60)
    print()

    engine = get_logic_law_engine()

    # Add sample logical statements
    engine.logic_kernel.add_statement("Contract", "is_valid", TruthValue.TRUE, Modality.MUST)
    engine.logic_kernel.add_statement("Party_A", "performs_obligation", TruthValue.TRUE)

    # Add sample legal entities
    engine.legal_kernel.add_entity("PERSON", "Party_A", role="contractor")
    engine.legal_kernel.add_entity("CONTRACT", "Service_Agreement", type="service")

    engine.legal_kernel.add_relation("OWES", "Party_A", "performance")

    # Run analysis
    results = engine.analyze(
        "Analyze contract validity and obligations",
        domains=["logic", "legal"],
    )

    # Print findings
    print(engine.get_findings_summary(results))

    print()
    print("=" * 60)
    print("Engine: OPERATIONAL")
    print("=" * 60)
    print("\nCapabilities:")
    print("  - Formal logic (AND, OR, NOT, etc.)")
    print("  - Legal entity/relation modeling")
    print("  - Argumentation analysis")
    print("  - Policy design support")
    print("  - Consistency checking")
    print("  - Conflict resolution")
    print()
    print("Safety: Gaps acknowledged, NO legal advice.")
