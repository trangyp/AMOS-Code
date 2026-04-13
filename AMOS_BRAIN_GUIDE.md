# AMOS Brain Complete Usage Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Core Concepts](#core-concepts)
3. [CLI Usage](#cli-usage)
4. [Cookbook Workflows](#cookbook-workflows)
5. [Python API](#python-api)
6. [Integration Patterns](#integration-patterns)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Run the Tutorial (5 minutes)
```bash
python amos_brain_tutorial.py
```
This interactive tutorial teaches Rule of 2, Rule of 4, and all CLI commands.

### 2. Try the CLI
```bash
python amos_brain_cli.py
amos> /decide Should we adopt microservices?
amos> /status
amos> /dashboard
```

### 3. Use Cookbook Workflows
```python
from amos_brain.cookbook import ArchitectureDecision

result = ArchitectureDecision.run(
    "Should we migrate to cloud?",
    context={"current_stack": "on-premise", "team_size": 10}
)
print(result.recommendations)
```

---

## Core Concepts

### Rule of 2 (L2 Compliance)
Every decision analysis checks TWO perspectives:
- **Primary**: Internal/micro view (direct factors)
- **Alternative**: External/macro view (systemic factors)

This prevents confirmation bias and ensures balanced analysis.

### Rule of 4 (L3 Compliance)
Every systems analysis covers FOUR quadrants:
1. **Biological/Human** - Human capacity, wellbeing, safety
2. **Technical/Infrastructural** - Feasibility, reliability
3. **Economic/Organizational** - Cost, ROI, resources
4. **Environmental/Planetary** - Sustainability, impact

### The 12 Cognitive Domains
The brain routes queries through relevant domain engines:
- `meta_logic` - Abstract reasoning
- `math_compute` - Calculations
- `physics_cosmos` - Physical systems
- `bio_neuro` - Biological systems
- `mind_behavior` - Psychology
- `society_culture` - Social dynamics
- `econ_finance` - Economics
- `strategy_game` - Strategic thinking
- `org_law_policy` - Legal/policy
- `tech_engineering` - Engineering
- `design_language` - UX/design
- `earth_ecology` - Environment

---

## CLI Usage

### /decide - Structured Decision Analysis
Use for any significant decision.

```bash
amos> /decide Should we adopt remote work permanently?
```

**Output includes:**
- Rule of 2 dual perspective analysis
- Rule of 4 four quadrant analysis
- Confidence score
- Recommendations
- Auto-saved to memory

### /analyze - Deep Systems Analysis
Use for understanding complex systems or topics.

```bash
amos> /analyze Impact of AI on software development
```

**Output includes:**
- Activated cognitive engines
- Multi-scale analysis (micro/meso/macro)
- Temporal analysis (short/medium/long term)
- Synthesis and recommendations

### /recall - Find Similar Past Reasoning
Before making a decision, check if you've analyzed similar problems.

```bash
amos> /recall Should we allow developers to work remotely?
```

**Output includes:**
- Similar past problems
- Similarity scores
- Past recommendations

### /dashboard - Analytics
Track your reasoning patterns over time.

```bash
amos> /dashboard        # Last 30 days
amos> /dashboard 7      # Last 7 days
```

**Output includes:**
- Total decisions analyzed
- L2/L3 compliance rates
- Confidence trends
- Decision velocity
- Personalized insights

### /audit - Compliance Checking
Check your law compliance statistics.

```bash
amos> /audit
```

**Output includes:**
- Total entries
- Rule of 2 compliance rate
- Rule of 4 compliance rate
- Average confidence

---

## Cookbook Workflows

### ArchitectureDecision
For architectural choices and system design.

```python
from amos_brain.cookbook import ArchitectureDecision

result = ArchitectureDecision.run(
    "Should we migrate from REST to GraphQL?",
    context={
        "current_stack": "REST APIs with 50+ endpoints",
        "constraints": "Mobile app needs efficient data fetching",
        "scale": "1M requests/day"
    }
)

print(f"Confidence: {result.confidence:.0%}")
print("Recommendations:")
for rec in result.recommendations:
    print(f"  • {rec}")
```

### ProjectPlanner
For project scoping and estimation.

```python
from amos_brain.cookbook import ProjectPlanner

result = ProjectPlanner.run(
    "Build real-time notification system",
    timeline="6 weeks",
    team="2 backend, 1 DevOps",
    constraints=["must handle 10k concurrent"]
)
```

### ProblemDiagnosis
For debugging and root cause analysis.

```python
from amos_brain.cookbook import ProblemDiagnosis

result = ProblemDiagnosis.run(
    "Database connection pool exhaustion",
    symptoms=["500 errors after 2 hours", "gradual latency increase"],
    checked=["query performance", "indexes"],
    timeline="Started 3 days ago"
)
```

### TechnologySelection
For choosing between tools/frameworks.

```python
from amos_brain.cookbook import TechnologySelection

result = TechnologySelection.run(
    "Message Queue",
    options=["RabbitMQ", "Apache Kafka", "AWS SQS"],
    criteria=["scalability", "operational-complexity", "cost"],
    must_haves=["persistent messages", "high-throughput"]
)
```

### RiskAssessment
For evaluating risks before major changes.

```python
from amos_brain.cookbook import RiskAssessment

result = RiskAssessment.run(
    "Migrate production database to new cloud provider",
    impacts=["revenue", "customer-trust", "data-integrity"],
    mitigations=["parallel-run", "automated-rollback"],
    severity_threshold="high"
)
```

---

## Python API

### Direct Brain Access

```python
from amos_brain import get_amos_integration

amos = get_amos_integration()

# Check status
status = amos.get_status()
print(f"Engines: {status['engines_count']}")
print(f"Laws: {', '.join(status['laws_active'])}")

# Analyze a problem
analysis = amos.analyze_with_rules("Should we adopt AI coding assistants?")

# Access results
if "rule_of_two" in analysis:
    r2 = analysis["rule_of_two"]
    print(f"Rule of 2 confidence: {r2['confidence']:.0%}")

if "rule_of_four" in analysis:
    r4 = analysis["rule_of_four"]
    print(f"Rule of 4 completeness: {r4['completeness_score']:.0%}")

print("Recommendations:")
for rec in analysis["recommendations"]:
    print(f"  • {rec}")
```

### Memory Management

```python
from amos_brain.memory import get_brain_memory

memory = get_brain_memory()

# Save reasoning manually
entry_id = memory.save_reasoning(
    problem="Should we use Kubernetes?",
    analysis=analysis,
    tags=["infrastructure", "devops"]
)

# Find similar reasoning
similar = memory.find_similar_reasoning(
    "Should we adopt container orchestration?",
    threshold=0.5
)

for item in similar:
    print(f"Similarity: {item['similarity']:.0%}")
    print(f"Past problem: {item['entry']['problem_preview']}")

# Get reasoning history
history = memory.get_reasoning_history(limit=10)
for entry in history:
    print(f"[{entry['timestamp'][:10]}] {entry['problem_preview']}")

# Get audit trail
audit = memory.get_audit_trail()
print(f"Total decisions: {audit['total_entries']}")
print(f"L2 compliance: {audit['law_compliance']['L2_compliance_rate']:.0%}")
```

### Dashboard Analytics

```python
from amos_brain.dashboard import BrainDashboard, print_dashboard

# Print dashboard to console
print_dashboard(days=30)

# Or get report programmatically
dashboard = BrainDashboard()
report = dashboard.generate_report(days=30)

# Access specific metrics
summary = report["summary"]
print(f"Total decisions: {summary['total_decisions']}")
print(f"L2 compliance: {summary['l2_compliance_rate']:.0%}")
print(f"Avg confidence: {summary['average_confidence']:.0%}")

# Get insights
for insight in report["insights"]:
    print(f"💡 {insight}")
```

### Laws Checking

```python
from amos_brain import GlobalLaws

laws = GlobalLaws()

# Check all laws
text = "We should implement this feature immediately without testing."
violations = []

# L4 - Check for contradictions
statements = text.split('.')
consistent, contradictions = laws.check_l4_integrity(statements)
if not consistent:
    violations.extend(contradictions)

# L5 - Check communication style
ok, l5_violations = laws.l5_communication_check(text)
if not ok:
    violations.extend(l5_violations)

print(f"Violations found: {len(violations)}")
for v in violations:
    print(f"  • {v}")
```

---

## Integration Patterns

### Pattern 1: Decision Before Action
Always use brain before significant decisions.

```python
def make_architecture_decision(problem: str, context: dict) -> dict:
    """Standard pattern for architecture decisions."""
    from amos_brain.cookbook import ArchitectureDecision
    from amos_brain.memory import get_brain_memory

    # Step 1: Check for similar past decisions
    memory = get_brain_memory()
    recall = memory.recall_for_problem(problem)

    if recall["has_prior_reasoning"]:
        print("Similar past decisions found:")
        for item in recall["similar_entries"][:3]:
            print(f"  - {item['entry']['problem_preview']}")

    # Step 2: Run analysis
    result = ArchitectureDecision.run(problem, context)

    # Step 3: Check confidence threshold
    if result.confidence < 0.6:
        print(f"⚠️ Low confidence ({result.confidence:.0%}). Consider gathering more data.")

    # Step 4: Return structured result
    return {
        "decision": problem,
        "recommendations": result.recommendations,
        "confidence": result.confidence,
        "memory_id": result.memory_id,
        "should_proceed": result.confidence > 0.6
    }
```

### Pattern 2: Weekly Review
Regular dashboard review for continuous improvement.

```python
def weekly_reasoning_review():
    """Weekly review of reasoning patterns."""
    from amos_brain.dashboard import BrainDashboard

    dashboard = BrainDashboard()
    report = dashboard.generate_report(days=7)

    summary = report["summary"]

    print(f"📊 Weekly Review ({report['period_days']} days)")
    print(f"   Decisions: {summary['total_decisions']}")
    print(f"   L2 Compliance: {summary['l2_compliance_rate']:.0%}")
    print(f"   L3 Compliance: {summary['l3_compliance_rate']:.0%}")
    print(f"   Avg Confidence: {summary['average_confidence']:.0%}")

    # Actionable insights
    for insight in report["insights"]:
        print(f"💡 {insight}")

    # Improvement recommendations
    if summary["l2_compliance_rate"] < 0.8:
        print("📚 Action: Practice using /decide more frequently")

    if summary["average_confidence"] < 0.6:
        print("📚 Action: Gather more data before making decisions")
```

### Pattern 3: Pre-Meeting Analysis
Use brain before important meetings.

```python
def prepare_for_discussion(topic: str, stakeholders: list[str]):
    """Prepare for important discussions."""
    from amos_brain import get_amos_integration
    from amos_brain.cognitive_stack import CognitiveStack

    amos = get_amos_integration()

    # Analyze the topic
    analysis = amos.analyze_with_rules(
        f"Discussion topic: {topic}\n"
        f"Stakeholders: {', '.join(stakeholders)}"
    )

    # Route through relevant engines
    stack = CognitiveStack()
    engines = stack.route_query(topic)

    print(f"📋 Pre-Meeting Analysis: {topic}")
    print(f"   Relevant domains: {', '.join(engines[:3])}")

    # Prepare talking points
    print("\n🎯 Key Perspectives to Cover:")
    if "rule_of_two" in analysis:
        for p in analysis["rule_of_two"].get("perspectives", []):
            viewpoint = p.viewpoint if hasattr(p, 'viewpoint') else str(p)
            print(f"   • {viewpoint[:60]}...")

    # Quadrants to address
    print("\n📊 Quadrants to Consider:")
    if "rule_of_four" in analysis:
        for q in analysis["rule_of_four"].get("quadrants_analyzed", []):
            print(f"   • {q}")

    return analysis
```

---

## Best Practices

### 1. Always Use /decide for Significant Decisions
**Why**: Ensures Rule of 2 and Rule of 4 compliance, saves to memory for recall.

**Thresholds**:
- Decisions affecting >5 people → Use /decide
- Architecture changes → Use ArchitectureDecision workflow
- Technology choices → Use TechnologySelection workflow

### 2. Check /recall Before /decide
**Why**: Avoid re-analyzing similar problems.

```bash
amos> /recall Should we adopt microservices?
amos> /decide Should we use service-oriented architecture?
```

### 3. Tag Your Reasoning
**Why**: Enables filtering and domain analysis.

```python
memory.save_reasoning(
    problem,
    analysis,
    tags=["architecture", "2024-q1", "high-priority"]
)
```

### 4. Weekly /dashboard Review
**Why**: Track compliance trends and identify improvement areas.

```bash
# Add to weekly routine
amos> /dashboard 7
```

### 5. Use Confidence Scores
**Why**: Low confidence indicates need for more data.

- **>80%**: Proceed with confidence
- **60-80%**: Consider gathering more information
- **<60%**: Don't decide yet; do more research

### 6. Build Your Decision History
**Why**: The brain learns from your patterns and provides better recall.

- Use /decide consistently
- Review /history periodically
- Leverage /recall for similar problems

---

## Troubleshooting

### "Brain not initialized" Error
**Cause**: Brain failed to load JSON specs.
**Solution**:
```python
# Check brain path
from amos_brain.loader import BrainLoader
loader = BrainLoader()
print(f"Brain path: {loader.brain_path}")

# Re-initialize
amos = get_amos_integration()
status = amos.initialize()
print(f"Status: {status}")
```

### Slow Response Times
**Cause**: Large brain specs loading synchronously.
**Solution**: Use async loading (already implemented in latest version).

### Memory Not Persisting
**Cause**: clawspring memory not available.
**Solution**: Ensure clawspring is installed, or use local cache only.

```python
from amos_brain.memory import get_brain_memory
memory = get_brain_memory()

# Check if clawspring available
if memory.memory_dir:
    print("Using clawspring memory")
else:
    print("Using local cache only")
```

### Low Confidence Scores
**Cause**: Insufficient information in problem statement.
**Solution**: Provide more context.

```python
# ❌ Vague
result = ArchitectureDecision.run("Should we use microservices?")

# ✅ Context-rich
result = ArchitectureDecision.run(
    "Should we use microservices?",
    context={
        "current_stack": "Django monolith",
        "team_size": 12,
        "scale": "100k users",
        "constraints": "limited DevOps expertise"
    }
)
```

### Similarity Recall Not Finding Matches
**Cause**: Threshold too high or different vocabulary.
**Solution**: Adjust threshold or use broader keywords.

```python
# Try lower threshold
similar = memory.find_similar_reasoning(
    problem,
    threshold=0.4  # Default is 0.6
)
```

---

## Advanced Usage

### Custom Workflows
Create your own workflow by extending the base pattern:

```python
from amos_brain import get_amos_integration
from amos_brain.memory import get_brain_memory
from dataclasses import dataclass

@dataclass
class CustomWorkflowResult:
    workflow_name: str
    analysis: dict
    recommendations: list

class CustomWorkflow:
    WORKFLOW_NAME = "My Custom Workflow"
    TAGS = ["custom", "my-domain"]

    @classmethod
    def run(cls, problem: str, **kwargs) -> CustomWorkflowResult:
        amos = get_amos_integration()
        memory = get_brain_memory()

        # Pre-processing
        enriched = cls._enrich(problem, kwargs)

        # Analysis
        analysis = amos.analyze_with_rules(enriched)

        # Post-processing
        recommendations = cls._post_process(analysis)

        # Save
        memory.save_reasoning(problem, analysis, tags=cls.TAGS)

        return CustomWorkflowResult(
            workflow_name=cls.WORKFLOW_NAME,
            analysis=analysis,
            recommendations=recommendations
        )

    @classmethod
    def _enrich(cls, problem, kwargs):
        # Add domain-specific context
        return problem

    @classmethod
    def _post_process(cls, analysis):
        # Extract domain-specific insights
        return analysis.get("recommendations", [])
```

### Batch Processing
Analyze multiple decisions at once:

```python
def batch_analyze(decisions: list[str]) -> list:
    """Analyze multiple decisions."""
    from amos_brain.cookbook import ArchitectureDecision

    results = []
    for decision in decisions:
        result = ArchitectureDecision.run(decision)
        results.append({
            "decision": decision,
            "confidence": result.confidence,
            "top_recommendation": result.recommendations[0] if result.recommendations else None
        })

    return results

# Usage
decisions = [
    "Should we use GraphQL?",
    "Should we adopt microservices?",
    "Should we migrate to cloud?"
]
results = batch_analyze(decisions)

# Sort by confidence
sorted_results = sorted(results, key=lambda x: x["confidence"], reverse=True)
print("Decisions by confidence:")
for r in sorted_results:
    print(f"  {r['confidence']:.0%}: {r['decision']}")
```

---

## Summary

**Start with**: `python amos_brain_tutorial.py`

**Daily use**: `python amos_brain_cli.py`

**Programmatic**: Import from `amos_brain` and `amos_brain.cookbook`

**Track progress**: Use `/dashboard` weekly

**Remember**: The more you use the brain, the more valuable it becomes through memory and pattern recognition.
