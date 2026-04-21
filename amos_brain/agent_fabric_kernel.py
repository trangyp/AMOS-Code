"""Agent Fabric Kernel - Bounded AI Labor System for Axiom One.

This implements Layer 10 of the Axiom One civilization substrate:
Deterministic, bounded, economically-accountable AI labor.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc


from enum import StrEnum
from typing import Any

# ============================================================================
# Core Types
# ============================================================================


class AgentRunPhase(StrEnum):
    """Standard phases for agent execution."""

    OBSERVE = "observe"
    MODEL = "model"
    FAULT_TREE = "fault_tree"
    PLAN = "plan"
    SIMULATE = "simulate"
    APPROVE = "approve"
    EXECUTE = "execute"
    VERIFY = "verify"
    RECEIPT = "receipt"
    STANDBY = "standby"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLBACK = "rollback"


class AgentClass(StrEnum):
    """Predefined agent classes with bounded capabilities."""

    REPO_DEBUGGER = "repo-debugger"
    PATCH_ENGINEER = "patch-engineer"
    DEPENDENCY_DOCTOR = "dependency-doctor"
    PACKAGING_DOCTOR = "packaging-doctor"
    INFRA_DEBUGGER = "infra-debugger"
    DB_MIGRATION_PLANNER = "db-migration-planner"
    RELEASE_MANAGER = "release-manager"
    OBSERVABILITY_ANALYST = "observability-analyst"
    INCIDENT_COMMANDER = "incident-commander"
    SECURITY_AUDITOR = "security-auditor"
    COMPLIANCE_OPERATOR = "compliance-operator"
    DOC_SYNCHRONIZER = "doc-synchronizer"
    ARCHITECTURE_REASONER = "architecture-reasoner"
    TEST_WRITER = "test-writer"
    PERFORMANCE_OPTIMIZER = "performance-optimizer"
    COST_OPTIMIZER = "cost-optimizer"
    PRODUCT_ANALYST = "product-analyst"
    SUPPORT_TRIAGER = "support-triager"


@dataclass(frozen=True)
class AgentIdentity:
    """Immutable agent identity."""

    id: str
    class_id: str
    version: str
    created_at: datetime
    authorized_by: str

    def __post_init__(self):
        object.__setattr__(self, "id", str(uuid.uuid4())[:16])


@dataclass
class AgentPermissions:
    """What this agent can do - bounded scope."""

    tools: list[str] = field(default_factory=list)
    read_scope: list[str] = field(default_factory=list)  # File patterns
    write_scope: list[str] = field(default_factory=list)  # File patterns
    exec_scope: list[str] = field(default_factory=list)  # Commands allowed
    network_policy: str = "isolated"  # isolated, restricted, full
    max_file_size: int = 10_000_000  # 10MB
    max_runtime_sec: float = 300.0  # 5 minutes


@dataclass
class AgentBudget:
    """Economic constraints on agent - always enforced."""

    max_usd: float = 10.0
    max_tokens: int = 100_000
    max_api_calls: int = 50
    max_compute_sec: float = 300.0
    current_spend: float = 0.0

    def remaining(self) -> float:
        return self.max_usd - self.current_spend

    def can_afford(self, cost: float) -> bool:
        return self.current_spend + cost <= self.max_usd


@dataclass
class AgentTask:
    """Task definition for agent execution."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    objective: str = ""
    inputs: dict[str, Any] = field(default_factory=dict)
    success_criteria: list[str] = field(default_factory=list)
    priority: str = "p2"  # p0, p1, p2, p3


@dataclass
class Observation:
    """Observation from the environment."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: str = ""  # file, log, metric, error, command_output
    source: str = ""  # Where this came from
    content: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Action:
    """Action taken by agent."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: str = ""  # read_file, write_file, run_command, api_call
    params: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] = field(default_factory=dict)
    cost_usd: float = 0.0
    reversible: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ApprovalRequest:
    """Request for human approval."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    action_id: str = ""
    reason: str = ""
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    approved: bool = None
    approved_by: str = None
    approved_at: datetime = None


@dataclass
class Escalation:
    """Escalation to human operator."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    reason: str = ""
    escalated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False
    resolved_at: datetime = None


@dataclass
class AgentReceipt:
    """Immutable record of agent work - NON-NEGOTIABLE."""

    # Identity
    run_id: str
    agent_id: str
    agent_class: str
    version: str

    # Intent
    objective: str
    success_criteria: list[str]

    # Evidence
    observations: list[Observation]
    files_read: list[str]
    files_changed: list[str]
    commands_run: list[dict]

    # Outcomes
    actions_taken: list[Action]
    test_results: list[dict]
    policy_checks: list[dict]

    # Failures
    failures: list[dict]
    partial_success: bool

    # Audit
    duration_ms: float
    cost_usd: float
    tokens_used: int
    approval_events: list[dict]

    # Rollback
    rollback_available: bool
    rollback_procedure: str
    rollback_verified: bool

    # Integrity
    content_hash: str
    signature: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def compute_hash(self) -> str:
        """Compute content hash for integrity verification."""
        content = {
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "objective": self.objective,
            "actions": [a.type for a in self.actions_taken],
            "files_changed": self.files_changed,
            "cost_usd": self.cost_usd,
            "timestamp": self.timestamp.isoformat(),
        }
        return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()[:32]

    def __post_init__(self):
        if not self.content_hash:
            object.__setattr__(self, "content_hash", self.compute_hash())


@dataclass
class AgentRun:
    """Single agent execution context."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:16])
    agent: AgentIdentity = None
    task: AgentTask = None
    budget: AgentBudget = field(default_factory=AgentBudget)
    permissions: AgentPermissions = field(default_factory=AgentPermissions)
    phase: str = AgentRunPhase.OBSERVE

    # Execution trace
    observations: list[Observation] = field(default_factory=list)
    plan: dict = None
    actions: list[Action] = field(default_factory=list)

    # Human oversight
    approval_requests: list[ApprovalRequest] = field(default_factory=list)
    escalations: list[Escalation] = field(default_factory=list)

    # Rollback
    rollback_available: bool = True
    rollback_checkpoint: str = None

    # Timing
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: datetime = None

    def to_receipt(self) -> AgentReceipt:
        """Generate receipt from completed run."""
        duration = 0.0
        if self.ended_at:
            duration = (self.ended_at - self.started_at).total_seconds() * 1000

        return AgentReceipt(
            run_id=self.id,
            agent_id=self.agent.id if self.agent else "",
            agent_class=self.agent.class_id if self.agent else "",
            version=self.agent.version if self.agent else "",
            objective=self.task.objective if self.task else "",
            success_criteria=self.task.success_criteria if self.task else [],
            observations=self.observations,
            files_read=list(set(o.source for o in self.observations if o.type == "file")),
            files_changed=[
                a.params.get("path", "") for a in self.actions if a.type == "write_file"
            ],
            commands_run=[
                {"command": a.params.get("command", ""), "exit_code": a.result.get("exit_code", 0)}
                for a in self.actions
                if a.type == "run_command"
            ],
            actions_taken=self.actions,
            test_results=[],  # Populated by validator
            policy_checks=[],  # Populated by governance
            failures=[
                {"action_id": a.id, "error": a.result.get("error", "")}
                for a in self.actions
                if a.result.get("error")
            ],
            partial_success=any(a.result.get("error") for a in self.actions),
            duration_ms=duration,
            cost_usd=self.budget.current_spend,
            tokens_used=0,  # Tracked by LLM provider
            approval_events=[
                {"id": r.id, "approved": r.approved}
                for r in self.approval_requests
                if r.approved is not None
            ],
            rollback_available=self.rollback_available,
            rollback_procedure="Auto-generated rollback" if self.rollback_available else None,
            rollback_verified=False,
            content_hash="",  # Computed in post_init
            signature="",  # Signed by agent fabric
        )


# ============================================================================
# Agent Class Definitions
# ============================================================================

AGENT_CLASS_DEFINITIONS: dict[str, dict] = {
    AgentClass.REPO_DEBUGGER: {
        "tools": ["read_file", "write_file", "run_command", "git_status", "search_code"],
        "read_scope": ["**/*"],
        "write_scope": [
            "**/*.py",
            "**/*.js",
            "**/*.ts",
            "**/*.json",
            "**/*.yaml",
            "**/*.yml",
            "**/*.md",
        ],
        "exec_scope": ["git", "python", "pytest", "npm", "pip"],
        "network_policy": "isolated",
        "max_runtime_sec": 300,
        "budget": {"max_usd": 10.0, "max_tokens": 100_000},
    },
    AgentClass.PATCH_ENGINEER: {
        "tools": ["read_file", "write_file", "run_command", "search_code", "compare_versions"],
        "read_scope": ["**/*"],
        "write_scope": ["**/*.py", "**/*.js", "**/*.ts", "**/*.jsx", "**/*.tsx"],
        "exec_scope": ["python", "pytest", "npm", "eslint"],
        "network_policy": "isolated",
        "max_runtime_sec": 600,
        "budget": {"max_usd": 50.0, "max_tokens": 200_000},
    },
    AgentClass.DEPENDENCY_DOCTOR: {
        "tools": ["read_file", "write_file", "run_command", "search_code"],
        "read_scope": [
            "**/requirements*.txt",
            "**/package.json",
            "**/pyproject.toml",
            "**/setup.py",
            "**/Pipfile",
            "**/poetry.lock",
        ],
        "write_scope": [
            "**/requirements*.txt",
            "**/package.json",
            "**/pyproject.toml",
            "**/setup.py",
            "**/Pipfile",
        ],
        "exec_scope": ["pip", "npm", "poetry", "pipenv"],
        "network_policy": "restricted",  # Needs package registry
        "max_runtime_sec": 300,
        "budget": {"max_usd": 20.0, "max_tokens": 50_000},
    },
    AgentClass.INCIDENT_COMMANDER: {
        "tools": ["read_file", "run_command", "query_metrics", "page_oncall", "send_notification"],
        "read_scope": ["**/*"],
        "write_scope": [],  # Read-only except runbooks
        "exec_scope": ["kubectl", "aws", "gcloud", "terraform"],
        "network_policy": "full",
        "max_runtime_sec": 1800,
        "budget": {"max_usd": 100.0, "max_tokens": 300_000},
    },
}


# ============================================================================
# Agent Fabric Kernel
# ============================================================================


class BudgetTracker:
    """Track agent spending with hard limits."""

    def __init__(self):
        self._allocations: dict[str, AgentBudget] = {}
        self._spent: dict[str, float] = {}

    def allocate(self, agent_id: str, task: AgentTask) -> AgentBudget:
        """Allocate budget for agent run."""
        # Get agent class from registry
        budget = AgentBudget()
        self._allocations[agent_id] = budget
        return budget

    def spend(self, run_id: str, amount: float) -> bool:
        """Record spending, return False if over budget."""
        if run_id not in self._allocations:
            return False

        budget = self._allocations[run_id]
        if budget.can_afford(amount):
            budget.current_spend += amount
            return True
        return False

    def get_remaining(self, run_id: str) -> float:
        """Get remaining budget."""
        if run_id not in self._allocations:
            return 0.0
        return self._allocations[run_id].remaining()


class ApprovalQueue:
    """Queue for human approval requests."""

    def __init__(self):
        self._pending: dict[str, ApprovalRequest] = {}
        self._resolved: dict[str, ApprovalRequest] = {}

    async def request(self, action_id: str, reason: str) -> str:
        """Request approval, return request ID."""
        req = ApprovalRequest(action_id=action_id, reason=reason)
        self._pending[req.id] = req

        # In real implementation, notify via Slack/PagerDuty/email
        print(f"[APPROVAL REQUEST] {req.id}: {reason}")

        return req.id

    def approve(self, request_id: str, approved_by: str) -> bool:
        """Approve a pending request."""
        if request_id not in self._pending:
            return False

        req = self._pending.pop(request_id)
        req.approved = True
        req.approved_by = approved_by
        req.approved_at = datetime.now(timezone.utc)
        self._resolved[request_id] = req
        return True

    def reject(self, request_id: str, rejected_by: str) -> bool:
        """Reject a pending request."""
        if request_id not in self._pending:
            return False

        req = self._pending.pop(request_id)
        req.approved = False
        req.approved_by = rejected_by
        req.approved_at = datetime.now(timezone.utc)
        self._resolved[request_id] = req
        return True

    def get_status(self, request_id: str) -> str:
        """Get approval status."""
        if request_id in self._pending:
            return "pending"
        if request_id in self._resolved:
            req = self._resolved[request_id]
            return "approved" if req.approved else "rejected"
        return None


class AgentFabricKernel:
    """Kernel for bounded AI labor."""

    def __init__(self):
        self._agents: dict[str, AgentIdentity] = {}
        self._runs: dict[str, AgentRun] = {}
        self._receipts: list[AgentReceipt] = []
        self._budget_tracker = BudgetTracker()
        self._approval_queue = ApprovalQueue()
        self._running: dict[str, asyncio.Task] = {}

    def register_agent(
        self,
        agent_class: str,
        authorized_by: str,
        custom_permissions: AgentPermissions = None,
    ) -> AgentIdentity:
        """Register new agent with class-defined permissions."""

        # Get class definition
        class_def = AGENT_CLASS_DEFINITIONS.get(agent_class, {})

        # Create permissions from class or custom
        if custom_permissions:
            permissions = custom_permissions
        else:
            permissions = AgentPermissions(
                tools=class_def.get("tools", []),
                read_scope=class_def.get("read_scope", []),
                write_scope=class_def.get("write_scope", []),
                exec_scope=class_def.get("exec_scope", []),
                network_policy=class_def.get("network_policy", "isolated"),
                max_runtime_sec=class_def.get("max_runtime_sec", 300),
            )

        # Create identity
        agent = AgentIdentity(
            id="",
            class_id=agent_class,
            version="1.0.0",
            created_at=datetime.now(timezone.utc),
            authorized_by=authorized_by,
        )

        self._agents[agent.id] = agent
        print(f"[AGENT REGISTERED] {agent.id} ({agent_class})")

        return agent

    def spawn_run(self, agent_id: str, task: AgentTask, context: dict[str, Any] = None) -> AgentRun:
        """Spawn new agent run with budget and permissions."""

        agent = self._agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        # Get class definition for budget
        class_def = AGENT_CLASS_DEFINITIONS.get(agent.class_id, {})
        budget_def = class_def.get("budget", {})

        # Create budget
        budget = AgentBudget(
            max_usd=budget_def.get("max_usd", 10.0),
            max_tokens=budget_def.get("max_tokens", 100_000),
        )

        # Create permissions from class
        permissions = AgentPermissions(
            tools=class_def.get("tools", []),
            read_scope=class_def.get("read_scope", []),
            write_scope=class_def.get("write_scope", []),
            exec_scope=class_def.get("exec_scope", []),
            network_policy=class_def.get("network_policy", "isolated"),
            max_runtime_sec=class_def.get("max_runtime_sec", 300),
        )

        # Create run
        run = AgentRun(
            agent=agent,
            task=task,
            budget=budget,
            permissions=permissions,
            phase=AgentRunPhase.OBSERVE,
            rollback_checkpoint=self._create_checkpoint(context or {}),
        )

        self._runs[run.id] = run

        # Start execution
        task_coro = self._execute_run(run)
        self._running[run.id] = asyncio.create_task(task_coro)

        print(f"[AGENT RUN STARTED] {run.id} ({agent.class_id}) - {task.objective[:50]}...")

        return run

    def _create_checkpoint(self, context: dict) -> str:
        """Create rollback checkpoint."""
        # In real implementation, use git stash or snapshot
        checkpoint_id = str(uuid.uuid4())[:12]
        return checkpoint_id

    async def _execute_run(self, run: AgentRun) -> None:
        """Execute agent run through all phases."""
        try:
            # Phase 1: Observe
            await self._phase_observe(run)

            # Phase 2: Model
            await self._phase_model(run)

            # Phase 3: Fault Tree
            await self._phase_fault_tree(run)

            # Phase 4: Plan
            await self._phase_plan(run)

            # Phase 5: Simulate
            await self._phase_simulate(run)

            # Phase 6: Approve (if needed)
            if self._requires_approval(run):
                approved = await self._request_approval(run)
                if not approved:
                    run.phase = AgentRunPhase.FAILED
                    run.ended_at = datetime.now(timezone.utc)
                    self._emit_receipt(run)
                    return

            # Phase 7: Execute
            await self._phase_execute(run)

            # Phase 8: Verify
            verified = await self._phase_verify(run)
            if not verified:
                await self._handle_verification_failure(run)
                return

            # Phase 9: Receipt
            run.phase = AgentRunPhase.RECEIPT
            receipt = self._emit_receipt(run)

            # Phase 10: Standby
            run.phase = AgentRunPhase.STANDBY

        except Exception as e:
            await self._handle_execution_failure(run, e)

    async def _phase_observe(self, run: AgentRun) -> None:
        """Gather evidence from environment."""
        run.phase = AgentRunPhase.OBSERVE

        # Gather file observations
        obs = Observation(
            type="file",
            source="./",
            content="Repository structure gathered",
            metadata={"files_count": 0},  # Would be populated
        )
        run.observations.append(obs)

        # Simulate observation delay
        await asyncio.sleep(0.1)

    async def _phase_model(self, run: AgentRun) -> None:
        """Build understanding of the system."""
        run.phase = AgentRunPhase.MODEL

        # Create internal model from observations
        run.plan = {
            "understanding": f"Model of system for task: {run.task.objective if run.task else ''}",
            "key_components": [],
            "dependencies": [],
        }

        await asyncio.sleep(0.1)

    async def _phase_fault_tree(self, run: AgentRun) -> None:
        """Identify potential failure modes."""
        run.phase = AgentRunPhase.FAULT_TREE

        # Analyze what could go wrong
        # In real implementation, use AMOS brain reasoning

        await asyncio.sleep(0.1)

    async def _phase_plan(self, run: AgentRun) -> None:
        """Generate execution plan."""
        run.phase = AgentRunPhase.PLAN

        # Create plan with steps
        run.plan = {
            "steps": [
                {"action": "analyze", "target": "problem"},
                {"action": "identify", "target": "root_cause"},
                {"action": "generate", "target": "fix"},
                {"action": "validate", "target": "solution"},
            ],
            "estimated_cost": 0.5,
        }

        await asyncio.sleep(0.1)

    async def _phase_simulate(self, run: AgentRun) -> None:
        """Predict outcomes before execution."""
        run.phase = AgentRunPhase.SIMULATE

        # Run simulation of planned actions
        # Would integrate with Simulation System

        await asyncio.sleep(0.1)

    def _requires_approval(self, run: AgentRun) -> bool:
        """Determine if human approval needed."""
        # Require approval for:
        # - Write operations to production
        # - High-cost operations
        # - Security-sensitive operations

        if run.budget.max_usd > 50:
            return True

        if any("production" in str(a) for a in run.task.inputs.values() if run.task):
            return True

        return False

    async def _request_approval(self, run: AgentRun) -> bool:
        """Request human approval for execution."""
        run.phase = AgentRunPhase.APPROVE

        reason = f"Agent {run.agent.class_id} requesting approval for task with budget ${run.budget.max_usd}"
        request_id = await self._approval_queue.request(run.id, reason)

        # Wait for approval (with timeout)
        timeout = 300  # 5 minutes
        for _ in range(timeout):
            status = self._approval_queue.get_status(request_id)
            if status == "approved":
                return True
            if status == "rejected":
                return False
            await asyncio.sleep(1)

        return False  # Timeout = reject

    async def _phase_execute(self, run: AgentRun) -> None:
        """Execute planned actions."""
        run.phase = AgentRunPhase.EXECUTE

        # Execute each planned action
        if run.plan and "steps" in run.plan:
            for step in run.plan["steps"]:
                action = Action(
                    type=step["action"],
                    params={"target": step["target"]},
                    result={"status": "completed"},
                    cost_usd=0.1,
                )
                run.actions.append(action)
                run.budget.current_spend += action.cost_usd

                # Check budget
                if not run.budget.can_afford(0):
                    raise Exception("Budget exhausted")

        await asyncio.sleep(0.1)

    async def _phase_verify(self, run: AgentRun) -> bool:
        """Validate results of execution."""
        run.phase = AgentRunPhase.VERIFY

        # Run tests/checks
        # Would integrate with test runner

        await asyncio.sleep(0.1)
        return True

    async def _handle_verification_failure(self, run: AgentRun) -> None:
        """Handle case where verification fails."""
        # Attempt rollback if available
        if run.rollback_available:
            run.phase = AgentRunPhase.ROLLBACK
            await self._rollback(run)

        run.phase = AgentRunPhase.FAILED
        run.ended_at = datetime.now(timezone.utc)
        self._emit_receipt(run)

    async def _handle_execution_failure(self, run: AgentRun, error: Exception) -> None:
        """Handle execution failure."""
        run.phase = AgentRunPhase.FAILED
        run.ended_at = datetime.now(timezone.utc)

        # Log failure
        print(f"[AGENT RUN FAILED] {run.id}: {error}")

        self._emit_receipt(run)

    async def _rollback(self, run: AgentRun) -> None:
        """Rollback agent run."""
        print(f"[ROLLBACK] {run.id} to checkpoint {run.rollback_checkpoint}")
        # In real implementation, restore from git stash/snapshot

    def _emit_receipt(self, run: AgentRun) -> AgentReceipt:
        """Generate and store receipt."""
        run.ended_at = datetime.now(timezone.utc)
        receipt = run.to_receipt()
        self._receipts.append(receipt)

        print(f"[RECEIPT EMITTED] {receipt.run_id} - Cost: ${receipt.cost_usd:.2f}")

        return receipt

    def get_run(self, run_id: str) -> AgentRun:
        """Get agent run by ID."""
        return self._runs.get(run_id)

    def get_receipt(self, run_id: str) -> AgentReceipt:
        """Get receipt for completed run."""
        for receipt in self._receipts:
            if receipt.run_id == run_id:
                return receipt
        return None

    def approve_action(self, request_id: str, approved_by: str) -> bool:
        """Approve pending action."""
        return self._approval_queue.approve(request_id, approved_by)

    def list_active_runs(self) -> list[AgentRun]:
        """List all active agent runs."""
        return [
            run
            for run in self._runs.values()
            if run.phase not in (AgentRunPhase.COMPLETED, AgentRunPhase.FAILED)
        ]


# Global kernel instance
_agent_fabric_kernel: AgentFabricKernel = None


def get_agent_fabric_kernel() -> AgentFabricKernel:
    """Get or create global agent fabric kernel."""
    global _agent_fabric_kernel
    if _agent_fabric_kernel is None:
        _agent_fabric_kernel = AgentFabricKernel()
    return _agent_fabric_kernel
