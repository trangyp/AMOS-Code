"""Axiom One Standalone Server - Real Working Features"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "clawspring"))

# Import Axiom One components
from axiom_one.git_service import GitService
from axiom_one_graph import AxiomGraph
from axiom_one_repo_autopsy import RepoAutopsyEngine

app = FastAPI(title="Axiom One", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# State
_graph: Optional[AxiomGraph] = None
_engine: Optional[RepoAutopsyEngine] = None
_git_service: Optional[GitService] = None


def get_graph() -> AxiomGraph:
    """Get or create graph."""
    global _graph
    if _graph is None:
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_auth = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password"))
        _graph = AxiomGraph(neo4j_uri, neo4j_auth)
    return _graph


def get_engine() -> RepoAutopsyEngine:
    """Get autopsy engine."""
    global _engine
    if _engine is None:
        _engine = RepoAutopsyEngine(get_graph())
    return _engine


def get_git_service() -> GitService:
    """Get git service."""
    global _git_service
    if _git_service is None:
        base_path = Path(os.getenv("REPO_BASE", "/tmp/repos"))
        base_path.mkdir(parents=True, exist_ok=True)
        _git_service = GitService(base_path)
    return _git_service


# ============================================================================
# Pydantic Models
# ============================================================================


class AutopsyRequest(BaseModel):
    repo_path: str
    repo_name: str = ""
    owner_id: str = ""


class AutopsyResponse(BaseModel):
    repo_path: str
    repo_name: str
    started_at: str
    completed_at: str
    summary: Dict[str, Any]
    issues: List[dict[str, Any]]
    validation_steps: List[dict[str, Any]]


class GitTreeRequest(BaseModel):
    repo_id: str
    path: str = ""


class FileContentRequest(BaseModel):
    repo_id: str
    file_path: str


class CreateBranchRequest(BaseModel):
    repo_id: str
    branch_name: str
    base: str = "main"


class CommitRequest(BaseModel):
    repo_id: str
    message: str
    files: List[str] = None


# ============================================================================
# REPO AUTOPSY ENDPOINTS
# ============================================================================


@app.post("/axiom-one/autopsy", response_model=AutopsyResponse)
async def run_repo_autopsy(request: AutopsyRequest) -> AutopsyResponse:
    """
    Run complete repo autopsy.
    Analyzes repository structure and runs validation.
    """
    engine = get_engine()

    try:
        report = await engine.autopsy(
            repo_path=request.repo_path,
            repo_name=request.repo_name or Path(request.repo_path).name,
            owner_id=request.owner_id or "system",
        )

        return AutopsyResponse(
            repo_path=report.repo_path,
            repo_name=report.repo_name,
            started_at=report.started_at,
            completed_at=report.completed_at,
            summary=report.to_dict().get("summary", {}),
            issues=[
                {
                    "id": i.id,
                    "category": i.category.value,
                    "severity": i.severity.value,
                    "title": i.title,
                    "auto_fixable": i.auto_fixable,
                }
                for i in report.issues
            ],
            validation_steps=[
                {
                    "step": v.step,
                    "success": v.success,
                    "duration_ms": v.duration_ms,
                    "exit_code": v.exit_code,
                }
                for v in report.validation_results
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GIT OPERATIONS ENDPOINTS
# ============================================================================


@app.post("/axiom-one/git/tree")
async def get_git_tree(request: GitTreeRequest) -> Dict[str, Any]:
    """Get file tree for repository."""
    git = get_git_service()
    try:
        nodes = git.get_file_tree(request.repo_id, request.path)
        return {
            "nodes": [
                {
                    "path": n.path,
                    "name": n.name,
                    "type": n.type.value,
                    "size": n.size,
                    "git_status": n.git_status,
                }
                for n in nodes
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/axiom-one/git/content")
async def get_file_content(request: FileContentRequest) -> Dict[str, str]:
    """Get file content."""
    git = get_git_service()
    try:
        content = git.get_file_content(request.repo_id, request.file_path)
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/axiom-one/git/branches")
async def get_branches(repo_id: str) -> Dict[str, Any]:
    """Get branches."""
    git = get_git_service()
    try:
        branches = git.get_branches(repo_id)
        return {
            "branches": [
                {
                    "name": b.name,
                    "sha": b.sha,
                    "is_default": b.is_default,
                    "ahead_count": b.ahead_count,
                    "behind_count": b.behind_count,
                }
                for b in branches
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/axiom-one/git/create-branch")
async def create_branch(request: CreateBranchRequest) -> Dict[str, Any]:
    """Create new branch."""
    git = get_git_service()
    try:
        branch = git.create_branch(request.repo_id, request.branch_name, request.base)
        return {
            "name": branch.name,
            "sha": branch.sha,
            "is_default": branch.is_default,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/axiom-one/git/commit")
async def commit(request: CommitRequest) -> Dict[str, Any]:
    """Create commit."""
    git = get_git_service()
    try:
        commit = git.commit(request.repo_id, request.message, request.files)
        return {
            "sha": commit.sha,
            "message": commit.message,
            "author": commit.author_name,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# HEALTH & INFO
# ============================================================================


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "healthy", "service": "axiom-one"}


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "name": "Axiom One",
        "version": "1.0.0",
        "endpoints": [
            "POST /axiom-one/autopsy - Repo autopsy",
            "POST /axiom-one/git/tree - File tree",
            "POST /axiom-one/git/content - File content",
            "POST /axiom-one/git/branches - List branches",
            "POST /axiom-one/git/create-branch - Create branch",
            "POST /axiom-one/git/commit - Create commit",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
