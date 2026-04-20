from __future__ import annotations

"""Repo Doctor API contracts for repository analysis and fixing."""

from datetime import UTC, datetime, timezone
from enum import Enum
from typing import Any

UTC = UTC

from pydantic import Field

from amos_brain.api_contracts.base import BaseAMOSModel


class IssueSeverity(str, Enum):
    """Severity level for repository issues."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ScanIssue(BaseAMOSModel):
    """A single issue found during repository scanning."""

    issue_id: str = Field(..., description="Unique issue identifier")
    severity: IssueSeverity = Field(..., description="Issue severity level")
    category: str = Field(..., description="Issue category (e.g., 'style', 'security')")
    file_path: str = Field(..., description="Path to the affected file")
    line_number: int = Field(None, ge=1, description="Line number if applicable")
    column: int = Field(None, ge=0, description="Column number if applicable")
    message: str = Field(..., description="Human-readable issue description")
    rule_id: str = Field(None, description="Rule that triggered this issue")
    suggested_fix: str = Field(None, description="Suggested code fix")
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence in this issue (0-1)"
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional issue metadata")


class FileChange(BaseAMOSModel):
    """A single file change for repo fixing."""

    file_path: str = Field(..., description="Path to the file")
    original_content: str = Field(None, description="Original file content (for verification)")
    new_content: str = Field(..., description="New file content")
    change_type: str = Field(default="modify", description="Type of change: create, modify, delete")
    description: str = Field(None, description="Human-readable description of the change")


class RepoScanRequest(BaseAMOSModel):
    """Request to scan a repository for issues.

    Example:
        {
            "repo_path": "/path/to/repo",
            "scan_types": ["style", "security", "typing"],
            "file_patterns": ["*.py"],
            "exclude_patterns": ["*/tests/*", "*/venv/*"]
        }
    """

    repo_path: str = Field(..., description="Absolute or relative path to the repository")
    scan_types: list[str] = Field(
        default_factory=lambda: ["style", "typing", "security"], description="Types of scans to run"
    )
    file_patterns: list[str] = Field(
        default_factory=lambda: ["*.py"], description="File patterns to include"
    )
    exclude_patterns: list[str] = Field(
        default_factory=lambda: ["*/tests/*", "*/venv/*", "*/.git/*"],
        description="Patterns to exclude from scanning",
    )
    max_issues: int = Field(None, ge=1, description="Maximum issues to return (None for all)")
    workspace_id: str = Field(None, description="Workspace context for the scan")


class RepoScanResult(BaseAMOSModel):
    """Result of a repository scan.

    Example:
        {
            "scan_id": "scan_abc123",
            "repo_path": "/path/to/repo",
            "status": "completed",
            "issues": [...],
            "summary": {
                "total_files": 150,
                "files_scanned": 142,
                "issues_found": 23,
                "by_severity": {"error": 5, "warning": 18}
            }
        }
    """

    scan_id: str = Field(..., description="Unique scan identifier")
    repo_path: str = Field(..., description="Repository path that was scanned")
    status: str = Field(..., description="Scan status: pending, running, completed, failed")
    issues: list[ScanIssue] = Field(
        default_factory=list, description="Issues found during the scan"
    )
    summary: dict[str, Any] = Field(default_factory=dict, description="Scan summary statistics")
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="When the scan started"
    )
    completed_at: datetime = Field(None, description="When the scan completed")
    error: str = Field(None, description="Error message if scan failed")
    workspace_id: str = Field(None, description="Workspace context for the scan")


class RepoFixRequest(BaseAMOSModel):
    """Request to apply fixes to a repository.

    Example:
        {
            "scan_id": "scan_abc123",
            "issue_ids": ["issue_1", "issue_2"],
            "auto_apply": false,
            "dry_run": true
        }
    """

    scan_id: str = Field(..., description="Scan ID to base fixes on")
    issue_ids: list[str | None] = Field(None, description="Specific issues to fix (None for all)")
    auto_apply: bool = Field(False, description="Whether to apply fixes automatically")
    dry_run: bool = Field(True, description="If True, only preview changes without applying")
    workspace_id: str = Field(None, description="Workspace context for the fix")


class RepoFixResult(BaseAMOSModel):
    """Result of applying repository fixes.

    Example:
        {
            "fix_id": "fix_xyz789",
            "scan_id": "scan_abc123",
            "status": "preview",
            "changes": [...],
            "applied": false,
            "summary": {
                "files_affected": 5,
                "issues_fixed": 12,
                "issues_remaining": 11
            }
        }
    """

    fix_id: str = Field(..., description="Unique fix identifier")
    scan_id: str = Field(..., description="Source scan ID")
    status: str = Field(..., description="Fix status: preview, applied, partial, failed")
    changes: list[FileChange] = Field(
        default_factory=list, description="File changes to be applied or that were applied"
    )
    applied: bool = Field(..., description="Whether changes were actually applied")
    summary: dict[str, Any] = Field(default_factory=dict, description="Fix summary statistics")
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="When the fix started"
    )
    completed_at: datetime = Field(None, description="When the fix completed")
    error: str = Field(None, description="Error message if fix failed")
    workspace_id: str = Field(None, description="Workspace context for the fix")
