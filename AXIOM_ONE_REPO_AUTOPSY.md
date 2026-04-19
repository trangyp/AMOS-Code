# Axiom One: Repo Autopsy (Repo Debugging System)
## Section 10 - Automatic Repository Fault Analysis & Repair

The Repo Autopsy system is the **automatic debugging layer** for repository failures.

---

## 10.1 Autopsy Request Types

```python
class AutopsyRequestType(Enum):
    """Types of repository failures to autopsy."""
    
    # Build Failures
    BUILD_FAILURE = "build_failure"           # Compilation, bundling, linking
    TEST_FAILURE = "test_failure"           # Test suite failures
    LINT_FAILURE = "lint_failure"           # Style/formatting violations
    TYPE_FAILURE = "type_failure"           # Type checking errors
    SECURITY_FAILURE = "security_failure"   # SAST/DAST failures
    
    # Runtime Failures
    CRASH = "crash"                         # Application crashes
    MEMORY_LEAK = "memory_leak"             # Memory consumption issues
    PERFORMANCE_DEGRADATION = "performance" # Latency/throughput issues
    DEADLOCK = "deadlock"                   # Concurrency deadlocks
    RACE_CONDITION = "race"                 # Race conditions
    
    # Integration Failures
    API_BREAKAGE = "api_breakage"           # API contract violations
    SCHEMA_BREAKAGE = "schema_breakage"     # Database schema issues
    DEPENDENCY_FAILURE = "dependency"       # Dependency resolution
    CONFIG_FAILURE = "config"               # Configuration errors
    NETWORK_FAILURE = "network"             # Network/connection issues
    
    # Deployment Failures
    DEPLOY_FAILURE = "deploy_failure"       # Deployment pipeline failures
    INFRA_FAILURE = "infra"                 # Infrastructure provisioning
    ROLLBACK_FAILURE = "rollback"           # Rollback failures
    
    # Data Failures
    DATA_CORRUPTION = "data_corruption"     # Data integrity issues
    MIGRATION_FAILURE = "migration"         # Database migration failures
    REPLICATION_FAILURE = "replication"     # Data replication issues

@dataclass
class AutopsyRequest:
    """Request for repo autopsy."""
    id: str
    type: AutopsyRequestType
    repo: RepositoryRef
    trigger:
        source: Literal["ci", "alert", "manual", "api"]
        reference: str  # CI run ID, alert ID, etc.
    evidence:
        logs: list[LogRef]
        traces: list[TraceRef]
        metrics: list[MetricRef]
        commits: list[CommitRef]
    context:
        environment: str
        deployment: DeploymentRef | None
        related_incidents: list[IncidentRef]
    priority: Literal["p0", "p1", "p2", "p3"]
    requested_by: PersonRef | None  # None = system-initiated
```

---

## 10.2 Autopsy Phases

```python
class AutopsyPhase(Enum):
    """Structured autopsy workflow."""
    
    # Phase 1: Evidence Collection
    COLLECT = "collect"
    # Phase 2: Pattern Matching  
    IDENTIFY = "identify"
    # Phase 3: Fault Localization
    LOCALIZE = "localize"
    # Phase 4: Impact Analysis
    IMPACT = "impact"
    # Phase 5: Repair Strategy
    STRATEGY = "strategy"
    # Phase 6: Fix Generation
    GENERATE = "generate"
    # Phase 7: Validation
    VALIDATE = "validate"
    # Phase 8: Report
    REPORT = "report"

@dataclass
class AutopsySession:
    """Running autopsy session."""
    request: AutopsyRequest
    phase: AutopsyPhase
    
    # Evidence
    collected_evidence: list[Evidence]
    
    # Analysis
    identified_patterns: list[FailurePattern]
    fault_locations: list[FaultLocation]
    impact_graph: ImpactGraph
    
    # Repair
    repair_strategies: list[RepairStrategy]
    generated_fixes: list[GeneratedFix]
    
    # Validation
    validation_results: list[ValidationResult]
    
    # Outcome
    report: AutopsyReport | None
    applied_fix: AppliedFix | None
```

---

## 10.3 Failure Pattern Database

```python
@dataclass
class FailurePattern:
    """Known failure pattern with diagnosis and repair."""
    
    id: str
    name: str
    category: str
    
    # Detection
    signature:
        error_patterns: list[str]  # Regex patterns
        log_patterns: list[str]
        stack_trace_patterns: list[str]
        metric_anomalies: list[MetricAnomalyPattern]
        
    # Diagnosis
    root_causes: list[RootCause]
    confidence_scoring: dict[str, float]
    
    # Repair
    repair_strategies: list[RepairStrategy]
    auto_repair_eligible: bool
    
    # Metadata
    occurrences: int
    first_seen: datetime
    last_seen: datetime
    success_rate: float  # Of auto-repairs

# Pre-defined Pattern Examples
PATTERNS = {
    "missing_import": FailurePattern(
        id="PY-001",
        name="Python Missing Import",
        category="build",
        signature={
            error_patterns=[r"ModuleNotFoundError: No module named '(.+)'"],
            log_patterns=[r"ImportError", r"cannot import"],
        },
        root_causes=[
            RootCause.MISSING_DEPENDENCY,
            RootCause.CIRCULAR_IMPORT,
            RootCause.RELATIVE_IMPORT_ISSUE,
        ],
        repair_strategies=[
            RepairStrategy.ADD_IMPORT,
            RepairStrategy.ADD_DEPENDENCY,
            RepairStrategy.FIX_CIRCULAR,
        ],
        auto_repair_eligible=True,
    ),
    
    "type_mismatch": FailurePattern(
        id="PY-002", 
        name="Python Type Mismatch",
        category="type",
        signature={
            error_patterns=[r"Incompatible types?", r"expected.*but got"],
        },
        root_causes=[
            RootCause.MISSING_TYPE_ANNOTATION,
            RootCause.INCORRECT_TYPE_CAST,
            RootCause.API_CHANGE,
        ],
        repair_strategies=[
            RepairStrategy.ADD_TYPE_HINT,
            RepairStrategy.FIX_CAST,
            RepairStrategy.UPDATE_CALL,
        ],
        auto_repair_eligible=True,
    ),
    
    "race_condition": FailurePattern(
        id="CONC-001",
        name="Race Condition",
        category="runtime",
        signature={
            log_patterns=[r"concurrent", r"race"],
            stack_trace_patterns=[r"deadlock", r"timeout"],
            metric_anomalies=[
                MetricAnomalyPattern("lock_wait_time", threshold=1.0),
            ],
        },
        root_causes=[
            RootCause.MISSING_LOCK,
            RootCause.INCORRECT_LOCK_ORDER,
            RootCause.SHARED_MUTABLE_STATE,
        ],
        repair_strategies=[
            RepairStrategy.ADD_LOCKING,
            RepairStrategy.REORDER_LOCKS,
            RepairStrategy.IMMUTABILITY,
        ],
        auto_repair_eligible=False,  # Requires human review
    ),
}
```

---

## 10.4 Autopsy Engine Implementation

```python
class RepoAutopsyEngine:
    """Engine for automatic repo debugging."""
    
    def __init__(self):
        self._pattern_db: PatternDatabase
        self._evidence_collector: EvidenceCollector
        self._fault_localizer: FaultLocalizer
        self._impact_analyzer: ImpactAnalyzer
        self._fix_generator: FixGenerator
        self._validator: FixValidator
        self._sessions: dict[str, AutopsySession]
        
    async def start_autopsy(self, request: AutopsyRequest) -> AutopsySession:
        """Start new autopsy session."""
        session = AutopsySession(
            request=request,
            phase=AutopsyPhase.COLLECT,
            collected_evidence=[],
            identified_patterns=[],
            fault_locations=[],
            impact_graph=None,
            repair_strategies=[],
            generated_fixes=[],
            validation_results=[],
            report=None,
            applied_fix=None,
        )
        
        self._sessions[session.request.id] = session
        
        # Execute autopsy phases
        asyncio.create_task(self._execute_autopsy(session))
        
        return session
        
    async def _execute_autopsy(self, session: AutopsySession) -> None:
        """Execute all autopsy phases."""
        try:
            # Phase 1: Collect Evidence
            await self._phase_collect(session)
            
            # Phase 2: Identify Patterns
            await self._phase_identify(session)
            
            # Phase 3: Localize Fault
            await self._phase_localize(session)
            
            # Phase 4: Analyze Impact
            await self._phase_impact(session)
            
            # Phase 5: Determine Strategy
            await self._phase_strategy(session)
            
            # Phase 6: Generate Fix
            await self._phase_generate(session)
            
            # Phase 7: Validate
            await self._phase_validate(session)
            
            # Phase 8: Generate Report
            await self._phase_report(session)
            
        except Exception as e:
            await self._handle_autopsy_failure(session, e)
            
    async def _phase_collect(self, session: AutopsySession) -> None:
        """Collect all available evidence."""
        evidence_tasks = [
            self._evidence_collector.collect_logs(session.request),
            self._evidence_collector.collect_traces(session.request),
            self._evidence_collector.collect_metrics(session.request),
            self._evidence_collector.collect_commits(session.request),
            self._evidence_collector.collect_artifacts(session.request),
            self._evidence_collector.collect_env(session.request),
        ]
        
        evidence = await asyncio.gather(*evidence_tasks)
        session.collected_evidence = list(chain.from_iterable(evidence))
        session.phase = AutopsyPhase.IDENTIFY
        
    async def _phase_identify(self, session: AutopsySession) -> None:
        """Match collected evidence to known patterns."""
        for pattern in self._pattern_db.all_patterns():
            score = self._match_pattern(session.collected_evidence, pattern)
            if score > 0.7:  # Threshold
                session.identified_patterns.append(
                    PatternMatch(pattern=pattern, confidence=score)
                )
                
        # Sort by confidence
        session.identified_patterns.sort(
            key=lambda p: p.confidence, 
            reverse=True
        )
        session.phase = AutopsyPhase.LOCALIZE
        
    async def _phase_localize(self, session: AutopsySession) -> None:
        """Locate exact fault positions."""
        for pattern_match in session.identified_patterns:
            locations = await self._fault_localizer.localize(
                session.collected_evidence,
                pattern_match.pattern
            )
            session.fault_locations.extend(locations)
            
        session.phase = AutopsyPhase.IMPACT
        
    async def _phase_impact(self, session: AutopsySession) -> None:
        """Analyze impact scope."""
        session.impact_graph = await self._impact_analyzer.analyze(
            session.request.repo,
            session.fault_locations
        )
        session.phase = AutopsyPhase.STRATEGY
        
    async def _phase_strategy(self, session: AutopsySession) -> None:
        """Determine repair strategy."""
        for pattern_match in session.identified_patterns:
            for strategy in pattern_match.pattern.repair_strategies:
                feasibility = await self._assess_feasibility(
                    strategy, 
                    session.fault_locations,
                    session.impact_graph
                )
                if feasibility.score > 0.5:
                    session.repair_strategies.append(
                        RepairStrategyPlan(
                            strategy=strategy,
                            feasibility=feasibility,
                            estimated_risk=feasibility.risk_score
                        )
                    )
                    
        # Sort by feasibility * success_rate
        session.repair_strategies.sort(
            key=lambda s: s.feasibility.score * s.strategy.success_rate,
            reverse=True
        )
        session.phase = AutopsyPhase.GENERATE
        
    async def _phase_generate(self, session: AutopsySession) -> None:
        """Generate actual code fixes."""
        for strategy_plan in session.repair_strategies[:3]:  # Top 3
            fix = await self._fix_generator.generate(
                strategy_plan.strategy,
                session.fault_locations,
                session.collected_evidence
            )
            if fix:
                session.generated_fixes.append(fix)
                
        session.phase = AutopsyPhase.VALIDATE
        
    async def _phase_validate(self, session: AutopsySession) -> None:
        """Validate generated fixes."""
        for fix in session.generated_fixes:
            result = await self._validator.validate(fix, session.request)
            session.validation_results.append(result)
            
        session.phase = AutopsyPhase.REPORT
        
    async def _phase_report(self, session: AutopsySession) -> None:
        """Generate autopsy report."""
        session.report = AutopsyReport(
            request=session.request,
            patterns_found=session.identified_patterns,
            fault_locations=session.fault_locations,
            impact_graph=session.impact_graph,
            proposed_fixes=[
                ProposedFix(
                    fix=fix,
                    validation=result,
                    confidence=self._compute_fix_confidence(fix, result)
                )
                for fix, result in zip(
                    session.generated_fixes, 
                    session.validation_results
                )
                if result.success
            ],
            recommended_fix=session.generated_fixes[0] if session.generated_fixes else None,
            estimated_repair_time=self._estimate_repair_time(session),
            requires_human_review=not session.generated_fixes or session.generated_fixes[0].risk_score > 0.5,
        )
```

---

## 10.5 Autopsy Report Format

```python
@dataclass
class AutopsyReport:
    """Final report from repo autopsy."""
    
    # Request
    request: AutopsyRequest
    
    # Findings
    patterns_found: list[PatternMatch]
    fault_locations: list[FaultLocation]
    impact_graph: ImpactGraph
    
    # Fixes
    proposed_fixes: list[ProposedFix]
    recommended_fix: GeneratedFix | None
    
    # Metadata
    estimated_repair_time: timedelta
    requires_human_review: bool
    
    def to_markdown(self) -> str:
        """Generate human-readable report."""
        lines = [
            f"# Autopsy Report: {self.request.type.value}",
            f"",
            f"**Repository:** {self.request.repo.name}",
            f"**Triggered By:** {self.request.trigger.source}",
            f"**Priority:** {self.request.priority}",
            f"",
            f"## Identified Patterns",
        ]
        
        for match in self.patterns_found:
            lines.append(f"- **{match.pattern.name}** (confidence: {match.confidence:.0%})")
            
        lines.extend([
            f"",
            f"## Fault Locations",
        ])
        
        for loc in self.fault_locations:
            lines.append(f"- `{loc.file}:{loc.line}` - {loc.description}")
            
        lines.extend([
            f"",
            f"## Proposed Fixes",
        ])
        
        for i, proposed in enumerate(self.proposed_fixes, 1):
            lines.append(f"{i}. **{proposed.fix.description}** (confidence: {proposed.confidence:.0%})")
            lines.append(f"   - Files changed: {len(proposed.fix.files_changed)}")
            lines.append(f"   - Tests passing: {proposed.validation.tests_passing}/{proposed.validation.total_tests}")
            
        if self.recommended_fix:
            lines.extend([
                f"",
                f"## Recommended Fix",
                f"",
                f"**Description:** {self.recommended_fix.description}",
                f"**Estimated Time:** {self.estimated_repair_time}",
                f"**Auto-Apply:** {'Yes' if not self.requires_human_review else 'Requires approval'}",
            ])
            
        return "\n".join(lines)
```

---

## 10.6 Human Interface: Autopsy Control

```python
class AutopsyControlInterface:
    """Human interface for autopsy oversight."""
    
    async def list_autopsies(
        self,
        repo: RepositoryRef | None = None,
        status: AutopsyPhase | None = None,
        limit: int = 50
    ) -> list[AutopsySummary]:
        """List recent autopsy sessions."""
        
    async def get_autopsy_detail(self, autopsy_id: str) -> AutopsySession:
        """Get detailed autopsy session."""
        
    async def approve_fix(self, autopsy_id: str, fix_index: int) -> AppliedFix:
        """Approve and apply proposed fix."""
        
    async def reject_fix(self, autopsy_id: str, fix_index: int, reason: str) -> None:
        """Reject proposed fix with reason."""
        
    async def request_manual_intervention(
        self,
        autopsy_id: str,
        reason: str
    ) -> None:
        """Request human expert to take over."""
        
    async def add_pattern_feedback(
        self,
        pattern_id: str,
        autopsy_id: str,
        accurate: bool,
        feedback: str
    ) -> None:
        """Provide feedback on pattern matching."""
```

---

## 10.7 Integration with Agent Fabric

The Repo Autopsy system feeds into the Agent Fabric as the primary **repair agent**:

```python
# When autopsy recommends a fix, it can auto-execute via agent
if report.recommended_fix and not report.requires_human_review:
    # Spawn patch-engineer agent
    agent_run = await agent_fabric.spawn_run(
        agent_id="patch-engineer",
        task=AgentTask(
            objective=f"Apply autopsy fix: {report.recommended_fix.description}",
            inputs={
                "autopsy_id": session.request.id,
                "fix_spec": report.recommended_fix.to_dict(),
                "test_plan": report.recommended_fix.validation.test_plan,
            }
        ),
        context={"repo": session.request.repo}
    )
```

---

## Summary

The Repo Autopsy system provides:

- **8 phases** of structured failure analysis
- **Pattern database** with known failure signatures  
- **Fault localization** to exact code locations
- **Impact analysis** showing blast radius
- **Auto-generated fixes** with validation
- **Human oversight** for high-risk repairs
- **Continuous learning** from repair outcomes

This is the **self-healing layer** for codebases.
