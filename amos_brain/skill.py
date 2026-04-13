"""AMOS Brain Decision Analysis Skill - Built-in skill for structured reasoning."""
from __future__ import annotations

# NOTE: Imports are lazy to avoid circular dependency with clawspring
# This module is imported by amos_brain/__init__.py, so it must not
# eagerly import clawspring modules which would trigger agent/tool imports


def _get_skill_classes():
    """Lazy import skill classes to avoid circular imports."""
    # When called from within clawspring, use relative import
    # When called standalone, add parent to path
    try:
        # Try relative import first (when called from clawspring/skill/__init__.py)
        from skill.loader import SkillDef, register_builtin_skill
    except ImportError:
        # Fall back to absolute import (when clawspring not yet loaded)
        import sys
        import os
        clawspring_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'clawspring'
        )
        if clawspring_path not in sys.path:
            sys.path.insert(0, clawspring_path)
        from skill.loader import SkillDef, register_builtin_skill
    return SkillDef, register_builtin_skill


_DECIDE_PROMPT = """\
Analyze the user's decision or problem using AMOS Brain structured reasoning (Rule of 2 and Rule of 4).

User wants to decide/understand: $ARGUMENTS

## AMOS Brain Analysis Required

Apply the following structured reasoning framework:

### Rule of 2 - Dual Perspective Analysis
Check at least TWO contrasting perspectives:

1. **Primary Perspective** (Internal/Micro/Short-term):
   - What are the immediate, direct factors?
   - What causal relationships are obvious?
   - What are the immediate benefits/risks?

2. **Alternative Perspective** (External/Macro/Long-term):
   - What systemic or environmental factors apply?
   - What long-term trends could affect this?
   - What are the second-order consequences?

Synthesis: What is the balanced view considering both perspectives?

### Rule of 4 - Four Quadrant Analysis
For this decision, analyze across ALL FOUR quadrants:

1. **Biological/Human Quadrant**:
   - Human capacity and limitations
   - Cognitive load and wellbeing impact
   - Health and safety considerations

2. **Technical/Infrastructural Quadrant**:
   - System reliability and feasibility
   - Technical debt or complexity
   - Scalability and security

3. **Economic/Organizational Quadrant**:
   - Cost structure and ROI
   - Resource requirements
   - Organizational capacity and alignment

4. **Environmental/Planetary Quadrant**:
   - Resource consumption
   - Sustainability impact
   - Regulatory and reputational considerations

### Global Laws Check (L1-L6)
- L1: Are we respecting physical/biological/legal constraints?
- L2: Have we considered both supporting and alternative cases?
- L3: Have all four quadrants been addressed?
- L4: Is our reasoning logically consistent and uncertainty labeled?
- L5: Is our language clear, grounded, functionally interpretable?
- L6: Does this align with biological integrity and reduce systemic harm?

### Output Format
```
## Decision Analysis: [Topic]

### Rule of 2 - Dual Perspectives
**Primary View:** [Summary]
- Evidence: [Key points]
- Limitations: [What this view misses]

**Alternative View:** [Summary]
- Evidence: [Key points]
- Limitations: [What this view misses]

**Synthesis:** [Balanced conclusion]

### Rule of 4 - Four Quadrants
| Quadrant | Factors | Risks | Opportunities |
|----------|---------|-------|---------------|
| Biological/Human | ... | ... | ... |
| Technical/Infrastructure | ... | ... | ... |
| Economic/Organizational | ... | ... | ... |
| Environmental/Planetary | ... | ... | ... |

### Global Laws Compliance
- [x] L1 - Constraints respected
- [x] L2 - Dual perspectives checked
- [x] L3 - Four quadrants analyzed
- [x] L4 - Logical consistency maintained
- [x] L5 - Clear communication
- [x] L6 - UBI alignment verified

### Recommendation
**Primary Path:** [Recommended approach]

**Confidence:** [High/Medium/Low] with justification

**Uncertainty Flags:** [What we don't know]

**Next Steps:** [Actionable items]
```

Use tools if needed to gather context about the problem domain.
"""


_ANALYZE_PROMPT = """\
Perform deep systems analysis on the user's topic using AMOS Brain cognitive stack.

Topic: $ARGUMENTS

## Deep Systems Analysis

### 1. Domain Intelligence Routing
Route this query through relevant cognitive engines:
- **Biology/Cognition**: If humans, behavior, or biology involved
- **Engineering/Math**: If technical systems or calculations needed
- **Economics/Finance**: If costs, markets, or resources involved
- **Strategy/Game Theory**: If competitive or strategic dynamics
- **Physics/Cosmos**: If natural laws or large-scale systems
- **Signal Processing**: If patterns, data, or noise involved
- **Logic/Law**: If reasoning, rules, or compliance needed
- **Design/Language**: If UX, communication, or aesthetics
- **Society/Culture**: If social dynamics or culture involved

### 2. Multi-Scale Analysis
Analyze at THREE scales:

**Micro Scale** (Immediate/Local):
- Direct actors and interactions
- Immediate causes and effects
- Local constraints

**Meso Scale** (Organizational/Regional):
- Organizational structures
- Regional patterns
- Industry/sector dynamics

**Macro Scale** (Systemic/Global):
- Long-term trends
- Systemic interconnections
- Global implications

### 3. Temporal Analysis
Consider THREE time horizons:

**Short-term** (Now - 1 year):
- Immediate actions and reactions
- Quick wins and risks

**Medium-term** (1-5 years):
- Implementation timeline
- Adaptation and learning

**Long-term** (5+ years):
- Strategic positioning
- Paradigm shifts

### 4. Causal Loop Mapping
Identify key feedback loops:
- **Reinforcing loops** (virtuous/vicious cycles)
- **Balancing loops** (stabilizing forces)
- **Delays** (time lags in the system)

### Output Format
```
## Deep Systems Analysis: [Topic]

### Domain Engines Activated
[List relevant engines and their contributions]

### Multi-Scale View
**Micro:** [Analysis]
**Meso:** [Analysis]
**Macro:** [Analysis]

### Temporal Dynamics
**Short-term:** [Analysis]
**Medium-term:** [Analysis]
**Long-term:** [Analysis]

### System Structure
**Key Variables:** [List]
**Reinforcing Loops:** [Description]
**Balancing Loops:** [Description]
**Leverage Points:** [Where small changes have big effects]

### Synthesis & Implications
[Integrated insight across all dimensions]

### Strategic Options
1. [Option with pros/cons]
2. [Option with pros/cons]
3. [Option with pros/cons]

### Recommended Approach
[Best path considering all analysis]
```

Use Read/Grep/Web tools as needed for research on the topic.
"""


def register_amos_skills() -> None:
    """Register AMOS brain decision analysis skills."""
    # Lazy import to avoid circular dependency
    SkillDef, register_builtin_skill = _get_skill_classes()

    register_builtin_skill(SkillDef(
        name="decide",
        description="Structured decision analysis using AMOS Brain Rule of 2 and Rule of 4",
        triggers=["/decide", "analyze decision"],
        tools=["Read", "Grep", "search_web"],
        prompt=_DECIDE_PROMPT,
        file_path="<builtin:amos>",
        when_to_use=(
            "Use when the user needs to make a decision or wants structured analysis. "
            "Applies Rule of 2 (dual perspectives) and Rule of 4 (four quadrants). "
            "Triggers: '/decide', 'help me decide', 'should I', 'analyze this decision'."
        ),
        argument_hint="<decision or problem to analyze>",
        arguments=["decision"],
        user_invocable=True,
        context="inline",
        source="builtin",
    ))

    register_builtin_skill(SkillDef(
        name="analyze",
        description="Deep systems analysis using AMOS Brain cognitive stack",
        triggers=["/analyze", "/systems"],
        tools=["Read", "Grep", "search_web", "Browser"],
        prompt=_ANALYZE_PROMPT,
        file_path="<builtin:amos>",
        when_to_use=(
            "Use when the user wants deep systems understanding of a topic. "
            "Applies multi-scale, multi-domain analysis across 12 intelligences. "
            "Triggers: '/analyze', '/systems', 'deep dive', 'system analysis'."
        ),
        argument_hint="<topic or system to analyze>",
        arguments=["topic"],
        user_invocable=True,
        context="inline",
        source="builtin",
    ))


# Auto-register on import (but only if clawspring is available)
# This is wrapped in try/except because amos_brain is imported before
# clawspring is fully initialized during early startup
try:
    register_amos_skills()
except Exception:
    # Skills will be unavailable until clawspring fully loads
    pass
