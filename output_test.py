#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

with open('/tmp/output.txt', 'w') as f:
    f.write("Step 1: Starting\n")
    
    try:
        f.write("Step 2: Importing clawspring\n")
        import clawspring
        f.write("Step 3: clawspring imported\n")
        
        f.write("Step 4: Getting runtime\n")
        r = clawspring.get_runtime()
        f.write(f"Step 5: Runtime = {r}\n")
        
        if r:
            f.write(f"Step 6: Loaded = {r._loaded}\n")
        else:
            f.write("Step 6: Runtime is None\n")
            
        f.write("SUCCESS\n")
    except Exception as e:
        f.write(f"ERROR: {e}\n")
        import traceback
        traceback.print_exc(file=f)

print("Output written to /tmp/output.txt")
