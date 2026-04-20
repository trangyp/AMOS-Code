"""World Model Engine — Main orchestrator for world context

Integrates macroeconomic, geopolitical, and sector analysis
to provide unified world context for AMOS decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional

from geopolitical_monitor import get_geopolitical_monitor
from macroeconomic_scanner import get_macro_scanner
from sector_analyzer import get_sector_analyzer


@dataclass
class WorldContext:
    """Comprehensive world context snapshot."""

    timestamp: str
    economic_stability: str
    geopolitical_risk: str
    top_sectors: list[str]
    active_risks: list[str]
    opportunities: list[str]
    recommended_actions: list[str]


class WorldModelEngine:
    """Main engine for world model operations.

    Integrates all world model components and provides
    unified context for organism decisions.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize sub-components
        self.macro = get_macro_scanner(data_dir / "macro")
        self.geo = get_geopolitical_monitor(data_dir / "geo")
        self.sectors = get_sector_analyzer(data_dir / "sectors")

    def get_world_context(self) -> WorldContext:
        """Get current comprehensive world context."""
        # Get economic context
        econ = self.macro.get_economic_context()

        # Get geopolitical risk
        geo_summary = self.geo.get_global_summary()
        regions = list(geo_summary["regional_stability"].keys())
        geo_risk = self.geo.assess_risk(regions) if regions else {"risk_level": "unknown"}

        # Get sector overview
        sector_ov = self.sectors.get_sector_overview()
        top_sectors = [s["name"] for s in sector_ov.get("top_sectors", [])[:3]]

        # Identify active risks
        active_risks = []
        if econ.get("overall_stability") in ["unstable", "volatile"]:
            active_risks.append("economic_volatility")
        if geo_risk.get("risk_level") in ["HIGH", "SEVERE"]:
            active_risks.append("geopolitical_tension")

        # Find opportunities
        opps = self.sectors.scan_opportunities()
        top_opps = [f"{o['sector']}: {o['opportunity']}" for o in opps[:3]]

        # Generate recommendations
        recommendations = self._generate_recommendations(econ, geo_risk, sector_ov)

        return WorldContext(
            timestamp=datetime.now(UTC).isoformat(),
            economic_stability=econ.get("overall_stability", "unknown"),
            geopolitical_risk=geo_risk.get("risk_level", "unknown"),
            top_sectors=top_sectors,
            active_risks=active_risks,
            opportunities=top_opps,
            recommended_actions=recommendations,
        )

    def _generate_recommendations(
        self,
        econ: dict[str, Any],
        geo_risk: dict[str, Any],
        sectors: dict[str, Any],
    ) -> list[str]:
        """Generate recommendations based on world state."""
        recs = []

        # Economic recommendations
        if econ.get("overall_stability") == "unstable":
            recs.append("Reduce financial exposure, increase liquidity")
        elif econ.get("overall_stability") == "stable":
            recs.append("Economic conditions favorable for investment")

        # Geopolitical recommendations
        risk_level = geo_risk.get("risk_level", "LOW")
        if risk_level in ["HIGH", "SEVERE"]:
            recs.append("Avoid new operations in high-risk regions")
        elif risk_level == "ELEVATED":
            recs.append("Monitor geopolitical developments closely")

        # Sector recommendations
        avg_growth = sectors.get("average_growth_rate", 0)
        if avg_growth > 10:
            recs.append("Strong sector growth - consider expansion")

        return recs

    def scan_all(self) -> dict[str, Any]:
        """Run comprehensive world scan."""
        macro_result = self.macro.scan()
        geo_summary = self.geo.get_global_summary()
        sector_ov = self.sectors.get_sector_overview()
        context = self.get_world_context()

        return {
            "scan_time": datetime.now(UTC).isoformat(),
            "macroeconomic": {
                "indicators": macro_result.get("indicators_tracked", 0),
                "signals": macro_result.get("signals_generated", 0),
                "stability": macro_result.get("summary", {}).get("overall_stability"),
            },
            "geopolitical": {
                "active_events": geo_summary.get("total_active_events", 0),
                "regions_tracked": len(geo_summary.get("regional_stability", {})),
            },
            "sectors": {
                "total": sector_ov.get("total_sectors", 0),
                "market_size": sector_ov.get("total_market_size_b", 0),
                "avg_growth": sector_ov.get("average_growth_rate", 0),
            },
            "context": {
                "economic_stability": context.economic_stability,
                "geopolitical_risk": context.geopolitical_risk,
                "active_risks": context.active_risks,
                "opportunities": context.opportunities,
                "recommendations": context.recommended_actions,
            },
        }

    def assess_operational_risk(self, regions: list[str]) -> dict[str, Any]:
        """Assess operational risk for given regions."""
        # Economic risk
        econ_stability = self.macro._calculate_stability()

        # Geopolitical risk
        geo_assessment = self.geo.assess_risk(regions)

        # Combined risk score
        econ_risk = (
            0.5 if econ_stability == "unstable" else 0.2 if econ_stability == "moderate" else 0.1
        )
        geo_risk_score = geo_assessment.get("overall_risk", 0.5)

        combined = (econ_risk + geo_risk_score) / 2

        return {
            "regions": regions,
            "economic_stability": econ_stability,
            "geopolitical_risk": geo_assessment.get("risk_level", "unknown"),
            "combined_risk_score": combined,
            "risk_category": "high" if combined > 0.6 else "medium" if combined > 0.3 else "low",
            "recommendation": geo_assessment.get("recommendation", "no specific recommendation"),
        }

    def get_sector_recommendations(self) -> list[dict[str, Any]]:
        """Get investment recommendations by sector."""
        opportunities = self.sectors.scan_opportunities()
        recommendations = []

        for opp in opportunities[:5]:
            sector_data = self.sectors.analyze_sector(opp["sector_id"])
            if sector_data:
                recommendations.append(
                    {
                        "sector": opp["sector"],
                        "opportunity": opp["opportunity"],
                        "health": sector_data["sector"]["health"],
                        "attractiveness": sector_data["investment_attractiveness"],
                        "risk_level": sector_data["risk_assessment"]["level"],
                    }
                )

        return recommendations


# Global instance
_ENGINE: Optional[WorldModelEngine] = None


def get_world_model_engine(data_dir: Optional[Path] = None) -> WorldModelEngine:
    """Get or create global world model engine."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = WorldModelEngine(data_dir)
    return _ENGINE


if __name__ == "__main__":
    print("World Model Engine (08_WORLD_MODEL)")
    print("=" * 40)

    engine = get_world_model_engine()

    print("\nRunning comprehensive world scan...")
    result = engine.scan_all()

    print(f"\nScan completed at {result['scan_time']}")
    print(f"\nEconomic stability: {result['macroeconomic']['stability']}")
    print(f"Geopolitical risk: {result['geopolitical']['active_events']} active events")
    print(f"Sectors tracked: {result['sectors']['total']}")

    print("\nContext summary:")
    ctx = result["context"]
    print(f"  Economic: {ctx['economic_stability']}")
    print(f"  Geopolitical: {ctx['geopolitical_risk']}")
    print(f"  Active risks: {ctx['active_risks']}")

    print("\nRecommendations:")
    for rec in ctx["recommendations"]:
        print(f"  - {rec}")
