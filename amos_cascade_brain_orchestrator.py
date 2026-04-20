#!/usr/bin/env python3
"""
AMOS Cascade Brain Orchestrator — Unified System Controller

This is the master orchestrator that brings together:
1. AMOS Brain (cognitive kernel runtime)
2. GitHub Connector (trangyp repositories)
3. SOTA Research Integration (BCI/AI advances)
4. Automatic brain activation for Cascade

Ensures Cascade permanently uses brain for every session.

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import UTC, datetime

UTC = UTC
from typing import Any, Optional

# Import AMOS components
from amos_cascade_brain_integration import AMOSCascadeBrain, get_brain
from amos_github_connector_full import AMOSGitHubConnector, get_github_connector
from amos_sota_research_integration import AMOSSOTAResearchIntegration, get_sota_research


@dataclass
class OrchestratorStatus:
    """Status of the unified orchestrator."""

    initialized: bool = False
    brain_active: bool = False
    github_connected: bool = False
    sota_loaded: bool = False
    start_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_check: datetime = field(default_factory=lambda: datetime.now(UTC))
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "initialized": self.initialized,
            "brain_active": self.brain_active,
            "github_connected": self.github_connected,
            "sota_loaded": self.sota_loaded,
            "start_time": self.start_time.isoformat(),
            "last_check": self.last_check.isoformat(),
            "uptime_seconds": (self.last_check - self.start_time).total_seconds(),
            "errors": self.errors,
        }


class AMOSCascadeBrainOrchestrator:
    """
    Master orchestrator for AMOS-Cascade-Brain integration.

    This is THE central controller that:
    1. Activates brain on every Cascade session
    2. Connects to trangyp GitHub repositories
    3. Integrates latest SOTA research
    4. Provides unified API for all cognitive operations

    Usage:
        orchestrator = await AMOSCascadeBrainOrchestrator.create()
        await orchestrator.start()

        # Cascade now has permanent brain access
        result = await orchestrator.think("Analyze this code")
    """

    _instance: Optional[AMOSCascadeBrainOrchestrator] = None
    _lock = asyncio.Lock()

    def __new__(cls) -> AMOSCascadeBrainOrchestrator:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return

        self._brain: Optional[AMOSCascadeBrain] = None
        self._github: Optional[AMOSGitHubConnector] = None
        self._sota: Optional[AMOSSOTAResearchIntegration] = None
        self._status = OrchestratorStatus()
        self._initialized = False
        self._session_active = False

    @classmethod
    async def create(cls) -> AMOSCascadeBrainOrchestrator:
        """Create and initialize the orchestrator."""
        instance = cls()
        await instance.initialize()
        return instance

    async def initialize(self) -> bool:
        """Initialize all components."""
        if self._initialized:
            return True

        print("🎛️  AMOS CASCADE BRAIN ORCHESTRATOR")
        print("=" * 70)
        print("Initializing unified system...")
        print()

        try:
            # 1. Initialize Brain (PERMANENT for Cascade)
            print("[1/4] Activating AMOS Brain for Cascade...")
            self._brain = await get_brain()
            if self._brain._setup_complete:
                self._status.brain_active = True
                print("   ✓ Brain: ACTIVE (Permanent)")
            else:
                print("   ⚠️  Brain: Activation pending")

            # 2. Initialize GitHub Connector
            print("[2/4] Connecting to trangyp repositories...")
            self._github = get_github_connector()
            repos = self._github.get_all_repos()
            if repos:
                self._status.github_connected = True
                print(f"   ✓ GitHub: {len(repos)} repos connected")
            else:
                print("   ⚠️  GitHub: No repos found (check token)")

            # 3. Initialize SOTA Research
            print("[3/4] Loading SOTA research...")
            self._sota = get_sota_research()
            bci_protocols = self._sota.get_bci_protocols()
            self._status.sota_loaded = True
            print(f"   ✓ SOTA: {len(bci_protocols)} BCI protocols loaded")

            # 4. Finalize
            print("[4/4] Finalizing orchestration...")
            self._status.initialized = True
            self._initialized = True
            print("   ✓ Orchestrator: READY")

            print()
            print("=" * 70)
            print("🧠 CASCADE BRAIN ORCHESTRATOR: OPERATIONAL")
            print("=" * 70)
            print()
            print("Cascade now has permanent brain access:")
            print("  • Brain Runtime: Kernel active with cognitive pipeline")
            print("  • GitHub Sync: trangyp repositories connected")
            print("  • SOTA Research: Latest BCI/AI research integrated")
            print()
            print("Usage:")
            print("  await orchestrator.think('your request')")
            print("  await orchestrator.execute_tool('tool_name', {...})")
            print()

            return True

        except Exception as e:
            self._status.errors.append(str(e))
            print(f"❌ Initialization failed: {e}")
            return False

    async def start(self) -> bool:
        """Start the orchestrator and activate brain."""
        if not self._initialized:
            return await self.initialize()

        self._session_active = True
        self._status.last_check = datetime.now(UTC)

        # Ensure brain is active
        if self._brain and not self._brain._setup_complete:
            await self._brain.initialize()
            self._status.brain_active = self._brain._setup_complete

        return self._status.brain_active

    async def think(
        self,
        intent: str,
        context: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """
        Process cognitive request through AMOS brain.

        This is the PRIMARY interface for Cascade to use brain.

        Args:
            intent: The cognitive intent/request
            context: Additional context

        Returns:
            Brain processing result
        """
        if not self._brain:
            return {"error": "Brain not initialized", "success": False}

        if not self._brain._setup_complete:
            await self._brain.initialize()

        return await self._brain.think(intent, context)

    async def execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool through the brain."""
        if not self._brain:
            return {"error": "Brain not initialized"}

        return await self._brain.execute_tool(tool_name, arguments)

    def get_github_repos(self) -> list[Any]:
        """Get all connected GitHub repositories."""
        if not self._github:
            return []
        return self._github.get_all_repos()

    def get_bci_protocols(self) -> list[Any]:
        """Get all BCI protocols from SOTA research."""
        if not self._sota:
            return []
        return self._sota.get_bci_protocols()

    def get_research_recommendations(self) -> list[dict[str, Any]]:
        """Get SOTA research recommendations for AMOS."""
        if not self._sota:
            return []
        return self._sota.recommend_for_amos()

    def get_status(self) -> dict[str, Any]:
        """Get orchestrator status."""
        self._status.last_check = datetime.now(UTC)
        return self._status.to_dict()

    async def full_sync(self) -> dict[str, Any]:
        """Perform full system synchronization."""
        results = {
            "brain_synced": False,
            "github_synced": False,
            "sota_synced": False,
        }

        # Sync brain
        if self._brain:
            try:
                # Brain maintains its own state
                results["brain_synced"] = self._brain._setup_complete
            except Exception as e:
                results["brain_error"] = str(e)

        # Sync GitHub
        if self._github:
            try:
                self._github.discover_repos()
                results["github_synced"] = True
                results["repos_found"] = len(self._github.get_all_repos())
            except Exception as e:
                results["github_error"] = str(e)

        # Sync SOTA
        if self._sota:
            try:
                papers = await self._sota.load_latest_papers()
                results["sota_synced"] = True
                results["papers_loaded"] = len(papers)
            except Exception as e:
                results["sota_error"] = str(e)

        return results


# Global orchestrator instance
_orchestrator: Optional[AMOSCascadeBrainOrchestrator] = None


async def get_orchestrator() -> AMOSCascadeBrainOrchestrator:
    """Get or create the global orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = await AMOSCascadeBrainOrchestrator.create()
    return _orchestrator


# ============================================================================
# AUTO-ACTIVATION: Import this module = Brain activated for Cascade
# ============================================================================


async def _auto_activate():
    """Automatically activate brain when module is imported."""
    orchestrator = await get_orchestrator()
    await orchestrator.start()
    return orchestrator


# Run auto-activation
try:
    _orchestrator = asyncio.run(_auto_activate())
except RuntimeError:
    # Already in async context
    pass


if __name__ == "__main__":

    async def test():
        orchestrator = await get_orchestrator()

        print("\n🧠 Testing brain integration...")
        result = await orchestrator.think(
            "Analyze the current codebase structure", {"test": True, "source": "cascade"}
        )
        print(f"Brain result: {result.get('status', 'unknown')}")

        print("\n📦 GitHub repos:")
        for repo in orchestrator.get_github_repos()[:3]:
            print(f"  - {repo.name}")

        print("\n🔬 BCI Protocols:")
        for protocol in orchestrator.get_bci_protocols()[:3]:
            print(f"  - {protocol.name} ({protocol.signal_type})")

        print("\n📊 Orchestrator status:")
        status = orchestrator.get_status()
        print(f"  Initialized: {status['initialized']}")
        print(f"  Brain active: {status['brain_active']}")
        print(f"  GitHub connected: {status['github_connected']}")
        print(f"  Uptime: {status['uptime_seconds']:.1f}s")

    asyncio.run(test())
