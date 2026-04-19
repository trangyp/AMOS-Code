#!/usr/bin/env python3
"""AMOS Extended Knowledge Loader
==============================

Loads country and sector knowledge packs to extend
intelligence beyond core Brain_Master knowledge.

Extends:
- 55 Country Knowledge Packs (geographic + cultural + economic)
- 19 Sector Knowledge Packs (industry expertise)

Integrates with: KnowledgeEnhancedBrain for unified querying

Owner: Trang
"""

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CountryKnowledge:
    """Country-specific knowledge pack."""

    country_code: str
    country_name: str
    geography: Dict[str, Any] = field(default_factory=dict)
    economy: Dict[str, Any] = field(default_factory=dict)
    culture: Dict[str, Any] = field(default_factory=dict)
    regulations: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class SectorKnowledge:
    """Sector/industry knowledge pack."""

    sector_code: str
    sector_name: str
    domain: str
    expertise: Dict[str, Any] = field(default_factory=dict)
    standards: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class ExtendedKnowledgeLoader:
    """Loader for extended knowledge packs (countries + sectors).

    Loads geographic and industry-specific knowledge to enable
    domain-specific reasoning beyond general intelligence.
    """

    def __init__(self):
        self.countries: Dict[str, CountryKnowledge] = {}
        self.sectors: Dict[str, SectorKnowledge] = {}
        self.loaded = False
        self.stats = {"countries_loaded": 0, "sectors_loaded": 0, "total_packs": 0, "memory_mb": 0}

    def load_all(self, base_path: Optional[Path] = None) -> Dict[str, Any]:
        """Load all extended knowledge packs.

        Args:
            base_path: Optional base path to knowledge packs

        Returns:
            Loading statistics
        """
        if base_path is None:
            repo_root = Path(__file__).parent.parent / "_AMOS_BRAIN"
            base_path = repo_root

        print("🌍 Loading Extended Knowledge Packs...")

        # Load country packs
        country_stats = self._load_countries(base_path / "Packs" / "Countries")

        # Load sector packs
        sector_stats = self._load_sectors(base_path / "Packs" / "Sectors")

        self.loaded = True
        self.stats["countries_loaded"] = country_stats["count"]
        self.stats["sectors_loaded"] = sector_stats["count"]
        self.stats["total_packs"] = country_stats["count"] + sector_stats["count"]
        self.stats["memory_mb"] = country_stats["size_mb"] + sector_stats["size_mb"]

        print("✅ Extended knowledge loaded!")
        print(f"   Countries: {self.stats['countries_loaded']}")
        print(f"   Sectors: {self.stats['sectors_loaded']}")
        print(f"   Total Packs: {self.stats['total_packs']}")
        print(f"   Size: {self.stats['memory_mb']:.1f}MB")

        return self.stats

    def _load_countries(self, path: Path) -> Dict[str, Any]:
        """Load country knowledge packs."""
        print(f"   Loading country packs from {path}...")

        if not path.exists():
            print(f"   ⚠️  Country path not found: {path}")
            return {"count": 0, "size_mb": 0}

        count = 0
        total_size = 0

        # Look for country JSON files
        for country_file in path.glob("*.json"):
            try:
                with open(country_file, encoding="utf-8") as f:
                    data = json.load(f)

                country_code = data.get("country_code", country_file.stem)
                country_name = data.get("country_name", country_code)

                country = CountryKnowledge(
                    country_code=country_code,
                    country_name=country_name,
                    geography=data.get("geography", {}),
                    economy=data.get("economy", {}),
                    culture=data.get("culture", {}),
                    regulations=data.get("regulations", {}),
                    tags=data.get("tags", []),
                )

                self.countries[country_code] = country
                count += 1
                total_size += country_file.stat().st_size

            except Exception as e:
                print(f"   ⚠️  Failed to load {country_file.name}: {e}")

        print(f"   ✅ Loaded {count} country packs")
        return {"count": count, "size_mb": total_size / 1024 / 1024}

    def _load_sectors(self, path: Path) -> Dict[str, Any]:
        """Load sector knowledge packs."""
        print(f"   Loading sector packs from {path}...")

        if not path.exists():
            print(f"   ⚠️  Sector path not found: {path}")
            return {"count": 0, "size_mb": 0}

        count = 0
        total_size = 0

        # Look for sector JSON files
        for sector_file in path.glob("*.json"):
            try:
                with open(sector_file, encoding="utf-8") as f:
                    data = json.load(f)

                sector_code = data.get("sector_code", sector_file.stem)
                sector_name = data.get("sector_name", sector_code)
                domain = data.get("domain", "general")

                sector = SectorKnowledge(
                    sector_code=sector_code,
                    sector_name=sector_name,
                    domain=domain,
                    expertise=data.get("expertise", {}),
                    standards=data.get("standards", []),
                    tags=data.get("tags", []),
                )

                self.sectors[sector_code] = sector
                count += 1
                total_size += sector_file.stat().st_size

            except Exception as e:
                print(f"   ⚠️  Failed to load {sector_file.name}: {e}")

        print(f"   ✅ Loaded {count} sector packs")
        return {"count": count, "size_mb": total_size / 1024 / 1024}

    def query_countries(self, query: str = None, limit: int = 10) -> List[CountryKnowledge]:
        """Query country knowledge packs."""
        if not self.loaded:
            return []

        results = []
        query_lower = query.lower() if query else ""

        for country in self.countries.values():
            if not query:
                results.append(country)
            else:
                # Match by name, code, or tags
                if (
                    query_lower in country.country_code.lower()
                    or query_lower in country.country_name.lower()
                    or any(query_lower in tag.lower() for tag in country.tags)
                ):
                    results.append(country)

        return results[:limit]

    def query_sectors(
        self, query: str = None, domain: str = None, limit: int = 10
    ) -> List[SectorKnowledge]:
        """Query sector knowledge packs."""
        if not self.loaded:
            return []

        results = []
        query_lower = query.lower() if query else ""

        for sector in self.sectors.values():
            # Domain filter
            if domain and sector.domain != domain:
                continue

            if not query:
                results.append(sector)
            else:
                # Match by name, code, or tags
                if (
                    query_lower in sector.sector_code.lower()
                    or query_lower in sector.sector_name.lower()
                    or any(query_lower in tag.lower() for tag in sector.tags)
                ):
                    results.append(sector)

        return results[:limit]

    def get_country(self, country_code: str) -> Optional[CountryKnowledge]:
        """Get specific country knowledge."""
        return self.countries.get(country_code.upper())

    def get_sector(self, sector_code: str) -> Optional[SectorKnowledge]:
        """Get specific sector knowledge."""
        return self.sectors.get(sector_code.upper())

    def list_countries(self) -> List[str]:
        """List all available country codes."""
        return sorted(list(self.countries.keys()))

    def list_sectors(self) -> List[str]:
        """List all available sector codes."""
        return sorted(list(self.sectors.keys()))

    def get_stats(self) -> Dict[str, Any]:
        """Get loading statistics."""
        return {
            "loaded": self.loaded,
            "countries": len(self.countries),
            "sectors": len(self.sectors),
            "total_packs": len(self.countries) + len(self.sectors),
            "memory_mb": self.stats.get("memory_mb", 0),
        }


class ComprehensiveKnowledgeSystem:
    """Complete knowledge system combining core + extended knowledge.

    Integrates:
    - Core: 17.8MB Brain_Master (general intelligence)
    - Extended: Country + Sector packs (specialized knowledge)
    """

    def __init__(self):
        self.core_loader = None  # Set externally
        self.extended_loader = ExtendedKnowledgeLoader()
        self.initialized = False

    def initialize(self, core_loader=None) -> Dict[str, Any]:
        """Initialize comprehensive knowledge system."""
        print("\n📚 Initializing Comprehensive Knowledge System...")

        self.core_loader = core_loader

        # Load extended knowledge
        extended_stats = self.extended_loader.load_all()

        self.initialized = True

        # Generate summary
        total_countries = extended_stats["countries_loaded"]
        total_sectors = extended_stats["sectors_loaded"]

        print("✅ Comprehensive knowledge system ready!")
        print("   Core knowledge: Brain_Master (17.8MB)")
        print(f"   Extended: {total_countries} countries + {total_sectors} sectors")

        return {
            "status": "initialized",
            "core": "Brain_Master (17.8MB)" if core_loader else "Not connected",
            "extended": extended_stats,
        }

    def query_all(self, query: str, limit: int = 10) -> dict[str, list]:
        """Query all knowledge sources."""
        results = {"core": [], "countries": [], "sectors": []}

        # Query core knowledge
        if self.core_loader:
            from amos_brain.knowledge_loader import query_knowledge
from typing import List, Optional, Set
from typing import Dict

            results["core"] = query_knowledge(query, limit=limit // 2)

        # Query extended knowledge
        if self.extended_loader.loaded:
            results["countries"] = self.extended_loader.query_countries(query, limit=limit // 3)
            results["sectors"] = self.extended_loader.query_sectors(query, limit=limit // 3)

        return results

    def get_geographic_intelligence(self, country_code: str) -> Dict[str, Any]:
        """Get comprehensive intelligence for a country."""
        country = self.extended_loader.get_country(country_code)
        if not country:
            return {"error": f"Country {country_code} not found"}

        return {
            "country": country.country_name,
            "geography": country.geography,
            "economy": country.economy,
            "culture": country.culture,
            "regulations": country.regulations,
        }

    def get_sector_intelligence(self, sector_code: str) -> Dict[str, Any]:
        """Get comprehensive intelligence for a sector."""
        sector = self.extended_loader.get_sector(sector_code)
        if not sector:
            return {"error": f"Sector {sector_code} not found"}

        return {
            "sector": sector.sector_name,
            "domain": sector.domain,
            "expertise": sector.expertise,
            "standards": sector.standards,
        }


# Global instance
_comprehensive_knowledge: Optional[ComprehensiveKnowledgeSystem] = None


def get_comprehensive_knowledge() -> ComprehensiveKnowledgeSystem:
    """Get or create comprehensive knowledge system."""
    global _comprehensive_knowledge
    if _comprehensive_knowledge is None:
        _comprehensive_knowledge = ComprehensiveKnowledgeSystem()
    return _comprehensive_knowledge


def load_extended_knowledge() -> Dict[str, Any]:
    """Convenience function to load extended knowledge."""
    system = get_comprehensive_knowledge()
    return system.initialize()


def query_comprehensive(query: str, limit: int = 10) -> dict[str, list]:
    """Query comprehensive knowledge (core + extended)."""
    system = get_comprehensive_knowledge()
    if not system.initialized:
        system.initialize()
    return system.query_all(query, limit)


def demo_extended_knowledge():
    """Demonstrate extended knowledge capabilities."""
    print("=" * 70)
    print("🌍 EXTENDED KNOWLEDGE LOADER DEMO")
    print("=" * 70)

    # Initialize
    system = get_comprehensive_knowledge()
    stats = system.initialize()

    print("\n📊 Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # Demo country query
    print("\n🗺️  Demo: Country Knowledge")
    print("-" * 70)
    countries = system.extended_loader.list_countries()[:5]
    print(f"Available countries (first 5): {', '.join(countries)}")

    # Demo sector query
    print("\n🏭 Demo: Sector Knowledge")
    print("-" * 70)
    sectors = system.extended_loader.list_sectors()[:5]
    print(f"Available sectors (first 5): {', '.join(sectors)}")

    # Demo comprehensive query
    print("\n🔍 Demo: Comprehensive Query")
    print("-" * 70)
    results = system.query_all("technology", limit=6)
    print("Query 'technology':")
    print(f"   Core results: {len(results['core'])}")
    print(f"   Country matches: {len(results['countries'])}")
    print(f"   Sector matches: {len(results['sectors'])}")

    print("\n" + "=" * 70)
    print("✅ Extended Knowledge Demo Complete!")
    print("=" * 70)


def main():
    """Main entry point."""
    demo_extended_knowledge()
    return 0


if __name__ == "__main__":
    sys.exit(main())
