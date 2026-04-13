"""
13_FACTORY — Code Generation & Agent Factory
=============================================

The manufacturing layer of AMOS.
Creates code, agents, and subsystems automatically.

Role: Code generation, automated building, agent creation
Kernel refs: FACTORY_KERNEL, BUILD_KERNEL

Owner: Trang
Version: 1.0.0
"""

from .agent_factory import AgentFactory, AgentSpec, AgentInstance
from .code_generator import CodeGenerator, CodeTemplate, GeneratedCode
from .builder_engine import BuilderEngine, BuildTask, BuildResult
from .quality_checker import QualityChecker, QualityReport

__all__ = [
    # Agent factory
    "AgentFactory",
    "AgentSpec",
    "AgentInstance",
    # Code generation
    "CodeGenerator",
    "CodeTemplate",
    "GeneratedCode",
    # Builder engine
    "BuilderEngine",
    "BuildTask",
    "BuildResult",
    # Quality checking
    "QualityChecker",
    "QualityReport",
]
