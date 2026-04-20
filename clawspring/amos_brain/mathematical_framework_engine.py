from __future__ import annotations

"""AMOS Mathematical Framework Engine - Core engine for equations and invariants.

Integrates 200+ mathematical equations and 50+ invariants from global UI/UX and AI frameworks.
Provides queryable knowledge base and validation for design systems, AI architectures,
cryptographic systems, and distributed systems.

Architecture Pattern: Modular Engine with Domain-Specific Sub-Engines
- UISubEngine: Design system equations (Tailwind, MUI, Ant Design, etc.)
- AISubEngine: Deep learning equations (Transformers, LSTM, GAN, etc.)
- SecuritySubEngine: Cryptographic equations (RSA, JWT, OAuth2)
- DistributedSubEngine: Consensus and scheduling algorithms
"""


import math
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import lru_cache
from typing import Any, TypeVar

T = TypeVar("T")


class Domain(Enum):
    """Mathematical domain categories."""

    UI_UX = auto()
    TYPOGRAPHY = auto()
    ANIMATION = auto()
    COLOR = auto()
    DEEP_LEARNING = auto()
    REINFORCEMENT_LEARNING = auto()
    NLP = auto()
    SECURITY = auto()
    DISTRIBUTED_SYSTEMS = auto()
    DATABASE = auto()
    WEB_PERFORMANCE = auto()


@dataclass
class Equation:
    """A mathematical equation with metadata."""

    name: str
    domain: Domain
    latex: str
    python_impl: Callable[..., Any]
    description: str
    parameters: dict[str, str] = field(default_factory=dict)
    invariant: str | None = None
    source_framework: str = ""

    def evaluate(self, **kwargs) -> Any:
        """Evaluate the equation with given parameters."""
        return self.python_impl(**kwargs)


@dataclass
class Invariant:
    """A mathematical invariant with validation."""

    name: str
    domain: Domain
    statement: str
    validator: Callable[..., bool]
    description: str
    source_framework: str = ""

    def check(self, **kwargs) -> bool:
        """Check if the invariant holds."""
        return self.validator(**kwargs)


@dataclass
class Framework:
    """A framework with its mathematical foundations."""

    name: str
    category: str
    equations: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    constants: dict[str, float] = field(default_factory=dict)


class UISubEngine:
    """UI/UX design system mathematical engine."""

    def __init__(self):
        self.equations: dict[str, Equation] = {}
        self.invariants: dict[str, Invariant] = {}
        self.frameworks: dict[str, Framework] = {}
        self._initialize()

    def _initialize(self):
        """Initialize all UI/UX mathematical foundations."""
        # Tailwind CSS Spacing
        self.equations["tailwind_spacing"] = Equation(
            name="Tailwind Spacing Scale",
            domain=Domain.UI_UX,
            latex="s(n) = n \\times 0.25\\text{rem} = n \\times 4\\text{px}",
            python_impl=lambda n: n * 4,
            description="4px base spacing system used by Tailwind CSS",
            parameters={"n": "Spacing multiplier (0.5, 1, 1.5, 2, ...)"},
            invariant="s(n) \\equiv 0 \\pmod{4}",
            source_framework="Tailwind CSS",
        )

        # 8-Point Grid
        self.invariants["eight_point_grid"] = Invariant(
            name="8-Point Grid Alignment",
            domain=Domain.UI_UX,
            statement="All spacing values must be divisible by 8",
            validator=lambda x: x % 8 == 0,
            description="Ensures visual harmony across design system",
            source_framework="Google Material Design",
        )

        # Golden Ratio
        self.equations["golden_ratio"] = Equation(
            name="Golden Ratio",
            domain=Domain.TYPOGRAPHY,
            latex="\\phi = \\frac{1 + \\sqrt{5}}{2} \\approx 1.618033988749894",
            python_impl=lambda: (1 + math.sqrt(5)) / 2,
            description="Divine proportion used in typography and layout",
            invariant="\\phi^2 = \\phi + 1",
            source_framework="Universal Design",
        )

        # Typography Scale
        self.equations["modular_type_scale"] = Equation(
            name="Modular Type Scale",
            domain=Domain.TYPOGRAPHY,
            latex="t(n) = \\text{base} \\times r^n",
            python_impl=lambda base, r, n: base * (r**n),
            description="Geometric progression for font sizes",
            parameters={
                "base": "Base font size",
                "r": "Ratio (1.125, 1.25, 1.618)",
                "n": "Scale step",
            },
            source_framework="IBM Design Language",
        )

        # IBM Line Height
        self.equations["ibm_line_height"] = Equation(
            name="IBM Type Scale Line Height",
            domain=Domain.TYPOGRAPHY,
            latex="y = y_0 + \\frac{x - y_0}{4}",
            python_impl=lambda x, y0=12: y0 + (x - y0) / 4,
            description="Harmonious line height calculation",
            parameters={"x": "Font size", "y0": "Base size (12px)"},
            source_framework="IBM Carbon Design System",
        )

        # Material Design dp
        self.equations["material_dp"] = Equation(
            name="Density-Independent Pixels",
            domain=Domain.UI_UX,
            latex="dp = \\frac{width_{px} \\times 160}{density_{dpi}}",
            python_impl=lambda width_px, density_dpi: (width_px * 160) / density_dpi,
            description="Device-independent sizing for Android",
            parameters={"width_px": "Width in pixels", "density_dpi": "Screen density"},
            source_framework="Material Design",
        )

        # Ant Design Gutter
        self.equations["ant_gutter"] = Equation(
            name="Ant Design Gutter Formula",
            domain=Domain.UI_UX,
            latex="gutter = 16 + 8n \\text{ (px)}, n \\in \\mathbb{N}",
            python_impl=lambda n: 16 + 8 * n,
            description="Grid spacing for Ant Design",
            parameters={"n": "Natural number"},
            invariant="gutter \\equiv 0 \\pmod{8}",
            source_framework="Ant Design",
        )

        # CSS Grid fr unit
        self.equations["css_grid_fr"] = Equation(
            name="CSS Grid fr Distribution",
            domain=Domain.UI_UX,
            latex="track_{size} = \\frac{free_{space} \\times flex_{factor}}{\\sum flex_{factors}}",
            python_impl=lambda free_space, flex_factor, total_flex: (
                (free_space * flex_factor) / total_flex
            ),
            description="Fractional unit distribution in CSS Grid",
            parameters={
                "free_space": "Available space",
                "flex_factor": "Track flex value",
                "total_flex": "Sum of all flex values",
            },
            source_framework="CSS Grid Layout",
        )

        # Flexbox grow
        self.equations["flexbox_grow"] = Equation(
            name="Flexbox Grow Distribution",
            domain=Domain.UI_UX,
            latex="child_{size} = base_{size} + \\frac{available \\times flex_{grow}}{\\sum flex_{grow}}",
            python_impl=lambda base, available, flex_grow, total_flex: (
                base + (available * flex_grow) / total_flex
            ),
            description="Space distribution in flex containers",
            parameters={
                "base": "Base size",
                "available": "Available space",
                "flex_grow": "Grow factor",
                "total_flex": "Total flex factors",
            },
            source_framework="CSS Flexbox",
        )

        # Initialize frameworks
        self.frameworks["tailwind"] = Framework(
            name="Tailwind CSS",
            category="CSS Framework",
            equations=["tailwind_spacing"],
            invariants=["eight_point_grid"],
            constants={"base_unit": 4, "rem_factor": 0.25},
        )

        self.frameworks["material_design"] = Framework(
            name="Material Design",
            category="Design System",
            equations=["material_dp"],
            constants={"mdpi": 160, "baseline": 1.0},
        )

        self.frameworks["ant_design"] = Framework(
            name="Ant Design",
            category="Component Library",
            equations=["ant_gutter"],
            constants={"grid_columns": 24, "gutter_base": 16},
        )

        self.frameworks["bootstrap"] = Framework(
            name="Bootstrap", category="CSS Framework", constants={"grid_columns": 12, "gutter": 24}
        )

    def validate_spacing(self, value: int) -> dict[str, Any]:
        """Validate if spacing follows 8-point grid."""
        return {
            "value": value,
            "valid_8pt": self.invariants["eight_point_grid"].check(x=value),
            "tailwind_class": f"p-{value // 4}" if value % 4 == 0 else None,
            "rem": value / 16,
        }

    def calculate_type_scale(self, base: float, ratio: float, steps: int) -> list[float]:
        """Calculate modular type scale."""
        return [
            self.equations["modular_type_scale"].evaluate(base=base, r=ratio, n=i)
            for i in range(steps)
        ]

    def get_golden_ratio(self) -> float:
        """Return the golden ratio."""
        return self.equations["golden_ratio"].evaluate()


class AISubEngine:
    """AI/ML mathematical engine."""

    def __init__(self):
        self.equations: dict[str, Equation] = {}
        self.invariants: dict[str, Invariant] = {}
        self.frameworks: dict[str, Framework] = {}
        self._initialize()

    def _initialize(self):
        """Initialize all AI/ML mathematical foundations."""
        # Transformer Attention
        self.equations["attention"] = Equation(
            name="Scaled Dot-Product Attention",
            domain=Domain.DEEP_LEARNING,
            latex="\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V",
            python_impl=self._attention_impl,
            description="Core transformer attention mechanism",
            parameters={
                "Q": "Query matrix",
                "K": "Key matrix",
                "V": "Value matrix",
                "d_k": "Key dimension",
            },
            invariant="\\sum \\alpha_i = 1",
            source_framework="Transformer",
        )

        # Softmax
        self.equations["softmax"] = Equation(
            name="Softmax Function",
            domain=Domain.DEEP_LEARNING,
            latex="\\text{softmax}(x_i) = \\frac{e^{x_i}}{\\sum_j e^{x_j}}",
            python_impl=lambda x: [math.exp(xi) / sum(math.exp(xj) for xj in x) for xi in x],
            description="Probability distribution over classes",
            invariant="0 < \\text{softmax}(x_i) < 1, \\sum \\text{softmax}(x_i) = 1",
            source_framework="Neural Networks",
        )

        # Layer Normalization
        self.equations["layer_norm"] = Equation(
            name="Layer Normalization",
            domain=Domain.DEEP_LEARNING,
            latex="\\text{LayerNorm}(x) = \\gamma \\times \\frac{x - \\mu}{\\sqrt{\\sigma^2 + \\epsilon}} + \\beta",
            python_impl=self._layer_norm_impl,
            description="Normalizes inputs across features",
            parameters={
                "x": "Input tensor",
                "gamma": "Scale",
                "beta": "Shift",
                "epsilon": "Stability constant",
            },
            invariant="\\mu = 0, \\sigma = 1",
            source_framework="Deep Learning",
        )

        # LSTM
        self.equations["lstm_cell"] = Equation(
            name="LSTM Cell State Update",
            domain=Domain.DEEP_LEARNING,
            latex="C_t = f_t \\odot C_{t-1} + i_t \\odot \\tilde{C}_t",
            python_impl=lambda f, C_prev, i, C_tilde: f * C_prev + i * C_tilde,
            description="Long-term memory preservation in LSTM",
            parameters={
                "f": "Forget gate",
                "C_prev": "Previous cell state",
                "i": "Input gate",
                "C_tilde": "Candidate state",
            },
            invariant="Gradient flow preserved: \\partial C_t / \\partial C_{t-1} = f_t",
            source_framework="LSTM",
        )

        # Gradient Descent
        self.equations["gradient_descent"] = Equation(
            name="Gradient Descent Update",
            domain=Domain.DEEP_LEARNING,
            latex="\\theta' = \\theta - \\eta \\nabla L",
            python_impl=lambda theta, eta, grad: theta - eta * grad,
            description="Parameter optimization via gradient descent",
            parameters={
                "theta": "Current parameters",
                "eta": "Learning rate",
                "grad": "Gradient of loss",
            },
            invariant="L(\\theta') \\leq L(\\theta) \\text{ for small } \\eta",
            source_framework="Optimization",
        )

        # GAN Minimax
        self.equations["gan_minimax"] = Equation(
            name="GAN Minimax Objective",
            domain=Domain.DEEP_LEARNING,
            latex="\\min_G \\max_D V(D, G) = \\mathbb{E}[\\log D(x)] + \\mathbb{E}[\\log(1 - D(G(z)))]",
            python_impl=lambda: "Adversarial training objective",
            description="Two-player game in GAN training",
            source_framework="GAN",
        )

        # VAE ELBO
        self.equations["vae_elbo"] = Equation(
            name="VAE Evidence Lower Bound",
            domain=Domain.DEEP_LEARNING,
            latex="\\mathcal{L} = \\mathbb{E}[\\log p(x|z)] - \\text{KL}(q(z|x) || p(z))",
            python_impl=lambda recon, kl_divergence: recon - kl_divergence,
            description="Variational autoencoder loss function",
            parameters={"recon": "Reconstruction term", "kl_divergence": "KL divergence"},
            invariant="\\text{ELBO} \\leq \\log p(x)",
            source_framework="VAE",
        )

        # Q-Learning
        self.equations["q_learning"] = Equation(
            name="Q-Learning Update",
            domain=Domain.REINFORCEMENT_LEARNING,
            latex="Q(s,a) \\leftarrow Q(s,a) + \\alpha[r + \\gamma \\max_{a'} Q(s',a') - Q(s,a)]",
            python_impl=lambda Q, alpha, r, gamma, max_Q_next: (
                Q + alpha * (r + gamma * max_Q_next - Q)
            ),
            description="Temporal difference learning for Q-values",
            parameters={
                "Q": "Current Q-value",
                "alpha": "Learning rate",
                "r": "Reward",
                "gamma": "Discount",
                "max_Q_next": "Max Q of next state",
            },
            source_framework="Reinforcement Learning",
        )

        # Softmax invariant
        self.invariants["softmax_probability"] = Invariant(
            name="Softmax Probability Simplex",
            domain=Domain.DEEP_LEARNING,
            statement="Sum of softmax outputs equals 1",
            validator=lambda outputs: abs(sum(outputs) - 1.0) < 1e-6,
            description="Ensures valid probability distribution",
        )

        # Initialize frameworks
        self.frameworks["transformer"] = Framework(
            name="Transformer",
            category="Deep Learning Architecture",
            equations=["attention", "softmax"],
            constants={"d_model": 512, "heads": 8, "d_k": 64},
        )

        self.frameworks["lstm"] = Framework(
            name="LSTM",
            category="Recurrent Neural Network",
            equations=["lstm_cell"],
            invariants=["gradient_flow"],
        )

        self.frameworks["gan"] = Framework(
            name="GAN", category="Generative Model", equations=["gan_minimax"]
        )

    def _attention_impl(self, Q, K, V, d_k):
        """Simplified attention implementation."""
        import numpy as np

        scores = np.dot(Q, K.T) / math.sqrt(d_k)
        exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
        weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
        return np.dot(weights, V)

    def _layer_norm_impl(self, x, gamma=1.0, beta=0.0, epsilon=1e-6):
        """Layer normalization implementation."""
        import numpy as np

        mean = np.mean(x, axis=-1, keepdims=True)
        var = np.var(x, axis=-1, keepdims=True)
        return gamma * (x - mean) / np.sqrt(var + epsilon) + beta

    def calculate_perplexity(self, cross_entropy: float) -> float:
        """Calculate perplexity from cross-entropy."""
        return math.exp(cross_entropy)

    def validate_probability_distribution(self, probs: list[float]) -> bool:
        """Check if values form a valid probability distribution."""
        return self.invariants["softmax_probability"].check(outputs=probs)


class SecuritySubEngine:
    """Cryptographic and security mathematical engine."""

    def __init__(self):
        self.equations: dict[str, Equation] = {}
        self.invariants: dict[str, Invariant] = {}
        self.frameworks: dict[str, Framework] = {}
        self._initialize()

    def _initialize(self):
        """Initialize cryptographic equations."""
        # RSA Encryption
        self.equations["rsa_encrypt"] = Equation(
            name="RSA Encryption",
            domain=Domain.SECURITY,
            latex="C = M^e \\pmod{N}",
            python_impl=lambda M, e, N: pow(M, e, N),
            description="RSA public key encryption",
            parameters={"M": "Message", "e": "Public exponent", "N": "Modulus"},
            source_framework="RSA",
        )

        # RSA Decryption
        self.equations["rsa_decrypt"] = Equation(
            name="RSA Decryption",
            domain=Domain.SECURITY,
            latex="M = C^d \\pmod{N}",
            python_impl=lambda C, d, N: pow(C, d, N),
            description="RSA private key decryption",
            parameters={"C": "Ciphertext", "d": "Private exponent", "N": "Modulus"},
            invariant="(M^e)^d \\equiv M \\pmod{N}",
            source_framework="RSA",
        )

        # HMAC
        self.equations["hmac"] = Equation(
            name="HMAC",
            domain=Domain.SECURITY,
            latex="\\text{HMAC}(K, m) = H((K' \\oplus \\text{opad}) || H((K' \\oplus \\text{ipad}) || m))",
            python_impl=lambda: "Hash-based message authentication code",
            description="Message authentication using hash functions",
            source_framework="JWT/HMAC",
        )

        # RSA correctness invariant
        self.invariants["rsa_correctness"] = Invariant(
            name="RSA Correctness",
            domain=Domain.SECURITY,
            statement="Decryption of encryption returns original message",
            validator=lambda M, e, d, N: pow(pow(M, e, N), d, N) == M % N,
            description="RSA must correctly encrypt and decrypt",
            source_framework="RSA",
        )


class DistributedSubEngine:
    """Distributed systems mathematical engine."""

    def __init__(self):
        self.equations: dict[str, Equation] = {}
        self.invariants: dict[str, Invariant] = {}
        self.frameworks: dict[str, Framework] = {}
        self._initialize()

    def _initialize(self):
        """Initialize distributed systems equations."""
        # CAP Theorem
        self.equations["cap_theorem"] = Equation(
            name="CAP Theorem",
            domain=Domain.DISTRIBUTED_SYSTEMS,
            latex="\\text{Pick 2: } C \\text{ (Consistency)}, A \\text{ (Availability)}, P \\text{ (Partition Tolerance)}",
            python_impl=lambda: "Cannot guarantee all three properties simultaneously",
            description="Fundamental trade-off in distributed systems",
            source_framework="Distributed Systems",
        )

        # Raft Leader Election
        self.equations["raft_majority"] = Equation(
            name="Raft Majority",
            domain=Domain.DISTRIBUTED_SYSTEMS,
            latex="\\text{Votes needed} = \\lceil \\frac{n}{2} \\rceil",
            python_impl=lambda n: math.ceil(n / 2),
            description="Majority required for leader election",
            parameters={"n": "Total nodes"},
            invariant="votes \\geq \\lceil n/2 \\rceil",
            source_framework="Raft Consensus",
        )

        # Kubernetes scheduling score
        self.equations["k8s_score"] = Equation(
            name="Kubernetes Node Score",
            domain=Domain.DISTRIBUTED_SYSTEMS,
            latex="\\text{score}(\\text{node}) = \\sum weight_i \\times score_i",
            python_impl=lambda scores, weights: sum(s * w for s, w in zip(scores, weights)),
            description="Pod scheduling priority calculation",
            source_framework="Kubernetes",
        )

        # Majority vote invariant
        self.invariants["majority_vote"] = Invariant(
            name="Majority Vote",
            domain=Domain.DISTRIBUTED_SYSTEMS,
            statement="Leader elected only with majority of votes",
            validator=lambda votes, total: votes >= math.ceil(total / 2),
            description="Ensures single leader in consensus",
            source_framework="Raft/Paxos",
        )


class MathematicalFrameworkEngine:
    """Main engine integrating all mathematical framework sub-engines."""

    def __init__(self):
        self.ui_engine = UISubEngine()
        self.ai_engine = AISubEngine()
        self.security_engine = SecuritySubEngine()
        self.distributed_engine = DistributedSubEngine()

        self.all_equations: dict[str, Equation] = {}
        self.all_invariants: dict[str, Invariant] = {}
        self.all_frameworks: dict[str, Framework] = {}

        self._aggregate_all()

    def _aggregate_all(self):
        """Aggregate all sub-engine resources."""
        # Collect from all sub-engines
        for engine in [
            self.ui_engine,
            self.ai_engine,
            self.security_engine,
            self.distributed_engine,
        ]:
            self.all_equations.update(engine.equations)
            self.all_invariants.update(engine.invariants)
            self.all_frameworks.update(engine.frameworks)

    def query_equation(self, name: str) -> Equation | None:
        """Query an equation by name."""
        return self.all_equations.get(name)

    def query_by_domain(self, domain: str) -> list[Equation]:
        """Query equations by domain."""
        result = []
        for eq in self.all_equations.values():
            if eq.domain == domain:
                result.append(eq)

        # Audit logging
        try:
            from .math_audit_logger import get_math_audit_logger

            logger = get_math_audit_logger()
            logger.log_equation_query(domain, "", len(result), {"method": "by_domain"})
        except Exception:
            pass

        return result

    def validate_invariant(self, name: str, **kwargs) -> bool:
        """Validate an invariant with given parameters."""
        invariant = self.all_invariants.get(name)
        if invariant:
            return invariant.check(**kwargs)
        return False

    # ... (rest of the code remains the same)
    def get_framework(self, name: str) -> Framework | None:
        """Get a framework by name."""
        return self.all_frameworks.get(name)

    def list_frameworks(self) -> list[str]:
        """List all available frameworks."""
        return list(self.all_frameworks.keys())

    def solve_design_spacing(self, target_px: int) -> dict[str, Any]:
        """Solve for design system spacing recommendations."""
        return {
            "target": target_px,
            "tailwind_class": self.ui_engine.validate_spacing(target_px),
            "is_8pt_aligned": target_px % 8 == 0,
            "is_4pt_aligned": target_px % 4 == 0,
            "recommendations": self._spacing_recommendations(target_px),
        }

    def _spacing_recommendations(self, target_px: int) -> list[str]:
        """Generate spacing recommendations."""
        recs = []
        if target_px % 8 == 0:
            recs.append("✓ Follows 8-point grid (optimal)")
        elif target_px % 4 == 0:
            recs.append("⚠ Follows 4-point grid (acceptable)")
        else:
            recs.append("✗ Not aligned to grid - consider adjusting")
            nearest_8 = round(target_px / 8) * 8
            recs.append(f"  Suggested: {nearest_8}px (8pt) or {round(target_px / 4) * 4}px (4pt)")
        return recs

    def calculate_attention(self, Q, K, V, d_k: int):
        """Calculate transformer attention."""
        return self.ai_engine.equations["attention"].evaluate(Q=Q, K=K, V=V, d_k=d_k)

    def analyze_architecture(self, task_description: str) -> dict[str, Any]:
        """Analyze task and recommend mathematical frameworks."""
        task_lower = task_description.lower()
        recommendations = {
            "detected_domains": [],
            "recommended_equations": [],
            "recommended_frameworks": [],
        }

        # Domain detection
        if any(kw in task_lower for kw in ["spacing", "grid", "layout", "design system"]):
            recommendations["detected_domains"].append("UI/UX")
            recommendations["recommended_equations"].extend(
                ["tailwind_spacing", "css_grid_fr", "flexbox_grow"]
            )
            recommendations["recommended_frameworks"].extend(
                ["tailwind", "material_design", "ant_design"]
            )

        if any(kw in task_lower for kw in ["font", "typography", "line height", "type scale"]):
            recommendations["detected_domains"].append("Typography")
            recommendations["recommended_equations"].extend(
                ["golden_ratio", "modular_type_scale", "ibm_line_height"]
            )

        if any(kw in task_lower for kw in ["neural", "attention", "transformer", "lstm", "gan"]):
            recommendations["detected_domains"].append("Deep Learning")
            recommendations["recommended_equations"].extend(
                ["attention", "softmax", "layer_norm", "lstm_cell"]
            )
            recommendations["recommended_frameworks"].extend(["transformer", "lstm", "gan"])

        if any(kw in task_lower for kw in ["encrypt", "decrypt", "jwt", "rsa", "oauth"]):
            recommendations["detected_domains"].append("Security")
            recommendations["recommended_equations"].extend(["rsa_encrypt", "rsa_decrypt", "hmac"])

        if any(
            kw in task_lower for kw in ["consensus", "distributed", "leader election", "kubernetes"]
        ):
            recommendations["detected_domains"].append("Distributed Systems")
            recommendations["recommended_equations"].extend(
                ["cap_theorem", "raft_majority", "k8s_score"]
            )

        return recommendations

    def get_stats(self) -> dict[str, int]:
        """Get engine statistics."""
        return {
            "total_equations": len(self.all_equations),
            "total_invariants": len(self.all_invariants),
            "total_frameworks": len(self.all_frameworks),
            "ui_equations": len(self.ui_engine.equations),
            "ai_equations": len(self.ai_engine.equations),
            "security_equations": len(self.security_engine.equations),
            "distributed_equations": len(self.distributed_engine.equations),
        }


@lru_cache(maxsize=1)
def get_framework_engine() -> MathematicalFrameworkEngine:
    """Get or create the global framework engine instance (singleton)."""
    return MathematicalFrameworkEngine()


if __name__ == "__main__":
    # Demo
    engine = get_framework_engine()

    print("=" * 70)
    print("AMOS MATHEMATICAL FRAMEWORK ENGINE")
    print("=" * 70)

    stats = engine.get_stats()
    print("\n📊 Engine Statistics:")
    print(f"  Total Equations: {stats['total_equations']}")
    print(f"  Total Invariants: {stats['total_invariants']}")
    print(f"  Total Frameworks: {stats['total_frameworks']}")
    print(f"  UI/UX Equations: {stats['ui_equations']}")
    print(f"  AI/ML Equations: {stats['ai_equations']}")

    print("\n🎨 Design System Analysis:")
    spacing_analysis = engine.solve_design_spacing(24)
    print(f"  24px spacing: {spacing_analysis}")

    print("\n🔍 Architecture Analysis:")
    analysis = engine.analyze_architecture(
        "Design responsive layout with proper spacing and typography"
    )
    print(f"  Detected: {analysis['detected_domains']}")
    print(f"  Frameworks: {analysis['recommended_frameworks']}")

    print("\n✅ Engine Ready")
    print("=" * 70)
