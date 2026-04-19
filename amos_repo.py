#!/usr/bin/env python3
"""AMOS Repo Intelligence - Section 14 of Architecture

Understands and analyzes code repositories:
- Skeleton: laws, types, contracts, invariants
- Cells: small reusable workers
- Nerves: signals, routing, salience, links
- Organs: major functional clusters
- Fascia: dependency/coherence/tension graph
- Blood: resource flow/perfusion
- Memory: storage and retrieval
- Immune: anomaly detection, quarantine, repair
- Awareness: self-model
- Motor: actuation and change
- Lifecycle: state transitions

Placement law:
Zone(x) = argmax_z [RoleFit(x,z) + DependencyFit(x,z) - Drift(x,z)]
"""

import ast
import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class CodeEntity:
    """A code entity in the repository."""

    name: str
    entity_type: str  # function, class, module, variable, etc.
    file_path: str
    line_start: int
    line_end: int
    content: str = ""

    # Metadata
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    complexity: int = 0
    docstring: str = ""

    # Zone classification
    zone: str = "unknown"  # skeleton, cells, nerves, organs, fascia, blood, memory, immune, motor


@dataclass
class DependencyEdge:
    """Dependency relationship between entities."""

    source: str
    target: str
    edge_type: str  # import, call, inherit, use
    strength: float = 1.0


class CodeParser:
    """Parse Python code to extract entities and relationships."""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.entities: Dict[str, CodeEntity] = {}
        self.dependencies: List[DependencyEdge] = []

    def parse_repository(self) -> Dict[str, CodeEntity]:
        """Parse entire repository."""
        for py_file in self.root_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            self._parse_file(py_file)

        # Build dependency graph
        self._build_dependency_graph()

        return self.entities

    def _parse_file(self, file_path: Path):
        """Parse a single Python file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            # Parse module-level
            module_name = str(file_path.relative_to(self.root_path))[:-3].replace("/", ".")

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._parse_class(node, file_path, content, module_name)
                elif isinstance(node, ast.FunctionDef):
                    self._parse_function(node, file_path, content, module_name)

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    def _parse_class(self, node: ast.ClassDef, file_path: Path, content: str, module: str):
        """Parse a class definition."""
        entity_id = f"{module}.{node.name}"

        # Get dependencies (bases)
        bases = [self._get_name(base) for base in node.bases if self._get_name(base)]

        # Calculate complexity (number of methods)
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        complexity = len(methods)

        # Get docstring
        docstring = ast.get_docstring(node) or ""

        entity = CodeEntity(
            name=node.name,
            entity_type="class",
            file_path=str(file_path),
            line_start=node.lineno,
            line_end=node.end_lineno if hasattr(node, "end_lineno") else node.lineno,
            content=content[node.lineno - 1 : node.end_lineno]
            if hasattr(node, "end_lineno")
            else "",
            dependencies=bases,
            complexity=complexity,
            docstring=docstring,
        )

        self.entities[entity_id] = entity

    def _parse_function(self, node: ast.FunctionDef, file_path: Path, content: str, module: str):
        """Parse a function definition."""
        entity_id = f"{module}.{node.name}"

        # Calculate complexity (simple: count of control flow statements)
        complexity = sum(
            1 for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While, ast.Try))
        )

        # Get docstring
        docstring = ast.get_docstring(node) or ""

        entity = CodeEntity(
            name=node.name,
            entity_type="function",
            file_path=str(file_path),
            line_start=node.lineno,
            line_end=node.end_lineno if hasattr(node, "end_lineno") else node.lineno,
            content=content[node.lineno - 1 : node.end_lineno]
            if hasattr(node, "end_lineno")
            else "",
            complexity=complexity,
            docstring=docstring,
        )

        self.entities[entity_id] = entity

    def _get_name(self, node) -> str:
        """Extract name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None

    def _build_dependency_graph(self):
        """Build dependency relationships between entities."""
        for entity_id, entity in self.entities.items():
            for dep in entity.dependencies:
                # Find the target entity
                target_id = self._resolve_dependency(dep, entity.file_path)
                if target_id and target_id in self.entities:
                    edge = DependencyEdge(
                        source=entity_id,
                        target=target_id,
                        edge_type="inherit" if entity.entity_type == "class" else "use",
                        strength=1.0,
                    )
                    self.dependencies.append(edge)

                    # Update entity dependents
                    self.entities[target_id].dependents.append(entity_id)

    def _resolve_dependency(self, name: str, file_path: str) -> str:
        """Resolve a dependency name to entity ID."""
        # Simple resolution - look for exact match
        for entity_id in self.entities:
            if entity_id.endswith(f".{name}") or entity_id == name:
                return entity_id
        return None


class ZoneClassifier:
    """Classify code entities into zones (skeleton, cells, nerves, organs, etc.)

    Zone(x) = argmax_z [RoleFit(x,z) + DependencyFit(x,z) - Drift(x,z)]
    """

    ZONE_DEFINITIONS = {
        "skeleton": {
            "description": "Laws, types, contracts, invariants - structural foundation",
            "patterns": [
                "abstract",
                "base",
                "interface",
                "contract",
                "law",
                "type",
                "schema",
                "config",
            ],
            "file_patterns": ["base", "core", "interface", "contract", "schema", "types"],
        },
        "cells": {
            "description": "Small reusable workers - simple, focused functions",
            "patterns": ["helper", "util", "tool", "worker"],
            "max_complexity": 5,
            "max_lines": 50,
        },
        "nerves": {
            "description": "Signals, routing, salience, links - communication",
            "patterns": ["signal", "event", "route", "channel", "queue", "message", "dispatch"],
        },
        "organs": {
            "description": "Major functional clusters - complex subsystems",
            "patterns": ["engine", "system", "manager", "controller", "service"],
            "min_complexity": 10,
        },
        "fascia": {
            "description": "Dependency/coherence/tension graph",
            "patterns": ["dependency", "graph", "connection", "link", "wire", "bind"],
        },
        "blood": {
            "description": "Resource flow/perfusion - data/resource movement",
            "patterns": ["flow", "stream", "pipeline", "resource", "allocation", "budget"],
        },
        "memory": {
            "description": "Storage and retrieval",
            "patterns": ["memory", "storage", "cache", "store", "persist", "retrieval", "recall"],
        },
        "immune": {
            "description": "Anomaly detection, quarantine, repair",
            "patterns": [
                "validate",
                "check",
                "verify",
                "detect",
                "guard",
                "protect",
                "sanitize",
                "immune",
            ],
        },
        "motor": {
            "description": "Actuation and change - execution",
            "patterns": ["execute", "run", "act", "perform", "morph", "transform", "apply"],
        },
    }

    def classify(self, entity: CodeEntity) -> str:
        """Classify entity into zone."""
        scores = {}

        for zone_name, zone_def in self.ZONE_DEFINITIONS.items():
            score = 0.0

            # RoleFit: Check name patterns
            name_lower = entity.name.lower()
            for pattern in zone_def.get("patterns", []):
                if pattern in name_lower:
                    score += 1.0

            # Complexity-based scoring
            if "max_complexity" in zone_def and entity.complexity <= zone_def["max_complexity"]:
                score += 0.5
            if "min_complexity" in zone_def and entity.complexity >= zone_def["min_complexity"]:
                score += 0.5

            if "max_lines" in zone_def:
                lines = entity.line_end - entity.line_start
                if lines <= zone_def["max_lines"]:
                    score += 0.5

            # File path patterns
            file_lower = entity.file_path.lower()
            for pattern in zone_def.get("file_patterns", []):
                if pattern in file_lower:
                    score += 1.0

            scores[zone_name] = score

        # Return zone with highest score
        if scores:
            best_zone = max(scores, key=scores.get)
            return best_zone if scores[best_zone] > 0 else "unknown"

        return "unknown"

    def classify_all(self, entities: Dict[str, CodeEntity]) -> Dict[str, CodeEntity]:
        """Classify all entities."""
        for entity in entities.values():
            entity.zone = self.classify(entity)
        return entities


class RepoAnalyzer:
    """Analyze repository health and structure."""

    def __init__(self, entities: Dict[str, CodeEntity], dependencies: List[DependencyEdge]):
        self.entities = entities
        self.dependencies = dependencies

    def compute_metrics(self) -> Dict[str, Any]:
        """Compute repository metrics."""
        metrics = {
            "total_entities": len(self.entities),
            "by_type": defaultdict(int),
            "by_zone": defaultdict(int),
            "avg_complexity": 0.0,
            "total_dependencies": len(self.dependencies),
            "orphan_entities": 0,
            "high_complexity_entities": 0,
        }

        complexities = []
        for entity in self.entities.values():
            metrics["by_type"][entity.entity_type] += 1
            metrics["by_zone"][entity.zone] += 1
            complexities.append(entity.complexity)

            # Orphan = no dependencies and no dependents
            if not entity.dependencies and not entity.dependents:
                metrics["orphan_entities"] += 1

            # High complexity threshold
            if entity.complexity > 20:
                metrics["high_complexity_entities"] += 1

        if complexities:
            metrics["avg_complexity"] = sum(complexities) / len(complexities)
            metrics["max_complexity"] = max(complexities)

        return dict(metrics)

    def find_cycles(self) -> List[list[str]]:
        """Find circular dependencies."""
        # Build adjacency list
        graph = defaultdict(set)
        for edge in self.dependencies:
            graph[edge.source].add(edge.target)

        cycles = []
        visited = set()
        path = []

        def dfs(node):
            if node in path:
                # Found cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return

            if node in visited:
                return

            visited.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                dfs(neighbor)

            path.pop()

        for entity_id in self.entities:
            if entity_id not in visited:
                dfs(entity_id)

        return cycles

    def detect_anomalies(self) -> List[dict]:
        """Detect anomalies in the codebase."""
        anomalies = []

        for entity in self.entities.values():
            # High complexity
            if entity.complexity > 30:
                anomalies.append(
                    {
                        "type": "high_complexity",
                        "entity": entity.name,
                        "severity": "warning",
                        "message": f"{entity.name} has complexity {entity.complexity} (very high)",
                    }
                )

            # Missing docstring on public API
            if entity.entity_type in ["class", "function"] and not entity.docstring:
                if not entity.name.startswith("_"):
                    anomalies.append(
                        {
                            "type": "missing_docstring",
                            "entity": entity.name,
                            "severity": "info",
                            "message": f"{entity.name} lacks documentation",
                        }
                    )

            # Too many dependencies
            if len(entity.dependencies) > 10:
                anomalies.append(
                    {
                        "type": "high_coupling",
                        "entity": entity.name,
                        "severity": "warning",
                        "message": f"{entity.name} has {len(entity.dependencies)} dependencies",
                    }
                )

        # Check for circular dependencies
        cycles = self.find_cycles()
        for cycle in cycles[:5]:  # Report first 5
            anomalies.append(
                {
                    "type": "circular_dependency",
                    "entity": " → ".join(cycle[:3]) + "...",
                    "severity": "error",
                    "message": f"Circular dependency detected: {' → '.join(cycle)}",
                }
            )

        return anomalies

    def generate_repo_summary(self) -> str:
        """Generate human-readable repository summary."""
        metrics = self.compute_metrics()
        anomalies = self.detect_anomalies()

        summary = []
        summary.append("=" * 70)
        summary.append("REPOSITORY ANALYSIS SUMMARY")
        summary.append("=" * 70)

        summary.append(f"\nTotal Entities: {metrics['total_entities']}")
        summary.append(f"Total Dependencies: {metrics['total_dependencies']}")
        summary.append(f"Average Complexity: {metrics['avg_complexity']:.1f}")
        summary.append(f"Max Complexity: {metrics.get('max_complexity', 'N/A')}")

        summary.append("\nBy Type:")
        for type_name, count in sorted(metrics["by_type"].items()):
            summary.append(f"  • {type_name}: {count}")

        summary.append("\nBy Zone (AMOS Architecture):")
        for zone_name, count in sorted(metrics["by_zone"].items()):
            if count > 0:
                summary.append(f"  • {zone_name}: {count}")

        # Anomalies
        errors = [a for a in anomalies if a["severity"] == "error"]
        warnings = [a for a in anomalies if a["severity"] == "warning"]

        if errors:
            summary.append(f"\nErrors ({len(errors)}):")
            for a in errors[:5]:
                summary.append(f"  ✗ {a['message']}")

        if warnings:
            summary.append(f"\nWarnings ({len(warnings)}):")
            for a in warnings[:5]:
                summary.append(f"  ⚠ {a['message']}")

        summary.append("\n" + "=" * 70)

        return "\n".join(summary)


class AMOSRepoIntelligence:
    """Complete AMOS Repo Intelligence System.

    Understands codebase structure, classifies components,
    detects anomalies, and provides recommendations.
    """

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.parser = CodeParser(repo_path)
        self.classifier = ZoneClassifier()
        self.analyzer: Optional[RepoAnalyzer] = None

    def analyze(self) -> Dict[str, Any]:
        """Complete repository analysis."""
        print(f"Analyzing repository: {self.repo_path}")

        # Parse code
        entities = self.parser.parse_repository()
        print(f"Found {len(entities)} code entities")

        # Classify into zones
        entities = self.classifier.classify_all(entities)

        # Create analyzer
        self.analyzer = RepoAnalyzer(entities, self.parser.dependencies)

        # Compute metrics
        metrics = self.analyzer.compute_metrics()

        # Detect anomalies
        anomalies = self.analyzer.detect_anomalies()

        return {
            "entities": entities,
            "metrics": metrics,
            "anomalies": anomalies,
            "summary": self.analyzer.generate_repo_summary(),
        }

    def get_entity(self, name: str) -> Optional[CodeEntity]:
        """Get specific entity by name."""
        if not self.analyzer:
            return None

        # Search by partial match
        for entity_id, entity in self.analyzer.entities.items():
            if name in entity_id or name in entity.name:
                return entity
        return None

    def find_similar(self, entity_name: str) -> List[CodeEntity]:
        """Find entities similar to given one."""
        target = self.get_entity(entity_name)
        if not target:
            return []

        similar = []
        for entity in self.analyzer.entities.values():
            if entity.name == target.name:
                continue

            # Same zone
            if entity.zone == target.zone:
                score = 1.0

                # Similar complexity
                complexity_diff = abs(entity.complexity - target.complexity)
                score += max(0, 1.0 - complexity_diff / 10)

                similar.append((entity, score))

        similar.sort(key=lambda x: x[1], reverse=True)
        return [e[0] for e in similar[:5]]

    def suggest_placement(self, entity: CodeEntity) -> str:
        """Suggest which zone an entity should be in."""
        current_zone = entity.zone
        suggested_zone = self.classifier.classify(entity)

        if current_zone != suggested_zone and suggested_zone != "unknown":
            return f"Consider moving {entity.name} from {current_zone} to {suggested_zone}"
        return f"{entity.name} is correctly placed in {current_zone}"


def demo_repo_intelligence():
    """Demonstrate AMOS Repo Intelligence."""
    print("=" * 70)
    print("📁 AMOS REPO INTELLIGENCE - Section 14")
    print("=" * 70)
    print("\nAnalyzing codebase structure and architecture...")
    print("Zone(x) = argmax_z [RoleFit(x,z) + DependencyFit(x,z) - Drift(x,z)]")
    print("=" * 70)

    # Analyze the AMOS codebase itself
    repo_path = os.path.dirname(os.path.abspath(__file__))
    intelligence = AMOSRepoIntelligence(repo_path)

    # Run analysis
    result = intelligence.analyze()

    # Display summary
    print("\n" + result["summary"])

    # Show zone distribution
    print("\n[Zone Analysis]")
    print("Code entities classified by AMOS architectural zones:")
    zone_counts = result["metrics"]["by_zone"]
    for zone, count in sorted(zone_counts.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            bar = "█" * count
            print(f"  {zone:12} {bar} ({count})")

    # Show some specific entities
    print("\n[Sample Classifications]")
    entities = list(result["entities"].values())[:10]
    for entity in entities:
        print(f"  • {entity.name:30} ({entity.entity_type:10}) → {entity.zone}")

    # Recommendations
    print("\n[Recommendations]")
    high_complexity = [e for e in result["entities"].values() if e.complexity > 20]
    if high_complexity:
        print(f"  • {len(high_complexity)} high-complexity entities could be refactored")

    orphans = result["metrics"].get("orphan_entities", 0)
    if orphans > 0:
        print(f"  • {orphans} entities have no dependencies (potential orphans)")

    cycles = len([a for a in result["anomalies"] if a["type"] == "circular_dependency"])
    if cycles > 0:
        print(f"  • {cycles} circular dependencies should be resolved")

    print("\n" + "=" * 70)
    print("✅ AMOS REPO INTELLIGENCE OPERATIONAL")
    print("=" * 70)
    print("\nCapabilities:")
    print("  • Parse and understand Python code structure")
    print("  • Classify entities into AMOS architectural zones")
    print("  • Detect anomalies (complexity, coupling, cycles)")
    print("  • Generate repository health reports")
    print("  • Provide refactoring recommendations")
    print("=" * 70)


if __name__ == "__main__":
    demo_repo_intelligence()
