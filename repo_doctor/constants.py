"""
Repository analysis constants.

Centralized string constants to eliminate magic strings
and enable safe refactoring across the codebase.
"""

# State dimension names (canonical single source of truth)
DIMENSION_SYNTAX = "syntax"
DIMENSION_IMPORT = "import"
DIMENSION_TYPE = "type"
DIMENSION_API = "api"
DIMENSION_ENTRYPOINT = "entrypoint"
DIMENSION_PACKAGING = "packaging"
DIMENSION_RUNTIME = "runtime"
DIMENSION_PERSISTENCE = "persistence"
DIMENSION_STATUS = "status"
DIMENSION_TEST = "test"
DIMENSION_DOCS = "docs"
DIMENSION_SECURITY = "security"
DIMENSION_HISTORY = "history"
DIMENSION_GENERATED_CODE = "generated_code"
DIMENSION_ENVIRONMENT = "environment"

# File patterns
PYTHON_EXTENSION = ".py"
TOML_EXTENSION = ".toml"
YAML_EXTENSION = ".yaml"
YML_EXTENSION = ".yml"
JSON_EXTENSION = ".json"

# Common directory names
TESTS_DIR = "tests"
TEST_DIR = "test"
SRC_DIR = "src"
DOCS_DIR = "docs"

# Configuration file names
PYPROJECT_TOML = "pyproject.toml"
SETUP_PY = "setup.py"
REQUIREMENTS_TXT = "requirements.txt"
PACKAGE_JSON = "package.json"

# Error severity levels
SEVERITY_CRITICAL = "critical"
SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"
SEVERITY_LOW = "low"
SEVERITY_INFO = "info"

# Invariant result statuses
STATUS_PASSED = "passed"
STATUS_FAILED = "failed"
STATUS_WARNING = "warning"
STATUS_SKIPPED = "skipped"

# Message templates (centralized for consistency)
MSG_ALL_RESOLVED = "All {} resolve"
MSG_NO_VIOLATIONS = "No {} violations"
MSG_ALL_VALID = "All {} valid"
MSG_PARSING_SUCCESS = "All files parse successfully"
MSG_METADATA_CONSISTENT = "{} metadata consistent"
MSG_IMPORTS_RESOLVED = "All imports resolve"
MSG_TYPES_VALID = "All signatures valid"
MSG_NO_SECURITY_VIOLATIONS = "No security violations"
MSG_API_COMMUTES = "Public API commutes with runtime reality"

# Default thresholds
DEFAULT_LINE_THRESHOLD = 500  # Monolith detection
DEFAULT_DUPLICATE_THRESHOLD = 3  # Duplicate detection
DEFAULT_TODO_THRESHOLD = 5  # TODO accumulation warning

# Evolution contract defaults
DEFAULT_MUTATION_BUDGET = 3  # Max files per evolution
DEFAULT_PROOF_BUDGET = "Run existing test suite"
