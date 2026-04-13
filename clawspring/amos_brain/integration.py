"""AMOS Brain Integration - Connects new runtime to ClawSpring agent."""
from __future__ import annotations


class AMOSBrainIntegration:
    """Bridge between AMOS runtime and ClawSpring agent."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton pattern - one integration per process."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        from ..amos_runtime import get_runtime

        self.runtime = get_runtime()
        self._initialized = True

    def enhance_system_prompt(self, base_prompt: str) -> str:
        """Enhance system prompt with AMOS brain context."""
        identity = self.runtime.get_identity()
        laws = self.runtime.get_law_summary()

        amos_section = f"""# AMOS Brain Integration (vInfinity)

System: {identity.get('system_name', 'AMOS')}
Creator: {identity.get('creator', 'Trang Phan')}

## Global Laws (Mandatory)
"""
        for law in laws[:6]:
            amos_section += f"- {law['id']}: {law['name']}\n"

        amos_section += """
## Operational Requirements
- Apply Rule of 2: Check two contrasting perspectives
- Apply Rule of 4: Consider biological, technical, economic, environmental quadrants
- Maintain absolute structural integrity
- Declare uncertainty explicitly
- Gap: No embodiment, consciousness, or autonomous action
"""

        return f"{base_prompt}\n\n{amos_section}"

    def pre_process(self, user_message: str) -> dict:
        """Pre-process user message through AMOS brain."""
        # Execute cognitive task analysis
        result = self.runtime.execute_cognitive_task(user_message)

        # Check for law violations or blocks
        blocked = False
        reason = ""

        # High-risk domain check
        high_risk_terms = ['medical diagnosis', 'legal advice', 'financial investment']
        msg_lower = user_message.lower()
        for term in high_risk_terms:
            if term in msg_lower:
                blocked = False  # Not blocking, but flagging
                reason = f"High-risk domain detected: {term}"

        return {
            "blocked": blocked,
            "reason": reason,
            "analysis": result,
            "perspectives": len(result.get('perspectives', [])),
            "quadrants": len(result.get('quadrant_analysis', {})),
        }

    def get_runtime_status(self) -> dict:
        """Get AMOS runtime status."""
        return {
            "bootstrapped": True,
            "identity": self.runtime.get_identity(),
            "laws_loaded": len(self.runtime.get_law_summary()),
        }


def get_amos_integration() -> AMOSBrainIntegration:
    """Get or create the global AMOS brain integration."""
    return AMOSBrainIntegration()
