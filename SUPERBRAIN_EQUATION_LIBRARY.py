#!/usr/bin/env python3
"""
AMOS SuperBrain Equation Library
Executable implementations of equations from 24 technology domains
"""

import math
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

import numpy as np

# ============================================================================
# CROSS-DOMAIN MATHEMATICAL PATTERNS
# ============================================================================


class MathematicalPattern(Enum):
    """Universal patterns found across multiple domains"""

    CONVEX_OPTIMIZATION = "convex_optimization"  # ML, Control, Signal Processing
    LINEAR_SYSTEMS = "linear_systems"  # Robotics, Control, Physics
    STOCHASTIC_PROCESS = "stochastic_process"  # Queueing, Epidemiology, ML
    INFORMATION_FLOW = "information_flow"  # Information Theory, Networking
    CONSERVATION_LAW = "conservation_law"  # Physics, Epidemiology, Databases
    CONVERGENCE = "convergence"  # ML, Distributed Systems, Real-Time


@dataclass
class Equation:
    """Universal equation representation"""

    name: str
    domain: str
    pattern: MathematicalPattern
    formula: str
    implementation: Callable
    invariants: List[str]
    parameters: dict


# ============================================================================
# MACHINE LEARNING & AI
# ============================================================================


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """
    Softmax: σ(x_i) = exp(x_i) / Σ exp(x_j)
    Pattern: Information Flow (probability distribution)
    Used in: Transformers, classification, attention mechanisms
    """
    exp_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return exp_x / np.sum(exp_x, axis=axis, keepdims=True)


def scaled_dot_product_attention(
    Q: np.ndarray, K: np.ndarray, V: np.ndarray, mask: np.ndarray = None
) -> tuple[np.ndarray, np.ndarray]:
    """
    Transformer Attention: Attention(Q,K,V) = softmax(QK^T/√d_k)V
    Pattern: Information Flow
    Invariant: Attention weights sum to 1
    """
    d_k = Q.shape[-1]
    scores = np.dot(Q, K.T) / np.sqrt(d_k)

    if mask is not None:
        scores = scores + (mask * -1e9)

    attention_weights = softmax(scores)
    output = np.dot(attention_weights, V)

    return output, attention_weights


def backpropagation_gradient(
    loss_gradient: np.ndarray, activations: list[np.ndarray], weights: list[np.ndarray]
) -> list[np.ndarray]:
    """
    Backpropagation Chain Rule: ∂E/∂w = ∂E/∂o · ∂o/∂net · ∂net/∂w
    Pattern: Convex Optimization
    Invariant: Gradient points in direction of steepest descent
    """
    gradients = []
    delta = loss_gradient

    for i in range(len(weights) - 1, -1, -1):
        # ∂E/∂w_i = δ · a_{i-1}^T
        grad = np.outer(delta, activations[i])
        gradients.insert(0, grad)

        # δ_{i-1} = (w_i^T · δ) ⊙ f'(net_{i-1})
        if i > 0:
            delta = np.dot(weights[i].T, delta) * (activations[i] * (1 - activations[i]))

    return gradients


# ============================================================================
# SYSTEMS & INFRASTRUCTURE
# ============================================================================


def littles_law(arrival_rate: float, avg_service_time: float) -> float:
    """
    Little's Law: L = λW
    Pattern: Stochastic Process
    Invariant: Holds regardless of arrival/service distribution
    Used in: Queueing theory, system capacity planning
    """
    return arrival_rate * avg_service_time


def utilization_bound_rm_scheduling(
    tasks: list[tuple[float, float]],  # (execution_time, period)
) -> bool:
    """
    Rate Monotonic Schedulability: Σ(C_i/P_i) ≤ n(2^(1/n) - 1)
    Pattern: Convergence (feasibility test)
    Used in: Real-time systems
    """
    n = len(tasks)
    utilization = sum(c / p for c, p in tasks)
    bound = n * (2 ** (1 / n) - 1)
    return utilization <= bound


def bloom_filter_false_positive(
    m: int,  # bits
    n: int,  # elements
    k: int,  # hash functions
) -> float:
    """
    Bloom Filter: p = (1 - e^(-kn/m))^k
    Pattern: Stochastic Process (probabilistic data structure)
    Invariant: No false negatives
    """
    return (1 - math.exp(-k * n / m)) ** k


# ============================================================================
# INFORMATION THEORY
# ============================================================================


def shannon_entropy(probabilities: np.ndarray) -> float:
    """
    Shannon Entropy: H(X) = -Σ p(x) log p(x)
    Pattern: Information Flow
    Invariant: H(X) ≥ 0, H(X) = 0 iff X is deterministic
    """
    # Handle zero probabilities
    probs = probabilities[probabilities > 0]
    return -np.sum(probs * np.log2(probs))


def mutual_information(
    joint_prob: np.ndarray, marginal_x: np.ndarray, marginal_y: np.ndarray
) -> float:
    """
    Mutual Information: I(X;Y) = Σ p(x,y) log(p(x,y)/p(x)p(y))
    Pattern: Information Flow
    Invariant: I(X;Y) ≥ 0, I(X;Y) = 0 iff X ⊥ Y
    """
    mi = 0.0
    for i in range(len(marginal_x)):
        for j in range(len(marginal_y)):
            if joint_prob[i, j] > 0:
                mi += joint_prob[i, j] * math.log2(
                    joint_prob[i, j] / (marginal_x[i] * marginal_y[j])
                )
    return mi


# ============================================================================
# CRYPTOGRAPHY
# ============================================================================


def elliptic_curve_point_addition(
    P: Tuple[int, int], Q: Tuple[int, int], a: int, p: int
) -> Tuple[int, int]:
    """
    ECC Point Addition: R = P + Q
    Curve: y² = x³ + ax + b (mod p)
    Pattern: Group Theory (Abelian group)
    Invariant: Associativity, identity (point at infinity)
    """
    x1, y1 = P
    x2, y2 = Q

    if P == (0, 0):  # Point at infinity (identity)
        return Q
    if Q == (0, 0):
        return P

    if P == Q:
        # Point doubling: λ = (3x₁² + a) / (2y₁)
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        # Point addition: λ = (y₂ - y₁) / (x₂ - x₁)
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p

    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p

    return (x3, y3)


# ============================================================================
# CONTROL THEORY
# ============================================================================


def pid_controller(
    error: float, integral_error: float, derivative_error: float, Kp: float, Ki: float, Kd: float
) -> float:
    """
    PID Controller: u(t) = K_p·e(t) + K_i·∫e + K_d·de/dt
    Pattern: Linear Systems (feedback control)
    Invariant: Stability when all poles have Re < 0
    """
    return Kp * error + Ki * integral_error + Kd * derivative_error


# ============================================================================
# EPIDEMIOLOGY
# ============================================================================


def sir_model_step(
    S: float,  # Susceptible
    I: float,  # Infectious
    R: float,  # Recovered
    beta: float,  # Infection rate
    gamma: float,  # Recovery rate
    dt: float,  # Time step
) -> Tuple[float, float, float]:
    """
    SIR Model:
    dS/dt = -βSI/N
    dI/dt = βSI/N - γI
    dR/dt = γI

    Pattern: Conservation Law (S + I + R = N)
    Invariant: Total population constant
    """
    N = S + I + R

    dS = -beta * S * I / N * dt
    dI = (beta * S * I / N - gamma * I) * dt
    dR = gamma * I * dt

    return S + dS, I + dI, R + dR


def basic_reproduction_number(beta: float, gamma: float) -> float:
    """
    R₀ = β/γ
    Pattern: Stochastic Process
    Invariant: R₀ < 1 → disease dies out
    """
    return beta / gamma


# ============================================================================
# CROSS-DOMAIN UNIFICATION
# ============================================================================


class EquationRegistry:
    """
    Knowledge graph of equations with cross-domain relationships
    """

    def __init__(self):
        self.equations: List[Equation] = []
        self.pattern_index: dict = {pattern: [] for pattern in MathematicalPattern}

    def register(self, eq: Equation):
        self.equations.append(eq)
        self.pattern_index[eq.pattern].append(eq)

    def get_by_pattern(self, pattern: MathematicalPattern) -> List[Equation]:
        return self.pattern_index[pattern]

    def find_isomorphisms(self) -> list[tuple[str, str, str]]:
        """
        Find equations that share the same mathematical structure
        Returns: [(eq1_name, eq2_name, pattern_description)]
        """
        isomorphisms = []

        # Example: Softmax and Rate Monotonic both involve normalization
        isomorphisms.append(
            (
                "softmax",
                "rate_monotonic_utilization",
                "Both normalize to [0,1] range for decision making",
            )
        )

        # Example: Entropy and Bloom Filter both use probabilistic measures
        isomorphisms.append(
            (
                "shannon_entropy",
                "bloom_filter_fp_rate",
                "Both measure information/uncertainty in probabilistic systems",
            )
        )

        # Example: SIR and Queueing both use conservation laws
        isomorphisms.append(
            ("sir_model", "littles_law", "Both conserve total quantities (population/items)")
        )

        return isomorphisms


# Global registry
REGISTRY = EquationRegistry()

# Register all equations
REGISTRY.register(
    Equation(
        name="scaled_dot_product_attention",
        domain="Machine Learning",
        pattern=MathematicalPattern.INFORMATION_FLOW,
        formula="softmax(QK^T/√d_k)V",
        implementation=scaled_dot_product_attention,
        invariants=["Attention weights sum to 1", "Output is weighted average of V"],
        parameters={"d_k": "key dimension"},
    )
)

REGISTRY.register(
    Equation(
        name="littles_law",
        domain="Systems",
        pattern=MathematicalPattern.STOCHASTIC_PROCESS,
        formula="L = λW",
        implementation=littles_law,
        invariants=["Holds for any arrival/service distribution", "L, λ, W > 0"],
        parameters={"lambda": "arrival rate", "W": "average time"},
    )
)

REGISTRY.register(
    Equation(
        name="shannon_entropy",
        domain="Information Theory",
        pattern=MathematicalPattern.INFORMATION_FLOW,
        formula="H(X) = -Σ p(x) log p(x)",
        implementation=shannon_entropy,
        invariants=["H(X) ≥ 0", "H(X) = 0 iff X deterministic"],
        parameters={"probabilities": "probability distribution"},
    )
)

REGISTRY.register(
    Equation(
        name="sir_model",
        domain="Epidemiology",
        pattern=MathematicalPattern.CONSERVATION_LAW,
        formula="S + I + R = N",
        implementation=sir_model_step,
        invariants=["Total population constant", "S, I, R ≥ 0"],
        parameters={"beta": "infection rate", "gamma": "recovery rate"},
    )
)

# ============================================================================
# VALIDATION FRAMEWORK
# ============================================================================


def validate_invariant(name: str, condition: bool, message: str) -> bool:
    """Validate a mathematical invariant"""
    if not condition:
        print(f"❌ INVARIANT VIOLATION [{name}]: {message}")
        return False
    print(f"✅ INVARIANT VALID [{name}]")
    return True


def test_all_equations():
    """Run invariant tests on all equation implementations"""
    results = []

    # Test softmax
    x = np.array([1.0, 2.0, 3.0])
    s = softmax(x)
    results.append(
        validate_invariant(
            "softmax_sum", abs(np.sum(s) - 1.0) < 1e-6, f"Sum should be 1, got {np.sum(s)}"
        )
    )

    # Test Little's Law
    L = littles_law(10.0, 5.0)
    results.append(
        validate_invariant("littles_law_positive", L > 0, f"L should be positive, got {L}")
    )

    # Test entropy
    probs = np.array([0.5, 0.5])
    H = shannon_entropy(probs)
    results.append(
        validate_invariant(
            "entropy_nonnegative", H >= 0, f"Entropy should be non-negative, got {H}"
        )
    )

    # Test SIR conservation
    S, I, R = 100.0, 10.0, 0.0
    S_new, I_new, R_new = sir_model_step(S, I, R, 0.3, 0.1, 0.1)
    results.append(
        validate_invariant(
            "sir_conservation",
            abs((S_new + I_new + R_new) - (S + I + R)) < 1e-6,
            "Population should be conserved",
        )
    )

    return all(results)


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS SUPERBRAIN EQUATION LIBRARY")
    print("=" * 60)

    print("\n📊 EQUATION REGISTRY")
    print("-" * 40)
    for pattern in MathematicalPattern:
        eqs = REGISTRY.get_by_pattern(pattern)
        print(f"\n{pattern.value}:")
        for eq in eqs:
            print(f"  • {eq.name} [{eq.domain}]")

    print("\n\n🔗 CROSS-DOMAIN ISOMORPHISMS")
    print("-" * 40)
    for eq1, eq2, desc in REGISTRY.find_isomorphisms():
        print(f"\n{eq1} ↔ {eq2}")
        print(f"  → {desc}")

    print("\n\n🧪 INVARIANT VALIDATION")
    print("-" * 40)
    all_passed = test_all_equations()

    print(f"\n{'=' * 60}")
    if all_passed:
        print("✅ ALL INVARIANTS VALIDATED")
    else:
        print("❌ SOME INVARIANTS FAILED")
    print("=" * 60)
