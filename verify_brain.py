#!/usr/bin/env python3
"""Verify AMOS Brain is fully operational."""
from amos_brain.super_brain import get_super_brain

brain = get_super_brain()
brain.initialize()

subsystems = [
    ('Core Freeze', brain._core_freeze),
    ('Memory Governance', brain._memory_governance),
    ('Tool Registry', brain._tool_registry),
    ('Model Router', brain._model_router),
    ('Action Gate', brain._action_gate),
    ('Kernel Router', brain._kernel_router),
    ('Math Engine', brain._math_engine),
    ('Math Audit Logger', brain._math_audit_logger),
    ('Equation Bridge', brain._equation_bridge),
    ('World Model', brain._world_model),
    ('Constitutional Governance', brain._constitutional_governance),
    ('Workflow Orchestrator', brain._workflow_orchestrator),
    ('A2A Agent', brain._a2a_agent),
    ('Knowledge Bridge', brain._knowledge_bridge),
]

active = sum(1 for _, s in subsystems if s)
print(f'AMOS Brain Status: {active}/14 subsystems active ({active/14*100:.0f}%)')
print()
for name, sys in subsystems:
    status = '✅' if sys else '❌'
    print(f'{status} {name}')
