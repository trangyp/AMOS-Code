"""Code Generator — Automated Code Creation

Generates Python code from templates and specifications.
Handles module creation, class generation, and code assembly.
"""

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class CodeTemplate:
    """Template for code generation."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    template_type: str = ""  # module, class, function, stub
    content: str = ""
    placeholders: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GeneratedCode:
    """Generated code output."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    template_id: str = ""
    file_path: str = ""
    content: str = ""
    language: str = "python"
    status: str = "draft"  # draft, validated, deployed
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CodeGenerator:
    """Generates code from templates and specifications.

    Creates Python modules, classes, and functions
    based on provided specifications and templates.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        self.templates: Dict[str, CodeTemplate] = {}
        self.generated: Dict[str, GeneratedCode] = {}

        self._register_default_templates()

    def _register_default_templates(self):
        """Register default code templates."""
        # Module template
        self.templates["module"] = CodeTemplate(
            name="python_module",
            template_type="module",
            content='"""\n{{module_name}} — {{description}}\n"""\n\n{{imports}}\n\n{{content}}\n',
            placeholders=["module_name", "description", "imports", "content"],
        )

        # Class template
        self.templates["class"] = CodeTemplate(
            name="python_class",
            template_type="class",
            content='\nclass {{class_name}}:\n    """\n    {{docstring}}\n    """\n\n    def __init__(self{{init_params}}):\n        {{init_body}}\n',
            placeholders=["class_name", "docstring", "init_params", "init_body"],
        )

        # Function template
        self.templates["function"] = CodeTemplate(
            name="python_function",
            template_type="function",
            content='\ndef {{func_name}}({{params}}):\n    """{{docstring}}"""\n    {{body}}\n',
            placeholders=["func_name", "params", "docstring", "body"],
        )

        # Stub template (for alias modules)
        self.templates["stub"] = CodeTemplate(
            name="alias_stub",
            template_type="stub",
            content='"""{{description}}"""\nimport sys\nfrom pathlib import Path\n\n{{path_setup}}\n\n{{imports}}\n\n__all__ = {{exports}}\n',
            placeholders=["description", "path_setup", "imports", "exports"],
        )

    def create_template(
        self,
        name: str,
        template_type: str,
        content: str,
        placeholders: list[str] = None,
    ) -> CodeTemplate:
        """Create a new code template."""
        template = CodeTemplate(
            name=name,
            template_type=template_type,
            content=content,
            placeholders=placeholders or [],
        )
        self.templates[template.id] = template
        return template

    def generate_from_template(
        self,
        template_id: str,
        file_path: str,
        values: Dict[str, str],
    ) -> Optional[GeneratedCode]:
        """Generate code from a template with value substitution."""
        template = self.templates.get(template_id)
        if not template:
            return None

        # Simple template substitution
        content = template.content
        for placeholder, value in values.items():
            content = content.replace(f"{{{{{placeholder}}}}}", value)

        generated = GeneratedCode(
            template_id=template_id,
            file_path=file_path,
            content=content,
            status="draft",
        )
        self.generated[generated.id] = generated
        return generated

    def generate_module(
        self,
        module_name: str,
        description: str,
        imports: list[str],
        classes: list[dict[str, Any]],
        file_path: str,
    ) -> GeneratedCode:
        """Generate a complete Python module."""
        # Build imports section
        imports_str = "\n".join(f"import {imp}" for imp in imports)

        # Build content section with classes
        content_parts = []
        for cls in classes:
            class_code = self._generate_class_code(cls)
            content_parts.append(class_code)

        values = {
            "module_name": module_name,
            "description": description,
            "imports": imports_str,
            "content": "\n\n".join(content_parts),
        }

        return self.generate_from_template("module", file_path, values)

    def generate_stub_module(
        self,
        description: str,
        target_module: str,
        exports: list[str],
        file_path: str,
    ) -> GeneratedCode:
        """Generate an alias stub module."""
        path_setup = f"""# Add target module to path
target_path = Path(__file__).parent.parent / "{target_module}"
if str(target_path) not in sys.path:
    sys.path.insert(0, str(target_path))"""

        imports = "\n".join(f"from {target_module}_module import {exp}" for exp in exports[:3])

        values = {
            "description": description,
            "path_setup": path_setup,
            "imports": imports,
            "exports": str(exports),
        }

        return self.generate_from_template("stub", file_path, values)

    def _generate_class_code(self, class_spec: Dict[str, Any]) -> str:
        """Generate class code from specification."""
        class_name = class_spec.get("name", "MyClass")
        docstring = class_spec.get("docstring", f"The {class_name} class.")

        # Build init parameters
        init_params = class_spec.get("init_params", [])
        if init_params:
            params_str = ", " + ", ".join(init_params)
        else:
            params_str = ""

        # Build init body
        init_body_parts = class_spec.get("init_body", ["pass"])
        init_body = "\n        ".join(init_body_parts)

        values = {
            "class_name": class_name,
            "docstring": docstring,
            "init_params": params_str,
            "init_body": init_body,
        }

        template = self.templates.get("class")
        if not template:
            return ""

        content = template.content
        for placeholder, value in values.items():
            content = content.replace(f"{{{{{placeholder}}}}}", value)

        return content

    def validate_code(self, generated_id: str) -> bool:
        """Validate generated code is syntactically correct."""
        generated = self.generated.get(generated_id)
        if not generated:
            return False

        try:
            compile(generated.content, generated.file_path, "exec")
            generated.status = "validated"
            return True
        except SyntaxError:
            return False

    def deploy_code(
        self,
        generated_id: str,
        target_dir: Optional[Path] = None,
    ) -> bool:
        """Deploy generated code to filesystem."""
        generated = self.generated.get(generated_id)
        if not generated:
            return False

        if target_dir is None:
            target_dir = self.data_dir / "generated"

        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            file_path = target_dir / generated.file_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(generated.content)
            generated.status = "deployed"
            return True
        except Exception as e:
            print(f"[CODE_GEN] Deploy error: {e}")
            return False

    def list_templates(self) -> list[dict[str, Any]]:
        """List all available templates."""
        return [t.to_dict() for t in self.templates.values()]

    def list_generated(self) -> list[dict[str, Any]]:
        """List all generated code."""
        return [g.to_dict() for g in self.generated.values()]

    def get_status(self) -> Dict[str, Any]:
        """Get generator status."""
        return {
            "total_templates": len(self.templates),
            "total_generated": len(self.generated),
            "validated": sum(1 for g in self.generated.values() if g.status == "validated"),
            "deployed": sum(1 for g in self.generated.values() if g.status == "deployed"),
        }


_GENERATOR: Optional[CodeGenerator] = None


def get_code_generator(data_dir: Optional[Path] = None) -> CodeGenerator:
    """Get or create global code generator."""
    global _GENERATOR
    if _GENERATOR is None:
        _GENERATOR = CodeGenerator(data_dir)
    return _GENERATOR
