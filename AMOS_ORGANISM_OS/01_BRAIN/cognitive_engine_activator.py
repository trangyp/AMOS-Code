#!/usr/bin/env python3
"""Cognitive Engine Activator - BRAIN Subsystem
==============================================

Activates and loads dormant cognitive engines from _AMOS_BRAIN.
Provides query interface for domain-specific expertise.

Owner: Trang
Version: 1.0.0
"""

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CognitiveEngine:
    """Represents a loaded cognitive engine."""

    name: str
    version: str
    description: str
    domain: str
    data: Dict[str, Any]
    file_path: Path
    size_bytes: int


class CognitiveEngineActivator:
    """Activates dormant cognitive engines from _AMOS_BRAIN.

    Loads domain-specific expertise engines:
    - Design Engine (architecture, patterns)
    - Engineering & Mathematics Engine
    - Biology & Cognition Engine
    - Econ & Finance Engine
    - And 6 more...
    """

    ENGINE_DIR = Path(__file__).parent.parent.parent / "_AMOS_BRAIN" / "Cognitive"

    def __init__(self):
        self.engines: Dict[str, CognitiveEngine] = {}
        self._loaded = False

    def load_all_engines(self) -> dict[str, CognitiveEngine]:
        """Load all cognitive engines from _AMOS_BRAIN/Cognitive/."""
        if not self.ENGINE_DIR.exists():
            print(f"[COGNITIVE] Engine directory not found: {self.ENGINE_DIR}")
            return {}

        json_files = list(self.ENGINE_DIR.glob("*.json"))
        print(f"[COGNITIVE] Found {len(json_files)} engine files")

        for file_path in json_files:
            try:
                engine = self._load_engine(file_path)
                if engine:
                    self.engines[engine.name] = engine
                    print(f"  ✓ Loaded: {engine.name} ({engine.domain})")
            except Exception as e:
                print(f"  ✗ Failed: {file_path.name} - {e}")

        self._loaded = True
        print(f"[COGNITIVE] Activated {len(self.engines)} engines")
        return self.engines

    def _load_engine(self, file_path: Path) -> Optional[CognitiveEngine]:
        """Load a single cognitive engine."""
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        # Extract metadata
        meta = data.get("meta", {}) if isinstance(data, dict) else {}
        if isinstance(data, list) and len(data) > 0:
            meta = data[0].get("meta", {})

        name = meta.get("name", file_path.stem.replace("_", " ").replace("v0", ""))
        version = meta.get("version", "v0")
        description = meta.get("description", "Cognitive engine")

        # Determine domain from filename
        domain = self._extract_domain(file_path.stem)

        return CognitiveEngine(
            name=name,
            version=version,
            description=description,
            domain=domain,
            data=data,
            file_path=file_path,
            size_bytes=file_path.stat().st_size,
        )

    def _extract_domain(self, filename: str) -> str:
        """Extract domain from engine filename."""
        domain_map = {
            "biology": "Life Sciences",
            "cognition": "Cognitive Science",
            "design": "Design & Architecture",
            "economics": "Economics & Finance",
            "electrical": "Electrical Engineering",
            "engineering": "Engineering & Math",
            "mechanical": "Mechanical & Structural",
            "medical": "Medical & Health",
            "physics": "Physics & Chemistry",
            "strategy": "Strategy & Game Theory",
            "signal": "Signal Processing",
            "numerical": "Numerical Methods",
            "society": "Society & Culture",
            "cosmos": "Physics & Cosmos",
            "deterministic": "Logic & Law",
        }

        lower_name = filename.lower()
        for key, domain in domain_map.items():
            if key in lower_name:
                return domain
        return "General"

    def get_engine(self, name: str) -> Optional[CognitiveEngine]:
        """Get a specific engine by name."""
        if not self._loaded:
            self.load_all_engines()
        return self.engines.get(name)

    def query_domain(self, domain: str, query: str) -> Dict[str, Any]:
        """Query engines in a specific domain."""
        if not self._loaded:
            self.load_all_engines()

        results = []
        for engine in self.engines.values():
            if domain.lower() in engine.domain.lower():
                results.append(
                    {
                        "engine": engine.name,
                        "description": engine.description,
                        "size_mb": round(engine.size_bytes / (1024 * 1024), 2),
                    }
                )

        return {
            "domain": domain,
            "query": query,
            "matching_engines": len(results),
            "engines": results,
        }

    def get_status(self) -> Dict[str, Any]:
        """Get activator status."""
        if not self._loaded:
            self.load_all_engines()

        total_size = sum(e.size_bytes for e in self.engines.values())
        domains = {}
        for e in self.engines.values():
            domains[e.domain] = domains.get(e.domain, 0) + 1

        return {
            "loaded": self._loaded,
            "engines_count": len(self.engines),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "domains": domains,
            "engine_names": list(self.engines.keys()),
        }


def main():
    """CLI demo of cognitive engine activator."""
    print("=" * 60)
    print("AMOS Cognitive Engine Activator")
    print("=" * 60)

    activator = CognitiveEngineActivator()
    status = activator.get_status()

    print("\nStatus:")
    print(f"  Engines loaded: {status['engines_count']}")
    print(f"  Total size: {status['total_size_mb']} MB")
    print(f"  Domains covered: {len(status['domains'])}")

    print("\nDomain Distribution:")
    for domain, count in sorted(status["domains"].items()):
        print(f"  - {domain}: {count} engines")

    print("\nActive Engines:")
    for name in status["engine_names"][:5]:
        engine = activator.get_engine(name)
        print(f"  ✓ {name}")
        print(f"    Domain: {engine.domain}")
        print(f"    Size: {round(engine.size_bytes / 1024, 1)} KB")

    if len(status["engine_names"]) > 5:
        print(f"    ... and {len(status['engine_names']) - 5} more")

    # Demo query
    print("\nDemo Query: 'design patterns'")
    result = activator.query_domain("Design", "design patterns")
    print(f"  Matching engines: {result['matching_engines']}")
    for eng in result["engines"][:2]:
        print(f"    - {eng['engine']}")

    print("\n" + "=" * 60)
    print("Cognitive Engine Activator ready")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
