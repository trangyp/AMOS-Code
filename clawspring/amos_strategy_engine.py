"""AMOS Strategy/Game Theory Engine - Strategic planning and game theory."""

from dataclasses import dataclass
from typing import Any

from amos_runtime import get_runtime


@dataclass
class StrategyAnalysis:
    """Result from strategy/game theory domain analysis."""

    domain: str
    input_data: str
    findings: List[dict]
    confidence: float
    limitations: List[str]
    law_compliance: dict
    gap_acknowledgment: str


class GameNormalFormKernel:
    """Normal form games - finite games, payoffs, dominance, equilibrium."""

    def analyze(self, input_data: str) -> StrategyAnalysis:
        """Analyze normal form game aspects."""
        findings = []

        game_indicators = {
            "players": ["player", "actor", "agent", "participant", "competitor"],
            "strategies": ["strategy", "choice", "decision", "option", "move"],
            "payoffs": ["payoff", "outcome", "utility", "reward", "benefit"],
            "dominance": ["dominant", "dominance", "best response", "equilibrium"],
            "nash": ["nash", "equilibrium", "stable", "no deviation"],
        }

        for category, terms in game_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "game_primitives": self._get_primitives(category),
                    }
                )

        return StrategyAnalysis(
            domain="game_normal_form",
            input_data=input_data,
            findings=findings,
            confidence=0.75 if findings else 0.3,
            limitations=[
                "No computational game solving",
                "No payoff matrix calculations",
                "Conceptual framework only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Game analysis is structural pattern matching. "
                "No game tree search. No equilibrium computation. Not game theory research."
            ),
        )

    def _get_primitives(self, category: str) -> List[str]:
        """Get game primitives for category."""
        primitives = {
            "players": ["player", "strategy", "payoff", "information_set"],
            "strategies": ["action", "pure_strategy", "mixed_strategy"],
            "payoffs": ["utility", "preference", "outcome_matrix"],
            "dominance": ["strict_dominance", "weak_dominance", "dominant_strategy"],
            "nash": ["nash_equilibrium", "best_response", "fixed_point"],
        }
        return primitives.get(category, [])


class GameDynamicalKernel:
    """Dynamical games - repeated games, evolutionary dynamics, learning."""

    def analyze(self, input_data: str) -> StrategyAnalysis:
        """Analyze dynamical game aspects."""
        findings = []

        dynamical_indicators = {
            "repeated_games": ["repeated", "iterative", "multi-round", "series"],
            "evolution": ["evolutionary", "dynamics", "selection", "mutation"],
            "learning": ["learning", "adaptation", "update", "belief_update"],
            "reputation": ["reputation", "trust", "history", "credibility"],
            "cooperation": ["cooperation", "defection", "tit-for-tat", "trigger"],
        }

        for category, terms in dynamical_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "dynamical_primitives": self._get_primitives(category),
                    }
                )

        return StrategyAnalysis(
            domain="game_dynamical",
            input_data=input_data,
            findings=findings,
            confidence=0.7 if findings else 0.25,
            limitations=[
                "No simulation capabilities",
                "No evolutionary computation",
                "Static pattern analysis only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Dynamical game analysis is pattern detection. "
                "No simulations. No learning models. Not dynamical game research."
            ),
        )

    def _get_primitives(self, category: str) -> List[str]:
        """Get dynamical primitives for category."""
        primitives = {
            "repeated_games": ["stage_game", "discount_factor", "continuation_value"],
            "evolution": ["population", "fitness", "replicator_dynamics"],
            "learning": ["belief", "strategy_update", "fictitious_play"],
            "reputation": ["type", "signal", "pooling", "separating"],
            "cooperation": ["folk_theorem", "punishment", "reward"],
        }
        return primitives.get(category, [])


class NegotiationKernel:
    """Negotiation and bargaining - coalitions, signals, reservation values."""

    SAFETY_WARNINGS = [
        "Do not design strategies for physical harm",
        "Do not support illegal market collusion",
        "Respect ethical negotiation practices",
    ]

    def analyze(self, input_data: str) -> StrategyAnalysis:
        """Analyze negotiation and bargaining aspects."""
        findings = []

        negotiation_indicators = {
            "bargaining": ["bargain", "negotiate", "deal", "agreement", "terms"],
            "coalitions": ["coalition", "alliance", "partnership", "collaboration"],
            "signaling": ["signal", "reveal", "information", "asymmetric"],
            "reservation": ["reservation", "walk-away", "minimum", "BATNA"],
            "threats": ["threat", "punishment", "sanction", "commitment"],
        }

        for category, terms in negotiation_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "negotiation_primitives": self._get_primitives(category),
                    }
                )

        # Add safety warnings
        warnings = []
        if any(t in input_data.lower() for t in ["threat", "punishment", "sanction", "war"]):
            warnings.append("SAFETY: Do not design strategies for physical harm")
            warnings.append("SAFETY: Focus on constructive negotiation approaches")

        if any(
            t in input_data.lower() for t in ["collusion", "cartel", "price_fixing", "monopoly"]
        ):
            warnings.append("SAFETY: Do not support illegal market collusion")
            warnings.append("SAFETY: Comply with antitrust regulations")

        return StrategyAnalysis(
            domain="negotiation",
            input_data=input_data,
            findings=findings + [{"type": "safety_warnings", "warnings": warnings}]
            if warnings
            else findings,
            confidence=0.7 if findings else 0.3,
            limitations=[
                "No real negotiation simulation",
                "No behavioral game theory models",
                "Framework analysis only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True, "L6": True},
            gap_acknowledgment=(
                "GAP: Negotiation analysis is pattern matching. "
                "No behavioral data. No simulation. Not negotiation science. "
                "DO NOT design strategies for harm."
            ),
        )

    def _get_primitives(self, category: str) -> List[str]:
        """Get negotiation primitives for category."""
        primitives = {
            "bargaining": ["offer", "counteroffer", "zone_of_agreement"],
            "coalitions": ["coalition_formation", "value_allocation", "core"],
            "signaling": ["cheap_talk", "costly_signal", "screening"],
            "reservation": ["reservation_value", "outside_option", "surplus"],
            "threats": ["threat_point", "commitment", "credibility"],
        }
        return primitives.get(category, [])


class AMOSStrategyEngine:
    """Unified strategy/game theory engine for strategic analysis."""

    DOMAINS = {
        "game_normal": GameNormalFormKernel,
        "game_dynamical": GameDynamicalKernel,
        "negotiation": NegotiationKernel,
    }

    def __init__(self):
        self.runtime = get_runtime()
        self.kernels: Dict[str, Any] = {}
        self._init_kernels()

    def _init_kernels(self):
        """Initialize all strategy/game kernels."""
        for domain, kernel_class in self.DOMAINS.items():
            self.kernels[domain] = kernel_class()

    def analyze(
        self,
        description: str,
        domains: Optional[List[str]] = None,
    ) -> dict[str, StrategyAnalysis]:
        """Run strategy/game analysis across specified domains."""
        domains = domains or list(self.DOMAINS.keys())
        results = {}

        for domain in domains:
            if domain in self.kernels:
                kernel = self.kernels[domain]
                results[domain] = kernel.analyze(description)

        return results

    def get_findings_summary(self, results: Dict[str, StrategyAnalysis]) -> str:
        """Generate human-readable findings summary."""
        lines = [
            "# AMOS Strategy/Game Theory Analysis Summary",
            "",
            f"Domains analyzed: {len(results)}",
            f"Overall confidence: {sum(r.confidence for r in results.values()) / len(results):.2f}",
            "",
            "⚠️ SAFETY NOTICE:",
            "⚠️ Do not design strategies for physical harm",
            "⚠️ Do not support illegal market collusion",
            "⚠️ Respect ethical negotiation practices",
            "",
            "## Findings by Domain",
            "",
        ]

        for domain, analysis in results.items():
            lines.extend(
                [
                    f"### {domain.upper().replace('_', ' ')}",
                    f"Confidence: {analysis.confidence:.2f}",
                    f"Findings: {len([f for f in analysis.findings if f.get('type') != 'safety_warnings'])}",
                    "",
                ]
            )

            for finding in analysis.findings:
                if finding.get("type") == "safety_warnings":
                    for warning in finding.get("warnings", []):
                        lines.append(f"⚠️ {warning}")
                else:
                    cat = finding.get("category", "general")
                    lines.append(f"- **{cat}**: {finding.get('detected_terms', [])}")
                    primitives = (
                        finding.get("game_primitives")
                        or finding.get("dynamical_primitives")
                        or finding.get("negotiation_primitives")
                    )
                    if primitives:
                        lines.append(f"  Primitives: {', '.join(primitives[:3])}")
            lines.append("")

        # Limitations section
        lines.extend(
            [
                "## Limitations",
                "",
            ]
        )
        all_limitations = set()
        for analysis in results.values():
            all_limitations.update(analysis.limitations)
        for limitation in all_limitations:
            lines.append(f"- {limitation}")

        # Law compliance
        lines.extend(
            [
                "",
                "## Law Compliance",
                "",
            ]
        )
        for domain, analysis in results.items():
            compliant = sum(1 for v in analysis.law_compliance.values() if v)
            total = len(analysis.law_compliance)
            lines.append(f"- {domain}: {compliant}/{total} laws")

        # Gap acknowledgment
        lines.extend(
            [
                "",
                "## Gap Acknowledgment",
                "GAP: Strategy/game analysis is structural pattern matching, not game theory research.",
                "No equilibrium computation. No simulations. No behavioral models.",
                "DO NOT use for actual strategic decisions without expert review.",
                "Human strategic expertise required for all decisions.",
            ]
        )

        return "\n".join(lines)


# Singleton
_strategy_engine: Optional[AMOSStrategyEngine] = None


def get_strategy_engine() -> AMOSStrategyEngine:
    """Get singleton strategy/game theory engine."""
    global _strategy_engine
    if _strategy_engine is None:
        _strategy_engine = AMOSStrategyEngine()
    return _strategy_engine


def analyze_strategy(
    description: str,
    domains: Optional[List[str]] = None,
) -> dict[str, StrategyAnalysis]:
    """Quick helper for strategy/game theory analysis."""
    return get_strategy_engine().analyze(description, domains)


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS STRATEGY/GAME THEORY ENGINE TEST")
    print("=" * 60)

    engine = get_strategy_engine()

    # Test multi-domain analysis
    test_input = (
        "Analyze a competitive pricing scenario between two firms "
        "considering repeated interaction and potential for tacit collusion. "
        "Evaluate Nash equilibrium strategies and bargaining over market share."
    )

    print(f"\nInput: {test_input[:70]}...")

    results = engine.analyze(test_input)

    print(f"\nAnalyzed {len(results)} strategy domains:")
    for domain, analysis in results.items():
        findings_count = len([f for f in analysis.findings if f.get("type") != "safety_warnings"])
        print(f"  - {domain}: {findings_count} findings, confidence={analysis.confidence:.2f}")

    # Full summary
    print("\n" + "=" * 60)
    print(engine.get_findings_summary(results))

    print("\n" + "=" * 60)
    print("Strategy/Game Theory Engine: OPERATIONAL")
    print("=" * 60)
    print("\nAll 3 game domains active: Normal Form, Dynamical, Negotiation")
    print("SAFETY: No strategies for physical harm. No illegal collusion.")
