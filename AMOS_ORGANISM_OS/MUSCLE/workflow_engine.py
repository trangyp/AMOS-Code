"""MUSCLE workflow_engine stub — Re-exports from 06_MUSCLE"""

import importlib.util
from pathlib import Path

# Load from 06_MUSCLE using importlib
_muscle_path = Path(__file__).parent.parent / "06_MUSCLE" / "workflow_engine.py"
_spec = importlib.util.spec_from_file_location("_wf_eng", _muscle_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
WorkflowEngine = _mod.WorkflowEngine
Workflow = _mod.Workflow
WorkflowStep = _mod.WorkflowStep
StepStatus = _mod.StepStatus

__all__ = ["WorkflowEngine", "Workflow", "WorkflowStep", "StepStatus"]
