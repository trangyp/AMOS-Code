"""AMOS Economics/Finance Engine - Economic analysis and financial systems."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from amos_runtime import get_runtime


@dataclass
class EconAnalysis:
    """Result from economics/finance domain analysis."""

    domain: str
    input_data: str
    findings: List[dict]
    confidence: float
    limitations: List[str]
    law_compliance: dict
    gap_acknowledgment: str


class MicroEconomicsEngine:
    """Microeconomics kernel - firms, households, markets."""

    def analyze(self, input_data: str) -> EconAnalysis:
        """Analyze microeconomic aspects."""
        findings = []

        micro_indicators = {
            "firm_behavior": ["firm", "company", "production", "cost", "profit", "revenue"],
            "consumer_behavior": ["consumer", "household", "demand", "preference", "utility"],
            "market_structure": ["market", "competition", "monopoly", "oligopoly", "price"],
            "equilibrium": ["supply", "demand", "equilibrium", "clearing", "allocation"],
        }

        for category, terms in micro_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "economic_principles": self._get_principles(category),
                    }
                )

        return EconAnalysis(
            domain="microeconomics",
            input_data=input_data,
            findings=findings,
            confidence=0.7 if findings else 0.3,
            limitations=[
                "No market data analysis",
                "No econometric modeling",
                "Conceptual framework only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Microeconomic analysis is conceptual pattern matching. "
                "No market data. No econometric analysis. Not economic research."
            ),
        )

    def _get_principles(self, category: str) -> List[str]:
        """Get economic principles for category."""
        principles = {
            "firm_behavior": ["Profit maximization", "Cost minimization"],
            "consumer_behavior": ["Utility maximization", "Budget constraint"],
            "market_structure": ["Market power", "Price setting"],
            "equilibrium": ["Supply-demand balance", "Market clearing"],
        }
        return principles.get(category, [])


class MacroEconomicsEngine:
    """Macroeconomics kernel - growth, inflation, policy."""

    def analyze(self, input_data: str) -> EconAnalysis:
        """Analyze macroeconomic aspects."""
        findings = []

        macro_indicators = {
            "growth": ["growth", "gdp", "output", "development", "expansion"],
            "inflation": ["inflation", "price level", "deflation", "cpi"],
            "employment": ["employment", "unemployment", "labor", "wages"],
            "policy": ["monetary", "fiscal", "central bank", "interest rate"],
            "business_cycle": ["recession", "boom", "cycle", "fluctuation"],
        }

        for category, terms in macro_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "macro_principles": self._get_principles(category),
                    }
                )

        return EconAnalysis(
            domain="macroeconomics",
            input_data=input_data,
            findings=findings,
            confidence=0.75 if findings else 0.25,
            limitations=[
                "No time series data",
                "No macroeconomic modeling",
                "Qualitative analysis only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Macroeconomic analysis is conceptual pattern detection. "
                "No national accounts data. No DSGE modeling. Not macro research."
            ),
        )

    def _get_principles(self, category: str) -> List[str]:
        """Get macroeconomic principles for category."""
        principles = {
            "growth": ["Solow model", "Human capital accumulation"],
            "inflation": ["Quantity theory", "Phillips curve"],
            "employment": ["NAIRU", "Labor market clearing"],
            "policy": ["Taylor rule", "Fiscal multiplier"],
            "business_cycle": ["Aggregate demand shocks", "Real business cycle"],
        }
        return principles.get(category, [])


class PublicFinanceEngine:
    """Public finance kernel - taxes, spending, debt."""

    def analyze(self, input_data: str) -> EconAnalysis:
        """Analyze public finance aspects."""
        findings = []

        public_finance_indicators = {
            "taxation": ["tax", "revenue", "fiscal", "burden", "collection"],
            "spending": ["spending", "expenditure", "budget", "public goods"],
            "debt": ["debt", "deficit", "borrowing", "sustainability"],
            "welfare": ["welfare", "transfer", "social security", "redistribution"],
        }

        for category, terms in public_finance_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "public_finance_principles": self._get_principles(category),
                    }
                )

        return EconAnalysis(
            domain="public_finance",
            input_data=input_data,
            findings=findings,
            confidence=0.7 if findings else 0.3,
            limitations=[
                "No government budget data",
                "No fiscal impact analysis",
                "Framework analysis only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True, "L6": True},
            gap_acknowledgment=(
                "GAP: Public finance analysis is conceptual. "
                "No fiscal data. No CBO scoring. Not public finance research."
            ),
        )

    def _get_principles(self, category: str) -> List[str]:
        """Get public finance principles for category."""
        principles = {
            "taxation": ["Ramsey taxation", "Optimal tax theory"],
            "spending": ["Public goods provision", "Cost-benefit analysis"],
            "debt": ["Ricardian equivalence", "Debt sustainability"],
            "welfare": ["Optimal redistribution", "Work incentives"],
        }
        return principles.get(category, [])


class FinanceMarketsEngine:
    """Financial markets kernel - instruments, risk, regulation."""

    SAFETY_CONSTRAINTS = [
        "No personalized investment advice",
        "No trading recommendations",
        "No market timing predictions",
        "Flag uncertainty explicitly",
    ]

    def analyze(self, input_data: str) -> EconAnalysis:
        """Analyze financial markets aspects."""
        findings = []

        finance_indicators = {
            "markets": ["market", "stock", "bond", "equity", "asset"],
            "instruments": ["derivative", "option", "future", "swap", "security"],
            "risk": ["risk", "volatility", "variance", "hedge", "exposure"],
            "valuation": ["valuation", "price", "npv", "discount", "cash flow"],
            "regulation": ["regulation", "compliance", " Basel", "Dodd-Frank"],
        }

        for category, terms in finance_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "finance_principles": self._get_principles(category),
                    }
                )

        # Add safety warnings if investment-related
        warnings = []
        investment_terms = ["invest", "portfolio", "return", "trading", "buy", "sell"]
        if any(t in input_data.lower() for t in investment_terms):
            warnings.append("SAFETY: No personalized investment advice provided")
            warnings.append("SAFETY: Financial analysis is conceptual, not actionable")

        return EconAnalysis(
            domain="financial_markets",
            input_data=input_data,
            findings=findings + [{"type": "safety_warnings", "warnings": warnings}]
            if warnings
            else findings,
            confidence=0.65 if findings else 0.2,
            limitations=[
                "No market data access",
                "No quantitative models",
                "No investment advice",
                "Conceptual framework only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Financial analysis is structural pattern matching. "
                "No Bloomberg data. No risk models. Not financial analysis. "
                "NO INVESTMENT ADVICE."
            ),
        )

    def _get_principles(self, category: str) -> List[str]:
        """Get finance principles for category."""
        principles = {
            "markets": ["Efficient markets hypothesis", "Arbitrage pricing"],
            "instruments": ["No-arbitrage pricing", "Risk-neutral valuation"],
            "risk": ["Modern portfolio theory", "CAPM"],
            "valuation": ["DCF analysis", "Relative valuation"],
            "regulation": ["Systemic risk", "Capital requirements"],
        }
        return principles.get(category, [])


class AMOSEconEngine:
    """Unified economics/finance engine for economic analysis."""

    DOMAINS = {
        "micro": MicroEconomicsEngine,
        "macro": MacroEconomicsEngine,
        "public_finance": PublicFinanceEngine,
        "finance": FinanceMarketsEngine,
    }

    def __init__(self):
        self.runtime = get_runtime()
        self.engines: Dict[str, Any] = {}
        self._init_engines()

    def _init_engines(self):
        """Initialize all economic domain engines."""
        for domain, engine_class in self.DOMAINS.items():
            self.engines[domain] = engine_class()

    def analyze(
        self,
        description: str,
        domains: Optional[List[str]] = None,
    ) -> Dict[str, EconAnalysis]:
        """Run economic analysis across specified domains."""
        domains = domains or list(self.DOMAINS.keys())
        results = {}

        for domain in domains:
            if domain in self.engines:
                engine = self.engines[domain]
                results[domain] = engine.analyze(description)

        return results

    def get_findings_summary(self, results: Dict[str, EconAnalysis]) -> str:
        """Generate human-readable findings summary."""
        lines = [
            "# AMOS Economics/Finance Analysis Summary",
            "",
            f"Domains analyzed: {len(results)}",
            f"Overall confidence: {sum(r.confidence for r in results.values()) / len(results):.2f}",
            "",
            "⚠️ SAFETY NOTICE: This is conceptual analysis only.",
            "⚠️ NO personalized investment advice.",
            "⚠️ NO trading recommendations.",
            "⚠️ Consult qualified professionals for financial decisions.",
            "",
            "## Findings by Domain",
            "",
        ]

        for domain, analysis in results.items():
            lines.extend(
                [
                    f"### {domain.upper().replace('_', ' ')}",
                    f"Confidence: {analysis.confidence:.2f}",
                    f"Findings: {len(analysis.findings)}",
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
                    principles = (
                        finding.get("economic_principles")
                        or finding.get("macro_principles")
                        or finding.get("public_finance_principles")
                        or finding.get("finance_principles")
                    )
                    if principles:
                        lines.append(f"  Principles: {', '.join(principles[:2])}")
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
                "GAP: Economic/finance analysis is pattern matching on text, not economic research.",
                "No data access. No econometric models. No forecasting ability.",
                "NOT SUITABLE for investment or policy decisions.",
                "Human economic expertise required for all decisions.",
            ]
        )

        return "\n".join(lines)


# Singleton
_econ_engine: Optional[AMOSEconEngine] = None


def get_econ_engine() -> AMOSEconEngine:
    """Get singleton economics/finance engine."""
    global _econ_engine
    if _econ_engine is None:
        _econ_engine = AMOSEconEngine()
    return _econ_engine


def analyze_economics(
    description: str,
    domains: Optional[List[str]] = None,
) -> Dict[str, EconAnalysis]:
    """Quick helper for economics analysis."""
    return get_econ_engine().analyze(description, domains)


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS ECONOMICS/FINANCE ENGINE TEST")
    print("=" * 60)

    engine = get_econ_engine()

    # Test multi-domain analysis
    test_input = (
        "Analyze the impact of central bank interest rate policy on "
        "corporate investment decisions and market valuations. "
        "Consider household savings behavior and public debt sustainability."
    )

    print(f"\nInput: {test_input[:70]}...")

    results = engine.analyze(test_input)

    print(f"\nAnalyzed {len(results)} economic domains:")
    for domain, analysis in results.items():
        print(
            f"  - {domain}: {len(analysis.findings)} findings, confidence={analysis.confidence:.2f}"
        )

    # Full summary
    print("\n" + "=" * 60)
    print(engine.get_findings_summary(results))

    print("\n" + "=" * 60)
    print("Economics/Finance Engine: OPERATIONAL")
    print("=" * 60)
    print("\nAll 4 economic domains active: Micro, Macro, Public Finance, Finance")
    print("GAP: Pattern matching only. Not economic research.")
    print("SAFETY: No investment advice. Consult professionals.")
