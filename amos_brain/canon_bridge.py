"""Canon-Brain Bridge - Integrates AMOS Canon with Brain Cognitive System.

Provides real-time access to canonical definitions during cognitive processing.
Uses CanonKnowledgeEngine to parse actual Canon JSON files.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from amos_canon_integration import get_canon_loader, initialize_canon


@dataclass
class CanonContext:
    """Canonical context for brain operations."""

    domain: str
    glossary_terms: Dict[str, Any]
    applicable_agents: List[str]
    relevant_engines: List[str]
    brain_os_config: Optional[dict] = None
    knowledge_entries: Optional[List[Any]] = None


class CanonBrainBridge:
    """Bridge between Canon definitions and Brain cognitive processing.

    Makes canonical definitions available to brain operations in real-time.
    """

    def __init__(self):
        self._loader = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the canon-brain bridge."""
        if self._initialized:
            return True

        success = await initialize_canon()
        if success:
            self._loader = get_canon_loader()
            self._initialized = True
        return success

    def get_context_for_domain(self, domain: str) -> CanonContext:
        """Get canonical context for a specific domain.

        Args:
            domain: The cognitive domain (e.g., "security", "api_design")

        Returns:
            CanonContext with relevant canonical definitions
        """
        if not self._initialized or not self._loader:
            return CanonContext(
                domain=domain,
                glossary_terms={},
                applicable_agents=[],
                relevant_engines=[],
                brain_os_config=None,
            )

        # Get glossary terms for this domain
        glossary = self._loader.get_glossary()
        domain_terms = {}

        # Search through layers structure
        for layer in glossary.get("layers", []):
            for term in layer.get("terms", []):
                term_name = term.get("name", "")
                term_def = term.get("definition", "")
                if domain.lower() in term_name.lower() or domain.lower() in term_def.lower():
                    domain_terms[term_name] = term_def

        # Get agents that can handle this domain
        agents = self._loader.get_agent_registry()
        applicable = [
            name
            for name, config in agents.items()
            if domain.lower() in name.lower() or domain.lower() in str(config).lower()
        ]

        # Get relevant engines
        kernels = self._loader.get_kernels()
        engines = [name for name in kernels.keys() if domain.lower() in name.lower()]

        # Get brain OS config if available
        brain_os = self._loader.get_brain_os_spec()
        config = brain_os[0] if brain_os else None

        return CanonContext(
            domain=domain,
            glossary_terms=domain_terms,
            applicable_agents=applicable,
            relevant_engines=engines,
            brain_os_config=config,
        )

    def enrich_query(self, query: str, domain: str) -> str:
        """Enrich a query with canonical context.

        Args:
            query: Original query
            domain: Domain for context

        Returns:
            Enriched query with canonical definitions
        """
        context = self.get_context_for_domain(domain)

        if not context.glossary_terms:
            return query

        # Build context prefix
        context_parts = ["=== CANONICAL CONTEXT ==="]

        if context.glossary_terms:
            context_parts.append("\nRelevant Terms:")
            for term, definition in list(context.glossary_terms.items())[:5]:
                context_parts.append(f"  - {term}: {str(definition)[:100]}")

        if context.applicable_agents:
            context_parts.append(f"\nApplicable Agents: {', '.join(context.applicable_agents[:3])}")

        if context.relevant_engines:
            context_parts.append(f"\nRelevant Engines: {', '.join(context.relevant_engines[:3])}")

        context_parts.append("\n=== ORIGINAL QUERY ===")

        return "\n".join(context_parts) + f"\n{query}"


# Global bridge instance
_bridge: Optional[CanonBrainBridge] = None


async def get_canon_bridge() -> CanonBrainBridge:
    """Get or create global canon-brain bridge."""
    global _bridge
    if _bridge is None:
        _bridge = CanonBrainBridge()
        await _bridge.initialize()
    return _bridge
