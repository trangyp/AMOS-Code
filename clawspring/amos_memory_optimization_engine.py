"""AMOS Memory Optimization Engine - Advanced memory management and caching."""

import time
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class CacheStrategy(Enum):
    """Cache replacement strategies."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    ARC = "arc"  # Adaptive Replacement Cache


class MemoryTier(Enum):
    """Memory hierarchy tiers."""
    L1_CACHE = "l1"  # CPU cache
    L2_CACHE = "l2"
    RAM = "ram"
    SSD = "ssd"
    DISK = "disk"


@dataclass
class CacheEntry:
    """Represents a cached item."""

    key: str
    value: Any
    size: int
    access_count: int = 1
    last_access: float = field(default_factory=time.time)
    created_at: float = field(default_factory=time.time)


class LRUCache:
    """Least Recently Used cache implementation."""

    def __init__(self, capacity: int, max_size_bytes: int = 100 * 1024 * 1024):
        self.capacity = capacity
        self.max_size_bytes = max_size_bytes
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.current_size = 0
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        if key in self.cache:
            entry = self.cache.pop(key)
            entry.last_access = time.time()
            entry.access_count += 1
            self.cache[key] = entry
            self.hits += 1
            return entry.value
        self.misses += 1
        return None

    def put(self, key: str, value: Any, size: int = 1024) -> bool:
        """Add item to cache."""
        if size > self.max_size_bytes:
            return False
        # Evict entries if needed
        while self.current_size + size > self.max_size_bytes or len(self.cache) >= self.capacity:
            if not self.cache:
                break
            evicted = self.cache.popitem(last=False)
            self.current_size -= evicted[1].size
        entry = CacheEntry(key, value, size)
        if key in self.cache:
            self.current_size -= self.cache[key].size
        self.cache[key] = entry
        self.current_size += size
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        return {
            "size": len(self.cache),
            "current_bytes": self.current_size,
            "max_bytes": self.max_size_bytes,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 3),
        }


class LFUCache:
    """Least Frequently Used cache implementation."""

    def __init__(self, capacity: int, max_size_bytes: int = 100 * 1024 * 1024):
        self.capacity = capacity
        self.max_size_bytes = max_size_bytes
        self.cache: Dict[str, CacheEntry] = {}
        self.current_size = 0
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        if key in self.cache:
            entry = self.cache[key]
            entry.access_count += 1
            entry.last_access = time.time()
            self.hits += 1
            return entry.value
        self.misses += 1
        return None

    def put(self, key: str, value: Any, size: int = 1024) -> bool:
        """Add item to cache."""
        if size > self.max_size_bytes:
            return False
        # Evict by lowest frequency
        while self.current_size + size > self.max_size_bytes or len(self.cache) >= self.capacity:
            if not self.cache:
                break
            lfu_key = min(self.cache.keys(), key=lambda k: self.cache[k].access_count)
            self.current_size -= self.cache[lfu_key].size
            del self.cache[lfu_key]
        entry = CacheEntry(key, value, size)
        if key in self.cache:
            self.current_size -= self.cache[key].size
            entry.access_count = self.cache[key].access_count + 1
        self.cache[key] = entry
        self.current_size += size
        return True

    def get_stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        return {
            "size": len(self.cache),
            "current_bytes": self.current_size,
            "max_bytes": self.max_size_bytes,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 3),
        }


class WorkingSetManager:
    """Manages working set of active memory pages."""

    def __init__(self, max_working_set: int = 1000):
        self.max_working_set = max_working_set
        self.working_set: Set[str] = set()
        self.access_history: List[tuple[str, float]] = []

    def access_page(self, page_id: str) -> bool:
        """Record page access."""
        timestamp = time.time()
        self.access_history.append((page_id, timestamp))
        # Trim old accesses (older than 30 seconds)
        cutoff = timestamp - 30
        self.access_history = [(p, t) for p, t in self.access_history if t > cutoff]
        # Update working set
        page_counts: Dict[str, int] = {}
        for p, _ in self.access_history:
            page_counts[p] = page_counts.get(p, 0) + 1
        # Keep top pages by frequency
        sorted_pages = sorted(page_counts.items(), key=lambda x: x[1], reverse=True)
        self.working_set = set(p for p, _ in sorted_pages[: self.max_working_set])
        return page_id in self.working_set

    def get_working_set_size(self) -> int:
        return len(self.working_set)

    def is_in_working_set(self, page_id: str) -> bool:
        return page_id in self.working_set


class TieredStorageManager:
    """Manages multi-tier storage hierarchy."""

    TIER_LATENCIES = {
        "l1": 1e-9,  # 1 ns
        "l2": 4e-9,  # 4 ns
        "ram": 100e-9,  # 100 ns
        "ssd": 100e-6,  # 100 us
        "disk": 10e-3,  # 10 ms
    }

    TIER_CAPACITIES = {
        "l1": 32 * 1024,  # 32 KB
        "l2": 256 * 1024,  # 256 KB
        "ram": 16 * 1024 * 1024 * 1024,  # 16 GB
        "ssd": 512 * 1024 * 1024 * 1024,  # 512 GB
        "disk": 2 * 1024 * 1024 * 1024 * 1024,  # 2 TB
    }

    def __init__(self):
        self.data_locations: Dict[str, str] = {}  # key -> tier
        self.tier_usage: Dict[str, int] = {tier: 0 for tier in self.TIER_CAPACITIES}

    def place_data(self, key: str, size: int, access_frequency: float) -> str:
        """Determine optimal tier for data."""
        if access_frequency > 1000:  # Very hot
            tier = "ram"
        elif access_frequency > 100:  # Hot
            tier = "ssd"
        else:  # Cold
            tier = "disk"
        # Check capacity
        if self.tier_usage[tier] + size > self.TIER_CAPACITIES[tier]:
            tier = self._find_space(size, tier)
        self.data_locations[key] = tier
        self.tier_usage[tier] += size
        return tier

    def _find_space(self, size: int, preferred: str) -> str:
        """Find tier with available space."""
        tiers = ["ram", "ssd", "disk"]
        if preferred in tiers:
            tiers.remove(preferred)
            tiers.insert(0, preferred)
        for tier in tiers:
            if self.tier_usage[tier] + size <= self.TIER_CAPACITIES[tier]:
                return tier
        return "disk"  # Default to disk

    def get_access_latency(self, key: str) -> float:
        """Get access latency for data."""
        tier = self.data_locations.get(key, "disk")
        return self.TIER_LATENCIES.get(tier, 10e-3)

    def get_tier_stats(self) -> Dict[str, Any]:
        """Get tier utilization statistics."""
        stats = {}
        for tier, capacity in self.TIER_CAPACITIES.items():
            usage = self.tier_usage[tier]
            stats[tier] = {
                "capacity": capacity,
                "used": usage,
                "free": capacity - usage,
                "utilization": round(usage / capacity, 3) if capacity > 0 else 0,
            }
        return stats


class PrefetchEngine:
    """Predicts and prefetches likely-needed data."""

    def __init__(self):
        self.access_patterns: Dict[str, list[str]] = {}
        self.prediction_cache: Dict[str, list[str]] = {}

    def record_access(self, key: str) -> None:
        """Record data access for pattern analysis."""
        timestamp = time.time()
        # Simple sequential detection
        for prev_key, accesses in list(self.access_patterns.items()):
            if accesses and accesses[-1] == key:
                continue
            if len(accesses) >= 2:
                # Detect sequential pattern
                if self._is_sequential(accesses[-3:] + [key]):
                    self.prediction_cache[prev_key] = [key]
        if key not in self.access_patterns:
            self.access_patterns[key] = []
        self.access_patterns[key].append(key)
        # Limit history
        self.access_patterns[key] = self.access_patterns[key][-10:]

    def _is_sequential(self, keys: List[str]) -> bool:
        """Check if keys follow sequential pattern."""
        if len(keys) < 2:
            return False
        try:
            nums = [int(k.split("_")[-1]) for k in keys if "_" in k]
            if len(nums) == len(keys):
                diffs = [nums[i + 1] - nums[i] for i in range(len(nums) - 1)]
                return len(set(diffs)) == 1
        except (ValueError, IndexError):
            pass
        return False

    def predict_next(self, current_key: str) -> List[str]:
        """Predict likely next accesses."""
        return self.prediction_cache.get(current_key, [])

    def get_prefetch_candidates(self, recent_accesses: List[str]) -> List[str]:
        """Get candidates for prefetching."""
        candidates = []
        for key in recent_accesses[-3:]:
            predicted = self.predict_next(key)
            candidates.extend(predicted)
        return list(set(candidates))  # Remove duplicates


class MemoryOptimizationEngine:
    """AMOS Memory Optimization Engine - Advanced memory management."""

    VERSION = "vInfinity_Memory_1.0.0"
    NAME = "AMOS_Memory_Optimization_OMEGA"

    def __init__(self):
        self.lru_cache = LRUCache(1000, 50 * 1024 * 1024)
        self.lfu_cache = LFUCache(500, 25 * 1024 * 1024)
        self.working_set = WorkingSetManager(500)
        self.tiered_storage = TieredStorageManager()
        self.prefetcher = PrefetchEngine()

    def analyze(
        self, scenario: str, context: Dict[str, Any]  = None
    ) -> Dict[str, Any]:
        """Run memory optimization analysis."""
        context = context or {}
        scenario_lower = scenario.lower()
        results: Dict[str, Any] = {
            "scenario": scenario[:100],
            "memory_strategy": self._detect_strategy(scenario_lower),
            "cache_stats": {},
            "working_set": {},
            "tiered_storage": {},
            "prefetch": {},
        }
        # Simulate cache operations
        if "cache" in scenario_lower or "lru" in scenario_lower:
            self._simulate_cache_operations(self.lru_cache, "lru")
            results["cache_stats"]["lru"] = self.lru_cache.get_stats()
        if "lfu" in scenario_lower or "frequency" in scenario_lower:
            self._simulate_cache_operations(self.lfu_cache, "lfu")
            results["cache_stats"]["lfu"] = self.lfu_cache.get_stats()
        # Working set analysis
        if "working" in scenario_lower or "active" in scenario_lower:
            self._simulate_working_set()
            results["working_set"] = {
                "size": self.working_set.get_working_set_size(),
                "max_size": self.working_set.max_working_set,
            }
        # Tiered storage analysis
        if "tier" in scenario_lower or "storage" in scenario_lower or "ssd" in scenario_lower:
            self._simulate_tiered_storage()
            results["tiered_storage"] = self.tiered_storage.get_tier_stats()
        # Prefetch analysis
        if "prefetch" in scenario_lower or "prediction" in scenario_lower:
            self._simulate_prefetch()
            candidates = self.prefetcher.get_prefetch_candidates(["data_1", "data_2", "data_3"])
            results["prefetch"] = {
                "candidates": candidates,
                "patterns_tracked": len(self.prefetcher.access_patterns),
            }
        return results

    def _detect_strategy(self, scenario: str) -> str:
        """Detect memory optimization strategy."""
        if "lru" in scenario:
            return "lru"
        elif "lfu" in scenario:
            return "lfu"
        elif "working" in scenario:
            return "working_set"
        elif "tier" in scenario:
            return "tiered_storage"
        elif "prefetch" in scenario:
            return "prefetching"
        elif "arc" in scenario:
            return "adaptive_replacement"
        else:
            return "general"

    def _simulate_cache_operations(self, cache, cache_type: str) -> None:
        """Simulate cache access patterns."""
        # Simulate sequential access
        for i in range(200):
            key = f"data_{i % 150}"
            value = f"value_{i}"
            if cache.get(key) is None:
                cache.put(key, value, 1024)
        # Simulate hot data
        for i in range(50):
            key = "hot_data_1"
            cache.get(key)
            if i == 0:
                cache.put(key, "hot_value", 2048)

    def _simulate_working_set(self) -> None:
        """Simulate working set behavior."""
        # Simulate program phases
        for i in range(300):
            # Phase 1: pages 0-50
            if i < 100:
                page = f"page_{i % 50}"
            # Phase 2: pages 50-100
            elif i < 200:
                page = f"page_{50 + (i % 50)}"
            # Phase 3: back to pages 0-50
            else:
                page = f"page_{i % 50}"
            self.working_set.access_page(page)

    def _simulate_tiered_storage(self) -> None:
        """Simulate tiered storage placement."""
        # Hot data to RAM
        for i in range(100):
            self.tiered_storage.place_data(f"hot_{i}", 1024, 5000)
        # Warm data to SSD
        for i in range(500):
            self.tiered_storage.place_data(f"warm_{i}", 10240, 500)
        # Cold data to disk
        for i in range(1000):
            self.tiered_storage.place_data(f"cold_{i}", 102400, 10)

    def _simulate_prefetch(self) -> None:
        """Simulate prefetch predictions."""
        # Simulate sequential access pattern
        for i in range(50):
            key = f"seq_data_{i}"
            self.prefetcher.record_access(key)

    def get_findings_summary(self, results: dict) -> str:
        """Generate findings summary."""
        lines = [
            f"# {self.NAME} {self.VERSION}",
            "",
            "Creator: Trang Phan | System: AMOS vInfinity",
            "Role: Advanced Memory Management and Caching",
            "",
            "## Memory Strategy Analysis",
        ]
        strategy = results.get("memory_strategy", "general")
        lines.append(f"- **Detected Strategy**: {strategy}")
        lines.extend(["", "## Available Strategies"])
        strategies = {
            "lru": "Least Recently Used - Evict least recently accessed items",
            "lfu": "Least Frequently Used - Evict least frequently accessed items",
            "working_set": "Working Set - Keep actively used pages in memory",
            "tiered_storage": "Tiered Storage - Place data based on access frequency",
            "prefetching": "Prefetching - Predict and load likely-needed data",
            "adaptive_replacement": "ARC - Balance between recency and frequency",
        }
        for strat, desc in strategies.items():
            marker = "✓" if strat == strategy else " "
            lines.append(f"- [{marker}] **{strat.upper()}**: {desc}")
        # Cache statistics
        cache_stats = results.get("cache_stats", {})
        if cache_stats:
            lines.extend(["", "## Cache Performance"])
            for cache_type, stats in cache_stats.items():
                lines.append(f"\n### {cache_type.upper()} Cache")
                lines.append(f"- **Size**: {stats['size']} entries")
                lines.append(f"- **Memory**: {stats['current_bytes'] / 1024 / 1024:.1f} MB / {stats['max_bytes'] / 1024 / 1024:.1f} MB")
                lines.append(f"- **Hit Rate**: {stats['hit_rate'] * 100:.1f}%")
                lines.append(f"- **Hits**: {stats['hits']}, Misses: {stats['misses']}")
        # Working set
        working = results.get("working_set", {})
        if working:
            lines.extend(["", "## Working Set Analysis"])
            lines.append(f"- **Current Size**: {working.get('size', 0)} pages")
            lines.append(f"- **Max Size**: {working.get('max_size', 0)} pages")
            utilization = working.get('size', 0) / working.get('max_size', 1) * 100
            lines.append(f"- **Utilization**: {utilization:.1f}%")
        # Tiered storage
        tiers = results.get("tiered_storage", {})
        if tiers:
            lines.extend(["", "## Tiered Storage Distribution"])
            for tier_name, tier_stats in tiers.items():
                util = tier_stats['utilization'] * 100
                capacity_gb = tier_stats['capacity'] / (1024 ** 3)
                used_gb = tier_stats['used'] / (1024 ** 3)
                lines.append(f"- **{tier_name.upper()}**: {used_gb:.2f} / {capacity_gb:.2f} GB ({util:.1f}%)")
        # Prefetch
        prefetch = results.get("prefetch", {})
        if prefetch:
            lines.extend(["", "## Prefetch Analysis"])
            candidates = prefetch.get('candidates', [])
            lines.append(f"- **Candidates**: {len(candidates)}")
            if candidates:
                lines.append(f"- **Predicted**: {', '.join(candidates[:5])}")
            lines.append(f"- **Patterns Tracked**: {prefetch.get('patterns_tracked', 0)}")
        lines.extend([
            "",
            "## Memory Hierarchy",
            "```",
            "CPU L1 Cache  (< 1 MB)     - 1 ns access",
            "CPU L2 Cache  (few MB)     - 4 ns access",
            "RAM           (16+ GB)     - 100 ns access",
            "SSD           (512+ GB)    - 100 μs access",
            "Disk          (2+ TB)      - 10 ms access",
            "```",
            "",
            "## Optimization Strategies",
            "1. **Temporal Locality**: Recently accessed items likely to be accessed again",
            "2. **Spatial Locality**: Nearby memory addresses likely to be accessed",
            "3. **Working Set**: Keep actively used pages in fast memory",
            "4. **Prefetching**: Load data before it's requested",
            "5. **Compression**: Reduce memory footprint",
            "",
            "## Cache Replacement Policies",
            "- **LRU**: Good for temporal locality",
            "- **LFU**: Good for frequently accessed items",
            "- **FIFO**: Simple but can suffer from Belady's anomaly",
            "- **ARC**: Self-tuning balance of LRU and LFU",
            "",
            "## Safety and Constraints",
            "- Memory limits enforced to prevent overflow",
            "- Working set size prevents thrashing",
            "- Tier placement respects capacity constraints",
            "- Prefetching limited to avoid bandwidth exhaustion",
            "",
            "## Limitations",
            "- Simulated cache (not actual system cache)",
            "- Simplified prefetching (no complex pattern detection)",
            "- Static tier capacities",
            "- No actual memory compression modeled",
        ])
        return "\n".join(lines)


# Singleton instance
_memory_engine: Optional[MemoryOptimizationEngine] = None


def get_memory_optimization_engine() -> MemoryOptimizationEngine:
    """Get or create the Memory Optimization Engine singleton."""
    global _memory_engine
    if _memory_engine is None:
        _memory_engine = MemoryOptimizationEngine()
    return _memory_engine
