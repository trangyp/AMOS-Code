"""AMOS Planetary Stack Engine - Planetary-scale systems intelligence."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class PlanetaryBoundary(Enum):
    """Planetary boundaries per Rockstrom et al."""
    CLIMATE_CHANGE = "climate_change"
    BIODIVERSITY_LOSS = "biodiversity_loss"
    LAND_USE_CHANGE = "land_use_change"
    FRESHWATER_USE = "freshwater_use"
    NITROGEN_CYCLES = "nitrogen_cycles"
    PHOSPHORUS_CYCLES = "phosphorus_cycles"
    OCEAN_ACIDIFICATION = "ocean_acidification"
    ATMOSPHERIC_AEROSOLS = "atmospheric_aerosols"
    CHEMICAL_POLLUTION = "chemical_pollution"
    STRATOSPHERIC_OZONE = "stratospheric_ozone"


class EcosystemType(Enum):
    """Major ecosystem types."""
    FOREST = "forest"
    OCEAN = "ocean"
    GRASSLAND = "grassland"
    WETLAND = "wetland"
    TUNDRA = "tundra"
    DESERT = "desert"
    FRESHWATER = "freshwater"
    AGRICULTURAL = "agricultural"
    URBAN = "urban"


@dataclass
class PlanetaryHealth:
    """Planetary health metrics."""

    biosphere_integrity: float  # 0-1
    climate_stability: float  # 0-1
    land_systems_change: float  # 0-1, lower is better
    freshwater_health: float  # 0-1
    biogeochemical_flows: float  # 0-1, within safe zone


class ClimateSystemsKernel:
    """Climate systems and carbon cycle."""

    def __init__(self):
        self.co2_ppm = 420.0
        self.temperature_anomaly = 1.2  # Celsius above pre-industrial
        self.ocean_ph = 8.1

    def calculate_carbon_budget(self, target_temp: float = 1.5) -> Dict[str, Any]:
        """Calculate remaining carbon budget."""
        # Simplified calculation
        if target_temp == 1.5:
            remaining_gt = 300.0  # Gt CO2
        elif target_temp == 2.0:
            remaining_gt = 900.0
        else:
            remaining_gt = 500.0
        annual_emissions = 40.0  # Gt CO2/year
        years_remaining = remaining_gt / annual_emissions
        return {
            "remaining_budget_gt_co2": remaining_gt,
            "annual_emissions_gt": annual_emissions,
            "years_at_current_rate": round(years_remaining, 1),
            "target_temperature": target_temp,
        }

    def assess_climate_stability(self) -> Dict[str, Any]:
        """Assess climate system stability."""
        tipping_points = [
            ("Greenland ice sheet", self.temperature_anomaly > 1.5),
            ("West Antarctic ice sheet", self.temperature_anomaly > 1.5),
            ("Amazon rainforest", self.temperature_anomaly > 2.0),
            ("Permafrost thaw", self.temperature_anomaly > 1.5),
        ]
        active_tipping = [tp for tp, triggered in tipping_points if triggered]
        return {
            "temperature_anomaly_c": self.temperature_anomaly,
            "co2_ppm": self.co2_ppm,
            "ocean_ph": self.ocean_ph,
            "tipping_points_at_risk": active_tipping,
            "stability_index": max(0.0, 1.0 - self.temperature_anomaly / 3.0),
        }


class EcologyBiodiversityKernel:
    """Ecological systems and biodiversity."""

    def __init__(self):
        self.species_extinction_rate = 100.0  # E/MSY (extinctions per million species years)
        self.habitat_loss_percent = 30.0
        self.ecosystem_health: Dict[str, float] = {
            EcosystemType.FOREST.value: 0.6,
            EcosystemType.OCEAN.value: 0.5,
            EcosystemType.GRASSLAND.value: 0.4,
            EcosystemType.WETLAND.value: 0.3,
            EcosystemType.FRESHWATER.value: 0.4,
        }

    def assess_biodiversity_crisis(self) -> Dict[str, Any]:
        """Assess biodiversity crisis severity."""
        background_extinction = 0.1  # E/MSY
        crisis_multiplier = self.species_extinction_rate / background_extinction
        if crisis_multiplier > 1000:
            severity = "sixth_mass_extinction"
        elif crisis_multiplier > 100:
            severity = "major_crisis"
        elif crisis_multiplier > 10:
            severity = "elevated"
        else:
            severity = "background"
        return {
            "extinction_rate_emsy": self.species_extinction_rate,
            "background_rate": background_extinction,
            "multiplier": round(crisis_multiplier, 1),
            "severity": severity,
            "habitat_loss_percent": self.habitat_loss_percent,
        }

    def calculate_ecosystem_services(self) -> dict[str, float]:
        """Calculate ecosystem services value (simplified)."""
        services = {
            "carbon_sequestration": 50.0,  # Gt CO2/year
            "pollination_value": 235.0,  # Billion USD
            "water_purification": 2.3,  # Trillion USD
            "fisheries": 80.0,  # Billion USD
        }
        return services


class ResourceCyclesKernel:
    """Resource and material cycles."""

    def __init__(self):
        self.nitrogen_fixation = 150.0  # Tg N/year (teragrams)
        self.phosphorus_mining = 20.0  # Tg P/year
        self.material_consumption = 100.0  # Gt/year

    def assess_nitrogen_cycle(self) -> Dict[str, Any]:
        """Assess nitrogen cycle disruption."""
        safe_limit = 62.0  # Tg N/year
        current = self.nitrogen_fixation
        overshoot = max(0.0, current - safe_limit)
        return {
            "current_fixation_tg": current,
            "safe_limit_tg": safe_limit,
            "overshoot_tg": overshoot,
            "percent_of_safe_zone": round(current / safe_limit * 100, 1),
            "status": "overshoot" if overshoot > 0 else "safe",
        }

    def assess_phosphorus_cycle(self) -> Dict[str, Any]:
        """Assess phosphorus cycle disruption."""
        safe_limit = 6.2  # Tg P/year
        current = self.phosphorus_mining
        overshoot = max(0.0, current - safe_limit)
        return {
            "current_mining_tg": current,
            "safe_limit_tg": safe_limit,
            "overshoot_tg": overshoot,
            "percent_of_safe_zone": round(current / safe_limit * 100, 1),
            "status": "overshoot" if overshoot > 0 else "safe",
        }

    def calculate_circular_economy_potential(self) -> Dict[str, Any]:
        """Calculate circular economy metrics."""
        recycling_rate = 0.2  # Global average
        material_intensity = 0.5  # kg/$GDP
        improvement_potential = 1.0 - recycling_rate
        return {
            "current_recycling_rate": recycling_rate,
            "material_intensity": material_intensity,
            "improvement_potential": improvement_potential,
            "priority_materials": ["plastics", "metals", "rare_earths", "construction"],
        }


class SustainabilityMetricsKernel:
    """Sustainability and planetary health metrics."""

    def __init__(self):
        self.hdi = 0.732  # Human Development Index
        self.footprint_per_capita = 2.8  # Global hectares
        self.biocapacity_per_capita = 1.6  # Global hectares

    def calculate_overshoot_day(self) -> Dict[str, Any]:
        """Calculate Earth Overshoot Day."""
        if self.footprint_per_capita > self.biocapacity_per_capita:
            overshoot_ratio = self.biocapacity_per_capita / self.footprint_per_capita
            day_of_year = int(365 * overshoot_ratio)
            from datetime import datetime, timedelta
            date = datetime(2024, 1, 1) + timedelta(days=day_of_year - 1)
            return {
                "overshoot_day": day_of_year,
                "date": date.strftime("%B %d"),
                "biocapacity_deficit": round(self.footprint_per_capita - self.biocapacity_per_capita, 2),
                "num_earths_needed": round(self.footprint_per_capita / self.biocapacity_per_capita, 2),
            }
        return {"status": "within_biocapacity"}

    def assess_doughnut_economics(self) -> Dict[str, Any]:
        """Assess doughnut economics framework."""
        social_foundation = {
            "water": 0.9,
            "food": 0.85,
            "health": 0.8,
            "education": 0.88,
            "housing": 0.75,
            "energy": 0.9,
        }
        planetary_ceiling = {
            "climate": 0.6,
            "biodiversity": 0.4,
            "land": 0.5,
            "water": 0.7,
            "pollution": 0.5,
        }
        shortfall = {k: max(0, 1.0 - v) for k, v in social_foundation.items()}
        overshoot = {k: max(0, v - 0.8) for k, v in planetary_ceiling.items()}
        return {
            "social_foundation": social_foundation,
            "planetary_ceiling": planetary_ceiling,
            "social_shortfall": shortfall,
            "planetary_overshoot": overshoot,
            "in_doughnut": all(v > 0.8 for v in social_foundation.values()) and all(v < 0.8 for v in planetary_ceiling.values()),
        }


class PlanetaryBoundariesKernel:
    """Planetary boundaries framework."""

    def __init__(self):
        self.boundaries: Dict[str, dict] = {
            PlanetaryBoundary.CLIMATE_CHANGE.value: {"current": 1.2, "safe": 1.0, "unit": "C"},
            PlanetaryBoundary.BIODIVERSITY_LOSS.value: {"current": 100, "safe": 10, "unit": "E/MSY"},
            PlanetaryBoundary.LAND_USE_CHANGE.value: {"current": 75, "safe": 75, "unit": "%"},
            PlanetaryBoundary.FRESHWATER_USE.value: {"current": 2600, "safe": 4000, "unit": "km3/yr"},
            PlanetaryBoundary.NITROGEN_CYCLES.value: {"current": 150, "safe": 62, "unit": "TgN/yr"},
            PlanetaryBoundary.PHOSPHORUS_CYCLES.value: {"current": 22, "safe": 6, "unit": "TgP/yr"},
            PlanetaryBoundary.OCEAN_ACIDIFICATION.value: {"current": 8.1, "safe": 8.2, "unit": "pH"},
        }

    def assess_all_boundaries(self) -> Dict[str, Any]:
        """Assess status of all planetary boundaries."""
        status = {}
        crossed = []
        safe = []
        for name, data in self.boundaries.items():
            current = data["current"]
            safe_limit = data["safe"]
            if name in [PlanetaryBoundary.OCEAN_ACIDIFICATION.value]:
                # Lower pH is worse
                is_crossed = current < safe_limit
            else:
                is_crossed = current > safe_limit
            status[name] = {
                "current": current,
                "safe_limit": safe_limit,
                "unit": data["unit"],
                "crossed": is_crossed,
            }
            if is_crossed:
                crossed.append(name)
            else:
                safe.append(name)
        return {
            "boundary_status": status,
            "crossed_count": len(crossed),
            "safe_count": len(safe),
            "crossed_boundaries": crossed,
            "safe_boundaries": safe,
        }


class PlanetaryStackEngine:
    """AMOS Planetary Stack Engine - Planetary-scale systems intelligence."""

    VERSION = "vInfinity_Planetary_1.0.0"
    NAME = "AMOS_Planetary_Stack_OMEGA"

    def __init__(self):
        self.climate = ClimateSystemsKernel()
        self.ecology = EcologyBiodiversityKernel()
        self.resources = ResourceCyclesKernel()
        self.sustainability = SustainabilityMetricsKernel()
        self.boundaries = PlanetaryBoundariesKernel()

    def analyze(self, query: str, context: Dict[str, Any]  = None) -> Dict[str, Any]:
        """Run planetary systems analysis."""
        context = context or {}
        query_lower = query.lower()
        results: Dict[str, Any] = {
            "query": query[:100],
            "climate_analysis": {},
            "ecology_analysis": {},
            "resources_analysis": {},
            "sustainability_analysis": {},
            "boundaries_analysis": {},
            "planetary_health_index": 0.0,
            "recommendations": [],
        }
        # Detect focus areas
        focus_areas = []
        if any(kw in query_lower for kw in ["climate", "carbon", "temperature", "warming"]):
            focus_areas.append("climate")
        if any(kw in query_lower for kw in ["biodiversity", "species", "extinction", "ecosystem"]):
            focus_areas.append("ecology")
        if any(kw in query_lower for kw in ["nitrogen", "phosphorus", "resources", "materials"]):
            focus_areas.append("resources")
        if any(kw in query_lower for kw in ["sustainability", "overshoot", "footprint", "doughnut"]):
            focus_areas.append("sustainability")
        if any(kw in query_lower for kw in ["boundaries", "planetary limits", "safe operating space"]):
            focus_areas.append("boundaries")
        if not focus_areas:
            focus_areas = ["climate", "ecology", "boundaries"]  # Default
        # Run analyses
        if "climate" in focus_areas:
            results["climate_analysis"] = {
                "carbon_budget": self.climate.calculate_carbon_budget(),
                "stability": self.climate.assess_climate_stability(),
            }
        if "ecology" in focus_areas:
            results["ecology_analysis"] = {
                "biodiversity_crisis": self.ecology.assess_biodiversity_crisis(),
                "ecosystem_services": self.ecology.calculate_ecosystem_services(),
            }
        if "resources" in focus_areas:
            results["resources_analysis"] = {
                "nitrogen": self.resources.assess_nitrogen_cycle(),
                "phosphorus": self.resources.assess_phosphorus_cycle(),
                "circular_economy": self.resources.calculate_circular_economy_potential(),
            }
        if "sustainability" in focus_areas:
            results["sustainability_analysis"] = {
                "overshoot": self.sustainability.calculate_overshoot_day(),
                "doughnut": self.sustainability.assess_doughnut_economics(),
            }
        if "boundaries" in focus_areas:
            results["boundaries_analysis"] = self.boundaries.assess_all_boundaries()
        # Calculate planetary health index
        climate_health = results.get("climate_analysis", {}).get("stability", {}).get("stability_index", 0.5)
        eco_health = 1.0 - results.get("ecology_analysis", {}).get("biodiversity_crisis", {}).get("habitat_loss_percent", 50) / 100
        results["planetary_health_index"] = round((climate_health + eco_health) / 2, 2)
        # Generate recommendations
        recommendations = []
        boundaries_crossed = results.get("boundaries_analysis", {}).get("crossed_count", 0)
        if boundaries_crossed > 3:
            recommendations.append(f"URGENT: {boundaries_crossed} planetary boundaries crossed - transformative change needed")
        if "climate" in focus_areas and self.climate.temperature_anomaly > 1.5:
            recommendations.append("Climate: Accelerate decarbonization, protect carbon sinks")
        if "ecology" in focus_areas and self.ecology.species_extinction_rate > 10:
            recommendations.append("Ecology: Expand protected areas, restore ecosystems")
        if "resources" in focus_areas:
            nitrogen_status = results.get("resources_analysis", {}).get("nitrogen", {}).get("status", "")
            if nitrogen_status == "overshoot":
                recommendations.append("Nitrogen: Reduce synthetic fertilizer use, improve nutrient recycling")
        if "sustainability" in focus_areas:
            overshoot_data = results.get("sustainability_analysis", {}).get("overshoot", {})
            if "num_earths_needed" in overshoot_data:
                recommendations.append(f"Overshoot: Currently using {overshoot_data['num_earths_needed']} Earths - reduce consumption")
        recommendations.append("Systemic: Integrate planetary boundaries into all decision-making")
        results["recommendations"] = recommendations
        return results

    def get_findings_summary(self, results: dict) -> str:
        """Generate findings summary."""
        lines = [
            f"# {self.NAME} {self.VERSION}",
            "",
            "Creator: Trang Phan | System: AMOS vInfinity",
            "Role: Planetary-Scale Systems Intelligence",
            "",
            "## Planetary Stack Overview",
            "Comprehensive analysis of planetary boundaries, climate systems,",
            "ecology, resource cycles, and sustainability metrics.",
            "",
            "## Planetary Boundaries Framework",
            "Based on Rockstrom et al. - Safe Operating Space for Humanity",
        ]
        boundaries = results.get("boundaries_analysis", {})
        crossed = boundaries.get("crossed_count", 0)
        safe = boundaries.get("safe_count", 0)
        lines.extend([
            f"- **Crossed Boundaries**: {crossed}",
            f"- **Safe Boundaries**: {safe}",
            "",
            "### Boundary Status",
        ])
        status = boundaries.get("boundary_status", {})
        for name, data in list(status.items())[:5]:
            marker = "⚠️" if data.get("crossed") else "✓"
            lines.append(f"- {marker} **{name}**: {data.get('current')} {data.get('unit')} (safe: {data.get('safe_limit')})")
        lines.extend([
            "",
            "## Climate Systems",
        ])
        climate = results.get("climate_analysis", {})
        stability = climate.get("stability", {})
        lines.extend([
            f"- **Temperature Anomaly**: +{stability.get('temperature_anomaly_c', 'N/A')}°C",
            f"- **CO2 Concentration**: {stability.get('co2_ppm', 'N/A')} ppm",
            f"- **Stability Index**: {stability.get('stability_index', 0):.2f}",
        ])
        budget = climate.get("carbon_budget", {})
        if budget:
            lines.extend([
                "",
                "### Carbon Budget (1.5°C Target)",
                f"- **Remaining**: {budget.get('remaining_budget_gt_co2', 'N/A')} Gt CO2",
                f"- **Years at Current Rate**: {budget.get('years_at_current_rate', 'N/A')}",
            ])
        ecology = results.get("ecology_analysis", {})
        bio_crisis = ecology.get("biodiversity_crisis", {})
        lines.extend([
            "",
            "## Ecology & Biodiversity",
            f"- **Extinction Rate**: {bio_crisis.get('extinction_rate_emsy', 'N/A')} E/MSY",
            f"- **Multiplier**: {bio_crisis.get('multiplier', 'N/A')}x background rate",
            f"- **Severity**: {bio_crisis.get('severity', 'N/A')}",
            f"- **Habitat Loss**: {bio_crisis.get('habitat_loss_percent', 'N/A')}%",
        ])
        lines.extend([
            "",
            "## Resource Cycles",
        ])
        resources = results.get("resources_analysis", {})
        nitrogen = resources.get("nitrogen", {})
        if nitrogen:
            lines.extend([
                "### Nitrogen Cycle",
                f"- **Current**: {nitrogen.get('current_fixation_tg', 'N/A')} Tg N/yr",
                f"- **Safe Limit**: {nitrogen.get('safe_limit_tg', 'N/A')} Tg N/yr",
                f"- **Status**: {nitrogen.get('status', 'N/A').upper()}",
            ])
        phosphorus = resources.get("phosphorus", {})
        if phosphorus:
            lines.extend([
                "",
                "### Phosphorus Cycle",
                f"- **Current**: {phosphorus.get('current_mining_tg', 'N/A')} Tg P/yr",
                f"- **Safe Limit**: {phosphorus.get('safe_limit_tg', 'N/A')} Tg P/yr",
                f"- **Status**: {phosphorus.get('status', 'N/A').upper()}",
            ])
        lines.extend([
            "",
            "## Sustainability Metrics",
        ])
        sust = results.get("sustainability_analysis", {})
        overshoot = sust.get("overshoot", {})
        if overshoot:
            if "num_earths_needed" in overshoot:
                lines.extend([
                    "### Earth Overshoot",
                    f"- **Overshoot Day**: {overshoot.get('date', 'N/A')} (Day {overshoot.get('overshoot_day', 'N/A')})",
                    f"- **Earths Needed**: {overshoot.get('num_earths_needed', 'N/A')}",
                ])
        doughnut = sust.get("doughnut", {})
        if doughnut:
            lines.extend([
                "",
                "### Doughnut Economics",
                f"- **In Doughnut Zone**: {doughnut.get('in_doughnut', False)}",
            ])
        lines.extend([
            "",
            "## Planetary Health Index",
            f"**Overall Score**: {results.get('planetary_health_index', 0):.2f} / 1.0",
            "",
            "### Interpretation",
            "- **0.8-1.0**: Healthy planetary systems",
            "- **0.6-0.8**: Moderate stress, management needed",
            "- **0.4-0.6**: Significant degradation",
            "- **<0.4**: Critical planetary emergency",
        ])
        recommendations = results.get("recommendations", [])
        if recommendations:
            lines.extend([
                "",
                "## Planetary-Scale Recommendations",
            ])
            for i, rec in enumerate(recommendations[:5], 1):
                lines.append(f"{i}. {rec}")
        lines.extend([
            "",
            "## Planetary Principles",
            "1. **Earth System Thinking**: View Earth as integrated, complex system",
            "2. **Precautionary Approach**: Act before boundaries are crossed",
            "3. **Stewardship Responsibility**: Humans as planetary stewards",
            "4. **Intergenerational Equity**: Preserve options for future generations",
            "5. **Systemic Solutions**: Address root causes, not symptoms",
            "",
            "## Integration with AMOS",
            "The Planetary Stack provides context for:",
            "- Species Interaction Core: Planetary constraints on human activity",
            "- UBI Stack: Biological basis for planetary health",
            "- vOmni Kernel: Planetary-scale routing and decisions",
            "",
            "## Limitations",
            "- Simplified planetary boundaries model",
            "- Static baseline values (dynamic Earth system)",
            "- Regional variations not captured",
            "- Not a substitute for IPCC/IPBES assessments",
        ])
        return "\n".join(lines)


# Singleton instance
_planetary_engine: Optional[PlanetaryStackEngine] = None


def get_planetary_stack_engine() -> PlanetaryStackEngine:
    """Get or create the Planetary Stack Engine singleton."""
from __future__ import annotations

    global _planetary_engine
    if _planetary_engine is None:
        _planetary_engine = PlanetaryStackEngine()
    return _planetary_engine
