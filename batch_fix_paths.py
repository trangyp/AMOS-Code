#!/usr/bin/env python3
"""Batch fix sys.path hacks in root-level files."""

import re
from pathlib import Path

files_to_fix = [
    "amos_brain_enhanced.py",
    "amos_knowledge_activation.py",
    "amos_knowledge_agent.py",
    "amos_knowledge_persistence.py",
    "amos_knowledge_synthesis.py",
    "amos_master_activation.py",
    "amos_observer.py",
    "amos_organism_cycle.py",
    "amos_organism_health.py",
    "amos_project_generator.py",
    "amos_reasoning_with_knowledge.py",
    "amos_self_decide.py",
    "amos_training_academy.py",
    "amos_unified_api.py",
    "amos_unified_cli.py",
    "amos_unified_orchestrator.py",
    "amos_workflow_example.py",
]

for fname in files_to_fix:
    fpath = Path(fname)
    if not fpath.exists():
        print(f"Skip: {fname} (not found)")
        continue

    content = fpath.read_text()
    original = content

    # Remove sys.path.insert and sys.path.append lines
    content = re.sub(
        r"^\s*sys\.path\.(?:insert|append)\([^)]+\)\s*$\n?", "", content, flags=re.MULTILINE
    )

    if content != original:
        fpath.write_text(content)
        print(f"Fixed: {fname}")
    else:
        print(f"No changes: {fname}")

print("\nDone!")
