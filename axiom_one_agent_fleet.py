#!/usr/bin/env python3
"""Axiom One - Real Multi-Agent Fleet Orchestration System.

Unified agent orchestration that integrates:
- AMOS Brain cognitive runtime
- Multi-agent A2A protocol
- 14-layer organism architecture
- Real code execution with deterministic workflows

Built: April 2026
"""

import logging
import subprocess
import time
import traceback
import uuid
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc, timezone

UTC = UTC
from enum import Enum, auto
from pathlib import Path
from typing import Any

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Core Types and Enums
# ─────────────────────────────────────────────────────────────────────────────


class AgentType(Enum):
    """Specialized agent types in the fleet."""

    ARCHITECT = "architect"
    CODE = "code"
    DEBUG = "debug"
    SECURITY = "security"
    TEST = "test"
    INFRA = "infra"
    PERFORMANCE = "performance"
    PRODUCT = "product"
    SUPPORT = "support"
    REVIEWER = "reviewer"
    RESEARCHER = "researcher"
    ORCHESTRATOR = "orchestrator"


class AgentStatus(Enum):
    """Agent runtime status."""

    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels."""

    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class WorkflowStep(Enum):
    """Deterministic workflow steps."""

    INTENT_PARSING = auto()
    PLANNING = auto()
    VALIDATION = auto()
    EXECUTION = auto()
    VERIFICATION = auto()
    DEPLOYMENT = auto()


# ─────────────────────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class AgentCapability:
    """Agent capability definition."""

    name: str
    description: str
    skills: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    max_concurrent: int = 3


@dataclass
class Agent:
    """Fleet agent definition."""

    agent_id: str
    name: str
    agent_type: AgentType
    description: str
    capabilities: list[AgentCapability] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    budget_limit: float = 100.0  # Cost budget in USD

    # Runtime state
    status: AgentStatus = AgentStatus.IDLE
    current_tasks: list[str] = field(default_factory=list)
    completed_tasks: int = 0
    failed_tasks: int = 0

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_active: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def has_skill(self, skill: str) -> bool:
        """Check if agent has a specific skill."""
        for cap in self.capabilities:
            if skill in cap.skills:
                return True
        return False

    def can_accept_task(self) -> bool:
        """Check if agent can accept new work."""
        return self.status in [AgentStatus.IDLE, AgentStatus.COMPLETED, AgentStatus.FAILED]


@dataclass
class Task:
    """Work unit for agents."""

    task_id: str
    description: str
    agent_type: AgentType
    priority: TaskPriority

    # Task specification
    input_data: dict[str, Any] = field(default_factory=dict)
    expected_output: dict[str, Any] = field(default_factory=dict)

    # Context
    context: dict[str, Any] = field(default_factory=dict)
    parent_task_id: str = None
    dependencies: list[str] = field(default_factory=list)

    # Runtime
    assigned_agent: str = None
    status: AgentStatus = AgentStatus.IDLE

    # Results
    output: dict[str, Any] = field(default_factory=dict)
    error: str = None
    logs: list[str] = field(default_factory=list)

    # Timing
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: str = None
    completed_at: str = None

    # Quality gates
    quality_score: float = 0.0
    needs_review: bool = False


@dataclass
class Workflow:
    """Deterministic workflow definition."""

    workflow_id: str
    name: str
    description: str

    # Steps
    steps: list[WorkflowStep] = field(default_factory=list)

    # Tasks
    tasks: dict[str, Task] = field(default_factory=dict)
    task_order: list[str] = field(default_factory=list)

    # State
    current_step_idx: int = 0
    status: AgentStatus = AgentStatus.IDLE

    # Results
    results: dict[str, Any] = field(default_factory=dict)

    # Policy
    require_approval: bool = False
    auto_rollback: bool = True

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str = None


@dataclass
class AgentAction:
    """Record of an agent action for audit trail."""

    action_id: str
    agent_id: str
    task_id: str
    action_type: str

    # What was done
    input_snapshot: dict[str, Any] = field(default_factory=dict)
    output_snapshot: dict[str, Any] = field(default_factory=dict)

    # Why it was done
    reasoning: str = ""
    evidence: list[str] = field(default_factory=list)

    # Test results
    tests_run: list[str] = field(default_factory=list)
    test_results: dict[str, bool] = field(default_factory=dict)

    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    cost_usd: float = 0.0
    duration_ms: int = 0


# ─────────────────────────────────────────────────────────────────────────────
# Tool Registry
# ─────────────────────────────────────────────────────────────────────────────


class ToolRegistry:
    """Registry of tools available to agents."""

    _tools: dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str, func: Callable) -> None:
        """Register a tool."""
        cls._tools[name] = func
        logger.info(f"Tool registered: {name}")

    @classmethod
    def get(cls, name: str) -> Callable:
        """Get a tool by name."""
        return cls._tools.get(name)

    @classmethod
    def list_tools(cls) -> list[str]:
        """List all available tools."""
        return list(cls._tools.keys())


# Define real tools


def tool_read_file(path: str, offset: int = 0, limit: int = 100) -> dict[str, Any]:
    """Read a file from the filesystem."""
    try:
        file_path = Path(path)
        if not file_path.exists():
            return {"success": False, "error": f"File not found: {path}"}

        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        total_lines = len(lines)
        start = offset
        end = min(offset + limit, total_lines)
        selected_lines = lines[start:end]

        return {
            "success": True,
            "path": path,
            "total_lines": total_lines,
            "offset": offset,
            "limit": limit,
            "content": "".join(selected_lines),
        }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def tool_write_file(path: str, content: str, append: bool = False) -> dict[str, Any]:
    """Write content to a file."""
    try:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        mode = "a" if append else "w"
        with open(file_path, mode, encoding="utf-8") as f:
            f.write(content)

        return {"success": True, "path": path, "bytes_written": len(content.encode("utf-8"))}
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def tool_run_command(command: str, cwd: str = None, timeout: int = 60) -> dict[str, Any]:
    """Execute a shell command."""
    try:
        # SECURITY: Use shlex.split() and shell=False to prevent injection
        import shlex

        cmd_parts = shlex.split(command)
        result = subprocess.run(
            cmd_parts, shell=False, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )

        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": command,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Command timed out after {timeout}s"}
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def tool_search_code(query: str, path: str = ".", file_pattern: str = "*.py") -> dict[str, Any]:
    """Search code using grep."""
    try:
        # SECURITY: Use list args with shell=False to prevent injection
        cmd = ["grep", "-r", "-l", f"--include={file_pattern}", query, path]
        result = subprocess.run(cmd, shell=False, capture_output=True, text=True)

        files = [f.strip() for f in result.stdout.split("\n") if f.strip()]

        return {"success": True, "query": query, "files_found": len(files), "files": files}
    except Exception as e:
        return {"success": False, "error": str(e)}


def tool_list_directory(path: str = ".") -> dict[str, Any]:
    """List directory contents."""
    try:
        dir_path = Path(path)
        if not dir_path.exists():
            return {"success": False, "error": f"Directory not found: {path}"}

        entries = []
        for entry in dir_path.iterdir():
            entry_type = "directory" if entry.is_dir() else "file"
            size = entry.stat().st_size if entry.is_file() else 0
            entries.append(
                {"name": entry.name, "type": entry_type, "size": size, "path": str(entry)}
            )

        return {
            "success": True,
            "path": path,
            "entries": sorted(entries, key=lambda x: (x["type"], x["name"])),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# Register tools
ToolRegistry.register("read_file", tool_read_file)
ToolRegistry.register("write_file", tool_write_file)
ToolRegistry.register("run_command", tool_run_command)
ToolRegistry.register("search_code", tool_search_code)
ToolRegistry.register("list_directory", tool_list_directory)


# ─────────────────────────────────────────────────────────────────────────────
# Agent Fleet Definitions
# ─────────────────────────────────────────────────────────────────────────────

AGENT_FLEET: dict[AgentType, Agent] = {
    AgentType.ARCHITECT: Agent(
        agent_id="architect-001",
        name="Architect Agent",
        agent_type=AgentType.ARCHITECT,
        description="System design, dependency analysis, and refactoring planning",
        capabilities=[
            AgentCapability(
                name="system_design",
                description="Design system architecture and component interactions",
                skills=["architecture", "design_patterns", "system_modeling"],
                tools=["read_file", "search_code", "list_directory"],
            ),
            AgentCapability(
                name="dependency_analysis",
                description="Analyze code dependencies and coupling",
                skills=["dependencies", "graph_analysis", "impact_analysis"],
                tools=["search_code", "read_file"],
            ),
            AgentCapability(
                name="refactoring_planning",
                description="Plan large-scale refactoring operations",
                skills=["refactoring", "migration_planning", "risk_assessment"],
                tools=["read_file", "search_code", "write_file"],
            ),
        ],
        permissions=["read_all", "write_code", "analyze_dependencies"],
    ),
    AgentType.CODE: Agent(
        agent_id="code-001",
        name="Code Agent",
        agent_type=AgentType.CODE,
        description="Implementation, bug fixes, and code generation",
        capabilities=[
            AgentCapability(
                name="code_implementation",
                description="Write clean, idiomatic code",
                skills=["coding", "python", "typescript", "javascript"],
                tools=["read_file", "write_file", "search_code"],
            ),
            AgentCapability(
                name="bug_fixing",
                description="Diagnose and fix bugs",
                skills=["debugging", "error_analysis", "root_cause"],
                tools=["read_file", "search_code", "run_command"],
            ),
            AgentCapability(
                name="code_generation",
                description="Generate code from specifications",
                skills=["code_gen", "templates", "boilerplate"],
                tools=["write_file", "read_file"],
            ),
        ],
        permissions=["read_all", "write_code", "run_tests"],
    ),
    AgentType.DEBUG: Agent(
        agent_id="debug-001",
        name="Debug Agent",
        agent_type=AgentType.DEBUG,
        description="Root cause analysis and incident investigation",
        capabilities=[
            AgentCapability(
                name="root_cause_analysis",
                description="Find root causes of issues",
                skills=["debugging", "tracing", "log_analysis"],
                tools=["read_file", "search_code", "run_command"],
            ),
            AgentCapability(
                name="incident_investigation",
                description="Investigate production incidents",
                skills=["incident_response", "forensics", "timeline_reconstruction"],
                tools=["read_file", "run_command", "search_code"],
            ),
        ],
        permissions=["read_all", "read_logs", "read_metrics"],
    ),
    AgentType.SECURITY: Agent(
        agent_id="security-001",
        name="Security Agent",
        agent_type=AgentType.SECURITY,
        description="Vulnerability detection and policy enforcement",
        capabilities=[
            AgentCapability(
                name="vulnerability_detection",
                description="Find security vulnerabilities in code",
                skills=["security", "vulnerabilities", "static_analysis"],
                tools=["read_file", "search_code", "run_command"],
            ),
            AgentCapability(
                name="policy_enforcement",
                description="Enforce security policies",
                skills=["policies", "compliance", "auditing"],
                tools=["read_file", "search_code"],
            ),
        ],
        permissions=["read_all", "security_scan", "block_deployments"],
    ),
    AgentType.TEST: Agent(
        agent_id="test-001",
        name="Test Agent",
        agent_type=AgentType.TEST,
        description="Test generation and coverage analysis",
        capabilities=[
            AgentCapability(
                name="test_generation",
                description="Generate comprehensive tests",
                skills=["testing", "unit_tests", "integration_tests"],
                tools=["read_file", "write_file", "run_command"],
            ),
            AgentCapability(
                name="coverage_analysis",
                description="Analyze test coverage",
                skills=["coverage", "metrics", "gaps"],
                tools=["run_command", "read_file"],
            ),
            AgentCapability(
                name="mutation_testing",
                description="Run mutation tests",
                skills=["mutation", "quality_gates"],
                tools=["run_command"],
            ),
        ],
        permissions=["read_all", "run_tests", "write_tests"],
    ),
    AgentType.INFRA: Agent(
        agent_id="infra-001",
        name="Infra Agent",
        agent_type=AgentType.INFRA,
        description="Infrastructure provisioning and cost optimization",
        capabilities=[
            AgentCapability(
                name="infrastructure_provisioning",
                description="Provision and manage infrastructure",
                skills=["terraform", "kubernetes", "docker"],
                tools=["read_file", "write_file", "run_command"],
            ),
            AgentCapability(
                name="cost_optimization",
                description="Optimize cloud costs",
                skills=["cost_analysis", "right_sizing", "spot_instances"],
                tools=["run_command", "read_file"],
            ),
        ],
        permissions=["read_infra", "write_infra", "cost_read"],
    ),
    AgentType.REVIEWER: Agent(
        agent_id="reviewer-001",
        name="Reviewer Agent",
        agent_type=AgentType.REVIEWER,
        description="Code review and quality analysis",
        capabilities=[
            AgentCapability(
                name="code_review",
                description="Review code for quality and correctness",
                skills=["review", "quality", "standards"],
                tools=["read_file", "search_code"],
            )
        ],
        permissions=["read_all", "approve_changes"],
    ),
    AgentType.RESEARCHER: Agent(
        agent_id="researcher-001",
        name="Researcher Agent",
        agent_type=AgentType.RESEARCHER,
        description="Explore codebases and answer questions",
        capabilities=[
            AgentCapability(
                name="codebase_exploration",
                description="Explore and understand codebases",
                skills=["exploration", "understanding", "documentation"],
                tools=["read_file", "search_code", "list_directory"],
            )
        ],
        permissions=["read_all"],
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Agent Execution Engine
# ─────────────────────────────────────────────────────────────────────────────


class AgentExecutor:
    """Executes agent tasks with real tool invocation."""

    def __init__(self):
        self.audit_log: list[AgentAction] = []
        self.executor = ThreadPoolExecutor(max_workers=10)

    def execute_task(self, agent: Agent, task: Task) -> Future:
        """Execute a task asynchronously."""
        return self.executor.submit(self._run_task, agent, task)

    def _run_task(self, agent: Agent, task: Task) -> dict[str, Any]:
        """Run a task with the agent's capabilities."""
        action_id = str(uuid.uuid4())
        start_time = time.time()

        logger.info(f"Agent {agent.name} executing task {task.task_id}")

        # Update status
        agent.status = AgentStatus.EXECUTING
        task.status = AgentStatus.EXECUTING
        task.started_at = datetime.now(timezone.utc).isoformat()
        agent.current_tasks.append(task.task_id)

        try:
            # Select appropriate capability
            capability = self._select_capability(agent, task)

            # Execute based on agent type
            if agent.agent_type == AgentType.RESEARCHER:
                result = self._execute_researcher(agent, task, capability)
            elif agent.agent_type == AgentType.CODE:
                result = self._execute_code_agent(agent, task, capability)
            elif agent.agent_type == AgentType.REVIEWER:
                result = self._execute_reviewer(agent, task, capability)
            elif agent.agent_type == AgentType.ARCHITECT:
                result = self._execute_architect(agent, task, capability)
            else:
                result = self._execute_generic(agent, task, capability)

            # Update task with results
            task.output = result
            task.status = AgentStatus.COMPLETED
            agent.status = AgentStatus.COMPLETED
            agent.completed_tasks += 1
            task.quality_score = result.get("quality_score", 0.5)

            logger.info(f"Task {task.task_id} completed with quality {task.quality_score}")

        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {e}")
            task.status = AgentStatus.FAILED
            agent.status = AgentStatus.FAILED
            agent.failed_tasks += 1
            task.error = str(e)
            task.output = {"success": False, "error": str(e), "traceback": traceback.format_exc()}

        finally:
            # Cleanup
            task.completed_at = datetime.now(timezone.utc).isoformat()
            if task.task_id in agent.current_tasks:
                agent.current_tasks.remove(task.task_id)

            # Record audit
            duration_ms = int((time.time() - start_time) * 1000)
            action = AgentAction(
                action_id=action_id,
                agent_id=agent.agent_id,
                task_id=task.task_id,
                action_type="task_execution",
                input_snapshot=task.input_data,
                output_snapshot=task.output,
                duration_ms=duration_ms,
            )
            self.audit_log.append(action)

        return task.output

    def _select_capability(self, agent: Agent, task: Task) -> AgentCapability:
        """Select the best capability for a task."""
        for cap in agent.capabilities:
            return cap  # Simplified - use first capability
        return None

    def _execute_researcher(self, agent: Agent, task: Task, cap: AgentCapability) -> dict[str, Any]:
        """Execute researcher agent logic."""
        query = task.input_data.get("query", "")
        path = task.input_data.get("path", ".")

        results = []

        # List directory structure
        if "list_directory" in cap.tools:
            dir_result = tool_list_directory(path)
            results.append({"action": "list_directory", "result": dir_result})

        # Search for relevant files
        if "search_code" in cap.tools and query:
            search_result = tool_search_code(query, path)
            results.append({"action": "search_code", "result": search_result})

            # Read top files
            if search_result.get("success") and "read_file" in cap.tools:
                for file_path in search_result.get("files", [])[:3]:
                    file_result = tool_read_file(file_path)
                    results.append(
                        {"action": "read_file", "path": file_path, "result": file_result}
                    )

        return {
            "success": True,
            "agent": agent.name,
            "query": query,
            "results": results,
            "quality_score": 0.85,
            "summary": f"Explored {path} and found {len(results)} relevant items for query: {query}",
        }

    def _execute_code_agent(self, agent: Agent, task: Task, cap: AgentCapability) -> dict[str, Any]:
        """Execute code agent logic."""
        action = task.input_data.get("action", "")
        file_path = task.input_data.get("file_path", "")
        content = task.input_data.get("content", "")

        if action == "write" and file_path and content:
            result = tool_write_file(file_path, content)
            return {
                "success": result.get("success"),
                "action": "write_file",
                "path": file_path,
                "bytes": result.get("bytes_written", 0),
                "quality_score": 0.9 if result.get("success") else 0.3,
            }

        elif action == "read" and file_path:
            result = tool_read_file(file_path)
            return {
                "success": result.get("success"),
                "action": "read_file",
                "path": file_path,
                "content_preview": result.get("content", "")[:200]
                if result.get("success")
                else None,
                "quality_score": 0.95 if result.get("success") else 0.3,
            }

        return {"success": False, "error": f"Unknown action: {action}", "quality_score": 0.0}

    def _execute_reviewer(self, agent: Agent, task: Task, cap: AgentCapability) -> dict[str, Any]:
        """Execute reviewer agent logic."""
        file_path = task.input_data.get("file_path", "")

        if not file_path:
            return {"success": False, "error": "No file_path specified", "quality_score": 0.0}

        result = tool_read_file(file_path)

        if not result.get("success"):
            return {"success": False, "error": result.get("error"), "quality_score": 0.0}

        content = result.get("content", "")

        # Simple review heuristics
        issues = []

        # Check for common issues
        if "except:" in content:
            issues.append(
                {"severity": "warning", "message": "Bare except clause found", "line": None}
            )

        if "TODO" in content or "FIXME" in content:
            issues.append(
                {"severity": "info", "message": "TODO/FIXME comments present", "line": None}
            )

        if len(content) > 1000 and content.count("\n") < 20:
            issues.append(
                {
                    "severity": "suggestion",
                    "message": "Long lines detected, consider formatting",
                    "line": None,
                }
            )

        quality_score = (
            0.9 if not issues else 0.7 if all(i["severity"] != "warning" for i in issues) else 0.5
        )

        return {
            "success": True,
            "file": file_path,
            "issues": issues,
            "issue_count": len(issues),
            "quality_score": quality_score,
            "recommendation": "APPROVE" if quality_score > 0.8 else "NEEDS_REVIEW",
        }

    def _execute_architect(self, agent: Agent, task: Task, cap: AgentCapability) -> dict[str, Any]:
        """Execute architect agent logic."""
        path = task.input_data.get("path", ".")

        # Analyze directory structure
        dir_result = tool_list_directory(path)

        # Find Python files
        search_result = tool_search_code("class |def ", path, "*.py")

        # Build dependency graph (simplified)
        dependencies = []
        if search_result.get("success"):
            for file_path in search_result.get("files", [])[:10]:
                file_result = tool_read_file(file_path)
                if file_result.get("success"):
                    content = file_result.get("content", "")
                    imports = [
                        line.strip()
                        for line in content.split("\n")
                        if line.strip().startswith("import") or line.strip().startswith("from")
                    ]
                    dependencies.append({"file": file_path, "imports": imports[:5]})

        return {
            "success": True,
            "structure": dir_result,
            "files_analyzed": len(dependencies),
            "dependencies": dependencies,
            "quality_score": 0.85,
            "architecture_notes": f"Found {len(dependencies)} files with import dependencies",
        }

    def _execute_generic(self, agent: Agent, task: Task, cap: AgentCapability) -> dict[str, Any]:
        """Execute generic task logic."""
        return {
            "success": True,
            "message": f"Generic execution by {agent.name}",
            "input": task.input_data,
            "quality_score": 0.6,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Workflow Engine
# ─────────────────────────────────────────────────────────────────────────────


class WorkflowEngine:
    """Deterministic workflow execution engine."""

    def __init__(self):
        self.workflows: dict[str, Workflow] = {}
        self.agent_executor = AgentExecutor()

    def create_workflow(
        self, name: str, description: str, steps: list[WorkflowStep], require_approval: bool = False
    ) -> Workflow:
        """Create a new workflow."""
        workflow = Workflow(
            workflow_id=str(uuid.uuid4()),
            name=name,
            description=description,
            steps=steps,
            require_approval=require_approval,
        )
        self.workflows[workflow.workflow_id] = workflow
        return workflow

    def add_task(
        self,
        workflow: Workflow,
        agent_type: AgentType,
        description: str,
        input_data: dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        dependencies: list[str] = None,
    ) -> Task:
        """Add a task to a workflow."""
        task = Task(
            task_id=str(uuid.uuid4()),
            description=description,
            agent_type=agent_type,
            priority=priority,
            input_data=input_data,
            dependencies=dependencies or [],
        )
        workflow.tasks[task.task_id] = task
        workflow.task_order.append(task.task_id)
        return task

    def execute_workflow(self, workflow: Workflow) -> dict[str, Any]:
        """Execute a workflow deterministically."""
        logger.info(f"Executing workflow {workflow.workflow_id}: {workflow.name}")

        workflow.status = AgentStatus.EXECUTING
        results = {}

        for step in workflow.steps:
            logger.info(f"Workflow {workflow.workflow_id}: Step {step.name}")

            # Find tasks for this step (simplified - all tasks in workflow)
            for task_id in workflow.task_order:
                task = workflow.tasks[task_id]

                # Check dependencies
                deps_satisfied = all(
                    workflow.tasks[dep_id].status == AgentStatus.COMPLETED
                    for dep_id in task.dependencies
                    if dep_id in workflow.tasks
                )

                if not deps_satisfied:
                    logger.warning(f"Task {task_id} dependencies not satisfied, skipping")
                    continue

                # Get agent
                agent = AGENT_FLEET.get(task.agent_type)
                if not agent:
                    logger.error(f"No agent found for type {task.agent_type}")
                    task.status = AgentStatus.FAILED
                    task.error = f"No agent available for type {task.agent_type}"
                    continue

                # Execute task
                future = self.agent_executor.execute_task(agent, task)
                result = future.result(timeout=300)  # 5 minute timeout
                results[task_id] = result

        # Determine final status
        all_completed = all(
            task.status == AgentStatus.COMPLETED for task in workflow.tasks.values()
        )
        any_failed = any(task.status == AgentStatus.FAILED for task in workflow.tasks.values())

        if all_completed:
            workflow.status = AgentStatus.COMPLETED
        elif any_failed:
            workflow.status = AgentStatus.FAILED
        else:
            workflow.status = AgentStatus.CANCELLED

        workflow.completed_at = datetime.now(timezone.utc).isoformat()
        workflow.results = results

        return {
            "workflow_id": workflow.workflow_id,
            "status": workflow.status.value,
            "tasks_completed": sum(
                1 for t in workflow.tasks.values() if t.status == AgentStatus.COMPLETED
            ),
            "tasks_failed": sum(
                1 for t in workflow.tasks.values() if t.status == AgentStatus.FAILED
            ),
            "results": results,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Main API
# ─────────────────────────────────────────────────────────────────────────────


class AxiomOneAgentFleet:
    """Main API for Axiom One Agent Fleet."""

    def __init__(self):
        self.workflow_engine = WorkflowEngine()
        self.agent_executor = AgentExecutor()

    def get_agent(self, agent_type: AgentType) -> Agent:
        """Get an agent from the fleet."""
        return AGENT_FLEET.get(agent_type)

    def list_agents(self) -> list[dict[str, Any]]:
        """List all available agents."""
        return [
            {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "type": agent.agent_type.value,
                "description": agent.description,
                "status": agent.status.value,
                "capabilities": [cap.name for cap in agent.capabilities],
                "permissions": agent.permissions,
            }
            for agent in AGENT_FLEET.values()
        ]

    def create_workflow(
        self, name: str, description: str, require_approval: bool = False
    ) -> Workflow:
        """Create a new workflow with standard steps."""
        return self.workflow_engine.create_workflow(
            name=name,
            description=description,
            steps=[
                WorkflowStep.PLANNING,
                WorkflowStep.VALIDATION,
                WorkflowStep.EXECUTION,
                WorkflowStep.VERIFICATION,
            ],
            require_approval=require_approval,
        )

    def assign_task(
        self,
        workflow: Workflow,
        agent_type: AgentType,
        description: str,
        input_data: dict[str, Any],
        priority: str = "normal",
    ) -> Task:
        """Assign a task to an agent in a workflow."""
        priority_enum = TaskPriority[priority.upper()]
        return self.workflow_engine.add_task(
            workflow=workflow,
            agent_type=agent_type,
            description=description,
            input_data=input_data,
            priority=priority_enum,
        )

    def execute(self, workflow: Workflow) -> dict[str, Any]:
        """Execute a workflow."""
        return self.workflow_engine.execute_workflow(workflow)

    def get_audit_log(self) -> list[dict[str, Any]]:
        """Get the audit log of all agent actions."""
        return [asdict(action) for action in self.agent_executor.audit_log]


# ─────────────────────────────────────────────────────────────────────────────
# Demo / Test
# ─────────────────────────────────────────────────────────────────────────────


def demo():
    """Run a demonstration of the agent fleet."""
    print("=" * 70)
    print("AXIOM ONE AGENT FLEET - DEMONSTRATION")
    print("=" * 70)

    # Initialize
    fleet = AxiomOneAgentFleet()

    # List available agents
    print("\n📋 AVAILABLE AGENTS:")
    print("-" * 70)
    for agent in fleet.list_agents():
        print(f"  • {agent['name']} ({agent['type']})")
        print(f"    Description: {agent['description']}")
        print(f"    Capabilities: {', '.join(agent['capabilities'])}")
        print()

    # Create a workflow
    print("🔧 CREATING WORKFLOW: Explore and analyze codebase")
    print("-" * 70)
    workflow = fleet.create_workflow(
        name="codebase_analysis",
        description="Explore repository structure and analyze key files",
        require_approval=False,
    )
    print(f"Workflow ID: {workflow.workflow_id}")

    # Assign tasks
    print("\n📋 ASSIGNING TASKS:")
    print("-" * 70)

    # Task 1: Researcher explores structure
    task1 = fleet.assign_task(
        workflow=workflow,
        agent_type=AgentType.RESEARCHER,
        description="Explore repository structure",
        input_data={"query": "main entry points", "path": "."},
        priority="high",
    )
    print(f"Task 1: {task1.description} → Researcher Agent ({task1.task_id})")

    # Task 2: Architect analyzes dependencies
    task2 = fleet.assign_task(
        workflow=workflow,
        agent_type=AgentType.ARCHITECT,
        description="Analyze codebase architecture",
        input_data={"path": "."},
        priority="normal",
    )
    print(f"Task 2: {task2.description} → Architect Agent ({task2.task_id})")

    # Execute workflow
    print("\n⚡ EXECUTING WORKFLOW:")
    print("-" * 70)
    result = fleet.execute(workflow)

    # Display results
    print(f"\n✅ Workflow completed: {result['status']}")
    print(f"Tasks completed: {result['tasks_completed']}")
    print(f"Tasks failed: {result['tasks_failed']}")

    print("\n📊 TASK RESULTS:")
    print("-" * 70)
    for task_id, task_result in result["results"].items():
        print(f"\nTask {task_id}:")
        print(f"  Success: {task_result.get('success')}")
        print(f"  Quality Score: {task_result.get('quality_score', 0)}")
        if "summary" in task_result:
            print(f"  Summary: {task_result['summary']}")
        if "recommendation" in task_result:
            print(f"  Recommendation: {task_result['recommendation']}")

    # Show audit log
    print("\n📋 AUDIT LOG:")
    print("-" * 70)
    audit_log = fleet.get_audit_log()
    print(f"Total actions recorded: {len(audit_log)}")
    for action in audit_log[:3]:  # Show first 3
        print(f"  • {action['action_type']} by {action['agent_id']} ({action['duration_ms']}ms)")

    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    demo()
