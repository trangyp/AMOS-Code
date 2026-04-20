#!/usr/bin/env python3
"""AMOS Knowledge Deep Dive - Extract Knowledge from Engine Specifications.

Reads and catalogs all knowledge from:
- _AMOS_BRAIN/ Cognitive engine specs (12 engines)
- _AMOS_BRAIN/ Auto/ domain packs
- _AMOS_BRAIN/ AMOS_ORGANISM_OS/ subsystem specs
- clawspring/ engine implementations

Usage: python amos_knowledge_deep_dive.py [--engine <name>] [--list-all]
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class EngineSpec:
    """Parsed engine specification."""

    name: str
    version: str
    domains: list[str]
    capabilities: list[str]
    principles: list[str]
    constraints: list[str]
    file_path: str
    size_bytes: int


class AMOSKnowledgeDeepDive:
    """Deep diver for AMOS knowledge systems."""

    def __init__(self, root_path: Optional[Path] = None):
        self.root = root_path or Path(__file__).parent
        self.brain_dir = self.root / "_AMOS_BRAIN"
        self.engines: list[EngineSpec] = []
        self.total_knowledge_size = 0

    def scan_cognitive_engines(self) -> list[EngineSpec]:
        """Scan all 12 cognitive engine specs."""
        cognitive_dir = self.brain_dir / "Cognitive"
        engines = []

        if not cognitive_dir.exists():
            return engines

        for json_file in cognitive_dir.glob("*.json"):
            try:
                data = json.loads(json_file.read_text())
                spec = self._parse_engine_spec(data, json_file)
                if spec:
                    engines.append(spec)
                    self.total_knowledge_size += spec.size_bytes
            except Exception as e:
                print(f"  ⚠️  Error parsing {json_file.name}: {e}")

        return engines

    def _parse_engine_spec(self, data: Any, file_path: Path) -> Optional[EngineSpec]:
        """Parse engine specification from JSON."""
        try:
            # Handle both list and dict formats
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
            elif not isinstance(data, dict):
                return None

            # Extract engine name
            name = data.get("name", file_path.stem)

            # Extract version
            version = data.get("version", "unknown")

            # Extract domains from meta
            domains = []
            meta = data.get("meta", {})
            coverage = meta.get("coverage", {})
            domains = coverage.get("domains", [])

            # Extract capabilities from components
            capabilities = []
            components = data.get("components", {})
            for comp_name, comp_data in components.items():
                if isinstance(comp_data, dict):
                    caps = comp_data.get("capabilities", [])
                    capabilities.extend(caps)

            # Extract principles and constraints
            principles = []
            constraints = []

            # Look for global laws or reasoning constraints
            brain_root = components.get("AMOS_BRAIN_ROOT.json", {})
            if brain_root:
                laws = brain_root.get("global_laws", {})
                for law_id, law_data in laws.items():
                    if isinstance(law_data, dict):
                        desc = law_data.get("description", "")
                        if desc:
                            principles.append(f"{law_id}: {desc}")

            return EngineSpec(
                name=name,
                version=version,
                domains=domains,
                capabilities=list(set(capabilities)),
                principles=principles[:5],  # Limit principles shown
                constraints=constraints,
                file_path=str(file_path.relative_to(self.root)),
                size_bytes=file_path.stat().st_size,
            )

        except Exception:
            return None

    def scan_organism_specs(self) -> dict[str, Any]:
        """Scan Organism OS specifications."""
        organism_dir = self.root / "AMOS_ORGANISM_OS"
        specs = {"subsystems": 0, "total_files": 0, "total_size": 0}

        for py_file in organism_dir.rglob("*.py"):
            if "__pycache__" not in str(py_file):
                specs["total_files"] += 1
                specs["total_size"] += py_file.stat().st_size

        return specs

    def scan_clawspring_engines(self) -> list[dict[str, Any]]:
        """Scan ClawSpring engine implementations."""
        clawspring_dir = self.root / "clawspring"
        engines = []

        for py_file in clawspring_dir.rglob("*engine*.py"):
            try:
                content = py_file.read_text()
                # Extract class names
                import ast

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if "Engine" in node.name:
                            methods = [
                                n.name
                                for n in node.body
                                if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")
                            ]
                            engines.append(
                                {
                                    "name": node.name,
                                    "file": str(py_file.relative_to(self.root)),
                                    "methods": methods[:5],
                                }
                            )
            except Exception:
                pass

        return engines

    def generate_knowledge_report(self) -> dict[str, Any]:
        """Generate comprehensive knowledge report."""
        self.engines = self.scan_cognitive_engines()
        organism_specs = self.scan_organism_specs()
        clawspring_engines = self.scan_clawspring_engines()

        # Calculate statistics
        total_domains = set()
        total_capabilities = set()
        for engine in self.engines:
            total_domains.update(engine.domains)
            total_capabilities.update(engine.capabilities)

        return {
            "cognitive_engines": {
                "count": len(self.engines),
                "total_size_kb": self.total_knowledge_size // 1024,
                "engines": [
                    {
                        "name": e.name,
                        "version": e.version,
                        "domains": e.domains,
                        "capabilities_count": len(e.capabilities),
                        "size_kb": e.size_bytes // 1024,
                    }
                    for e in self.engines
                ],
            },
            "domain_coverage": {
                "unique_domains": list(total_domains),
                "unique_capabilities": len(total_capabilities),
            },
            "organism_os": organism_specs,
            "clawspring_engines": {
                "count": len(clawspring_engines),
                "engines": clawspring_engines[:10],
            },
            "summary": {
                "total_knowledge_size_mb": self.total_knowledge_size / (1024 * 1024),
                "total_engines": len(self.engines) + len(clawspring_engines),
                "total_domains_covered": len(total_domains),
            },
        }

    def print_knowledge_summary(self) -> None:
        """Print formatted knowledge summary."""
        report = self.generate_knowledge_report()

        print("=" * 70)
        print("  📚 AMOS KNOWLEDGE DEEP DIVE")
        print("  Engine Specifications & Domain Coverage")
        print("=" * 70)

        # Cognitive Engines
        cog = report["cognitive_engines"]
        print(f"\n  🧠 COGNITIVE ENGINES: {cog['count']}")
        print(f"     Total Knowledge: {cog['total_size_kb']:,} KB")

        for engine in cog["engines"]:
            name = engine["name"].replace("AMOS_", "").replace("_Engine", "")
            domains = ", ".join(engine["domains"][:3]) if engine["domains"] else "General"
            print(f"\n     📖 {name}")
            print(f"        Version: {engine['version']}")
            print(f"        Domains: {domains}")
            print(f"        Capabilities: {engine['capabilities_count']}")
            print(f"        Size: {engine['size_kb']} KB")

        # Domain Coverage
        coverage = report["domain_coverage"]
        print("\n  🌐 DOMAIN COVERAGE")
        print(f"     Unique Domains: {coverage['unique_domains']}")
        print(f"     Total Capabilities: {coverage['unique_capabilities']}")

        # Organism OS
        org = report["organism_os"]
        print("\n  🏥 ORGANISM OS")
        print(f"     Implementation Files: {org['total_files']}")
        print(f"     Code Size: {org['total_size'] // 1024:,} KB")

        # ClawSpring
        claw = report["clawspring_engines"]
        print(f"\n  🔌 CLAWSPRING ENGINES: {claw['count']}")
        for engine in claw["engines"][:5]:
            print(f"     ⚡ {engine['name']}")

        # Summary
        summary = report["summary"]
        print("\n" + "=" * 70)
        print("  📊 TOTAL KNOWLEDGE BASE")
        print(f"     Size: {summary['total_knowledge_size_mb']:.1f} MB")
        print(f"     Engines: {summary['total_engines']}")
        print(f"     Domain Coverage: {summary['total_domains_covered']} domains")
        print("=" * 70)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS Knowledge Deep Dive")
    parser.add_argument("--engine", type=str, help="Show specific engine details")
    parser.add_argument("--list-all", action="store_true", help="List all capabilities")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    diver = AMOSKnowledgeDeepDive()

    if args.engine:
        # Show specific engine
        engines = diver.scan_cognitive_engines()
        for engine in engines:
            if args.engine.lower() in engine.name.lower():
                print(f"\n📖 {engine.name}")
                print(f"   Version: {engine.version}")
                print(f"   Domains: {engine.domains}")
                print(f"   Capabilities: {engine.capabilities}")
                print(f"   Principles: {engine.principles}")
                return
        print(f"Engine '{args.engine}' not found")
        return

    if args.json:
        report = diver.generate_knowledge_report()
        print(json.dumps(report, indent=2))
        return

    # Default: print summary
    diver.print_knowledge_summary()


if __name__ == "__main__":
    main()
