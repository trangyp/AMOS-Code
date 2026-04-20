#!/usr/bin/env python3

from typing import Any

"""AMOS OpenClaws Bridge - Activates BrainClawSpringBridge and Local LLM

This module initializes and manages the connection between:
- AMOS Brain cognitive architecture
- ClawSpring agent framework (OpenClaws)
- Local Ollama LLM models

Usage:
    python amos_openclaws_bridge.py

Environment:
    OLLAMA_BASE_URL - Ollama endpoint (default: http://localhost:11434)
    CLAWSPRING_ENABLED - Enable ClawSpring bridge (default: true)
"""

import asyncio
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos_openclaws")

# Import alias modules to set up paths
import clawspring  # noqa: F401


class AMOSOpenClawsBridge:
    """Unified bridge connecting AMOS Brain to OpenClaws and Local LLMs."""

    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_enabled = os.getenv("OLLAMA_ENABLED", "true").lower() == "true"
        self.clawspring_enabled = os.getenv("CLAWSPRING_ENABLED", "true").lower() == "true"
        self.brain_bridge = None
        self.ollama_models: list[str] = []
        self._initialized = False

    async def initialize(self) -> dict[str, Any]:
        """Initialize all connections."""
        results = {
            "ollama": {"connected": False, "models": [], "error": None, "url": self.ollama_url},
            "clawspring": {"connected": False, "error": None},
            "brain_bridge": {"connected": False, "error": None},
        }

        # 1. Connect to Ollama
        if self.ollama_enabled:
            try:
                self.ollama_models = await self._check_ollama()
                results["ollama"]["connected"] = True
                results["ollama"]["models"] = self.ollama_models
                count = len(self.ollama_models)
                logger.info(f"✅ Ollama connected: {count} models available")
            except Exception as e:
                results["ollama"]["error"] = str(e)
                logger.error(f"❌ Ollama failed: {e}")

        # 2. Initialize BrainClawSpringBridge
        if self.clawspring_enabled:
            try:
                self.brain_bridge = await self._init_brain_bridge()
                results["brain_bridge"]["connected"] = True
                results["clawspring"]["connected"] = True
                logger.info("✅ BrainClawSpringBridge initialized")
            except Exception as e:
                err = str(e)
                results["brain_bridge"]["error"] = err
                results["clawspring"]["error"] = err
                logger.error(f"❌ Brain bridge failed: {e}")

        self._initialized = True
        return results

    async def _check_ollama(self) -> list[str]:
        """Check Ollama connection and return available models."""
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.ollama_url}/api/tags") as resp:
                if resp.status != 200:
                    raise ConnectionError(f"Ollama returned {resp.status}")
                data = await resp.json()
                return [m["name"] for m in data.get("models", [])]

    async def _init_brain_bridge(self) -> Any:
        """Initialize the BrainClawSpringBridge."""
        import importlib.util

        # Load the module directly
        module_path = REPO_ROOT / "clawspring" / "amos_brain_integration.py"
        spec = importlib.util.spec_from_file_location("amos_brain_integration", module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["amos_brain_integration"] = module
        spec.loader.exec_module(module)

        bridge = module.BrainClawSpringBridge()
        # Initialize a default agent session
        goal = "Cognitive task execution with local LLMs"
        bridge.init_agent("AMOS-OpenClaws-Agent", goal)
        return bridge

    def get_available_models(self) -> list[str]:
        """Return list of available Ollama models."""
        return self.ollama_models

    async def query_local_llm(self, model: str, prompt: str) -> str:
        """Query a local Ollama model."""

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.ollama_url}/api/generate", json=payload) as resp:
                if resp.status != 200:
                    raise ConnectionError(f"Ollama generate failed: {resp.status}")
                data = await resp.json()
                return data.get("response", "")

    async def think_with_brain(self, query: str, domain: str = "general") -> dict[str, Any]:
        """Use BrainClawSpringBridge for cognitive processing."""
        if not self.brain_bridge:
            raise RuntimeError("Brain bridge not initialized")
        return self.brain_bridge.think(query, domain)

    def get_status(self) -> dict[str, Any]:
        """Get current connection status."""
        return {
            "initialized": self._initialized,
            "ollama_enabled": self.ollama_enabled,
            "ollama_url": self.ollama_url,
            "ollama_models": self.ollama_models,
            "clawspring_enabled": self.clawspring_enabled,
            "brain_bridge_active": self.brain_bridge is not None,
        }


async def main():
    """Run bridge initialization and status check."""
    print("🚀 AMOS OpenClaws Bridge - Activation Script")
    print("=" * 50)

    bridge = AMOSOpenClawsBridge()

    # Initialize connections
    results = await bridge.initialize()

    print("\n📊 Connection Status:")
    print("-" * 50)

    # Ollama status
    ollama = results["ollama"]
    if ollama["connected"]:
        print("✅ Ollama: Connected")
        models = ollama["models"][:3]
        print(f"   Models: {', '.join(models)}")
        if len(ollama["models"]) > 3:
            remaining = len(ollama["models"]) - 3
            print(f"   ... and {remaining} more")
    else:
        err = ollama.get("error", "Not connected")
        print(f"❌ Ollama: {err}")

    # Brain Bridge status
    brain = results["brain_bridge"]
    if brain["connected"]:
        print("✅ BrainClawSpringBridge: Active")
    else:
        err = brain.get("error", "Not initialized")
        print(f"❌ BrainClawSpringBridge: {err}")

    print("\n🔧 Available Actions:")
    print("-" * 50)
    print("1. bridge.query_local_llm('qwen2.5-coder:14b', 'Your prompt')")
    print("2. bridge.think_with_brain('complex query', 'domain')")
    print("3. bridge.get_available_models()")
    print("4. bridge.get_status()")

    return bridge


if __name__ == "__main__":
    # Run the bridge
    bridge = asyncio.run(main())

    # Keep script alive for interactive use
    print("\n💡 Bridge is active. Import this module to use the connection.")
    print("   from amos_openclaws_bridge import AMOSOpenClawsBridge")
    print("   bridge = AMOSOpenClawsBridge()")
    print("   asyncio.run(bridge.initialize())")
