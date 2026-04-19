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
from amos_universe.contracts.pydantic.chat import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    ChatContext,
    ConversationSummary,
)
from amos_universe.contracts.pydantic.repo import (
    RepoScanRequest,
    RepoScanResult,
    RepoFixRequest,
    RepoFixResult,
    FileChange,
    ScanIssue,
    IssueSeverity,
)
from amos_universe.contracts.pydantic.models import (
    ModelInfo,
    ModelCapabilities,
    ModelProvider,
    ModelRequest,
    ModelResponse,
)
from amos_universe.contracts.pydantic.session import (
    UserSession,
    SessionContext,
    Workspace,
    User,
)
from amos_universe.contracts.pydantic.errors import (
    ApiError,
    ErrorCode,
    ValidationError,
    AuthenticationError,
    NotFoundError,
)
from amos_universe.contracts.pydantic.brain import (
    BrainRunRequest,
    BrainRunResponse,
    StateGraphInput,
    BranchResult,
    MorphExecution,
)
from amos_universe.contracts.pydantic.workflow import (
    WorkflowRunRequest,
    WorkflowRunResponse,
    WorkflowStatus,
    TaskResult,
)
from amos_universe.contracts.pydantic.events import (
    BaseEvent,
    EventType,
    EventMetadata,
    ClawsAgentRequestedEvent,
    ClawsAgentCompletedEvent,
    RepoScanCompletedEvent,
    RepoFixCompletedEvent,
    ModelRunCompletedEvent,
    WorkflowStartedEvent,
    WorkflowCompletedEvent,
    UniverseSchemaUpdatedEvent,
    UniverseContractPublishedEvent,
    UniverseOntologyChangedEvent,
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
