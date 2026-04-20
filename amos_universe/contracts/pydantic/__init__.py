"""AMOS API Contracts - Shared Pydantic models for hub-and-spoke architecture.

This package defines the API contracts used between:
- AMOS-Consulting (API hub) - imports and validates requests/responses
- AMOS-Claws (agent client) - imports to structure API calls
- Mailinhconect (product client) - imports to structure API calls
- AMOS-Invest (investor client) - imports to structure API calls

Usage:
    from amos_universe.contracts.pydantic import ChatRequest, ChatResponse
    from amos_universe.contracts.pydantic import RepoScanRequest, RepoScanResult
    from amos_universe.contracts.pydantic import ModelInfo, UserSession
"""

from amos_universe.contracts.pydantic.base import BaseAMOSModel, TimestampsMixin
from amos_universe.contracts.pydantic.brain import (
    BrainRunRequest,
    BrainRunResponse,
    BranchResult,
    MorphExecution,
    StateGraphInput,
)
from amos_universe.contracts.pydantic.chat import (
    ChatContext,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ConversationSummary,
)
from amos_universe.contracts.pydantic.errors import (
    ApiError,
    AuthenticationError,
    ErrorCode,
    NotFoundError,
    ValidationError,
)
from amos_universe.contracts.pydantic.events import (
    BaseEvent,
    ClawsAgentCompletedEvent,
    ClawsAgentRequestedEvent,
    EventMetadata,
    EventType,
    ModelRunCompletedEvent,
    RepoFixCompletedEvent,
    RepoScanCompletedEvent,
    UniverseContractPublishedEvent,
    UniverseOntologyChangedEvent,
    UniverseSchemaUpdatedEvent,
    WorkflowCompletedEvent,
    WorkflowStartedEvent,
)
from amos_universe.contracts.pydantic.models import (
    ModelCapabilities,
    ModelInfo,
    ModelProvider,
    ModelRequest,
    ModelResponse,
)
from amos_universe.contracts.pydantic.repo import (
    FileChange,
    IssueSeverity,
    RepoFixRequest,
    RepoFixResult,
    RepoScanRequest,
    RepoScanResult,
    ScanIssue,
)
from amos_universe.contracts.pydantic.session import (
    SessionContext,
    User,
    UserSession,
    Workspace,
)
from amos_universe.contracts.pydantic.workflow import (
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
    # Events
    "BaseEvent",
    "EventType",
    "EventMetadata",
    "ClawsAgentRequestedEvent",
    "ClawsAgentCompletedEvent",
    "RepoScanCompletedEvent",
    "RepoFixCompletedEvent",
    "ModelRunCompletedEvent",
    "WorkflowStartedEvent",
    "WorkflowCompletedEvent",
    "UniverseSchemaUpdatedEvent",
    "UniverseContractPublishedEvent",
    "UniverseOntologyChangedEvent",
]
