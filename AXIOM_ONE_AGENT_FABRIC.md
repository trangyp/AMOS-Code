# Axiom One: Agent Fabric (Layer 10)
## Bounded AI Labor System

The Agent Fabric is the **formal labor layer** where AI agents operate as bounded, deterministic workers—not chat assistants.

---

## 10.1 Agent Classes

| Class | Role | Tools | Scope | Budget |
|-------|------|-------|-------|--------|
| `repo-debugger` | Fix broken repos | read, patch, test, git | Single repo | $10/run |
| `patch-engineer` | Implement features | read, write, test, PR | Feature branch | $50/run |
| `dependency-doctor` | Fix dependency issues | scan, update, lock, test | Dependencies | $20/run |
| `packaging-doctor` | Fix packaging | setup.py, pyproject.toml, CI | Packaging | $15/run |
| `infra-debugger` | Fix infrastructure | terraform, k8s, logs | Infrastructure | $30/run |
| `db-migration-planner` | Plan migrations | schema, data, rollback | Database | $25/run |
| `release-manager` | Manage releases | tag, deploy, notify, rollback | Release | $40/run |
| `observability-analyst` | Analyze metrics | query, alert, dashboard | Telemetry | $20/run |
| `incident-commander` | Coordinate incidents | page, mitigate, communicate | Incident | $100/run |
| `security-auditor` | Security reviews | scan, analyze, report | Security | $50/run |
| `compliance-operator` | Compliance checks | audit, evidence, attest | Compliance | $35/run |
| `doc-synchronizer` | Sync documentation | read, write, link, verify | Docs | $10/run |
| `architecture-reasoner` | Design systems | model, simulate, validate | Architecture | $75/run |
| `test-writer` | Generate tests | analyze, write, validate | Tests | $25/run |
| `performance-optimizer` | Optimize code | profile, analyze, patch | Performance | $40/run |
| `cost-optimizer` | Optimize costs | analyze, recommend, implement | FinOps | $30/run |
| `product-analyst` | Analyze features | metrics, feedback, impact | Product | $20/run |
| `support-triager` | Route tickets | classify, prioritize, assign | Support | $15/run |

---

## 10.2 Agent Anatomy

```python
@dataclass(frozen=True)
class AgentIdentity:
    """Immutable agent identity."""
    id: str
    class_id: str  # repo-debugger, etc.
    version: str
    created_at: datetime
    authorized_by: str  # Person who created/approved
    
@dataclass(frozen=True)
class AgentPermissions:
    """What this agent can do."""
    tools: list[str]  # Primitive IDs
    read_scope: list[str]  # File patterns
    write_scope: list[str]  # File patterns
    exec_scope: list[str]  # Commands allowed
    network_policy: Literal["isolated", "restricted", "full"]
    max_file_size: int  # Bytes
    max_runtime_sec: float
    
@dataclass(frozen=True)
class AgentBudget:
    """Economic constraints on agent."""
    max_usd: float
    max_tokens: int
    max_api_calls: int
    max_compute_sec: float
    current_spend: float = 0.0
    
@dataclass(frozen=True)
class AgentRun:
    """Single agent execution context."""
    id: str
    agent: AgentIdentity
    task: AgentTask
    budget: AgentBudget
    permissions: AgentPermissions
    status: Literal["planning", "executing", "verifying", "completed", "failed"]
    
    # Execution trace
    observations: list[Observation]
    plan: ExecutionPlan | None
    actions: list[Action]
    receipts: list[Receipt]
    
    # Human oversight
    approval_requests: list[ApprovalRequest]
    escalations: list[Escalation]
    
    # Rollback
    rollback_available: bool
    rollback_checkpoint: str | None
```

---

## 10.3 Agent Run Phases

```python
class AgentRunPhase(Enum):
    """Standard agent execution phases."""
    
    OBSERVE = "observe"           # 1. Gather evidence
    MODEL = "model"               # 2. Build understanding
    FAULT_TREE = "fault_tree"     # 3. Identify failure modes
    PLAN = "plan"                 # 4. Generate execution plan
    SIMULATE = "simulate"         # 5. Predict outcomes
    APPROVE = "approve"           # 6. Request human approval if needed
    EXECUTE = "execute"           # 7. Execute plan
    VERIFY = "verify"             # 8. Validate results
    RECEIPT = "receipt"           # 9. Emit completion receipt
    STANDBY = "standby"           # 10. Available for follow-up

@dataclass
class AgentRunState:
    """State machine for agent execution."""
    phase: AgentRunPhase
    phase_started_at: datetime
    phase_deadline: datetime | None
    can_rollback: bool
    human_paused: bool
    
    async def transition(self, to_phase: AgentRunPhase) -> None:
        """Validate and execute phase transition."""
        # Valid transitions only
        valid = {
            AgentRunPhase.OBSERVE: [AgentRunPhase.MODEL, AgentRunPhase.FAILED],
            AgentRunPhase.MODEL: [AgentRunPhase.FAULT_TREE, AgentRunPhase.FAILED],
            AgentRunPhase.FAULT_TREE: [AgentRunPhase.PLAN, AgentRunPhase.FAILED],
            AgentRunPhase.PLAN: [AgentRunPhase.SIMULATE, AgentRunPhase.FAILED],
            AgentRunPhase.SIMULATE: [AgentRunPhase.APPROVE, AgentRunPhase.EXECUTE, AgentRunPhase.FAILED],
            AgentRunPhase.APPROVE: [AgentRunPhase.EXECUTE, AgentRunPhase.FAILED],
            AgentRunPhase.EXECUTE: [AgentRunPhase.VERIFY, AgentRunPhase.ROLLBACK, AgentRunPhase.FAILED],
            AgentRunPhase.VERIFY: [AgentRunPhase.RECEIPT, AgentRunPhase.ROLLBACK, AgentRunPhase.FAILED],
            AgentRunPhase.RECEIPT: [AgentRunPhase.STANDBY, AgentRunPhase.FAILED],
            AgentRunPhase.STANDBY: [AgentRunPhase.COMPLETED],
        }
        
        if to_phase not in valid.get(self.phase, []):
            raise InvalidPhaseTransition(self.phase, to_phase)
            
        self.phase = to_phase
        self.phase_started_at = datetime.utcnow()
```

---

## 10.4 Agent Receipts (Non-Negotiable)

Every agent run MUST emit:

```python
@dataclass(frozen=True)
class AgentReceipt:
    """Immutable record of agent work."""
    
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
    commands_run: list[CommandRecord]
    
    # Outcomes
    actions_taken: list[Action]
    test_results: list[TestResult]
    policy_checks: list[PolicyCheck]
    
    # Failures
    failures: list[Failure]
    partial_success: bool
    
    # Audit
    duration_ms: float
    cost_usd: float
    tokens_used: int
    approval_events: list[ApprovalEvent]
    
    # Rollback
    rollback_available: bool
    rollback_procedure: str | None
    rollback_verified: bool
    
    # Hash for integrity
    content_hash: str
    signature: str  # Signed by agent identity
```

---

## 10.5 Implementation: Agent Fabric Kernel

```python
class AgentFabricKernel:
    """Kernel for bounded AI labor."""
    
    def __init__(self):
        self._agents: dict[str, AgentIdentity] = {}
        self._runs: dict[str, AgentRun] = {}
        self._receipts: EventStore[AgentReceipt]
        self._budget_tracker: BudgetTracker
        self._approval_queue: ApprovalQueue
        
    async def register_agent(
        self,
        agent_class: str,
        permissions: AgentPermissions,
        budget_template: AgentBudget,
        authorized_by: str
    ) -> AgentIdentity:
        """Register new agent class."""
        agent = AgentIdentity(
            id=generate_ulid(),
            class_id=agent_class,
            version="1.0.0",
            created_at=datetime.utcnow(),
            authorized_by=authorized_by
        )
        self._agents[agent.id] = agent
        await self._emit_event("AGENT_REGISTERED", agent)
        return agent
        
    async def spawn_run(
        self,
        agent_id: str,
        task: AgentTask,
        context: dict[str, Any]
    ) -> AgentRun:
        """Spawn new agent run with budget and permissions."""
        agent = self._agents[agent_id]
        
        # Create budget instance
        budget = self._budget_tracker.allocate(agent_id, task)
        
        # Create run
        run = AgentRun(
            id=generate_ulid(),
            agent=agent,
            task=task,
            budget=budget,
            permissions=self._derive_permissions(agent, task),
            status=AgentRunPhase.OBSERVE,
            observations=[],
            plan=None,
            actions=[],
            receipts=[],
            approval_requests=[],
            escalations=[],
            rollback_available=True,
            rollback_checkpoint=await self._create_checkpoint(context)
        )
        
        self._runs[run.id] = run
        
        # Start execution
        asyncio.create_task(self._execute_run(run))
        
        return run
        
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
            if self._requires_approval(run.plan):
                approved = await self._request_approval(run)
                if not approved:
                    await self._emit_receipt(run, cancelled=True)
                    return
            
            # Phase 7: Execute
            await self._phase_execute(run)
            
            # Phase 8: Verify
            verified = await self._phase_verify(run)
            if not verified:
                await self._handle_verification_failure(run)
                return
            
            # Phase 9: Receipt
            receipt = await self._emit_receipt(run, success=True)
            
            # Phase 10: Standby
            await self._phase_standby(run)
            
        except Exception as e:
            await self._handle_execution_failure(run, e)
            
    async def rollback(self, run_id: str) -> RollbackResult:
        """Rollback agent run to checkpoint."""
        run = self._runs[run_id]
        
        if not run.rollback_available:
            raise RollbackNotAvailable(run_id)
            
        # Restore checkpoint
        await self._restore_checkpoint(run.rollback_checkpoint)
        
        # Reverse actions in reverse order
        for action in reversed(run.actions):
            if action.reversible:
                await self._reverse_action(action)
                
        return RollbackResult(success=True, run_id=run_id)
```

---

## 10.6 Human Interface: Agent Control

```python
class AgentControlInterface:
    """Human interface for agent oversight."""
    
    async def get_agent_status(self, run_id: str) -> AgentStatus:
        """Get current agent run status."""
        
    async def pause_agent(self, run_id: str, reason: str) -> None:
        """Pause agent at next checkpoint."""
        
    async def resume_agent(self, run_id: str) -> None:
        """Resume paused agent."""
        
    async def approve_action(self, request_id: str) -> None:
        """Approve pending agent action."""
        
    async def reject_action(self, request_id: str, reason: str) -> None:
        """Reject pending agent action."""
        
    async def escalate_to_human(self, run_id: str, reason: str) -> None:
        """Escalate agent run to human operator."""
        
    async def force_rollback(self, run_id: str) -> RollbackResult:
        """Force immediate rollback."""
```

This is the **formal labor layer** that makes AI deterministic, bounded, and economically accountable.
