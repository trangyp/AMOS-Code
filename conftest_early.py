# Early conftest - runs before pytest imports any plugins
import sys
from unittest.mock import MagicMock

# Create complete trio mock structure before any imports can happen
trio_mock = MagicMock()
trio_core = MagicMock()
trio_core_run = MagicMock()

trio_mock._core = trio_core
trio_mock._core._run = trio_core_run
trio_mock._core.TASK_STATUS_IGNORED = None
trio_mock._core.RunVar = MagicMock
trio_mock._core.RunVarToken = MagicMock

sys.modules["trio"] = trio_mock
sys.modules["trio._core"] = trio_core
sys.modules["trio._core._run"] = trio_core_run
sys.modules["httpcore._backends.trio"] = MagicMock()

# Add this to PYTHONPATH to make it load first
print("Early trio mock installed")
