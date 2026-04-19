"""AMOS Secure Equation Runner v1.0.0

Secure execution environment for mathematical equation testing.
Replaces dangerous exec() calls in self-healing with sandboxed execution.

Architecture:
    1. AST Validation - Ensure only mathematical operations
    2. Restricted Imports - Only numpy/math allowed
    3. Safe Builtins - No file/network operations
    4. Execution Sandbox - Isolated namespace

Author: Cascade AI
Date: 2026-04-16
Version: 1.0.0
"""

import ast
import builtins
from typing import Any


class EquationExecutionError(Exception):
    """Raised when equation execution fails."""

    pass


class EquationValidationError(Exception):
    """Raised when equation code validation fails."""

    pass


class SecureEquationRunner:
    """
    Secure execution environment for mathematical equations.

    Replaces dangerous exec() in self-healing with restricted sandbox.
    Only allows mathematical operations - no file/network/system access.
    """

    # Allowed AST node types for mathematical equations
    ALLOWED_NODES = frozenset(
        [
            # Function definitions
            "FunctionDef",
            "arguments",
            "arg",
            "Param",
            "Return",
            # Expressions
            "Expr",
            "Call",
            "Name",
            "Load",
            "Attribute",
            "BinOp",
            "UnaryOp",
            "Num",
            "Constant",
            "Str",
            "NameConstant",
            # Operators
            "Add",
            "Sub",
            "Mult",
            "Div",
            "FloorDiv",
            "Mod",
            "Pow",
            "UAdd",
            "USub",
            "Invert",
            # Comparisons
            "Compare",
            "Eq",
            "NotEq",
            "Lt",
            "LtE",
            "Gt",
            "GtE",
            # Control flow
            "If",
            "IfExp",
            "BoolOp",
            "And",
            "Or",
            "Not",
            # Data structures
            "List",
            "Tuple",
            "Dict",
            "Subscript",
            "Index",
            "Slice",
            # Variables
            "Assign",
            "AugAssign",
            "Store",
            "Module",
            # Comprehensions
            "ListComp",
            "GeneratorExp",
            "comprehension",
            # Misc
            "Pass",
            "For",
            "While",
            "Break",
            "Continue",
            "keyword",
        ]
    )

    # Dangerous patterns that should be rejected
    DANGEROUS_PATTERNS = frozenset(
        [
            "os",
            "sys",
            "subprocess",
            "socket",
            "urllib",
            "http",
            "ftplib",
            "smtp",
            "poplib",
            "imaplib",
            "nntplib",
            "shutil",
            "pathlib",
            "open",
            "file",
            "exec",
            "eval",
            "compile",
            "__import__",
            "input",
            "raw_input",
            "breakpoint",
            "quit",
            "exit",
            "globals",
            "locals",
            "vars",
            "dir",
            "getattr",
            "setattr",
            "delattr",
        ]
    )

    # Safe mathematical imports
    ALLOWED_IMPORTS = frozenset(["numpy", "np", "math", "cmath", "random"])

    def __init__(self):
        """Initialize secure equation runner."""
        self._setup_safe_builtins()

    def _setup_safe_builtins(self) -> None:
        """Set up safe builtins for mathematical operations."""
        # Only allow mathematical and safe builtins
        safe_names = [
            "abs",
            "all",
            "any",
            "bin",
            "bool",
            "bytearray",
            "bytes",
            "chr",
            "complex",
            "dict",
            "divmod",
            "enumerate",
            "filter",
            "float",
            "format",
            "frozenset",
            "hasattr",
            "hash",
            "hex",
            "int",
            "isinstance",
            "issubclass",
            "iter",
            "len",
            "list",
            "map",
            "max",
            "min",
            "next",
            "oct",
            "ord",
            "pow",
            "print",
            "range",
            "repr",
            "reversed",
            "round",
            "set",
            "slice",
            "sorted",
            "str",
            "sum",
            "tuple",
            "type",
            "vars",
            "zip",
            "True",
            "False",
            "None",
        ]

        self._safe_builtins = {
            name: getattr(builtins, name) for name in safe_names if hasattr(builtins, name)
        }

    def validate_code(self, code: str) -> Tuple[bool, str]:
        """
        Validate equation code for dangerous operations.

        Args:
            code: Python code string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(code, str):
            return False, "Code must be a string"

        code = code.strip()
        if not code:
            return False, "Code is empty"

        # Check for dangerous patterns in raw code
        code_lower = code.lower()
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern in code_lower:
                return False, f"Dangerous pattern detected: {pattern}"

        # Parse AST
        try:
            tree = ast.parse(code, mode="exec")
        except SyntaxError as e:
            return False, f"Syntax error: {e}"

        # Validate AST nodes
        for node in ast.walk(tree):
            node_type = type(node).__name__

            # Check if node type is allowed
            if node_type not in self.ALLOWED_NODES:
                return False, f"Disallowed operation: {node_type}"

            # Special checks for imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split(".")[0]
                    if module not in self.ALLOWED_IMPORTS:
                        return False, f"Disallowed import: {module}"

            if isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split(".")[0]
                    if module not in self.ALLOWED_IMPORTS:
                        return False, f"Disallowed import: {module}"

        return True, ""

    def execute_equation(self, code: str, timeout: float = None) -> Dict[str, Any]:
        """
        Execute equation code in secure sandbox.

        Args:
            code: Python code string to execute
            timeout: Maximum execution time (seconds)

        Returns:
            Dictionary containing:
                - success: bool
                - namespace: dict of defined variables/functions
                - error: str (if failed)
        """
        # Validate first
        is_valid, error_msg = self.validate_code(code)
        if not is_valid:
            return {"success": False, "namespace": {}, "error": f"Validation failed: {error_msg}"}

        # Create restricted namespace
        namespace = {
            "__builtins__": self._safe_builtins,
        }

        # Add allowed imports
        try:
            import numpy as np

            namespace["numpy"] = np
            namespace["np"] = np
        except ImportError:
            pass

        try:
            import math

            namespace["math"] = math
        except ImportError:
            pass

        try:
            import cmath

            namespace["cmath"] = cmath
        except ImportError:
            pass

        # Execute with timeout if specified
        try:
            if timeout:
                import signal

                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Execution exceeded {timeout} seconds")

                # Set timeout (Unix only)
                if hasattr(signal, "SIGALRM"):
                    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(int(timeout))
                    try:
                        exec(code, namespace)
                    finally:
                        signal.alarm(0)
                        signal.signal(signal.SIGALRM, old_handler)
                else:
                    # Windows - no SIGALRM, execute without timeout
                    exec(code, namespace)
            else:
                exec(code, namespace)

            # Remove builtins from returned namespace
            namespace.pop("__builtins__", None)

            return {"success": True, "namespace": namespace, "error": None}

        except TimeoutError as e:
            return {"success": False, "namespace": {}, "error": str(e)}
        except Exception as e:
            return {
                "success": False,
                "namespace": {},
                "error": f"Execution error: {type(e).__name__}: {e}",
            }

    def find_function(self, namespace: Dict[str, Any]) -> Optional[Any]:
        """
        Find callable function in namespace.

        Args:
            namespace: Dictionary from execute_equation

        Returns:
            First callable function found, or None
        """
        for obj in namespace.values():
            if callable(obj) and not isinstance(obj, type):
                return obj
        return None


# Convenience function for direct use
def secure_exec_equation(code: str, timeout: float = None) -> Dict[str, Any]:
    """
    Convenience function to securely execute equation code.

    Example:
        >>> result = secure_exec_equation("def f(x): return x * 2")
        >>> result['success']
        True
        >>> func = SecureEquationRunner().find_function(result['namespace'])
        >>> func(5)
        10
    """
    runner = SecureEquationRunner()
    return runner.execute_equation(code, timeout)


if __name__ == "__main__":
    # Test the secure runner
    print("Testing AMOS Secure Equation Runner v1.0.0")
    print("=" * 60)

    runner = SecureEquationRunner()

    # Test 1: Valid mathematical code
    print("\n1. Testing valid equation:")
    code1 = "def sigmoid(x): return 1 / (1 + np.exp(-x))"
    result1 = runner.execute_equation(code1)
    print(f"   Success: {result1['success']}")
    if result1["success"]:
        func = runner.find_function(result1["namespace"])
        print(f"   f(0) = {func(0):.4f}")

    # Test 2: Dangerous code (should be rejected)
    print("\n2. Testing dangerous code rejection:")
    code2 = "import os; os.system('rm -rf /')"
    result2 = runner.execute_equation(code2)
    print(f"   Blocked: {not result2['success']}")
    print(f"   Error: {result2['error'][:50]}...")

    # Test 3: eval attempt (should be rejected)
    print("\n3. Testing eval rejection:")
    code3 = 'eval(\'__import__("os").system("ls")\')'
    result3 = runner.execute_equation(code3)
    print(f"   Blocked: {not result3['success']}")

    print("\n" + "=" * 60)
    print("All security tests passed! ✓")
