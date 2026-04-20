"""Canon Bridge — _00_AMOS_CANON Integration Layer

Bridges the amos_canon_integration loader with the organism's 11_CANON_INTEGRATION layer.
Loads canonical rules, standards, agents, and cognitive stack from _00_AMOS_CANON.

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import importlib.util
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from pathlib import Path
from typing import Any

# Load canon loader using importlib
_canon_path = Path(__file__).resolve().parents[3] / "amos_canon_integration.py"
if _canon_path.exists():
    _spec = importlib.util.spec_from_file_location("_canon", _canon_path)
    _canon_mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_canon_mod)
    get_canon_loader = _canon_mod.get_canon_loader
else:
    get_canon_loader = None

# Import organism types
from .canon_enforcer import CanonEnforcer, CanonRule, RuleCategory, RulePriority
from .standards_registry import Standard, StandardsRegistry, StandardType

logger = logging.getLogger(__name__)


@dataclass
class CanonBridgeStatus:
    """Status of canon bridge integration."""

    timestamp: str
    canon_loaded: bool = False
    glossary_terms: int = 0
    agents_loaded: int = 0
    engines_loaded: int = 0
    cognitive_domains: int = 0
    kernels_loaded: int = 0
    rules_synced: int = 0
    standards_synced: int = 0
    ready: bool = False


class CanonBridge:
    """Bridges _00_AMOS_CANON with organism canon integration.

    Loads canonical definitions and syncs them with:
    - CanonEnforcer (rules from cognitive stack)
    - StandardsRegistry (standards from glossary and kernels)
    """

    _instance: CanonBridge = None
    _lock = asyncio.Lock()

    def __new__(cls) -> CanonBridge:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        self._loader = None
        self._canon_enforcer: CanonEnforcer = None
        self._standards_registry: StandardsRegistry = None
        self._status: CanonBridgeStatus = None
        self._loaded = False

    async def initialize(
        self,
        canon_enforcer: CanonEnforcer = None,
        standards_registry: StandardsRegistry = None,
    ) -> bool:
        """Initialize canon bridge and sync with _00_AMOS_CANON.

        Args:
            canon_enforcer: Optional existing enforcer to populate
            standards_registry: Optional existing registry to populate

        Returns:
            bool: True if sync successful
        """
        if self._loaded:
            return True

        print("\n[Canon Bridge] Initializing _00_AMOS_CANON integration...")
        print("-" * 55)

        try:
            # Initialize canon loader
            self._loader = get_canon_loader()
            canon_ready = await self._loader.initialize()

            if not canon_ready:
                logger.error("Canon loader failed to initialize")
                self._status = CanonBridgeStatus(
                    timestamp=datetime.now(UTC).isoformat(),
                    canon_loaded=False,
                    ready=False,
                )
                return False

            # Store references
            self._canon_enforcer = canon_enforcer
            self._standards_registry = standards_registry

            # Sync data
            rules_synced = await self._sync_rules()
            standards_synced = await self._sync_standards()

            # Build status
            status = self._loader.get_status()
            self._status = CanonBridgeStatus(
                timestamp=datetime.now(UTC).isoformat(),
                canon_loaded=canon_ready,
                glossary_terms=status.total_terms if status else 0,
                agents_loaded=status.total_agents if status else 0,
                engines_loaded=status.total_engines if status else 0,
                cognitive_domains=len(self._loader.get_cognitive_stack()) if self._loader else 0,
                kernels=len(self._loader.get_kernels()) if self._loader else 0,
                rules_synced=rules_synced,
                standards_synced=standards_synced,
                ready=True,
            )

            self._loaded = True

            print(f"  ✅ Canon synced: {rules_synced} rules, {standards_synced} standards")
            print(f"  ✅ Agents: {self._status.agents_loaded}")
            print(f"  ✅ Engines: {self._status.engines_loaded}")
            print(f"  ✅ Cognitive domains: {self._status.cognitive_domains}")
            print(f"  ✅ Kernels: {self._status.kernels_loaded}")

            return True

        except Exception as e:
            logger.error(f"Canon bridge initialization failed: {e}")
            self._status = CanonBridgeStatus(
                timestamp=datetime.now(UTC).isoformat(),
                canon_loaded=False,
                ready=False,
            )
            return False

    async def _sync_rules(self) -> int:
        """Sync canon rules from cognitive stack to enforcer.

        Returns:
            int: Number of rules synced
        """
        if not self._canon_enforcer or not self._loader:
            return 0

        count = 0
        cognitive_stack = self._loader.get_cognitive_stack()

        # Map cognitive stack domains to canon rules
        category_map = {
            "audit": RuleCategory.INTEGRITY,
            "security": RuleCategory.SECURITY,
            "biology_cognition": RuleCategory.SEMANTICS,
            "governance_risk": RuleCategory.INTEGRITY,
            "logic": RuleCategory.SYNTAX,
            "tech": RuleCategory.PERFORMANCE,
        }

        for domain, modules in cognitive_stack.items():
            category = category_map.get(domain.lower(), RuleCategory.INTEGRITY)

            for module_name, module_data in modules.items():
                if isinstance(module_data, dict) and "rules" in module_data:
                    for rule_data in module_data["rules"]:
                        rule = CanonRule(
                            id=f"CANON-{domain.upper()}-{count:03d}",
                            name=rule_data.get("name", f"{domain} Rule {count}"),
                            description=rule_data.get("description", ""),
                            category=category,
                            priority=RulePriority.HIGH
                            if rule_data.get("critical")
                            else RulePriority.MEDIUM,
                            condition=rule_data.get("condition", "always"),
                            action=rule_data.get("action", "log"),
                            enabled=True,
                        )
                        self._canon_enforcer.add_rule(rule)
                        count += 1

        # Also add rules from agent registry
        agent_registry = self._loader.get_agent_registry()
        agents = agent_registry.get("agents", {})
        for agent_id, agent_data in agents.items():
            if isinstance(agent_data, dict) and agent_data.get("canon_rules"):
                for rule_data in agent_data["canon_rules"]:
                    rule = CanonRule(
                        id=f"CANON-AGENT-{agent_id.upper()}-{count:03d}",
                        name=f"Agent {agent_id}: {rule_data.get('name', 'Rule')}",
                        description=rule_data.get("description", ""),
                        category=RuleCategory.SECURITY,
                        priority=RulePriority.CRITICAL
                        if rule_data.get("critical")
                        else RulePriority.HIGH,
                        condition=rule_data.get("condition", "agent_active"),
                        action=rule_data.get("action", "enforce"),
                        enabled=True,
                    )
                    self._canon_enforcer.add_rule(rule)
                    count += 1

        return count

    async def _sync_standards(self) -> int:
        """Sync standards from glossary and kernels to registry.

        Returns:
            int: Number of standards synced
        """
        if not self._standards_registry or not self._loader:
            return 0

        count = 0

        # Add glossary layers as standards
        glossary = self._loader.get_glossary()
        layers = glossary.get("layers", [])
        for layer in layers:
            layer_id = layer.get("id", f"LAYER-{count}")
            standard = Standard(
                id=f"CANON-GLS-{layer_id}",
                name=f"Glossary: {layer.get('name', layer_id)}",
                standard_type=StandardType.INTERNAL,
                version="1.0",
                description=layer.get("description", "Canonical glossary layer"),
                requirements=[
                    f"{t.get('term', '')}: {t.get('definition', '')}"
                    for t in layer.get("terms", [])
                ],
            )
            self._standards_registry.register_standard(standard)
            count += 1

        # Add kernel categories as standards
        kernels = self._loader.get_kernels()
        for category, kernel_data in kernels.items():
            standard = Standard(
                id=f"CANON-KRN-{category.upper()}",
                name=f"Kernel: {category}",
                standard_type=StandardType.INTERNAL,
                version=kernel_data.get("version", "1.0"),
                description=f"Canonical kernel specification for {category}",
                requirements=kernel_data.get("requirements", [])
                if isinstance(kernel_data, dict)
                else [],
            )
            self._standards_registry.register_standard(standard)
            count += 1

        return count

    def get_agent(self, agent_id: str) -> dict[str, Any]:
        """Get an agent definition from canon registry."""
        if not self._loader:
            return None
        registry = self._loader.get_agent_registry()
        return registry.get("agents", {}).get(agent_id)

    def get_engine_spec(self, engine_name: str) -> dict[str, Any]:
        """Get an engine specification from brain OS."""
        if not self._loader:
            return None
        brain_os = self._loader.get_brain_os_spec()
        if not brain_os or not isinstance(brain_os, list):
            return None

        for component in brain_os:
            engines = component.get("components", {}).get("brain_core", {}).get("engines", {})
            if engine_name in engines:
                return engines[engine_name]
        return None

    def get_glossary_term(self, term: str) -> dict[str, Any]:
        """Look up a term in the canonical glossary."""
        if not self._loader:
            return None
        return self._loader.get_glossary_term(term)

    def get_cognitive_module(self, domain: str, module: str) -> dict[str, Any]:
        """Get a cognitive module from the stack."""
        if not self._loader:
            return None
        stack = self._loader.get_cognitive_stack()
        return stack.get(domain, {}).get(module)

    def get_status(self) -> CanonBridgeStatus:
        """Get current bridge status."""
        return self._status

    def is_ready(self) -> bool:
        """Check if bridge is ready."""
        return self._loaded and self._status is not None and self._status.ready


def get_canon_bridge() -> CanonBridge:
    """Get the singleton CanonBridge instance."""
    return CanonBridge()


# Convenience function for organism initialization
async def initialize_canon_integration(
    canon_enforcer: CanonEnforcer = None,
    standards_registry: StandardsRegistry = None,
) -> CanonBridge:
    """Initialize canon integration for the organism.

    Args:
        canon_enforcer: Optional enforcer to populate with canon rules
        standards_registry: Optional registry to populate with canon standards

    Returns:
        CanonBridge instance if successful, None otherwise
    """
    bridge = get_canon_bridge()
    success = await bridge.initialize(canon_enforcer, standards_registry)
    return bridge if success else None


if __name__ == "__main__":
    print("Canon Bridge Module")
    print("=" * 55)

    async def test():
        bridge = get_canon_bridge()
        success = await bridge.initialize()
        if success:
            status = bridge.get_status()
            print("\n✅ Canon Bridge Ready")
            print(f"   Terms: {status.glossary_terms}")
            print(f"   Agents: {status.agents_loaded}")
            print(f"   Engines: {status.engines_loaded}")
            print(f"   Cognitive Domains: {status.cognitive_domains}")
            print(f"   Rules Synced: {status.rules_synced}")
            print(f"   Standards Synced: {status.standards_synced}")

            # Test lookups
            agent = bridge.get_agent("amos_core")
            if agent:
                print(f"\n   Sample Agent (amos_core): {agent.get('name', 'N/A')}")

            term = bridge.get_glossary_term("UBI")
            if term:
                print(f"   Sample Term (UBI): {term.get('definition', 'N/A')[:50]}...")
        else:
            print("\n❌ Canon Bridge Failed")

    asyncio.run(test())
