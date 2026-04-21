"""Bridge connecting AMOS Kernel 8 Buses to AMOS Brain.

This module provides the actual integration between:
- amos_kernel (8 integration buses, engine loader, fastapi)
- amos_brain (super brain, thinking engine, cognitive runtime)

Usage:
    bridge = get_brain_kernel_bridge()
    await bridge.initialize()
    
    # Use brain through kernel buses
    result = await bridge.process_via_model_bus("Hello from brain")
    
    # Or use directly
    brain = bridge.get_brain()
    buses = bridge.get_bus_coordinator()
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

# Kernel imports
from amos_kernel import (
    BusType,
    create_llm_provider,
    get_bus_coordinator,
    get_engine_registry,
    get_unified_kernel,
)
from amos_kernel.engine_loader import AMOSEngine, EngineRegistry

# Brain imports - use try/except for optional dependencies
try:
    from amos_brain import get_brain, think, decide, validate
    from amos_brain.thinking_engine import ThinkingEngine, ThinkingMode
    from amos_brain.super_brain import SuperBrainRuntime
    BRAIN_AVAILABLE = True
except ImportError:
    BRAIN_AVAILABLE = False


@dataclass
class BrainKernelBridge:
    """Bridge between AMOS Brain and AMOS Kernel."""
    
    bus_coordinator: Any = field(default=None)
    engine_registry: EngineRegistry = field(default=None)
    brain: Any = field(default=None)
    unified_kernel: Any = field(default=None)
    llm_provider: Any = field(default=None)
    _initialized: bool = field(default=False)
    
    def __post_init__(self):
        if self.engine_registry is None:
            self.engine_registry = get_engine_registry()
        if self.bus_coordinator is None:
            self.bus_coordinator = get_bus_coordinator()
        if self.unified_kernel is None:
            self.unified_kernel = get_unified_kernel()
    
    async def initialize(self) -> None:
        """Initialize the bridge connecting brain and kernel."""
        if self._initialized:
            return
        
        # Initialize brain if available
        if BRAIN_AVAILABLE:
            self.brain = get_brain()
        
        # Initialize LLM provider
        self.llm_provider = create_llm_provider("mock")
        
        self._initialized = True
    
    def get_brain(self) -> Any:
        """Get the AMOS brain instance."""
        if not BRAIN_AVAILABLE:
            raise RuntimeError("amos_brain not available")
        return self.brain
    
    def get_bus_coordinator(self) -> Any:
        """Get the kernel bus coordinator."""
        return self.bus_coordinator
    
    def get_unified_kernel(self) -> Any:
        """Get the unified kernel."""
        return self.unified_kernel
    
    def get_engine_registry(self) -> EngineRegistry:
        """Get the engine registry with loaded engines."""
        return self.engine_registry
    
    async def process_via_model_bus(self, prompt: str, model_id: str = "mock") -> str:
        """Process text through brain using kernel's ModelBus."""
        from amos_kernel import ModelRequest
        
        model_bus = self.bus_coordinator.get_bus(BusType.MODEL)
        
        request = ModelRequest(
            model_id=model_id,
            prompt=prompt,
            parameters={}
        )
        
        # If brain is available, use it for enhanced processing
        if BRAIN_AVAILABLE and self.brain:
            # Use brain's thinking capability
            thought = await self._brain_think(prompt)
            return thought
        
        # Fallback to direct LLM provider
        response = await self.llm_provider.generate(request)
        return response.content
    
    async def _brain_think(self, query: str) -> str:
        """Use brain's thinking capability."""
        if not BRAIN_AVAILABLE:
            return f"Brain not available: {query}"
        
        try:
            # Use brain's facade for guided thinking
            from amos_brain.facade import get_brain
            brain = get_brain()
            
            # Brain-guided decision
            result = brain.think(query)
            
            # Validate the thought
            validation = brain.validate_action(
                action="think",
                context={"query": query, "result": result}
            )
            
            return str(result) if validation.get("valid", True) else str(validation)
        except Exception as e:
            return f"Brain error: {e}"
    
    async def store_in_memory(self, content: str, domain: str = "general") -> str:
        """Store content via kernel's MemoryBus."""
        memory_bus = self.bus_coordinator.get_bus(BusType.MEMORY)
        
        entry_id = f"mem_{datetime.now(timezone.utc).isoformat()}"
        
        # Create memory entry
        entry = {
            "entry_id": entry_id,
            "content": content,
            "domain": domain,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Publish to memory bus
        await memory_bus.publish({
            "topic": "memory.store",
            "payload": entry
        })
        
        return entry_id
    
    async def execute_tool(self, tool_id: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute tool via kernel's ToolBus."""
        tool_bus = self.bus_coordinator.get_bus(BusType.TOOL)
        
        # Publish tool execution request
        await tool_bus.publish({
            "topic": f"tool.execute.{tool_id}",
            "payload": {
                "tool_id": tool_id,
                "arguments": arguments
            }
        })
        
        return {"executed": True, "tool_id": tool_id}
    
    async def run_code(self, code: str, language: str = "python") -> dict[str, Any]:
        """Execute code via kernel's RuntimeBus."""
        runtime_bus = self.bus_coordinator.get_bus(BusType.RUNTIME)
        
        from amos_kernel import RuntimeExecution
        
        execution = RuntimeExecution(
            code=code,
            language=language,
            timeout_seconds=30.0
        )
        
        result = await runtime_bus.execute(execution)
        
        return {
            "success": result.success,
            "output": result.stdout,
            "errors": result.stderr if result.stderr else None
        }
    
    async def apply_policy(self, action: str, context: dict[str, Any]) -> dict[str, Any]:
        """Apply policy via kernel's PolicyBus."""
        policy_bus = self.bus_coordinator.get_bus(BusType.POLICY)
        
        from amos_kernel import PolicyRequest
        
        request = PolicyRequest(
            action=action,
            context=context
        )
        
        result = await policy_bus.evaluate(request)
        
        return {
            "allowed": result.decision == "allow",
            "decision": result.decision,
            "explanation": result.explanation
        }
    
    def get_all_buses(self) -> dict[str, Any]:
        """Get all 8 buses with their types."""
        return {
            "model": self.bus_coordinator.get_bus(BusType.MODEL),
            "memory": self.bus_coordinator.get_bus(BusType.MEMORY),
            "tool": self.bus_coordinator.get_bus(BusType.TOOL),
            "protocol": self.bus_coordinator.get_bus(BusType.PROTOCOL),
            "runtime": self.bus_coordinator.get_bus(BusType.RUNTIME),
            "frontend": self.bus_coordinator.get_bus(BusType.FRONTEND),
            "policy": self.bus_coordinator.get_bus(BusType.POLICY),
            "sync": self.bus_coordinator.get_bus(BusType.SYNC),
        }
    
    def list_engines(self) -> list[AMOSEngine]:
        """List all loaded AMOS engines."""
        return self.engine_registry.list_engines()
    
    async def health_check(self) -> dict[str, Any]:
        """Health check for bridge and all components."""
        health = {
            "bridge": "healthy",
            "brain_available": BRAIN_AVAILABLE,
            "brain_initialized": self.brain is not None,
            "kernel": "healthy",
            "buses": {}
        }
        
        # Check all buses
        for bus_type in BusType:
            bus = self.bus_coordinator.get_bus(bus_type)
            bus_health = await bus.health_check()
            health["buses"][bus_type.value] = bus_health.get("status", "unknown")
        
        return health


# Global bridge instance
_bridge: BrainKernelBridge | None = None


def get_brain_kernel_bridge() -> BrainKernelBridge:
    """Get or create the brain-kernel bridge singleton."""
    global _bridge
    if _bridge is None:
        _bridge = BrainKernelBridge()
    return _bridge


# Convenience functions
async def process_with_brain(prompt: str) -> str:
    """Process text using brain through kernel buses."""
    bridge = get_brain_kernel_bridge()
    if not bridge._initialized:
        await bridge.initialize()
    return await bridge.process_via_model_bus(prompt)


async def store_memory(content: str, domain: str = "general") -> str:
    """Store content in memory via kernel."""
    bridge = get_brain_kernel_bridge()
    if not bridge._initialized:
        await bridge.initialize()
    return await bridge.store_in_memory(content, domain)


async def execute_code(code: str, language: str = "python") -> dict[str, Any]:
    """Execute code via kernel runtime bus."""
    bridge = get_brain_kernel_bridge()
    if not bridge._initialized:
        await bridge.initialize()
    return await bridge.run_code(code, language)
