#!/usr/bin/env python3
"""AMOS Knowledge Activation Engine
=================================
Transform 963 JSON engines and 886MB of knowledge into runtime memory.

Features:
- Hot-load JSON engines on demand
- Knowledge query interface for reasoning
- Lazy loading with LRU cache
- Context injection into AMOS Brain
- Runtime knowledge graph

Usage:
    python amos_knowledge_activation.py [command]

Commands:
    status          Show activation status
    load <engine>   Load specific engine into runtime
    query <topic>   Query knowledge base
    activate        Activate all critical engines
    inject          Inject knowledge into AMOS Brain
    server          Start knowledge API server
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).parent / "clawspring"))
sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class ActivatedKnowledge:
    """Activated knowledge in runtime memory."""

    name: str
    category: str
    content: dict[str, Any]
    activated_at: str
    size_bytes: int
    access_count: int = 0
    last_accessed: Optional[str] = None


class KnowledgeActivation:
    """Activate and manage knowledge in runtime memory."""

    CRITICAL_ENGINES = [
        # Core Intelligence
        ("Core/AMOS_Brain_Master_Os_v0.json", "master_brain"),
        ("Core/Ubi/AMOS_Ubi_Engine_v0.json", "ubi"),
        ("Core/Ubi/AMOS_Nbi_Engine_v0.json", "nbi"),
        ("Core/Ubi/AMOS_Nei_Engine_v0.json", "nei"),
        ("Core/Ubi/AMOS_Si_Engine_v0.json", "si"),
        ("Core/Ubi/AMOS_Bei_Engine_v0.json", "bei"),
        # Cognitive Stack
        ("Core/7_Intelligents/AMOS_Biology_And_Cognition_Engine_v0.json", "biology"),
        ("Core/7_Intelligents/AMOS_Engineering_And_Mathematics_Engine_v0.json", "engineering"),
        ("Core/7_Intelligents/AMOS_Physics_Cosmos_Engine_v0.json", "physics"),
        ("Core/7_Intelligents/AMOS_Society_Culture_Engine_v0.json", "society"),
        ("Core/7_Intelligents/AMOS_Econ_Finance_Engine_v0.json", "economics"),
        ("Core/7_Intelligents/AMOS_Strategy_Game_Engine_v0.json", "strategy"),
        ("Core/7_Intelligents/AMOS_Deterministic_Logic_And_Law_Engine_v0.json", "law"),
    ]

    def __init__(self, brain_root: Optional[Path] = None):
        self.brain_root = brain_root or Path(__file__).parent / "_AMOS_BRAIN"
        self.active_knowledge: dict[str, ActivatedKnowledge] = {}
        self.query_cache: dict[str, Any] = {}
        self.stats = {
            "loaded_engines": 0,
            "total_size_mb": 0.0,
            "queries_served": 0,
            "cache_hits": 0,
        }

    def get_status(self) -> dict[str, Any]:
        """Get activation status."""
        return {
            "active_engines": len(self.active_knowledge),
            "total_engines_available": 963,
            "memory_usage_mb": self.stats["total_size_mb"],
            "queries_served": self.stats["queries_served"],
            "critical_engines_loaded": sum(
                1 for _, key in self.CRITICAL_ENGINES if key in self.active_knowledge
            ),
            "timestamp": datetime.now().isoformat(),
        }

    def print_status(self):
        """Print activation status."""
        print("=" * 70)
        print("AMOS KNOWLEDGE ACTIVATION - STATUS")
        print("=" * 70)

        status = self.get_status()
        print(f"\nActive Engines: {status['active_engines']}/963")
        print(f"Critical Engines: {status['critical_engines_loaded']}/{len(self.CRITICAL_ENGINES)}")
        print(f"Memory Usage: {status['memory_usage_mb']:.2f} MB")
        print(f"Queries Served: {status['queries_served']}")

        if self.active_knowledge:
            print("\nCurrently Active:")
            for name, knowledge in sorted(self.active_knowledge.items()):
                size_kb = knowledge.size_bytes / 1024
                accesses = knowledge.access_count
                print(f"  {name:20s} {size_kb:8.1f} KB ({accesses} accesses)")

    @lru_cache(maxsize=50)
    def _load_json_file(self, path: Path) -> Optional[dict]:
        """Load JSON file with caching."""
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"  ⚠ Error loading {path}: {e}")
            return None

    def activate_engine(self, engine_path: str, key: Optional[str] = None) -> bool:
        """Activate a specific engine into runtime memory."""
        full_path = self.brain_root / engine_path

        if not full_path.exists():
            print(f"  ✗ Engine not found: {engine_path}")
            return False

        # Load content
        content = self._load_json_file(full_path)
        if content is None:
            return False

        # Create key from filename if not provided
        if key is None:
            key = full_path.stem.replace("AMOS_", "").replace("_Engine_v0", "").lower()

        # Store in active knowledge
        size = full_path.stat().st_size
        knowledge = ActivatedKnowledge(
            name=full_path.stem,
            category=self._get_category(full_path),
            content=content,
            activated_at=datetime.now().isoformat(),
            size_bytes=size,
        )

        self.active_knowledge[key] = knowledge
        self.stats["loaded_engines"] += 1
        self.stats["total_size_mb"] += size / (1024 * 1024)

        print(f"  ✓ Activated: {key} ({size / 1024:.1f} KB)")
        return True

    def _get_category(self, path: Path) -> str:
        """Determine category from path."""
        path_str = str(path).lower()
        if "/core/ubi/" in path_str:
            return "ubi"
        elif "/core/7_intelligents/" in path_str:
            return "cognitive"
        elif "/core/" in path_str:
            return "core"
        elif "/cognitive/" in path_str:
            return "cognitive"
        elif "/unipower/" in path_str:
            return "unipower"
        elif "/domains/" in path_str:
            return "domains"
        elif "/kernels/tech/" in path_str:
            return "tech"
        else:
            return "other"

    def activate_critical_engines(self) -> dict[str, Any]:
        """Activate all critical engines for runtime operation."""
        print("=" * 70)
        print("ACTIVATING CRITICAL ENGINES")
        print("=" * 70)

        success = 0
        failed = 0

        for engine_path, key in self.CRITICAL_ENGINES:
            if self.activate_engine(engine_path, key):
                success += 1
            else:
                failed += 1

        print(f"\n✓ Activated: {success}/{len(self.CRITICAL_ENGINES)} critical engines")
        if failed:
            print(f"⚠ Failed: {failed}")

        return {"success": success, "failed": failed}

    def query(self, topic: str, depth: int = 1) -> dict[str, Any]:
        """Query active knowledge for a topic."""
        self.stats["queries_served"] += 1
        topic_lower = topic.lower()

        results = {"topic": topic, "matches": [], "related_engines": [], "summary": ""}

        # Search in active knowledge
        for key, knowledge in self.active_knowledge.items():
            knowledge.access_count += 1
            knowledge.last_accessed = datetime.now().isoformat()

            # Check if topic matches engine name/category
            if topic_lower in key.lower() or topic_lower in knowledge.category.lower():
                results["matches"].append(
                    {
                        "engine": key,
                        "category": knowledge.category,
                        "activated": knowledge.activated_at,
                    }
                )

            # Search in content (limited depth)
            if depth > 0 and isinstance(knowledge.content, dict):
                content_str = json.dumps(knowledge.content)[:10000]  # Limit search
                if topic_lower in content_str.lower():
                    results["related_engines"].append(key)

        # Generate summary
        if results["matches"]:
            results["summary"] = f"Found {len(results['matches'])} matching engines"
        elif results["related_engines"]:
            results["summary"] = f"Found {len(results['related_engines'])} related engines"
        else:
            results["summary"] = "No active knowledge found. Try activating more engines."

        return results

    def inject_into_amos(self) -> bool:
        """Inject activated knowledge into AMOS Brain runtime."""
        print("=" * 70)
        print("INJECTING KNOWLEDGE INTO AMOS BRAIN")
        print("=" * 70)

        try:
            from amos_brain import get_amos_integration

            amos = get_amos_integration()

            # Build knowledge summary
            knowledge_summary = {
                "active_engines": list(self.active_knowledge.keys()),
                "categories": list(set(k.category for k in self.active_knowledge.values())),
                "total_engines": len(self.active_knowledge),
                "injected_at": datetime.now().isoformat(),
            }

            # Add to AMOS context if possible
            if hasattr(amos, "context"):
                amos.context["activated_knowledge"] = knowledge_summary
                print("  ✓ Knowledge summary added to AMOS context")

            # Log activation
            print(f"  ✓ Injected {len(self.active_knowledge)} engines into AMOS runtime")
            print(f"  ✓ Categories: {', '.join(knowledge_summary['categories'])}")

            return True
        except Exception as e:
            print(f"  ✗ Failed to inject: {e}")
            return False

    def get_knowledge_graph(self) -> dict[str, Any]:
        """Get knowledge graph of active engines."""
        nodes = []
        edges = []

        for key, knowledge in self.active_knowledge.items():
            nodes.append(
                {
                    "id": key,
                    "category": knowledge.category,
                    "size": knowledge.size_bytes,
                    "access_count": knowledge.access_count,
                }
            )

            # Create edges based on category relationships
            for other_key, other in self.active_knowledge.items():
                if key != other_key and knowledge.category == other.category:
                    edges.append({"source": key, "target": other_key, "type": "same_category"})

        return {"nodes": nodes, "edges": edges}

    def hot_load(self, category: str) -> int:
        """Hot-load all engines of a category."""
        print(f"\nHot-loading category: {category}")

        loaded = 0
        # Scan for matching engines
        search_paths = [
            self.brain_root / "Core" / "**" / "*.json",
            self.brain_root / "Cognitive" / "**" / "*.json",
            self.brain_root / "Unipower" / "**" / "*.json",
        ]

        for pattern in search_paths:
            for json_file in self.brain_root.glob(str(pattern)):
                cat = self._get_category(json_file)
                if cat == category:
                    key = json_file.stem.replace("AMOS_", "").replace("_Engine_v0", "").lower()[:20]
                    if key not in self.active_knowledge:
                        relative = json_file.relative_to(self.brain_root)
                        if self.activate_engine(str(relative), key):
                            loaded += 1

        print(f"  ✓ Hot-loaded {loaded} {category} engines")
        return loaded

    def interactive_shell(self):
        """Interactive knowledge shell."""
        print("=" * 70)
        print("AMOS KNOWLEDGE ACTIVATION SHELL")
        print("=" * 70)
        print("\nCommands:")
        print("  status              Show activation status")
        print("  load <engine>       Load specific engine")
        print("  activate            Activate critical engines")
        print("  query <topic>       Query knowledge")
        print("  hotload <category>  Hot-load category")
        print("  inject              Inject into AMOS Brain")
        print("  graph               Show knowledge graph")
        print("  quit                Exit shell")

        while True:
            try:
                cmd = input("\nKnowledge> ").strip().split()
                if not cmd:
                    continue

                if cmd[0] == "quit":
                    break
                elif cmd[0] == "status":
                    self.print_status()
                elif cmd[0] == "activate":
                    self.activate_critical_engines()
                elif cmd[0] == "load" and len(cmd) > 1:
                    self.activate_engine(cmd[1])
                elif cmd[0] == "query" and len(cmd) > 1:
                    topic = " ".join(cmd[1:])
                    results = self.query(topic)
                    print(f"\nQuery: {topic}")
                    print(f"Summary: {results['summary']}")
                    if results["matches"]:
                        print("Matches:")
                        for m in results["matches"][:10]:
                            print(f"  - {m['engine']} ({m['category']})")
                elif cmd[0] == "hotload" and len(cmd) > 1:
                    self.hot_load(cmd[1])
                elif cmd[0] == "inject":
                    self.inject_into_amos()
                elif cmd[0] == "graph":
                    graph = self.get_knowledge_graph()
                    print("\nKnowledge Graph:")
                    print(f"  Nodes: {len(graph['nodes'])}")
                    print(f"  Edges: {len(graph['edges'])}")
                    for node in graph["nodes"][:10]:
                        print(f"    {node['id']} ({node['category']})")
                else:
                    print("Unknown command")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

        print("\nKnowledge shell exited.")


def main():
    parser = argparse.ArgumentParser(
        description="AMOS Knowledge Activation - Load 963 engines into runtime",
        epilog="""
Examples:
  python amos_knowledge_activation.py status
  python amos_knowledge_activation.py activate
  python amos_knowledge_activation.py query biology
  python amos_knowledge_activation.py inject
  python amos_knowledge_activation.py shell
        """,
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="status",
        choices=["status", "activate", "query", "inject", "graph", "shell", "hotload"],
    )
    parser.add_argument("argument", nargs="?", help="Engine path, query topic, or category")

    args = parser.parse_args()

    activation = KnowledgeActivation()

    if args.command == "status":
        activation.print_status()
    elif args.command == "activate":
        activation.activate_critical_engines()
        activation.print_status()
    elif args.command == "query":
        if args.argument:
            results = activation.query(args.argument)
            print(f"\nQuery: {args.argument}")
            print(f"Summary: {results['summary']}")
            if results["matches"]:
                print("\nMatching Engines:")
                for m in results["matches"]:
                    print(f"  ✓ {m['engine']} ({m['category']})")
            if results["related_engines"]:
                print(f"\nRelated: {', '.join(results['related_engines'][:10])}")
        else:
            print("Usage: python amos_knowledge_activation.py query <topic>")
    elif args.command == "inject":
        activation.activate_critical_engines()
        activation.inject_into_amos()
    elif args.command == "graph":
        graph = activation.get_knowledge_graph()
        print("\nKnowledge Graph:")
        print(f"  Active Engines: {len(graph['nodes'])}")
        print(f"  Relationships: {len(graph['edges'])}")
        print("\nActive Knowledge:")
        for node in sorted(graph["nodes"], key=lambda x: x["access_count"], reverse=True)[:15]:
            size_kb = node["size"] / 1024
            print(
                f"  {node['id']:20s} {node['category']:12s} {size_kb:8.1f} KB ({node['access_count']} hits)"
            )
    elif args.command == "hotload":
        if args.argument:
            activation.hot_load(args.argument)
        else:
            print("Usage: python amos_knowledge_activation.py hotload <category>")
    elif args.command == "shell":
        activation.interactive_shell()

    return 0


if __name__ == "__main__":
    sys.exit(main())
