"""Resource Engine — Core resource tracking and allocation

Manages the "blood" of the organism - computational resources, tokens,
time budgets, and financial allocations.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ResourceType(Enum):
    """Types of resources in the system."""

    COMPUTATIONAL = "computational"  # CPU, memory, storage
    FINANCIAL = "financial"  # Money, credits
    TEMPORAL = "temporal"  # Time, cycles
    COGNITIVE = "cognitive"  # Token budgets, API calls
    HUMAN = "human"  # Operator attention, approval capacity


@dataclass
class ResourceAllocation:
    """A single resource allocation record."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    resource_type: ResourceType = ResourceType.COMPUTATIONAL
    amount: float = 0.0
    unit: str = "units"
    allocated_to: str = ""  # Subsystem or task
    purpose: str = ""
    allocated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    expires_at: Optional[str] = None
    returned: bool = False
    returned_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "resource_type": self.resource_type.value,
        }


@dataclass
class ResourcePool:
    """A pool of available resources."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    resource_type: ResourceType = ResourceType.COMPUTATIONAL
    total_capacity: float = 0.0
    allocated: float = 0.0
    unit: str = "units"
    min_reserve: float = 0.1  # 10% minimum reserve
    allocations: List[ResourceAllocation] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def available(self) -> float:
        """Calculate available resources (minus reserve)."""
        reserve_amount = self.total_capacity * self.min_reserve
        return max(0, self.total_capacity - self.allocated - reserve_amount)

    @property
    def utilization_rate(self) -> float:
        """Calculate utilization percentage."""
        if self.total_capacity == 0:
            return 0.0
        return self.allocated / self.total_capacity

    def allocate(
        self,
        amount: float,
        allocated_to: str,
        purpose: str = "",
        duration_hours: Optional[int] = None,
    ) -> Optional[ResourceAllocation]:
        """Allocate resources from this pool."""
        if amount > self.available:
            return None

        expires = None
        if duration_hours:
            expires = (datetime.now(UTC) + timedelta(hours=duration_hours)).isoformat()

        allocation = ResourceAllocation(
            resource_type=self.resource_type,
            amount=amount,
            unit=self.unit,
            allocated_to=allocated_to,
            purpose=purpose,
            expires_at=expires,
        )

        self.allocations.append(allocation)
        self.allocated += amount

        return allocation

    def release(self, allocation_id: str) -> bool:
        """Release an allocation back to the pool."""
        for alloc in self.allocations:
            if alloc.id == allocation_id and not alloc.returned:
                alloc.returned = True
                alloc.returned_at = datetime.now(UTC).isoformat()
                self.allocated -= alloc.amount
                return True
        return False

    def cleanup_expired(self) -> int:
        """Release expired allocations. Returns count cleaned."""
        now = datetime.now(UTC).isoformat()
        cleaned = 0

        for alloc in self.allocations:
            if not alloc.returned and alloc.expires_at and alloc.expires_at < now:
                self.release(alloc.id)
                cleaned += 1

        return cleaned

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "resource_type": self.resource_type.value,
            "available": self.available,
            "utilization_rate": self.utilization_rate,
        }


class ResourceEngine:
    """Central resource management for the AMOS organism.

    Tracks all resource pools, handles allocation requests,
    monitors utilization, and enforces limits.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.pools: Dict[str, ResourcePool] = {}
        self._load_pools()

        # Initialize default pools if none exist
        if not self.pools:
            self._init_default_pools()

    def _init_default_pools(self):
        """Create default resource pools for the organism."""
        defaults = [
            ResourcePool(
                name="computational_budget",
                resource_type=ResourceType.COMPUTATIONAL,
                total_capacity=100.0,
                unit="compute_units",
            ),
            ResourcePool(
                name="token_budget",
                resource_type=ResourceType.COGNITIVE,
                total_capacity=1000000,  # 1M tokens
                unit="tokens",
            ),
            ResourcePool(
                name="operator_attention",
                resource_type=ResourceType.HUMAN,
                total_capacity=8.0,  # 8 hours
                unit="hours",
                min_reserve=0.2,  # 20% reserve
            ),
        ]

        for pool in defaults:
            self.pools[pool.name] = pool

    def _load_pools(self):
        """Load resource pools from disk."""
        pools_file = self.data_dir / "resource_pools.json"
        if pools_file.exists():
            try:
                data = json.loads(pools_file.read_text())
                for pool_data in data.get("pools", []):
                    pool = ResourcePool(
                        id=pool_data["id"],
                        name=pool_data["name"],
                        resource_type=ResourceType(pool_data["resource_type"]),
                        total_capacity=pool_data["total_capacity"],
                        allocated=pool_data["allocated"],
                        unit=pool_data["unit"],
                        min_reserve=pool_data["min_reserve"],
                        created_at=pool_data["created_at"],
                    )
                    # Restore allocations
                    for alloc_data in pool_data.get("allocations", []):
                        alloc = ResourceAllocation(
                            id=alloc_data["id"],
                            resource_type=ResourceType(alloc_data["resource_type"]),
                            amount=alloc_data["amount"],
                            unit=alloc_data["unit"],
                            allocated_to=alloc_data["allocated_to"],
                            purpose=alloc_data["purpose"],
                            allocated_at=alloc_data["allocated_at"],
                            expires_at=alloc_data.get("expires_at"),
                            returned=alloc_data["returned"],
                            returned_at=alloc_data.get("returned_at"),
                        )
                        pool.allocations.append(alloc)
                    self.pools[pool.name] = pool
            except Exception as e:
                print(f"[RESOURCE] Error loading pools: {e}")

    def save(self):
        """Save resource pools to disk."""
        pools_file = self.data_dir / "resource_pools.json"
        data = {
            "saved_at": datetime.now(UTC).isoformat(),
            "pools": [pool.to_dict() for pool in self.pools.values()],
        }
        pools_file.write_text(json.dumps(data, indent=2))

    def get_pool(self, name: str) -> Optional[ResourcePool]:
        """Get a resource pool by name."""
        return self.pools.get(name)

    def allocate(
        self,
        pool_name: str,
        amount: float,
        allocated_to: str,
        purpose: str = "",
        duration_hours: Optional[int] = None,
    ) -> Optional[ResourceAllocation]:
        """Allocate resources from a specific pool."""
        pool = self.pools.get(pool_name)
        if not pool:
            return None

        allocation = pool.allocate(amount, allocated_to, purpose, duration_hours)
        if allocation:
            self.save()
        return allocation

    def release(self, pool_name: str, allocation_id: str) -> bool:
        """Release an allocation back to a pool."""
        pool = self.pools.get(pool_name)
        if not pool:
            return False

        result = pool.release(allocation_id)
        if result:
            self.save()
        return result

    def cleanup(self) -> Dict[str, int]:
        """Cleanup expired allocations across all pools."""
        results = {}
        for name, pool in self.pools.items():
            cleaned = pool.cleanup_expired()
            if cleaned > 0:
                results[name] = cleaned
        if results:
            self.save()
        return results

    def get_status(self) -> Dict[str, Any]:
        """Get overall resource status."""
        return {
            "pools_count": len(self.pools),
            "pools": {
                name: {
                    "available": pool.available,
                    "allocated": pool.allocated,
                    "total": pool.total_capacity,
                    "utilization": pool.utilization_rate,
                }
                for name, pool in self.pools.items()
            },
            "last_saved": datetime.now(UTC).isoformat(),
        }

    def create_pool(
        self,
        name: str,
        resource_type: ResourceType,
        capacity: float,
        unit: str = "units",
        min_reserve: float = 0.1,
    ) -> ResourcePool:
        """Create a new resource pool."""
        pool = ResourcePool(
            name=name,
            resource_type=resource_type,
            total_capacity=capacity,
            unit=unit,
            min_reserve=min_reserve,
        )
        self.pools[name] = pool
        self.save()
        return pool


# Global instance
_ENGINE: Optional[ResourceEngine] = None


def get_resource_engine(data_dir: Optional[Path] = None) -> ResourceEngine:
    """Get or create global resource engine."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = ResourceEngine(data_dir)
    return _ENGINE


if __name__ == "__main__":
    print("Resource Engine (04_BLOOD)")
    print("=" * 40)

    engine = get_resource_engine()

    print("\nResource Pools:")
    status = engine.get_status()
    for name, info in status["pools"].items():
        print(f"  {name}:")
        print(f"    Available: {info['available']:.2f}")
        print(f"    Utilization: {info['utilization']:.1%}")

    # Test allocation
    print("\nTest allocation:")
    alloc = engine.allocate(
        "computational_budget",
        10.0,
        "test_task",
        "Testing resource allocation",
        duration_hours=1,
    )
    if alloc:
        print(f"  Allocated: {alloc.amount} {alloc.unit}")
        print(f"  ID: {alloc.id}")

    print("\nUpdated status:")
    status = engine.get_status()
    for name, info in status["pools"].items():
        print(f"  {name}: {info['allocated']:.2f} / {info['total']:.2f}")
