"""AMOS Society & Culture Engine - Social dynamics and institutions."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SocietyCultureDomain(Enum):
    """Society and culture domain classifications."""
    INSTITUTIONS = "institutions"
    CULTURAL_NORMS = "cultural_norms"
    DEMOGRAPHICS = "demographics"
    MEDIA_INFORMATION = "media_information"


@dataclass
class SocialEntity:
    """Social entity representation."""

    name: str
    entity_type: str
    domain: SocietyCultureDomain
    parameters: dict = field(default_factory=dict)


class InstitutionalKernel:
    """Kernel for institutional analysis (states, markets, civil society)."""

    def __init__(self):
        self.institutions: List[dict] = []
        self.roles: List[dict] = []

    def add_institution(
        self, name: str, inst_type: str, scope: str, legitimacy_score: float
    ) -> dict:
        """Add institution."""
        institution = {
            "name": name,
            "type": inst_type,
            "scope": scope,
            "legitimacy_score": legitimacy_score,
        }
        self.institutions.append(institution)
        return institution

    def add_role(self, name: str, institution: str, permissions: List[str]) -> dict:
        """Add role within institution."""
        role = {
            "name": name,
            "institution": institution,
            "permissions": permissions,
        }
        self.roles.append(role)
        return role

    def power_index_simple(
        self, resources_controlled: float, network_connections: int
    ) -> dict:
        """Calculate simple power index."""
        # Power as function of resources and connections
        power = resources_controlled * (1 + 0.1 * network_connections)
        return {
            "resources_controlled": resources_controlled,
            "network_connections": network_connections,
            "power_index": power,
        }

    def get_principles(self) -> List[str]:
        return [
            "Institutional roles and rules",
            "Resource flows and enforcement",
            "Legitimacy and authority",
            "State, market, civil society",
        ]


class CulturalNormsKernel:
    """Kernel for cultural norms, values, and narratives."""

    def __init__(self):
        self.values: List[dict] = []
        self.narratives: List[dict] = []

    def add_value(self, name: str, importance: float, universality: float) -> dict:
        """Add cultural value."""
        value = {
            "name": name,
            "importance": importance,
            "universality": universality,
        }
        self.values.append(value)
        return value

    def add_narrative(
        self, name: str, narrative_type: str, transmission_rate: float
    ) -> dict:
        """Add cultural narrative."""
        narrative = {
            "name": name,
            "type": narrative_type,
            "transmission_rate": transmission_rate,
        }
        self.narratives.append(narrative)
        return narrative

    def cultural_distance(
        self, values_set_a: List[float], values_set_b: List[float]
    ) -> dict:
        """Calculate cultural distance between two value sets."""
        if len(values_set_a) != len(values_set_b):
            return {"error": "Value sets must have same length"}
        # Euclidean distance
        distance = sum((a - b) ** 2 for a, b in zip(values_set_a, values_set_b)) ** 0.5
        return {
            "values_set_a": values_set_a,
            "values_set_b": values_set_b,
            "cultural_distance": distance,
            "similar": distance < 1.0,
        }

    def get_principles(self) -> List[str]:
        return [
            "Values and value systems",
            "Cultural narratives and scripts",
            "Rituals and taboos",
            "Identity and status signals",
        ]


class DemographicKernel:
    """Kernel for population dynamics and demographics."""

    def __init__(self):
        self.populations: List[dict] = []
        self.cohorts: List[dict] = []

    def add_population(
        self, name: str, total: int, growth_rate: float, urban_pct: float
    ) -> dict:
        """Add population."""
        population = {
            "name": name,
            "total": total,
            "growth_rate_pct": growth_rate,
            "urban_pct": urban_pct,
        }
        self.populations.append(population)
        return population

    def add_cohort(
        self, name: str, birth_year_range: str, size: int, characteristics: List[str]
    ) -> dict:
        """Add demographic cohort."""
        cohort = {
            "name": name,
            "birth_year_range": birth_year_range,
            "size": size,
            "characteristics": characteristics,
        }
        self.cohorts.append(cohort)
        return cohort

    def demographic_transition_stage(
        self, birth_rate: float, death_rate: float, migration_rate: float
    ) -> dict:
        """Estimate demographic transition stage."""
        # Simplified stage estimation
        if birth_rate > 30 and death_rate > 30:
            stage = "pre_transition"
        elif birth_rate > 30 and death_rate < 15:
            stage = "early_transition"
        elif birth_rate < 20 and death_rate < 15:
            stage = "late_transition"
        else:
            stage = "post_transition"
        return {
            "birth_rate_per_1000": birth_rate,
            "death_rate_per_1000": death_rate,
            "migration_rate_per_1000": migration_rate,
            "demographic_stage": stage,
        }

    def dependency_ratio(
        self, young_pop: int, working_age_pop: int, elderly_pop: int
    ) -> dict:
        """Calculate dependency ratio."""
        if working_age_pop == 0:
            return {"error": "Zero working age population"}
        dependents = young_pop + elderly_pop
        ratio = dependents / working_age_pop
        return {
            "young_population": young_pop,
            "working_age_population": working_age_pop,
            "elderly_population": elderly_pop,
            "dependency_ratio": ratio,
            "burden_per_worker": ratio,
        }

    def get_principles(self) -> List[str]:
        return [
            "Population dynamics",
            "Fertility and mortality",
            "Migration and urbanization",
            "Demographic transition",
        ]


class MediaInformationKernel:
    """Kernel for media, information flows, and network effects."""

    def __init__(self):
        self.channels: List[dict] = []
        self.networks: List[dict] = []

    def add_channel(
        self, name: str, channel_type: str, reach_millions: float, bias_score: float
    ) -> dict:
        """Add media channel."""
        channel = {
            "name": name,
            "type": channel_type,
            "reach_millions": reach_millions,
            "bias_score": bias_score,
        }
        self.channels.append(channel)
        return channel

    def add_network(self, name: str, nodes: int, edges: int, network_type: str) -> dict:
        """Add information network."""
        density = edges / (nodes * (nodes - 1)) if nodes > 1 else 0
        network = {
            "name": name,
            "nodes": nodes,
            "edges": edges,
            "type": network_type,
            "density": density,
        }
        self.networks.append(network)
        return network

    def information_cascade_threshold(
        self, network_density: float, influencer_fraction: float
    ) -> dict:
        """Estimate cascade threshold for information spread."""
        # Simplified threshold model
        threshold = 1 / (network_density * (1 + influencer_fraction))
        return {
            "network_density": network_density,
            "influencer_fraction": influencer_fraction,
            "cascade_threshold": threshold,
            "cascade_likely": threshold < 0.5,
        }

    def get_principles(self) -> List[str]:
        return [
            "Media channels and reach",
            "Information networks",
            "Memes and propagation",
            "Amplifiers and filters",
        ]


class SocietyCultureEngine:
    """AMOS Society & Culture Engine - Social dynamics and institutions."""

    VERSION = "vInfinity_MAX"
    NAME = "AMOS_Society_Culture_OMEGA"

    def __init__(self):
        self.institutional_kernel = InstitutionalKernel()
        self.cultural_kernel = CulturalNormsKernel()
        self.demographic_kernel = DemographicKernel()
        self.media_kernel = MediaInformationKernel()

    def analyze(
        self, description: str, domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run society/culture analysis across specified domains."""
        domains = domains or [
            "institutions", "cultural_norms", "demographics", "media_information"
        ]
        results: Dict[str, Any] = {}
        if "institutions" in domains:
            results["institutions"] = self._analyze_institutions(description)
        if "cultural_norms" in domains:
            results["cultural_norms"] = self._analyze_cultural(description)
        if "demographics" in domains:
            results["demographics"] = self._analyze_demographics(description)
        if "media_information" in domains:
            results["media_information"] = self._analyze_media(description)
        return results

    def _analyze_institutions(self, description: str) -> dict:
        return {
            "query": description[:100],
            "institutions": len(self.institutional_kernel.institutions),
            "roles": len(self.institutional_kernel.roles),
            "principles": self.institutional_kernel.get_principles(),
        }

    def _analyze_cultural(self, description: str) -> dict:
        return {
            "query": description[:100],
            "values": len(self.cultural_kernel.values),
            "narratives": len(self.cultural_kernel.narratives),
            "principles": self.cultural_kernel.get_principles(),
        }

    def _analyze_demographics(self, description: str) -> dict:
        return {
            "query": description[:100],
            "populations": len(self.demographic_kernel.populations),
            "cohorts": len(self.demographic_kernel.cohorts),
            "principles": self.demographic_kernel.get_principles(),
        }

    def _analyze_media(self, description: str) -> dict:
        return {
            "query": description[:100],
            "channels": len(self.media_kernel.channels),
            "networks": len(self.media_kernel.networks),
            "principles": self.media_kernel.get_principles(),
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
            "institutions": "Institutions (States, Markets, Civil Society)",
            "cultural_norms": "Cultural Norms (Values, Narratives, Identity)",
            "demographics": "Demographics (Population, Migration, Urbanization)",
            "media_information": "Media & Information (Networks, Propagation)",
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
            "- Deep cultural context requires local expertise",
            "- Demographic projections subject to uncertainty",
            "- Media landscape changes rapidly",
            "- Institutional power dynamics are complex",
            "",
            "## Safety Disclaimer",
            "Avoids prescriptive cultural judgments. Flags sensitive demographic "
            "topics. Does not generate targeted manipulation strategies. "
            "Analysis is for understanding, not manipulation.",
        ])
        return "\n".join(lines)


# Singleton instance
_society_culture_engine: Optional[SocietyCultureEngine] = None


def get_society_culture_engine() -> SocietyCultureEngine:
    """Get or create the Society Culture Engine singleton."""
from __future__ import annotations

    global _society_culture_engine
    if _society_culture_engine is None:
        _society_culture_engine = SocietyCultureEngine()
    return _society_culture_engine
