#!/usr/bin/env python3
"""Quick AMOS System Validator."""

import sys

sys.path.insert(0, "clawspring/amos_brain")
sys.path.insert(0, "clawspring")

from system_validator import SystemValidator

validator = SystemValidator()
results = validator.validate_all()

passed = sum(1 for r in results if r.status == "PASS")
failed = sum(1 for r in results if r.status == "FAIL")

print(f"Validation: {passed} passed, {failed} failed")
print(f"Health: {validator.get_health_score():.0f}%")

if failed == 0:
    print(" AMOS is ready for use!")
else:
    print(" Some components need attention")
    sys.exit(1)
