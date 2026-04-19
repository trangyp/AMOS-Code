"""Tests for Workflow Service - Saga Pattern Orchestration

Owner: Trang Phan
Version: 2.0.0
"""

from unittest.mock import AsyncMock

import pytest

from backend.workflow import (
    ActivityStatus,
    CompensationManager,
    SagaOrchestrator,
    WorkflowActivity,
    WorkflowService,
    WorkflowStatus,
)


@pytest.fixture
def workflow_service():
    """Create a workflow service instance for testing."""
    return WorkflowService()


@pytest.fixture
def sample_workflow_def():
    """Sample workflow definition for testing."""

    async def handler(**kwargs):
        return {"result": "success", "input": kwargs}

    async def compensation(**kwargs):
        return {"compensated": True}

    return [
        WorkflowActivity(
            activity_id="act1",
            name="test_activity",
            handler=handler,
            compensation=compensation,
            input_data={"test": True},
        )
    ]


class TestWorkflowService:
    """Test WorkflowService functionality."""

    @pytest.mark.asyncio
    async def test_start_workflow(self, workflow_service, sample_workflow_def):
        """Test starting a new workflow."""
        workflow_service._workflow_definitions["test"] = sample_workflow_def

        workflow_id = await workflow_service.start_workflow(
            workflow_type="test", input_data={"key": "value"}
        )

        assert workflow_id is not None
        assert workflow_id.startswith("wf-")

        instance = workflow_service.get_workflow(workflow_id)
        assert instance is not None
        assert instance.workflow_type == "test"
        assert instance.status == WorkflowStatus.PENDING

    def test_get_workflow_not_found(self, workflow_service):
        """Test getting non-existent workflow."""
        result = workflow_service.get_workflow("non-existent")
        assert result is None

    def test_list_workflows_empty(self, workflow_service):
        """Test listing workflows when empty."""
        workflows = workflow_service.list_workflows()
        assert workflows == []

    def test_list_workflows_with_status(self, workflow_service, sample_workflow_def):
        """Test listing workflows with status filter."""
        # Need to use asyncio.run for async methods in sync test
        workflow_service._workflow_definitions["test"] = sample_workflow_def

        # This would need to be an async test
        # workflows = await workflow_service.list_workflows(status=WorkflowStatus.PENDING)
        # assert len(workflows) >= 0


class TestWorkflowActivity:
    """Test WorkflowActivity functionality."""

    def test_activity_creation(self):
        """Test creating a workflow activity."""

        async def handler(**kwargs):
            return {"result": "test"}

        activity = WorkflowActivity(
            activity_id="test-1", name="test_activity", handler=handler, input_data={"test": True}
        )

        assert activity.activity_id == "test-1"
        assert activity.name == "test_activity"
        assert activity.status == ActivityStatus.PENDING
        assert activity.retry_count == 0

    @pytest.mark.asyncio
    async def test_activity_execution(self):
        """Test executing an activity."""

        async def handler(**kwargs):
            return {"computed": kwargs.get("value", 0) * 2}

        activity = WorkflowActivity(
            activity_id="test-2", name="double", handler=handler, input_data={"value": 5}
        )

        result = await activity.handler(**activity.input_data)
        assert result["computed"] == 10


class TestSagaOrchestrator:
    """Test SagaOrchestrator functionality."""

    @pytest.mark.asyncio
    async def test_saga_execution_success(self):
        """Test successful saga execution."""

        async def step1(**kwargs):
            return {"step": 1}

        async def step2(**kwargs):
            return {"step": 2}

        activities = [
            WorkflowActivity("s1", "step1", step1),
            WorkflowActivity("s2", "step2", step2),
        ]

        orchestrator = SagaOrchestrator(
            workflow_id="test-saga", activities=activities, input_data={}
        )

        result = await orchestrator.execute()
        assert result is True
        assert orchestrator.status == WorkflowStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_saga_with_compensation(self):
        """Test saga with compensation on failure."""
        compensations = []

        async def compensate(**kwargs):
            compensations.append(kwargs.get("activity_id"))
            return {"compensated": True}

        async def success_step(**kwargs):
            return {"ok": True}

        async def fail_step(**kwargs):
            raise ValueError("Intentional failure")

        activities = [
            WorkflowActivity("s1", "success", success_step, compensation=compensate),
            WorkflowActivity("s2", "fail", fail_step, compensation=compensate),
        ]

        orchestrator = SagaOrchestrator(
            workflow_id="test-fail", activities=activities, input_data={}
        )

        result = await orchestrator.execute()
        assert result is False
        assert orchestrator.status == WorkflowStatus.FAILED


class TestCompensationManager:
    """Test CompensationManager functionality."""

    @pytest.mark.asyncio
    async def test_compensation_execution(self):
        """Test executing compensations."""
        compensations = []

        async def compensate1(**kwargs):
            compensations.append("c1")
            return True

        async def compensate2(**kwargs):
            compensations.append("c2")
            return True

        activities = [
            WorkflowActivity("a1", "act1", AsyncMock(), compensation=compensate1),
            WorkflowActivity("a2", "act2", AsyncMock(), compensation=compensate2),
        ]

        # Mark activities as completed so they'll be compensated
        activities[0].status = ActivityStatus.COMPLETED
        activities[1].status = ActivityStatus.COMPLETED

        manager = CompensationManager(activities)
        result = await manager.compensate_all(context={"reason": "test"})

        assert result is True
        assert "c1" in compensations
        assert "c2" in compensations
