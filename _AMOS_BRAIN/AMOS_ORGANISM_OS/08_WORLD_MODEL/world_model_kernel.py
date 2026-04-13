#!/usr/bin/env python3
"""
AMOS World Model Kernel - 08_WORLD_MODEL Subsystem

Responsible for:
- Environmental representation and state maintenance
- Spatial and temporal reasoning
- Object tracking and relationship mapping
- Context management
- Predictive modeling
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos.world_model")


class ObjectType(Enum):
    """Types of objects in the world model."""
    FILE = auto()
    DIRECTORY = auto()
    PROCESS = auto()
    SUBSYSTEM = auto()
    ENTITY = auto()
    RELATIONSHIP = auto()


class SpatialRelation(Enum):
    """Spatial relationships between objects."""
    CONTAINS = auto()
    ADJACENT = auto()
    NEAR = auto()
    FAR = auto()
    OVERLAPS = auto()


@dataclass
class Position:
    """Spatial position (can be 2D, 3D, or abstract)."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    path: str = ""  # For file system or hierarchical positions


@dataclass
class WorldObject:
    """An object in the world model."""
    object_id: str
    name: str
    object_type: ObjectType
    position: Position = field(default_factory=Position)
    properties: Dict[str, Any] = field(default_factory=dict)
    relationships: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    created_at: str = ""
    last_updated: str = ""
    confidence: float = 1.0  # Confidence in this object's existence
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        if not self.last_updated:
            self.last_updated = self.created_at


@dataclass
class Context:
    """Environmental context snapshot."""
    context_id: str
    timestamp: str
    active_objects: List[str] = field(default_factory=list)
    spatial_relations: List[Tuple[str, str, SpatialRelation]] = field(default_factory=list)
    environmental_state: Dict[str, Any] = field(default_factory=dict)
    inferred_facts: List[str] = field(default_factory=list)


class WorldModelKernel:
    """
    The World Model Kernel maintains a representation of the environment,
    enabling spatial reasoning, object tracking, and predictive modeling.
    """
    
    def __init__(self, organism_root: Path):
        self.root = organism_root
        self.world_path = organism_root / "08_WORLD_MODEL"
        self.memory_path = self.world_path / "memory"
        self.logs_path = self.world_path / "logs"
        
        # Ensure directories
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        # Object registry
        self.objects: Dict[str, WorldObject] = {}
        
        # Context history
        self.contexts: List[Context] = []
        self.max_contexts = 100
        
        # Current context
        self.current_context: Optional[Context] = None
        
        # Spatial index (simplified)
        self.spatial_grid: Dict[str, Set[str]] = defaultdict(set)
        
        # Predictions
        self.predictions: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self.stats = {
            "objects_tracked": 0,
            "contexts_captured": 0,
            "predictions_made": 0,
            "inferences_drawn": 0
        }
        
        logger.info(f"WorldModelKernel initialized at {self.world_path}")
    
    def add_object(
        self,
        name: str,
        object_type: ObjectType,
        position: Optional[Position] = None,
        properties: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0
    ) -> WorldObject:
        """Add an object to the world model."""
        object_id = f"{object_type.name}_{name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        obj = WorldObject(
            object_id=object_id,
            name=name,
            object_type=object_type,
            position=position or Position(),
            properties=properties or {},
            confidence=confidence
        )
        
        self.objects[object_id] = obj
        self.stats["objects_tracked"] += 1
        
        # Add to spatial index
        if position and position.path:
            self.spatial_grid[position.path].add(object_id)
        
        logger.debug(f"Added object: {name} ({object_type.name})")
        return obj
    
    def remove_object(self, object_id: str) -> bool:
        """Remove an object from the world model."""
        if object_id in self.objects:
            obj = self.objects[object_id]
            
            # Remove from spatial index
            if obj.position.path:
                self.spatial_grid[obj.position.path].discard(object_id)
            
            # Remove from relationships
            for other_obj in self.objects.values():
                for rel_type, rel_list in other_obj.relationships.items():
                    if object_id in rel_list:
                        rel_list.remove(object_id)
            
            del self.objects[object_id]
            logger.debug(f"Removed object: {object_id}")
            return True
        return False
    
    def update_object(
        self,
        object_id: str,
        position: Optional[Position] = None,
        properties: Optional[Dict[str, Any]] = None,
        confidence: Optional[float] = None
    ) -> bool:
        """Update an object's state."""
        if object_id not in self.objects:
            return False
        
        obj = self.objects[object_id]
        
        # Update position
        if position:
            # Remove from old spatial index
            if obj.position.path:
                self.spatial_grid[obj.position.path].discard(object_id)
            
            obj.position = position
            
            # Add to new spatial index
            if position.path:
                self.spatial_grid[position.path].add(object_id)
        
        # Update properties
        if properties:
            obj.properties.update(properties)
        
        # Update confidence
        if confidence is not None:
            obj.confidence = confidence
        
        obj.last_updated = datetime.utcnow().isoformat()
        logger.debug(f"Updated object: {object_id}")
        return True
    
    def add_relationship(
        self,
        from_id: str,
        to_id: str,
        relation: SpatialRelation
    ) -> bool:
        """Add a relationship between two objects."""
        if from_id not in self.objects or to_id not in self.objects:
            return False
        
        rel_key = relation.name
        if to_id not in self.objects[from_id].relationships[rel_key]:
            self.objects[from_id].relationships[rel_key].append(to_id)
        
        logger.debug(f"Added relationship: {from_id} {relation.name} {to_id}")
        return True
    
    def get_object(self, object_id: str) -> Optional[WorldObject]:
        """Get an object by ID."""
        return self.objects.get(object_id)
    
    def find_objects(
        self,
        object_type: Optional[ObjectType] = None,
        name_pattern: Optional[str] = None,
        path_prefix: Optional[str] = None
    ) -> List[WorldObject]:
        """Find objects matching criteria."""
        results = []
        
        for obj in self.objects.values():
            # Filter by type
            if object_type and obj.object_type != object_type:
                continue
            
            # Filter by name pattern
            if name_pattern and name_pattern not in obj.name:
                continue
            
            # Filter by path
            if path_prefix and not obj.position.path.startswith(path_prefix):
                continue
            
            results.append(obj)
        
        return results
    
    def capture_context(self, environmental_state: Optional[Dict[str, Any]] = None) -> Context:
        """Capture current environmental context."""
        context_id = f"ctx_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Gather active objects (recently updated)
        now = datetime.utcnow()
        active_objects = [
            obj_id for obj_id, obj in self.objects.items()
            if (now - datetime.fromisoformat(obj.last_updated)) < timedelta(minutes=5)
        ]
        
        # Gather spatial relations
        spatial_relations = []
        for obj_id, obj in self.objects.items():
            for rel_type, rel_list in obj.relationships.items():
                try:
                    relation = SpatialRelation[rel_type]
                    for target_id in rel_list:
                        spatial_relations.append((obj_id, target_id, relation))
                except KeyError:
                    continue
        
        context = Context(
            context_id=context_id,
            timestamp=datetime.utcnow().isoformat(),
            active_objects=active_objects,
            spatial_relations=spatial_relations,
            environmental_state=environmental_state or {},
            inferred_facts=[]
        )
        
        # Run inference
        self._infer_facts(context)
        
        self.contexts.append(context)
        self.current_context = context
        
        # Trim contexts
        if len(self.contexts) > self.max_contexts:
            self.contexts = self.contexts[-self.max_contexts:]
        
        self.stats["contexts_captured"] += 1
        logger.info(f"Captured context: {context_id} ({len(active_objects)} active objects)")
        return context
    
    def _infer_facts(self, context: Context):
        """Draw inferences from current context."""
        inferences = []
        
        # Inference 1: Files in same directory are related
        path_objects: Dict[str, List[str]] = defaultdict(list)
        for obj_id in context.active_objects:
            obj = self.objects.get(obj_id)
            if obj and obj.position.path:
                parent = str(Path(obj.position.path).parent)
                path_objects[parent].append(obj_id)
        
        for path, obj_ids in path_objects.items():
            if len(obj_ids) > 1:
                inferences.append(f"Directory '{path}' contains {len(obj_ids)} related objects")
        
        # Inference 2: Recently modified objects are active
        now = datetime.utcnow()
        recent_count = sum(
            1 for obj_id in context.active_objects
            if obj_id in self.objects
            and (now - datetime.fromisoformat(self.objects[obj_id].last_updated)) < timedelta(minutes=1)
        )
        if recent_count > 0:
            inferences.append(f"{recent_count} objects modified in last minute")
        
        # Inference 3: Object type distribution
        type_counts: Dict[str, int] = defaultdict(int)
        for obj_id in context.active_objects:
            if obj_id in self.objects:
                type_counts[self.objects[obj_id].object_type.name] += 1
        
        for obj_type, count in type_counts.items():
            inferences.append(f"{count} {obj_type} objects active")
        
        context.inferred_facts = inferences
        self.stats["inferences_drawn"] += len(inferences)
    
    def predict(
        self,
        object_id: str,
        prediction_type: str = "future_state",
        horizon_seconds: int = 60
    ) -> Dict[str, Any]:
        """Make a prediction about an object's future state."""
        if object_id not in self.objects:
            return {"error": "Object not found"}
        
        obj = self.objects[object_id]
        
        # Simple prediction based on recent activity
        now = datetime.utcnow()
        last_update = datetime.fromisoformat(obj.last_updated)
        time_since_update = (now - last_update).total_seconds()
        
        prediction = {
            "object_id": object_id,
            "prediction_type": prediction_type,
            "horizon_seconds": horizon_seconds,
            "timestamp": datetime.utcnow().isoformat(),
            "confidence": 0.5
        }
        
        # Predict based on object type
        if obj.object_type == ObjectType.FILE:
            # Predict file will be accessed if recently modified
            if time_since_update < 300:  # 5 minutes
                prediction["prediction"] = "likely_to_be_accessed"
                prediction["confidence"] = 0.7
            else:
                prediction["prediction"] = "stable"
                prediction["confidence"] = 0.8
        
        elif obj.object_type == ObjectType.PROCESS:
            # Predict process will continue running
            prediction["prediction"] = "continue_running"
            prediction["confidence"] = 0.6 if time_since_update > 60 else 0.9
        
        else:
            prediction["prediction"] = "stable"
            prediction["confidence"] = 0.5
        
        self.predictions[object_id] = prediction
        self.stats["predictions_made"] += 1
        
        return prediction
    
    def spatial_query(
        self,
        center_path: str,
        depth: int = 1
    ) -> List[WorldObject]:
        """Query objects in spatial proximity."""
        results = []
        
        # Direct contents
        if center_path in self.spatial_grid:
            for obj_id in self.spatial_grid[center_path]:
                if obj_id in self.objects:
                    results.append(self.objects[obj_id])
        
        # Adjacent directories (simplified)
        if depth > 0:
            center = Path(center_path)
            for path in self.spatial_grid.keys():
                path_obj = Path(path)
                if path_obj.parent == center or center.parent == path_obj:
                    for obj_id in self.spatial_grid[path]:
                        if obj_id in self.objects and obj_id not in [r.object_id for r in results]:
                            results.append(self.objects[obj_id])
        
        return results
    
    def get_state(self) -> Dict[str, Any]:
        """Get current world model state."""
        # Count by type
        type_counts: Dict[str, int] = defaultdict(int)
        for obj in self.objects.values():
            type_counts[obj.object_type.name] += 1
        
        return {
            "objects_tracked": len(self.objects),
            "by_type": dict(type_counts),
            "contexts_stored": len(self.contexts),
            "current_context_id": self.current_context.context_id if self.current_context else None,
            "spatial_locations": len(self.spatial_grid),
            "predictions_active": len(self.predictions),
            "total_inferences": self.stats["inferences_drawn"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_object_graph(self) -> Dict[str, Any]:
        """Get object relationship graph."""
        return {
            "nodes": [
                {
                    "id": obj_id,
                    "name": obj.name,
                    "type": obj.object_type.name,
                    "position": {
                        "x": obj.position.x,
                        "y": obj.position.y,
                        "z": obj.position.z,
                        "path": obj.position.path
                    }
                }
                for obj_id, obj in self.objects.items()
            ],
            "edges": [
                {
                    "source": obj_id,
                    "target": target_id,
                    "relation": rel_type
                }
                for obj_id, obj in self.objects.items()
                for rel_type, targets in obj.relationships.items()
                for target_id in targets
            ]
        }


if __name__ == "__main__":
    # Test the world model kernel
    root = Path(__file__).parent.parent
    world = WorldModelKernel(root)
    
    print("World Model State (initial):")
    print(json.dumps(world.get_state(), indent=2))
    
    print("\n=== Test 1: Add objects ===")
    
    # Add file objects
    file1 = world.add_object(
        name="brain_kernel.py",
        object_type=ObjectType.FILE,
        position=Position(path=str(root / "01_BRAIN")),
        properties={"size": 2048, "language": "python"}
    )
    
    file2 = world.add_object(
        name="senses_kernel.py",
        object_type=ObjectType.FILE,
        position=Position(path=str(root / "02_SENSES")),
        properties={"size": 1536, "language": "python"}
    )
    
    dir1 = world.add_object(
        name="AMOS_ORGANISM_OS",
        object_type=ObjectType.DIRECTORY,
        position=Position(path=str(root)),
        properties={"contains_subsystems": True}
    )
    
    print(f"Added {len(world.objects)} objects")
    
    print("\n=== Test 2: Add relationships ===")
    world.add_relationship(dir1.object_id, file1.object_id, SpatialRelation.CONTAINS)
    world.add_relationship(dir1.object_id, file2.object_id, SpatialRelation.CONTAINS)
    world.add_relationship(file1.object_id, file2.object_id, SpatialRelation.ADJACENT)
    
    print("Relationships added")
    
    print("\n=== Test 3: Find objects ===")
    files = world.find_objects(object_type=ObjectType.FILE)
    print(f"Found {len(files)} files")
    
    print("\n=== Test 4: Spatial query ===")
    nearby = world.spatial_query(str(root), depth=1)
    print(f"Objects near root: {len(nearby)}")
    
    print("\n=== Test 5: Capture context ===")
    context = world.capture_context({"system_load": 0.5, "active_users": 1})
    print(f"Context captured: {context.context_id}")
    print(f"Active objects: {len(context.active_objects)}")
    print(f"Inferred facts: {context.inferred_facts}")
    
    print("\n=== Test 6: Make prediction ===")
    prediction = world.predict(file1.object_id, horizon_seconds=300)
    print(f"Prediction: {prediction}")
    
    print("\nFinal State:")
    print(json.dumps(world.get_state(), indent=2))
