"""Axiom One FastAPI Server"""

import asyncio
import os
import subprocess
import sys
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
UTC = timezone.utc
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware

# Add parent to path
_AMOS_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(_AMOS_ROOT))


from axiom_one.git_service import GitService
from axiom_one.models import (
    HealthFinding,
    RepoGraph,
    RepoGraphEdge,
    RepoGraphNode,
    RepoProvider,
    Repository,
    TerminalSession,
    Workspace,
    WorkspaceStatus,
)


class TerminalService:
    """Terminal session management."""

    def __init__(self, workspace_base: Path):
        self.workspace_base = workspace_base
        self.active_sessions: dict[str, asyncio.subprocess.Process] = {}

    async def create_session(
        self,
        workspace_id: str,
        repository_id: str,
        command: str,
        cwd: str = None,
    ) -> TerminalSession:
        session_id = str(uuid.uuid4())

        if cwd:
            work_dir = Path(cwd)
        elif repository_id:
            work_dir = self.workspace_base / workspace_id / "repos" / repository_id
        else:
            work_dir = self.workspace_base / workspace_id

        work_dir.mkdir(parents=True, exist_ok=True)

        session_env = os.environ.copy()
        session_env["WORKSPACE_ID"] = workspace_id
        if repository_id:
            session_env["REPO_ID"] = repository_id

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=work_dir,
                env=session_env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to start process: {e}")

        self.active_sessions[session_id] = process

        return TerminalSession(
            id=session_id,
            workspace_id=workspace_id,
            repository_id=repository_id,
            command=command,
            cwd=str(work_dir),
            env={},
            pid=process.pid,
            status="running",
            output=[],
            exit_code=None,
            created_at=datetime.now(timezone.utc),
            finished_at=None,
        )

    async def read_output(self, session_id: str) -> AsyncIterator[str]:
        process = self.active_sessions.get(session_id)
        if not process:
            return

        while True:
            try:
                line = await asyncio.wait_for(process.stdout.readline(), timeout=0.1)
                if line:
                    yield line.decode("utf-8", errors="replace")
                    continue

                if process.returncode is not None:
                    break

            except TimeoutError:
                if process.returncode is not None:
                    break
                continue
            except Exception:
                break


class RepoGraphService:
    """Repository graph analysis."""

    def __init__(self, repo_base: Path):
        self.repo_base = repo_base

    async def generate_graph(self, repo_id: str) -> RepoGraph:
        repo_path = self.repo_base / repo_id

        nodes: list[RepoGraphNode] = []
        edges: list[RepoGraphEdge] = []

        # Use os.walk with directory pruning for efficient scanning
        exclude_dirs = {
            ".venv",
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
        }
        max_file_size = 1024 * 1024  # 1MB limit

        for root, dirs, files in os.walk(repo_path):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if not file.endswith(".py"):
                    continue

                py_file = Path(root) / file
                rel_path = str(py_file.relative_to(repo_path))
                file_id = f"file:{rel_path}"

                nodes.append(
                    RepoGraphNode(
                        id=file_id,
                        type="file",
                        name=py_file.name,
                        file_path=rel_path,
                        line_start=1,
                        line_end=0,
                    )
                )

                try:
                    # Check file size before reading
                    stat = py_file.stat()
                    if stat.st_size > max_file_size:
                        continue  # Skip files larger than 1MB

                    content = py_file.read_text(encoding="utf-8", errors="replace")
                    for i, line in enumerate(content.split("\n"), 1):
                        if line.strip().startswith("import ") or line.strip().startswith("from "):
                            target = line.strip().split()[1].split(".")[0]
                            import_id = f"import:{target}"

                            if not any(n.id == import_id for n in nodes):
                                nodes.append(
                                    RepoGraphNode(
                                        id=import_id,
                                        type="import",
                                        name=target,
                                        file_path="",
                                        line_start=0,
                                        line_end=0,
                                    )
                                )

                            edges.append(
                                RepoGraphEdge(
                                    source=file_id,
                                    target=import_id,
                                    type="imports",
                                )
                            )
                except Exception:
                    pass

        return RepoGraph(
            repository_id=repo_id,
            nodes=nodes,
            edges=edges,
            generated_at=datetime.now(timezone.utc),
        )


class AIRepoHealthAgent:
    """AI agent for repository health analysis."""

    def __init__(self, repo_base: Path):
        self.repo_base = repo_base

    async def analyze_repository(self, repo_id: str) -> list[HealthFinding]:
        repo_path = self.repo_base / repo_id
        findings: list[HealthFinding] = []

        # Check for broken imports
        findings.extend(await self._check_imports(repo_path, repo_id))

        # Check for missing files
        findings.extend(await self._check_missing_files(repo_path, repo_id))

        # Check for hardcoded paths
        findings.extend(await self._check_path_assumptions(repo_path, repo_id))

        # Check for security issues
        findings.extend(await self._check_security(repo_path, repo_id))

        return findings

    async def _check_imports(self, repo_path: Path, repo_id: str) -> list[HealthFinding]:
        findings = []

        # Use os.walk with directory pruning for efficient scanning
        exclude_dirs = {
            ".venv",
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
        }
        max_file_size = 1024 * 1024  # 1MB limit

        for root, dirs, files in os.walk(repo_path):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if not file.endswith(".py"):
                    continue

                py_file = Path(root) / file

                try:
                    # Check file size before reading
                    stat = py_file.stat()
                    if stat.st_size > max_file_size:
                        continue  # Skip large files

                    content = py_file.read_text(encoding="utf-8", errors="replace")
                    rel_path = str(py_file.relative_to(repo_path))

                    for i, line in enumerate(content.split("\n"), 1):
                        stripped = line.strip()
                        if stripped.startswith("from ") or stripped.startswith("import "):
                            parts = stripped.split()
                            if len(parts) >= 2:
                                module = parts[1].split(".")[0]

                                if module not in [
                                    "os",
                                    "sys",
                                    "typing",
                                    "pathlib",
                                    "json",
                                    "datetime",
                                    "collections",
                                ]:
                                    try:
                                        __import__(module)
                                    except ImportError:
                                        findings.append(
                                            HealthFinding(
                                                id=str(uuid.uuid4()),
                                                severity="high",
                                                category="import",
                                                title=f"Broken import: {module}",
                                                description=f"Cannot import '{module}' - module not found",
                                                file_path=rel_path,
                                                line_start=i,
                                                line_end=i,
                                                suggested_fix=f"pip install {module}"
                                                if module.islower()
                                                else "Check import path",
                                                auto_fixable=False,
                                            )
                                        )
                except Exception:
                    pass

        return findings

    async def _check_missing_files(self, repo_path: Path, repo_id: str) -> list[HealthFinding]:
        findings = []

        essential_files = ["README.md", ".gitignore"]
        for filename in essential_files:
            if not (repo_path / filename).exists():
                findings.append(
                    HealthFinding(
                        id=str(uuid.uuid4()),
                        severity="medium" if filename == ".gitignore" else "low",
                        category="style",
                        title=f"Missing {filename}",
                        description=f"Repository should have a {filename} file",
                        file_path=None,
                        line_start=None,
                        line_end=None,
                        suggested_fix=f"Create {filename} with appropriate content",
                        auto_fixable=filename == ".gitignore",
                    )
                )

        return findings

    async def _check_path_assumptions(self, repo_path: Path, repo_id: str) -> list[HealthFinding]:
        findings = []

        # Use os.walk with directory pruning for efficient scanning
        exclude_dirs = {
            ".venv",
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
        }
        max_file_size = 1024 * 1024  # 1MB limit

        for root, dirs, files in os.walk(repo_path):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if not file.endswith(".py"):
                    continue

                py_file = Path(root) / file

                try:
                    # Check file size before reading
                    stat = py_file.stat()
                    if stat.st_size > max_file_size:
                        continue  # Skip large files

                    content = py_file.read_text(encoding="utf-8", errors="replace")
                    rel_path = str(py_file.relative_to(repo_path))

                    for i, line in enumerate(content.split("\n"), 1):
                        if "/home/" in line or "/Users/" in line or "C:\\" in line:
                            if "__file__" not in line and "Path" not in line:
                                findings.append(
                                    HealthFinding(
                                        id=str(uuid.uuid4()),
                                        severity="medium",
                                        category="style",
                                        title="Hardcoded path detected",
                                        description="Path may not work on other systems",
                                        file_path=rel_path,
                                        line_start=i,
                                        line_end=i,
                                        suggested_fix="Use pathlib.Path or os.path.join with relative paths",
                                        auto_fixable=False,
                                    )
                                )
                except Exception:
                    pass

        return findings

    async def _check_security(self, repo_path: Path, repo_id: str) -> list[HealthFinding]:
        findings = []
        secret_patterns = ["password", "secret", "api_key", "token"]

        # Use os.walk with directory pruning for efficient scanning
        exclude_dirs = {
            ".venv",
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
        }
        max_file_size = 1024 * 1024  # 1MB limit

        for root, dirs, files in os.walk(repo_path):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if not file.endswith(".py"):
                    continue

                py_file = Path(root) / file

                try:
                    # Check file size before reading
                    stat = py_file.stat()
                    if stat.st_size > max_file_size:
                        continue  # Skip large files

                    content = py_file.read_text(encoding="utf-8", errors="replace")
                    rel_path = str(py_file.relative_to(repo_path))

                    for i, line in enumerate(content.split("\n"), 1):
                        lower_line = line.lower()
                        for pattern in secret_patterns:
                            if pattern in lower_line and "=" in line:
                                if any(c in line for c in ['"', "'"]):
                                    findings.append(
                                        HealthFinding(
                                            id=str(uuid.uuid4()),
                                            severity="critical",
                                            category="security",
                                            title="Possible hardcoded secret",
                                            description=f"Line contains '{pattern}' with string value",
                                            file_path=rel_path,
                                            line_start=i,
                                            line_end=i,
                                            suggested_fix="Use environment variables or secret manager",
                                            auto_fixable=False,
                                        )
                                    )
                except Exception:
                    pass

        return findings


# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.workspace_connections: dict[str, set[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: str, workspace_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        if workspace_id not in self.workspace_connections:
            self.workspace_connections[workspace_id] = set()
        self.workspace_connections[workspace_id].add(client_id)

    def disconnect(self, client_id: str, workspace_id: str):
        self.active_connections.pop(client_id, None)
        if workspace_id in self.workspace_connections:
            self.workspace_connections[workspace_id].discard(client_id)

    async def broadcast_to_workspace(self, workspace_id: str, message: dict, exclude: str = None):
        if workspace_id not in self.workspace_connections:
            return

        for client_id in self.workspace_connections[workspace_id]:
            if client_id == exclude:
                continue
            websocket = self.active_connections.get(client_id)
            if websocket:
                try:
                    await websocket.send_json(message)
                except Exception:
                    pass


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context."""
    app.state.workspace_base = Path("./workspaces")
    app.state.workspace_base.mkdir(exist_ok=True)

    app.state.git_service = GitService(app.state.workspace_base / "repos")
    app.state.terminal_service = TerminalService(app.state.workspace_base)
    app.state.graph_service = RepoGraphService(app.state.workspace_base / "repos")
    app.state.ai_agent = AIRepoHealthAgent(app.state.workspace_base / "repos")

    yield


app = FastAPI(
    title="Axiom One",
    description="Unified Software Operating Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Routes - Workspaces
@app.get("/api/v1/workspaces")
async def list_workspaces():
    return [
        Workspace(
            id="ws-1",
            name="Default Workspace",
            slug="default",
            owner_id="user-1",
            status=WorkspaceStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    ]


@app.post("/api/v1/workspaces")
async def create_workspace(name: str, slug: str):
    workspace = Workspace(
        id=str(uuid.uuid4()),
        name=name,
        slug=slug,
        owner_id="user-1",
        status=WorkspaceStatus.ACTIVE,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    workspace_path = Path(f"./workspaces/{workspace.id}")
    workspace_path.mkdir(parents=True, exist_ok=True)
    (workspace_path / "repos").mkdir(exist_ok=True)
    return workspace


# API Routes - Repositories
@app.get("/api/v1/workspaces/{workspace_id}/repositories")
async def list_repositories(workspace_id: str):
    repo_base = Path(f"./workspaces/{workspace_id}/repos")
    if not repo_base.exists():
        return []

    repos = []
    for repo_dir in repo_base.iterdir():
        if repo_dir.is_dir() and (repo_dir / ".git").exists():
            repos.append(
                Repository(
                    id=repo_dir.name,
                    workspace_id=workspace_id,
                    name=repo_dir.name,
                    full_name=f"{workspace_id}/{repo_dir.name}",
                    provider=RepoProvider.LOCAL,
                    url=str(repo_dir),
                    default_branch="main",
                )
            )
    return repos


@app.post("/api/v1/workspaces/{workspace_id}/repositories")
async def create_repository(workspace_id: str, name: str, clone_url: str = None):
    repo_path = Path(f"./workspaces/{workspace_id}/repos/{name}")
    repo_path.mkdir(parents=True, exist_ok=True)

    if clone_url:
        subprocess.run(
            ["git", "clone", clone_url, "."], cwd=repo_path, capture_output=True, timeout=300
        )
    else:
        subprocess.run(["git", "init"], cwd=repo_path, capture_output=True)
        subprocess.run(["git", "checkout", "-b", "main"], cwd=repo_path, capture_output=True)

    return Repository(
        id=name,
        workspace_id=workspace_id,
        name=name,
        full_name=f"{workspace_id}/{name}",
        provider=RepoProvider.LOCAL,
        url=str(repo_path),
        default_branch="main",
    )


# API Routes - Code Studio
@app.get("/api/v1/repositories/{repo_id}/files")
async def get_file_tree(repo_id: str, path: str = ""):
    git = app.state.git_service
    return git.get_file_tree(repo_id, path)


@app.get("/api/v1/repositories/{repo_id}/files/content")
async def get_file_content(repo_id: str, path: str, ref: str = None):
    git = app.state.git_service
    content = git.get_file_content(repo_id, path, ref)
    return {"content": content, "path": path}


@app.put("/api/v1/repositories/{repo_id}/files/content")
async def update_file(repo_id: str, path: str, content: str):
    git = app.state.git_service
    git.write_file(repo_id, path, content)
    return {"status": "saved", "path": path}


@app.get("/api/v1/repositories/{repo_id}/branches")
async def list_branches(repo_id: str):
    git = app.state.git_service
    return git.get_branches(repo_id)


@app.post("/api/v1/repositories/{repo_id}/branches")
async def create_branch(repo_id: str, name: str, base: str = "main"):
    git = app.state.git_service
    return git.create_branch(repo_id, name, base)


@app.get("/api/v1/repositories/{repo_id}/commits")
async def list_commits(repo_id: str, branch: str = "main", limit: int = 50):
    git = app.state.git_service
    return git.get_commits(repo_id, branch, limit)


@app.post("/api/v1/repositories/{repo_id}/commit")
async def create_commit(repo_id: str, message: str, files: list[str] = None):
    git = app.state.git_service
    return git.commit(repo_id, message, files)


# API Routes - Terminal
@app.post("/api/v1/terminal/sessions")
async def create_terminal_session(workspace_id: str, command: str, repository_id: str = None):
    terminal = app.state.terminal_service
    return await terminal.create_session(workspace_id, repository_id, command)


@app.websocket("/ws/terminal/{session_id}")
async def terminal_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    terminal = app.state.terminal_service

    try:
        async for output in terminal.read_output(session_id):
            await websocket.send_text(output)
    except Exception as e:
        await websocket.send_text(f"\n[Error: {e}]\n")
    finally:
        await websocket.close()


# API Routes - Repo Graph
@app.get("/api/v1/repositories/{repo_id}/graph")
async def get_repo_graph(repo_id: str):
    graph_service = app.state.graph_service
    return await graph_service.generate_graph(repo_id)


@app.get("/api/v1/repositories/{repo_id}/impact")
async def get_impact_analysis(repo_id: str, file_path: str):
    graph_service = app.state.graph_service
    graph = await graph_service.generate_graph(repo_id)
    impacted = (
        graph_service.get_impact_analysis(graph, file_path)
        if hasattr(graph_service, "get_impact_analysis")
        else []
    )

    # Find files that import from this file
    file_id = f"file:{file_path}"
    for edge in graph.edges:
        if edge.target == file_id:
            impacted.append(edge.source)

    return {
        "file_path": file_path,
        "impacted_files": impacted,
        "impact_count": len(impacted),
    }


# API Routes - AI Repo Health
@app.post("/api/v1/repositories/{repo_id}/health/analyze")
async def analyze_repo_health(repo_id: str):
    ai_agent = app.state.ai_agent
    return await ai_agent.analyze_repository(repo_id)


@app.post("/api/v1/repositories/{repo_id}/health/fix")
async def generate_fixes(repo_id: str, background_tasks: BackgroundTasks):
    ai_agent = app.state.ai_agent
    findings = await ai_agent.analyze_repository(repo_id)

    # For now, just return findings - auto-fix would create a branch
    return {
        "status": "analysis_complete",
        "total_findings": len(findings),
        "findings": findings,
    }


# API Routes - Autopsy with Brain Integration
@app.post("/api/v1/repositories/{repo_id}/autopsy")
async def run_repo_autopsy(repo_id: str, enable_brain: bool = True):
    """
    Run repository autopsy with brain cognitive analysis.
    Uses the AMOS brain to analyze critical/high severity issues.
    """
    from brain_minimal import get_minimal_brain

    # Get repository path
    repo_path = Path(f"./workspaces/default/repos/{repo_id}")
    if not repo_path.exists():
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} not found")

    # Run basic autopsy analysis
    findings = []
    total_files = 0
    issues_count = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    # Scan Python files for basic issues
    for file_path in repo_path.rglob("*.py"):
        total_files += 1
        try:
            content = file_path.read_text()
            lines = content.split("\n")

            # Check for bare except clauses
            for i, line in enumerate(lines):
                if (
                    "except:" in line
                    and "except Exception" not in line
                    and "except " not in line.replace(":", "")
                ):
                    findings.append(
                        {
                            "id": f"bare-except-{file_path}-{i}",
                            "severity": "high",
                            "category": "code_quality",
                            "title": "Bare except clause detected",
                            "description": f"Line {i+1}: Bare except clause should use 'except Exception:'",
                            "file_path": str(file_path.relative_to(repo_path)),
                            "line_number": i + 1,
                            "auto_fixable": False,
                        }
                    )
                    issues_count["high"] += 1

            # Check for datetime.now(timezone.utc) usage
            if "datetime.now(timezone.utc)" in content:
                for i, line in enumerate(lines):
                    if "datetime.now(timezone.utc)" in line:
                        findings.append(
                            {
                                "id": f"deprecated-datetime-{file_path}-{i}",
                                "severity": "medium",
                                "category": "maintenance",
                                "title": "Deprecated datetime.now(timezone.utc) usage",
                                "description": f"Line {i+1}: Use datetime.now(timezone.utc) instead",
                                "file_path": str(file_path.relative_to(repo_path)),
                                "line_number": i + 1,
                                "auto_fixable": True,
                                "suggested_fix": line.replace(
                                    "datetime.now(timezone.utc)", "datetime.now(timezone.utc)"
                                ),
                            }
                        )
                        issues_count["medium"] += 1

        except Exception:
            pass

    # Enhance with brain analysis for critical/high issues
    brain_analysis = []
    if enable_brain and findings:
        brain = get_minimal_brain()

        # Analyze top 5 critical/high issues with brain
        critical_issues = [f for f in findings if f["severity"] in ["critical", "high"]][:5]

        for issue in critical_issues:
            try:
                brain_result = brain.think(
                    f"Analyze {issue['category']} issue: {issue['title']}. "
                    f"Description: {issue['description']}. "
                    f"File: {issue['file_path']}",
                    domain="code_review",
                    context={
                        "repo_id": repo_id,
                        "issue_type": issue["category"],
                        "severity": issue["severity"],
                    },
                )
                brain_analysis.append(
                    {
                        "issue_id": issue["id"],
                        "brain_confidence": brain_result.confidence,
                        "brain_reasoning": brain_result.reasoning,
                        "brain_content": brain_result.content[:200]
                        if brain_result.content
                        else None,
                    }
                )
            except Exception:
                pass  # Brain analysis is best-effort

    return {
        "repo_id": repo_id,
        "repo_path": str(repo_path),
        "total_files_scanned": total_files,
        "total_issues": len(findings),
        "issues_breakdown": issues_count,
        "findings": findings,
        "brain_analysis": brain_analysis if brain_analysis else None,
        "brain_enabled": enable_brain,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
    }


# API Routes - Health
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/")
async def root():
    return {
        "name": "Axiom One",
        "version": "1.0.0",
        "description": "Unified Software Operating Platform",
        "endpoints": [
            "/api/v1/workspaces",
            "/api/v1/repositories/{repo_id}/files",
            "/api/v1/repositories/{repo_id}/branches",
            "/api/v1/repositories/{repo_id}/commits",
            "/api/v1/repositories/{repo_id}/graph",
            "/api/v1/repositories/{repo_id}/health/analyze",
            "/api/v1/terminal/sessions",
            "/ws/terminal/{session_id}",
            "/health",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
