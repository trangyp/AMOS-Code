"""Canonical event definitions for the AMOS 6-repo ecosystem.

This module defines all event types that flow through the AMOS event bus,
providing type-safe, versioned, and well-documented event contracts.

Event Flow:
    Publisher → Redis Stream → Subscribers
    
Example:
    ```python
    from amos_universe.contracts.pydantic.events import (
        EventType, EventMetadata, ClawsAgentRequestedEvent, ClawsAgentPayload
    )
    
    event = ClawsAgentRequestedEvent(
        metadata=EventMetadata(
            event_id="evt-123",
            source="amos-claws",
            tenant_id="ws-456"
        ),
        payload=ClawsAgentPayload(
            task_id="task-789",
            agent_type="repo_scan"
        )
    )
    
    # Publish to event bus
    await event_bus.publish(event)
    
    # Subscribe to events
    async def on_agent_requested(event: ClawsAgentRequestedEvent):
        print(f"Agent requested: {event.payload.agent_type}")
    
    event_bus.subscribe(EventType.CLAWS_AGENT_REQUESTED, on_agent_requested)
    ```
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import Field

from amos_universe.contracts.pydantic.base import BaseAMOSModel


class EventType(str, Enum):
    """Canonical event types for the AMOS 6-repo ecosystem.
    
    Event names follow the pattern: `{domain}.{action}.{status}`
    
    Domains:
        - claws: AMOS-Claws operator actions
        - mailinh: Mailinhconect product actions
        - invest: AMOS-Invest investor actions
        - repo: Repository scanning/fixing
        - model: LLM model operations
        - workflow: Workflow execution
        - universe: AMOS-UNIVERSE schema/ontology changes
        - system: System-level events
    """
    
    # Layer 09 - Social/Agent (AMOS-Claws)
    CLAWS_SESSION_STARTED = "claws.session.started"
    CLAWS_SESSION_ENDED = "claws.session.ended"
    CLAWS_AGENT_REQUESTED = "claws.agent.requested"
    CLAWS_AGENT_COMPLETED = "claws.agent.completed"
    CLAWS_AGENT_FAILED = "claws.agent.failed"
    CLAWS_TOOL_INVOKED = "claws.tool.invoked"
    
    # Layer 14 - Interfaces (Mailinhconect)
    MAILINH_LEAD_CREATED = "mailinh.lead.created"
    MAILINH_CONTACT_SUBMITTED = "mailinh.contact.submitted"
    MAILINH_USER_REGISTERED = "mailinh.user.registered"
    MAILINH_FORM_SUBMITTED = "mailinh.form.submitted"
    
    # Layer 14 - Interfaces (AMOS-Invest)
    INVEST_REPORT_REQUESTED = "invest.report.requested"
    INVEST_REPORT_COMPLETED = "invest.report.completed"
    INVEST_SIGNAL_GENERATED = "invest.signal.generated"
    INVEST_ANALYTICS_VIEWED = "invest.analytics.viewed"
    
    # Layer 01 - Brain (Repository operations)
    REPO_SCAN_STARTED = "repo.scan.started"
    REPO_SCAN_COMPLETED = "repo.scan.completed"
    REPO_SCAN_FAILED = "repo.scan.failed"
    REPO_FIX_STARTED = "repo.fix.started"
    REPO_FIX_COMPLETED = "repo.fix.completed"
    REPO_FIX_FAILED = "repo.fix.failed"
    REPO_PR_CREATED = "repo.pr.created"
    
    # Layer 10 - Memory (Model operations)
    MODEL_RUN_STARTED = "model.run.started"
    MODEL_RUN_COMPLETED = "model.run.completed"
    MODEL_RUN_FAILED = "model.run.failed"
    MODEL_LOADED = "model.loaded"
    MODEL_UNLOADED = "model.unloaded"
    MODEL_HEALTH_CHECK = "model.health_check"
    
    # Layer 06 - Muscle (Workflow operations)
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    WORKFLOW_CANCELLED = "workflow.cancelled"
    WORKFLOW_STEP_STARTED = "workflow.step.started"
    WORKFLOW_STEP_COMPLETED = "workflow.step.completed"
    WORKFLOW_STEP_FAILED = "workflow.step.failed"
    
    # Layer 11 - Canon (AMOS-UNIVERSE events) ⭐
    UNIVERSE_SCHEMA_UPDATED = "universe.schema.updated"
    UNIVERSE_SCHEMA_DEPRECATED = "universe.schema.deprecated"
    UNIVERSE_CONTRACT_PUBLISHED = "universe.contract.published"
    UNIVERSE_ONTOLOGY_CHANGED = "universe.ontology.changed"
    UNIVERSE_ADR_PUBLISHED = "universe.adr.published"
    
    # Layer 00 - Root (System events)
    SYSTEM_ALERT = "system.alert"
    SYSTEM_HEALTH_CHANGED = "system.health.changed"
    SYSTEM_MAINTENANCE_SCHEDULED = "system.maintenance.scheduled"
    SYSTEM_MAINTENANCE_STARTED = "system.maintenance.started"
    SYSTEM_MAINTENANCE_COMPLETED = "system.maintenance.completed"


class EventPriority(str, Enum):
    """Event priority levels for processing."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class EventMetadata(BaseAMOSModel):
    """Metadata attached to all events.
    
    Provides tracing, routing, and audit information for every event.
    
    Fields:
        event_id: Unique UUID for the event
        timestamp: When the event occurred (UTC)
        source: Which repository published the event
        version: Schema version of the event
        trace_id: Distributed tracing correlation ID
        tenant_id: Multi-tenant workspace ID (if applicable)
        priority: Processing priority
    """
    
    event_id: str = Field(
        ...,
        description="Unique event identifier (UUID)",
        examples=["evt-550e8400-e29b-41d4-a716-446655440000"]
    )
    
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Event timestamp (ISO 8601 UTC)",
        json_schema_extra={"format": "date-time"}
    )
    
    source: str = Field(
        ...,
        description="Source repository name",
        examples=["amos-claws", "amos-consulting", "mailinhconect"]
    )
    
    version: str = Field(
        default="1.0",
        description="Event schema version",
        pattern=r"^\d+\.\d+$",
        examples=["1.0", "1.1", "2.0"]
    )
    
    trace_id: str | None = Field(
        default=None,
        description="Distributed trace ID for request correlation"
    )
    
    tenant_id: str | None = Field(
        default=None,
        description="Multi-tenant workspace ID (if applicable)"
    )
    
    priority: EventPriority = Field(
        default=EventPriority.NORMAL,
        description="Event processing priority"
    )


class BaseEvent(BaseAMOSModel):
    """Base class for all AMOS events.
    
    All specific event types inherit from this class and override
    the event_type and payload fields with concrete types.
    
    Attributes:
        event_type: The canonical event type (from EventType enum)
        metadata: Event metadata (id, timestamp, source, etc.)
        payload: Event-specific data (varies by event type)
    """
    
    event_type: EventType = Field(
        ...,
        description="Canonical event type"
    )
    
    metadata: EventMetadata = Field(
        ...,
        description="Event metadata (tracing, routing, audit)"
    )
    
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific payload data"
    )
    
    def get_routing_key(self) -> str:
        """Get the routing key for this event type.
        
        Returns:
            The event type value suitable for message routing.
        """
        return self.event_type.value
    
    def get_topic_pattern(self) -> str:
        """Get the wildcard topic pattern for this event.
        
        Returns:
            Pattern like 'claws.session.*' for subscription matching.
        """
        parts = self.event_type.value.split(".")
        return f"{parts[0]}.{parts[1]}.*"


# =============================================================================
# Event Payloads
# =============================================================================

class ClawsSessionPayload(BaseAMOSModel):
    """Payload for claws.session.* events."""
    
    session_id: str
    user_id: str | None = None
    workspace_id: str | None = None
    client_info: dict[str, Any] | None = None
    ip_address: str | None = None
    user_agent: str | None = None


class ClawsAgentPayload(BaseAMOSModel):
    """Payload for claws.agent.* events."""
    
    task_id: str
    agent_type: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    target_repo: str | None = None
    requested_by: str | None = None


class MailinhLeadPayload(BaseAMOSModel):
    """Payload for mailinh.lead.* events."""
    
    lead_id: str
    source: str = Field(description="Lead source: 'website', 'api', 'import'")
    email: str | None = None
    phone: str | None = None
    name: str | None = None
    company: str | None = None
    form_data: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None


class RepoScanPayload(BaseAMOSModel):
    """Payload for repo.scan.* events."""
    
    scan_id: str
    repo_url: str
    repo_name: str | None = None
    branch: str = "main"
    scan_types: list[str] = Field(default_factory=list)
    commit_sha: str | None = None
    findings_count: int = 0
    findings_by_severity: dict[str, int] = Field(default_factory=dict)
    duration_seconds: float | None = None
    report_url: str | None = None
    triggered_by: str | None = None


class RepoFixPayload(BaseAMOSModel):
    """Payload for repo.fix.* events."""
    
    fix_id: str
    scan_id: str
    repo_url: str
    files_changed: list[str] = Field(default_factory=list)
    pr_url: str | None = None
    pr_number: int | None = None
    commit_sha: str | None = None
    fixes_applied: int = 0
    fixes_failed: int = 0
    applied_by: str | None = None


class ModelRunPayload(BaseAMOSModel):
    """Payload for model.run.* events."""
    
    run_id: str
    model_id: str
    provider: str = Field(description="Provider: 'ollama', 'lmstudio', 'vllm'")
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    duration_ms: float | None = None
    input_length: int | None = None
    output_length: int | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    requested_by: str | None = None


class WorkflowPayload(BaseAMOSModel):
    """Payload for workflow.* events."""
    
    workflow_id: str
    workflow_name: str | None = None
    execution_id: str
    step_id: str | None = None
    step_name: str | None = None
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: dict[str, Any] = Field(default_factory=dict)
    error_message: str | None = None
    duration_ms: float | None = None
    triggered_by: str | None = None


class UniverseSchemaPayload(BaseAMOSModel):
    """Payload for universe.schema.* events."""
    
    schema_name: str
    schema_version: str
    change_type: Literal["created", "updated", "deprecated", "removed"]
    affected_repos: list[str] = Field(default_factory=list)
    breaking_changes: bool = False
    migration_guide_url: str | None = None
    published_by: str | None = None


class SystemAlertPayload(BaseAMOSModel):
    """Payload for system.alert events."""
    
    severity: Literal["info", "warning", "critical", "emergency"]
    component: str = Field(description="Component: 'api', 'database', 'redis'")
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    remediation: str | None = None
    acknowledged: bool = False
    acknowledged_by: str | None = None


# =============================================================================
# Typed Event Classes
# =============================================================================

class ClawsSessionStartedEvent(BaseEvent):
    """Event: claws.session.started"""
    event_type: EventType = EventType.CLAWS_SESSION_STARTED
    payload: ClawsSessionPayload


class ClawsSessionEndedEvent(BaseEvent):
    """Event: claws.session.ended"""
    event_type: EventType = EventType.CLAWS_SESSION_ENDED
    payload: ClawsSessionPayload


class ClawsAgentRequestedEvent(BaseEvent):
    """Event: claws.agent.requested"""
    event_type: EventType = EventType.CLAWS_AGENT_REQUESTED
    payload: ClawsAgentPayload


class ClawsAgentCompletedEvent(BaseEvent):
    """Event: claws.agent.completed"""
    event_type: EventType = EventType.CLAWS_AGENT_COMPLETED
    payload: ClawsAgentPayload


class MailinhLeadCreatedEvent(BaseEvent):
    """Event: mailinh.lead.created"""
    event_type: EventType = EventType.MAILINH_LEAD_CREATED
    payload: MailinhLeadPayload


class MailinhContactSubmittedEvent(BaseEvent):
    """Event: mailinh.contact.submitted"""
    event_type: EventType = EventType.MAILINH_CONTACT_SUBMITTED
    payload: MailinhLeadPayload


class InvestReportRequestedEvent(BaseEvent):
    """Event: invest.report.requested"""
    event_type: EventType = EventType.INVEST_REPORT_REQUESTED
    payload: dict[str, Any] = Field(default_factory=dict)


class InvestSignalGeneratedEvent(BaseEvent):
    """Event: invest.signal.generated"""
    event_type: EventType = EventType.INVEST_SIGNAL_GENERATED
    payload: dict[str, Any] = Field(default_factory=dict)


class RepoScanCompletedEvent(BaseEvent):
    """Event: repo.scan.completed"""
    event_type: EventType = EventType.REPO_SCAN_COMPLETED
    payload: RepoScanPayload


class RepoScanFailedEvent(BaseEvent):
    """Event: repo.scan.failed"""
    event_type: EventType = EventType.REPO_SCAN_FAILED
    payload: RepoScanPayload


class RepoFixCompletedEvent(BaseEvent):
    """Event: repo.fix.completed"""
    event_type: EventType = EventType.REPO_FIX_COMPLETED
    payload: RepoFixPayload


class RepoFixFailedEvent(BaseEvent):
    """Event: repo.fix.failed"""
    event_type: EventType = EventType.REPO_FIX_FAILED
    payload: RepoFixPayload


class ModelRunCompletedEvent(BaseEvent):
    """Event: model.run.completed"""
    event_type: EventType = EventType.MODEL_RUN_COMPLETED
    payload: ModelRunPayload


class ModelRunFailedEvent(BaseEvent):
    """Event: model.run.failed"""
    event_type: EventType = EventType.MODEL_RUN_FAILED
    payload: ModelRunPayload


class WorkflowStartedEvent(BaseEvent):
    """Event: workflow.started"""
    event_type: EventType = EventType.WORKFLOW_STARTED
    payload: WorkflowPayload


class WorkflowCompletedEvent(BaseEvent):
    """Event: workflow.completed"""
    event_type: EventType = EventType.WORKFLOW_COMPLETED
    payload: WorkflowPayload


class WorkflowFailedEvent(BaseEvent):
    """Event: workflow.failed"""
    event_type: EventType = EventType.WORKFLOW_FAILED
    payload: WorkflowPayload


class UniverseSchemaUpdatedEvent(BaseEvent):
    """Event: universe.schema.updated"""
    event_type: EventType = EventType.UNIVERSE_SCHEMA_UPDATED
    payload: UniverseSchemaPayload


class UniverseContractPublishedEvent(BaseEvent):
    """Event: universe.contract.published"""
    event_type: EventType = EventType.UNIVERSE_CONTRACT_PUBLISHED
    payload: UniverseSchemaPayload


class UniverseOntologyChangedEvent(BaseEvent):
    """Event: universe.ontology.changed"""
    event_type: EventType = EventType.UNIVERSE_ONTOLOGY_CHANGED
    payload: dict[str, Any] = Field(default_factory=dict)


class SystemAlertEvent(BaseEvent):
    """Event: system.alert"""
    event_type: EventType = EventType.SYSTEM_ALERT
    payload: SystemAlertPayload


# =============================================================================
# Event Registry for Deserialization
# =============================================================================

EVENT_REGISTRY: dict[EventType, type[BaseEvent]] = {
    EventType.CLAWS_SESSION_STARTED: ClawsSessionStartedEvent,
    EventType.CLAWS_SESSION_ENDED: ClawsSessionEndedEvent,
    EventType.CLAWS_AGENT_REQUESTED: ClawsAgentRequestedEvent,
    EventType.CLAWS_AGENT_COMPLETED: ClawsAgentCompletedEvent,
    EventType.MAILINH_LEAD_CREATED: MailinhLeadCreatedEvent,
    EventType.MAILINH_CONTACT_SUBMITTED: MailinhContactSubmittedEvent,
    EventType.INVEST_REPORT_REQUESTED: InvestReportRequestedEvent,
    EventType.INVEST_SIGNAL_GENERATED: InvestSignalGeneratedEvent,
    EventType.REPO_SCAN_COMPLETED: RepoScanCompletedEvent,
    EventType.REPO_SCAN_FAILED: RepoScanFailedEvent,
    EventType.REPO_FIX_COMPLETED: RepoFixCompletedEvent,
    EventType.REPO_FIX_FAILED: RepoFixFailedEvent,
    EventType.MODEL_RUN_COMPLETED: ModelRunCompletedEvent,
    EventType.MODEL_RUN_FAILED: ModelRunFailedEvent,
    EventType.WORKFLOW_STARTED: WorkflowStartedEvent,
    EventType.WORKFLOW_COMPLETED: WorkflowCompletedEvent,
    EventType.WORKFLOW_FAILED: WorkflowFailedEvent,
    EventType.UNIVERSE_SCHEMA_UPDATED: UniverseSchemaUpdatedEvent,
    EventType.UNIVERSE_CONTRACT_PUBLISHED: UniverseContractPublishedEvent,
    EventType.UNIVERSE_ONTOLOGY_CHANGED: UniverseOntologyChangedEvent,
    EventType.SYSTEM_ALERT: SystemAlertEvent,
}


def deserialize_event(data: dict[str, Any]) -> BaseEvent:
    """Deserialize an event from dictionary data.
    
    Uses the EVENT_REGISTRY to determine the correct event class
    based on the event_type field.
    
    Args:
        data: Dictionary containing event data with 'event_type' key.
        
    Returns:
        Concrete event instance based on the event type.
        
    Raises:
        ValueError: If event_type is missing or unknown.
        
    Example:
        ```python
        data = {
            "event_type": "claws.agent.requested",
            "metadata": {...},
            "payload": {...}
        }
        event = deserialize_event(data)
        assert isinstance(event, ClawsAgentRequestedEvent)
        ```
    """
    event_type_str = data.get("event_type")
    if not event_type_str:
        raise ValueError("Missing 'event_type' field in event data")
    
    try:
        event_type = EventType(event_type_str)
    except ValueError:
        raise ValueError(f"Unknown event type: {event_type_str}")
    
    event_class = EVENT_REGISTRY.get(event_type, BaseEvent)
    return event_class.model_validate(data)


def get_event_class(event_type: EventType) -> type[BaseEvent]:
    """Get the event class for a given event type.
    
    Args:
        event_type: The event type enum value.
        
    Returns:
        The concrete event class for the type.
    """
    return EVENT_REGISTRY.get(event_type, BaseEvent)
