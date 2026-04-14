#!/usr/bin/env python3
"""AMOS Energy System - Section 15 of Architecture

E_t = (E_total, Allocation, Demand, Reserve)

Compute is treated as organism energy.

Key constraints:
- Conservation: Σ Allocation_i ≤ E_total
- Allocation: Allocation_i = (Priority_i · Demand_i) / Σ(Priority_j · Demand_j)
- Reserve: Reserve ≥ ρ
- Branch budget: |Ψ_t| ≤ E_branch / Cost_simulation
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class EnergyPool:
    """A pool of energy resources."""

    name: str
    total_capacity: float  # Total energy available
    current_level: float = None  # Currently available (defaults to total_capacity)
    reserve_minimum: float = 0.1  # ρ - minimum reserve (10%)
    allocated: float = field(default=0.0, init=False)  # Usage tracking
    consumed: float = field(default=0.0, init=False)

    def __post_init__(self):
        if self.current_level is None:
            self.current_level = self.total_capacity
        if self.current_level > self.total_capacity:
            self.current_level = self.total_capacity

    @property
    def available(self) -> float:
        """Energy available for allocation."""
        return max(0, self.current_level - self.allocated)

    @property
    def reserve(self) -> float:
        """Current reserve level."""
        return self.total_capacity * self.reserve_minimum

    def can_allocate(self, amount: float) -> bool:
        """Check if amount can be allocated."""
        return amount <= self.available

    def allocate(self, amount: float) -> bool:
        """Allocate energy. Returns success."""
        if self.can_allocate(amount):
            self.allocated += amount
            return True
        return False

    def consume(self, amount: float) -> bool:
        """Consume allocated energy."""
        if amount <= self.allocated:
            self.allocated -= amount
            self.consumed += amount
            self.current_level -= amount
            return True
        return False

    def release(self, amount: float):
        """Release unused allocation back to pool."""
        self.allocated = max(0, self.allocated - amount)

    def recharge(self, amount: float):
        """Add energy to pool."""
        self.current_level = min(self.total_capacity, self.current_level + amount)


@dataclass
class EnergyConsumer:
    """Something that consumes energy."""

    consumer_id: str
    name: str
    priority: float = 1.0  # Higher = more important
    demand: float = 0.0  # Energy required
    allocation: float = 0.0  # Currently allocated

    # Efficiency metrics
    efficiency: float = 1.0  # Output per unit energy
    actual_consumption: float = 0.0

    def compute_demand(self, task_complexity: float = 1.0) -> float:
        """Compute energy demand based on task."""
        base_demand = 10.0  # Base energy units
        self.demand = base_demand * task_complexity
        return self.demand


class EnergyAllocator:
    """Manages energy allocation across competing demands.

    Allocation_i = (Priority_i · Demand_i) / Σ(Priority_j · Demand_j)
    """

    def __init__(self, pool: EnergyPool):
        self.pool = pool
        self.consumers: dict[str, EnergyConsumer] = {}
        self.allocation_history: list[dict] = []

    def register_consumer(self, consumer: EnergyConsumer):
        """Register an energy consumer."""
        self.consumers[consumer.consumer_id] = consumer

    def compute_allocations(self) -> dict[str, float]:
        """Compute proportional allocation based on priority and demand."""
        # Total weighted demand
        total_weighted_demand = sum(
            c.priority * c.demand for c in self.consumers.values() if c.demand > 0
        )

        allocations = {}
        available = self.pool.available

        for consumer_id, consumer in self.consumers.items():
            if consumer.demand <= 0:
                allocations[consumer_id] = 0.0
                continue

            # Proportional allocation
            if total_weighted_demand > 0:
                share = (consumer.priority * consumer.demand) / total_weighted_demand
                allocation = min(available * share, consumer.demand)
            else:
                allocation = 0.0

            allocations[consumer_id] = allocation

        return allocations

    def allocate(self) -> dict[str, float]:
        """Execute allocation to all registered consumers."""
        allocations = self.compute_allocations()

        # Apply allocations
        for consumer_id, amount in allocations.items():
            consumer = self.consumers[consumer_id]

            # Release previous allocation
            if consumer.allocation > 0:
                self.pool.release(consumer.allocation)

            # Allocate new amount
            if self.pool.allocate(amount):
                consumer.allocation = amount
            else:
                consumer.allocation = 0.0

        # Record history
        self.allocation_history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "available": self.pool.available,
                "allocations": allocations.copy(),
            }
        )

        return allocations

    def get_consumer_status(self) -> list[dict]:
        """Get status of all consumers."""
        return [
            {
                "id": c.consumer_id,
                "name": c.name,
                "priority": c.priority,
                "demand": c.demand,
                "allocation": c.allocation,
                "satisfaction": c.allocation / c.demand if c.demand > 0 else 1.0,
            }
            for c in self.consumers.values()
        ]


class BranchEnergyBudget:
    """Manages energy budget for branch generation.

    |Ψ_t| ≤ E_branch / Cost_simulation
    """

    def __init__(self, energy_pool: EnergyPool):
        self.pool = energy_pool
        self.simulation_cost: float = 5.0  # Energy per simulation
        self.branch_budget_ratio: float = 0.3  # 30% of energy for branches

    def compute_max_branches(self) -> int:
        """Compute maximum number of branches given energy budget."""
        energy_for_branches = self.pool.available * self.branch_budget_ratio
        max_branches = int(energy_for_branches / self.simulation_cost)
        return max(1, max_branches)  # At least 1

    def can_simulate(self, n_branches: int) -> bool:
        """Check if we have energy to simulate n branches."""
        required = n_branches * self.simulation_cost
        energy_for_branches = self.pool.available * self.branch_budget_ratio
        return required <= energy_for_branches

    def charge_for_simulation(self, n_branches: int) -> bool:
        """Charge energy for branch simulation."""
        cost = n_branches * self.simulation_cost
        # Create temporary consumer
        sim_consumer = EnergyConsumer(
            consumer_id="branch_sim", name="Branch Simulation", priority=0.8, demand=cost
        )

        if self.pool.allocate(cost):
            self.pool.consume(cost)
            return True
        return False


class EnergyMonitor:
    """Monitors energy usage and efficiency."""

    def __init__(self, pool: EnergyPool):
        self.pool = pool
        self.usage_history: list[dict] = []
        self.efficiency_metrics: dict[str, list[float]] = defaultdict(list)

    def record_usage(self, consumer_id: str, energy_used: float, output_produced: float):
        """Record energy usage and output."""
        efficiency = output_produced / energy_used if energy_used > 0 else 0

        self.usage_history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "consumer": consumer_id,
                "energy": energy_used,
                "output": output_produced,
                "efficiency": efficiency,
            }
        )

        self.efficiency_metrics[consumer_id].append(efficiency)

        # Keep history manageable
        if len(self.usage_history) > 1000:
            self.usage_history = self.usage_history[-500:]

    def get_average_efficiency(self, consumer_id: str) -> float:
        """Get average efficiency for a consumer."""
        metrics = self.efficiency_metrics.get(consumer_id, [])
        if not metrics:
            return 1.0
        return sum(metrics) / len(metrics)

    def get_system_efficiency(self) -> float:
        """Get overall system efficiency."""
        total_energy = sum(u["energy"] for u in self.usage_history)
        total_output = sum(u["output"] for u in self.usage_history)

        if total_energy == 0:
            return 1.0
        return total_output / total_energy

    def generate_report(self) -> dict:
        """Generate energy usage report."""
        if not self.usage_history:
            return {"status": "no_data"}

        recent = self.usage_history[-100:]

        return {
            "current_level": self.pool.current_level,
            "total_capacity": self.pool.total_capacity,
            "reserve": self.pool.reserve,
            "available": self.pool.available,
            "system_efficiency": self.get_system_efficiency(),
            "recent_consumption": sum(u["energy"] for u in recent),
            "recent_output": sum(u["output"] for u in recent),
            "consumer_efficiencies": {
                cid: self.get_average_efficiency(cid) for cid in self.efficiency_metrics.keys()
            },
        }


class AMOSEnergySystem:
    """Complete AMOS Energy Management System.

    Coordinates:
    - Energy pools (compute, memory, IO)
    - Consumer allocation
    - Branch simulation budgeting
    - Efficiency monitoring
    """

    def __init__(self, total_energy: float = 1000.0):
        # Main energy pool (compute units)
        self.compute_pool = EnergyPool(
            name="compute",
            total_capacity=total_energy,
            current_level=total_energy,
            reserve_minimum=0.15,  # 15% reserve
        )

        # Subsystem energy pools
        self.pools: dict[str, EnergyPool] = {
            "compute": self.compute_pool,
            "memory": EnergyPool(name="memory", total_capacity=200, current_level=200),
            "io": EnergyPool(name="io", total_capacity=100, current_level=100),
        }

        # Allocators for each pool
        self.allocators: dict[str, EnergyAllocator] = {
            name: EnergyAllocator(pool) for name, pool in self.pools.items()
        }

        # Branch budget manager
        self.branch_budget = BranchEnergyBudget(self.compute_pool)

        # Monitor
        self.monitor = EnergyMonitor(self.compute_pool)

        # Subsystem consumers
        self._init_consumers()

    def _init_consumers(self):
        """Initialize default consumers."""
        # Brain consumers
        self.register_consumer(
            "compute",
            EnergyConsumer(consumer_id="brain_cognition", name="Brain Cognition", priority=0.9),
        )

        self.register_consumer(
            "compute",
            EnergyConsumer(consumer_id="branch_generation", name="Branch Generation", priority=0.8),
        )

        self.register_consumer(
            "compute",
            EnergyConsumer(consumer_id="simulation", name="Simulation Engine", priority=0.7),
        )

        self.register_consumer(
            "compute",
            EnergyConsumer(consumer_id="morph_execution", name="Morph Execution", priority=0.6),
        )

        self.register_consumer(
            "memory",
            EnergyConsumer(consumer_id="memory_storage", name="Memory Storage", priority=0.8),
        )

        self.register_consumer(
            "memory",
            EnergyConsumer(consumer_id="memory_retrieval", name="Memory Retrieval", priority=0.7),
        )

    def register_consumer(self, pool_name: str, consumer: EnergyConsumer):
        """Register consumer to specific pool."""
        if pool_name in self.allocators:
            self.allocators[pool_name].register_consumer(consumer)

    def allocate_all(self) -> dict[str, dict[str, float]]:
        """Execute allocation across all pools."""
        allocations = {}
        for pool_name, allocator in self.allocators.items():
            allocations[pool_name] = allocator.allocate()
        return allocations

    def check_energy_constraints(self) -> dict[str, Any]:
        """Check all energy constraints."""
        results = {}

        for name, pool in self.pools.items():
            results[name] = {
                "conservation_satisfied": pool.allocated <= pool.total_capacity,
                "reserve_satisfied": pool.current_level >= pool.reserve,
                "available": pool.available,
                "reserve": pool.reserve,
                "utilization": pool.consumed / pool.total_capacity
                if pool.total_capacity > 0
                else 0,
            }

        return results

    def can_generate_branches(self, n_branches: int) -> bool:
        """Check if we can generate n branches given energy budget."""
        return self.branch_budget.can_simulate(n_branches)

    def get_max_branches(self) -> int:
        """Get maximum branches allowed by energy budget."""
        return self.branch_budget.compute_max_branches()

    def consume(self, consumer_id: str, pool_name: str, amount: float, output: float = 0.0):
        """Record energy consumption."""
        pool = self.pools.get(pool_name)
        if pool:
            pool.consume(amount)
            self.monitor.record_usage(consumer_id, amount, output)

    def get_status(self) -> dict:
        """Get complete energy system status."""
        return {
            "pools": {
                name: {
                    "current": pool.current_level,
                    "total": pool.total_capacity,
                    "reserve": pool.reserve,
                    "available": pool.available,
                    "allocated": pool.allocated,
                }
                for name, pool in self.pools.items()
            },
            "constraints": self.check_energy_constraints(),
            "branch_budget": {
                "max_branches": self.get_max_branches(),
                "simulation_cost": self.branch_budget.simulation_cost,
            },
            "efficiency": self.monitor.get_system_efficiency(),
            "consumers": {
                pool_name: allocator.get_consumer_status()
                for pool_name, allocator in self.allocators.items()
            },
        }


def demo_energy_system():
    """Demonstrate AMOS Energy System."""
    print("=" * 70)
    print("⚡ AMOS ENERGY SYSTEM - Section 15")
    print("=" * 70)
    print("\nE_t = (E_total, Allocation, Demand, Reserve)")
    print("Σ Allocation_i ≤ E_total")
    print("|Ψ_t| ≤ E_branch / Cost_simulation")
    print("=" * 70)

    # Initialize energy system
    energy = AMOSEnergySystem(total_energy=1000.0)

    # 1. Show initial status
    print("\n[1] Initial Energy Status")
    status = energy.get_status()
    for pool_name, pool_data in status["pools"].items():
        print(
            f"  {pool_name}: {pool_data['current']:.0f}/{pool_data['total']:.0f} "
            f"(reserve: {pool_data['reserve']:.0f}, available: {pool_data['available']:.0f})"
        )

    # 2. Set demands and allocate
    print("\n[2] Computing Energy Allocations")

    # Simulate tasks with different complexity
    tasks = [
        ("brain_cognition", "compute", 2.0),
        ("branch_generation", "compute", 1.5),
        ("simulation", "compute", 3.0),
        ("morph_execution", "compute", 1.0),
        ("memory_storage", "memory", 1.0),
        ("memory_retrieval", "memory", 0.5),
    ]

    for consumer_id, pool_name, complexity in tasks:
        allocator = energy.allocators[pool_name]
        if consumer_id in allocator.consumers:
            consumer = allocator.consumers[consumer_id]
            demand = consumer.compute_demand(complexity)
            print(f"  {consumer.name}: demand={demand:.1f} units")

    # Allocate
    allocations = energy.allocate_all()

    print("\n[3] Allocation Results")
    for pool_name, allocs in allocations.items():
        print(f"  {pool_name} pool:")
        for consumer_id, amount in allocs.items():
            consumer = energy.allocators[pool_name].consumers[consumer_id]
            pct = (amount / consumer.demand * 100) if consumer.demand > 0 else 0
            print(f"    - {consumer.name}: {amount:.1f} ({pct:.0f}% of demand)")

    # 4. Check constraints
    print("\n[4] Energy Constraints Check")
    constraints = energy.check_energy_constraints()
    for pool_name, checks in constraints.items():
        status = "✓" if all(checks.values()) else "✗"
        print(
            f"  {status} {pool_name}: conservation={checks['conservation_satisfied']}, "
            f"reserve={checks['reserve_satisfied']}"
        )

    # 5. Branch generation budget
    print("\n[5] Branch Generation Budget")
    max_branches = energy.get_max_branches()
    print(f"  Max branches given energy: {max_branches}")

    test_branches = [3, 5, 10, 20]
    for n in test_branches:
        can_do = energy.can_generate_branches(n)
        status = "✓" if can_do else "✗"
        print(f"  {status} {n} branches: {'possible' if can_do else 'insufficient energy'}")

    # 6. Simulate consumption
    print("\n[6] Simulating Energy Consumption")
    consumption = [
        ("brain_cognition", "compute", 15.0, 8.0),
        ("branch_generation", "compute", 12.0, 5.0),
        ("simulation", "compute", 20.0, 6.0),
        ("morph_execution", "compute", 8.0, 7.0),
        ("memory_storage", "memory", 5.0, 4.0),
    ]

    for consumer_id, pool_name, energy_used, output in consumption:
        energy.consume(consumer_id, pool_name, energy_used, output)
        eff = output / energy_used if energy_used > 0 else 0
        print(
            f"  {consumer_id}: {energy_used:.1f} energy → {output:.1f} output "
            f"(efficiency: {eff:.1%})"
        )

    # 7. Final status
    print("\n[7] Final Energy Status")
    final_status = energy.get_status()
    for pool_name, pool_data in final_status["pools"].items():
        used = pool_data["total"] - pool_data["current"]
        pct = used / pool_data["total"] * 100
        print(
            f"  {pool_name}: {pool_data['current']:.0f}/{pool_data['total']:.0f} "
            f"({pct:.1f}% used)"
        )

    # 8. Efficiency report
    print("\n[8] System Efficiency")
    report = energy.monitor.generate_report()
    print(f"  Overall efficiency: {report['system_efficiency']:.1%}")
    print(f"  Recent consumption: {report['recent_consumption']:.1f} units")
    print(f"  Recent output: {report['recent_output']:.1f} value")

    print("\n" + "=" * 70)
    print("✅ AMOS ENERGY SYSTEM OPERATIONAL")
    print("=" * 70)
    print("\nEnergy Capabilities:")
    print("  • Multi-pool resource management")
    print("  • Proportional allocation by priority")
    print("  • Reserve constraints (ρ ≥ 10%)")
    print("  • Conservation: Σ Allocation ≤ E_total")
    print("  • Branch budget: |Ψ_t| ≤ E_branch / Cost_sim")
    print("  • Efficiency monitoring and reporting")
    print("=" * 70)


if __name__ == "__main__":
    demo_energy_system()
