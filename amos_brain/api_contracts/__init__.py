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
from amos_brain.api_contracts.chat import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    ChatContext,
    ConversationSummary,
)
from amos_brain.api_contracts.repo import (
    RepoScanRequest,
    RepoScanResult,
    RepoFixRequest,
    RepoFixResult,
    FileChange,
    ScanIssue,
    IssueSeverity,
)
from amos_brain.api_contracts.models import (
    ModelInfo,
    ModelCapabilities,
    ModelProvider,
    ModelRequest,
    ModelResponse,
)
from amos_brain.api_contracts.session import (
    UserSession,
    SessionContext,
    Workspace,
    User,
)
from amos_brain.api_contracts.errors import (
    ApiError,
    ErrorCode,
    ValidationError,
    AuthenticationError,
    NotFoundError,
)
from amos_brain.api_contracts.brain import (
    BrainRunRequest,
    BrainRunResponse,
    StateGraphInput,
    BranchResult,
    MorphExecution,
)
from amos_brain.api_contracts.workflow import (
    WorkflowRunRequest,
    WorkflowRunResponse,
    WorkflowStatus,
    TaskResult,
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
