"""AMOS Kernel Router - Routes tasks to appropriate cognitive kernels."""

from __future__ import annotations

from dataclasses import dataclass


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
        "software": ["code", "program", "function", "bug", "fix", "implement"],
        "ai": ["model", "train", "inference", "llm", "neural", "predict"],
        "cloud": ["deploy", "server", "aws", "azure", "gcp", "infra"],
        "logic": ["analyze", "reason", "logic", "structure", "framework"],
        "ubi": ["biological", "nervous", "somatic", "health", "neuro"],
        "psychology": ["emotion", "behavior", "mind", "mental", "cognitive"],
    }

    DOMAIN_ENGINE_HINTS = {
        "software": [
            "AMOS_Engineering_And_Mathematics_Engine",
            "AMOS_Design_Language_Engine",
        ],
        "ai": [
            "AMOS_Signal_Processing_Engine",
            "AMOS_Engineering_And_Mathematics_Engine",
        ],
        "cloud": [
            "AMOS_Electrical_Power_Engine",
            "AMOS_Mechanical_Structural_Engine",
        ],
        "logic": [
            "AMOS_Deterministic_Logic_And_Law_Engine",
            "AMOS_Strategy_Game_Engine",
        ],
        "ubi": [
            "AMOS_Biology_And_Cognition_Engine",
        ],
        "psychology": [
            "AMOS_Society_Culture_Engine",
            "AMOS_Biology_And_Cognition_Engine",
        ],
    }

    def __init__(self, brain_loader):
        self.brain = brain_loader

    def parse_intent(self, task_description: str) -> TaskIntent:
        """Parse task description to determine intent."""
        task_lower = task_description.lower()

        # Detect domains
        detected_domains = []
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            if any(kw in task_lower for kw in keywords):
                detected_domains.append(domain)

        # Default to logic if no domain detected
        if not detected_domains:
            detected_domains = ["logic"]

        # Determine risk level
        risk_level = "low"
        high_risk_terms = ["medical", "legal", "financial", "security", "prod"]
        if any(term in task_lower for term in high_risk_terms):
            risk_level = "high"
        elif "design" in task_lower or "architecture" in task_lower:
            risk_level = "medium"

        # Determine requirements
        requires_code = any(
            kw in task_lower
            for kw in [
                "code",
                "implement",
                "write",
                "bug",
                "fix",
                "refactor",
                "debug",
                "function",
                "class",
            ]
        )
        requires_reasoning = any(
            kw in task_lower
            for kw in ["analyze", "design", "plan", "architecture", "review", "compare"]
        )
        requires_memory = any(kw in task_lower for kw in ["remember", "previous", "context"])

        return TaskIntent(
            primary_domain=detected_domains[0],
            secondary_domains=detected_domains[1:] if len(detected_domains) > 1 else [],
            risk_level=risk_level,
            requires_reasoning=requires_reasoning,
            requires_code=requires_code,
            requires_memory=requires_memory,
        )

    def route(self, task_description: str) -> list[dict]:
        """Route task to appropriate engines/kernels."""
        intent = self.parse_intent(task_description)

        # Get available engines from brain
        engines = self.brain.list_engines() if self.brain else []
        engine_set = set(engines)

        active_engines = []
        seen = set()
        for domain in [intent.primary_domain] + intent.secondary_domains:
            for engine_name in self.DOMAIN_ENGINE_HINTS.get(domain, []):
                if engine_name in engine_set and engine_name not in seen:
                    active_engines.append(
                        {
                            "id": engine_name,
                            "name": engine_name,
                            "domain": domain,
                        }
                    )
                    seen.add(engine_name)

        # Fallback to logic-safe engines if nothing matched
        if not active_engines:
            for engine_name in [
                "AMOS_Deterministic_Logic_And_Law_Engine",
                "AMOS_Engineering_And_Mathematics_Engine",
                "AMOS_Design_Language_Engine",
            ]:
                if engine_name in engine_set and engine_name not in seen:
                    active_engines.append(
                        {
                            "id": engine_name,
                            "name": engine_name,
                            "domain": intent.primary_domain,
                        }
                    )
                    seen.add(engine_name)

        return active_engines

    def get_kernel_chain(self, task_description: str) -> list[str]:
        """Get ordered list of kernel IDs for a task."""
        engines = self.route(task_description)
        return [e["id"] for e in engines]

    def explain_routing(self, task_description: str) -> str:
        """Generate human-readable explanation of routing decision."""
        intent = self.parse_intent(task_description)
        engines = self.route(task_description)

        lines = [
            f"Task Domain: {intent.primary_domain}",
            f"Secondary Domains: {', '.join(intent.secondary_domains) or 'none'}",
            f"Risk Level: {intent.risk_level}",
            f"Requires Code: {intent.requires_code}",
            f"Requires Reasoning: {intent.requires_reasoning}",
            "",
            f"Active Engines ({len(engines)}):",
        ]

        for e in engines[:10]:  # Limit to 10
            lines.append(f"  - {e['name']} (domain: {e['domain']})")

        if len(engines) > 10:
            lines.append(f"  ... and {len(engines) - 10} more")

        return "\n".join(lines)


# Global router instance
_router_instance: KernelRouter | None = None


def get_kernel_router() -> KernelRouter:
    """Get or create global kernel router instance."""
    global _router_instance
    if _router_instance is None:
        from .loader import get_brain

        _router_instance = KernelRouter(get_brain())
    return _router_instance
