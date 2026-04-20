#!/usr/bin/env python3
"""AMOS Self-coding System - Section 15 of Architecture

Enables AMOS to generate, modify, and improve its own code.
Uses Repo Intelligence to understand structure, then generates
new code following AMOS architectural principles.
"""

import ast
from dataclasses import dataclass, field
from datetime import UTC, datetime

UTC = UTC
from pathlib import Path
from typing import Any


@dataclass
class CodeTemplate:
    """Template for generating code."""

    name: str
    description: str
    template_type: str  # class, function, module, method
    parameters: list[dict[str, str]] = field(default_factory=list)
    body_template: str = ""
    imports: list[str] = field(default_factory=list)
    docstring_template: str = ""


@dataclass
class GeneratedCode:
    """Result of code generation."""

    code: str
    template_used: str
    target_file: str
    entity_name: str
    generated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    validation_status: str = "pending"  # pending, valid, invalid
    errors: list[str] = field(default_factory=list)


class CodeGenerator:
    """Generate new code following AMOS patterns."""

    TEMPLATES = {
        "amos_component": CodeTemplate(
            name="AMOS Component",
            description="Standard AMOS system component",
            template_type="class",
            parameters=[
                {"name": "component_name", "type": "str", "description": "Name of component"},
                {"name": "purpose", "type": "str", "description": "What this component does"},
            ],
            imports=["from dataclasses import dataclass", "from typing import Any"],
            docstring_template='"""\n{purpose}\n\nPart of AMOS architecture.\n"""',
            body_template='''
@dataclass
class {component_name}:
    """{purpose}"""

    # State
    state: dict[str, Any] = field(default_factory=dict)

    def __init__(self):
        self.initialize()

    def initialize(self):
        """Initialize component state."""
        pass

    def process(self, input_data: Any) -> Any:
        """Main processing function."""
        # Implementation here
        return input_data
''',
        ),
        "amos_function": CodeTemplate(
            name="AMOS Function",
            description="Utility function following AMOS patterns",
            template_type="function",
            parameters=[
                {"name": "function_name", "type": "str"},
                {"name": "purpose", "type": "str"},
                {"name": "input_type", "type": "str", "default": "Any"},
                {"name": "output_type", "type": "str", "default": "Any"},
            ],
            docstring_template='"""\n{purpose}\n\nArgs:\n    input_data: Input to process\n\nReturns:\n    Processed result\n"""',
            body_template='''
def {function_name}(input_data: {input_type}) -> {output_type}:
    """{purpose}"""
    # Validate input
    if input_data is None:
        return None

    # Process
    result = input_data  # Transform here

    return result
''',
        ),
        "amos_test": CodeTemplate(
            name="AMOS Test",
            description="Unit test for AMOS component",
            template_type="function",
            parameters=[
                {"name": "component_name", "type": "str"},
                {"name": "test_scenario", "type": "str"},
            ],
            imports=["import unittest"],
            docstring_template='"""\nTest {component_name}: {test_scenario}\n"""',
            body_template='''
def test_{component_name}_{test_scenario}():
    """Test {component_name}: {test_scenario}"""
    # Arrange
    component = {component_name}()

    # Act
    result = component.process(None)

    # Assert
    assert result is not None
    print(f"✓ {test_scenario} passed")
''',
        ),
    }

    def generate(
        self, template_name: str, params: dict[str, str], target_file: str = "generated.py"
    ) -> GeneratedCode:
        """Generate code from template."""
        template = self.TEMPLATES.get(template_name)
        if not template:
            return GeneratedCode(
                code="",
                template_used=template_name,
                target_file=target_file,
                entity_name="error",
                validation_status="invalid",
                errors=[f"Template {template_name} not found"],
            )

        # Fill template
        code_parts = []

        # Add imports
        for imp in template.imports:
            code_parts.append(imp)
        if template.imports:
            code_parts.append("")

        # Generate docstring
        if template.docstring_template:
            docstring = template.docstring_template.format(**params)
            params_with_doc = {**params, "docstring": docstring}
        else:
            params_with_doc = params

        # Fill body template
        body = template.body_template.format(**params_with_doc)
        code_parts.append(body)

        code = "\n".join(code_parts)

        return GeneratedCode(
            code=code,
            template_used=template_name,
            target_file=target_file,
            entity_name=params.get("component_name", params.get("function_name", "unknown")),
            validation_status="pending",
        )

    def validate_code(self, generated: GeneratedCode) -> GeneratedCode:
        """Validate generated code for syntax errors."""
        try:
            ast.parse(generated.code)
            generated.validation_status = "valid"
        except SyntaxError as e:
            generated.validation_status = "invalid"
            generated.errors.append(f"Syntax error: {e}")

        return generated


class CodeModifier:
    """Modify existing code safely."""

    def __init__(self, backup_dir: str = "code_backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

    def backup_file(self, file_path: str) -> str:
        """Create backup before modification."""
        original = Path(file_path)
        if not original.exists():
            return ""

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_name = f"{original.stem}_{timestamp}{original.suffix}"
        backup_path = self.backup_dir / backup_name

        backup_path.write_text(original.read_text())
        return str(backup_path)

    def add_method(self, file_path: str, class_name: str, method_code: str) -> dict[str, Any]:
        """Add method to existing class."""
        # Backup first
        backup = self.backup_file(file_path)

        try:
            with open(file_path) as f:
                content = f.read()

            # Parse to find insertion point
            tree = ast.parse(content)

            # Find class
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    # Insert after last method
                    insert_line = (
                        node.end_lineno if hasattr(node, "end_lineno") else len(content.split("\n"))
                    )

                    # Add method
                    lines = content.split("\n")
                    indent = "    "
                    method_lines = method_code.strip().split("\n")
                    indented_method = [
                        indent + line if line.strip() else line for line in method_lines
                    ]

                    # Insert
                    lines.insert(insert_line - 1, "\n" + "\n".join(indented_method))

                    new_content = "\n".join(lines)

                    # Validate
                    try:
                        ast.parse(new_content)
                    except SyntaxError as e:
                        return {"success": False, "error": str(e), "backup": backup}

                    # Write
                    with open(file_path, "w") as f:
                        f.write(new_content)

                    return {"success": True, "backup": backup, "lines_added": len(method_lines)}

            return {"success": False, "error": f"Class {class_name} not found", "backup": backup}

        except Exception as e:
            return {"success": False, "error": str(e), "backup": backup}

    def refactor_extract_method(
        self, file_path: str, start_line: int, end_line: int, new_method_name: str
    ) -> dict[str, Any]:
        """Extract code block into new method."""
        backup = self.backup_file(file_path)

        try:
            with open(file_path) as f:
                lines = f.readlines()

            # Extract code
            extracted_code = lines[start_line - 1 : end_line]
            extracted_text = "".join(extracted_code)

            # Create method
            method_def = f"\n    def {new_method_name}(self):\n"
            indented_code = ["        " + line for line in extracted_code]
            method_body = method_def + "".join(indented_code) + "\n"

            # Replace original with method call
            method_call = f"        self.{new_method_name}()\n"
            new_lines = lines[: start_line - 1] + [method_call] + lines[end_line:]

            # Find class end to insert method
            # (Simplified: insert at end of file within class)
            # In real implementation, would find proper class scope

            new_content = "".join(new_lines) + method_body

            # Validate
            try:
                ast.parse(new_content)
            except SyntaxError as e:
                return {"success": False, "error": str(e), "backup": backup}

            with open(file_path, "w") as f:
                f.write(new_content)

            return {
                "success": True,
                "backup": backup,
                "new_method": new_method_name,
                "lines_extracted": end_line - start_line + 1,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "backup": backup}


class SelfImprovement:
    """Self-improvement strategies for AMOS."""

    IMPROVEMENT_PATTERNS = {
        "reduce_complexity": {
            "detect": lambda entity: entity.get("complexity", 0) > 20,
            "action": "Extract methods to reduce complexity",
        },
        "add_docstrings": {
            "detect": lambda entity: not entity.get("docstring"),
            "action": "Generate docstring from name and parameters",
        },
        "improve_naming": {
            "detect": lambda entity: (
                len(entity.get("name", "")) < 3 or "_" not in entity.get("name", "")
            ),
            "action": "Suggest clearer name following conventions",
        },
        "add_type_hints": {
            "detect": lambda entity: "->" not in entity.get("signature", ""),
            "action": "Add type annotations",
        },
    }

    def analyze_for_improvement(self, code_entities: list[dict]) -> list[dict]:
        """Analyze code for improvement opportunities."""
        improvements = []

        for entity in code_entities:
            for pattern_name, pattern in self.IMPROVEMENT_PATTERNS.items():
                if pattern["detect"](entity):
                    improvements.append(
                        {
                            "entity": entity.get("name"),
                            "pattern": pattern_name,
                            "suggestion": pattern["action"],
                            "priority": self._compute_priority(entity, pattern_name),
                        }
                    )

        # Sort by priority
        improvements.sort(key=lambda x: x["priority"], reverse=True)
        return improvements

    def _compute_priority(self, entity: dict, pattern: str) -> float:
        """Compute improvement priority score."""
        base_priority = 0.5

        # High complexity is critical
        if pattern == "reduce_complexity":
            complexity = entity.get("complexity", 0)
            base_priority += min(complexity / 50, 0.5)

        # Missing docs on public API
        if pattern == "add_docstrings" and not entity.get("name", "").startswith("_"):
            base_priority += 0.3

        return min(base_priority, 1.0)

    def generate_improvement_plan(self, improvements: list[dict]) -> str:
        """Generate improvement plan."""
        plan = ["# AMOS Self-Improvement Plan\n"]

        for i, imp in enumerate(improvements[:10], 1):
            plan.append(f"{i}. **{imp['entity']}**")
            plan.append(f"   - Issue: {imp['pattern']}")
            plan.append(f"   - Action: {imp['suggestion']}")
            plan.append(f"   - Priority: {imp['priority']:.1%}")
            plan.append("")

        return "\n".join(plan)


class AMOSSelfCoding:
    """Complete AMOS Self-coding System.

    Enables AMOS to:
    - Generate new code from templates
    - Modify existing code safely
    - Self-improve based on analysis
    """

    def __init__(self, output_dir: str = "generated_code"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.generator = CodeGenerator()
        self.modifier = CodeModifier()
        self.improver = SelfImprovement()

        self.generation_history: list[GeneratedCode] = []
        self.modification_history: list[dict] = []

    def create_component(
        self, component_name: str, purpose: str, zone: str = "organs"
    ) -> GeneratedCode:
        """Create new AMOS component."""
        params = {"component_name": component_name, "purpose": purpose, "zone": zone}

        generated = self.generator.generate(
            "amos_component",
            params,
            target_file=str(self.output_dir / f"{component_name.lower()}.py"),
        )

        # Validate
        generated = self.generator.validate_code(generated)

        if generated.validation_status == "valid":
            # Save to file
            with open(generated.target_file, "w") as f:
                f.write(generated.code)

        self.generation_history.append(generated)
        return generated

    def create_function(self, function_name: str, purpose: str) -> GeneratedCode:
        """Create new utility function."""
        params = {
            "function_name": function_name,
            "purpose": purpose,
            "input_type": "Any",
            "output_type": "Any",
        }

        generated = self.generator.generate(
            "amos_function", params, target_file=str(self.output_dir / "utils.py")
        )

        generated = self.generator.validate_code(generated)

        if generated.validation_status == "valid":
            mode = "a" if Path(generated.target_file).exists() else "w"
            with open(generated.target_file, mode) as f:
                f.write("\n\n" + generated.code)

        self.generation_history.append(generated)
        return generated

    def improve_codebase(self, repo_analysis: dict) -> str:
        """Generate improvement plan from repo analysis."""
        entities = [
            {"name": name, "complexity": e.complexity, "docstring": e.docstring, "zone": e.zone}
            for name, e in repo_analysis.get("entities", {}).items()
        ]

        improvements = self.improver.analyze_for_improvement(entities)
        plan = self.improver.generate_improvement_plan(improvements)

        return plan

    def get_stats(self) -> dict:
        """Get self-coding statistics."""
        return {
            "total_generations": len(self.generation_history),
            "valid_generations": sum(
                1 for g in self.generation_history if g.validation_status == "valid"
            ),
            "modifications": len(self.modification_history),
            "output_files": list(set(g.target_file for g in self.generation_history)),
        }


def demo_self_coding():
    """Demonstrate AMOS Self-coding."""
    print("=" * 70)
    print("📝 AMOS SELF-CODING SYSTEM - Section 15")
    print("=" * 70)
    print("\nAMOS can now generate and modify its own code")
    print("=" * 70)

    # Initialize self-coding
    self_coding = AMOSSelfCoding(output_dir="amos_generated")

    # 1. Generate new component
    print("\n[1] Generating New Component")
    component = self_coding.create_component(
        component_name="AnalyticsEngine",
        purpose="Analyze system performance metrics",
        zone="organs",
    )

    print(f"  Component: {component.entity_name}")
    print(f"  Status: {component.validation_status}")
    print(f"  File: {component.target_file}")

    if component.validation_status == "valid":
        print("  Preview (first 5 lines):")
        for line in component.code.split("\n")[:5]:
            print(f"    {line}")

    # 2. Generate utility function
    print("\n[2] Generating Utility Function")
    func = self_coding.create_function(
        function_name="compute_efficiency", purpose="Calculate energy efficiency ratio"
    )

    print(f"  Function: {func.entity_name}")
    print(f"  Status: {func.validation_status}")

    # 3. Show improvement plan
    print("\n[3] Self-Improvement Analysis")
    # Simulate repo analysis
    mock_analysis = {
        "entities": {
            "ComplexClass": type(
                "Mock",
                (),
                {"complexity": 35, "docstring": None, "zone": "organs", "name": "ComplexClass"},
            )()
        }
    }

    plan = self_coding.improve_codebase(mock_analysis)
    print("  Improvement opportunities detected:")
    print("  - High complexity entities need refactoring")
    print("  - Missing documentation on public APIs")

    # 4. Stats
    print("\n[4] Generation Statistics")
    stats = self_coding.get_stats()
    print(f"  Total generations: {stats['total_generations']}")
    print(f"  Valid: {stats['valid_generations']}")
    print(f"  Output files: {len(stats['output_files'])}")

    print("\n" + "=" * 70)
    print("✅ AMOS SELF-CODING OPERATIONAL")
    print("=" * 70)
    print("\nSelf-coding Capabilities:")
    print("  • Generate new components from templates")
    print("  • Create utility functions")
    print("  • Analyze code for improvement opportunities")
    print("  • Generate self-improvement plans")
    print("  • Safe code modification with backups")
    print("=" * 70)


if __name__ == "__main__":
    demo_self_coding()
