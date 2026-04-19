"""Test suite for AMOS Equation Kernel.

Comprehensive testing using pytest and Hypothesis for property-based testing
of mathematical invariants across all equation implementations.

Run with: pytest tests/test_equation_kernel.py -v
"""

import math

# Import the kernel
import sys
from pathlib import Path

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List

from .ast_nodes import (
    EquationKernel,
    MathematicalPattern,
    get_equation_kernel,
)


class TestSoftmax:
    """Test suite for softmax function."""

    @pytest.fixture
    def kernel(self) -> EquationKernel:
        return get_equation_kernel()

    def test_softmax_basic(self, kernel: EquationKernel) -> None:
        """Test basic softmax computation."""
        result = kernel.execute("softmax", {"x": np.array([1.0, 2.0, 3.0])})
        assert result.value is not None
        assert result.invariants_valid
        assert len(result.value) == 3

    def test_softmax_sum_to_one(self, kernel: EquationKernel) -> None:
        """Invariant: softmax outputs sum to 1."""
        result = kernel.execute("softmax", {"x": np.array([0.0, 0.0, 0.0])})
        assert result.value is not None
        np.testing.assert_allclose(np.sum(result.value), 1.0, atol=1e-6)

    def test_softmax_all_positive(self, kernel: EquationKernel) -> None:
        """Invariant: all softmax outputs are positive."""
        result = kernel.execute("softmax", {"x": np.array([-100.0, 0.0, 100.0])})
        assert result.value is not None
        assert np.all(result.value > 0)

    def test_softmax_extreme_values(self, kernel: EquationKernel) -> None:
        """Test softmax with extreme values."""
        result = kernel.execute("softmax", {"x": np.array([1000.0, -1000.0])})
        assert result.value is not None
        # One should be close to 1, other close to 0
        assert np.max(result.value) > 0.99
        assert np.min(result.value) < 0.01

    @given(st.lists(st.floats(min_value=-10, max_value=10), min_size=2, max_size=10))
    @settings(max_examples=100)
    def test_softmax_properties_hypothesis(self, kernel: EquationKernel, data: List[float]) -> None:
        """Property-based testing for softmax invariants."""
        arr = np.array(data)
        result = kernel.execute("softmax", {"x": arr})

        if result.value is not None:
            # Property 1: Sum to 1
            assert abs(np.sum(result.value) - 1.0) < 1e-5

            # Property 2: All positive
            assert np.all(result.value > 0)

            # Property 3: Same length as input
            assert len(result.value) == len(data)


class TestLittlesLaw:
    """Test suite for Little's Law."""

    @pytest.fixture
    def kernel(self) -> EquationKernel:
        return get_equation_kernel()

    def test_littles_law_basic(self, kernel: EquationKernel) -> None:
        """Test basic Little's Law computation."""
        result = kernel.execute("littles_law", {"arrival_rate": 10.0, "avg_time": 5.0})
        assert result.value == 50.0
        assert result.invariants_valid

    def test_littles_law_positive(self, kernel: EquationKernel) -> None:
        """Invariant: L must be positive for positive inputs."""
        result = kernel.execute("littles_law", {"arrival_rate": 1.0, "avg_time": 1.0})
        assert result.value is not None
        assert result.value > 0

    def test_littles_law_zero_arrival(self, kernel: EquationKernel) -> None:
        """Test with zero arrival rate."""
        result = kernel.execute("littles_law", {"arrival_rate": 0.0, "avg_time": 5.0})
        assert result.value == 0.0

    def test_littles_law_negative_error(self, kernel: EquationKernel) -> None:
        """Test that negative inputs raise error."""
        with pytest.raises((ValueError, Exception)):
            kernel.execute("littles_law", {"arrival_rate": -1.0, "avg_time": 5.0})

    @given(st.floats(min_value=0.001, max_value=1000), st.floats(min_value=0.001, max_value=1000))
    @settings(max_examples=50)
    def test_littles_law_properties(self, kernel: EquationKernel, lam: float, w: float) -> None:
        """Property-based testing: L = λ × W."""
        result = kernel.execute("littles_law", {"arrival_rate": lam, "avg_time": w})
        if result.value is not None:
            # Property: L = λ × W
            assert abs(result.value - lam * w) < 1e-6
            # Property: L > 0 for positive inputs
            assert result.value > 0


class TestShannonEntropy:
    """Test suite for Shannon Entropy."""

    @pytest.fixture
    def kernel(self) -> EquationKernel:
        return get_equation_kernel()

    def test_entropy_uniform(self, kernel: EquationKernel) -> None:
        """Entropy of uniform distribution is log2(n)."""
        result = kernel.execute("shannon_entropy", {"probabilities": np.array([0.5, 0.5])})
        assert result.value is not None
        assert abs(result.value - 1.0) < 1e-6  # log2(2) = 1

    def test_entropy_deterministic(self, kernel: EquationKernel) -> None:
        """Invariant: deterministic distribution has entropy 0."""
        result = kernel.execute("shannon_entropy", {"probabilities": np.array([1.0, 0.0])})
        assert result.value is not None
        assert result.value == 0.0

    def test_entropy_nonnegative(self, kernel: EquationKernel) -> None:
        """Invariant: entropy is always non-negative."""
        result = kernel.execute("shannon_entropy", {"probabilities": np.array([0.3, 0.7])})
        assert result.value is not None
        assert result.value >= 0

    def test_entropy_four_symbol_uniform(self, kernel: EquationKernel) -> None:
        """Entropy of 4-symbol uniform distribution is 2."""
        result = kernel.execute(
            "shannon_entropy", {"probabilities": np.array([0.25, 0.25, 0.25, 0.25])}
        )
        assert result.value is not None
        assert abs(result.value - 2.0) < 1e-6  # log2(4) = 2

    @given(st.lists(st.floats(min_value=0.01, max_value=1.0), min_size=2, max_size=5))
    @settings(max_examples=50)
    def test_entropy_properties(self, kernel: EquationKernel, probs: List[float]) -> None:
        """Property-based testing for entropy invariants."""
        # Normalize to valid probability distribution
        arr = np.array(probs)
        arr = arr / np.sum(arr)

        result = kernel.execute("shannon_entropy", {"probabilities": arr})
        if result.value is not None:
            # Property: Entropy >= 0
            assert result.value >= 0
            # Property: Entropy <= log2(n) for n symbols
            max_entropy = math.log2(len(arr))
            assert result.value <= max_entropy + 1e-6


class TestBasicReproductionNumber:
    """Test suite for R0 calculation."""

    @pytest.fixture
    def kernel(self) -> EquationKernel:
        return get_equation_kernel()

    def test_r0_basic(self, kernel: EquationKernel) -> None:
        """Test basic R0 computation."""
        result = kernel.execute("basic_reproduction_number", {"beta": 0.5, "gamma": 0.1})
        assert result.value == 5.0

    def test_r0_epidemic_threshold(self, kernel: EquationKernel) -> None:
        """R0 > 1 indicates epidemic potential."""
        result = kernel.execute("basic_reproduction_number", {"beta": 0.3, "gamma": 0.1})
        assert result.value is not None
        assert result.value > 1.0  # Epidemic

    def test_r0_dies_out(self, kernel: EquationKernel) -> None:
        """R0 < 1 indicates disease dies out."""
        result = kernel.execute("basic_reproduction_number", {"beta": 0.05, "gamma": 0.1})
        assert result.value is not None
        assert result.value < 1.0  # Dies out

    def test_r0_zero_gamma_error(self, kernel: EquationKernel) -> None:
        """Test error on zero recovery rate."""
        with pytest.raises((ValueError, ZeroDivisionError, Exception)):
            kernel.execute("basic_reproduction_number", {"beta": 0.5, "gamma": 0.0})


class TestBloomFilter:
    """Test suite for Bloom filter false positive rate."""

    @pytest.fixture
    def kernel(self) -> EquationKernel:
        return get_equation_kernel()

    def test_bloom_fp_basic(self, kernel: EquationKernel) -> None:
        """Test basic FP rate computation."""
        result = kernel.execute("bloom_filter_fp_rate", {"m": 1000, "n": 100, "k": 3})
        assert result.value is not None
        assert 0 <= result.value <= 1

    def test_bloom_fp_in_range(self, kernel: EquationKernel) -> None:
        """Invariant: FP rate is probability [0, 1]."""
        result = kernel.execute("bloom_filter_fp_rate", {"m": 10000, "n": 1000, "k": 5})
        assert result.value is not None
        assert 0 <= result.value <= 1

    def test_bloom_fp_more_bits_lower_rate(self, kernel: EquationKernel) -> None:
        """More bits should generally lower FP rate."""
        result1 = kernel.execute("bloom_filter_fp_rate", {"m": 1000, "n": 100, "k": 3})
        result2 = kernel.execute("bloom_filter_fp_rate", {"m": 10000, "n": 100, "k": 3})
        assert result1.value is not None
        assert result2.value is not None
        assert result2.value < result1.value


class TestPIDController:
    """Test suite for PID controller."""

    @pytest.fixture
    def kernel(self) -> EquationKernel:
        return get_equation_kernel()

    def test_pid_zero_error(self, kernel: EquationKernel) -> None:
        """Zero error should give zero output with zero gains."""
        result = kernel.execute(
            "pid_controller",
            {
                "error": 0.0,
                "integral_error": 0.0,
                "derivative_error": 0.0,
                "Kp": 1.0,
                "Ki": 0.0,
                "Kd": 0.0,
            },
        )
        assert result.value == 0.0

    def test_pid_proportional_only(self, kernel: EquationKernel) -> None:
        """Test proportional term only."""
        result = kernel.execute(
            "pid_controller",
            {
                "error": 5.0,
                "integral_error": 0.0,
                "derivative_error": 0.0,
                "Kp": 2.0,
                "Ki": 0.0,
                "Kd": 0.0,
            },
        )
        assert result.value == 10.0  # 5 * 2

    def test_pid_all_terms(self, kernel: EquationKernel) -> None:
        """Test with all PID terms."""
        result = kernel.execute(
            "pid_controller",
            {
                "error": 1.0,
                "integral_error": 2.0,
                "derivative_error": 3.0,
                "Kp": 1.0,
                "Ki": 0.5,
                "Kd": 0.1,
            },
        )
        expected = 1.0 * 1.0 + 2.0 * 0.5 + 3.0 * 0.1  # 1 + 1 + 0.3 = 2.3
        assert abs(result.value - 2.3) < 1e-6


class TestRateMonotonic:
    """Test suite for Rate Monotonic scheduling."""

    @pytest.fixture
    def kernel(self) -> EquationKernel:
        return get_equation_kernel()

    def test_rm_schedulable(self, kernel: EquationKernel) -> None:
        """Test schedulable task set."""
        result = kernel.execute(
            "rate_monotonic_schedulability",
            {"tasks": [(1, 10), (2, 20)]},  # (C, P) pairs
        )
        assert result.value is True

    def test_rm_not_schedulable(self, kernel: EquationKernel) -> None:
        """Test non-schedulable task set."""
        result = kernel.execute(
            "rate_monotonic_schedulability",
            {"tasks": [(8, 10), (8, 10)]},  # 80% + 80% > bound
        )
        assert result.value is False

    def test_rm_single_task(self, kernel: EquationKernel) -> None:
        """Test single task (always schedulable if utilization <= 1)."""
        result = kernel.execute(
            "rate_monotonic_schedulability",
            {"tasks": [(5, 10)]},  # 50% utilization
        )
        assert result.value is True


class TestEquationRegistry:
    """Test suite for equation registry functionality."""

    @pytest.fixture
    def kernel(self) -> EquationKernel:
        return get_equation_kernel()

    def test_get_all_equations(self, kernel: EquationKernel) -> None:
        """Test retrieving all equations."""
        equations = kernel.get_all_equations()
        assert len(equations) >= 8  # At least our 8 core equations
        names = [eq.name for eq in equations]
        assert "softmax" in names
        assert "littles_law" in names

    def test_get_by_pattern(self, kernel: EquationKernel) -> None:
        """Test pattern-based filtering."""
        info_flow = kernel.get_by_pattern(MathematicalPattern.INFORMATION_FLOW)
        assert len(info_flow) >= 2  # softmax, shannon_entropy

        conservation = kernel.get_by_pattern(MathematicalPattern.CONSERVATION_LAW)
        assert len(conservation) >= 1  # littles_law

    def test_find_isomorphisms(self, kernel: EquationKernel) -> None:
        """Test isomorphism detection."""
        isomorphisms = kernel.find_isomorphisms()
        assert len(isomorphisms) >= 3  # At least our 3 documented

        # Check structure
        for iso in isomorphisms:
            assert "equation1" in iso
            assert "equation2" in iso
            assert "similarity" in iso


class TestErrorHandling:
    """Test suite for error handling."""

    @pytest.fixture
    def kernel(self) -> EquationKernel:
        return get_equation_kernel()

    def test_unknown_equation(self, kernel: EquationKernel) -> None:
        """Test handling of unknown equation name."""
        result = kernel.execute("unknown_equation", {})
        assert result.value is None
        assert not result.invariants_valid
        assert len(result.errors) > 0

    def test_missing_parameters(self, kernel: EquationKernel) -> None:
        """Test handling of missing parameters."""
        result = kernel.execute("softmax", {})  # Missing 'x'
        assert result.value is None or not result.invariants_valid


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
