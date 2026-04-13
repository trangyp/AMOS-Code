# AMOS Brain Integration Guide

Complete integration of AMOS Brain into ClawSpring agent system.

## Quick Start

```bash
# Enable AMOS mode from CLI
python clawspring/clawspring.py --amos

# Or enable in REPL
/amos on

# Check AMOS status
/amos-status
```

## Features

### 1. Cognitive Architecture
- **Rule of 2**: Dual-perspective analysis (optimistic/pessimistic)
- **Rule of 4**: Four-quadrant analysis (biological, technical, economic, environmental)
- **Global Laws L1-L6**: Safety and governance constraints
- **UBI Alignment**: Unified Biological Intelligence principles

### 2. Skills (7 total)
| Skill | Description |
|-------|-------------|
| `/amos-analyze` | Deep cognitive analysis with Rule of 2/4 |
| `/amos-laws` | Display active global laws |
| `/amos-status` | Show brain status and engines |
| `/decide` | Structured decision analysis |
| `/analyze` | General AMOS analysis |
| `/commit` | Git commit helper |
| `/review` | Code review helper |

### 3. Tools (5 AMOS tools)
- `AMOSReasoning`: Rule of 2/4 analysis
- `AMOSLaws`: Global laws enforcement
- `AMOSEngines`: Cognitive engine registry
- `AMOSStatus`: Brain status check
- `AMOSEnhancePrompt`: System prompt enhancement

### 4. Agent Types
- `amos`: Specialized AMOS-powered sub-agent

## Architecture

```
┌─────────────────────────────────────────┐
│           clawspring CLI               │
│         (python clawspring.py          │
│          --amos)                       │
└──────────────────┬──────────────────────┘
                   │
    ┌──────────────┴──────────────┐
    │                             │
┌───▼────┐                  ┌─────▼─────┐
│ Agent  │                  │  Context  │
│ Loop   │                  │  Builder  │
└───┬────┘                  └─────┬─────┘
    │                             │
    │         ┌───────────────────┘
    │         │
┌───▼─────────▼────────────────┐
│     AMOS Brain Integration   │
│  ┌────────────────────────┐   │
│  │  AMOSBrainIntegration │   │
│  │  - pre_process()      │   │
│  │  - enhance_prompt()   │   │
│  └────────────────────────┘   │
│  ┌────────────────────────┐   │
│  │  CognitiveStack (12)    │   │
│  │  - 7 Intelligences      │   │
│  │  - Domain engines       │   │
│  └────────────────────────┘   │
│  ┌────────────────────────┐   │
│  │  GlobalLaws (L1-L6)     │   │
│  │  - L1: Law of Law       │   │
│  │  - L2: Rule of 2        │   │
│  │  - L3: Rule of 4        │   │
│  │  - L4: Absolute Struct  │   │
│  │  - L5: Post-Theory Com  │   │
│  │  - L6: UBI Alignment    │   │
│  └────────────────────────┘   │
└──────────────────────────────┘
```

## Files Modified/Created

### Core Integration
- `clawspring/agent.py` - AMOS hooks in agent loop
- `clawspring/context.py` - AMOS context injection
- `clawspring/amos_cognitive_router.py` - Task routing
- `clawspring/amos_integration.py` - Bridge class
- `clawspring/amos_tools.py` - Tool registrations

### Skills
- `skill/builtin_amos.py` - `/amos-*` skills
- `amos_brain/skill.py` - AMOS brain skills
- `skill/__init__.py` - Unified registration

### Multi-Agent
- `multi_agent/subagent.py` - AMOS agent type

### CLI
- `clawspring/clawspring.py` - `--amos` flag

### Testing
- `test_amos_integration.py` - Comprehensive test suite

## Usage Examples

### Deep Analysis
```
/amos analyze this microservices architecture
```

### Decision Making
```
/decide Should we migrate from monolith to microservices?
Pros: scalability, team autonomy
Cons: complexity, operational overhead
```

### Laws Check
```
/amos-laws
```

### Sub-agent
```
/agent amos analyze the security implications
```

## Testing

```bash
# Run integration tests
python test_amos_integration.py --verbose

# Expected: 12 tests pass
# - Core Brain
# - Tools (5 AMOS tools)
# - Skills (7 skills)
# - Agent Types
# - Agent Loop
# - Context
# - Cognitive Router
# - CLI Flag
```

## Architecture Decisions

1. **Unified Skill Registry**: Both `skill/` and `amos_brain/skill.py` register to the same registry
2. **Lazy Loading**: AMOS brain components load on first use
3. **Pre-processing Hook**: Laws enforcement runs before agent loop
4. **Prompt Enhancement**: AMOS context added to system prompt
5. **Dual Skill Sources**: AMOS skills from both root and amos_brain packages

## Compliance

All outputs include:
- **Gap Acknowledgment**: System declares its limitations
- **Uncertainty Labeling**: Unknowns are explicitly marked
- **Law References**: L1-L6 constraints applied
- **UBI Alignment**: Biological-system harmony emphasized

---

*Created: 2026-04-13*
*Status: Production Ready*
