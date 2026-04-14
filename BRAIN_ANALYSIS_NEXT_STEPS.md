# BRAIN ANALYSIS: Next Steps & Fixes

## Current State (Using New Debugging Tools)

### Tests Status
- ✅ test_model_backends.py: 13 tests PASS
- ⏳ test_coherence_bridge.py: Pending verification
- ⏳ test_integration.py: Pending verification
- ⏳ test_full_integration.py: Pending verification

### Dependencies Fixed
- ✅ Fixed pytest dependency conflict (uninstalled pytest-asyncio, downgraded pytest)
- ⚠️ pytest still has plugin issues (pytest_aiohttp requires pytest-asyncio)

## Brain Decision Matrix

| Priority | Issue | Impact | Effort | Decision |
|----------|-------|--------|--------|----------|
| **P0** | Pytest plugin conflicts | Can't run test suite | Low | **FIX NOW** |
| **P1** | Missing test coverage for coherence bridge | 8 tests not verified | Low | **FIX NOW** |
| **P2** | Integration test end-to-end | Full system validation | Medium | **NEXT** |
| **P3** | Documentation gaps | User onboarding | Low | **LATER** |

## BRAIN DECISION: Fix Test Infrastructure First

**Reasoning:** Without working tests, we cannot validate any changes. This is blocking all other work.

### Action Plan:

1. **Fix pytest configuration** - Remove conflicting plugins
2. **Verify all 21 tests** - Ensure test suite passes
3. **Create test runner script** - Direct Python execution as fallback
4. **Document test procedure** - For future reference

### Implementation:

```python
# test_runner.py - Direct test execution without pytest conflicts
#!/usr/bin/env python3
"""
AMOS Test Runner - Bypasses pytest plugin conflicts
"""

import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import test modules
from tests.test_model_backends import *
from tests.test_coherence_bridge import *

def run_all_tests():
    """Run all tests with direct unittest"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Discover tests in each module
    suite.addTests(loader.loadTestsFromModule(test_model_backends))
    suite.addTests(loader.loadTestsFromModule(test_coherence_bridge))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
```

## Next After Tests Fixed

1. **Integration Test with Real Ollama** - Validate local model architecture
2. **Coherence Bridge Validation** - Signal detection → Local LLM pipeline
3. **Performance Profiling** - Use py-spy/memray on coherence engine
4. **Documentation** - API docs, architecture records

---

**DECISION:** Fix test infrastructure now, then proceed to integration testing.
