"""Storage Manager — Storage Backend Management

Manages storage backends, capacity monitoring, and storage
optimization for memory archival.

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class StorageType(Enum):
    """Types of storage backends."""

    LOCAL_DISK = "local_disk"
    NETWORK = "network"
    CLOUD = "cloud"
    MEMORY = "memory"
    TAPE = "tape"


class StorageStatus(Enum):
    """Status of storage backend."""

    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    FULL = "full"


@dataclass
class StorageMetrics:
    """Metrics for storage backend."""

    total_capacity_bytes: int
    used_bytes: int
    free_bytes: int
    read_ops_per_sec: float
    write_ops_per_sec: float
    latency_ms: float


@dataclass
class StorageBackend:
    """Storage backend definition."""

    backend_id: str
    name: str
    storage_type: StorageType
    path: str
    status: StorageStatus
    metrics: StorageMetrics
    created_at: datetime
    config: dict[str, Any] = field(default_factory=dict)


class StorageManager:
    """Manages storage backends for memory archival.

    Monitors capacity, handles backend selection, and
    optimizes storage utilization.
    """

    def __init__(self):
        self.backends: dict[str, StorageBackend] = {}
        self.default_backend_id: str = None

    def register_backend(self, backend: StorageBackend) -> bool:
        """Register a new storage backend."""
        if backend.backend_id in self.backends:
            return False

        self.backends[backend.backend_id] = backend

        # Set as default if first backend
        if self.default_backend_id is None:
            self.default_backend_id = backend.backend_id

        return True

    def create_backend(
        self,
        name: str,
        storage_type: StorageType,
        path: str,
        capacity_bytes: int,
        config: dict[str, Any] = None,
    ) -> StorageBackend:
        """Create and register a new storage backend."""
        backend_id = f"storage_{len(self.backends) + 1}"

        metrics = StorageMetrics(
            total_capacity_bytes=capacity_bytes,
            used_bytes=0,
            free_bytes=capacity_bytes,
            read_ops_per_sec=0.0,
            write_ops_per_sec=0.0,
            latency_ms=0.0,
        )

        backend = StorageBackend(
            backend_id=backend_id,
            name=name,
            storage_type=storage_type,
            path=path,
            status=StorageStatus.ONLINE,
            metrics=metrics,
            created_at=datetime.now(UTC),
            config=config or {},
        )

        self.register_backend(backend)
        return backend

    def get_backend(self, backend_id: str) -> Optional[StorageBackend]:
        """Get a storage backend by ID."""
        return self.backends.get(backend_id)

    def get_default_backend(self) -> Optional[StorageBackend]:
        """Get the default storage backend."""
        if self.default_backend_id:
            return self.backends.get(self.default_backend_id)
        return None

    def set_default_backend(self, backend_id: str) -> bool:
        """Set the default storage backend."""
        if backend_id not in self.backends:
            return False
        self.default_backend_id = backend_id
        return True

    def update_metrics(
        self, backend_id: str, used_bytes: int, read_ops: float, write_ops: float, latency_ms: float
    ) -> bool:
        """Update storage backend metrics."""
        if backend_id not in self.backends:
            return False

        backend = self.backends[backend_id]
        backend.metrics.used_bytes = used_bytes
        backend.metrics.free_bytes = backend.metrics.total_capacity_bytes - used_bytes
        backend.metrics.read_ops_per_sec = read_ops
        backend.metrics.write_ops_per_sec = write_ops
        backend.metrics.latency_ms = latency_ms

        # Update status based on capacity
        usage_ratio = used_bytes / backend.metrics.total_capacity_bytes
        if usage_ratio >= 0.95:
            backend.status = StorageStatus.FULL
        elif usage_ratio >= 0.85:
            backend.status = StorageStatus.DEGRADED

        return True

    def list_backends(self, status_filter: Optional[StorageStatus] = None) -> list[StorageBackend]:
        """List all storage backends, optionally filtered by status."""
        backends = list(self.backends.values())
        if status_filter:
            backends = [b for b in backends if b.status == status_filter]
        return backends

    def get_available_backends(self) -> list[StorageBackend]:
        """Get all online backends with available space."""
        return [
            b
            for b in self.backends.values()
            if b.status == StorageStatus.ONLINE and b.metrics.free_bytes > 0
        ]

    def select_backend_for_write(self, size_bytes: int) -> Optional[StorageBackend]:
        """Select best backend for writing data."""
        available = self.get_available_backends()

        # Filter by capacity
        suitable = [b for b in available if b.metrics.free_bytes >= size_bytes]

        if not suitable:
            return None

        # Select by lowest latency
        return min(suitable, key=lambda b: b.metrics.latency_ms)

    def get_total_capacity(self) -> dict[str, int]:
        """Get total capacity across all backends."""
        total = sum(b.metrics.total_capacity_bytes for b in self.backends.values())
        used = sum(b.metrics.used_bytes for b in self.backends.values())
        free = sum(b.metrics.free_bytes for b in self.backends.values())

        return {
            "total_bytes": total,
            "used_bytes": used,
            "free_bytes": free,
            "usage_percent": (used / total * 100) if total > 0 else 0,
        }

    def remove_backend(self, backend_id: str) -> bool:
        """Remove a storage backend."""
        if backend_id not in self.backends:
            return False

        del self.backends[backend_id]

        # Update default if needed
        if self.default_backend_id == backend_id:
            if self.backends:
                self.default_backend_id = next(iter(self.backends.keys()))
            else:
                self.default_backend_id = None

        return True


if __name__ == "__main__":
    print("Storage Manager Module")
    print("=" * 50)

    manager = StorageManager()

    # Create backends
    backend1 = manager.create_backend(
        "Local Storage",
        StorageType.LOCAL_DISK,
        "/var/amos/storage",
        100 * 1024 * 1024 * 1024,  # 100 GB
    )
    print(f"Created: {backend1.name}")

    backend2 = manager.create_backend(
        "Cloud Archive",
        StorageType.CLOUD,
        "s3://amos-archive",
        1024 * 1024 * 1024 * 1024,  # 1 TB
    )
    print(f"Created: {backend2.name}")

    capacity = manager.get_total_capacity()
    print(f"\nTotal capacity: {capacity['total_bytes'] / (1024**3):.1f} GB")
    print(f"Usage: {capacity['usage_percent']:.1f}%")

    print("Storage Manager ready")
