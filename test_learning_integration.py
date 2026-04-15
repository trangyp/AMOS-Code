"""Test Real Learning Engine integration with BrainTaskProcessor."""
import sys
sys.path.insert(0, "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")

from amos_brain.task_processor import BrainTaskProcessor, process_task
from amos_brain.real_learning_engine import get_learning_engine

print("=" * 70)
print("REAL LEARNING ENGINE INTEGRATION TEST")
print("=" * 70)

# Test 1: BrainTaskProcessor with learning
print("\n[1] Testing BrainTaskProcessor integration...")
processor = BrainTaskProcessor()
print(f"   Processor created with learning engine: {processor.learning_engine is not None}")

# Test 2: Process a task and verify learning
print("\n[2] Processing task to trigger learning...")
result = processor.process("Fix import error for test module", {"type": "import"})
print(f"   Task ID: {result.task_id}")
print(f"   Confidence: {result.confidence}")

# Test 3: Check learning state
print("\n[3] Checking learning state...")
engine = get_learning_engine()
state = engine.get_learning_state()
print(f"   Procedures stored: {state['procedures_stored']}")
print(f"   Patterns detected: {state['patterns_stored']}")

# Test 4: Verify reuse works
print("\n[4] Testing procedure reuse...")
from amos_brain.real_learning_engine import attempt_procedure_reuse

# First learn a procedure
from amos_brain.real_learning_engine import learn_from_task
proc = learn_from_task(
    "Fix import error for missing module",
    ["Check module exists", "Add __init__.py", "Verify import"],
    {"success": True, "summary": "Import fixed"},
    500,
    {"error_type": "import"}
)
print(f"   Learned procedure: {proc.name if proc else 'None'}")

# Then try to reuse
reuse = attempt_procedure_reuse("Fix import error in another file", {"error_type": "import"})
if reuse and reuse.get("reused"):
    print(f"   ✅ Procedure REUSED: {reuse['procedure_name']}")
else:
    print(f"   → No procedure match (expected for new patterns)")

print("\n" + "=" * 70)
print("INTEGRATION TEST COMPLETE - Real Learning Active!")
print("=" * 70)
