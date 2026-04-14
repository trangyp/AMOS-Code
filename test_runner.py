#!/usr/bin/env python3
"""
AMOS Test Runner - Bypasses pytest plugin conflicts
Uses direct unittest execution for reliable testing.

Usage:
    python test_runner.py              # Run all tests
    python test_runner.py --verbose      # Run with detailed output
    python test_runner.py --list         # List available tests
"""

import unittest
import sys
import argparse
import importlib.util
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_test_module(module_name: str, module_path: str) -> unittest.TestSuite:
    """Load tests from a module file"""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        return unittest.TestSuite()
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    # Load tests from module
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Find TestCase classes
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, type) and issubclass(obj, unittest.TestCase) and obj != unittest.TestCase:
            suite.addTests(loader.loadTestsFromTestCase(obj))
    
    return suite


def get_test_modules() -> list:
    """Discover all test modules in tests/ directory"""
    tests_dir = PROJECT_ROOT / "tests"
    if not tests_dir.exists():
        return []
    
    test_files = sorted(tests_dir.glob("test_*.py"))
    return [(f.stem, str(f)) for f in test_files]


def run_tests(verbose: bool = False, list_only: bool = False) -> bool:
    """Run all discovered tests"""
    test_modules = get_test_modules()
    
    if list_only:
        print("\n📋 Available Test Modules:")
        print("=" * 50)
        for name, path in test_modules:
            print(f"  • {name}")
        print(f"\nTotal: {len(test_modules)} test modules\n")
        return True
    
    print("\n🧪 AMOS Test Suite")
    print("=" * 50)
    
    all_tests = unittest.TestSuite()
    loaded_modules = []
    
    for module_name, module_path in test_modules:
        try:
            suite = load_test_module(module_name, module_path)
            if suite.countTestCases() > 0:
                all_tests.addTests(suite)
                loaded_modules.append((module_name, suite.countTestCases()))
                print(f"✓ {module_name}: {suite.countTestCases()} tests")
            else:
                print(f"⚠ {module_name}: No tests found")
        except Exception as e:
            print(f"✗ {module_name}: ERROR - {e}")
    
    print(f"\n📊 Total Tests: {all_tests.countTestCases()}")
    print("=" * 50)
    
    if all_tests.countTestCases() == 0:
        print("❌ No tests to run!")
        return False
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(all_tests)
    
    # Summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED")
    else:
        print(f"❌ FAILURES: {len(result.failures)}")
        print(f"❌ ERRORS: {len(result.errors)}")
    print("=" * 50 + "\n")
    
    return result.wasSuccessful()


def main():
    parser = argparse.ArgumentParser(description="AMOS Test Runner")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--list", "-l", action="store_true", help="List available tests")
    
    args = parser.parse_args()
    
    success = run_tests(verbose=args.verbose, list_only=args.list)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
