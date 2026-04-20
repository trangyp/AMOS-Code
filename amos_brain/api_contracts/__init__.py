"""AMOS API Contracts - Shared Pydantic models for hub-and-spoke architecture.

This package defines the API contracts used between:
- AMOS-Consulting (API hub) - imports and validates requests/responses
- AMOS-Claws (agent client) - imports to structure API calls
- Mailinhconect (product client) - imports to structure API calls
- AMOS-Invest (investor client) - imports to structure API calls

Usage:
    from amos_brain.api_contracts import ChatRequest, ChatResponse
    from amos_brain.api_contracts import RepoScanRequest, RepoScanResult
    from amos_brain.api_contracts import ModelInfo, UserSession
"""

from amos_brain.api_contracts.base import BaseAMOSModel, TimestampsMixin
from amos_brain.api_contracts.brain import (
    BrainRunRequest,
    BrainRunResponse,
    BranchResult,
    MorphExecution,
    StateGraphInput,
)
from amos_brain.api_contracts.chat import (
    ChatContext,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ConversationSummary,
)
from amos_brain.api_contracts.errors import (
    ApiError,
    AuthenticationError,
    ErrorCode,
    NotFoundError,
    ValidationError,
)
from amos_brain.api_contracts.models import (
    ModelCapabilities,
    ModelInfo,
    ModelProvider,
    ModelRequest,
    ModelResponse,
)
from amos_brain.api_contracts.repo import (
    FileChange,
    IssueSeverity,
    RepoFixRequest,
    RepoFixResult,
    RepoScanRequest,
    RepoScanResult,
    ScanIssue,
)
from amos_brain.api_contracts.session import (
    SessionContext,
    User,
    UserSession,
    Workspace,
)
from amos_brain.api_contracts.workflow import (
    TaskResult,
    WorkflowRunRequest,
    WorkflowRunResponse,
    WorkflowStatus,
)

__all__ = [
    # Base
    "BaseAMOSModel",
    "TimestampsMixin",
    # Chat
    "ChatRequest",
    "ChatResponse",
    "ChatMessage",
    "ChatContext",
    "ConversationSummary",
    # Repo
    "RepoScanRequest",
    "RepoScanResult",
    "RepoFixRequest",
    "RepoFixResult",
    "FileChange",
    "ScanIssue",
    "IssueSeverity",
    # Models
    "ModelInfo",
    "ModelCapabilities",
    "ModelProvider",
    "ModelRequest",
    "ModelResponse",
    # Session
    "UserSession",
    "SessionContext",
    "Workspace",
    "User",
    # Errors
    "ApiError",
    "ErrorCode",
    "ValidationError",
    "AuthenticationError",
    "NotFoundError",
    # Brain
    "BrainRunRequest",
    "BrainRunResponse",
    "StateGraphInput",
    "BranchResult",
    "MorphExecution",
    # Workflow
    "WorkflowRunRequest",
    "WorkflowRunResponse",
    "WorkflowStatus",
    "TaskResult",
]
