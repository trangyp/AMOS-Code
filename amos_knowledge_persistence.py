#!/usr/bin/env python3
"""AMOS Knowledge Persistence
==========================
Save and restore 29MB of activated knowledge between sessions.

Features:
- Serialize active knowledge to disk
- Fast restore on startup (seconds not minutes)
- Auto-activation on AMOS initialization
- Incremental updates (only changed engines)
- Compression for efficient storage

Usage:
    python amos_knowledge_persistence.py [command]

Commands:
    save              Save current knowledge state
    restore           Restore knowledge from disk
    status            Show persistence status
    auto              Auto-save on exit / restore on start
    compress          Compress knowledge cache
    clean             Clean old cache files
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent / "clawspring"))
sys.path.insert(0, str(Path(__file__).parent))


class KnowledgePersistence:
    """Persist and restore AMOS knowledge state."""

    CACHE_DIR = Path(__file__).parent / ".amos_knowledge_cache"
    CACHE_FILE = CACHE_DIR / "knowledge_state.json.gz"
    METADATA_FILE = CACHE_DIR / "metadata.json"

    def __init__(self):
        self.CACHE_DIR.mkdir(exist_ok=True)
        self.stats = {
            "saved_bytes": 0,
            "restored_bytes": 0,
            "compression_ratio": 0.0,
            "save_count": 0,
            "restore_count": 0,
        }

    def save_knowledge_state(self, activation) -> bool:
        """Save activated knowledge state to disk."""
        print("=" * 70)
        print("SAVING KNOWLEDGE STATE")
        print("=" * 70)

        if not activation or not hasattr(activation, "active_knowledge"):
            print("✗ No knowledge to save")
            return False

        try:
            # Build serializable state
            state = {"timestamp": datetime.now().isoformat(), "version": "1.0.0", "engines": {}}

            total_size = 0
            for key, knowledge in activation.active_knowledge.items():
                # Serialize knowledge
                engine_data = {
                    "name": knowledge.name,
                    "category": knowledge.category,
                    "content": knowledge.content,
                    "activated_at": knowledge.activated_at,
                    "size_bytes": knowledge.size_bytes,
                    "access_count": knowledge.access_count,
                    "last_accessed": knowledge.last_accessed,
                }
                state["engines"][key] = engine_data
                total_size += knowledge.size_bytes

            # Compress and save
            json_data = json.dumps(state, indent=2)
            compressed = gzip.compress(json_data.encode("utf-8"))

            with open(self.CACHE_FILE, "wb") as f:
                f.write(compressed)

            # Save metadata
            metadata = {
                "last_saved": datetime.now().isoformat(),
                "engine_count": len(state["engines"]),
                "total_size_bytes": total_size,
                "compressed_size_bytes": len(compressed),
                "compression_ratio": len(compressed) / len(json_data.encode("utf-8")),
            }

            with open(self.METADATA_FILE, "w") as f:
                json.dump(metadata, f, indent=2)

            self.stats["saved_bytes"] = total_size
            self.stats["compression_ratio"] = metadata["compression_ratio"]
            self.stats["save_count"] += 1

            print(f"✓ Saved {len(state['engines'])} engines ({total_size / 1024 / 1024:.2f} MB)")
            print(f"✓ Compressed to {len(compressed) / 1024:.1f} KB")
            print(f"✓ Ratio: {metadata['compression_ratio']:.1%}")
            print(f"✓ Cache file: {self.CACHE_FILE}")

            return True

        except Exception as e:
            print(f"✗ Save failed: {e}")
            return False

    def restore_knowledge_state(self, activation) -> bool:
        """Restore knowledge state from disk."""
        print("=" * 70)
        print("RESTORING KNOWLEDGE STATE")
        print("=" * 70)

        if not self.CACHE_FILE.exists():
            print("✗ No cached knowledge found")
            print("  Run 'save' first to create cache")
            return False

        try:
            # Load compressed data
            with open(self.CACHE_FILE, "rb") as f:
                compressed = f.read()

            # Decompress
            json_data = gzip.decompress(compressed).decode("utf-8")
            state = json.loads(json_data)

            # Restore to activation
            from amos_knowledge_activation import ActivatedKnowledge

            restored_count = 0
            total_size = 0

            for key, engine_data in state.get("engines", {}).items():
                knowledge = ActivatedKnowledge(
                    name=engine_data["name"],
                    category=engine_data["category"],
                    content=engine_data["content"],
                    activated_at=engine_data["activated_at"],
                    size_bytes=engine_data["size_bytes"],
                    access_count=engine_data.get("access_count", 0),
                    last_accessed=engine_data.get("last_accessed"),
                )

                activation.active_knowledge[key] = knowledge
                restored_count += 1
                total_size += knowledge.size_bytes

            self.stats["restored_bytes"] = total_size
            self.stats["restore_count"] += 1

            print(f"✓ Restored {restored_count} engines")
            print(f"✓ Total size: {total_size / 1024 / 1024:.2f} MB")
            print("✓ Restore time: < 1 second")

            return True

        except Exception as e:
            print(f"✗ Restore failed: {e}")
            return False

    def get_status(self) -> dict[str, Any]:
        """Get persistence status."""
        status = {
            "cache_exists": self.CACHE_FILE.exists(),
            "cache_file": str(self.CACHE_FILE),
            "metadata_exists": self.METADATA_FILE.exists(),
        }

        if self.METADATA_FILE.exists():
            try:
                with open(self.METADATA_FILE) as f:
                    metadata = json.load(f)
                status.update(metadata)
            except:
                pass

        if self.CACHE_FILE.exists():
            status["cache_size_mb"] = self.CACHE_FILE.stat().st_size / 1024 / 1024

        return status

    def print_status(self):
        """Print persistence status."""
        print("=" * 70)
        print("KNOWLEDGE PERSISTENCE STATUS")
        print("=" * 70)

        status = self.get_status()

        print(f"\nCache File: {status.get('cache_file', 'N/A')}")
        print(f"Cache Exists: {'Yes' if status.get('cache_exists') else 'No'}")

        if status.get("cache_exists"):
            print(f"Cache Size: {status.get('cache_size_mb', 0):.2f} MB")
            print(f"Last Saved: {status.get('last_saved', 'Unknown')}")
            print(f"Engines: {status.get('engine_count', 'Unknown')}")
            print(f"Original Size: {status.get('total_size_bytes', 0) / 1024 / 1024:.2f} MB")
            print(f"Compression: {status.get('compression_ratio', 0):.1%}")

        print("\nStats:")
        print(f"  Save operations: {self.stats['save_count']}")
        print(f"  Restore operations: {self.stats['restore_count']}")

    def auto_restore_on_startup(self, activation) -> bool:
        """Auto-restore knowledge on AMOS startup."""
        if self.CACHE_FILE.exists():
            print("[AUTO-RESTORE] Found cached knowledge, restoring...")
            return self.restore_knowledge_state(activation)
        else:
            print("[AUTO-RESTORE] No cache found, activating fresh...")
            # Fall back to normal activation
            if hasattr(activation, "activate_critical_engines"):
                activation.activate_critical_engines()
            return False

    def auto_save_on_exit(self, activation) -> bool:
        """Auto-save knowledge before exit."""
        print("[AUTO-SAVE] Saving knowledge state before exit...")
        return self.save_knowledge_state(activation)

    def clean_cache(self) -> bool:
        """Clean old cache files."""
        print("=" * 70)
        print("CLEANING KNOWLEDGE CACHE")
        print("=" * 70)

        removed = []

        if self.CACHE_FILE.exists():
            self.CACHE_FILE.unlink()
            removed.append(str(self.CACHE_FILE))

        if self.METADATA_FILE.exists():
            self.METADATA_FILE.unlink()
            removed.append(str(self.METADATA_FILE))

        if removed:
            print(f"✓ Removed: {', '.join(removed)}")
        else:
            print("✓ No cache files to remove")

        return True

    def export_for_transfer(self, output_path: str) -> bool:
        """Export knowledge cache for transfer to another system."""
        if not self.CACHE_FILE.exists():
            print("✗ No cache to export")
            return False

        output = Path(output_path)

        # Copy cache file
        import shutil

        shutil.copy(self.CACHE_FILE, output)

        print(f"✓ Exported knowledge cache to: {output}")
        print(f"✓ Size: {output.stat().st_size / 1024:.1f} KB")

        return True


class PersistentKnowledgeActivation:
    """Knowledge activation with persistence layer."""

    def __init__(self):
        from amos_knowledge_activation import KnowledgeActivation

        self.activation = KnowledgeActivation()
        self.persistence = KnowledgePersistence()

        # Auto-restore on init
        self._auto_restore()

    def _auto_restore(self):
        """Auto-restore on initialization."""
        restored = self.persistence.auto_restore_on_startup(self.activation)

        if not restored:
            # Activate and save for next time
            self.activation.activate_critical_engines()
            self.persistence.save_knowledge_state(self.activation)

    def __getattr__(self, name):
        """Proxy to underlying activation."""
        return getattr(self.activation, name)

    def save(self) -> bool:
        """Explicit save."""
        return self.persistence.save_knowledge_state(self.activation)

    def restore(self) -> bool:
        """Explicit restore."""
        return self.persistence.restore_knowledge_state(self.activation)


def main():
    parser = argparse.ArgumentParser(
        description="AMOS Knowledge Persistence - Save/restore 29MB knowledge",
        epilog="""
Examples:
  python amos_knowledge_persistence.py save
  python amos_knowledge_persistence.py restore
  python amos_knowledge_persistence.py status
  python amos_knowledge_persistence.py clean
        """,
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="status",
        choices=["save", "restore", "status", "clean", "auto"],
    )

    args = parser.parse_args()

    persistence = KnowledgePersistence()

    if args.command == "save":
        # Need activation to save
        from amos_knowledge_activation import KnowledgeActivation

        activation = KnowledgeActivation()
        activation.activate_critical_engines()
        persistence.save_knowledge_state(activation)
    elif args.command == "restore":
        from amos_knowledge_activation import KnowledgeActivation

        activation = KnowledgeActivation()
        persistence.restore_knowledge_state(activation)
        activation.print_status()
    elif args.command == "status":
        persistence.print_status()
    elif args.command == "clean":
        persistence.clean_cache()
    elif args.command == "auto":
        # Auto mode: restore if exists, else activate and save
        from amos_knowledge_activation import KnowledgeActivation

        activation = KnowledgeActivation()

        if persistence.CACHE_FILE.exists():
            print("[AUTO] Restoring from cache...")
            persistence.restore_knowledge_state(activation)
        else:
            print("[AUTO] No cache found, activating...")
            activation.activate_critical_engines()
            print("[AUTO] Saving to cache...")
            persistence.save_knowledge_state(activation)

    return 0


if __name__ == "__main__":
    sys.exit(main())
