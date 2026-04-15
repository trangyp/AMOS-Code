"""Compatibility module for context imports.

Provides execution context management.
"""

from typing import Any


class Context:
    """Execution context for tasks."""

    def __init__(self, **kwargs: Any):
        self.data = kwargs
        self.session_id = kwargs.get("session_id", "default")

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from context."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set value in context."""
        self.data[key] = value


class ContextManager:
    """Manages execution contexts."""

    def __init__(self):
        self._contexts: dict[str, Context] = {}

    def create_context(self, session_id: str, **kwargs: Any) -> Context:
        """Create new context."""
        ctx = Context(session_id=session_id, **kwargs)
        self._contexts[session_id] = ctx
        return ctx

    def get_context(self, session_id: str) -> Context | None:
        """Get context by session ID."""
        return self._contexts.get(session_id)


__all__ = ["Context", "ContextManager"]
