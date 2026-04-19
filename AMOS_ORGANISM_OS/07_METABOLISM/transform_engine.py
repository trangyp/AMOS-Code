"""Transform Engine — Data transformation operations

Handles data transformations, conversions, and mappings
between different formats and structures.
"""

import json
import uuid
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class TransformContext:
    """Context for transform operations."""

    source_format: str = ""
    target_format: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Transform:
    """A data transformation definition."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    transform_type: str = ""  # map, filter, aggregate, convert
    input_schema: str = ""
    output_schema: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TransformEngine:
    """Manages and executes data transformations.

    Provides a registry of transforms and handles
    conversion between different data formats.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.transforms: Dict[str, Transform] = {}
        self.transformers: Dict[str, Callable] = {}

        self._load_transforms()
        self._register_default_transformers()

    def _load_transforms(self):
        """Load saved transforms."""
        transforms_file = self.data_dir / "transforms.json"
        if transforms_file.exists():
            try:
                data = json.loads(transforms_file.read_text())
                for t_data in data.get("transforms", []):
                    transform = Transform(
                        id=t_data["id"],
                        name=t_data["name"],
                        transform_type=t_data["transform_type"],
                        input_schema=t_data.get("input_schema", ""),
                        output_schema=t_data.get("output_schema", ""),
                        config=t_data.get("config", {}),
                        created_at=t_data["created_at"],
                    )
                    self.transforms[transform.id] = transform
            except Exception as e:
                print(f"[TRANSFORM] Error loading transforms: {e}")

    def save(self):
        """Save transforms to disk."""
        transforms_file = self.data_dir / "transforms.json"
        data = {
            "saved_at": datetime.now(UTC).isoformat(),
            "transforms": [t.to_dict() for t in self.transforms.values()],
        }
        transforms_file.write_text(json.dumps(data, indent=2))

    def _register_default_transformers(self):
        """Register default transformation functions."""
        self.transformers["json_to_dict"] = self._json_to_dict
        self.transformers["dict_to_json"] = self._dict_to_json
        self.transformers["extract_field"] = self._extract_field
        self.transformers["add_timestamp"] = self._add_timestamp
        self.transformers["flatten"] = self._flatten

    def register_transformer(self, name: str, func: Callable):
        """Register a custom transformer."""
        self.transformers[name] = func

    def create_transform(
        self,
        name: str,
        transform_type: str,
        input_schema: str = "",
        output_schema: str = "",
        config: dict = None,
    ) -> Transform:
        """Create a new transform definition."""
        transform = Transform(
            name=name,
            transform_type=transform_type,
            input_schema=input_schema,
            output_schema=output_schema,
            config=config or {},
        )
        self.transforms[transform.id] = transform
        self.save()
        return transform

    def execute_transform(
        self,
        transform_id: str,
        data: Any,
        context: Optional[TransformContext] = None,
    ) -> Dict[str, Any]:
        """Execute a transform on data."""
        transform = self.transforms.get(transform_id)
        if not transform:
            return {"success": False, "error": "Transform not found"}

        context = context or TransformContext()

        # Get the transformer function
        transformer = self.transformers.get(transform.transform_type)
        if not transformer:
            return {
                "success": False,
                "error": f"No transformer for type: {transform.transform_type}",
            }

        try:
            result = transformer(data, transform.config, context)
            return {
                "success": True,
                "result": result,
                "transform_id": transform_id,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "transform_id": transform_id,
            }

    def apply_transforms(
        self,
        data: Any,
        transform_ids: list[str],
        context: Optional[TransformContext] = None,
    ) -> Dict[str, Any]:
        """Apply multiple transforms in sequence."""
        current_data = data
        applied = []
        failed = []

        for transform_id in transform_ids:
            result = self.execute_transform(transform_id, current_data, context)
            if result["success"]:
                current_data = result["result"]
                applied.append(transform_id)
            else:
                failed.append({"id": transform_id, "error": result.get("error")})
                break

        return {
            "success": len(failed) == 0,
            "result": current_data,
            "applied": applied,
            "failed": failed,
        }

    # Default transformer functions
    def _json_to_dict(self, data: Any, config: dict, context: TransformContext) -> Any:
        """Convert JSON string to dict."""
        if isinstance(data, str):
            return json.loads(data)
        return data

    def _dict_to_json(self, data: Any, config: dict, context: TransformContext) -> Any:
        """Convert dict to JSON string."""
        if isinstance(data, dict):
            return json.dumps(data, indent=config.get("indent", 2))
        return data

    def _extract_field(self, data: Any, config: dict, context: TransformContext) -> Any:
        """Extract a field from data."""
        field = config.get("field", "")
        if isinstance(data, dict) and field:
            return data.get(field)
        return data

    def _add_timestamp(self, data: Any, config: dict, context: TransformContext) -> Any:
        """Add timestamp to data."""
        if isinstance(data, dict):
            data["_timestamp"] = datetime.now(UTC).isoformat()
            return data
        return {"data": data, "_timestamp": datetime.now(UTC).isoformat()}

    def _flatten(self, data: Any, config: dict, context: TransformContext) -> Any:
        """Flatten nested structure."""
        if not isinstance(data, dict):
            return data

        separator = config.get("separator", ".")
        result = {}

        def _flatten_recursive(obj, prefix=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{prefix}{separator}{k}" if prefix else k
                    _flatten_recursive(v, new_key)
            else:
                result[prefix] = obj

        _flatten_recursive(data)
        return result

    def list_transforms(self) -> list[dict]:
        """List all transforms."""
        return [
            {
                "id": t.id,
                "name": t.name,
                "type": t.transform_type,
                "input": t.input_schema,
                "output": t.output_schema,
            }
            for t in self.transforms.values()
        ]


# Global instance
_ENGINE: Optional[TransformEngine] = None


def get_transform_engine(data_dir: Optional[Path] = None) -> TransformEngine:
    """Get or create global transform engine."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = TransformEngine(data_dir)
    return _ENGINE


if __name__ == "__main__":
    print("Transform Engine (07_METABOLISM)")
    print("=" * 40)

    engine = get_transform_engine()

    # Create a transform
    transform = engine.create_transform(
        "Extract Content",
        "extract_field",
        config={"field": "content"},
    )
    print(f"\nCreated transform: {transform.name}")

    # Test it
    test_data = {"content": "Hello World", "meta": {"id": 123}}
    result = engine.execute_transform(transform.id, test_data)
    print(f"Result: {result}")

    print("\nRegistered transformers:")
    for name in engine.transformers.keys():
        print(f"  - {name}")
