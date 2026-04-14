"""Sector Analyzer — Industry sectors and supply chains

Analyzes industry sectors, supply chain health, and
sector-specific risks and opportunities.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class SectorHealth(Enum):
    """Health status of a sector."""

    BOOMING = "booming"
    HEALTHY = "healthy"
    STABLE = "stable"
    DECLINING = "declining"
    DISTRESSED = "distressed"
    TRANSITIONING = "transitioning"


@dataclass
class Sector:
    """An industry sector."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    health: SectorHealth = SectorHealth.STABLE
    growth_rate: float = 0.0  # Annual growth %
    market_size_b: float = 0.0  # Market size in billions
    key_players: list[str] = field(default_factory=list)
    related_sectors: list[str] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    opportunities: list[str] = field(default_factory=list)
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "health": self.health.value,
        }


@dataclass
class SupplyChainNode:
    """A node in a supply chain."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    node_type: str = ""  # supplier, manufacturer, distributor, retailer
    region: str = ""
    sector: str = ""
    health_score: float = 1.0  # 0-1
    dependencies: list[str] = field(default_factory=list)
    risk_level: str = "low"  # low, medium, high

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SectorAnalyzer:
    """Analyzes industry sectors and supply chains.

    Tracks sector health, supply chain risks, and
    identifies opportunities across industries.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.sectors: dict[str, Sector] = {}
        self.supply_chains: dict[str, list[SupplyChainNode]] = {}

        self._load_data()

        # Initialize with default sectors if empty
        if not self.sectors:
            self._init_default_sectors()

    def _load_data(self):
        """Load sector data from disk."""
        data_file = self.data_dir / "sector_data.json"
        if data_file.exists():
            try:
                data = json.loads(data_file.read_text())
                for sec_data in data.get("sectors", []):
                    sector = Sector(
                        id=sec_data["id"],
                        name=sec_data["name"],
                        description=sec_data["description"],
                        health=SectorHealth(sec_data["health"]),
                        growth_rate=sec_data["growth_rate"],
                        market_size_b=sec_data["market_size_b"],
                        key_players=sec_data.get("key_players", []),
                        related_sectors=sec_data.get("related_sectors", []),
                        risk_factors=sec_data.get("risk_factors", []),
                        opportunities=sec_data.get("opportunities", []),
                        last_updated=sec_data["last_updated"],
                    )
                    self.sectors[sector.id] = sector
            except Exception as e:
                print(f"[SECTOR] Error loading data: {e}")

    def save(self):
        """Save sector data to disk."""
        data_file = self.data_dir / "sector_data.json"
        data = {
            "saved_at": datetime.utcnow().isoformat(),
            "sectors": [s.to_dict() for s in self.sectors.values()],
        }
        data_file.write_text(json.dumps(data, indent=2))

    def _init_default_sectors(self):
        """Initialize with default sectors."""
        defaults = [
            Sector(
                name="Technology",
                description="Software, hardware, AI, and digital services",
                health=SectorHealth.HEALTHY,
                growth_rate=15.0,
                market_size_b=5000.0,
                key_players=["Google", "Microsoft", "Apple", "Amazon"],
                risk_factors=["Regulation", "Cybersecurity"],
                opportunities=["AI adoption", "Cloud migration"],
            ),
            Sector(
                name="Healthcare",
                description="Medical services, pharmaceuticals, biotech",
                health=SectorHealth.STABLE,
                growth_rate=8.0,
                market_size_b=8000.0,
                key_players=["Johnson & Johnson", "Pfizer", "UnitedHealth"],
                risk_factors=["Regulation", "Pricing pressure"],
                opportunities=["Aging population", "Telemedicine"],
            ),
            Sector(
                name="Energy",
                description="Oil, gas, renewables, utilities",
                health=SectorHealth.TRANSITIONING,
                growth_rate=3.0,
                market_size_b=6000.0,
                key_players=["Exxon", "Shell", "NextEra"],
                risk_factors=["Climate policy", "Commodity prices"],
                opportunities=["Renewables", "Grid modernization"],
            ),
            Sector(
                name="Finance",
                description="Banking, insurance, investment services",
                health=SectorHealth.HEALTHY,
                growth_rate=6.0,
                market_size_b=7000.0,
                key_players=["JPMorgan", "Berkshire Hathaway", "Visa"],
                risk_factors=["Interest rates", "Regulation"],
                opportunities=["Fintech", "Digital payments"],
            ),
        ]

        for sector in defaults:
            self.sectors[sector.id] = sector

        self.save()

    def add_sector(self, sector: Sector) -> Sector:
        """Add a new sector."""
        self.sectors[sector.id] = sector
        self.save()
        return sector

    def analyze_sector(self, sector_id: str) -> Optional[dict[str, Any]]:
        """Analyze a specific sector."""
        sector = self.sectors.get(sector_id)
        if not sector:
            return None

        # Calculate health metrics
        health_score = self._calculate_health_score(sector)

        return {
            "sector": sector.to_dict(),
            "health_score": health_score,
            "investment_attractiveness": self._calculate_attractiveness(sector),
            "risk_assessment": self._assess_risk(sector),
            "related_opportunities": self._find_related_opportunities(sector),
        }

    def _calculate_health_score(self, sector: Sector) -> float:
        """Calculate numerical health score."""
        health_weights = {
            SectorHealth.BOOMING: 0.9,
            SectorHealth.HEALTHY: 0.8,
            SectorHealth.STABLE: 0.6,
            SectorHealth.DECLINING: 0.4,
            SectorHealth.DISTRESSED: 0.2,
        }
        base = health_weights.get(sector.health, 0.5)

        # Adjust for growth
        if sector.growth_rate > 10:
            base += 0.1
        elif sector.growth_rate < 0:
            base -= 0.2

        return min(1.0, max(0.0, base))

    def _calculate_attractiveness(self, sector: Sector) -> str:
        """Calculate investment attractiveness."""
        if (
            sector.health in (SectorHealth.BOOMING, SectorHealth.HEALTHY)
            and sector.growth_rate > 10
        ):
            return "High"
        elif sector.health == SectorHealth.STABLE and sector.growth_rate > 5:
            return "Medium-High"
        elif sector.health == SectorHealth.STABLE:
            return "Medium"
        else:
            return "Low"

    def _assess_risk(self, sector: Sector) -> dict[str, Any]:
        """Assess sector risks."""
        risk_count = len(sector.risk_factors)

        if risk_count == 0:
            level = "Low"
        elif risk_count <= 2:
            level = "Medium"
        else:
            level = "High"

        return {
            "level": level,
            "factors": sector.risk_factors,
            "count": risk_count,
        }

    def _find_related_opportunities(self, sector: Sector) -> list[dict[str, Any]]:
        """Find opportunities in related sectors."""
        opportunities = []

        for related_id in sector.related_sectors:
            if related_id in self.sectors:
                related = self.sectors[related_id]
                opportunities.extend(
                    [{"sector": related.name, "opportunity": op} for op in related.opportunities]
                )

        return opportunities

    def get_sector_comparison(self, sector_ids: list[str]) -> dict[str, Any]:
        """Compare multiple sectors."""
        comparison = []

        for sid in sector_ids:
            sector = self.sectors.get(sid)
            if sector:
                analysis = self.analyze_sector(sid)
                if analysis:
                    comparison.append(
                        {
                            "id": sid,
                            "name": sector.name,
                            "health": sector.health.value,
                            "health_score": analysis["health_score"],
                            "growth": sector.growth_rate,
                            "attractiveness": analysis["investment_attractiveness"],
                        }
                    )

        # Sort by health score
        comparison.sort(key=lambda x: x["health_score"], reverse=True)

        return {
            "sectors_compared": len(comparison),
            "ranking": comparison,
            "best_performer": comparison[0] if comparison else None,
        }

    def scan_opportunities(self) -> list[dict[str, Any]]:
        """Scan for opportunities across all sectors."""
        opportunities = []

        for sector in self.sectors.values():
            for opp in sector.opportunities:
                opportunities.append(
                    {
                        "sector": sector.name,
                        "sector_id": sector.id,
                        "opportunity": opp,
                        "sector_health": sector.health.value,
                        "growth_rate": sector.growth_rate,
                    }
                )

        # Sort by sector health and growth
        opportunities.sort(
            key=lambda x: (x["sector_health"], x["growth_rate"]),
            reverse=True,
        )

        return opportunities

    def get_sector_overview(self) -> dict[str, Any]:
        """Get overview of all sectors."""
        by_health = {}
        for sector in self.sectors.values():
            h = sector.health.value
            if h not in by_health:
                by_health[h] = []
            by_health[h].append(sector.name)

        total_market = sum(s.market_size_b for s in self.sectors.values())
        avg_growth = (
            sum(s.growth_rate for s in self.sectors.values()) / len(self.sectors)
            if self.sectors
            else 0
        )

        return {
            "total_sectors": len(self.sectors),
            "total_market_size_b": total_market,
            "average_growth_rate": avg_growth,
            "by_health": by_health,
            "top_sectors": sorted(
                [s.to_dict() for s in self.sectors.values()],
                key=lambda x: x["market_size_b"],
                reverse=True,
            )[:5],
        }


# Global instance
_ANALYZER: Optional[SectorAnalyzer] = None


def get_sector_analyzer(data_dir: Optional[Path] = None) -> SectorAnalyzer:
    """Get or create global sector analyzer."""
    global _ANALYZER
    if _ANALYZER is None:
        _ANALYZER = SectorAnalyzer(data_dir)
    return _ANALYZER


if __name__ == "__main__":
    print("Sector Analyzer (08_WORLD_MODEL)")
    print("=" * 40)

    analyzer = get_sector_analyzer()

    print("\nSectors tracked:")
    overview = analyzer.get_sector_overview()
    for sector in overview["top_sectors"]:
        print(f"  - {sector['name']}: ${sector['market_size_b']:.0f}B")

    print(f"\nTotal market size: ${overview['total_market_size_b']:.0f}B")
    print(f"Average growth: {overview['average_growth_rate']:.1f}%")

    print("\nOpportunities:")
    opps = analyzer.scan_opportunities()
    for opp in opps[:3]:
        print(f"  - {opp['sector']}: {opp['opportunity']}")
