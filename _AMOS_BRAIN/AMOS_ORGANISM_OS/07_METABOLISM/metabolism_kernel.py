#!/usr/bin/env python3
"""AMOS Metabolism Kernel - 07_METABOLISM Subsystem

Responsible for:
- Performance monitoring and metrics collection
- Resource usage tracking (CPU, memory, disk, network)
- Energy management and efficiency optimization
- Garbage collection and cleanup
- Homeostasis - maintaining optimal operating conditions
"""

import json
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Any

import psutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos.metabolism")


class MetricType(Enum):
    """Types of metrics collected."""

    CPU = auto()
    MEMORY = auto()
    DISK = auto()
    NETWORK = auto()
    PROCESS = auto()
    SUBSYSTEM = auto()


class EfficiencyLevel(Enum):
    """Efficiency classification."""

    OPTIMAL = auto()
    GOOD = auto()
    FAIR = auto()
    POOR = auto()
    CRITICAL = auto()


@dataclass
class Metric:
    """A performance metric data point."""

    metric_type: MetricType
    name: str
    value: float
    unit: str
    timestamp: str = ""
    source: str = "metabolism"

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()


@dataclass
class ResourceUsage:
    """Resource usage snapshot."""

    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_percent: float
    disk_used_gb: float
    disk_free_gb: float
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()


@dataclass
class EfficiencyReport:
    """Efficiency analysis report."""

    overall_level: EfficiencyLevel
    cpu_efficiency: float  # 0-1
    memory_efficiency: float
    disk_efficiency: float
    recommendations: list[str]
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()


class MetabolismKernel:
    """The Metabolism Kernel manages resource utilization,
    performance monitoring, and energy efficiency.
    """

    def __init__(self, organism_root: Path):
        self.root = organism_root
        self.metabolism_path = organism_root / "07_METABOLISM"
        self.memory_path = self.metabolism_path / "memory"
        self.logs_path = self.metabolism_path / "logs"

        # Ensure directories
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Metrics storage - circular buffers for time series
        self.metrics_history: dict[str, deque] = {
            "cpu": deque(maxlen=1000),
            "memory": deque(maxlen=1000),
            "disk": deque(maxlen=100),
            "network": deque(maxlen=100),
        }

        # Resource usage snapshots
        self.resource_snapshots: list[ResourceUsage] = []
        self.max_snapshots = 1000

        # Subsystem resource tracking
        self.subsystem_usage: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

        # Efficiency thresholds
        self.thresholds = {
            "cpu_warning": 70.0,
            "cpu_critical": 90.0,
            "memory_warning": 80.0,
            "memory_critical": 95.0,
            "disk_warning": 85.0,
            "disk_critical": 95.0,
        }

        # Homeostasis targets
        self.targets = {
            "cpu_optimal": 50.0,
            "memory_optimal": 60.0,
            "disk_optimal": 70.0,
        }

        # Monitoring thread
        self._monitoring = False
        self._monitor_thread: threading.Thread = None
        self.monitor_interval = 5.0  # seconds

        # Statistics
        self.stats = {
            "metrics_collected": 0,
            "gc_runs": 0,
            "optimizations_applied": 0,
        }

        logger.info(f"MetabolismKernel initialized at {self.metabolism_path}")

    def start(self):
        """Start metabolic monitoring."""
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Metabolic monitoring started")

    def stop(self):
        """Stop metabolic monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        logger.info("Metabolic monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self._monitoring:
            try:
                self._collect_system_metrics()
                time.sleep(self.monitor_interval)
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                time.sleep(1.0)

    def _collect_system_metrics(self):
        """Collect system-wide resource metrics."""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_metric = Metric(
            metric_type=MetricType.CPU, name="cpu_percent", value=cpu_percent, unit="percent"
        )
        self.metrics_history["cpu"].append(cpu_metric)

        # Memory
        memory = psutil.virtual_memory()
        memory_metric = Metric(
            metric_type=MetricType.MEMORY,
            name="memory_percent",
            value=memory.percent,
            unit="percent",
        )
        self.metrics_history["memory"].append(memory_metric)

        # Disk
        disk = psutil.disk_usage(str(self.root))
        disk_percent = (disk.used / disk.total) * 100
        disk_metric = Metric(
            metric_type=MetricType.DISK, name="disk_percent", value=disk_percent, unit="percent"
        )
        self.metrics_history["disk"].append(disk_metric)

        # Resource snapshot
        snapshot = ResourceUsage(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / (1024 * 1024),
            memory_available_mb=memory.available / (1024 * 1024),
            disk_percent=disk_percent,
            disk_used_gb=disk.used / (1024 * 1024 * 1024),
            disk_free_gb=disk.free / (1024 * 1024 * 1024),
        )
        self.resource_snapshots.append(snapshot)

        # Trim history
        if len(self.resource_snapshots) > self.max_snapshots:
            self.resource_snapshots = self.resource_snapshots[-self.max_snapshots :]

        self.stats["metrics_collected"] += 1

        # Check thresholds and log warnings
        self._check_thresholds(cpu_percent, memory.percent, disk_percent)

    def _check_thresholds(self, cpu: float, memory: float, disk: float):
        """Check resource thresholds and log warnings."""
        if cpu > self.thresholds["cpu_critical"]:
            logger.warning(f"CRITICAL: CPU at {cpu:.1f}%")
        elif cpu > self.thresholds["cpu_warning"]:
            logger.warning(f"WARNING: CPU at {cpu:.1f}%")

        if memory > self.thresholds["memory_critical"]:
            logger.warning(f"CRITICAL: Memory at {memory:.1f}%")
        elif memory > self.thresholds["memory_warning"]:
            logger.warning(f"WARNING: Memory at {memory:.1f}%")

        if disk > self.thresholds["disk_critical"]:
            logger.warning(f"CRITICAL: Disk at {disk:.1f}%")
        elif disk > self.thresholds["disk_warning"]:
            logger.warning(f"WARNING: Disk at {disk:.1f}%")

    def track_subsystem_usage(self, subsystem: str, resource_type: str, amount: float):
        """Track resource usage by subsystem."""
        self.subsystem_usage[subsystem][resource_type] += amount

    def get_current_usage(self) -> ResourceUsage:
        """Get current resource usage snapshot."""
        if self.resource_snapshots:
            return self.resource_snapshots[-1]

        # Collect fresh
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(str(self.root))

        return ResourceUsage(
            cpu_percent=psutil.cpu_percent(interval=0.1),
            memory_percent=memory.percent,
            memory_used_mb=memory.used / (1024 * 1024),
            memory_available_mb=memory.available / (1024 * 1024),
            disk_percent=(disk.used / disk.total) * 100,
            disk_used_gb=disk.used / (1024 * 1024 * 1024),
            disk_free_gb=disk.free / (1024 * 1024 * 1024),
        )

    def analyze_efficiency(self) -> EfficiencyReport:
        """Analyze system efficiency and provide recommendations."""
        if not self.resource_snapshots:
            return EfficiencyReport(
                overall_level=EfficiencyLevel.GOOD,
                cpu_efficiency=0.5,
                memory_efficiency=0.5,
                disk_efficiency=0.5,
                recommendations=["Not enough data for analysis"],
            )

        # Calculate averages from recent snapshots
        recent = (
            self.resource_snapshots[-100:]
            if len(self.resource_snapshots) > 100
            else self.resource_snapshots
        )

        avg_cpu = sum(s.cpu_percent for s in recent) / len(recent)
        avg_memory = sum(s.memory_percent for s in recent) / len(recent)
        avg_disk = sum(s.disk_percent for s in recent) / len(recent)

        # Calculate efficiency scores (0-1, higher is better)
        # Optimal range is 30-60% utilization
        def calc_efficiency(avg, optimal):
            deviation = abs(avg - optimal) / optimal
            return max(0.0, 1.0 - deviation)

        cpu_eff = calc_efficiency(avg_cpu, self.targets["cpu_optimal"])
        memory_eff = calc_efficiency(avg_memory, self.targets["memory_optimal"])
        disk_eff = calc_efficiency(avg_disk, self.targets["disk_optimal"])

        # Overall efficiency
        overall = (cpu_eff + memory_eff + disk_eff) / 3

        # Determine level
        if overall > 0.8:
            level = EfficiencyLevel.OPTIMAL
        elif overall > 0.6:
            level = EfficiencyLevel.GOOD
        elif overall > 0.4:
            level = EfficiencyLevel.FAIR
        elif overall > 0.2:
            level = EfficiencyLevel.POOR
        else:
            level = EfficiencyLevel.CRITICAL

        # Generate recommendations
        recommendations = []

        if avg_cpu > 80:
            recommendations.append("High CPU usage: Consider load balancing or scaling")
        elif avg_cpu < 20:
            recommendations.append("Low CPU usage: Resources may be underutilized")

        if avg_memory > 85:
            recommendations.append("High memory usage: Consider memory optimization or cleanup")

        if avg_disk > 90:
            recommendations.append("High disk usage: Cleanup required")

        return EfficiencyReport(
            overall_level=level,
            cpu_efficiency=cpu_eff,
            memory_efficiency=memory_eff,
            disk_efficiency=disk_eff,
            recommendations=recommendations or ["System operating within normal parameters"],
        )

    def garbage_collect(self) -> dict[str, Any]:
        """Perform garbage collection and cleanup."""
        results = {
            "memory_freed": 0,
            "temp_files_removed": 0,
            "old_logs_cleaned": 0,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Force Python GC
        import gc

        gc.collect()

        # Clean old log files (>7 days)
        cutoff = datetime.now() - timedelta(days=7)
        for log_file in self.logs_path.glob("*.log"):
            try:
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff:
                    log_file.unlink()
                    results["old_logs_cleaned"] += 1
            except Exception as e:
                logger.debug(f"Failed to clean {log_file}: {e}")

        # Clear old metrics beyond retention
        self._cleanup_old_metrics()

        self.stats["gc_runs"] += 1
        logger.info(f"Garbage collection completed: {results}")

        return results

    def _cleanup_old_metrics(self):
        """Clean up metrics beyond retention limits."""
        # Deques handle this automatically via maxlen
        pass

    def optimize(self) -> list[str]:
        """Apply optimizations based on current state."""
        optimizations = []

        usage = self.get_current_usage()

        # Memory optimization
        if usage.memory_percent > 90:
            self.garbage_collect()
            optimizations.append("Forced garbage collection due to high memory")

        # Adjust monitoring interval based on load
        if usage.cpu_percent > 80:
            if self.monitor_interval < 10.0:
                self.monitor_interval = 10.0
                optimizations.append("Increased monitoring interval to reduce overhead")
        elif usage.cpu_percent < 30:
            if self.monitor_interval > 2.0:
                self.monitor_interval = 2.0
                optimizations.append("Decreased monitoring interval for better resolution")

        self.stats["optimizations_applied"] += len(optimizations)

        return optimizations if optimizations else ["No optimizations needed"]

    def get_subsystem_breakdown(self) -> dict[str, dict[str, float]]:
        """Get resource usage breakdown by subsystem."""
        return dict(self.subsystem_usage)

    def get_metrics_summary(self, minutes: int = 5) -> dict[str, Any]:
        """Get metrics summary for recent period."""
        cutoff = datetime.now(UTC) - timedelta(minutes=minutes)

        summary = {}
        for metric_type, history in self.metrics_history.items():
            recent = [m for m in history if datetime.fromisoformat(m.timestamp) > cutoff]
            if recent:
                values = [m.value for m in recent]
                summary[metric_type] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "current": values[-1],
                }

        return summary

    def get_state(self) -> dict[str, Any]:
        """Get current metabolism state."""
        usage = self.get_current_usage()
        efficiency = self.analyze_efficiency()

        return {
            "monitoring_active": self._monitoring,
            "current_cpu": usage.cpu_percent,
            "current_memory": usage.memory_percent,
            "current_disk": usage.disk_percent,
            "efficiency_level": efficiency.overall_level.name,
            "metrics_collected": self.stats["metrics_collected"],
            "snapshots_stored": len(self.resource_snapshots),
            "gc_runs": self.stats["gc_runs"],
            "optimizations_applied": self.stats["optimizations_applied"],
            "monitor_interval": self.monitor_interval,
            "timestamp": datetime.now(UTC).isoformat(),
        }


if __name__ == "__main__":
    # Test the metabolism kernel
    root = Path(__file__).parent.parent
    metabolism = MetabolismKernel(root)

    print("Metabolism State (initial):")
    print(json.dumps(metabolism.get_state(), indent=2))

    print("\n=== Test 1: Start monitoring ===")
    metabolism.start()
    time.sleep(0.5)
    print(f"Monitoring active: {metabolism._monitoring}")

    print("\n=== Test 2: Collect metrics ===")
    time.sleep(2.0)
    usage = metabolism.get_current_usage()
    print(f"CPU: {usage.cpu_percent:.1f}%")
    print(f"Memory: {usage.memory_percent:.1f}%")
    print(f"Disk: {usage.disk_percent:.1f}%")

    print("\n=== Test 3: Efficiency analysis ===")
    efficiency = metabolism.analyze_efficiency()
    print(f"Overall Level: {efficiency.overall_level.name}")
    print(f"CPU Efficiency: {efficiency.cpu_efficiency:.2f}")
    print(f"Memory Efficiency: {efficiency.memory_efficiency:.2f}")
    print(f"Disk Efficiency: {efficiency.disk_efficiency:.2f}")
    print(f"Recommendations: {efficiency.recommendations}")

    print("\n=== Test 4: Track subsystem usage ===")
    metabolism.track_subsystem_usage("01_BRAIN", "cpu", 15.5)
    metabolism.track_subsystem_usage("01_BRAIN", "memory", 128.0)
    metabolism.track_subsystem_usage("06_MUSCLE", "cpu", 10.2)
    print(f"Subsystem usage: {dict(metabolism.subsystem_usage)}")

    print("\n=== Test 5: Garbage collection ===")
    gc_results = metabolism.garbage_collect()
    print(f"GC Results: {gc_results}")

    print("\n=== Test 6: Optimization ===")
    optimizations = metabolism.optimize()
    print(f"Optimizations: {optimizations}")

    metabolism.stop()

    print("\nFinal State:")
    print(json.dumps(metabolism.get_state(), indent=2))
