#!/usr/bin/env python3
"""Test Phase 14: Quantum Gravity & Holographic Systems + AI Frontiers"""

from amos_superbrain_equation_bridge import SuperBrainEquationRegistry


def test_ryu_takayanagi_entropy():
    """Test holographic entanglement entropy calculation."""
    registry = SuperBrainEquationRegistry()

    result = registry.execute(
        "ryu_takayanagi_entropy",
        {"boundary_region_size": 10.0, "bulk_minimal_surface": 4.0, "gravitational_constant": 1.0},
    )

    assert result.invariants_valid
    expected = 4.0 / (4 * 1.0)  # S = Area / 4G
    assert abs(result.outputs["result"] - expected) < 0.001
    print("✓ ryu_takayanagi_entropy: S =", result.outputs["result"])


def test_ads_cft_correlator():
    """Test AdS/CFT two-point correlator."""
    registry = SuperBrainEquationRegistry()

    result = registry.execute(
        "ads_cft_correlator",
        {"boundary_separation": 2.0, "ads_radius": 1.0, "scaling_dimension": 2.0},
    )

    assert result.invariants_valid
    # ⟨O(x)O(y)⟩ ∝ 1/|x-y|^(2Δ)
    expected = 1.0 / (2.0 ** (2 * 2.0))
    assert abs(result.outputs["result"] - expected) < 0.001
    print("✓ ads_cft_correlator:", result.outputs["result"])


def test_black_hole_information_rate():
    """Test black hole information retention (Page curve)."""
    registry = SuperBrainEquationRegistry()

    # Before Page time - information still trapped (high retention)
    result1 = registry.execute(
        "black_hole_information_rate",
        {
            "black_hole_mass": 10.0,
            "hawking_temperature": 1.0,
            "time": 100.0,  # Early, before Page time (t_page = 1000)
        },
    )
    assert result1.invariants_valid
    assert 0 < result1.outputs["result"] <= 1
    assert result1.outputs["result"] > 0.8  # High retention early

    # Near Page time - information starts returning (lower retention)
    result2 = registry.execute(
        "black_hole_information_rate",
        {
            "black_hole_mass": 10.0,
            "hawking_temperature": 1.0,
            "time": 900.0,  # Near Page time
        },
    )
    assert result2.invariants_valid
    assert result2.outputs["result"] < result1.outputs["result"]  # Decreases before Page time
    print(
        "✓ black_hole_information_rate: before=",
        result1.outputs["result"],
        "after=",
        result2.outputs["result"],
    )


def test_holographic_complexity():
    """Test holographic complexity via wormhole volume."""
    registry = SuperBrainEquationRegistry()

    result = registry.execute(
        "holographic_complexity",
        {"volume_of_wormhole": 100.0, "newton_constant": 1.0, "ads_radius": 1.0},
    )

    assert result.invariants_valid
    expected = 100.0 / (1.0 * 1.0)  # C = V / (G * R)
    assert abs(result.outputs["result"] - expected) < 0.001
    print("✓ holographic_complexity: C =", result.outputs["result"])


def test_sensor_fusion_confidence():
    """Test embodied AI sensor fusion."""
    registry = SuperBrainEquationRegistry()

    result = registry.execute(
        "sensor_fusion_confidence",
        {"sensor_readings": [1.0, 1.1, 0.9], "sensor_uncertainties": [0.1, 0.2, 0.15]},
    )

    assert result.invariants_valid
    assert 0.9 <= result.outputs["result"] <= 1.1
    print("✓ sensor_fusion_confidence:", result.outputs["result"])


def test_mechanistic_interpretability():
    """Test AI safety interpretability score."""
    registry = SuperBrainEquationRegistry()

    result = registry.execute(
        "mechanistic_interpretability", {"activation_sparsity": 0.8, "concept_purity": 0.9}
    )

    assert result.invariants_valid
    expected = (0.8 + 0.9) / 2
    assert abs(result.outputs["result"] - expected) < 0.001
    print("✓ mechanistic_interpretability:", result.outputs["result"])


def test_kv_cache_memory():
    """Test long context KV cache memory calculation."""
    registry = SuperBrainEquationRegistry()

    result = registry.execute(
        "kv_cache_memory", {"seq_length": 2048, "hidden_dim": 4096, "bytes_per_value": 4}
    )

    assert result.invariants_valid
    expected = (2 * 2048 * 4096 * 4) / (1024**3)  # GB
    assert abs(result.outputs["result"] - expected) < 0.001
    print("✓ kv_cache_memory:", result.outputs["result"], "GB")


def test_context_compression_ratio():
    """Test context compression ratio."""
    registry = SuperBrainEquationRegistry()

    result = registry.execute(
        "context_compression_ratio", {"original_length": 10000, "compressed_length": 2500}
    )

    assert result.invariants_valid
    expected = 10000 / 2500  # ratio = 4.0
    assert abs(result.outputs["result"] - expected) < 0.001
    print("✓ context_compression_ratio:", result.outputs["result"])


def main():
    """Run all Phase 14 tests."""
    print("=" * 60)
    print("Phase 14: Quantum Gravity & Holographic Systems Tests")
    print("=" * 60)

    # Quantum Gravity tests
    print("\n--- Quantum Gravity & Holographic Systems ---")
    test_ryu_takayanagi_entropy()
    test_ads_cft_correlator()
    test_black_hole_information_rate()
    test_holographic_complexity()

    # AI Frontiers tests
    print("\n--- AI Frontiers (2025-2026) ---")
    test_sensor_fusion_confidence()
    test_mechanistic_interpretability()
    test_kv_cache_memory()
    test_context_compression_ratio()

    print("\n" + "=" * 60)
    print("✓ All Phase 14 tests passed!")
    print("=" * 60)

    # Summary
    registry = SuperBrainEquationRegistry()
    print(f"\nTotal equations registered: {len(registry.equations)}")

    phase14_eqs = [name for name, meta in registry.metadata.items() if meta.phase == 14]
    print(f"Phase 14 equations: {len(phase14_eqs)}")

    quantum_gravity_eqs = [
        name
        for name, meta in registry.metadata.items()
        if meta.domain in ["quantum_gravity", "holographic_principle", "black_hole_information"]
    ]
    print(f"Quantum Gravity equations: {len(quantum_gravity_eqs)}")
    print(f"  - {', '.join(quantum_gravity_eqs)}")


if __name__ == "__main__":
    main()
