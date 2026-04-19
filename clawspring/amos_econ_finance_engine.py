"""AMOS Economics & Finance Engine - Market and financial analysis."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EconFinanceDomain(Enum):
    """Economics and finance domain classifications."""
    MICRO = "micro"
    MACRO = "macro"
    PUBLIC_FINANCE = "public_finance"
    FINANCIAL_SYSTEM = "financial_system"


@dataclass
class EconomicEntity:
    """Economic entity representation."""

    name: str
    entity_type: str
    domain: EconFinanceDomain
    parameters: dict = field(default_factory=dict)


class MicroEconomicsKernel:
    """Kernel for microeconomic analysis."""

    def __init__(self):
        self.firms: List[dict] = []
        self.households: List[dict] = []
        self.markets: List[dict] = []

    def add_firm(
        self, name: str, industry: str, employees: int, revenue_m: float
    ) -> dict:
        """Add firm."""
        firm = {
            "name": name,
            "industry": industry,
            "employees": employees,
            "revenue_m": revenue_m,
        }
        self.firms.append(firm)
        return firm

    def add_household(self, name: str, income_k: float, size: int) -> dict:
        """Add household."""
        household = {
            "name": name,
            "income_k": income_k,
            "size": size,
        }
        self.households.append(household)
        return household

    def add_market(self, name: str, market_type: str, participants: int) -> dict:
        """Add market."""
        market = {
            "name": name,
            "type": market_type,
            "participants": participants,
        }
        self.markets.append(market)
        return market

    def calculate_elasticity(
        self, pct_change_quantity: float, pct_change_price: float
    ) -> dict:
        """Calculate price elasticity."""
        if pct_change_price == 0:
            return {"error": "Zero price change"}
        elasticity = pct_change_quantity / pct_change_price
        return {
            "pct_change_quantity": pct_change_quantity,
            "pct_change_price": pct_change_price,
            "elasticity": elasticity,
            "elastic": abs(elasticity) > 1,
        }

    def get_principles(self) -> List[str]:
        return [
            "Supply and demand equilibrium",
            "Consumer choice theory",
            "Production and costs",
            "Market structures",
        ]


class MacroEconomicsKernel:
    """Kernel for macroeconomic analysis."""

    def __init__(self):
        self.countries: List[dict] = []
        self.indicators: List[dict] = []

    def add_country(
        self, name: str, gdp_b: float, population_m: float, currency: str
    ) -> dict:
        """Add country economy."""
        country = {
            "name": name,
            "gdp_b": gdp_b,
            "population_m": population_m,
            "currency": currency,
            "gdp_per_capita": (gdp_b * 1000) / population_m if population_m > 0 else 0,
        }
        self.countries.append(country)
        return country

    def add_indicator(self, name: str, value: float, unit: str) -> dict:
        """Add economic indicator."""
        indicator = {"name": name, "value": value, "unit": unit}
        self.indicators.append(indicator)
        return indicator

    def calculate_growth_rate(self, gdp_current: float, gdp_previous: float) -> dict:
        """Calculate GDP growth rate."""
        if gdp_previous == 0:
            return {"error": "Zero previous GDP"}
        growth_rate = (gdp_current - gdp_previous) / gdp_previous * 100
        return {
            "gdp_current": gdp_current,
            "gdp_previous": gdp_previous,
            "growth_rate_pct": growth_rate,
        }

    def okuns_law(self, output_gap_pct: float) -> dict:
        """Apply Okun's Law to estimate unemployment change."""
        # Okun's Law: 1% output gap ≈ 0.5% unemployment change (inverse)
        unemployment_change = -0.5 * output_gap_pct
        return {
            "output_gap_pct": output_gap_pct,
            "unemployment_change_pct": unemployment_change,
            "relationship": "Okuns_Law",
        }

    def get_principles(self) -> List[str]:
        return [
            "GDP and economic growth",
            "Inflation and monetary policy",
            "Unemployment and labor markets",
            "Business cycles",
        ]


class PublicFinanceKernel:
    """Kernel for public finance analysis."""

    def __init__(self):
        self.tax_systems: List[dict] = []
        self.spending_programs: List[dict] = []

    def add_tax_system(
        self, name: str, tax_type: str, rate_pct: float, revenue_b: float
    ) -> dict:
        """Add tax system."""
        tax = {
            "name": name,
            "type": tax_type,
            "rate_pct": rate_pct,
            "revenue_b": revenue_b,
        }
        self.tax_systems.append(tax)
        return tax

    def add_spending(
        self, name: str, category: str, amount_b: float, beneficiaries_m: float
    ) -> dict:
        """Add spending program."""
        program = {
            "name": name,
            "category": category,
            "amount_b": amount_b,
            "beneficiaries_m": beneficiaries_m,
        }
        self.spending_programs.append(program)
        return program

    def calculate_deficit(
        self, revenue_b: float, spending_b: float
    ) -> dict:
        """Calculate budget deficit/surplus."""
        deficit = spending_b - revenue_b
        return {
            "revenue_b": revenue_b,
            "spending_b": spending_b,
            "deficit_b": deficit,
            "surplus": deficit < 0,
            "deficit_pct_of_revenue": (deficit / revenue_b * 100) if revenue_b > 0 else 0,
        }

    def debt_to_gdp_ratio(self, debt_b: float, gdp_b: float) -> dict:
        """Calculate debt-to-GDP ratio."""
        if gdp_b == 0:
            return {"error": "Zero GDP"}
        ratio = (debt_b / gdp_b) * 100
        return {
            "debt_b": debt_b,
            "gdp_b": gdp_b,
            "debt_to_gdp_pct": ratio,
            "sustainable": ratio < 90,  # Rough heuristic
        }

    def get_principles(self) -> List[str]:
        return [
            "Taxation and revenue",
            "Government spending",
            "Budget deficits and debt",
            "Fiscal policy effects",
        ]


class FinancialSystemKernel:
    """Kernel for financial system analysis."""

    def __init__(self):
        self.banks: List[dict] = []
        self.assets: List[dict] = []

    def add_bank(
        self, name: str, assets_b: float, deposits_b: float, capital_ratio: float
    ) -> dict:
        """Add bank."""
        bank = {
            "name": name,
            "assets_b": assets_b,
            "deposits_b": deposits_b,
            "capital_ratio": capital_ratio,
        }
        self.banks.append(bank)
        return bank

    def add_asset(
        self, name: str, asset_type: str, value: float, risk_rating: str
    ) -> dict:
        """Add financial asset."""
        asset = {
            "name": name,
            "type": asset_type,
            "value": value,
            "risk_rating": risk_rating,
        }
        self.assets.append(asset)
        return asset

    def calculate_leverage_ratio(
        self, tier1_capital: float, total_assets: float
    ) -> dict:
        """Calculate Tier 1 leverage ratio."""
        if total_assets == 0:
            return {"error": "Zero assets"}
        ratio = tier1_capital / total_assets
        return {
            "tier1_capital": tier1_capital,
            "total_assets": total_assets,
            "leverage_ratio": ratio,
            "min_requirement_met": ratio >= 0.03,  # Basel III minimum
        }

    def portfolio_return(
        self, weights: List[float], returns: List[float]
    ) -> dict:
        """Calculate weighted portfolio return."""
        if len(weights) != len(returns):
            return {"error": "Weights and returns length mismatch"}
        if sum(weights) != 1.0:
            return {"error": "Weights must sum to 1.0"}
        portfolio_return = sum(w * r for w, r in zip(weights, returns))
        return {
            "weights": weights,
            "asset_returns": returns,
            "portfolio_return": portfolio_return,
        }

    def get_principles(self) -> List[str]:
        return [
            "Banking and leverage",
            "Asset pricing",
            "Risk management",
            "Capital markets",
        ]


class EconFinanceEngine:
    """AMOS Economics & Finance Engine - Markets and policy."""

    VERSION = "vInfinity_MAX"
    NAME = "AMOS_Econ_Finance_OMEGA"

    def __init__(self):
        self.micro_kernel = MicroEconomicsKernel()
        self.macro_kernel = MacroEconomicsKernel()
        self.public_finance_kernel = PublicFinanceKernel()
        self.financial_kernel = FinancialSystemKernel()

    def analyze(
        self, description: str, domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run economic/financial analysis across specified domains."""
        domains = domains or [
            "micro", "macro", "public_finance", "financial_system"
        ]
        results: Dict[str, Any] = {}
        if "micro" in domains:
            results["micro"] = self._analyze_micro(description)
        if "macro" in domains:
            results["macro"] = self._analyze_macro(description)
        if "public_finance" in domains:
            results["public_finance"] = self._analyze_public_finance(description)
        if "financial_system" in domains:
            results["financial_system"] = self._analyze_financial(description)
        return results

    def _analyze_micro(self, description: str) -> dict:
        return {
            "query": description[:100],
            "firms": len(self.micro_kernel.firms),
            "households": len(self.micro_kernel.households),
            "markets": len(self.micro_kernel.markets),
            "principles": self.micro_kernel.get_principles(),
        }

    def _analyze_macro(self, description: str) -> dict:
        return {
            "query": description[:100],
            "countries": len(self.macro_kernel.countries),
            "indicators": len(self.macro_kernel.indicators),
            "principles": self.macro_kernel.get_principles(),
        }

    def _analyze_public_finance(self, description: str) -> dict:
        return {
            "query": description[:100],
            "tax_systems": len(self.public_finance_kernel.tax_systems),
            "spending_programs": len(self.public_finance_kernel.spending_programs),
            "principles": self.public_finance_kernel.get_principles(),
        }

    def _analyze_financial(self, description: str) -> dict:
        return {
            "query": description[:100],
            "banks": len(self.financial_kernel.banks),
            "assets": len(self.financial_kernel.assets),
            "principles": self.financial_kernel.get_principles(),
        }

    def get_findings_summary(self, results: dict) -> str:
        """Generate findings summary with gap acknowledgment."""
        lines = [
            f"# {self.NAME} {self.VERSION}",
            "",
            "Creator: Trang Phan | System: AMOS vInfinity",
            "",
            "## Domain Coverage",
        ]
        domain_names = {
            "micro": "Microeconomics (Firms, Households, Markets)",
            "macro": "Macroeconomics (Growth, Inflation, Policy)",
            "public_finance": "Public Finance (Taxes, Spending, Debt)",
            "financial_system": "Financial Systems (Banks, Markets, Risk)",
        }
        for domain, data in results.items():
            display_name = domain_names.get(domain, domain.title())
            lines.extend(["", f"### {display_name}"])
            if isinstance(data, dict):
                for key, value in data.items():
                    if key not in ("principles", "query"):
                        lines.append(f"- **{key}**: {value}")
                if "principles" in data:
                    lines.append(
                        f"- **Principles**: {', '.join(data['principles'][:2])}..."
                    )
        lines.extend([
            "",
            "## Gaps and Limitations",
            "- Real-time market data not available",
            "- Long-horizon forecasts inherently uncertain",
            "- Personalized investment advice not provided",
            "- Country-specific regulations require manual lookup",
            "",
            "## Safety Disclaimer",
            "Does not provide personalized investment advice. "
            "All economic projections are subject to significant uncertainty. "
            "Consult qualified financial professionals for investment decisions. "
            "Avoid illegal financial behavior.",
        ])
        return "\n".join(lines)


# Singleton instance
_econ_finance_engine: Optional[EconFinanceEngine] = None


def get_econ_finance_engine() -> EconFinanceEngine:
    """Get or create the Econ Finance Engine singleton."""
from __future__ import annotations

    global _econ_finance_engine
    if _econ_finance_engine is None:
        _econ_finance_engine = EconFinanceEngine()
    return _econ_finance_engine
