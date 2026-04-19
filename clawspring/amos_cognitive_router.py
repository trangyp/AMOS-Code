"""AMOS Active Cognitive Router - Implements the brain's orchestration pattern."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TaskAnalysis:
    """Analysis of an incoming task per AMOS orchestration contract."""

    primary_domain: str
    risk_level: str  # low, medium, high, critical
    detected_domains: List[str]
    requires_reasoning: bool
    requires_code: bool
    requires_multi_agent: bool
    suggested_engines: List[str]
    law_violations: List[str] = field(default_factory=list)
    quadrant_check: Dict[str, bool] = field(default_factory=dict)


class CognitiveRouter:
    """Routes tasks through AMOS cognitive architecture."""

    # Domain detection patterns
    DOMAIN_PATTERNS = {
        "software": [
            "code",
            "program",
            "function",
            "class",
            "bug",
            "fix",
            "implement",
            "refactor",
            "debug",
        ],
        "ai_ml": [
            "model",
            "train",
            "inference",
            "llm",
            "neural",
            "predict",
            "embedding",
            "fine-tune",
        ],
        "infrastructure": [
            "deploy",
            "server",
            "aws",
            "azure",
            "gcp",
            "docker",
            "kubernetes",
            "cloud",
        ],
        "data": ["database", "sql", "query", "dataset", "csv", "json", "schema", "migration"],
        "security": [
            "auth",
            "encrypt",
            "vulnerability",
            "exploit",
            "penetration",
            "security",
            "cve",
        ],
        "design": ["architecture", "pattern", "structure", "diagram", "component", "interface"],
        "analysis": ["analyze", "review", "audit", "assess", "evaluate", "compare", "benchmark"],
        "documentation": ["readme", "doc", "documentation", "comment", "explain", "tutorial"],
        "testing": ["test", "unit test", "integration", "pytest", "jest", "coverage"],
        "ubi": ["biological", "nervous", "somatic", "health", "neuro", "organism"],
        "economics": ["finance", "budget", "cost", "revenue", "investment", "market"],
        "legal": ["compliance", "regulation", "gdpr", "contract", "liability", "ip"],
    }

    # High-risk terms
    HIGH_RISK_TERMS = [
        "medical",
        "clinical",
        "diagnosis",
        "treatment",
        "surgery",
        "legal advice",
        "attorney",
        "court",
        "lawsuit",
        "liability",
        "financial trading",
        "investment advice",
        "stock",
        "crypto trading",
        "weapon",
        "explosive",
        "surveillance",
        "national security",
        "production deploy",
        "live system",
        "customer data",
        "payment",
    ]

    # Critical risk terms
    CRITICAL_RISK_TERMS = [
        "life support",
        "medical device",
        "pacemaker",
        "insulin pump",
        "nuclear",
        "radiation",
        "missile",
        "weapon system",
    ]

    def __init__(self):
        self._global_laws: dict[str, Any] = None

    @property
    def global_laws(self) -> Dict[str, Any]:
        """Lazy-load global laws to prevent blocking during initialization."""
        if self._global_laws is None:
            self._global_laws = self._load_brain_laws()
        return self._global_laws

    def _load_brain_laws(self) -> Dict[str, Any]:
        """Load global laws from AMOS brain."""
        brain_path = (
            Path(__file__).resolve().parent.parent
            / "_AMOS_BRAIN/_LEGACY BRAIN/Core/AMOS_Os_Agent_v0.json"
        )
        try:
            with open(brain_path) as f:
                data = json.load(f)[0]
            components = data.get("components", {})
            brain_root = components.get("AMOS_BRAIN_ROOT.json", {})
            return brain_root.get("global_laws", {})
        except Exception:
            return {}

    def analyze(self, task_description: str) -> TaskAnalysis:
        """Analyze task per AMOS orchestration: identify domain and risk."""
        task_lower = task_description.lower()

        # 1. Detect domains
        detected_domains = []
        for domain, keywords in self.DOMAIN_PATTERNS.items():
            if any(kw in task_lower for kw in keywords):
                detected_domains.append(domain)

        if not detected_domains:
            detected_domains = ["general"]

        primary_domain = detected_domains[0]

        # 2. Assess risk
        risk_level = "low"
        if any(term in task_lower for term in self.CRITICAL_RISK_TERMS):
            risk_level = "critical"
        elif any(term in task_lower for term in self.HIGH_RISK_TERMS):
            risk_level = "high"
        elif primary_domain in ["security", "legal"]:
            risk_level = "medium"

        # 3. Determine requirements
        requires_code = any(
            kw in task_lower
            for kw in ["code", "implement", "write", "function", "class", "script", "program"]
        )
        requires_reasoning = any(
            kw in task_lower
            for kw in ["analyze", "design", "structure", "plan", "architecture", "review"]
        )
        requires_multi_agent = any(
            kw in task_lower
            for kw in ["brainstorm", "debate", "multiple", "team", "parallel", "fork"]
        )

        # 4. Suggest engines based on domain
        suggested_engines = self._suggest_engines(
            detected_domains, requires_code, requires_reasoning
        )

        # 4b. Apply feedback loop enhancement if available
        try:
            from amos_brain.feedback_loop import get_enhanced_engines

            primary = detected_domains[0] if detected_domains else "general"
            suggested_engines = get_enhanced_engines(primary, suggested_engines)
        except Exception:
            pass  # Silent fail if feedback not available

        # 5. Check Rule of 4 quadrants
        quadrant_check = self._check_quadrants(task_lower, detected_domains)

        # 6. Check for law violations
        law_violations = self._check_law_violations(task_lower)

        return TaskAnalysis(
            primary_domain=primary_domain,
            risk_level=risk_level,
            detected_domains=detected_domains,
            requires_reasoning=requires_reasoning,
            requires_code=requires_code,
            requires_multi_agent=requires_multi_agent,
            suggested_engines=suggested_engines,
            law_violations=law_violations,
            quadrant_check=quadrant_check,
        )

    def _suggest_engines(
        self, domains: List[str], requires_code: bool, requires_reasoning: bool
    ) -> List[str]:
        """Suggest cognitive engines based on task characteristics."""
        engines = []

        # Always include meta-logic for reasoning
        if requires_reasoning:
            engines.extend(
                [
                    "AMOS_Deterministic_Logic_And_Law_Engine",
                    "AMOS_Strategy_Game_Engine",
                ]
            )

        # Domain-specific engines
        domain_engine_map = {
            "software": ["AMOS_Engineering_And_Mathematics_Engine", "AMOS_Design_Language_Engine"],
            "ai_ml": ["AMOS_Signal_Processing_Engine", "AMOS_Engineering_And_Mathematics_Engine"],
            "infrastructure": ["AMOS_Electrical_Power_Engine", "AMOS_Mechanical_Structural_Engine"],
            "data": ["AMOS_Numerical_Methods_Engine"],
            "design": ["AMOS_Design_Language_Engine"],
            "ubi": ["AMOS_Biology_And_Cognition_Engine"],
            "economics": ["AMOS_Econ_Finance_Engine"],
            "legal": ["AMOS_Deterministic_Logic_And_Law_Engine"],
        }

        for domain in domains:
            if domain in domain_engine_map:
                engines.extend(domain_engine_map[domain])

        # Add emotion engine for high-stakes decisions
        if requires_reasoning and len(engines) > 2:
            engines.append("AMOS_Society_Culture_Engine")

        return list(dict.fromkeys(engines))  # Remove duplicates

    def _check_quadrants(self, task_lower: str, domains: List[str]) -> dict[str, bool]:
        """Check Rule of 4: biological, technical, economic, environmental."""
        return {
            "biological": any(d in ["ubi", "medical", "health"] for d in domains),
            "technical": any(d in ["software", "ai_ml", "infrastructure", "data"] for d in domains),
            "economic": any(d in ["economics", "business"] for d in domains)
            or "cost" in task_lower,
            "environmental": "environment" in task_lower or "sustainable" in task_lower,
        }

    def _check_law_violations(self, task_lower: str) -> List[str]:
        """Check for potential violations of AMOS global laws."""
        violations = []

        # L4: Absolute Structural Integrity - check for claims without evidence
        certainty_words = ["definitely", "guaranteed", "100% certain", "impossible to fail"]
        if any(word in task_lower for word in certainty_words):
            violations.append(
                "L4: Uncertainty not labeled - using certainty language without evidence"
            )

        # L5: Post-Theory Communication - check for ambiguous terms
        ambiguous_terms = ["spiritual", "energy field", "vibration", "quantum healing"]
        if any(term in task_lower for term in ambiguous_terms):
            violations.append("L5: Ambiguous language detected - prefer concrete mechanisms")

        return violations

    def apply_global_laws(self, analysis: TaskAnalysis) -> List[str]:
        """Apply AMOS global laws to task analysis."""
        guidance = []

        # L1: Law of Law
        if analysis.risk_level in ["high", "critical"]:
            guidance.append(
                "L1: High-risk task - verify against all applicable constraints before proceeding"
            )

        # L2: Rule of 2
        if analysis.requires_reasoning:
            guidance.append("L2: Check at least two contrasting perspectives before concluding")

        # L3: Rule of 4
        missing_quadrants = [q for q, checked in analysis.quadrant_check.items() if not checked]
        if analysis.risk_level in ["medium", "high", "critical"] and len(missing_quadrants) > 0:
            guidance.append(f"L3: Consider missing quadrants: {', '.join(missing_quadrants)}")

        # L4: Absolute Structural Integrity
        if analysis.law_violations:
            guidance.extend(analysis.law_violations)
        else:
            guidance.append("L4: Maintain structural integrity - label assumptions and uncertainty")

        # L5: Post-Theory Communication
        guidance.append("L5: Use clear, grounded, functionally interpretable language")

        # L6: UBI Alignment
        if analysis.quadrant_check.get("biological") or "organism" in str(
            analysis.detected_domains
        ):
            guidance.append("L6: Align with Unified Biological Intelligence principles")

        return guidance

    def build_cognitive_prompt(self, task_description: str, execute: bool = False) -> str:
        """Build a system prompt augmented with cognitive routing.

        Args:
            task_description: The task to analyze
            execute: If True, also execute through cognitive engines
        """
        analysis = self.analyze(task_description)
        laws_guidance = self.apply_global_laws(analysis)

        lines = [
            "# AMOS COGNITIVE ROUTING",
            "",
            f"Task Domain: {analysis.primary_domain}",
            f"Risk Level: {analysis.risk_level.upper()}",
            f"Detected Domains: {', '.join(analysis.detected_domains)}",
            "",
            "## Global Laws Guidance",
        ]

        for guidance in laws_guidance:
            lines.append(f"- {guidance}")

        if analysis.suggested_engines:
            lines.extend(
                [
                    "",
                    "## Active Cognitive Engines",
                ]
            )
            for engine in analysis.suggested_engines[:5]:
                lines.append(f"- {engine}")

        # Execute through engines if requested
        consensus_score = None
        exec_time_ms = 0.0
        recommendation = "Analyze with suggested engines"

        if execute and analysis.suggested_engines:
            try:
                # Use multi-agent orchestration for complex tasks
                if analysis.requires_multi_agent or len(analysis.suggested_engines) > 1:
                    from amos_brain.multi_agent_orchestrator import run_cognitive_consensus

                    consensus = run_cognitive_consensus(
                        task_description, analysis.suggested_engines[:4]
                    )
                    consensus_score = consensus.agreement_score
                    exec_time_ms = consensus.total_execution_time_ms
                    recommendation = consensus.recommended_action
                    lines.extend(
                        [
                            "",
                            "## Multi-Agent Consensus",
                            f"Agreement: {consensus.agreement_score:.0%} | "
                            f"Time: {consensus.total_execution_time_ms:.1f}ms | "
                            f"Perspectives: {len(consensus.perspectives)}",
                            "",
                            f"**{consensus.recommended_action}**",
                        ]
                    )
                    if consensus.dissenting_views:
                        lines.append("⚠️ Dissent detected - review perspectives")
                else:
                    from amos_brain.engine_executor import execute_cognitive_task

                    result = execute_cognitive_task(
                        task_description, analysis.suggested_engines[:3]
                    )
                    exec_time_ms = result.execution_time_ms
                    recommendation = f"Executed {len(result.engines_used)} engines"
                    lines.extend(
                        [
                            "",
                            "## Pre-execution Analysis",
                            f"Executed {len(result.engines_used)} engines "
                            f"in {result.execution_time_ms:.1f}ms",
                        ]
                    )
                    if result.violations_found:
                        lines.append("⚠️ Law violations detected - review required")
            except Exception:
                pass  # Silent fail if execution modules not available

        # Record to audit trail
        try:
            from amos_brain.cognitive_audit import record_cognitive_decision

            record_cognitive_decision(
                task=task_description,
                domain=analysis.primary_domain,
                risk_level=analysis.risk_level,
                engines=analysis.suggested_engines,
                consensus_score=consensus_score,
                laws=analysis.law_violations or [],
                violations=analysis.law_violations or [],
                exec_time_ms=exec_time_ms,
                recommendation=recommendation,
            )
        except Exception:
            pass  # Silent fail for non-critical audit

        if analysis.requires_multi_agent:
            lines.extend(
                [
                    "",
                    "## Multi-Agent Recommendation",
                    "Consider using /brainstorm for parallel perspectives",
                ]
            )

        lines.extend(
            [
                "",
                "## Task Processing",
                "Apply the above laws and route through suggested engines.",
                "---",
                "",
            ]
        )

        return "\n".join(lines)

    def explain_routing(self, task_description: str) -> str:
        """Generate human-readable explanation of routing decision."""
        analysis = self.analyze(task_description)

        lines = [
            f"Domain: {analysis.primary_domain}",
            f"Risk: {analysis.risk_level.upper()}",
        ]

        if analysis.suggested_engines:
            lines.append(f"Engines: {', '.join(analysis.suggested_engines[:3])}")

        missing = [q for q, checked in analysis.quadrant_check.items() if not checked]
        if missing and analysis.risk_level != "low":
            lines.append(f"Note: Missing quadrants - {', '.join(missing)}")

        return " | ".join(lines)


# Global singleton
_router: Optional[CognitiveRouter] = None


def get_router() -> CognitiveRouter:
    """Get or create global cognitive router."""
    global _router
    if _router is None:
        _router = CognitiveRouter()
    return _router


def analyze_task(task: str) -> Dict[str, Any]:
    """Convenience function to analyze a task."""
    router = get_router()
    analysis = router.analyze(task)
    return {
        "domain": analysis.primary_domain,
        "risk": analysis.risk_level,
        "engines": analysis.suggested_engines,
        "quadrants": analysis.quadrant_check,
        "violations": analysis.law_violations,
    }


def build_enhanced_prompt(task: str) -> str:
    """Build system prompt with cognitive routing for a task."""
    router = get_router()
    return router.build_cognitive_prompt(task)


if __name__ == "__main__":
    # Test the router
    test_tasks = [
        "Write a Python function to calculate fibonacci",
        "Design the architecture for a microservices system",
        "Analyze the biological impact of this algorithm",
        "Review my code for security vulnerabilities",
    ]

    router = get_router()
    for task in test_tasks:
        print(f"\n{'=' * 60}")
        print(f"Task: {task}")
        print(f"{'=' * 60}")
        print(router.build_cognitive_prompt(task))
        print(router.explain_routing(task))
