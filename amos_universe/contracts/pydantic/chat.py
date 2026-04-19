"""Chat API contracts for AMOS conversational interfaces."""

from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum
from typing import Any, Optional

from pydantic import Field

from amos_universe.contracts.pydantic.base import BaseAMOSModel


class MessageRole(str, Enum):
    """Role of a message sender in the conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ChatMessage(BaseAMOSModel):
    """A single message in a chat conversation."""
    
    role: MessageRole = Field(..., description="Role of the message sender")
    content: str = Field(..., min_length=1, description="Message content")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the message was sent"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional message metadata (e.g., tool calls)"
    )


class ChatContext(BaseAMOSModel):
    """Context information for a chat session."""
    
    workspace_id: Optional[str] = Field(
        None,
        description="Workspace/tenant identifier"
    )
    conversation_id: Optional[str] = Field(
        None,
        description="Unique conversation identifier"
    )
    session_id: str = Field(
        ...,
        description="Session identifier for continuity"
    )
    user_id: Optional[str] = Field(
        None,
        description="Authenticated user identifier"
    )
    preferences: dict[str, Any] = Field(
        default_factory=dict,
        description="User preferences for this chat"
    )


class ChatRequest(BaseAMOSModel):
    """Request model for chat endpoint.
    
    Example:
        {
            "message": "Explain the softmax function",
            "context": {
                "session_id": "sess_123",
                "workspace_id": "ws_456"
            },
            "history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi! How can I help?"}
            ]
        }
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=100000,
        description="User message to process"
    )
    context: ChatContext = Field(
        ...,
        description="Session and workspace context"
    )
    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=100,
        description="Previous messages in the conversation"
    )
    model: Optional[str] = Field(
        None,
        description="Specific model to use (auto-selected if not provided)"
    )
    temperature: float = Field(
        0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature"
    )
    max_tokens: Optional[int] = Field(
        None,
        ge=1,
        le=32000,
        description="Maximum tokens in response"
    )
    stream: bool = Field(
        False,
        description="Whether to stream the response"
    )
    tools: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Available tools for the assistant"
    )


class ChatResponse(BaseAMOSModel):
    """Response model for chat endpoint.
    
    Example:
        {
            "message": "The softmax function...",
            "conversation_id": "conv_789",
            "usage": {
                "prompt_tokens": 150,
                "completion_tokens": 200,
                "total_tokens": 350
            },
            "model": "llama3.1:8b"
        }
    """
    
    message: str = Field(..., description="Assistant response content")
    conversation_id: str = Field(..., description="Conversation identifier")
    session_id: str = Field(..., description="Session identifier")
    usage: dict[str, int] = Field(
        default_factory=dict,
        description="Token usage statistics"
    )
    model: str = Field(..., description="Model used for the response")
    finish_reason: Optional[str] = Field(
        None,
        description="Why the generation stopped (stop/length/tool_calls)"
    )
    tool_calls: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Tool calls requested by the model"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional response metadata"
    )


class ConversationSummary(BaseAMOSModel):
    """Summary of a conversation for listing."""
    
    conversation_id: str = Field(..., description="Unique conversation ID")
    title: Optional[str] = Field(None, description="Generated or user-set title")
    message_count: int = Field(..., ge=0, description="Number of messages")
    last_message_at: Optional[datetime] = Field(None, description="Last activity timestamp")
    created_at: Optional[datetime] = Field(None, description="When conversation started")
    workspace_id: Optional[str] = Field(None, description="Workspace identifier")
