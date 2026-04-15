"""World Model Engine stub for compatibility."""

from typing import Any


class WorldModel:
    """World model representation."""

    def __init__(self):
        self.entities: list[dict[str, Any]] = []
        self.relations: list[dict[str, Any]] = []

    def add_entity(self, entity: dict[str, Any]) -> None:
        """Add entity to model."""
        self.entities.append(entity)

    def query(self, pattern: str) -> list[dict[str, Any]]:
        """Query the world model."""
        return []


class WorldModelEngine:
    """Engine for world model operations."""

    def __init__(self):
        self.models: dict[str, WorldModel] = {}

    def create_model(self, name: str) -> WorldModel:
        """Create new world model."""
        model = WorldModel()
        self.models[name] = model
        return model

    def get_model(self, name: str) -> WorldModel | None:
        """Get world model by name."""
        return self.models.get(name)


__all__ = ["WorldModel", "WorldModelEngine"]
