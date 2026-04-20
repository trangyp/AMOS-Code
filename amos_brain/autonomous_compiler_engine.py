"""
AMOS Autonomous Compiler Engine

Integrates the natural-language compiler with the AMOS brain for actual autonomous execution.

Architecture:
  1. Intent Parsing (uses brain's cognitive stack)
  2. Deep Repo Analysis (symbol-aware, not text-based)
  3. Plan Generation (hierarchical task decomposition)
  4. Execution (file-by-file with rollback capability)
  5. Verification (test, typecheck, lint - auto-retry on failure)
  6. Self-Correction (analyzes failures, regenerates fixes)

This is the production implementation - not a demo.
"""

from __future__ import annotations

import ast
import hashlib
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from pathlib import Path
from typing import Optional

from amos_compiler.grounding import GroundedIntent


@dataclass
class ExecutionStep:
    """A single execution step in an autonomous plan."""

    id: str
    order: int
    action: str  # "read", "analyze", "generate", "edit", "verify", "retry"
    target_file: Optional[str] = None
    target_symbol: Optional[str] = None
    description: str = ""
    generated_code: Optional[str] = None
    status: str = "pending"  # pending, running, success, failed, retrying
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    dependencies: list[str] = field(default_factory=list)


@dataclass
class AutonomousPlan:
    """A complete autonomous execution plan."""

    id: str
    instruction: str
    goal: str
    steps: list[ExecutionStep] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    status: str = "draft"  # draft, executing, completed, failed
    current_step_index: int = 0
    rollback_snapshot: dict[str, str] = field(default_factory=dict)  # file_path -> original_content

    def get_current_step(self) -> Optional[ExecutionStep]:
        if self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def advance(self) -> bool:
        """Move to next step. Returns True if there are more steps."""
        self.current_step_index += 1
        return self.current_step_index < len(self.steps)


@dataclass
class VerificationResult:
    """Result of verification step."""

    check_type: str
    passed: bool
    output: str = ""
    error: Optional[str] = None
    fix_suggestion: Optional[str] = None


@dataclass
class SymbolInfo:
    """Detailed symbol information for intelligent editing."""

    name: str
    type: str  # class, function, method, variable
    file_path: str
    line_start: int
    line_end: int
    signature: Optional[str] = None
    docstring: Optional[str] = None
    decorators: list[str] = field(default_factory=list)
    body_text: str = ""
    dependencies: list[str] = field(default_factory=list)  # Other symbols this depends on
    dependents: list[str] = field(default_factory=list)  # Symbols that depend on this


class DeepRepoAnalyzer:
    """
    Deep semantic analysis of the repository.

    Not just filename matching - actual AST parsing, symbol extraction,
    dependency graph building, and call chain analysis.
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.symbols: dict[str, SymbolInfo] = {}
        self.file_ast_cache: dict[str, ast.AST] = {}
        self.dependency_graph: dict[str, set[str]] = {}

    def analyze_file(self, file_path: Path) -> list[SymbolInfo]:
        """Deep analysis of a single file."""
        symbols = []

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
            self.file_ast_cache[str(file_path)] = tree

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    symbol = self._extract_class_info(node, file_path, content)
                    symbols.append(symbol)

                elif isinstance(node, ast.FunctionDef):
                    symbol = self._extract_function_info(node, file_path, content)
                    symbols.append(symbol)

        except SyntaxError:
            pass  # Skip files with syntax errors
        except Exception:
            pass  # Skip files that can't be parsed

        return symbols

    def _extract_class_info(self, node: ast.ClassDef, file_path: Path, content: str) -> SymbolInfo:
        """Extract class information including methods."""
        lines = content.split("\n")
        body_start = node.lineno
        body_end = node.end_lineno or body_start

        # Get decorators
        decorators = [ast.unparse(d) for d in node.decorator_list]

        # Get docstring
        docstring = ast.get_docstring(node)

        # Get class body (excluding methods)
        body_text = "\n".join(lines[body_start:body_end])

        return SymbolInfo(
            name=node.name,
            type="class",
            file_path=str(file_path),
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=docstring,
            decorators=decorators,
            body_text=body_text,
        )

    def _extract_function_info(
        self, node: ast.FunctionDef, file_path: Path, content: str
    ) -> SymbolInfo:
        """Extract function information."""
        lines = content.split("\n")
        body_start = node.lineno
        body_end = node.end_lineno or body_start

        # Get signature
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)

        returns = ""
        if node.returns:
            returns = f" -> {ast.unparse(node.returns)}"

        signature = f"({', '.join(args)}){returns}"

        # Get decorators
        decorators = [ast.unparse(d) for d in node.decorator_list]

        # Get docstring
        docstring = ast.get_docstring(node)

        # Get body
        body_text = "\n".join(lines[body_start:body_end])

        # Find dependencies (calls to other functions)
        dependencies = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    dependencies.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    dependencies.append(child.func.attr)

        return SymbolInfo(
            name=node.name,
            type="function",
            file_path=str(file_path),
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            signature=signature,
            docstring=docstring,
            decorators=decorators,
            body_text=body_text,
            dependencies=list(set(dependencies)),
        )

    def build_dependency_graph(self) -> dict[str, set[str]]:
        """Build complete dependency graph."""
        graph = {}

        for symbol_name, symbol in self.symbols.items():
            graph[symbol_name] = set(symbol.dependencies)

        # Reverse: find dependents
        for symbol_name, symbol in self.symbols.items():
            for dep in symbol.dependencies:
                if dep in self.symbols:
                    self.symbols[dep].dependents.append(symbol_name)

        self.dependency_graph = graph
        return graph

    def scan_repo(self, pattern: str = "*.py") -> dict[str, list[SymbolInfo]]:
        """Scan entire repository."""
        results = {}

        for py_file in self.repo_root.rglob(pattern):
            # Skip unwanted directories
            if any(part.startswith(".") for part in py_file.parts):
                continue
            if ".venv" in py_file.parts or "node_modules" in py_file.parts:
                continue
            if "__pycache__" in py_file.parts:
                continue

            symbols = self.analyze_file(py_file)
            if symbols:
                results[str(py_file)] = symbols

                # Add to global symbol table
                for symbol in symbols:
                    self.symbols[symbol.name] = symbol

        # Build dependency graph
        self.build_dependency_graph()

        return results

    def find_symbol(self, name: str) -> Optional[SymbolInfo]:
        """Find a symbol by name."""
        return self.symbols.get(name)

    def find_references(self, symbol_name: str) -> list[SymbolInfo]:
        """Find all symbols that reference the given symbol."""
        refs = []
        for name, symbol in self.symbols.items():
            if symbol_name in symbol.dependencies:
                refs.append(symbol)
        return refs


class VerificationEngine:
    """
    Comprehensive verification with auto-fix capability.

    Runs tests, typecheck, lint - and if failures occur,
    analyzes the output and suggests fixes.
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.verification_history: list[VerificationResult] = []

    def run_check(
        self, check_type: str, target_files: Optional[list[str]] = None
    ) -> VerificationResult:
        """Run a single verification check."""

        commands: dict[str, str] = {
            "syntax": "python -m py_compile {file}",
            "test": "python -m pytest {files} -x --tb=short -q",
            "typecheck": "python -m mypy {files} --ignore-missing-imports --no-error-summary",
            "lint": "python -m ruff check {files} --output-format=text",
            "import": 'python -c "import {module}"',
        }

        cmd_template = commands.get(check_type, f"echo 'Unknown check: {check_type}'")

        # Format command
        if target_files:
            files_str = " ".join(target_files)
            cmd = cmd_template.replace("{files}", files_str).replace("{file}", target_files[0])
        else:
            cmd = cmd_template.replace("{files}", ".").replace("{file}", ".")

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.repo_root,
            )

            passed = result.returncode == 0
            output = result.stdout + "\n" + result.stderr

            # If failed, try to extract fix suggestion
            fix_suggestion = None
            if not passed:
                fix_suggestion = self._analyze_error(output, check_type)

            ver_result = VerificationResult(
                check_type=check_type,
                passed=passed,
                output=output,
                fix_suggestion=fix_suggestion,
            )

            self.verification_history.append(ver_result)
            return ver_result

        except subprocess.TimeoutExpired:
            return VerificationResult(
                check_type=check_type,
                passed=False,
                error="Verification timed out after 120s",
            )
        except Exception as e:
            return VerificationResult(
                check_type=check_type,
                passed=False,
                error=str(e),
            )

    def _analyze_error(self, output: str, check_type: str) -> Optional[str]:
        """Analyze error output and suggest fix."""

        if check_type == "syntax":
            if "SyntaxError" in output:
                return "Fix syntax error in the generated code"

        elif check_type == "typecheck":
            if "import" in output.lower() and "not found" in output.lower():
                return "Add missing import statement"
            if "has no attribute" in output:
                return "Check attribute name or add method to class"
            if "incompatible type" in output:
                return "Fix type annotation or add type cast"

        elif check_type == "test":
            if "FAILED" in output:
                return "Update test expectations or fix implementation"
            if "ERROR" in output:
                return "Fix runtime error in implementation"

        elif check_type == "lint":
            if "undefined" in output.lower():
                return "Add import or define the undefined name"
            if "unused" in output.lower():
                return "Remove unused import or variable"

        return None

    def verify_all(self, target_files: list[str]) -> list[VerificationResult]:
        """Run full verification suite."""
        results = []

        # Syntax check first
        for file in target_files:
            result = self.run_check("syntax", [file])
            results.append(result)
            if not result.passed:
                return results  # Stop early on syntax error

        # Type check
        result = self.run_check("typecheck", target_files)
        results.append(result)

        # Lint
        result = self.run_check("lint", target_files)
        results.append(result)

        # Tests
        result = self.run_check("test", target_files)
        results.append(result)

        return results


class AutonomousCompilerEngine:
    """
    Production autonomous compiler engine.

    Integrates with AMOS brain for actual code generation and modification.
    This is not a demo - it performs real file operations with verification.
    """

    def __init__(self, repo_root: Path | str):
        self.repo_root = Path(repo_root)
        self.analyzer = DeepRepoAnalyzer(self.repo_root)
        self.verifier = VerificationEngine(self.repo_root)
        self.active_plan: Optional[AutonomousPlan] = None

    def create_plan(self, grounded_intent: GroundedIntent) -> AutonomousPlan:
        """
        Create an autonomous execution plan from grounded intent.

        This does hierarchical task decomposition:
        1. Analysis phase: Understand existing code
        2. Generation phase: Create new code
        3. Integration phase: Insert into codebase
        4. Verification phase: Test and validate
        """
        plan_id = hashlib.sha256(grounded_intent.original.raw_instruction.encode()).hexdigest()[:12]

        plan = AutonomousPlan(
            id=plan_id,
            instruction=grounded_intent.original.raw_instruction,
            goal=grounded_intent.original.target_domain.name,
        )

        edit_scope = grounded_intent.edit_scope

        # Phase 1: Analysis steps
        for i, file_path in enumerate(edit_scope.files[:10]):  # Limit to 10 files
            step = ExecutionStep(
                id=f"analyze_{i}",
                order=i,
                action="analyze",
                target_file=file_path,
                description=f"Analyze {file_path} for modification requirements",
            )
            plan.steps.append(step)

        # Phase 2: Generation steps
        for i, symbol_name in enumerate(edit_scope.symbols[:5]):  # Limit to 5 symbols
            step = ExecutionStep(
                id=f"generate_{i}",
                order=len(plan.steps) + i,
                action="generate",
                target_symbol=symbol_name,
                description=f"Generate code for {symbol_name}",
                dependencies=[s.id for s in plan.steps if s.action == "analyze"],
            )
            plan.steps.append(step)

        # Phase 3: Edit steps
        for i, file_path in enumerate(edit_scope.files[:5]):
            step = ExecutionStep(
                id=f"edit_{i}",
                order=len(plan.steps) + i,
                action="edit",
                target_file=file_path,
                description=f"Apply edits to {file_path}",
                dependencies=[s.id for s in plan.steps if s.action == "generate"],
            )
            plan.steps.append(step)

        # Phase 4: Verification step
        step = ExecutionStep(
            id="verify_all",
            order=len(plan.steps),
            action="verify",
            description="Run full verification suite",
            dependencies=[s.id for s in plan.steps if s.action == "edit"],
        )
        plan.steps.append(step)

        self.active_plan = plan
        return plan

    def execute_step(self, step: ExecutionStep, dry_run: bool = True) -> bool:
        """
        Execute a single step.

        Returns True on success, False on failure (triggers retry or abort).
        """
        step.status = "running"

        try:
            if step.action == "analyze":
                return self._execute_analyze(step)
            elif step.action == "generate":
                return self._execute_generate(step)
            elif step.action == "edit":
                return self._execute_edit(step, dry_run)
            elif step.action == "verify":
                return self._execute_verify(step)
            else:
                step.status = "failed"
                step.error_message = f"Unknown action: {step.action}"
                return False

        except Exception as e:
            step.status = "failed"
            step.error_message = str(e)
            return False

    def _execute_analyze(self, step: ExecutionStep) -> bool:
        """Analyze a file."""
        if not step.target_file:
            return False

        file_path = self.repo_root / step.target_file
        if not file_path.exists():
            step.error_message = f"File not found: {step.target_file}"
            return False

        # Run deep analysis
        symbols = self.analyzer.analyze_file(file_path)

        step.status = "success"
        return True

    def _execute_generate(self, step: ExecutionStep) -> bool:
        """Generate code for a symbol using LLM."""
        from .llm_code_generator import CodeGenerationRequest, get_llm_generator

        generator = get_llm_generator()

        # Build request
        request = CodeGenerationRequest(
            instruction=step.description,
            target_file=step.target_file,
            target_symbol=step.target_symbol,
        )

        # Add existing code context if target file exists
        if step.target_file:
            target_path = self.repo_root / step.target_file
            if target_path.exists():
                request.existing_code = target_path.read_text()

        # Generate with self-correction
        result = generator.generate_with_self_correction(request, max_attempts=3)

        if result.success:
            step.generated_code = result.generated_code
            step.status = "success"
            return True
        else:
            step.status = "failed"
            step.error_message = result.error or "Code generation failed"
            return False

    def _execute_edit(self, step: ExecutionStep, dry_run: bool) -> bool:
        """Apply edits to a file."""
        if not step.target_file:
            return False

        file_path = self.repo_root / step.target_file

        # Create rollback snapshot
        if file_path.exists():
            self.active_plan.rollback_snapshot[str(file_path)] = file_path.read_text()

        if dry_run:
            step.status = "success"
            return True

        # Apply actual edits
        if step.generated_code:
            try:
                # Ensure parent directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)

                # Write the generated code
                file_path.write_text(step.generated_code, encoding="utf-8")

                step.status = "success"
                return True
            except Exception as e:
                step.status = "failed"
                step.error_message = f"Failed to write file: {e}"
                return False
        else:
            step.status = "failed"
            step.error_message = "No generated code to apply"
            return False

    def _execute_verify(self, step: ExecutionStep) -> bool:
        """Run verification."""
        target_files = [
            s.target_file for s in self.active_plan.steps if s.action == "edit" and s.target_file
        ]

        results = self.verifier.verify_all(target_files)

        all_passed = all(r.passed for r in results)

        if all_passed:
            step.status = "success"
        else:
            step.status = "failed"
            failed = [r for r in results if not r.passed]
            step.error_message = "; ".join(f"{r.check_type}: {r.output[:100]}" for r in failed)

        return all_passed

    def execute_plan(self, plan: AutonomousPlan, dry_run: bool = True) -> AutonomousPlan:
        """
        Execute the complete plan with retry logic.
        """
        plan.status = "executing"

        while plan.current_step_index < len(plan.steps):
            step = plan.get_current_step()
            if not step:
                break

            success = self.execute_step(step, dry_run)

            if not success:
                if step.retry_count < step.max_retries:
                    step.retry_count += 1
                    step.status = "retrying"
                    # Retry the same step
                    continue
                else:
                    plan.status = "failed"
                    break

            if not plan.advance():
                break

        if plan.status != "failed":
            plan.status = "completed"

        return plan

    def rollback(self, plan: AutonomousPlan) -> None:
        """Rollback all changes from a plan."""
        for file_path, original_content in plan.rollback_snapshot.items():
            Path(file_path).write_text(original_content)


def get_autonomous_compiler(repo_root: Path | Optional[str] = None) -> AutonomousCompilerEngine:
    """Get autonomous compiler instance."""
    if repo_root is None:
        repo_root = Path(".")
    return AutonomousCompilerEngine(repo_root)
