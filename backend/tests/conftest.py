"""AMOS Test Configuration and Fixtures.

Provides shared test fixtures for the complete test suite.

Creator: Trang Phan
Version: 3.0.0
"""

import os

# Import the FastAPI app
import sys

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_integrated import app


# Create test database
@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create test database session."""
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="function")
def client(test_session):
    """Create test client with database override."""

    def override_get_session():
        return test_session

    # Override the dependency

    # Mock the database dependency
    app.dependency_overrides = {}

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides after test
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sample_agent_task():
    """Create sample agent task data."""
    return {
        "name": "Test Task",
        "description": "A test agent task",
        "agent_type": "general",
        "priority": "normal",
        "payload": '{"key": "value"}',
    }


@pytest.fixture(scope="function")
def sample_memory_entry():
    """Create sample memory entry data."""
    return {
        "system": "cognitive",
        "content": "Test memory content",
        "importance": "high",
        "tags": '["test", "memory"]',
    }


@pytest.fixture(scope="function")
def sample_checkpoint():
    """Create sample checkpoint data."""
    return {
        "label": "Test Checkpoint",
        "state_hash": "abc123",
        "files_count": 42,
        "metadata": '{"version": "3.0.0"}',
    }


@pytest.fixture(scope="function")
def chat_request_data():
    """Create sample chat request data."""
    return {
        "messages": [{"role": "user", "content": "Hello AMOS!"}],
        "model": "mock-gpt",
        "provider": "mock",
        "temperature": 0.7,
        "max_tokens": 100,
    }


@pytest.fixture(scope="session")
def base_url():
    """Base URL for API."""
    return "/api/v1"
