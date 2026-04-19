#!/usr/bin/env python3
"""
Axiom One Standalone Server with AMOS Brain Integration

A lightweight implementation using only stdlib plus AMOS brain capabilities.
Compatible with Python 3.9+.

Owner: Trang Phan
Version: 2.0.0
"""

import ast
import json
import re
import subprocess
import uuid
from datetime import datetime, timezone
UTC = timezone.utc
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import parse_qs, urlparse

# ============================================================================
# AMOS BRAIN INTEGRATION
# ============================================================================

# Try to import brain bridge
try:
    from axiom_one_brain_bridge import _BRAIN_AVAILABLE, get_brain_bridge
except Exception:
    _BRAIN_AVAILABLE = False
    get_brain_bridge = None

# Try to import canon integration
try:
    from amos_canon_integration import _CANON_AVAILABLE, get_canon_loader, initialize_canon
except Exception:
    _CANON_AVAILABLE = False
    get_canon_loader = None
    initialize_canon = None

# ============================================================================
# DATA MODELS (Pure Python - No Pydantic)
# ============================================================================


class Workspace:
    def __init__(
        self,
        id: str,
        name: str,
        slug: str,
        owner_id: str,
        status: str = "active",
        created_at: str = None,
        updated_at: str = None,
    ):
        self.id = id
        self.name = name
        self.slug = slug
        self.owner_id = owner_id
        self.status = status
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.updated_at = updated_at or datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "owner_id": self.owner_id,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class Repository:
    def __init__(
        self, id: str, workspace_id: str, name: str, provider: str = "local", url: str = ""
    ):
        self.id = id
        self.workspace_id = workspace_id
        self.name = name
        self.full_name = f"{workspace_id}/{name}"
        self.provider = provider
        self.url = url
        self.default_branch = "main"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "name": self.name,
            "full_name": self.full_name,
            "provider": self.provider,
            "url": self.url,
            "default_branch": self.default_branch,
        }


class FileNode:
    def __init__(
        self,
        path: str,
        name: str,
        type: str,
        size: int = 0,
        git_status: str = None,
        children: list = None,
    ):
        self.path = path
        self.name = name
        self.type = type
        self.size = size
        self.git_status = git_status
        self.children = children

    def to_dict(self) -> dict:
        result = {
            "path": self.path,
            "name": self.name,
            "type": self.type,
            "size": self.size,
            "git_status": self.git_status,
        }
        if self.children:
            result["children"] = [c.to_dict() for c in self.children]
        return result


class Commit:
    def __init__(
        self, sha: str, message: str, author_name: str, author_email: str, authored_at: str
    ):
        self.sha = sha
        self.message = message
        self.author_name = author_name
        self.author_email = author_email
        self.authored_at = authored_at
        self.parent_shas = []

    def to_dict(self) -> dict:
        return {
            "sha": self.sha,
            "message": self.message,
            "author_name": self.author_name,
            "authored_at": self.authored_at,
        }


class HealthFinding:
    def __init__(
        self,
        id: str,
        severity: str,
        category: str,
        title: str,
        description: str,
        file_path: str = None,
        line_start: int = None,
        auto_fixable: bool = False,
    ):
        self.id = id
        self.severity = severity
        self.category = category
        self.title = title
        self.description = description
        self.file_path = file_path
        self.line_start = line_start
        self.line_end = line_start
        self.suggested_fix = None
        self.auto_fixable = auto_fixable

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "severity": self.severity,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "auto_fixable": self.auto_fixable,
        }


# ============================================================================
# BRAIN-POWERED AI SERVICES
# ============================================================================


class IntelligentCodeAnalyzer:
    """AI-powered code analysis using AST and pattern recognition."""

    def __init__(self, repo_base: Path):
        self.repo_base = repo_base

    def analyze_file(self, repo_id: str, file_path: str) -> Dict[str, Any]:
        """Perform deep analysis of a Python file."""
        full_path = self.repo_base / repo_id / file_path
        if not full_path.exists():
            return {"error": "File not found"}

        try:
            content = full_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(content)

            analysis = {
                "file": file_path,
                "imports": self._extract_imports(tree),
                "functions": self._extract_functions(tree),
                "classes": self._extract_classes(tree),
                "complexity": self._calculate_complexity(tree),
                "issues": self._detect_code_smells(tree, content),
                "suggestions": self._generate_suggestions(tree, content),
            }
            return analysis
        except SyntaxError as e:
            return {"file": file_path, "error": f"Syntax error: {e}"}
        except Exception as e:
            return {"file": file_path, "error": str(e)}

    def _extract_imports(self, tree: ast.AST) -> List[dict[str, Any]]:
        """Extract all imports from AST."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        {
                            "type": "import",
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                        }
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(
                        {
                            "type": "from_import",
                            "module": module,
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                        }
                    )
        return imports

    def _extract_functions(self, tree: ast.AST) -> List[dict[str, Any]]:
        """Extract function definitions with metrics."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    "name": node.name,
                    "line": node.lineno,
                    "args": len(node.args.args),
                    "docstring": ast.get_docstring(node),
                    "returns": self._get_return_annotation(node),
                }
                functions.append(func_info)
        return functions

    def _extract_classes(self, tree: ast.AST) -> List[dict[str, Any]]:
        """Extract class definitions."""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "line": node.lineno,
                    "bases": [base.id for base in node.bases if isinstance(base, ast.Name)],
                    "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                    "docstring": ast.get_docstring(node),
                }
                classes.append(class_info)
        return classes

    def _calculate_complexity(self, tree: ast.AST) -> Dict[str, int]:
        """Calculate cyclomatic complexity."""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(
                node, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With, ast.Assert)
            ):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return {"cyclomatic": complexity}

    def _detect_code_smells(self, tree: ast.AST, content: str) -> List[dict[str, Any]]:
        """Detect potential code smells and anti-patterns."""
        issues = []

        # Check for long functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                lines = node.end_lineno - node.lineno if node.end_lineno else 0
                if lines > 50:
                    issues.append(
                        {
                            "type": "long_function",
                            "severity": "medium",
                            "message": f"Function '{node.name}' is {lines} lines long",
                            "line": node.lineno,
                            "suggestion": "Consider breaking into smaller functions",
                        }
                    )

        # Check for bare except clauses
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    issues.append(
                        {
                            "type": "bare_except",
                            "severity": "high",
                            "message": "Bare except clause detected",
                            "line": node.lineno,
                            "suggestion": "Use 'except Exception:' instead",
                        }
                    )

        # Check for TODO/FIXME comments
        todo_pattern = re.compile(r"#\s*(TODO|FIXME|XXX|HACK)", re.IGNORECASE)
        for i, line in enumerate(content.split("\n"), 1):
            match = todo_pattern.search(line)
            if match:
                issues.append(
                    {
                        "type": "todo",
                        "severity": "low",
                        "message": f"{match.group(1)} comment found",
                        "line": i,
                        "suggestion": "Address or remove before production",
                    }
                )

        return issues

    def _generate_suggestions(self, tree: ast.AST, content: str) -> List[dict[str, Any]]:
        """Generate AI-powered improvement suggestions."""
        suggestions = []

        # Suggest type hints for functions without them
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.args.args and not node.returns:
                    arg_names = [arg.arg for arg in node.args.args if arg.arg != "self"]
                    if arg_names:
                        suggestions.append(
                            {
                                "type": "type_hints",
                                "message": f"Add type hints to function '{node.name}'",
                                "line": node.lineno,
                                "priority": "medium",
                                "example": f"def {node.name}(...) -> ...:",
                            }
                        )

        # Suggest dataclasses for simple classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_only_init = all(
                    isinstance(n, (ast.FunctionDef, ast.Pass, ast.Expr)) for n in node.body
                )
                init_methods = [
                    n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == "__init__"
                ]
                if has_only_init and init_methods:
                    suggestions.append(
                        {
                            "type": "dataclass",
                            "message": f"Consider using @dataclass for '{node.name}'",
                            "line": node.lineno,
                            "priority": "low",
                            "example": "@dataclass\nclass MyClass:",
                        }
                    )

        return suggestions

    def _get_return_annotation(self, node: ast.FunctionDef) -> str:
        """Get return type annotation if present."""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return str(node.returns.value)
        return None


class GitService:
    def __init__(self, repo_base_path: Path):
        self.repo_base_path = repo_base_path

    def _run_git(self, repo_id: str, *args: str) -> Tuple[int, str, str]:
        repo_path = self.repo_base_path / repo_id
        try:
            result = subprocess.run(
                ["git"] + list(args),
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except FileNotFoundError:
            return -1, "", "Git not found"

    def get_file_tree(self, repo_id: str, path: str = "") -> List[FileNode]:
        repo_path = self.repo_base_path / repo_id / path
        if not repo_path.exists():
            return []

        nodes = []
        try:
            for item in sorted(repo_path.iterdir()):
                if item.name.startswith(".") and item.name != ".github":
                    continue

                node_type = "directory" if item.is_dir() else "file"
                rel_path = str(item.relative_to(self.repo_base_path / repo_id))

                status_code, stdout, _ = self._run_git(repo_id, "status", "--porcelain", rel_path)
                git_status = stdout[:2].strip() if status_code == 0 and stdout else None

                node = FileNode(
                    path=rel_path,
                    name=item.name,
                    type=node_type,
                    size=item.stat().st_size if item.is_file() else 0,
                    git_status=git_status,
                )

                if item.is_dir():
                    node.children = self.get_file_tree(repo_id, rel_path)

                nodes.append(node)
        except PermissionError:
            pass

        return nodes

    def get_file_content(self, repo_id: str, file_path: str) -> str:
        full_path = self.repo_base_path / repo_id / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return full_path.read_text(encoding="utf-8", errors="replace")

    def write_file(self, repo_id: str, file_path: str, content: str) -> None:
        full_path = self.repo_base_path / repo_id / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")

    def get_commits(self, repo_id: str, max_count: int = 50) -> List[Commit]:
        code, stdout, _ = self._run_git(
            repo_id, "log", f"-{max_count}", "--format=%H%x00%an%x00%ae%x00%at%x00%s"
        )
        if code != 0:
            return []

        commits = []
        for line in stdout.strip().split("\n"):
            parts = line.split("\x00")
            if len(parts) < 5:
                continue

            commits.append(
                Commit(
                    sha=parts[0],
                    message=parts[4],
                    author_name=parts[1],
                    author_email=parts[2],
                    authored_at=datetime.fromtimestamp(int(parts[3]), tz=timezone.utc).isoformat(),
                )
            )

        return commits

    def create_branch(self, repo_id: str, name: str, base: str = "main") -> bool:
        code, _, _ = self._run_git(repo_id, "checkout", "-b", name, base)
        return code == 0

    def commit(self, repo_id: str, message: str, files: List[str] = None) -> bool:
        if files:
            for f in files:
                self._run_git(repo_id, "add", f)
        else:
            self._run_git(repo_id, "add", "-A")

        code, _, _ = self._run_git(repo_id, "commit", "-m", message)
        return code == 0


class AIRepoHealthAgent:
    def __init__(self, repo_base: Path):
        self.repo_base = repo_base

    def analyze_repository(self, repo_id: str) -> List[HealthFinding]:
        repo_path = self.repo_base / repo_id
        findings: List[HealthFinding] = []

        findings.extend(self._check_imports(repo_path, repo_id))
        findings.extend(self._check_missing_files(repo_path, repo_id))
        findings.extend(self._check_path_assumptions(repo_path, repo_id))
        findings.extend(self._check_security(repo_path, repo_id))

        return findings

    def _check_imports(self, repo_path: Path, repo_id: str) -> List[HealthFinding]:
        findings = []

        for py_file in repo_path.rglob("*.py"):
            if ".venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                rel_path = str(py_file.relative_to(repo_path))

                for i, line in enumerate(content.split("\n"), 1):
                    stripped = line.strip()
                    if stripped.startswith("from ") or stripped.startswith("import "):
                        parts = stripped.split()
                        if len(parts) >= 2:
                            module = parts[1].split(".")[0]

                            stdlib_modules = [
                                "os",
                                "sys",
                                "typing",
                                "pathlib",
                                "json",
                                "datetime",
                                "collections",
                                "enum",
                                "re",
                                "math",
                            ]
                            if module not in stdlib_modules:
                                try:
                                    __import__(module)
                                except ImportError:
                                    findings.append(
                                        HealthFinding(
                                            id=str(uuid.uuid4()),
                                            severity="high",
                                            category="import",
                                            title=f"Broken import: {module}",
                                            description=f"Cannot import '{module}'",
                                            file_path=rel_path,
                                            line_start=i,
                                        )
                                    )
            except Exception:
                pass

        return findings

    def _check_missing_files(self, repo_path: Path, repo_id: str) -> List[HealthFinding]:
        findings = []

        for filename in ["README.md", ".gitignore"]:
            if not (repo_path / filename).exists():
                findings.append(
                    HealthFinding(
                        id=str(uuid.uuid4()),
                        severity="medium" if filename == ".gitignore" else "low",
                        category="style",
                        title=f"Missing {filename}",
                        description=f"Repository should have a {filename} file",
                        auto_fixable=filename == ".gitignore",
                    )
                )

        return findings

    def _check_path_assumptions(self, repo_path: Path, repo_id: str) -> List[HealthFinding]:
        findings = []

        for py_file in repo_path.rglob("*.py"):
            if ".venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
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
                                )
                            )
            except Exception:
                pass

        return findings

    def _check_security(self, repo_path: Path, repo_id: str) -> List[HealthFinding]:
        findings = []
        secret_patterns = ["password", "secret", "api_key", "token"]

        for py_file in repo_path.rglob("*.py"):
            if ".venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
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
                                        description=f"Line contains '{pattern}'",
                                        file_path=rel_path,
                                        line_start=i,
                                    )
                                )
            except Exception:
                pass

        return findings


# ============================================================================
# IN-MEMORY DATABASE
# ============================================================================


class InMemoryDB:
    def __init__(self):
        self.workspaces: Dict[str, Workspace] = {}
        self.repositories: Dict[str, Repository] = {}
        self.terminal_sessions: Dict[str, dict] = {}

        # Create default workspace
        default_ws = Workspace(
            id="ws-default",
            name="Default Workspace",
            slug="default",
            owner_id="user-1",
        )
        self.workspaces[default_ws.id] = default_ws

    def get_workspace(self, id: str) -> Optional[Workspace]:
        return self.workspaces.get(id)

    def list_workspaces(self) -> List[Workspace]:
        return list(self.workspaces.values())

    def create_workspace(self, name: str, slug: str) -> Workspace:
        ws = Workspace(
            id=str(uuid.uuid4()),
            name=name,
            slug=slug,
            owner_id="user-1",
        )
        self.workspaces[ws.id] = ws

        # Create workspace directory
        workspace_path = Path(f"./workspaces/{ws.id}")
        workspace_path.mkdir(parents=True, exist_ok=True)
        (workspace_path / "repos").mkdir(exist_ok=True)

        return ws

    def list_repositories(self, workspace_id: str = None) -> List[Repository]:
        repos = list(self.repositories.values())
        if workspace_id:
            repos = [r for r in repos if r.workspace_id == workspace_id]
        return repos

    def create_repository(self, workspace_id: str, name: str) -> Repository:
        repo = Repository(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            name=name,
            url=f"./workspaces/{workspace_id}/repos/{name}",
        )
        self.repositories[repo.id] = repo

        # Create repo directory and init git
        repo_path = Path(f"./workspaces/{workspace_id}/repos/{name}")
        repo_path.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init"], cwd=repo_path, capture_output=True)
        subprocess.run(["git", "checkout", "-b", "main"], cwd=repo_path, capture_output=True)

        return repo


# Global database instance
db = InMemoryDB()
git_service = GitService(Path("./workspaces/repos"))
health_agent = AIRepoHealthAgent(Path("./workspaces/repos"))
intelligent_analyzer = IntelligentCodeAnalyzer(Path("./workspaces/repos"))


# ============================================================================
# HTTP HANDLER
# ============================================================================


class AxiomOneHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        # Suppress default logging
        pass

    def send_json_response(self, data: dict, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        # API Routes
        if path == "/":
            self.send_json_response(
                {
                    "name": "Axiom One Standalone",
                    "version": "2.0.0",
                    "brain_available": _BRAIN_AVAILABLE and get_brain_bridge is not None,
                    "endpoints": [
                        "/api/workspaces",
                        "/api/repositories",
                        "/api/repos/{id}/files",
                        "/api/repos/{id}/files/content?path=...",
                        "/api/repos/{id}/files/analyze?path=...",
                        "/api/repos/{id}/commits",
                        "/api/repos/{id}/health/analyze",
                        "/api/repos/{id}/health/fix",
                        "/api/repos/{id}/brain/analyze?path=...",
                        "/api/brain/status",
                        "/health",
                    ],
                }
            )

        elif path == "/health":
            health_data = {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "brain_available": _BRAIN_AVAILABLE and get_brain_bridge is not None,
                "version": "2.0.0",
            }
            self.send_json_response(health_data)

        elif path == "/api/brain/status":
            """Get brain status and statistics."""
            if get_brain_bridge is None:
                self.send_json_response(
                    {
                        "available": False,
                        "message": "Brain bridge not installed",
                    }
                )
            else:
                try:
                    bridge = get_brain_bridge()
                    stats = bridge.get_stats()
                    self.send_json_response(
                        {
                            "available": stats.get("initialized", False),
                            "brain_available": stats.get("brain_available", False),
                            "total_tasks": stats.get("total_tasks", 0),
                        }
                    )
                except Exception as e:
                    self.send_json_response(
                        {
                            "available": False,
                            "error": str(e),
                        },
                        500,
                    )

        elif path == "/api/canon/status":
            """Get canon integration status."""
            if get_canon_loader is None:
                self.send_json_response(
                    {
                        "available": False,
                        "message": "Canon integration not installed",
                    }
                )
            else:
                try:
                    canon = get_canon_loader()
                    if canon.is_loaded():
                        self.send_json_response(
                            {
                                "available": True,
                                "loaded": True,
                                "glossary_layers": len(canon.get_glossary().get("layers", [])),
                                "agents": len(canon.get_agent_registry().get("agents", {})),
                                "engines": len(
                                    canon.get_brain_os_spec()[0]
                                    .get("components", {})
                                    .get("brain_core", {})
                                    .get("engines", {})
                                )
                                if canon.get_brain_os_spec()
                                else 0,
                                "cognitive_stack_keys": list(canon.get_cognitive_stack().keys()),
                            }
                        )
                    else:
                        self.send_json_response(
                            {
                                "available": True,
                                "loaded": False,
                                "message": "Canon not yet initialized",
                            }
                        )
                except Exception as e:
                    self.send_json_response(
                        {
                            "available": False,
                            "error": str(e),
                        },
                        500,
                    )

        elif path == "/api/canon/glossary":
            """Get the canonical glossary."""
            if get_canon_loader is None:
                self.send_json_response(
                    {
                        "error": "Canon integration not installed",
                    },
                    503,
                )
            else:
                try:
                    canon = get_canon_loader()
                    self.send_json_response(canon.get_glossary())
                except Exception as e:
                    self.send_json_response({"error": str(e)}, 500)

        elif path == "/api/canon/agents":
            """Get the agent registry."""
            if get_canon_loader is None:
                self.send_json_response(
                    {
                        "error": "Canon integration not installed",
                    },
                    503,
                )
            else:
                try:
                    canon = get_canon_loader()
                    self.send_json_response(canon.get_agent_registry())
                except Exception as e:
                    self.send_json_response({"error": str(e)}, 500)

        elif path == "/api/canon/engines":
            """Get the brain OS engine specifications."""
            if get_canon_loader is None:
                self.send_json_response(
                    {
                        "error": "Canon integration not installed",
                    },
                    503,
                )
            else:
                try:
                    canon = get_canon_loader()
                    spec = canon.get_brain_os_spec()
                    if spec and len(spec) > 0:
                        components = spec[0].get("components", {})
                        brain_core = components.get("brain_core", {})
                        engines = brain_core.get("engines", {})
                        self.send_json_response(
                            {
                                "engines": engines,
                                "total_engines": len(engines),
                            }
                        )
                    else:
                        self.send_json_response(
                            {
                                "engines": {},
                                "total_engines": 0,
                            }
                        )
                except Exception as e:
                    self.send_json_response({"error": str(e)}, 500)

        elif path == "/api/brain/think":
            """POST endpoint for brain reasoning."""
            if self.command != "POST":
                self.send_json_response({"error": "Method not allowed"}, 405)
                return

            if get_brain_bridge is None:
                self.send_json_response(
                    {
                        "error": "Brain not available",
                        "brain_available": False,
                    },
                    503,
                )
                return

            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode())

                query = data.get("query", "")
                context = data.get("context", {})

                if not query:
                    self.send_json_response({"error": "Query required"}, 400)
                    return

                bridge = get_brain_bridge()
                result = bridge.think(query, context)

                self.send_json_response(
                    {
                        "query": query,
                        "brain_available": True,
                        "result": result,
                    }
                )
            except json.JSONDecodeError:
                self.send_json_response({"error": "Invalid JSON"}, 400)
            except Exception as e:
                self.send_json_response(
                    {
                        "error": str(e),
                        "brain_available": _BRAIN_AVAILABLE,
                    },
                    500,
                )
            else:
                try:
                    bridge = get_brain_bridge()
                    stats = bridge.get_stats()
                    self.send_json_response(
                        {
                            "available": stats.get("initialized", False),
                            "brain_available": stats.get("brain_available", False),
                            "total_tasks": stats.get("total_tasks", 0),
                            "completed": stats.get("completed", 0),
                            "failed": stats.get("failed", 0),
                            "pending": stats.get("pending", 0),
                        }
                    )
                except Exception as e:
                    self.send_json_response(
                        {
                            "available": False,
                            "error": str(e),
                        }
                    )

        elif path == "/api/workspaces":
            workspaces = db.list_workspaces()
            self.send_json_response({"workspaces": [w.to_dict() for w in workspaces]})

        elif path == "/api/repositories":
            repos = db.list_repositories()
            self.send_json_response({"repositories": [r.to_dict() for r in repos]})

        elif path.startswith("/api/repos/") and path.endswith("/files"):
            parts = path.split("/")
            if len(parts) >= 5:
                repo_id = parts[3]
                files = git_service.get_file_tree(repo_id)
                self.send_json_response({"files": [f.to_dict() for f in files]})
            else:
                self.send_json_response({"error": "Invalid path"}, 400)

        elif path.startswith("/api/repos/") and path.endswith("/commits"):
            parts = path.split("/")
            if len(parts) >= 5:
                repo_id = parts[3]
                commits = git_service.get_commits(repo_id)
                self.send_json_response({"commits": [c.to_dict() for c in commits]})
            else:
                self.send_json_response({"error": "Invalid path"}, 400)

        elif path.startswith("/api/repos/") and "/files/content" in path:
            parts = path.split("/")
            if len(parts) >= 6:
                repo_id = parts[3]
                query = parse_qs(parsed.query)
                file_path = query.get("path", [""])[0]
                try:
                    content = git_service.get_file_content(repo_id, file_path)
                    self.send_json_response({"path": file_path, "content": content})
                except FileNotFoundError:
                    self.send_json_response({"error": "File not found"}, 404)
            else:
                self.send_json_response({"error": "Invalid path"}, 400)

        elif path.startswith("/api/repos/") and path.endswith("/health/analyze"):
            parts = path.split("/")
            if len(parts) >= 5:
                repo_id = parts[3]
                findings = health_agent.analyze_repository(repo_id)
                self.send_json_response(
                    {
                        "findings": [f.to_dict() for f in findings],
                        "total": len(findings),
                    }
                )
            else:
                self.send_json_response({"error": "Invalid path"}, 400)

        elif path.startswith("/api/repos/") and "/files/analyze" in path:
            parts = path.split("/")
            if len(parts) >= 6:
                repo_id = parts[3]
                query = parse_qs(parsed.query)
                file_path = query.get("path", [""])[0]
                if file_path:
                    analysis = intelligent_analyzer.analyze_file(repo_id, file_path)
                    self.send_json_response(analysis)
                else:
                    self.send_json_response({"error": "Missing path parameter"}, 400)
            else:
                self.send_json_response({"error": "Invalid path"}, 400)

        else:
            self.send_json_response({"error": "Not found"}, 404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        # Read body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            data = json.loads(body.decode()) if body else {}
        except json.JSONDecodeError:
            data = {}

        if path == "/api/workspaces":
            name = data.get("name", "New Workspace")
            slug = data.get("slug", str(uuid.uuid4())[:8])
            ws = db.create_workspace(name, slug)
            self.send_json_response(ws.to_dict(), 201)

        elif path == "/api/repositories":
            workspace_id = data.get("workspace_id", "ws-default")
            name = data.get("name", f"repo-{uuid.uuid4().hex[:8]}")
            repo = db.create_repository(workspace_id, name)
            self.send_json_response(repo.to_dict(), 201)

        elif path.startswith("/api/repos/") and "/branches" in path:
            parts = path.split("/")
            if len(parts) >= 5:
                repo_id = parts[3]
                name = data.get("name", "feature-branch")
                success = git_service.create_branch(repo_id, name)
                self.send_json_response(
                    {
                        "created": success,
                        "name": name,
                    }
                )
            else:
                self.send_json_response({"error": "Invalid path"}, 400)

        elif path.startswith("/api/repos/") and path.endswith("/commits"):
            parts = path.split("/")
            if len(parts) >= 5:
                repo_id = parts[3]
                message = data.get("message", "Update files")
                files = data.get("files")
                success = git_service.commit(repo_id, message, files)
                self.send_json_response(
                    {
                        "committed": success,
                        "message": message,
                    }
                )
            else:
                self.send_json_response({"error": "Invalid path"}, 400)

        elif path.startswith("/api/repos/") and "/files/content" in path:
            parts = path.split("/")
            if len(parts) >= 6:
                repo_id = parts[3]
                file_path = data.get("path", "")
                content = data.get("content", "")
                git_service.write_file(repo_id, file_path, content)
                self.send_json_response(
                    {
                        "saved": True,
                        "path": file_path,
                    }
                )
            else:
                self.send_json_response({"error": "Invalid path"}, 400)

        elif path.startswith("/api/repos/") and path.endswith("/health/fix"):
            parts = path.split("/")
            if len(parts) >= 5:
                repo_id = parts[3]
                repo_path = Path(f"./workspaces/repos/{repo_id}")

                # Apply auto-fixes
                fixes_applied = 0
                if not (repo_path / ".gitignore").exists():
                    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
.Python
build/
dist/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
.venv/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
"""
                    (repo_path / ".gitignore").write_text(gitignore_content)
                    fixes_applied += 1

                self.send_json_response(
                    {
                        "fixes_applied": fixes_applied,
                        "status": "completed",
                    }
                )
            else:
                self.send_json_response({"error": "Invalid path"}, 400)

        elif path.startswith("/api/repos/") and "/brain/analyze" in path:
            parts = path.split("/")
            if len(parts) >= 6:
                repo_id = parts[3]
                query = parse_qs(parsed.query)
                file_path = query.get("path", [""])[0]

                # Check if brain is available
                if get_brain_bridge is None:
                    self.send_json_response(
                        {
                            "error": "Brain not available",
                            "brain_available": False,
                            "message": "AMOS brain integration is not installed",
                        },
                        503,
                    )
                    return

                try:
                    # Read file content
                    content = git_service.get_file_content(repo_id, file_path)

                    # Use brain bridge for analysis
                    bridge = get_brain_bridge()
                    result = bridge.analyze_code(content)

                    self.send_json_response(
                        {
                            "file": file_path,
                            "brain_available": True,
                            "analysis": result,
                        }
                    )
                except FileNotFoundError:
                    self.send_json_response({"error": "File not found"}, 404)
                except Exception as e:
                    self.send_json_response(
                        {"error": str(e), "brain_available": _BRAIN_AVAILABLE}, 500
                    )
            else:
                self.send_json_response({"error": "Invalid path"}, 400)

        else:
            self.send_json_response({"error": "Not found"}, 404)

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


# ============================================================================
# MAIN SERVER
# ============================================================================


def run_server(host: str = "0.0.0.0", port: int = 8001) -> None:
    """Run the standalone Axiom One server."""
    # Initialize Canon on startup
    canon_status = {"status": "unavailable"}
    if _CANON_AVAILABLE:
        try:
            import asyncio

            canon_loaded = asyncio.run(initialize_canon())
            if canon_loaded:
                canon = get_canon_loader()
                canon_status = {
                    "status": "loaded",
                    "glossary_terms": len(canon.get_glossary().get("layers", [])),
                    "agents": len(canon.get_agent_registry().get("agents", {})),
                    "engines": len(
                        canon.get_brain_os_spec()[0]
                        .get("components", {})
                        .get("brain_core", {})
                        .get("engines", {})
                    )
                    if canon.get_brain_os_spec()
                    else 0,
                }
                print("✓ Canon (_00_AMOS_CANON) integrated")
            else:
                canon_status = {"status": "failed"}
                print("⚠ Canon initialization failed")
        except Exception as e:
            canon_status = {"status": "error", "error": str(e)}
            print(f"⚠ Canon error: {e}")
    else:
        print("ℹ Canon not available")

    server = HTTPServer((host, port), AxiomOneHandler)
    print(f"\nAxiom One Standalone Server running on http://{host}:{port}")
    print(f"API Documentation: http://{host}:{port}/")
    print("\nAvailable endpoints:")
    print(f"  GET  http://{host}:{port}/api/workspaces")
    print(f"  POST http://{host}:{port}/api/workspaces")
    print(f"  GET  http://{host}:{port}/api/repositories")
    print(f"  POST http://{host}:{port}/api/repositories")
    print(f"  GET  http://{host}:{port}/api/repos/{{id}}/files")
    print(f"  GET  http://{host}:{port}/api/repos/{{id}}/files/content?path=...")
    print(f"  GET  http://{host}:{port}/api/repos/{{id}}/files/analyze?path=...")
    print(f"  PUT  http://{host}:{port}/api/repos/{{id}}/files/content")
    print(f"  GET  http://{host}:{port}/api/repos/{{id}}/commits")
    print(f"  POST http://{host}:{port}/api/repos/{{id}}/commits")
    print(f"  POST http://{host}:{port}/api/repos/{{id}}/health/analyze")
    print(f"  POST http://{host}:{port}/api/repos/{{id}}/health/fix")
    print("\nBrain-Powered Endpoints (AMOS AI):")
    print(f"  GET  http://{host}:{port}/api/brain/status")
    print(f"  POST http://{host}:{port}/api/brain/think")
    print(f"  POST http://{host}:{port}/api/repos/{id}/brain/analyze")
    print("\nCanon Integration Endpoints (_00_AMOS_CANON):")
    print(f"  GET  http://{host}:{port}/api/canon/status")
    print(f"  GET  http://{host}:{port}/api/canon/glossary")
    print(f"  GET  http://{host}:{port}/api/canon/agents")
    print(f"  GET  http://{host}:{port}/api/canon/engines")
    print("\nPress Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Axiom One Standalone Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    args = parser.parse_args()

    run_server(args.host, args.port)
