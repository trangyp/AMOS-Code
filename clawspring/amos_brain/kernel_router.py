"""AMOS Kernel Router - Routes tasks to appropriate cognitive kernels."""

from dataclasses import dataclass, field
from typing import Any

from .loader import BrainLoader, KernelConfig


@dataclass
class TaskIntent:
    """Parsed task intent for routing decisions."""

    primary_domain: str
    secondary_domains: list[str]
    risk_level: str
    requires_reasoning: bool
    requires_code: bool
    requires_memory: bool
    mathematical_domains: list[str] = field(default_factory=list)
    recommended_frameworks: list[str] = field(default_factory=list)


class KernelRouter:
    """Routes incoming tasks to appropriate AMOS kernels."""

    DOMAIN_KEYWORDS = {
        "software": ["code", "program", "function", "class", "bug", "fix", "implement"],
        "ai": ["model", "train", "inference", "llm", "neural", "predict"],
        "cloud": ["deploy", "server", "aws", "azure", "gcp", "infrastructure"],
        "logic": ["analyze", "reason", "logic", "structure", "framework"],
        "ubi": ["biological", "nervous", "somatic", "health", "neuro"],
        "design": ["design", "layout", "spacing", "typography", "ui", "ux"],
        "security": ["encrypt", "decrypt", "auth", "jwt", "rsa", "oauth"],
        "distributed": ["consensus", "raft", "kubernetes", "distributed", "cluster"],
    }

    def __init__(self, brain_loader: BrainLoader):
        self.brain = brain_loader
        self._math_engine: Any = None
        self._initialize_math_engine()

    def _initialize_math_engine(self) -> None:
        """Initialize mathematical framework engine for enhanced routing."""
        try:
            from .mathematical_framework_engine import get_framework_engine

            self._math_engine = get_framework_engine()
        except Exception:
            self._math_engine = None

    def parse_intent(self, task_description: str) -> TaskIntent:
        """Parse task description to determine intent."""
        task_lower = task_description.lower()

        # Detect domains
        detected_domains = []
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            if any(kw in task_lower for kw in keywords):
                detected_domains.append(domain)

        if not detected_domains:
            detected_domains = ["logic"]

        # Determine risk level
        risk_level = "low"
        high_risk_terms = ["medical", "legal", "financial", "security", "production"]
        if any(term in task_lower for term in high_risk_terms):
            risk_level = "high"

        # Determine requirements
        requires_code = any(kw in task_lower for kw in ["code", "implement", "write"])
        requires_reasoning = any(kw in task_lower for kw in ["analyze", "design", "structure"])
        requires_memory = any(kw in task_lower for kw in ["remember", "previous", "context"])

        # Enhanced detection with mathematical framework engine
        math_domains: list[str] = []
        recommended_frameworks: list[str] = []
        if self._math_engine:
            try:
                math_analysis = self._math_engine.analyze_architecture(task_description)
                math_domains = math_analysis.get("detected_domains", [])
                recommended_frameworks = math_analysis.get("recommended_frameworks", [])
                # Merge mathematical domains with detected domains
                for domain in math_domains:
                    domain_lower = domain.lower().replace("/", "_").replace(" ", "_")
                    if domain_lower not in detected_domains:
                        detected_domains.append(domain_lower)
            except Exception:
                pass

        return TaskIntent(
            primary_domain=detected_domains[0],
            secondary_domains=detected_domains[1:] if len(detected_domains) > 1 else [],
            risk_level=risk_level,
            requires_reasoning=requires_reasoning,
            requires_code=requires_code,
            requires_memory=requires_memory,
            mathematical_domains=math_domains,
            recommended_frameworks=recommended_frameworks,
        )

    def route(self, task_description: str) -> list[KernelConfig]:
        """Route task to appropriate kernels."""
        intent = self.parse_intent(task_description)

        # Start with required kernels
        active_kernels = self.brain.get_required_kernels()
        active_ids = {k.id for k in active_kernels}

        # Find matching kernels for domains
        domains = [intent.primary_domain] + intent.secondary_domains
        domain_kernels = self.brain.get_kernels_for_domains(domains)

        for kernel in domain_kernels:
            if kernel.id not in active_ids:
                active_kernels.append(kernel)
                active_ids.add(kernel.id)

        # Sort by priority
        active_kernels.sort(key=lambda x: x.priority, reverse=True)

        return active_kernels

    def explain_routing(self, task_description: str) -> str:
        """Generate human-readable explanation of routing decision."""
        intent = self.parse_intent(task_description)
        kernels = self.route(task_description)

        lines = [
            f"Task Domain: {intent.primary_domain}",
            f"Risk Level: {intent.risk_level}",
        ]

        # Add mathematical analysis if available
        if intent.mathematical_domains:
            lines.append(f"Mathematical Domains: {', '.join(intent.mathematical_domains)}")
        if intent.recommended_frameworks:
            lines.append(f"Recommended Frameworks: {', '.join(intent.recommended_frameworks)}")

        lines.append(f"Active Kernels ({len(kernels)}):")

        for k in kernels:
            req_marker = " [required]" if k.required else ""
            lines.append(f"  - {k.name} (priority {k.priority}){req_marker}")

        return "\n".join(lines)
