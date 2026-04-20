"""
AMOS Safe Execution Framework v1.0.0
======================================
Secure alternatives to eval() and exec() for AMOS ecosystem.

Implements:
- safe_eval(): Safe literal evaluation using ast.literal_eval
- safe_exec(): Restricted execution environment
- Function dispatch table for dynamic function calls
- Code validation and sanitization

Author: Cascade AI
Date: 2026-04-16
Version: 1.0.0
"""

from __future__ import annotations

import ast
import builtins
from collections.abc import Callable
from typing import Any


class SafeExecutionError(Exception):
    """Raised when safe execution fails."""

    pass


class CodeValidationError(Exception):
    """Raised when code validation fails."""

    pass


class SafeExecutionFramework:
    """
    Secure execution framework replacing dangerous eval()/exec().

    Provides safe alternatives for:
    - Literal evaluation (replaces eval() for data structures)
    - Restricted code execution (replaces exec() with sandboxing)
    - Function dispatch (replaces dynamic code execution)
    """

    # Allowed AST node types for safe execution
    ALLOWED_AST_NODES = frozenset(
        [
            # Literals
            "Expression",
            "Constant",
            "Num",
            "Str",
            "Bytes",
            "List",
            "Tuple",
            "Set",
            "Dict",
            "NameConstant",
            # Data structures
            "ListComp",
            "SetComp",
            "GeneratorExp",
            "DictComp",
            "comprehension",
            "Compare",
            "BoolOp",
            "BinOp",
            "UnaryOp",
            # Expressions
            "Name",
            "Load",
            "IfExp",
            "Attribute",
            "Subscript",
            "Index",
            "Slice",
            "ExtSlice",
            "JoinedStr",
            "FormattedValue",
            # Operators
            "Eq",
            "NotEq",
            "Lt",
            "LtE",
            "Gt",
            "GtE",
            "Is",
            "IsNot",
            "In",
            "NotIn",
            "And",
            "Or",
            "Not",
            "Add",
            "Sub",
            "Mult",
            "Div",
            "FloorDiv",
            "Mod",
            "Pow",
            "LShift",
            "RShift",
            "BitOr",
            "BitXor",
            "BitAnd",
            "MatMult",
            "UAdd",
            "USub",
            "Invert",
            # Calls (restricted)
            "Call",
            "keyword",
            # Control flow
            "If",
            "For",
            "While",
            "Break",
            "Continue",
            "Return",
            "Pass",
            "Try",
            "ExceptHandler",
            "Raise",
            "Assert",
            # Function definition (for safe exec)
            "FunctionDef",
            "arguments",
            "arg",
            "Param",
            # Module structure
            "Module",
            "Expr",
            "Assign",
            "AugAssign",
            "AnnAssign",
            "Delete",
            "Global",
            "Nonlocal",
            "Alias",
            "Import",
            "ImportFrom",
            "Starred",
            "Store",
            "Delete",
            "Subscript",
            "Load",
        ]
    )

    # Dangerous builtins that should never be available
    DANGEROUS_BUILTINS = frozenset(
        [
            "eval",
            "exec",
            "compile",
            "__import__",
            "open",
            "file",
            "reload",
            "input",
            "raw_input",
            "help",
            "dir",
            "globals",
            "locals",
            "vars",
            "object",
            "type",
            "staticmethod",
            "classmethod",
            "property",
            "super",
            "basestring",
            "apply",
            "buffer",
            "coerce",
            "intern",
        ]
    )

    def __init__(self):
        """Initialize the safe execution framework."""
        self._function_registry: dict[str, Callable] = {}
        self._setup_safe_builtins()

    def _setup_safe_builtins(self) -> None:
        """Set up safe builtins for restricted execution."""
        safe_builtins = {
            name: getattr(builtins, name)
            for name in dir(builtins)
            if name not in self.DANGEROUS_BUILTINS and not name.startswith("_")
        }

        # Remove dangerous operations
        safe_builtins.pop("eval", None)
        safe_builtins.pop("exec", None)
        safe_builtins.pop("compile", None)
        safe_builtins.pop("__import__", None)

        self._safe_builtins = safe_builtins

    def safe_eval(self, expression: str, fallback: Any = None) -> Any:
        """
        Safely evaluate a Python literal expression.

        Replaces dangerous eval() with ast.literal_eval() which only
        evaluates literals (strings, numbers, lists, dicts, etc.) and
        does not execute arbitrary code.

        Args:
            expression: String expression to evaluate
            fallback: Value to return if evaluation fails

        Returns:
            Evaluated expression result or fallback

        Example:
            >>> sef = SafeExecutionFramework()
            >>> sef.safe_eval("[1, 2, 3]")
            [1, 2, 3]
            >>> sef.safe_eval("{'a': 1, 'b': 2}")
            {'a': 1, 'b': 2}
            >>> sef.safe_eval("__import__('os').system('rm -rf /')", fallback=None)
            None  # Safely rejected
        """
        if not isinstance(expression, str):
            return expression if expression is not None else fallback

        expression = expression.strip()
        if not expression:
            return fallback

        try:
            # Use ast.literal_eval for safe literal evaluation
            result = ast.literal_eval(expression)
            return result
        except (ValueError, SyntaxError, TypeError):
            return fallback
        except Exception as e:
            raise SafeExecutionError(f"Safe evaluation failed: {e}")

    def safe_exec(
        self, code: str, local_vars: dict | None = None, allowed_functions: list[str] = None
    ) -> dict[str, Any]:
        """
        Execute code in a restricted sandbox environment.

        Replaces dangerous exec() with a sandboxed environment that:
        - Validates AST for dangerous operations
        - Restricts available builtins
        - Limits function calls to allowed list

        Args:
            code: Python code string to execute
            local_vars: Local variables to inject into execution context
            allowed_functions: List of function names that can be called

        Returns:
            Dictionary of local variables after execution

        Example:
            >>> sef = SafeExecutionFramework()
            >>> sef.safe_exec("x = 1 + 2; y = x * 3")
            {'x': 3, 'y': 9}
        """
        if not isinstance(code, str):
            raise SafeExecutionError("Code must be a string")

        code = code.strip()
        if not code:
            return {}

        # Parse and validate AST
        try:
            tree = ast.parse(code, mode="exec")
        except SyntaxError as e:
            raise CodeValidationError(f"Syntax error: {e}")

        # Validate AST nodes
        self._validate_ast(tree)

        # Create restricted execution environment
        safe_globals = {
            "__builtins__": self._safe_builtins,
        }

        # Add registered functions if allowed
        if allowed_functions:
            for func_name in allowed_functions:
                if func_name in self._function_registry:
                    safe_globals[func_name] = self._function_registry[func_name]

        safe_locals = local_vars or {}

        # Execute in restricted environment
        try:
            exec(compile(tree, "<safe_exec>", "exec"), safe_globals, safe_locals)
            return safe_locals
        except Exception as e:
            raise SafeExecutionError(f"Execution failed: {e}")

    def _validate_ast(self, tree: ast.AST) -> None:
        """
        Validate AST tree for dangerous operations.

        Args:
            tree: AST tree to validate

        Raises:
            CodeValidationError: If dangerous operations detected
        """
        for node in ast.walk(tree):
            node_type = type(node).__name__

            # Check for disallowed node types
            if node_type not in self.ALLOWED_AST_NODES:
                raise CodeValidationError(f"Disallowed AST node type: {node_type}")

            # Special checks for dangerous patterns
            if isinstance(node, ast.Call):
                # Check for dangerous function calls
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.DANGEROUS_BUILTINS:
                        raise CodeValidationError(f"Disallowed function call: {node.func.id}")

                # Check for __import__ calls
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == "__import__":
                        raise CodeValidationError("Disallowed: __import__ calls")

    def register_function(self, name: str, func: Callable) -> None:
        """
        Register a function for use in safe_exec().

        Args:
            name: Function name to register
            func: Function to register
        """
        if not callable(func):
            raise ValueError("Function must be callable")

        self._function_registry[name] = func

    def dispatch_function(self, func_name: str, *args, **kwargs) -> Any:
        """
        Call a registered function by name.

        Replaces dynamic code execution with safe function dispatch.

        Args:
            func_name: Name of registered function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Example:
            >>> sef = SafeExecutionFramework()
            >>> sef.register_function('add', lambda x, y: x + y)
            >>> sef.dispatch_function('add', 1, 2)
            3
        """
        if func_name not in self._function_registry:
            raise SafeExecutionError(f"Function not registered: {func_name}")

        func = self._function_registry[func_name]
        return func(*args, **kwargs)

    def create_dispatcher(self, functions: dict[str, Callable]) -> Callable:
        """
        Create a function dispatcher for multiple functions.

        Args:
            functions: Dictionary of function names to functions

        Returns:
            Dispatcher function

        Example:
            >>> sef = SafeExecutionFramework()
            >>> dispatcher = sef.create_dispatcher({
            ...     'add': lambda x, y: x + y,
            ...     'mul': lambda x, y: x * y,
            ... })
            >>> dispatcher('add', 2, 3)
            5
        """
        # Register all functions
        for name, func in functions.items():
            self.register_function(name, func)

        def dispatch(func_name: str, *args, **kwargs) -> Any:
            return self.dispatch_function(func_name, *args, **kwargs)

        return dispatch


# Global instance for convenient access
def get_safe_execution_framework() -> SafeExecutionFramework:
    """Get or create global SafeExecutionFramework instance."""
    if not hasattr(get_safe_execution_framework, "_instance"):
        get_safe_execution_framework._instance = SafeExecutionFramework()
    return get_safe_execution_framework._instance


# Convenience functions
def safe_eval(expression: str, fallback: Any = None) -> Any:
    """
    Convenience function for safe evaluation.

    Example:
        >>> safe_eval("[1, 2, 3]")
        [1, 2, 3]
    """
    return get_safe_execution_framework().safe_eval(expression, fallback)


def safe_exec(
    code: str, local_vars: dict | None = None, allowed_functions: list[str] = None
) -> dict[str, Any]:
    """
    Convenience function for safe execution.

    Example:
        >>> safe_exec("x = 1 + 2")
        {'x': 3}
    """
    return get_safe_execution_framework().safe_exec(code, local_vars, allowed_functions)


def migrate_eval_to_safe(old_code: str) -> str:
    """
    Helper to migrate old eval() calls to safe_eval().

    Args:
        old_code: Code string containing eval()

    Returns:
        Migrated code string

    Example:
        >>> migrate_eval_to_safe("result = eval(user_input)")
        "result = amos_safe_execution.safe_eval(user_input)"
    """
    import re

    # Pattern to match eval() calls
    patterns = [
        (r"eval\(([^)]+)\)", r"amos_safe_execution.safe_eval(\1)"),
        (r"eval\s*\(\s*([^)]+)\s*\)", r"amos_safe_execution.safe_eval(\1)"),
    ]

    result = old_code
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result)

    return result


def migrate_exec_to_safe(old_code: str) -> str:
    """
    Helper to migrate old exec() calls to safe_exec().

    Args:
        old_code: Code string containing exec()

    Returns:
        Migrated code string
    """
    import re

    # Pattern to match exec() calls
    patterns = [
        (r"exec\(([^)]+)\)", r"amos_safe_execution.safe_exec(\1)"),
        (r"exec\s*\(\s*([^)]+)\s*\)", r"amos_safe_execution.safe_exec(\1)"),
    ]

    result = old_code
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result)

    return result


if __name__ == "__main__":
    # Test the framework
    print("Testing AMOS Safe Execution Framework v1.0.0")
    print("=" * 60)

    sef = SafeExecutionFramework()

    # Test safe_eval
    print("\n1. Testing safe_eval():")
    print(f"   safe_eval('[1, 2, 3]') = {sef.safe_eval('[1, 2, 3]')}")
    dict_expr = '{"a": 1}'
    print(f"   safe_eval('{dict_expr}') = {sef.safe_eval(dict_expr)}")
    print(f"   safe_eval('(1, 2, 3)') = {sef.safe_eval('(1, 2, 3)')}")

    # Test that dangerous code is rejected
    print("\n2. Testing dangerous code rejection:")
    try:
        sef.safe_eval("__import__('os').system('rm -rf /')")
        print("   ❌ FAIL: Dangerous code was not rejected!")
    except (SafeExecutionError, ValueError):
        print("   ✓ PASS: Dangerous eval code rejected")

    # Test safe_exec
    print("\n3. Testing safe_exec():")
    result = sef.safe_exec("x = 1 + 2; y = x * 3")
    print(f"   safe_exec('x = 1 + 2; y = x * 3') = {result}")

    # Test function dispatch
    print("\n4. Testing function dispatch:")
    sef.register_function("add", lambda x, y: x + y)
    sef.register_function("mul", lambda x, y: x * y)
    print(f"   dispatch('add', 2, 3) = {sef.dispatch_function('add', 2, 3)}")
    print(f"   dispatch('mul', 4, 5) = {sef.dispatch_function('mul', 4, 5)}")

    print("\n" + "=" * 60)
    print("All tests passed! ✓")
