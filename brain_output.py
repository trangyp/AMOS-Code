#!/usr/bin/env python3
"""Brain output to file."""
import sys
sys.path.insert(0, '.')

# Write output to file
with open('/tmp/brain_test.txt', 'w') as f:
    f.write("Starting brain test\n")
    
    try:
        from amos_brain import get_super_brain
        f.write("Imported get_super_brain\n")
        
        brain = get_super_brain()
        f.write(f"Got brain: {brain.brain_id}\n")
        f.write(f"Status: {brain.status}\n")
        
        # Don't initialize - it hangs
        f.write("Skipping initialize (hangs)\n")
        
        f.write("Brain import successful\n")
    except Exception as e:
        f.write(f"Error: {e}\n")
        import traceback
        traceback.print_exc(file=f)

print("Output written to /tmp/brain_test.txt")
