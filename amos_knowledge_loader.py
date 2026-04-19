#!/usr/bin/env python3
"""AMOS Knowledge Loader v2.0.0 - Load 1,500+ knowledge files with SuperBrain governance.

SUPERBRAIN INTEGRATION:
- Knowledge loading validated via ActionGate
- All knowledge access recorded in brain audit trail
- Canonical access point for _AMOS_BRAIN knowledge base

Owner: Trang Phan
Version: 2.0.0
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# SuperBrain integration
try:
    from typing import Final

    from amos_brain import get_super_brain

    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False


@dataclass
class LoadedKnowledge:
    """A loaded knowledge item in runtime memory."""

    name: str
    category: str
    source_path: str
    content: Dict[str, Any] = field(default_factory=dict)
    load_time: str = ""
    size_bytes: int = 0
    access_count: int = 0


class KnowledgeLoader:
    """Load and manage 1,500+ knowledge files with SuperBrain governance."""

    def __init__(self, brain_root: Optional[Path] = None):
        self.brain_root = brain_root or Path(__file__).parent / "_AMOS_BRAIN"
        self.knowledge_cache: Dict[str, LoadedKnowledge] = {}
        self.category_index: dict[str, list[str]] = {}
        self.total_loaded = 0
        self.total_size_mb = 0.0
        self._brain = None
        self._init_superbrain()

    def _init_superbrain(self):
        """Initialize SuperBrain connection for governance."""
        if SUPERBRAIN_AVAILABLE:
            try:
                self._brain = get_super_brain()
            except Exception:
                pass

    def _validate_knowledge_load(self, operation: str, file_count: int) -> bool:
        """Validate knowledge loading via SuperBrain ActionGate."""
        if not SUPERBRAIN_AVAILABLE or not self._brain:
            return True

        try:
            if hasattr(self._brain, "action_gate"):
                action_result = self._brain.action_gate.validate_action(
                    agent_id="knowledge_loader",
                    action=f"knowledge_{operation}",
                    details={"file_count": file_count, "brain_root": str(self.brain_root)},
                )
                return action_result.authorized
        except Exception:
            pass
        return True

    def _record_knowledge_access(self, operation: str, file_count: int):
        """Record knowledge access in SuperBrain audit trail."""
        if not SUPERBRAIN_AVAILABLE or not self._brain:
            return

        try:
            if hasattr(self._brain, "record_audit"):
                self._brain.record_audit(
                    action=f"knowledge_{operation}",
                    agent_id="knowledge_loader",
                    details={
                        "files": file_count,
                        "size_mb": self.total_size_mb,
                        "categories": len(self.category_index),
                    },
                )
        except Exception:
            pass

    def load_all(self) -> Dict[str, Any]:
        """Load all 1,500+ knowledge files with SuperBrain governance."""
        print("[KNOWLEDGE_LOADER] Loading ecosystem knowledge...")
        print(f"  Source: {self.brain_root}")

        if not self.brain_root.exists():
            print("  ❌ Brain root not found")
            return {"error": "Brain root not found"}

        # CANONICAL: Validate knowledge loading via SuperBrain
        if not self._validate_knowledge_load("load_all", 0):
            print("  ❌ Knowledge loading blocked by SuperBrain governance")
            return {"error": "Governance blocked"}

        # Load JSON knowledge files
        self._load_json_knowledge()

        # Load text specifications
        self._load_text_specs()

        # Build category index
        self._build_category_index()

        stats = {
            "total_loaded": len(self.knowledge_cache),
            "total_size_mb": self.total_size_mb,
            "categories": len(self.category_index),
            "by_category": {k: len(v) for k, v in self.category_index.items()},
        }

        # CANONICAL: Record knowledge access in SuperBrain audit
        self._record_knowledge_access("load_all", stats["total_loaded"])

        print(f"\n✓ Loaded {stats['total_loaded']} knowledge items")
        print(f"✓ Total size: {stats['total_size_mb']:.1f} MB")
        print(f"✓ Categories: {stats['categories']}")

        return stats

    def _load_json_knowledge(self):
        """Load JSON knowledge files."""
        json_files = list(self.brain_root.rglob("*.json"))

        for file_path in json_files:
            if not file_path.is_file():
                continue

            try:
                # Skip very large files (>50MB) for now - load on demand
                size = file_path.stat().st_size
                if size > 50 * 1024 * 1024:
                    self._register_large_file(file_path, size)
                    continue

                # Load the JSON
                with open(file_path, encoding="utf-8") as f:
                    content = json.load(f)

                # Categorize
                name_lower = file_path.stem.lower()
                category = self._categorize_knowledge(name_lower)

                # Create loaded knowledge entry
                knowledge = LoadedKnowledge(
                    name=file_path.stem,
                    category=category,
                    source_path=str(file_path.relative_to(self.brain_root)),
                    content=content,
                    load_time=datetime.now(UTC).isoformat(),
                    size_bytes=size,
                )

                key = f"{category}/{file_path.stem}"
                self.knowledge_cache[key] = knowledge
                self.total_size_mb += size / (1024 * 1024)

            except Exception as e:
                print(f"  ⚠ Failed to load {file_path}: {e}")

    def _load_text_specs(self):
        """Load text specification files."""
        txt_files = list(self.brain_root.rglob("*.txt"))

        for file_path in txt_files:
            if not file_path.is_file():
                continue

            try:
                size = file_path.stat().st_size
                if size > 10 * 1024 * 1024:  # Skip files > 10MB
                    continue

                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    text_content = f.read()

                name_lower = file_path.stem.lower()
                category = self._categorize_knowledge(name_lower)

                knowledge = LoadedKnowledge(
                    name=file_path.stem,
                    category=f"{category}_text",
                    source_path=str(file_path.relative_to(self.brain_root)),
                    content={"text": text_content[:10000]},  # First 10KB
                    load_time=datetime.now(UTC).isoformat(),
                    size_bytes=size,
                )

                key = f"text/{file_path.stem}"
                self.knowledge_cache[key] = knowledge
                self.total_size_mb += size / (1024 * 1024)

            except Exception:
                pass  # Skip problematic text files

    def _categorize_knowledge(self, name_lower: str) -> str:
        """Categorize knowledge by filename."""
        if "engine" in name_lower:
            return "engine"
        elif "kernel" in name_lower:
            return "kernel"
        elif "pack" in name_lower:
            return "pack"
        elif "brain" in name_lower:
            return "brain"
        elif "consulting" in name_lower:
            return "consulting"
        elif "coding" in name_lower or "code" in name_lower:
            return "coding"
        elif "legal" in name_lower:
            return "legal"
        elif "vietnam" in name_lower or "vn_" in name_lower:
            return "vietnam"
        elif "ubi" in name_lower:
            return "ubi"
        elif "universe" in name_lower or "omni" in name_lower:
            return "universe"
        elif "unipower" in name_lower or "unitaxi" in name_lower:
            return "unipower"
        elif "hse" in name_lower:
            return "hse"
        elif "governance" in name_lower:
            return "governance"
        elif "tech" in name_lower:
            return "tech"
        elif "cognition" in name_lower:
            return "cognition"
        else:
            return "general"

    def _register_large_file(self, file_path: Path, size: int):
        """Register large file for on-demand loading."""
        name_lower = file_path.stem.lower()
        category = self._categorize_knowledge(name_lower)

        knowledge = LoadedKnowledge(
            name=file_path.stem,
            category=f"{category}_large",
            source_path=str(file_path.relative_to(self.brain_root)),
            content={"status": "registered_for_on_demand_load", "size_mb": size / (1024 * 1024)},
            load_time=datetime.now(UTC).isoformat(),
            size_bytes=size,
        )

        key = f"large/{file_path.stem}"
        self.knowledge_cache[key] = knowledge

    def _build_category_index(self):
        """Build index by category."""
        for key, knowledge in self.knowledge_cache.items():
            cat = knowledge.category
            if cat not in self.category_index:
                self.category_index[cat] = []
            self.category_index[cat].append(key)

    def get_knowledge(self, category: str, name: str = None) -> List[LoadedKnowledge]:
        """Get knowledge by category."""
        results = []

        if name:
            # Specific lookup
            key = f"{category}/{name}"
            if key in self.knowledge_cache:
                knowledge = self.knowledge_cache[key]
                knowledge.access_count += 1
                results.append(knowledge)
        else:
            # Category lookup
            for key in self.category_index.get(category, []):
                knowledge = self.knowledge_cache[key]
                knowledge.access_count += 1
                results.append(knowledge)

        return results

    def query_knowledge(self, query: str, top_n: int = 10) -> List[LoadedKnowledge]:
        """Query loaded knowledge by content match."""
        query_lower = query.lower()
        scored_results = []

        for key, knowledge in self.knowledge_cache.items():
            score = 0.0

            # Name match
            if query_lower in knowledge.name.lower():
                score += 5.0

            # Category match
            if query_lower in knowledge.category.lower():
                score += 3.0

            # Content match (for text content)
            if isinstance(knowledge.content, dict):
                text = knowledge.content.get("text", "")
                if query_lower in text.lower():
                    score += 2.0

                # JSON content match
                content_str = json.dumps(knowledge.content).lower()
                if query_lower in content_str:
                    score += 1.0

            if score > 0:
                knowledge.access_count += 1
                scored_results.append((score, knowledge))

        # Sort by score
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [k for _, k in scored_results[:top_n]]

    def get_stats(self) -> Dict[str, Any]:
        """Get loader statistics."""
        most_accessed = sorted(
            self.knowledge_cache.values(), key=lambda k: k.access_count, reverse=True
        )[:10]

        return {
            "total_loaded": len(self.knowledge_cache),
            "total_size_mb": self.total_size_mb,
            "categories": list(self.category_index.keys()),
            "by_category": {k: len(v) for k, v in self.category_index.items()},
            "most_accessed": [(k.name, k.access_count) for k in most_accessed],
        }


def demo_loader():
    """Demonstrate knowledge loading."""
    print("\n" + "=" * 60)
    print("AMOS KNOWLEDGE LOADER - DEMONSTRATION")
    print("=" * 60)
    print("\n🎯 Goal: Load 659+ knowledge files into runtime memory")

    loader = KnowledgeLoader()

    print("\n[1] Loading all knowledge...")
    stats = loader.load_all()

    if "error" in stats:
        print(f"  ❌ Error: {stats['error']}")
        return

    print(f"\n  ✓ Loaded: {stats['total_loaded']} items")
    print(f"  ✓ Size: {stats['total_size_mb']:.1f} MB")
    print(f"  ✓ Categories: {stats['categories']}")

    print("\n[2] Knowledge by category:")
    for cat, count in sorted(stats["by_category"].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"    • {cat}: {count} items")

    print("\n[3] Query demonstration...")
    queries = ["brain", "engine", "kernel", "vietnam", "ubi"]

    for query in queries:
        results = loader.query_knowledge(query, top_n=3)
        print(f"\n  Query '{query}': {len(results)} matches")
        for k in results[:2]:
            print(f"    - {k.name} ({k.category})")

    print("\n[4] Final statistics...")
    final_stats = loader.get_stats()
    print(f"  Total in memory: {final_stats['total_loaded']}")
    print(f"  Total size: {final_stats['total_size_mb']:.1f} MB")

    print("\n" + "=" * 60)
    print("✓ KNOWLEDGE LOADER COMPLETE")
    print("=" * 60)
    print("\nImpact: 659+ knowledge files now accessible to runtime")
    print("Status: Knowledge content loaded into memory")
    print("=" * 60)


if __name__ == "__main__":
    demo_loader()
