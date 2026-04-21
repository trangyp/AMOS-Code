#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

with open('/tmp/brain_result.txt', 'w') as f:
    f.write("Starting brain test\n")
    
    try:
        f.write("Importing math engine...\n")
        from clawspring.amos_brain.mathematical_framework_engine import get_framework_engine
        f.write("Got math engine import\n")
        
        f.write("Getting engine instance...\n")
        engine = get_framework_engine()
        f.write(f"Engine: {engine}\n")
        
        f.write("Getting stats...\n")
        stats = engine.get_stats()
        f.write(f"Stats: {stats}\n")
        
        f.write(f"Equations: {stats.get('total_equations', 0)}\n")
        f.write(f"Invariants: {stats.get('total_invariants', 0)}\n")
        f.write("BRAIN WORKING\n")
    except Exception as e:
        f.write(f"ERROR: {e}\n")
        import traceback
        traceback.print_exc(file=f)

print("Done - check /tmp/brain_result.txt")
