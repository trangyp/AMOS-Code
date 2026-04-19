"""AXIOM One - Technical Operating System

Core architecture: Operator + Swarm + Twin + Ledger

- ExecutionSlot: Fundamental unit of work (replaces "conversation")
- Operator: Local-first developer surface (beats Claude Code)
- Swarm: Multi-agent scheduler (beats Devin)
- Twin: Digital twin of codebase and runtime
- Ledger: Governance, audit, and economics layer

Version: 3.0.0
"""

__version__ = "3.0.0"
__author__ = "AMOS System"

from .backend_integration import (
    BackendIntegratedOrchestrator,
    BackendIntegrationConfig,
    get_backend_orchestrator,
)
from .brain_integration import BrainExecutionConfig, BrainPoweredOrchestrator
from .cli import main as cli_main
from .execution_slot import (
    AcceptanceCriteria,
    EnvironmentSnapshot,
    ExecutionSlot,
    ExecutionSlotManager,
    RepoSnapshot,
    RollbackPath,
    SlotBudget,
    SlotMode,
    SlotStatus,
    ToolPermissions,
)
from .ledger import AuditReceipt, Ledger, PolicyRule
from .operator import Operator, OperatorConfig
from .orchestrator import AxiomOne, OrchestratorConfig
from .swarm import AgentRole, SubTask, Swarm, SwarmConfig, TaskDAG
from .twin import EnvironmentState, Twin

__all__ = [
    "ExecutionSlot",
    "ExecutionSlotManager",
    "SlotMode",
    "SlotStatus",
    "RepoSnapshot",
    "EnvironmentSnapshot",
    "ToolPermissions",
    "SlotBudget",
    "AcceptanceCriteria",
    "RollbackPath",
    "Operator",
    "OperatorConfig",
    "Swarm",
    "SwarmConfig",
    "TaskDAG",
    "SubTask",
    "AgentRole",
    "Twin",
    "EnvironmentState",
    "Ledger",
    "AuditReceipt",
    "PolicyRule",
    "AxiomOne",
    "OrchestratorConfig",
    "BrainPoweredOrchestrator",
    "BrainExecutionConfig",
    "BackendIntegratedOrchestrator",
    "BackendIntegrationConfig",
    "get_backend_orchestrator",
    "cli_main",
]
