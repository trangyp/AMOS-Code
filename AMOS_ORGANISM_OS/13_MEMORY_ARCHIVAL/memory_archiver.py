"""Memory Archiver — Long-term Memory Archival

Archives memories from short-term to long-term storage,
manages compression, and handles retrieval.

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional


class ArchivePriority(Enum):
    """Priority for archival."""

    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class ArchiveStatus(Enum):
    """Status of archived memory."""

    PENDING = "pending"
    ARCHIVING = "archiving"
    ARCHIVED = "archived"
    RETRIEVING = "retrieving"
    ERROR = "error"


@dataclass
class ArchiveConfig:
    """Configuration for memory archival."""

    compression_enabled: bool = True
    compression_level: int = 6  # 1-9
    encryption_enabled: bool = False
    retention_days: int = 365
    auto_archive_threshold: int = 1000  # memories


@dataclass
class ArchivedMemory:
    """An archived memory record."""

    memory_id: str
    content: dict[str, Any]
    archived_at: datetime
    priority: ArchivePriority
    status: ArchiveStatus
    size_bytes: int
    compressed: bool
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class MemoryArchiver:
    """Manages archival of memories to long-term storage.

    Handles compression, encryption, and retrieval of memories
    from the archival system.
    """

    def __init__(self, config: Optional[ArchiveConfig] = None):
        self.config = config or ArchiveConfig()
        self.archives: dict[str, ArchivedMemory] = {}
        self.pending_queue: list[str] = []

    def queue_for_archive(
        self,
        memory_id: str,
        content: dict[str, Any],
        priority: ArchivePriority = ArchivePriority.NORMAL,
        tags: list[str] = None,
    ) -> bool:
        """Queue a memory for archival."""
        if memory_id in self.archives:
            return False

        archived = ArchivedMemory(
            memory_id=memory_id,
            content=content,
            archived_at=datetime.now(UTC),
            priority=priority,
            status=ArchiveStatus.PENDING,
            size_bytes=self._estimate_size(content),
            compressed=False,
            tags=tags or [],
        )

        self.archives[memory_id] = archived
        self.pending_queue.append(memory_id)
        return True

    def _estimate_size(self, content: dict[str, Any]) -> int:
        """Estimate memory size in bytes."""
        import json

        try:
            return len(json.dumps(content).encode("utf-8"))
        except Exception:
            return 1024  # Default estimate

    def archive(self, memory_id: str) -> bool:
        """Archive a specific memory."""
        if memory_id not in self.archives:
            return False

        archived = self.archives[memory_id]
        archived.status = ArchiveStatus.ARCHIVING

        # Simulate compression
        if self.config.compression_enabled:
            archived.compressed = True
            archived.size_bytes = int(archived.size_bytes * 0.3)  # 70% compression

        archived.status = ArchiveStatus.ARCHIVED
        archived.archived_at = datetime.now(UTC)

        if memory_id in self.pending_queue:
            self.pending_queue.remove(memory_id)

        return True

    def archive_all_pending(self) -> int:
        """Archive all pending memories."""
        count = 0
        for memory_id in list(self.pending_queue):
            if self.archive(memory_id):
                count += 1
        return count

    def retrieve(self, memory_id: str) -> Optional[ArchivedMemory]:
        """Retrieve an archived memory."""
        if memory_id not in self.archives:
            return None

        archived = self.archives[memory_id]
        archived.status = ArchiveStatus.RETRIEVING

        # Simulate decompression
        if archived.compressed:
            archived.compressed = False
            archived.size_bytes = int(archived.size_bytes / 0.3)

        archived.status = ArchiveStatus.ARCHIVED
        return archived

    def delete_archive(self, memory_id: str) -> bool:
        """Delete an archived memory."""
        if memory_id not in self.archives:
            return False

        del self.archives[memory_id]
        if memory_id in self.pending_queue:
            self.pending_queue.remove(memory_id)
        return True

    def get_archives_by_tag(self, tag: str) -> list[ArchivedMemory]:
        """Get all archives with a specific tag."""
        return [a for a in self.archives.values() if tag in a.tags]

    def get_storage_stats(self) -> dict[str, Any]:
        """Get archival storage statistics."""
        total_size = sum(a.size_bytes for a in self.archives.values())
        compressed_size = sum(a.size_bytes for a in self.archives.values() if a.compressed)

        return {
            "total_archives": len(self.archives),
            "pending_count": len(self.pending_queue),
            "total_size_bytes": total_size,
            "compressed_size_bytes": compressed_size,
            "compression_ratio": compressed_size / total_size if total_size > 0 else 0,
        }

    def cleanup_expired(self) -> int:
        """Remove expired archives based on retention policy."""
        cutoff = datetime.now(UTC) - timedelta(days=self.config.retention_days)
        expired = [mid for mid, a in self.archives.items() if a.archived_at < cutoff]

        for memory_id in expired:
            self.delete_archive(memory_id)

        return len(expired)

    def queue_for_archival(self, result: dict[str, Any]) -> bool:
        """Queue a result for archival (alias for queue_for_archive)."""
        memory_id = result.get("id", f"result_{datetime.now(UTC).timestamp()}")
        return self.queue_for_archive(
            memory_id=memory_id,
            content=result,
            priority=ArchivePriority.NORMAL,
            tags=["cycle_result"],
        )

    def process_queue(self) -> int:
        """Process all pending archival items (alias for archive_all_pending)."""
        return self.archive_all_pending()


if __name__ == "__main__":
    print("Memory Archiver Module")
    print("=" * 50)

    archiver = MemoryArchiver()

    # Queue some memories
    archiver.queue_for_archive("mem_001", {"data": "test memory 1"}, tags=["test"])
    archiver.queue_for_archive("mem_002", {"data": "test memory 2"}, tags=["test"])

    print(f"Queued: {len(archiver.pending_queue)} memories")

    # Archive all
    archived = archiver.archive_all_pending()
    print(f"Archived: {archived} memories")

    stats = archiver.get_storage_stats()
    print(f"Total archives: {stats['total_archives']}")

    print("Memory Archiver ready")
