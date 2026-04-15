#!/usr/bin/env python3
"""Analyze repository architecture using AMOS Brain."""

import sys
from pathlib import Path

# Add repo_doctor to path
sys.path.insert(0, str(Path(__file__).parent))

from amos_brain.facade import BrainClient
from repo_doctor.arch_invariants import ArchitectureInvariantEngine
from repo_doctor.arch_pathologies import (
    ArchitecturalPathologyEngine,
    get_pathology_engine,
)


def analyze_repository_architecture(repo_path: str = ".") -> dict:
    """Use AMOS brain to analyze repository architecture."""
    print("🧠 Initializing AMOS Brain...")
    client = BrainClient(repo_path=repo_path)
    
    print("🔍 Running architectural invariant checks...")
    engine = ArchitectureInvariantEngine(repo_path)
    invariant_results = engine.run_all()
    
    print("🦠 Detecting architectural pathologies...")
    pathology_engine = get_pathology_engine(repo_path)
    pathologies = pathology_engine.detect_all()
    
    # Use brain to think about architecture
    print("🤔 Brain analyzing architecture...")
    analysis_prompt = f"""
    Analyze this repository architecture:
    - Invariant checks: {len([r for r in invariant_results if not r.passed])} failures
    - Pathologies detected: {len(pathologies)}
    
    Think about:
    1. What are the critical architectural issues?
    2. What fixes should be prioritized?
    3. What is the structural integrity score?
    """
    
    response = client.think(analysis_prompt)
    
    return {
        "invariants": invariant_results,
        "pathologies": pathologies,
        "brain_analysis": response,
        "facade": client,
    }


def suggest_architecture_fixes(analysis: dict) -> list[str]:
    """Generate architecture fix suggestions."""
    client = analysis["facade"]
    
    # Ask brain for fixes
    fix_prompt = """
    Based on the architecture analysis, suggest specific fixes:
    1. File reorganization needed
    2. Import cycle resolution
    3. Boundary integrity improvements
    4. Missing architectural components
    
    Provide actionable fix commands.
    """
    
    decision = client.decide(fix_prompt, options=["reorganize", "fix_imports", "add_boundaries", "document"])
    
    fixes = []
    if decision.approved:
        fixes.append(f"Decision: {decision.reasoning}")
    
    # Check for specific issues
    for inv in analysis["invariants"]:
        if not inv.passed:
            fixes.append(f"FIX: {inv.invariant_name} - {inv.message}")
    
    for path in analysis["pathologies"]:
        if isinstance(path, str):
            fixes.append(f"PATHOLOGY: {path}")
        else:
            fixes.append(f"PATHOLOGY: {getattr(path, 'name', path)} in {getattr(path, 'location', 'unknown')}")
    
    return fixes


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS Brain Architecture Analysis")
    print("=" * 60)
    
    try:
        analysis = analyze_repository_architecture()
        
        print("\n" + "=" * 60)
        print("BRAIN ANALYSIS OUTPUT")
        print("=" * 60)
        print(analysis["brain_analysis"].content)
        
        print("\n" + "=" * 60)
        print("SUGGESTED FIXES")
        print("=" * 60)
        fixes = suggest_architecture_fixes(analysis)
        for fix in fixes[:20]:  # Limit output
            print(f"  • {fix}")
        
        if len(fixes) > 20:
            print(f"  ... and {len(fixes) - 20} more fixes")
        
        print("\n" + "=" * 60)
        print(f"Summary: {len(analysis['invariants'])} invariants, {len(analysis['pathologies'])} pathologies")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
