"""Axiom One - Data Models"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class WorkspaceStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class RepoProvider(str, Enum):
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"
    LOCAL = "local"


class FileNodeType(str, Enum):
    FILE = "file"
    DIRECTORY = "directory"
    SYMLINK = "symlink"


class ChangeType(str, Enum):
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


class IssueStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    CLOSED = "closed"


class PipelineStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Workspace(BaseModel):
    id: str
    name: str
    slug: str
    owner_id: str
    status: WorkspaceStatus
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class User(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: str = None
    role: UserRole
    workspace_ids: list[str] = Field(default_factory=list)


class Repository(BaseModel):
    id: str
    workspace_id: str
    name: str
    full_name: str
    provider: RepoProvider
    url: str
    default_branch: str = "main"
    is_private: bool = True
    last_synced_at: datetime = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class FileNode(BaseModel):
    path: str
    name: str
    type: FileNodeType
    size: int = 0
    children: list[FileNode] = None
    git_status: str = None


class CodeChange(BaseModel):
    file_path: str
    change_type: ChangeType
    line_start: int
    line_end: int
    old_content: str
    new_content: str
    hunk_header: str = None


class Commit(BaseModel):
    sha: str
    message: str
    author_name: str
    author_email: str
    authored_at: datetime
    committer_name: str
    committer_email: str
    committed_at: datetime
    parent_shas: list[str]
    stats: dict[str, int] = None


class Branch(BaseModel):
    name: str
    sha: str
    is_default: bool = False
    is_protected: bool = False
    ahead_count: int = 0
    behind_count: int = 0
    last_commit_at: datetime = None


class TerminalSession(BaseModel):
    id: str
    workspace_id: str
    repository_id: str = None
    command: str
    cwd: str
    env: dict[str, str] = Field(default_factory=dict)
    pid: int = None
    status: str
    output: list[str] = Field(default_factory=list)
    exit_code: int = None
    created_at: datetime
    finished_at: datetime = None


class TestResult(BaseModel):
    id: str
    name: str
    status: str
    duration_ms: float
    suite: str
    file_path: str
    line_number: int = None
    error_message: str = None
    stack_trace: str = None


class HealthFinding(BaseModel):
    id: str
    severity: str
    category: str
    title: str
    description: str
    file_path: str = None
    line_start: int = None
    line_end: int = None
    suggested_fix: str = None
    auto_fixable: bool = False


class RepoGraphNode(BaseModel):
    id: str
    type: str
    name: str
    file_path: str
    line_start: int
    line_end: int
    properties: dict[str, Any] = Field(default_factory=dict)


class RepoGraphEdge(BaseModel):
    source: str
    target: str
    type: str
    properties: dict[str, Any] = Field(default_factory=dict)


class RepoGraph(BaseModel):
    repository_id: str
    nodes: list[RepoGraphNode]
    edges: list[RepoGraphEdge]
    generated_at: datetime
