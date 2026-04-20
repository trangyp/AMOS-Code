# AMOS Compiler Specification

## Overview

The AMOS Compiler is a **natural-language-to-code compiler** that transforms human instructions into repo-grounded code transformations through a deterministic, verifiable pipeline.

This implements the AMOS architecture principle:
```
Intent -> Meaning -> Lawful Transformation -> Verified Execution -> Audited Outcome
```

## Architecture

### Core Pipeline

```
Human Instruction
    ↓
[Intent Parser] → IntentIR
    ↓
[Repo Scanner] → RepoGraph
    ↓
[Grounding Engine] → GroundedIntent
    ↓
[Planner] → TransformationPlan
    ↓
[Gamma Gate] → Verified Changes
    ↓
[Apply] → Committed Result
```

### Components

#### 1. Intent IR (`intent_ir.py`)

Intermediate representation of human intent:

```python
@dataclass
class IntentIR:
    raw_instruction: str
    action: ActionType  # MODIFY, FIX, REFACTOR, RENAME, etc.
    edit_level: EditLevel  # TEXT, AST, SYMBOL, SEMANTIC
    target_domain: TargetDomain
    constraints: list[Constraint]
    required_checks: list[CheckRequirement]
    risk_level: RiskLevel
    ambiguities: list[str]
```

#### 2. Repo Graph (`repo_graph.py`)

Complete codebase representation:

```python
@dataclass
class RepoGraph:
    modules: dict[str, Module]  # Files with symbols
    symbols: dict[str, Symbol]  # All code symbols
    entrypoints: list[Entrypoint]
    import_graph: list[ImportEdge]
    call_graph: list[CallEdge]
    glossary_terms: dict[str, list[str]]
```

#### 3. Grounding Engine (`grounding.py`)

Maps human terms to code symbols:

```python
@dataclass
class GroundedIntent:
    original: IntentIR
    grounded_concepts: list[GroundedConcept]
    edit_scope: EditScope  # Files, symbols, tests
    confidence: float
```

### The .amos/ Control Directory

Each repo must have:

```
.amos/
├── repo.yaml           # Repo metadata and commands
├── glossary.yaml       # Human-to-code term mappings
├── policies.yaml       # Safety policies and invariants
└── architecture.yaml   # Layer boundaries and SSOT
```

#### repo.yaml

```yaml
repo:
  name: AMOS-Code
  languages:
    primary: python
  entrypoints:
    cli: [amos_cli.py]
    api: [backend/main:app]
  commands:
    test: "python -m pytest tests/"
    typecheck: "python -m mypy ."
    lint: "python -m ruff check ."
```

#### glossary.yaml

```yaml
terms:
  brain:
    maps_to: [AMOSBrain, amos_brain/, brain_os.py]
    description: "Core cognitive runtime"
  customer:
    maps_to: [Customer, User, CustomerService]
    description: "End user in the system"
  self_hosted:
    maps_to: [self_hosted_provider, ollama, lmstudio]
    description: "Locally-hosted AI providers"
```

#### policies.yaml

```yaml
policies:
  auto_apply:
    low_risk:
      - pattern: "docs/*.md"
        action: ["text_edit"]
  requires_approval:
    medium_risk:
      - pattern: "amos_brain/*.py"
        reason: "Core brain modifications affect stability"
  protected:
    high_risk:
      - pattern: "amos_kernel/L0_*.py"
        reason: "Universal laws are immutable"
  invariants:
    structural:
      - "no_bare_except_clauses"
      - "imports_must_resolve"
    behavioral:
      - "tests_must_pass"
      - "typecheck_must_pass"
```

## CLI Usage

### Universal Entrypoint

```bash
amos "<human instruction>"
```

### Modes

```bash
# Explain what would happen (default)
amos "make localhost API key optional"

# Show detailed plan
amos "rename customer to account holder" --plan

# Apply changes after verification
amos "add email validation" --apply

# Extra safe mode - refuse uncertain operations
amos "fix the auth bug" --safe

# Limit scope
amos "update README" --scope docs/

# JSON output for automation
amos "explain the kernel" --json
```

## Verification (Gamma Gate)

The Gamma gate checks invariants before applying changes:

### Structural
- Syntax valid
- Imports resolve
- No forbidden layer violations

### Semantic
- Change matches intent
- Scope is correct
- No unrelated changes

### Behavioral
- Tests pass
- Typecheck passes
- Critical contracts preserved

### Policy
- Protected files not touched
- High-risk changes flagged
- SSOT owners respected

## Output Format

### Human-Readable

```
============================================================
GROUNDED INTERPRETATION
============================================================

You asked to: make localhost API key optional for self-hosted providers

I mapped that to:
  - Action: MODIFY
  - Edit Level: SEMANTIC
  - Concepts:
    • 'localhost' → ['localhost', '127.0.0.1', 'local_provider']
      Found 5 matching symbols
    • 'api key' → ['APIKey', 'api_key', 'auth']
      Found 8 matching symbols

  - Edit Scope:
    Files: 4 files
      • backend/api/auth.py
      • amos_auth_manager.py
      • tests/test_auth.py
      • docs/auth.md
    Symbols: 12 symbols
    Tests: 3 related test files

  - Risk: medium
    Reason: auth behavior change

  Confidence: 85%
============================================================
```

### JSON

```json
{
  "instruction": "make localhost API key optional",
  "intent_ir": {
    "action": "MODIFY",
    "edit_level": 4,
    "risk_level": "medium",
    "constraints": [
      {"type": "local_only", "description": "localhost only"}
    ]
  },
  "grounded_intent": {
    "grounded_concepts": [
      {
        "human_term": "localhost",
        "repo_concepts": ["local_provider", "127.0.0.1"],
        "symbol_count": 5,
        "confidence": 0.9
      }
    ],
    "edit_scope": {
      "files": ["backend/api/auth.py", "amos_auth_manager.py"],
      "symbols": ["APIKey.validate", "AuthManager.authenticate"],
      "tests": ["tests/test_auth.py"]
    },
    "confidence": 0.85
  }
}
```

## Implementation

### File Structure

```
amos_compiler/
├── __init__.py       # Package exports
├── intent_ir.py      # Intent IR and parser
├── repo_graph.py     # Repo scanner and graph
├── grounding.py      # Grounding engine
├── cli.py            # Command-line interface
└── README.md         # This spec
```

### Usage as Library

```python
from amos_compiler import compile_instruction

result = compile_instruction(
    "make localhost API key optional",
    repo_root=".",
    dry_run=True
)

print(result["grounded_intent"]["edit_scope"]["files"])
# ['backend/api/auth.py', 'amos_auth_manager.py', ...]
```

## Roadmap

### Phase 1: Core (Complete)
- [x] Intent IR schema
- [x] Repo Graph schema
- [x] Grounding engine
- [x] CLI interface
- [x] .amos/ control directory

### Phase 2: Enhanced Grounding
- [ ] LLM-based intent parser
- [ ] Semantic code search
- [ ] Call graph analysis
- [ ] Test impact analysis

### Phase 3: Patch Generation
- [ ] AST-aware patch generation
- [ ] Symbol-level refactoring
- [ ] Multi-file coordinated edits
- [ ] Automatic test generation

### Phase 4: Verification
- [ ] Architecture boundary enforcement
- [ ] Formal invariant checking
- [ ] Differential testing
- [ ] Rollback capability

## The AMOS Principle

This compiler embodies the AMOS architectural principle:

> **Natural language is not just text to be matched—it is intent to be compiled.**

The compiler does not:
- Do regex replacements
- Generate code blindly
- Treat the repo as a text file

The compiler does:
- Parse intent into structured IR
- Build semantic understanding of the repo
- Ground human terms to code symbols
- Plan transformations at the right abstraction level
- Verify through invariant gates
- Only commit lawful changes

## License

MIT - AMOS Project
