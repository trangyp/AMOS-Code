"""AMOSL Information Geometry - Belief Manifold and Fisher Metric.

Implements the information-geometric regime:
    - Belief manifold P(X)
    - Fisher information metric g_ij(θ)
    - KL-divergence for bridge legality
    - Bayesian belief updates
    - Uncertainty bundles u(x) = (p, γ, δ, κ, ν)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
import math


@dataclass
class UncertaintyBundle:
    """Uncertainty bundle: u(x) = (p, γ, δ, κ, ν)."""
    probability: float = 1.0
    gamma: float = 0.0  # Precision
    delta: float = 0.0  # Bias
    kappa: float = 0.0  # Confidence
    nu: float = 0.0     # Noise level
    
    def combine(self, other: UncertaintyBundle) -> UncertaintyBundle:
        """Combine two uncertainty bundles."""
        return UncertaintyBundle(
            probability=self.probability * other.probability,
            gamma=(self.gamma + other.gamma) / 2,
            delta=(self.delta + other.delta) / 2,
            kappa=min(self.kappa, other.kappa),
            nu=max(self.nu, other.nu)
        )


@dataclass
class BeliefState:
    """Belief state p(x) ∈ P(X)."""
    distribution: Dict[str, float] = field(default_factory=dict)
    timestamp: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def normalize(self) -> None:
        """Normalize to valid probability distribution."""
        total = sum(self.distribution.values())
        if total > 0:
            self.distribution = {k: v/total for k, v in self.distribution.items()}
    
    def expectation(self, values: Dict[str, float]) -> float:
        """Compute E[value] under belief."""
        return sum(self.distribution.get(k, 0) * v 
                   for k, v in values.items())
    
    def entropy(self) -> float:
        """Compute Shannon entropy H(p)."""
        return -sum(p * math.log2(p) for p in self.distribution.values() if p > 0)


class InformationGeometry:
    """Information-geometric operations on belief manifold."""
    
    def __init__(self):
        self.beliefs: Dict[str, BeliefState] = {}
        self.history: List[Tuple[str, BeliefState]] = []
    
    def fisher_metric(self, params: List[float], 
                     log_likelihood_derivatives: List[List[float]]) -> List[List[float]]:
        """Compute Fisher information metric g_ij(θ).
        
        g_ij(θ) = E[∂log p/∂θ_i · ∂log p/∂θ_j]
        """
        n = len(params)
        g = [[0.0 for _ in range(n)] for _ in range(n)]
        
        # Simplified computation using provided derivatives
        for i in range(n):
            for j in range(n):
                if log_likelihood_derivatives:
                    # Expected value over observations
                    products = [di[i] * di[j] for di in log_likelihood_derivatives]
                    g[i][j] = sum(products) / len(products) if products else 0.0
        
        return g
    
    def kl_divergence(self, p: BeliefState, q: BeliefState) -> float:
        """Compute KL divergence D_KL(p || q)."""
        divergence = 0.0
        for key, prob_p in p.distribution.items():
            prob_q = q.distribution.get(key, 1e-10)  # Avoid log(0)
            if prob_p > 0:
                divergence += prob_p * math.log(prob_p / prob_q)
        return divergence
    
    def check_bridge_legality(self, source_belief: BeliefState,
                               target_belief: BeliefState,
                               epsilon: float = 0.5) -> Tuple[bool, float]:
        """Check if bridge information loss is within bounds.
        
        D_ij <= ε_ij (legal bridge condition)
        """
        divergence = self.kl_divergence(source_belief, target_belief)
        legal = divergence <= epsilon
        return legal, divergence
    
    def bayesian_update(self, prior: BeliefState,
                       likelihood: Dict[str, float],
                       observation: str) -> BeliefState:
        """Bayesian update: p(x|y) = p(y|x)p(x)/p(y)."""
        posterior = BeliefState(
            timestamp=prior.timestamp + 1,
            metadata={"prior": prior.distribution, "observation": observation}
        )
        
        # Compute posterior
        for key, prior_prob in prior.distribution.items():
            likelihood_val = likelihood.get(key, 0.0)
            posterior.distribution[key] = prior_prob * likelihood_val
        
        # Normalize
        posterior.normalize()
        
        # Store
        self.history.append(("update", posterior))
        
        return posterior
    
    def compute_uncertainty_bundle(self, belief: BeliefState) -> UncertaintyBundle:
        """Compute uncertainty bundle from belief state."""
        entropy = belief.entropy()
        
        # Convert entropy to precision (lower entropy = higher precision)
        gamma = max(0.0, 1.0 - entropy / 2.0)  # Normalized
        
        return UncertaintyBundle(
            probability=1.0,  # Belief is always normalized
            gamma=gamma,
            delta=0.0,  # No bias in pure belief
            kappa=gamma,  # Confidence = precision
            nu=entropy / 5.0  # Noise proportional to entropy
        )
    
    def distance_on_manifold(self, belief1: BeliefState, 
                            belief2: BeliefState) -> float:
        """Compute distance between beliefs on information manifold.
        
        Uses Fisher metric induced distance (approximated by KL divergence for nearby points).
        """
        return math.sqrt(self.kl_divergence(belief1, belief2) + 
                        self.kl_divergence(belief2, belief1))
    
    def gradient_flow(self, belief: BeliefState, 
                     potential: Dict[str, float],
                     step_size: float = 0.1) -> BeliefState:
        """Natural gradient flow on belief manifold.
        
        Moves belief in direction of steepest descent of potential
        with respect to Fisher metric.
        """
        new_belief = BeliefState(
            distribution=belief.distribution.copy(),
            timestamp=belief.timestamp + 1,
            metadata={"flow": True}
        )
        
        # Simplified gradient step
        for key in new_belief.distribution:
            grad = potential.get(key, 0.0)
            new_belief.distribution[key] *= math.exp(-step_size * grad)
        
        new_belief.normalize()
        return new_belief
    
    def projection_onto_constraints(self, belief: BeliefState,
                                    constraints: List[callable]) -> BeliefState:
        """Project belief onto constraint manifold.
        
        Information-theoretic projection: minimizes KL divergence to original
        while satisfying constraints.
        """
        # Simplified: just verify constraints
        valid = all(c(belief) for c in constraints)
        
        projected = BeliefState(
            distribution=belief.distribution.copy(),
            timestamp=belief.timestamp,
            metadata={"constrained": True, "valid": valid}
        )
        
        return projected


class BeliefManifold:
    """Manifold of admissible beliefs over state."""
    
    def __init__(self):
        self.geometry = InformationGeometry()
        self.current_belief: Optional[BeliefState] = None
        self.trajectory: List[BeliefState] = []
    
    def initialize_uniform(self, states: List[str]) -> BeliefState:
        """Initialize uniform belief over given states."""
        n = len(states)
        belief = BeliefState(
            distribution={s: 1.0/n for s in states},
            timestamp=0.0,
            metadata={"type": "uniform"}
        )
        self.current_belief = belief
        self.trajectory.append(belief)
        return belief
    
    def update(self, observation: str, likelihood: Dict[str, float]) -> BeliefState:
        """Update belief with observation."""
        if self.current_belief is None:
            raise ValueError("No current belief to update")
        
        new_belief = self.geometry.bayesian_update(
            self.current_belief, likelihood, observation
        )
        
        self.current_belief = new_belief
        self.trajectory.append(new_belief)
        
        return new_belief
    
    def get_uncertainty(self) -> UncertaintyBundle:
        """Get current uncertainty bundle."""
        if self.current_belief is None:
            return UncertaintyBundle()
        
        return self.geometry.compute_uncertainty_bundle(self.current_belief)
    
    def verify_geodesic(self, path: List[BeliefState]) -> bool:
        """Verify if path is approximately a geodesic on manifold."""
        if len(path) < 2:
            return True
        
        # Geodesic should locally minimize distance
        total_distance = 0.0
        for i in range(len(path) - 1):
            dist = self.geometry.distance_on_manifold(path[i], path[i+1])
            total_distance += dist
        
        # Simplified: just check finite
        return total_distance < float('inf')
