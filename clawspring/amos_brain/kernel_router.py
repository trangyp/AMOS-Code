"""AMOS Kernel Router - Routes tasks to appropriate cognitive kernels."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
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


class KernelRouter:
    """Routes incoming tasks to appropriate AMOS kernels."""

    DOMAIN_KEYWORDS = {
        "software": ["code", "program", "function", "class", "bug", "fix", "implement"],
        "ai": ["model", "train", "inference", "llm", "neural", "predict"],
        "cloud": ["deploy", "server", "aws", "azure", "gcp", "infrastructure"],
        "logic": ["analyze", "reason", "logic", "structure", "framework"],
        "ubi": ["biological", "nervous", "somatic", "health", "neuro"],
    }

    def __init__(self, brain_loader: BrainLoader):
        self.brain = brain_loader

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

        return TaskIntent(
            primary_domain=detected_domains[0],
            secondary_domains=detected_domains[1:] if len(detected_domains) > 1 else [],
            risk_level=risk_level,
            requires_reasoning=requires_reasoning,
            requires_code=requires_code,
            requires_memory=requires_memory,
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
            f"Active Kernels ({len(kernels)}):",
        ]

        for k in kernels:
            req_marker = " [required]" if k.required else ""
            lines.append(f"  - {k.name} (priority {k.priority}){req_marker}")

        return "\n".join(lines)
