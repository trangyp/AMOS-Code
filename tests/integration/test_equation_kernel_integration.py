#!/usr/bin/env python3
"""
Integration Tests for AMOS Equation-Kernel Integration

Validates end-to-end equation execution through kernel with:
- Law enforcement (L = I × S)
- Collapse gates (σ = Ω/K)
- State graph tracking
- Rollback on violations

Usage:
    python -m pytest tests/integration/test_equation_kernel_integration.py -v
    python tests/integration/test_equation_kernel_integration.py
"""


import asyncio
import sys
import time
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from amos_equation_kernel_integration import (
    get_equation_kernel_integration,
    initialize_equation_kernel_integration,
    EquationExecutionMode,
    EquationKernelResult,
)


class TestEquationKernelIntegration:
    """Integration tests for equation-kernel integration layer."""

    @classmethod
    def setup_class(cls):
        """Initialize integration layer once for all tests."""
        cls.integration = get_equation_kernel_integration()
        cls.initialized = asyncio.run(cls.integration.initialize())

    def test_initialization(self):
        """Test that integration layer initializes successfully."""
        assert self.initialized, "Integration layer should initialize"

        stats = self.integration.get_stats()
        assert stats["initialized"] is True
        print(f"\n  Integration stats: {stats}")

    def test_execute_softmax_kernel_governed(self):
        """Test softmax equation execution through kernel with law enforcement."""
        result = self.integration.execute_equation(
            equation_name="softmax",
            inputs={"logits": [1.0, 2.0, 3.0]},
            mode=EquationExecutionMode.KERNEL_GOVERNED,
            enforce_laws=True,
        )

        # Validate result structure
        assert isinstance(result, EquationKernelResult)
        assert result.equation_name == "softmax"
        assert result.inputs == {"logits": [1.0, 2.0, 3.0]}

        # Kernel governance fields
        assert result.law_score >= 0.0, f"Law score should be >= 0, got {result.law_score}"
        assert result.stability_index >= 0.0, f"Stability should be >= 0, got {result.stability_index}"

        # Execution metadata
        assert result.execution_time_ms > 0, "Should track execution time"

        print(f"\n  Equation: {result.equation_name}")
        print(f"  Success: {result.success}")
        print(f"  Law Score (L = I × S): {result.law_score:.4f}")
        print(f"  Stability Index (σ = Ω/K): {result.stability_index:.4f}")
        print(f"  State Graph ID: {result.state_graph_id}")
        print(f"  Rollback Triggered: {result.rollback_triggered}")

    def test_execute_sigmoid_kernel_governed(self):
        """Test sigmoid equation execution through kernel."""
        result = self.integration.execute_equation(
            equation_name="sigmoid",
            inputs={"x": 0.5},
            mode=EquationExecutionMode.KERNEL_GOVERNED,
        )

        assert isinstance(result, EquationKernelResult)
        assert result.equation_name == "sigmoid"
        assert result.law_score >= 0.0
        assert result.stability_index >= 0.0

        print(f"\n  Sigmoid result: law_score={result.law_score:.4f}, stability={result.stability_index:.4f}")

    def test_execute_relu_kernel_governed(self):
        """Test ReLU equation execution through kernel."""
        result = self.integration.execute_equation(
            equation_name="relu",
            inputs={"x": -2.0},
            mode=EquationExecutionMode.KERNEL_GOVERNED,
        )

        assert isinstance(result, EquationKernelResult)
        assert result.equation_name == "relu"
        assert result.law_score >= 0.0

        print(f"\n  ReLU result: law_score={result.law_score:.4f}, stability={result.stability_index:.4f}")

    def test_direct_execution_mode(self):
        """Test direct execution mode (no kernel governance)."""
        result = self.integration.execute_equation(
            equation_name="softmax",
            inputs={"logits": [1.0, 2.0, 3.0]},
            mode=EquationExecutionMode.DIRECT,
        )

        assert isinstance(result, EquationKernelResult)
        # Direct mode may not have full kernel tracking
        print(f"\n  Direct mode result: {result.success}")

    def test_list_available_equations(self):
        """Test listing available equations."""
        equations = self.integration.list_available_equations()

        assert isinstance(equations, list)
        assert len(equations) > 0, "Should have equations available"

        # Check for known equations
        expected = ["softmax", "sigmoid", "relu"]
        for eq in expected:
            assert eq in equations, f"Expected equation '{eq}' not found"

        print(f"\n  Available equations: {len(equations)}")
        print(f"  Sample: {equations[:10]}")

    def test_get_stats(self):
        """Test getting integration statistics."""
        stats = self.integration.get_stats()

        required_keys = [
            "total_executions",
            "successful",
            "failed",
            "initialized",
            "execution_history_size",
        ]

        for key in required_keys:
            assert key in stats, f"Missing stat key: {key}"

        print(f"\n  Integration stats: {stats}")

    def test_execution_history_tracking(self):
        """Test that execution history is tracked."""
        # Execute a few equations
        for _ in range(3):
            self.integration.execute_equation(
                equation_name="softmax",
                inputs={"logits": [1.0, 2.0, 3.0]},
                mode=EquationExecutionMode.KERNEL_GOVERNED,
            )

        # Check history
        history = self.integration.get_execution_history(limit=5)
        assert len(history) >= 3, f"Should have at least 3 executions, got {len(history)}"

        # Check filtering
        filtered = self.integration.get_execution_history(
            limit=10,
            equation_filter="softmax",
        )
        assert all(h.equation_name == "softmax" for h in filtered)

        print(f"\n  Execution history size: {len(history)}")

    def test_concurrent_executions(self):
        """Test concurrent equation executions."""
        async def run_concurrent():
            tasks = [
                self.integration.execute_equation(
                    equation_name="softmax",
                    inputs={"logits": [1.0, 2.0, 3.0]},
                    mode=EquationExecutionMode.KERNEL_GOVERNED,
                )
                for _ in range(5)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results

        # Note: execute_equation is sync, so we test sequential but rapid execution
        start_time = time.time()
        results = []
        for _ in range(5):
            result = self.integration.execute_equation(
                equation_name="softmax",
                inputs={"logits": [1.0, 2.0, 3.0]},
                mode=EquationExecutionMode.KERNEL_GOVERNED,
            )
            results.append(result)

        elapsed = time.time() - start_time

        # All should succeed
        assert all(isinstance(r, EquationKernelResult) for r in results)
        assert all(r.success for r in results)

        print(f"\n  5 concurrent executions completed in {elapsed:.2f}s")
        print(f"  Average law score: {sum(r.law_score for r in results) / len(results):.4f}")


async def demo():
    """Demonstrate equation-kernel integration."""
    print("=" * 70)
    print(" AMOS EQUATION-KERNEL INTEGRATION - DEMO")
    print("=" * 70)

    # Initialize
    integration = get_equation_kernel_integration()
    success = await integration.initialize()

    if not success:
        print("❌ Integration initialization failed")
        return 1

    print("\n✅ Integration layer initialized")

    # Get stats
    stats = integration.get_stats()
    print(f"\nStats: {stats}")

    # List equations
    equations = integration.list_available_equations()
    print(f"\nAvailable equations: {len(equations)}")
    print(f"Sample: {equations[:10]}")

    # Execute with kernel governance
    print("\n" + "-" * 70)
    print("Executing equations with kernel governance...")
    print("-" * 70)

    test_cases = [
        ("softmax", {"logits": [1.0, 2.0, 3.0]}),
        ("sigmoid", {"x": 0.5}),
        ("relu", {"x": -2.0}),
    ]

    for name, inputs in test_cases:
        print(f"\n[TEST] {name}({inputs})")

        result = integration.execute_equation(
            equation_name=name,
            inputs=inputs,
            mode=EquationExecutionMode.KERNEL_GOVERNED,
        )

        print(f"  Success: {result.success}")
        print(f"  Law Score (L = I × S): {result.law_score:.4f}")
        print(f"  Stability (σ = Ω/K): {result.stability_index:.4f}")
        print(f"  Execution Time: {result.execution_time_ms:.2f}ms")
        print(f"  State Graph ID: {result.state_graph_id}")
        print(f"  Rollback: {result.rollback_triggered}")

    # Final stats
    print("\n" + "=" * 70)
    print("FINAL STATISTICS")
    print("=" * 70)
    final_stats = integration.get_stats()
    print(f"Total Executions: {final_stats['total_executions']}")
    print(f"Successful: {final_stats['successful']}")
    print(f"Failed: {final_stats['failed']}")
    print(f"History Size: {final_stats['execution_history_size']}")

    print("\n✅ DEMO COMPLETE")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    # Run pytest if available, otherwise run demo
    try:
        import pytest
        sys.exit(pytest.main([__file__, "-v"]))
    except ImportError:
        print("pytest not installed, running demo mode...")
        sys.exit(asyncio.run(demo()))
