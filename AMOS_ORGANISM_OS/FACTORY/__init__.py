"""FACTORY module — Alias for 13_FACTORY"""

import importlib.util
from pathlib import Path

# Load modules from 13_FACTORY using importlib
_13_FACTORY_PATH = Path(__file__).parent.parent / "13_FACTORY"

# agent_factory
_spec_af = importlib.util.spec_from_file_location(
    "_agent_fact", _13_FACTORY_PATH / "agent_factory.py"
)
_mod_af = importlib.util.module_from_spec(_spec_af)
_spec_af.loader.exec_module(_mod_af)
AgentFactory = _mod_af.AgentFactory
AgentSpec = _mod_af.AgentSpec
AgentInstance = _mod_af.AgentInstance

# builder_engine
_spec_be = importlib.util.spec_from_file_location(
    "_build_eng", _13_FACTORY_PATH / "builder_engine.py"
)
_mod_be = importlib.util.module_from_spec(_spec_be)
_spec_be.loader.exec_module(_mod_be)
BuilderEngine = _mod_be.BuilderEngine
BuildTask = _mod_be.BuildTask
BuildResult = _mod_be.BuildResult

# code_generator
_spec_cg = importlib.util.spec_from_file_location(
    "_code_gen", _13_FACTORY_PATH / "code_generator.py"
)
_mod_cg = importlib.util.module_from_spec(_spec_cg)
_spec_cg.loader.exec_module(_mod_cg)
CodeGenerator = _mod_cg.CodeGenerator
CodeTemplate = _mod_cg.CodeTemplate
GeneratedCode = _mod_cg.GeneratedCode

# quality_checker
_spec_qc = importlib.util.spec_from_file_location(
    "_qual_check", _13_FACTORY_PATH / "quality_checker.py"
)
_mod_qc = importlib.util.module_from_spec(_spec_qc)
_spec_qc.loader.exec_module(_mod_qc)
QualityChecker = _mod_qc.QualityChecker
QualityReport = _mod_qc.QualityReport

__all__ = [
    "AgentFactory",
    "AgentSpec",
    "AgentInstance",
    "CodeGenerator",
    "CodeTemplate",
    "GeneratedCode",
    "BuilderEngine",
    "BuildTask",
    "BuildResult",
    "QualityChecker",
    "QualityReport",
]
