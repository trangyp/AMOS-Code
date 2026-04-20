"""Repo Autopsy Engine - Automatic Repository Debugging System.

Section 10 of Axiom One: Automatic fault analysis and repair for repositories.
"""

from __future__ import annotations

import asyncio
import re
import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone

UTC = UTC

UTC = timezone.utc
from enum import Enum
from pathlib import Path
from typing import Any


class AutopsyRequestType(Enum):
    """Types of repository failures to autopsy."""

    BUILD_FAILURE = "build_failure"
    TEST_FAILURE = "test_failure"
    LINT_FAILURE = "lint_failure"
    TYPE_FAILURE = "type_failure"
    SECURITY_FAILURE = "security_failure"
    CRASH = "crash"
    MEMORY_LEAK = "memory_leak"
    PERFORMANCE_DEGRADATION = "performance"
    API_BREAKAGE = "api_breakage"
    SCHEMA_BREAKAGE = "schema_breakage"
    DEPENDENCY_FAILURE = "dependency"
    CONFIG_FAILURE = "config"
    DEPLOY_FAILURE = "deploy_failure"
    MIGRATION_FAILURE = "migration"


class AutopsyPhase(Enum):
    """Structured autopsy workflow."""

    COLLECT = "collect"
    IDENTIFY = "identify"
    LOCALIZE = "localize"
    IMPACT = "impact"
    STRATEGY = "strategy"
    GENERATE = "generate"
    VALIDATE = "validate"
    REPORT = "report"


@dataclass
class Evidence:
    """Collected evidence from environment."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: str = ""  # log, trace, metric, commit, artifact
    source: str = ""  # File path or URL
    content: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FailurePattern:
    """Known failure pattern with diagnosis and repair."""

    id: str = ""
    name: str = ""
    category: str = ""
    error_patterns: list[str] = field(default_factory=list)
    log_patterns: list[str] = field(default_factory=list)
    auto_repair_eligible: bool = False
    repair_strategy: str = ""
    success_rate: float = 0.0


@dataclass
class PatternMatch:
    """Match between evidence and pattern."""

    pattern: FailurePattern
    confidence: float
    matched_evidence: list[str] = field(default_factory=list)


@dataclass
class FaultLocation:
    """Exact location of a fault."""

    file: str = ""
    line: int = 0
    column: int = 0
    description: str = ""
    severity: str = "error"  # error, warning, info


@dataclass
class ImpactGraph:
    """Graph showing blast radius of failure."""

    root_cause: str = ""
    affected_files: list[str] = field(default_factory=list)
    affected_services: list[str] = field(default_factory=list)
    affected_apis: list[str] = field(default_factory=list)
    depth: int = 0


@dataclass
class GeneratedFix:
    """Auto-generated code fix."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    files_changed: list[dict] = field(default_factory=list)
    patches: list[dict] = field(default_factory=list)
    risk_score: float = 0.0
    test_plan: list[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Result of fix validation."""

    success: bool = False
    tests_passing: int = 0
    total_tests: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass
class ProposedFix:
    """Fix proposal with metadata."""

    fix: GeneratedFix
    validation: ValidationResult
    confidence: float = 0.0


@dataclass
class AutopsyReport:
    """Final report from repo autopsy."""

    request_id: str = ""
    patterns_found: list[PatternMatch] = field(default_factory=list)
    fault_locations: list[FaultLocation] = field(default_factory=list)
    impact_graph: ImpactGraph = None
    proposed_fixes: list[ProposedFix] = field(default_factory=list)
    recommended_fix: GeneratedFix = None
    estimated_repair_time: int = 0  # minutes
    requires_human_review: bool = True
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_markdown(self) -> str:
        """Generate human-readable report."""
        lines = [
            "# Autopsy Report",
            "",
            f"**Request ID:** {self.request_id}",
            f"**Generated:** {self.generated_at.isoformat()}",
            f"**Requires Review:** {'Yes' if self.requires_human_review else 'No'}",
            "",
            "## Identified Patterns",
        ]

        for match in self.patterns_found:
            lines.append(f"- **{match.pattern.name}** (confidence: {match.confidence:.0%})")

        lines.extend(
            [
                "",
                "## Fault Locations",
            ]
        )

        for loc in self.fault_locations:
            lines.append(f"- `{loc.file}:{loc.line}` - {loc.description}")

        if self.impact_graph:
            lines.extend(
                [
                    "",
                    "## Impact Analysis",
                    f"- Root Cause: {self.impact_graph.root_cause}",
                    f"- Affected Files: {len(self.impact_graph.affected_files)}",
                    f"- Impact Depth: {self.impact_graph.depth}",
                ]
            )

        lines.extend(
            [
                "",
                "## Proposed Fixes",
            ]
        )

        for i, proposed in enumerate(self.proposed_fixes, 1):
            lines.append(
                f"{i}. **{proposed.fix.description}** (confidence: {proposed.confidence:.0%})"
            )
            lines.append(f"   - Files: {len(proposed.fix.files_changed)}")
            lines.append(
                f"   - Tests: {proposed.validation.tests_passing}/{proposed.validation.total_tests}"
            )

        if self.recommended_fix:
            lines.extend(
                [
                    "",
                    "## Recommended Fix",
                    "",
                    f"**Description:** {self.recommended_fix.description}",
                    f"**Estimated Time:** {self.estimated_repair_time} min",
                    f"**Auto-Apply:** {'Yes' if not self.requires_human_review else 'Requires approval'}",
                ]
            )

        return "\n".join(lines)


@dataclass
class AutopsyRequest:
    """Request for repo autopsy."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    type: AutopsyRequestType = AutopsyRequestType.BUILD_FAILURE
    repo_path: str = ""
    trigger_source: str = "manual"  # ci, alert, manual, api
    reference: str = ""  # CI run ID, alert ID
    priority: str = "p2"  # p0, p1, p2, p3


@dataclass
class AutopsySession:
    """Running autopsy session."""

    request: AutopsyRequest
    phase: AutopsyPhase = AutopsyPhase.COLLECT
    collected_evidence: list[Evidence] = field(default_factory=list)
    identified_patterns: list[PatternMatch] = field(default_factory=list)
    fault_locations: list[FaultLocation] = field(default_factory=list)
    impact_graph: ImpactGraph = None
    generated_fixes: list[GeneratedFix] = field(default_factory=list)
    validation_results: list[ValidationResult] = field(default_factory=list)
    report: AutopsyReport = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime = None


# Pre-defined failure patterns
FAILURE_PATTERNS: list[FailurePattern] = [
    FailurePattern(
        id="PY-001",
        name="Python Missing Import",
        category="build",
        error_patterns=[
            r"ModuleNotFoundError: No module named '(.+)'",
            r"ImportError: No module named",
        ],
        log_patterns=[r"ImportError", r"cannot import"],
        auto_repair_eligible=True,
        repair_strategy="add_import",
        success_rate=0.85,
    ),
    FailurePattern(
        id="PY-002",
        name="Python Type Mismatch",
        category="type",
        error_patterns=[r"Incompatible types?", r"expected.*but got", r"Argument.*incompatible"],
        auto_repair_eligible=True,
        repair_strategy="add_type_hint",
        success_rate=0.75,
    ),
    FailurePattern(
        id="PY-003",
        name="Python Syntax Error",
        category="build",
        error_patterns=[r"SyntaxError:", r"IndentationError:"],
        auto_repair_eligible=False,
        repair_strategy="manual_fix",
        success_rate=0.30,
    ),
    FailurePattern(
        id="PY-004",
        name="Python Undefined Variable",
        category="build",
        error_patterns=[r"NameError: name '(.+)' is not defined"],
        auto_repair_eligible=True,
        repair_strategy="define_variable",
        success_rate=0.80,
    ),
    FailurePattern(
        id="JS-001",
        name="JavaScript Missing Import",
        category="build",
        error_patterns=[r"Cannot find module", r"Module not found"],
        auto_repair_eligible=True,
        repair_strategy="add_import",
        success_rate=0.85,
    ),
    FailurePattern(
        id="DEP-001",
        name="Dependency Version Conflict",
        category="dependency",
        error_patterns=[r"version conflict", r"incompatible.*version", r"Could not find a version"],
        log_patterns=[r"pip.*error", r"npm.*ERR"],
        auto_repair_eligible=True,
        repair_strategy="update_dependencies",
        success_rate=0.70,
    ),
    FailurePattern(
        id="TEST-001",
        name="Test Assertion Failure",
        category="test",
        error_patterns=[r"AssertionError", r"assert.*failed"],
        auto_repair_eligible=False,
        repair_strategy="fix_test",
        success_rate=0.40,
    ),
    FailurePattern(
        id="TEST-002",
        name="Test Timeout",
        category="test",
        error_patterns=[r"Timeout", r"exceeded timeout"],
        auto_repair_eligible=True,
        repair_strategy="optimize_test",
        success_rate=0.60,
    ),
]


class EvidenceCollector:
    """Collect evidence from repository and build environment."""

    async def collect_logs(self, request: AutopsyRequest) -> list[Evidence]:
        """Collect build logs, test logs, and error logs."""
        evidence = []
        repo_path = Path(request.repo_path)

        # Common log locations
        log_paths = [
            repo_path / "build.log",
            repo_path / "test.log",
            repo_path / "pytest.log",
            repo_path / "npm-debug.log",
            repo_path / "yarn-error.log",
        ]

        for log_path in log_paths:
            if log_path.exists():
                content = log_path.read_text()[:10000]  # Limit size
                evidence.append(
                    Evidence(
                        type="log",
                        source=str(log_path),
                        content=content,
                        metadata={"size": len(content)},
                    )
                )

        return evidence

    async def collect_traces(self, request: AutopsyRequest) -> list[Evidence]:
        """Collect stack traces and execution traces."""
        evidence = []
        repo_path = Path(request.repo_path)

        # Look for trace files
        trace_paths = [
            repo_path / "stacktrace.txt",
            repo_path / "trace.log",
        ]

        for trace_path in trace_paths:
            if trace_path.exists():
                content = trace_path.read_text()
                evidence.append(
                    Evidence(
                        type="trace",
                        source=str(trace_path),
                        content=content,
                    )
                )

        return evidence

    async def collect_commits(self, request: AutopsyRequest) -> list[Evidence]:
        """Collect recent commit history."""
        evidence = []

        try:
            result = subprocess.run(
                ["git", "-C", request.repo_path, "log", "--oneline", "-20"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                evidence.append(
                    Evidence(
                        type="commit",
                        source="git log",
                        content=result.stdout,
                    )
                )
        except Exception:
            pass

        return evidence

    async def collect_env(self, request: AutopsyRequest) -> list[Evidence]:
        """Collect environment information."""
        evidence = []

        # Python version
        try:
            result = subprocess.run(
                ["python", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            evidence.append(
                Evidence(
                    type="env",
                    source="python --version",
                    content=result.stdout.strip(),
                )
            )
        except Exception:
            pass

        # Git status
        try:
            result = subprocess.run(
                ["git", "-C", request.repo_path, "status", "--short"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            evidence.append(
                Evidence(
                    type="env",
                    source="git status",
                    content=result.stdout,
                )
            )
        except Exception:
            pass

        return evidence


class FaultLocalizer:
    """Locate exact fault positions in code."""

    async def localize(
        self,
        evidence: list[Evidence],
        pattern: FailurePattern,
    ) -> list[FaultLocation]:
        """Find fault locations based on pattern and evidence."""
        locations = []

        for ev in evidence:
            if ev.type in ("log", "trace"):
                # Parse stack traces
                locations.extend(self._parse_stack_trace(ev.content))

                # Match error patterns
                for error_pattern in pattern.error_patterns:
                    for match in re.finditer(error_pattern, ev.content):
                        # Try to find file/line context
                        context = ev.content[max(0, match.start() - 200) : match.end() + 200]
                        file_match = re.search(r'File "([^"]+)", line (\d+)', context)
                        if file_match:
                            locations.append(
                                FaultLocation(
                                    file=file_match.group(1),
                                    line=int(file_match.group(2)),
                                    description=f"Pattern match: {pattern.name}",
                                )
                            )

        return locations

    def _parse_stack_trace(self, content: str) -> list[FaultLocation]:
        """Parse Python/JavaScript stack traces."""
        locations = []

        # Python stack trace pattern
        py_pattern = r'File "([^"]+)", line (\d+), in ([^\n]+)'
        for match in re.finditer(py_pattern, content):
            locations.append(
                FaultLocation(
                    file=match.group(1),
                    line=int(match.group(2)),
                    description=f"In {match.group(3).strip()}",
                )
            )

        return locations


class ImpactAnalyzer:
    """Analyze impact scope of failures."""

    async def analyze(
        self,
        repo_path: str,
        fault_locations: list[FaultLocation],
    ) -> ImpactGraph:
        """Build impact graph showing blast radius."""
        graph = ImpactGraph()

        if not fault_locations:
            return graph

        # Set root cause
        root = fault_locations[0]
        graph.root_cause = f"{root.file}:{root.line}"

        # Find affected files
        affected = set()
        for loc in fault_locations:
            affected.add(loc.file)

            # Find files that import this file
            affected.update(await self._find_importers(repo_path, loc.file))

        graph.affected_files = list(affected)
        graph.depth = len(fault_locations)

        return graph

    async def _find_importers(self, repo_path: str, file_path: str) -> list[str]:
        """Find files that import the given file."""
        importers = []

        # Get module name from file path
        module_name = Path(file_path).stem

        # Search for imports
        try:
            result = subprocess.run(
                ["grep", "-r", f"from.*{module_name}", repo_path, "--include=*.py"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if ":" in line:
                        file = line.split(":")[0]
                        if file not in importers:
                            importers.append(file)
        except Exception:
            pass

        return importers


class FixGenerator:
    """Generate code fixes based on patterns and fault locations."""

    async def generate(
        self,
        pattern: FailurePattern,
        fault_locations: list[FaultLocation],
        evidence: list[Evidence],
    ) -> GeneratedFix:
        """Generate fix for identified pattern."""

        if not pattern.auto_repair_eligible:
            return None

        fix = GeneratedFix(
            description=f"Auto-fix for {pattern.name}",
            risk_score=0.3 if pattern.success_rate > 0.8 else 0.6,
        )

        if pattern.repair_strategy == "add_import":
            fix = await self._generate_import_fix(pattern, fault_locations, evidence)
        elif pattern.repair_strategy == "add_type_hint":
            fix = await self._generate_type_fix(pattern, fault_locations)
        elif pattern.repair_strategy == "define_variable":
            fix = await self._generate_variable_fix(pattern, fault_locations)
        elif pattern.repair_strategy == "update_dependencies":
            fix = await self._generate_dependency_fix(pattern, fault_locations)

        return fix

    async def _generate_import_fix(
        self,
        pattern: FailurePattern,
        fault_locations: list[FaultLocation],
        evidence: list[Evidence],
    ) -> GeneratedFix:
        """Generate import fix based on missing module."""
        fix = GeneratedFix(description="Add missing import")

        # Extract missing module name from evidence
        missing_module = None
        for ev in evidence:
            for pattern_regex in pattern.error_patterns:
                match = re.search(pattern_regex, ev.content)
                if match:
                    missing_module = match.group(1)
                    break
            if missing_module:
                break

        if missing_module and fault_locations:
            loc = fault_locations[0]
            fix.files_changed = [
                {
                    "file": loc.file,
                    "action": "add_import",
                    "module": missing_module,
                }
            ]
            fix.patches = [
                {
                    "file": loc.file,
                    "line": 1,
                    "action": "add",
                    "content": f"import {missing_module}\n",
                }
            ]

        return fix

    async def _generate_type_fix(
        self,
        pattern: FailurePattern,
        fault_locations: list[FaultLocation],
    ) -> GeneratedFix:
        """Generate type hint fix."""
        return GeneratedFix(
            description="Add type annotations (requires manual review)",
            risk_score=0.7,  # Higher risk
        )

    async def _generate_variable_fix(
        self,
        pattern: FailurePattern,
        fault_locations: list[FaultLocation],
    ) -> GeneratedFix:
        """Generate variable definition fix."""
        return GeneratedFix(
            description="Define undefined variable (requires manual review)",
            risk_score=0.8,
        )

    async def _generate_dependency_fix(
        self,
        pattern: FailurePattern,
        fault_locations: list[FaultLocation],
    ) -> GeneratedFix:
        """Generate dependency update fix."""
        return GeneratedFix(
            description="Update dependency versions",
            risk_score=0.5,
        )


class FixValidator:
    """Validate generated fixes."""

    async def validate(
        self,
        fix: GeneratedFix,
        repo_path: str,
    ) -> ValidationResult:
        """Validate fix by running tests and checks."""
        result = ValidationResult()

        # Run syntax check
        if not await self._check_syntax(fix, repo_path):
            result.errors.append("Syntax check failed")
            return result

        # Run tests if available
        test_result = await self._run_tests(repo_path)
        result.tests_passing = test_result.get("passed", 0)
        result.total_tests = test_result.get("total", 0)

        result.success = len(result.errors) == 0 and result.tests_passing > 0

        return result

    async def _check_syntax(self, fix: GeneratedFix, repo_path: str) -> bool:
        """Check Python syntax of changes."""
        for patch in fix.patches:
            file_path = Path(repo_path) / patch.get("file", "")
            if file_path.exists() and file_path.suffix == ".py":
                try:
                    result = subprocess.run(
                        ["python", "-m", "py_compile", str(file_path)],
                        capture_output=True,
                        timeout=10,
                    )
                    if result.returncode != 0:
                        return False
                except Exception:
                    return False
        return True

    async def _run_tests(self, repo_path: str) -> dict:
        """Run tests to validate fix."""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "-xvs", "--tb=short", "-q"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=120,
            )

            # Parse test results
            output = result.stdout + result.stderr
            passed = output.count("PASSED")
            failed = output.count("FAILED")

            return {
                "passed": passed,
                "failed": failed,
                "total": passed + failed,
            }
        except Exception as e:
            return {"passed": 0, "failed": 0, "total": 0, "error": str(e)}


class RepoAutopsyEngine:
    """Engine for automatic repo debugging."""

    def __init__(self):
        self._collector = EvidenceCollector()
        self._localizer = FaultLocalizer()
        self._analyzer = ImpactAnalyzer()
        self._generator = FixGenerator()
        self._validator = FixValidator()
        self._sessions: dict[str, AutopsySession] = {}
        self._pattern_db = {p.id: p for p in FAILURE_PATTERNS}

    async def start_autopsy(self, request: AutopsyRequest) -> AutopsySession:
        """Start new autopsy session."""
        session = AutopsySession(request=request)
        self._sessions[session.request.id] = session

        # Execute autopsy phases
        asyncio.create_task(self._execute_autopsy(session))

        return session

    async def _execute_autopsy(self, session: AutopsySession) -> None:
        """Execute all autopsy phases."""
        try:
            # Phase 1: Collect
            await self._phase_collect(session)

            # Phase 2: Identify
            await self._phase_identify(session)

            # Phase 3: Localize
            await self._phase_localize(session)

            # Phase 4: Impact
            await self._phase_impact(session)

            # Phase 5: Strategy
            await self._phase_strategy(session)

            # Phase 6: Generate
            await self._phase_generate(session)

            # Phase 7: Validate
            await self._phase_validate(session)

            # Phase 8: Report
            await self._phase_report(session)

        except Exception as e:
            print(f"[AUTOPSY ERROR] {session.request.id}: {e}")
            session.completed_at = datetime.now(timezone.utc)

    async def _phase_collect(self, session: AutopsySession) -> None:
        """Collect evidence."""
        session.phase = AutopsyPhase.COLLECT

        tasks = [
            self._collector.collect_logs(session.request),
            self._collector.collect_traces(session.request),
            self._collector.collect_commits(session.request),
            self._collector.collect_env(session.request),
        ]

        results = await asyncio.gather(*tasks)
        for evidence_list in results:
            session.collected_evidence.extend(evidence_list)

        print(
            f"[AUTOPSY] {session.request.id}: Collected {len(session.collected_evidence)} evidence items"
        )

    async def _phase_identify(self, session: AutopsySession) -> None:
        """Identify failure patterns."""
        session.phase = AutopsyPhase.IDENTIFY

        for pattern in self._pattern_db.values():
            score = self._match_pattern(session.collected_evidence, pattern)
            if score > 0.6:
                session.identified_patterns.append(
                    PatternMatch(
                        pattern=pattern,
                        confidence=score,
                    )
                )

        session.identified_patterns.sort(key=lambda p: p.confidence, reverse=True)

        print(
            f"[AUTOPSY] {session.request.id}: Identified {len(session.identified_patterns)} patterns"
        )

    def _match_pattern(self, evidence: list[Evidence], pattern: FailurePattern) -> float:
        """Match evidence against pattern."""
        scores = []

        for ev in evidence:
            # Check error patterns
            for error_pattern in pattern.error_patterns:
                if re.search(error_pattern, ev.content):
                    scores.append(0.9)

            # Check log patterns
            for log_pattern in pattern.log_patterns:
                if re.search(log_pattern, ev.content):
                    scores.append(0.7)

        return max(scores) if scores else 0.0

    async def _phase_localize(self, session: AutopsySession) -> None:
        """Localize faults."""
        session.phase = AutopsyPhase.LOCALIZE

        for pattern_match in session.identified_patterns:
            locations = await self._localizer.localize(
                session.collected_evidence,
                pattern_match.pattern,
            )
            session.fault_locations.extend(locations)

        # Remove duplicates
        seen = set()
        unique = []
        for loc in session.fault_locations:
            key = f"{loc.file}:{loc.line}"
            if key not in seen:
                seen.add(key)
                unique.append(loc)
        session.fault_locations = unique

        print(
            f"[AUTOPSY] {session.request.id}: Found {len(session.fault_locations)} fault locations"
        )

    async def _phase_impact(self, session: AutopsySession) -> None:
        """Analyze impact."""
        session.phase = AutopsyPhase.IMPACT

        session.impact_graph = await self._analyzer.analyze(
            session.request.repo_path,
            session.fault_locations,
        )

        print(f"[AUTOPSY] {session.request.id}: Impact depth {session.impact_graph.depth}")

    async def _phase_strategy(self, session: AutopsySession) -> None:
        """Determine repair strategy."""
        session.phase = AutopsyPhase.STRATEGY

        # Strategy determined by highest confidence pattern
        if session.identified_patterns:
            best = session.identified_patterns[0]
            print(f"[AUTOPSY] {session.request.id}: Strategy - {best.pattern.repair_strategy}")

    async def _phase_generate(self, session: AutopsySession) -> None:
        """Generate fixes."""
        session.phase = AutopsyPhase.GENERATE

        for pattern_match in session.identified_patterns[:3]:
            fix = await self._generator.generate(
                pattern_match.pattern,
                session.fault_locations,
                session.collected_evidence,
            )
            if fix:
                session.generated_fixes.append(fix)

        print(f"[AUTOPSY] {session.request.id}: Generated {len(session.generated_fixes)} fixes")

    async def _phase_validate(self, session: AutopsySession) -> None:
        """Validate fixes."""
        session.phase = AutopsyPhase.VALIDATE

        for fix in session.generated_fixes:
            result = await self._validator.validate(fix, session.request.repo_path)
            session.validation_results.append(result)

        print(f"[AUTOPSY] {session.request.id}: Validated {len(session.validation_results)} fixes")

    async def _phase_report(self, session: AutopsySession) -> None:
        """Generate final report."""
        session.phase = AutopsyPhase.REPORT
        session.completed_at = datetime.now(timezone.utc)

        # Build proposed fixes
        proposed = []
        for fix, result in zip(session.generated_fixes, session.validation_results):
            confidence = result.tests_passing / max(result.total_tests, 1)
            if result.success:
                proposed.append(ProposedFix(fix=fix, validation=result, confidence=confidence))

        # Recommend best fix
        recommended = None
        if proposed:
            proposed.sort(key=lambda p: p.confidence, reverse=True)
            recommended = proposed[0].fix

        # Determine if human review needed
        needs_review = True
        if recommended and recommended.risk_score < 0.5:
            needs_review = False

        session.report = AutopsyReport(
            request_id=session.request.id,
            patterns_found=session.identified_patterns,
            fault_locations=session.fault_locations,
            impact_graph=session.impact_graph,
            proposed_fixes=proposed,
            recommended_fix=recommended,
            estimated_repair_time=len(session.fault_locations) * 10,
            requires_human_review=needs_review,
        )

        print(f"[AUTOPSY] {session.request.id}: Report complete - {len(proposed)} fixes proposed")

    def get_session(self, session_id: str) -> AutopsySession:
        """Get autopsy session by ID."""
        return self._sessions.get(session_id)

    def list_sessions(self) -> list[AutopsySession]:
        """List all autopsy sessions."""
        return list(self._sessions.values())


# Global engine instance
_autopsy_engine: RepoAutopsyEngine = None


def get_repo_autopsy_engine() -> RepoAutopsyEngine:
    """Get or create global autopsy engine."""
    global _autopsy_engine
    if _autopsy_engine is None:
        _autopsy_engine = RepoAutopsyEngine()
    return _autopsy_engine
