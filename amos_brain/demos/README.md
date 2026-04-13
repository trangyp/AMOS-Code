# AMOS Brain Demos & Examples (Layer 13)

Comprehensive usage examples and demonstrations for the AMOS Brain Cognitive OS.

## Quick Start

```bash
# Basic thinking demo
python basic_thinking.py

# Architecture decision workflow
python architecture_decision.py

# Comprehensive system test
python comprehensive_test.py
```

## Demo Files

### 1. `basic_thinking.py`
Simplest introduction to AMOS Brain.

Shows:
- `think()` - One-line cognitive processing
- `decide()` - Decision with reasoning
- `validate()` - Quick action validation
- `BrainClient` - Full SDK capabilities

### 2. `architecture_decision.py`
Architecture Decision Records (ADR) workflow.

Shows:
- Technology selection
- Migration decisions
- API design choices
- Context-aware analysis

### 3. `code_review_example.py`
Automated code review with law compliance.

Shows:
- Code analysis
- Security vulnerability detection
- Best practice validation
- Law compliance checking

### 4. `comprehensive_test.py`
Validates all 12 layers of the cognitive OS.

Tests:
- Layer 1: Brain Loader
- Layer 4: Task Processor
- Layer 5: Global Laws
- Layer 6: Agent Bridge
- Layer 7: State Manager
- Layer 8: Meta-Cognitive Controller
- Layer 9: Cognitive Monitor
- Layer 10: Cognitive Facade
- Layer 11: Cognitive Config
- Layer 12: Cognitive Cookbook

## Usage Examples

### Simple Thinking

```python
from amos_brain import think

response = think("How to design a secure API?")
print(response.content)
print(f"Confidence: {response.confidence}")
```

### Architecture Decision

```python
from amos_brain import ArchitectureDecision

result = ArchitectureDecision.analyze(
    "Should we use microservices?",
    context={"team_size": 10}
)
print(result.recommendations)
```

### Code Review

```python
from amos_brain import CodeReview

result = CodeReview.analyze(code="def transfer(...): ...")
print(f"Issues found: {len(result.recommendations)}")
```

### Full Client

```python
from amos_brain import BrainClient

client = BrainClient()
status = client.get_status()
plan = client.orchestrate("Build notification system")
```

## API Integration Example

```python
from fastapi import FastAPI
from amos_brain import think, ArchitectureDecision

app = FastAPI()

@app.post("/think")
def cognitive_think(query: str):
    response = think(query)
    return {
        "analysis": response.content,
        "confidence": response.confidence,
        "compliant": response.law_compliant
    }
```

## Next Steps

- Read the main [AMOS Brain documentation](../docs/)
- Explore the [cookbook recipes](../cookbook.py)
- Try the [CLI tool](../../amos_brain_cli.py)
- Build your own integrations

---

**AMOS Brain Cognitive OS vInfinity**
- 12 Layers
- 26 Engines
- 6 Global Laws
- Production Ready
