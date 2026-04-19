# Quick Start Guide

Get your first AMOS agent running in under 5 minutes!

## Step 1: Start AMOS

=== "Python API"

    ```python
    from amos_unified_system import AMOSUnifiedSystem

    # Initialize AMOS
    amos = AMOSUnifiedSystem()
    amos.initialize()
    ```

=== "Command Line"

    ```bash
    python amos_unified_system.py
    ```

=== "Docker"

    ```bash
    docker-compose -f docker-compose.amos.yml up -d
    ```

## Step 2: Spawn Your First Agent

```python
# Spawn a hybrid architect agent
agent = amos.spawn_agent(
    role="architect",
    paradigm="HYBRID"
)

print(f"Created agent: {agent.name}")
print(f"Role: {agent.role}")
print(f"Paradigm: {agent.paradigm}")
```

## Step 3: Execute a Task

```python
# Execute a multi-agent task
result = amos.execute(
    task="Design a REST API for a todo application",
    agents=["architect"],
    require_consensus=True
)

# View the decision
print(result["final_decision"])
```

## Step 4: Check Law Compliance

```python
# Validate an action against Global Laws
validation = amos.validate_action(
    "Delete all files in the system"
)

print(f"Compliant: {validation['compliant']}")
if not validation['compliant']:
    print(f"Violations: {validation['violations']}")
```

## Step 5: Access Memory

```python
# Record an episode to memory
amos.memory.record_episode(
    task="Design REST API",
    outcome="Created 5 endpoints",
    agents_used=["architect"],
    law_compliance=True,
    lessons_learned=["Use consistent naming"]
)

# Query memory
memories = amos.memory.search("REST API design patterns")
```

## Full Example

```python title="first_agent.py"
#!/usr/bin/env python3
"""Your first AMOS agent."""

from amos_unified_system import AMOSUnifiedSystem

def main():
    # Initialize AMOS
    amos = AMOSUnifiedSystem()
    status = amos.initialize()
    
    if not status.core_ready:
        print("❌ AMOS initialization failed")
        return
    
    print("✅ AMOS initialized")
    
    # Spawn agents
    architect = amos.spawn_agent(role="architect")
    reviewer = amos.spawn_agent(role="reviewer")
    
    print(f"✅ Spawned {architect.name} and {reviewer.name}")
    
    # Execute task
    result = amos.execute(
        task="Design a simple task management API",
        agents=["architect", "reviewer"],
        require_consensus=True
    )
    
    print("\n📝 Final Decision:")
    print(result["final_decision"])
    
    print("\n🔍 Agent Reasoning:")
    for agent_id, reasoning in result["agent_reasoning"].items():
        print(f"  {agent_id}: {reasoning[:100]}...")

if __name__ == "__main__":
    main()
```

Run it:

```bash
python first_agent.py
```

## Next Steps

- Learn about [different agent roles](../user-guide/agents.md)
- Explore [multi-agent orchestration](../user-guide/orchestration.md)
- Understand [Global Laws](../user-guide/laws.md)
- Read the [full User Guide](../user-guide/index.md)

---

!!! success "You're Ready!"
    You now have a working AMOS installation. Explore the documentation to learn more about what AMOS can do!
