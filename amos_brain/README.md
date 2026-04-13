# AMOS Brain Integration Layer

Connects the AMOS cognitive architecture to the ClawSpring agent runtime.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AMOS Brain Layer                         │
├─────────────────────────────────────────────────────────────┤
│  loader.py      →  Load brain JSON specs                  │
│  laws.py          →  Global Laws L1-L6, UBI alignment      │
│  reasoning.py    →  Rule of 2, Rule of 4 engines            │
│  cognitive_stack.py → Domain engine routing                 │
│  integration.py  →  Main brain integration                  │
│  clawspring_bridge.py → Agent runtime bridge                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  ClawSpring Agent Runtime                   │
│              (agent loop, tools, memory)                    │
└─────────────────────────────────────────────────────────────┘
```

## Global Laws (L1-L6)

- **L1 - Law of Law**: Obey highest applicable constraints
- **L2 - Rule of 2**: Dual perspective check required
- **L3 - Rule of 4**: Four quadrant analysis required
- **L4 - Absolute Structural Integrity**: Logical consistency required
- **L5 - Post-Theory Communication**: Clear, grounded language
- **L6 - UBI Alignment**: Protect biological integrity

## Usage

### Basic Usage

```python
from amos_brain import get_amos_integration

# Initialize brain
amos = get_amos_integration()
status = amos.get_status()

# Pre-process user input
result = amos.pre_process("Design a sustainable system")
if result.get('blocked'):
    print(f"Blocked: {result['reason']}")

# Enhance system prompt
enhanced = amos.enhance_system_prompt(base_prompt)

# Analyze with Rule of 2 and Rule of 4
analysis = amos.analyze_with_rules("Should we adopt cloud infrastructure?")
```

### Run Brain-Enhanced Agent

```bash
# Standard ClawSpring with AMOS brain
python amos_clawspring.py

# With specific options
python amos_clawspring.py --model claude-3-5-sonnet
```

## Files

| File | Purpose |
|------|---------|
| `loader.py` | Load brain JSON specifications |
| `laws.py` | Global laws L1-L6, UBI alignment |
| `reasoning.py` | Rule of 2, Rule of 4 engines |
| `cognitive_stack.py` | 12 domain engine management |
| `integration.py` | Main integration class |
| `tools.py` | ClawSpring tools (amos_decide, amos_status, etc.) |
| `skill.py` | ClawSpring skills (/decide, /analyze) |
| `clawspring_bridge.py` | Agent runtime bridge |
| `clawspring_plugin.py` | Auto-registration plugin |
| `memory.py` | Reasoning persistence to clawspring memory |
| `demo_amos_brain.py` | Demo script |
| `amos_brain_cli.py` | Interactive brain CLI |

## CLI Commands

```bash
# Interactive brain CLI
python amos_brain_cli.py

# Commands:
#   /decide <problem>    - Analyze with Rule of 2 + Rule of 4
#   /analyze <topic>     - Deep systems analysis
#   /status              - Show brain status
#   /laws                - Show global laws
#   /history             - Show reasoning history
#   /recall <problem>    - Find similar past reasoning
#   /audit               - Show compliance audit
```

## Tools Available

When registered with ClawSpring:

- `amos_decide(problem)` - Analyze decision using Rule of 2 and Rule of 4
- `amos_status()` - Get brain status
- `amos_route(query)` - Route query to cognitive engines
- `amos_laws_check(text)` - Check text compliance with L4/L5

## Skills Available

- `/decide <decision>` - Structured decision analysis
- `/analyze <topic>` - Deep systems analysis

## Domains Covered

1. meta_logic
2. math_compute
3. physics_cosmos
4. bio_neuro
5. mind_behavior
6. society_culture
7. econ_finance
8. strategy_game
9. org_law_policy
10. tech_engineering
11. design_language
12. earth_ecology

## 7 Intelligences

1. AMOS_Biology_And_Cognition_Engine
2. AMOS_Design_Language_Engine
3. AMOS_Deterministic_Logic_And_Law_Engine
4. AMOS_Econ_Finance_Engine
5. AMOS_Electrical_Power_Engine
6. AMOS_Engineering_And_Mathematics_Engine
7. AMOS_Mechanical_Structural_Engine
8. AMOS_Numerical_Methods_Engine
9. AMOS_Physics_Cosmos_Engine
10. AMOS_Signal_Processing_Engine
11. AMOS_Society_Culture_Engine
12. AMOS_Strategy_Game_Engine
