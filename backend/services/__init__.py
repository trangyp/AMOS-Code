"""Backend Service Layer Integration.

This module provides example implementations of how to integrate
the AMOS service layer into FastAPI endpoints.
"""

from backend.services.agent_service import AgentService
from backend.services.user_service import UserService

__all__ = ["UserService", "AgentService"]
