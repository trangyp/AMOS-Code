"""FACTORY module — Alias for 13_FACTORY"""

import sys
from pathlib import Path

factory_path = Path(__file__).parent.parent / "13_FACTORY"
if str(factory_path) not in sys.path:
    sys.path.insert(0, str(factory_path))

from agent_factory import AgentFactory, AgentSpec, AgentInstance
from code_generator import CodeGenerator, CodeTemplate, GeneratedCode
from builder_engine import BuilderEngine, BuildTask, BuildResult
from quality_checker import QualityChecker, QualityReport

__all__ = [
    "AgentFactory", "AgentSpec", "AgentInstance",
    "CodeGenerator", "CodeTemplate", "GeneratedCode",
    "BuilderEngine", "BuildTask", "BuildResult",
    "QualityChecker", "QualityReport",
]
