"""AMOS Brain built-in skill for cognitive analysis."""

from .loader import SkillDef, register_builtin_skill

# ── /amos analyze ──────────────────────────────────────────────────────────

_AMOS_ANALYZE_PROMPT = """\
Analyze the user's problem using AMOS Brain's cognitive architecture.

## AMOS Analysis Protocol

Apply the following structured reasoning:

### 1. Rule of 2 (Dual Perspective)
- Provide at least TWO contrasting viewpoints on the problem
- One internal/micro/short-term perspective
- One external/macro/long-term perspective
- Identify common ground and gaps between perspectives

### 2. Rule of 4 (Four Quadrants)
Consider the problem across all four entangled domains:
- **Biological/Human**: Human factors, cognitive load, wellbeing, biological limits
- **Technical/Infrastructural**: System reliability, scalability, security, technical debt
- **Economic/Organizational**: Cost, ROI, stakeholder alignment, resource constraints
- **Environmental/Planetary**: Sustainability, resource consumption, ecosystem impact

### 3. Global Laws Compliance
Check against AMOS L1-L6:
- L1: Respect highest constraints (physical, biological, legal)
- L2: Dual perspectives confirmed (above)
- L3: All four quadrants considered (above)
- L4: No contradictions in reasoning
- L5: Clear, grounded language (no metaphor, mysticism)
- L6: UBI alignment (protect biological integrity)

### 4. Irreducible Limits Acknowledgment
Explicitly state what the system CANNOT do:
- No physical embodiment or direct sensory input
- No subjective consciousness or qualia
- No autonomous action without human execution
- No access to private data beyond provided context

## Output Format

```
## Dual Perspective Analysis
[Primary viewpoint with evidence and limitations]
[Alternative viewpoint with evidence and limitations]
[Synthesis and confidence score]

## Four-Quadrant Analysis
[Biological factors and risks]
[Technical factors and risks]
[Economic factors and risks]
[Environmental factors and risks]
[Cross-impacts between quadrants]
[Integrated recommendation]

## Compliance Check
- L1-L6: [Pass/Fail for each]
- Uncertainty labels: [Where labeled]
- Assumptions: [Explicit assumptions made]

## Final Recommendation
[Clear, actionable next step with confidence level]
```

User request: $ARGUMENTS
"""

# ── /amos laws ─────────────────────────────────────────────────────────────

_AMOS_LAWS_PROMPT = """\
Display the AMOS Global Laws and explain their application.

List all 6 Global Laws with:
1. Law ID and name
2. Full description
3. Practical application example
4. Violation consequences

Then explain UBI (Unified Biological Intelligence) principles:
1. Protect biological integrity
2. Reduce systemic harm
3. Support sustainable nervous system function
4. Respect organism-environment coupling
5. Maintain organizational coherence
6. Preserve planetary system boundaries

Also display the 4 Irreducible Limits:
- No embodiment
- No consciousness
- No autonomous action
- No private data access

User context: $ARGUMENTS
"""

# ── /amos status ──────────────────────────────────────────────────────────

_AMOS_STATUS_PROMPT = """\
Report the current AMOS Brain operational status.

Check and display:
1. Brain identity (name, version)
2. Available domain engines (count and list)
3. Loaded cognitive specifications
4. Active laws and constraints
5. Gap management rules
6. Any initialization issues

Format as a clean status report.

User request: $ARGUMENTS
"""


def _register_amos_skills() -> None:
    """Register AMOS brain built-in skills."""
    register_builtin_skill(
        SkillDef(
            name="amos-analyze",
            description="Analyze a problem using AMOS Brain's Rule of 2 and Rule of 4 cognitive architecture",
            triggers=["/amos", "/amos-analyze", "/analyze"],
            tools=["Read", "Grep"],
            prompt=_AMOS_ANALYZE_PROMPT,
            file_path="<builtin:amos>",
            when_to_use="When user needs structured cognitive analysis with dual perspectives and four-quadrant evaluation",
            argument_hint="[problem or question to analyze]",
            arguments=[],
            user_invocable=True,
            context="inline",
            source="builtin",
        )
    )

    register_builtin_skill(
        SkillDef(
            name="amos-laws",
            description="Display AMOS Global Laws, UBI principles, and irreducible limits",
            triggers=["/amos-laws", "/laws"],
            tools=[],
            prompt=_AMOS_LAWS_PROMPT,
            file_path="<builtin:amos>",
            when_to_use="When user wants to understand AMOS governance framework",
            argument_hint="[optional context]",
            arguments=[],
            user_invocable=True,
            context="inline",
            source="builtin",
        )
    )

    register_builtin_skill(
        SkillDef(
            name="amos-status",
            description="Report AMOS Brain operational status and loaded engines",
            triggers=["/amos-status", "/brain-status"],
            tools=[],
            prompt=_AMOS_STATUS_PROMPT,
            file_path="<builtin:amos>",
            when_to_use="When user wants to verify brain initialization and available capabilities",
            argument_hint="[optional context]",
            arguments=[],
            user_invocable=True,
            context="inline",
            source="builtin",
        )
    )


_register_amos_skills()
