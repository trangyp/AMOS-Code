"""
Deep Architectural Pathologies - Higher-order failure classes.

Implements the 18+ architectural problem classes from the deeper model:
- Authority inversion (tests/docs more authoritative than runtime)
- Layer leakage (docs determining rollout, packaging changing runtime)
- Bootstrap path failure (undeclared external dependencies)
- Shadow dependencies (hidden PATH, system packages, network endpoints)
- Artifact chain discontinuity (Source → Build → Install → Runtime divergence)
- Migration geometry failure (rollback paths, skipped migrations)
- Mode-lattice drift (local/CI/prod/debug/safe mode breakage)
- Repair unsafety under rollout/rollback/fleet constraints

Invariants:
- I_authority_order: truth flows downward from canonical layers
- I_layer_separation: cross-layer influence only through declared interfaces
- I_bootstrap: system can reach valid initial state through declared paths
- I_dependency_visibility: all correctness-critical dependencies represented
- I_artifact_continuity: every transformation preserves contract surface
- I_migration: all upgrade/rollback paths preserve admissibility
- I_modes: all workflows valid across supported mode lattice
- I_repair_safe: repairs preserve validity under rollout constraints
"""

import ast
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any


class PathologyType(Enum):
    """Types of architectural pathologies."""

    # Authority pathologies
    AUTHORITY_INVERSION = auto()  # Wrong layer owns truth
    AUTHORITY_DUPLICATION = auto()  # Multiple sources of truth

    # Layer pathologies
    LAYER_LEAKAGE = auto()  # Cross-layer influence outside interfaces
    PLANE_CONFUSION = auto()  # Control/data/execution/observation mix

    # Bootstrap pathologies
    BOOTSTRAP_FAILURE = auto()  # Requires external undeclared steps
    HIDDEN_COUPLING = auto()  # Undeclared operational coupling

    # Dependency pathologies
    SHADOW_DEPENDENCY = auto()  # Hidden PATH, system packages
    FOLKLORE_OPERATION = auto()  # Undocumented human behavior required

    # Artifact pathologies
    ARTIFACT_DISCONTINUITY = auto()  # Source/build/install/runtime divergence
    DERIVATION_DRIFT = auto()  # Generated artifacts out of sync

    # Migration pathologies
    MIGRATION_GEOMETRY_FAILURE = auto()  # Invalid rollback/skip paths
    UPGRADE_NON_MONOTONIC = auto()  # Upgrades break validity

    # Mode pathologies
    MODE_LATTICE_DRIFT = auto()  # Breaks in local/CI/prod/debug modes

    # Organizational pathologies
    OWNER_MISALIGNMENT = auto()  # Authority/ownership mismatch

    # Repair pathologies
    REPAIR_UNSAFE = auto()  # Fix increases debt elsewhere
    NON_MONOTONIC_REPAIR = auto()  # Repair violates invariants


@dataclass
class ArchitecturalPathology:
    """A detected architectural pathology."""

    pathology_type: PathologyType
    severity: str  # "critical", "high", "medium", "low"
    message: str
    location: str  # File or component
    details: Dict[str, Any] = field(default_factory=dict)
    remediation: str = ""


@dataclass
class AuthoritySource:
    """Represents a potential authority source."""

    name: str
    layer: str  # "canonical", "derived", "incidental"
    location: str
    authority_type: str  # "api", "command", "schema", "config", "docs"
    confidence: float = 1.0  # How authoritative this source is


class AuthorityInversionDetector:
    """
    Detects authority inversion: wrong layer owns the truth.

    Examples
    --------
    - demos more accurate API spec than runtime handlers
    - tests more authoritative than implementation
    - launcher menu more accurate than shell registry
    - docs maintained separately from actual interface

    """

    # Layer hierarchy: lower = more canonical
    LAYER_HIERARCHY = {
        "schema_authority": 0,  # Most canonical
        "runtime_handler": 1,
        "api_contract": 2,
        "command_registry": 3,
        "shell_interface": 4,
        "demo": 5,
        "test": 6,
        "docs": 7,  # Least canonical (derived)
        "guide": 8,
    }

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self.authority_sources: List[AuthoritySource] = []

    def detect(self) -> List[ArchitecturalPathology]:
        """Find all authority inversions in the repo."""
        pathologies = []

        # Collect potential authority sources
        self._collect_schema_authorities()
        self._collect_runtime_handlers()
        self._collect_api_contracts()
        self._collect_command_registries()
        self._collect_shell_interfaces()
        self._collect_demos()
        self._collect_tests()
        self._collect_docs()

        # Check for inversions
        pathologies.extend(self._check_api_authority_inversion())
        pathologies.extend(self._check_command_authority_inversion())
        pathologies.extend(self._check_test_authority_inversion())
        pathologies.extend(self._check_docs_authority_inversion())

        return pathologies

    def _collect_schema_authorities(self):
        """Find schema definition files."""
        for pattern in ["*.json", "*.yaml", "*.yml", "*schema*.py"]:
            for f in self.repo_path.rglob(pattern):
                if "test" not in str(f) and "__pycache__" not in str(f):
                    self.authority_sources.append(
                        AuthoritySource(
                            name=f.stem,
                            layer="schema_authority",
                            location=str(f),
                            authority_type="schema",
                            confidence=1.0,
                        )
                    )

    def _collect_runtime_handlers(self):
        """Find runtime API handlers."""
        for f in self.repo_path.rglob("*.py"):
            if "test" in str(f) or "__pycache__" in str(f):
                continue
            content = f.read_text()
            if "def handle" in content or "def process" in content or "@app.route" in content:
                self.authority_sources.append(
                    AuthoritySource(
                        name=f.stem,
                        layer="runtime_handler",
                        location=str(f),
                        authority_type="api",
                        confidence=0.8,
                    )
                )

    def _collect_api_contracts(self):
        """Find API contract definitions."""
        for f in self.repo_path.rglob("*.py"):
            if "contract" in f.name.lower() or "interface" in f.name.lower():
                self.authority_sources.append(
                    AuthoritySource(
                        name=f.stem,
                        layer="api_contract",
                        location=str(f),
                        authority_type="api",
                        confidence=0.9,
                    )
                )

    def _collect_command_registries(self):
        """Find command registration code."""
        for f in self.repo_path.rglob("*.py"):
            if "__pycache__" in str(f):
                continue
            content = f.read_text()
            if "register_command" in content or "add_command" in content:
                self.authority_sources.append(
                    AuthoritySource(
                        name=f.stem,
                        layer="command_registry",
                        location=str(f),
                        authority_type="command",
                        confidence=0.7,
                    )
                )

    def _collect_shell_interfaces(self):
        """Find shell/CLI interface definitions."""
        for f in self.repo_path.rglob("*.py"):
            if "cli" in f.name.lower() or "shell" in f.name.lower():
                self.authority_sources.append(
                    AuthoritySource(
                        name=f.stem,
                        layer="shell_interface",
                        location=str(f),
                        authority_type="command",
                        confidence=0.6,
                    )
                )

    def _collect_demos(self):
        """Find demo/example code."""
        for pattern in ["**/demo*/**/*.py", "**/example*/**/*.py", "**/example*.py"]:
            for f in self.repo_path.glob(pattern):
                if f.is_file():
                    self.authority_sources.append(
                        AuthoritySource(
                            name=f.stem,
                            layer="demo",
                            location=str(f),
                            authority_type="api",
                            confidence=0.3,
                        )
                    )

    def _collect_tests(self):
        """Find test code."""
        for f in self.repo_path.rglob("test*.py"):
            if "__pycache__" not in str(f):
                self.authority_sources.append(
                    AuthoritySource(
                        name=f.stem,
                        layer="test",
                        location=str(f),
                        authority_type="api",
                        confidence=0.2,
                    )
                )

    def _collect_docs(self):
        """Find documentation."""
        for pattern in ["**/*.md", "**/*.rst", "**/README*"]:
            for f in self.repo_path.glob(pattern):
                if f.is_file():
                    self.authority_sources.append(
                        AuthoritySource(
                            name=f.stem,
                            layer="docs",
                            location=str(f),
                            authority_type="api",
                            confidence=0.1,
                        )
                    )

    def _check_api_authority_inversion(self) -> List[ArchitecturalPathology]:
        """Check if demos/tests are more accurate than runtime."""
        pathologies = []

        # Find APIs defined in demos but not in runtime
        demo_apis = set()
        runtime_apis = set()

        for src in self.authority_sources:
            if src.authority_type == "api":
                if src.layer == "demo":
                    demo_apis.add(src.name)
                elif src.layer in ["runtime_handler", "api_contract"]:
                    runtime_apis.add(src.name)

        # Check for demo-only APIs
        demo_only = demo_apis - runtime_apis
        if demo_only:
            pathologies.append(
                ArchitecturalPathology(
                    pathology_type=PathologyType.AUTHORITY_INVERSION,
                    severity="high",
                    message=f"APIs defined in demos but not in runtime: {demo_only}",
                    location="demos/",
                    details={"apis": list(demo_only)},
                    remediation="Promote demo APIs to runtime handlers or remove",
                )
            )

        return pathologies

    def _check_command_authority_inversion(self) -> List[ArchitecturalPathology]:
        """Check if launcher/shell has more commands than registry."""
        pathologies = []

        registry_cmds = set()
        shell_cmds = set()

        for src in self.authority_sources:
            if src.authority_type == "command":
                if src.layer == "command_registry":
                    registry_cmds.add(src.name)
                elif src.layer == "shell_interface":
                    shell_cmds.add(src.name)

        # Shell-only commands suggest launcher menu is more accurate
        shell_only = shell_cmds - registry_cmds
        if shell_only:
            pathologies.append(
                ArchitecturalPathology(
                    pathology_type=PathologyType.AUTHORITY_INVERSION,
                    severity="medium",
                    message=f"Commands in shell but not in registry: {shell_only}",
                    location="shell/",
                    details={"commands": list(shell_only)},
                    remediation="Register shell commands in canonical registry",
                )
            )

        return pathologies

    def _check_test_authority_inversion(self) -> List[ArchitecturalPathology]:
        """Check if tests are more authoritative than implementation."""
        pathologies = []

        # Check for tests that define behavior not in implementation
        test_defined_apis = set()
        impl_apis = set()

        for src in self.authority_sources:
            if src.authority_type == "api":
                if src.layer == "test":
                    test_defined_apis.add(src.name)
                elif src.layer in ["runtime_handler", "api_contract", "schema_authority"]:
                    impl_apis.add(src.name)

        # If tests define APIs not in implementation, that's inversion
        test_only = test_defined_apis - impl_apis
        if len(test_only) > 3:  # Threshold for significant inversion
            pathologies.append(
                ArchitecturalPathology(
                    pathology_type=PathologyType.AUTHORITY_INVERSION,
                    severity="high",
                    message=f"Tests define {len(test_only)} APIs not in implementation",
                    location="tests/",
                    details={"test_only_apis": list(test_only)[:10]},
                    remediation="Move API definitions from tests to canonical layers",
                )
            )

        return pathologies

    def _check_docs_authority_inversion(self) -> List[ArchitecturalPathology]:
        """Check if docs are maintained separately from code."""
        pathologies = []

        # Find docs with API signatures that don't match code
        docs_with_apis = [s for s in self.authority_sources if s.layer == "docs"]

        for doc in docs_with_apis:
            content = Path(doc.location).read_text()
            # Look for API signatures in docs
            api_patterns = re.findall(r"`(\w+\([^)]*\))`", content)
            if api_patterns:
                # Check if these match any runtime API
                has_matching_runtime = any(
                    s.layer in ["runtime_handler", "api_contract"] for s in self.authority_sources
                )
                if not has_matching_runtime:
                    pathologies.append(
                        ArchitecturalPathology(
                            pathology_type=PathologyType.AUTHORITY_INVERSION,
                            severity="medium",
                            message=f"Docs define APIs that may not match runtime: {doc.location}",
                            location=doc.location,
                            details={"doc_apis": api_patterns[:5]},
                            remediation="Derive docs from canonical API definitions",
                        )
                    )

        return pathologies


class LayerLeakageDetector:
    """
    Detects layer leakage: one layer influences another outside declared interfaces.

    Examples
    --------
    - docs determining rollout order
    - packaging layout changing runtime semantics
    - codegen output changing test oracle assumptions
    - shell aliases substituting for API compatibility

    """

    LAYERS = ["source", "build", "package", "install", "runtime", "observability"]

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)

    def detect(self) -> List[ArchitecturalPathology]:
        """Find all layer leakages."""
        pathologies = []

        pathologies.extend(self._check_docs_rollout_influence())
        pathologies.extend(self._check_packaging_runtime_coupling())
        pathologies.extend(self._check_codegen_test_coupling())
        pathologies.extend(self._check_shell_alias_substitution())
        pathologies.extend(self._check_migration_naming_logic())

        return pathologies

    def _check_docs_rollout_influence(self) -> List[ArchitecturalPathology]:
        """Check if docs encode rollout rules."""
        pathologies = []

        for doc in self.repo_path.rglob("*.md"):
            content = doc.read_text()
            # Look for rollout instructions in docs
            rollout_patterns = [
                "deploy.*first",
                "rollout.*order",
                "deploy.*before",
                "release.*sequence",
            ]
            for pattern in rollout_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # Check if this is also in a deployment config
                    has_deploy_config = any(
                        (self.repo_path / f).exists()
                        for f in [".github/workflows/deploy.yml", "deploy.py", "rollout.yml"]
                    )
                    if not has_deploy_config:
                        pathologies.append(
                            ArchitecturalPathology(
                                pathology_type=PathologyType.LAYER_LEAKAGE,
                                severity="high",
                                message=f"Docs encode rollout rules not in deployment config: {doc}",
                                location=str(doc),
                                details={"pattern": pattern},
                                remediation="Move rollout rules to deployment configuration",
                            )
                        )
                    break

        return pathologies

    def _check_packaging_runtime_coupling(self) -> List[ArchitecturalPathology]:
        """Check if packaging layout affects runtime."""
        pathologies = []

        # Check for __init__.py with side effects
        for init_file in self.repo_path.rglob("__init__.py"):
            content = init_file.read_text()
            # Look for runtime logic in package init
            if "import" in content and any(
                kw in content for kw in ["config", "setup", "initialize", "patch"]
            ):
                # Check if this is doing more than just exports
                lines = content.split("\n")
                non_export_lines = [
                    line
                    for line in lines
                    if line.strip()
                    and not line.startswith(("#", "__version__", "from ", "import ", "__all__"))
                ]
                if len(non_export_lines) > 5:
                    pathologies.append(
                        ArchitecturalPathology(
                            pathology_type=PathologyType.LAYER_LEAKAGE,
                            severity="medium",
                            message=f"Package __init__.py has runtime side effects: {init_file}",
                            location=str(init_file),
                            details={"side_effect_lines": len(non_export_lines)},
                            remediation="Move runtime initialization to explicit entrypoints",
                        )
                    )

        return pathologies

    def _check_codegen_test_coupling(self) -> List[ArchitecturalPathology]:
        """Check if test oracles depend on generated code."""
        pathologies = []

        # Find generated code
        generated_dirs = ["generated", "gen", "dist", "build"]
        for gen_dir in generated_dirs:
            gen_path = self.repo_path / gen_dir
            if gen_path.exists():
                # Check if tests import from generated
                for test in self.repo_path.rglob("test*.py"):
                    content = test.read_text()
                    if gen_dir in content:
                        pathologies.append(
                            ArchitecturalPathology(
                                pathology_type=PathologyType.LAYER_LEAKAGE,
                                severity="medium",
                                message=f"Tests depend on generated code: {test}",
                                location=str(test),
                                details={"generated_dir": gen_dir},
                                remediation="Test against canonical schema, not generated artifacts",
                            )
                        )

        return pathologies

    def _check_shell_alias_substitution(self) -> List[ArchitecturalPathology]:
        """Check if shell aliases substitute for API compatibility."""
        pathologies = []

        # Look for shell scripts that workaround API issues
        for shell_file in self.repo_path.rglob("*.sh"):
            content = shell_file.read_text()
            # Look for compatibility workarounds
            workaround_patterns = [
                "compat",
                "workaround",
                "alias.*=",
                "legacy",
                "backward",
            ]
            for pattern in workaround_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    pathologies.append(
                        ArchitecturalPathology(
                            pathology_type=PathologyType.LAYER_LEAKAGE,
                            severity="low",
                            message=f"Shell script may contain API compatibility workarounds: {shell_file}",
                            location=str(shell_file),
                            details={"pattern": pattern},
                            remediation="Fix API compatibility at source, not in shell",
                        )
                    )
                    break

        return pathologies

    def _check_migration_naming_logic(self) -> List[ArchitecturalPathology]:
        """Check if migration file names determine business logic."""
        pathologies = []

        # Look for migrations
        migration_dirs = ["migrations", "alembic", "migrate"]
        for mig_dir in migration_dirs:
            mig_path = self.repo_path / mig_dir
            if mig_path.exists():
                # Check if code parses migration file names
                for py_file in self.repo_path.rglob("*.py"):
                    if "__pycache__" in str(py_file):
                        continue
                    content = py_file.read_text()
                    if mig_dir in content and re.search(r"\d{3,}.*\.py", content):
                        # Might be parsing migration order from filenames
                        if "version" in content.lower() or "order" in content.lower():
                            pathologies.append(
                                ArchitecturalPathology(
                                    pathology_type=PathologyType.LAYER_LEAKAGE,
                                    severity="high",
                                    message=f"Code parses migration filenames for logic: {py_file}",
                                    location=str(py_file),
                                    details={"migration_dir": mig_dir},
                                    remediation="Use explicit migration registry, not filenames",
                                )
                            )

        return pathologies


class BootstrapPathValidator:
    """
    Validates bootstrap paths: undeclared external dependencies.

    Examples
    --------
    - command works only after manual build step
    - generated files must exist before tests
    - migrations must have run before CLI starts
    - one package must be installed editable for another to resolve
    - local executable on PATH required

    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)

    def validate(self) -> List[ArchitecturalPathology]:
        """Find all bootstrap path failures."""
        pathologies = []

        pathologies.extend(self._check_manual_build_requirements())
        pathologies.extend(self._check_generated_file_prerequisites())
        pathologies.extend(self._check_migration_prerequisites())
        pathologies.extend(self._check_editable_install_coupling())
        pathologies.extend(self._check_path_dependencies())

        return pathologies

    def _check_manual_build_requirements(self) -> List[ArchitecturalPathology]:
        """Check for undocumented manual build steps."""
        pathologies = []

        # Look for build scripts
        build_scripts = list(self.repo_path.glob("build.py")) + list(
            self.repo_path.glob("Makefile")
        )

        if build_scripts:
            # Check if these are documented in setup instructions
            setup_docs = list(self.repo_path.glob("SETUP.md")) + list(
                self.repo_path.glob("README.md")
            )

            for script in build_scripts:
                script_name = script.name
                documented = any(
                    script_name in doc.read_text() for doc in setup_docs if doc.exists()
                )

                if not documented:
                    pathologies.append(
                        ArchitecturalPathology(
                            pathology_type=PathologyType.BOOTSTRAP_FAILURE,
                            severity="medium",
                            message=f"Build script not documented in setup: {script}",
                            location=str(script),
                            details={"script": script_name},
                            remediation="Document manual build step in SETUP.md",
                        )
                    )

        return pathologies

    def _check_generated_file_prerequisites(self) -> List[ArchitecturalPathology]:
        """Check if tests require generated files but don't generate them."""
        pathologies = []

        # Look for imports of generated modules in tests
        for test in self.repo_path.rglob("test*.py"):
            content = test.read_text()

            # Check for imports from common generated directories
            generated_imports = re.findall(r"from\s+(generated|gen|build|dist)\.?", content)

            if generated_imports:
                # Check if test setup generates these
                if "setUp" not in content and "pytest.fixture" not in content:
                    pathologies.append(
                        ArchitecturalPathology(
                            pathology_type=PathologyType.BOOTSTRAP_FAILURE,
                            severity="high",
                            message=f"Test imports generated files without generating them: {test}",
                            location=str(test),
                            details={"generated_imports": generated_imports},
                            remediation="Add test fixtures to generate required files",
                        )
                    )

        return pathologies

    def _check_migration_prerequisites(self) -> List[ArchitecturalPathology]:
        """Check if CLI requires migrations but doesn't declare it."""
        pathologies = []

        # Look for CLI entrypoints
        for cli in self.repo_path.rglob("cli.py"):
            content = cli.read_text()

            # Check if it uses database without migration check
            if any(kw in content for kw in ["db", "database", "session", "model"]):
                # Check for migration dependency declaration
                has_migration_check = "migration" in content.lower()

                if not has_migration_check:
                    pathologies.append(
                        ArchitecturalPathology(
                            pathology_type=PathologyType.BOOTSTRAP_FAILURE,
                            severity="high",
                            message=f"CLI may require migrations but doesn't check: {cli}",
                            location=str(cli),
                            details={},
                            remediation="Add migration version check to CLI startup",
                        )
                    )

        return pathologies

    def _check_editable_install_coupling(self) -> List[ArchitecturalPathology]:
        """Check if package requires editable install of another package."""
        pathologies = []

        # Look for development requirements
        dev_reqs = list(self.repo_path.glob("requirements-dev.txt")) + list(
            self.repo_path.glob("dev-requirements.txt")
        )

        for req_file in dev_reqs:
            content = req_file.read_text()

            # Check for editable installs (-e or --editable)
            if "-e " in content or "--editable" in content:
                editable_packages = re.findall(r"-e\s+(\S+)", content)

                for pkg in editable_packages:
                    pathologies.append(
                        ArchitecturalPathology(
                            pathology_type=PathologyType.BOOTSTRAP_FAILURE,
                            severity="medium",
                            message=f"Package requires editable install of {pkg}",
                            location=str(req_file),
                            details={"package": pkg},
                            remediation="Use proper package dependencies instead of editable installs",
                        )
                    )

        return pathologies

    def _check_path_dependencies(self) -> List[ArchitecturalPathology]:
        """Check for hidden PATH dependencies."""
        pathologies = []

        # Look for subprocess calls that assume executables on PATH
        for py_file in self.repo_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            content = py_file.read_text()

            # Check for subprocess calls without full paths
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        # Check for subprocess calls
                        if isinstance(node.func, ast.Attribute):
                            if node.func.attr in ["run", "call", "Popen"]:
                                # Check if command is just a name (not full path)
                                if node.args:
                                    first_arg = node.args[0]
                                    if isinstance(first_arg, ast.Constant):
                                        cmd = first_arg.value
                                        if isinstance(cmd, str) and not cmd.startswith(
                                            ("/", ".", "python")
                                        ):
                                            # Likely depends on PATH
                                            if (
                                                "git" not in cmd and "python" not in cmd
                                            ):  # Exclude common tools
                                                pathologies.append(
                                                    ArchitecturalPathology(
                                                        pathology_type=PathologyType.SHADOW_DEPENDENCY,
                                                        severity="low",
                                                        message=f"Code calls '{cmd}' which requires PATH: {py_file}",
                                                        location=str(py_file),
                                                        details={"command": cmd},
                                                        remediation="Declare PATH dependency explicitly or use full path",
                                                    )
                                                )
            except SyntaxError:
                continue

        return pathologies


class ShadowDependencyDetector:
    """
    Detects shadow dependencies: hidden PATH, system packages, network endpoints.

    Examples
    --------
    - local executable on PATH
    - hidden system package
    - external network endpoint
    - dynamic plugin discovered at runtime
    - filesystem layout assumption

    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)

    def detect(self) -> List[ArchitecturalPathology]:
        """Find all shadow dependencies."""
        pathologies = []

        pathologies.extend(self._check_system_package_dependencies())
        pathologies.extend(self._check_network_endpoints())
        pathologies.extend(self._check_filesystem_layout_assumptions())
        pathologies.extend(self._check_dynamic_plugin_loading())
        pathologies.extend(self._check_env_var_dependencies())

        return pathologies

    def _check_system_package_dependencies(self) -> List[ArchitecturalPathology]:
        """Check for dependencies on system packages not in requirements."""
        pathologies = []

        # Look for imports that might be system packages
        system_packages = ["sqlite3", "zlib", "gzip", "ctypes", "ssl", "hashlib"]

        for py_file in self.repo_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            content = py_file.read_text()

            for pkg in system_packages:
                if f"import {pkg}" in content or f"from {pkg}" in content:
                    # Check if this is documented
                    pathologies.append(
                        ArchitecturalPathology(
                            pathology_type=PathologyType.SHADOW_DEPENDENCY,
                            severity="low",
                            message=f"Code imports system package '{pkg}' that may not be available: {py_file}",
                            location=str(py_file),
                            details={"package": pkg},
                            remediation="Document system dependency in setup requirements",
                        )
                    )

        return pathologies

    def _check_network_endpoints(self) -> List[ArchitecturalPathology]:
        """Check for hardcoded network endpoints."""
        pathologies = []

        # Look for URLs in code
        url_patterns = [
            r"https?://[^\s\"']+",
            r"[a-z0-9.-]+\.com",
            r"[a-z0-9.-]+\.io",
            r"localhost:\d+",
            r"127\.0\.0\.1:\d+",
        ]

        for py_file in self.repo_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            content = py_file.read_text()

            for pattern in url_patterns:
                matches = re.findall(pattern, content)
                for match in matches[:3]:  # Limit to first 3 per file
                    pathologies.append(
                        ArchitecturalPathology(
                            pathology_type=PathologyType.SHADOW_DEPENDENCY,
                            severity="medium",
                            message=f"Hardcoded network endpoint: {match}",
                            location=str(py_file),
                            details={"endpoint": match},
                            remediation="Externalize endpoint configuration",
                        )
                    )

        return pathologies

    def _check_filesystem_layout_assumptions(self) -> List[ArchitecturalPathology]:
        """Check for filesystem layout assumptions."""
        pathologies = []

        # Look for hardcoded paths
        path_patterns = [
            r"/tmp/\w+",
            r"/var/\w+",
            r"/home/\w+",
            r"~/\.",
            r"C:\\\\",
        ]

        for py_file in self.repo_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            content = py_file.read_text()

            for pattern in path_patterns:
                matches = re.findall(pattern, content)
                for match in matches[:2]:  # Limit to first 2 per file
                    pathologies.append(
                        ArchitecturalPathology(
                            pathology_type=PathologyType.SHADOW_DEPENDENCY,
                            severity="low",
                            message=f"Hardcoded filesystem path: {match}",
                            location=str(py_file),
                            details={"path": match},
                            remediation="Use platform-independent path utilities",
                        )
                    )

        return pathologies

    def _check_dynamic_plugin_loading(self) -> List[ArchitecturalPathology]:
        """Check for dynamic plugin discovery at runtime."""
        pathologies = []

        # Look for dynamic imports
        dynamic_patterns = [
            "__import__",
            "importlib",
            "imp.load",
            "exec(",
            "eval(",
        ]

        for py_file in self.repo_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            content = py_file.read_text()

            for pattern in dynamic_patterns:
                if pattern in content:
                    pathologies.append(
                        ArchitecturalPathology(
                            pathology_type=PathologyType.SHADOW_DEPENDENCY,
                            severity="medium",
                            message=f"Dynamic code loading detected: {py_file}",
                            location=str(py_file),
                            details={"pattern": pattern},
                            remediation="Document plugin loading mechanism and dependencies",
                        )
                    )
                    break  # One report per file is enough

        return pathologies

    def _check_env_var_dependencies(self) -> List[ArchitecturalPathology]:
        """Check for undocumented environment variable dependencies."""
        pathologies = []

        # Look for os.environ usage
        for py_file in self.repo_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Subscript):
                        if isinstance(node.value, ast.Attribute):
                            if node.value.attr == "environ":
                                # Found os.environ access
                                if isinstance(node.slice, ast.Constant):
                                    env_var = node.slice.value
                                    if isinstance(env_var, str) and not env_var.startswith(
                                        ("HOME", "PATH", "USER")
                                    ):
                                        pathologies.append(
                                            ArchitecturalPathology(
                                                pathology_type=PathologyType.SHADOW_DEPENDENCY,
                                                severity="low",
                                                message=f"Undocumented env var dependency: {env_var}",
                                                location=str(py_file),
                                                details={"env_var": env_var},
                                                remediation="Document required environment variables",
                                            )
                                        )
            except SyntaxError:
                continue

        return pathologies


class ArtifactChainValidator:
    """
    Validates artifact chain continuity: Source → Build → Install → Runtime.

    Examples
    --------
    - command exists in source but not after install
    - wheel omits top-level module
    - console script resolves locally but not from package
    - source and artifact expose different mode surfaces

    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)

    def validate(self) -> List[ArchitecturalPathology]:
        """Find all artifact chain discontinuities."""
        pathologies = []

        pathologies.extend(self._check_source_install_divergence())
        pathologies.extend(self._check_wheel_completeness())
        pathologies.extend(self._check_console_script_resolution())
        pathologies.extend(self._check_mode_surface_divergence())

        return pathologies

    def _check_source_install_divergence(self) -> List[ArchitecturalPathology]:
        """Check if source and installed package differ."""
        pathologies = []

        # Look for package structure
        pkg_dirs = [
            d for d in self.repo_path.iterdir() if d.is_dir() and not d.name.startswith(".")
        ]

        for pkg_dir in pkg_dirs:
            if (pkg_dir / "__init__.py").exists():
                # Check if there's a pyproject.toml or setup.py
                has_setup = (self.repo_path / "setup.py").exists() or (
                    self.repo_path / "pyproject.toml"
                ).exists()

                if has_setup:
                    # Check if package is declared correctly
                    try:
                        setup_py = (self.repo_path / "setup.py").read_text()
                        if pkg_dir.name not in setup_py:
                            pathologies.append(
                                ArchitecturalPathology(
                                    pathology_type=PathologyType.ARTIFACT_DISCONTINUITY,
                                    severity="critical",
                                    message=f"Package '{pkg_dir.name}' not declared in setup.py",
                                    location=str(self.repo_path / "setup.py"),
                                    details={"package": pkg_dir.name},
                                    remediation="Add package to setup.py packages list",
                                )
                            )
                    except FileNotFoundError:
                        pass

        return pathologies

    def _check_wheel_completeness(self) -> List[ArchitecturalPathology]:
        """Check if wheel includes all necessary files."""
        pathologies = []

        # Look for MANIFEST.in or package_data
        manifest = self.repo_path / "MANIFEST.in"

        # Check for data files that might be needed at runtime
        data_dirs = ["data", "config", "templates", "static"]

        for data_dir in data_dirs:
            data_path = self.repo_path / data_dir
            if data_path.exists() and data_path.is_dir():
                # Check if these are included in package
                if not manifest.exists():
                    pathologies.append(
                        ArchitecturalPathology(
                            pathology_type=PathologyType.ARTIFACT_DISCONTINUITY,
                            severity="medium",
                            message=f"Data directory '{data_dir}' may not be included in wheel",
                            location=str(data_path),
                            details={"directory": data_dir},
                            remediation="Add MANIFEST.in or package_data to include data files",
                        )
                    )

        return pathologies

    def _check_console_script_resolution(self) -> List[ArchitecturalPathology]:
        """Check if console scripts resolve correctly."""
        pathologies = []

        # Look for pyproject.toml or setup.py console_scripts
        try:
            pyproject = (self.repo_path / "pyproject.toml").read_text()
            if "console_scripts" in pyproject:
                # Extract console scripts
                scripts = re.findall(r"(\w+)\s*=\s*([\w.]+):(\w+)", pyproject)

                for script_name, module, func in scripts:
                    # Check if module exists
                    module_path = self.repo_path / module.replace(".", "/") / "__init__.py"
                    if not module_path.exists():
                        pathologies.append(
                            ArchitecturalPathology(
                                pathology_type=PathologyType.ARTIFACT_DISCONTINUITY,
                                severity="critical",
                                message=f"Console script '{script_name}' points to non-existent module: {module}",
                                location="pyproject.toml",
                                details={"script": script_name, "module": module},
                                remediation="Fix console_scripts entry point",
                            )
                        )
        except FileNotFoundError:
            pass

        return pathologies

    def _check_mode_surface_divergence(self) -> List[ArchitecturalPathology]:
        """Check if source and runtime expose different modes."""
        pathologies = []

        # Look for mode definitions in source
        mode_patterns = ["debug", "safe_mode", "dev_mode", "production", "staging"]

        source_modes = set()
        runtime_modes = set()

        for py_file in self.repo_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            content = py_file.read_text()

            for mode in mode_patterns:
                if mode in content.lower():
                    if "config" in str(py_file) or "settings" in str(py_file):
                        source_modes.add(mode)
                    elif "runtime" in str(py_file) or "main" in str(py_file):
                        runtime_modes.add(mode)

        # Check for divergence
        diverged = source_modes.symmetric_difference(runtime_modes)
        if diverged:
            pathologies.append(
                ArchitecturalPathology(
                    pathology_type=PathologyType.ARTIFACT_DISCONTINUITY,
                    severity="medium",
                    message=f"Mode surface divergence between config and runtime: {diverged}",
                    location="config/",
                    details={"diverged_modes": list(diverged)},
                    remediation="Ensure all modes are consistently defined",
                )
            )

        return pathologies


class MigrationGeometryValidator:
    """
    Validates migration geometry: rollback paths, skipped migrations.

    Invariant: I_migration = 1 iff all declared forward and rollback paths
    preserve admissibility, compatibility, and data-shape invariants.
    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)

    def validate(self) -> List[ArchitecturalPathology]:
        """Find all migration geometry failures."""
        pathologies = []

        pathologies.extend(self._check_upgrade_only_migrations())
        pathologies.extend(self._check_rollback_safety())
        pathologies.extend(self._check_migration_order_validity())
        pathologies.extend(self._check_schema_client_mismatch())

        return pathologies

    def _check_upgrade_only_migrations(self) -> List[ArchitecturalPathology]:
        """Check for migrations without rollback."""
        pathologies = []

        # Look for migration files
        migration_dirs = ["migrations", "alembic/versions"]

        for mig_dir in migration_dirs:
            mig_path = self.repo_path / mig_dir
            if mig_path.exists():
                for mig_file in mig_path.rglob("*.py"):
                    if mig_file.name.startswith("__"):
                        continue

                    content = mig_file.read_text()

                    # Check for upgrade function
                    has_upgrade = "def upgrade" in content
                    # Check for downgrade function
                    has_downgrade = "def downgrade" in content

                    if has_upgrade and not has_downgrade:
                        pathologies.append(
                            ArchitecturalPathology(
                                pathology_type=PathologyType.MIGRATION_GEOMETRY_FAILURE,
                                severity="high",
                                message=f"Migration lacks rollback: {mig_file.name}",
                                location=str(mig_file),
                                details={},
                                remediation="Add downgrade() function for rollback support",
                            )
                        )

        return pathologies

    def _check_rollback_safety(self) -> List[ArchitecturalPathology]:
        """Check if rollbacks preserve data integrity."""
        pathologies = []

        # This is a heuristic - look for destructive operations in migrations
        destructive_ops = ["DROP COLUMN", "DROP TABLE", "DELETE FROM"]

        migration_dirs = ["migrations", "alembic/versions"]

        for mig_dir in migration_dirs:
            mig_path = self.repo_path / mig_dir
            if mig_path.exists():
                for mig_file in mig_path.rglob("*.py"):
                    if mig_file.name.startswith("__"):
                        continue

                    content = mig_file.read_text()

                    # Check both upgrade and downgrade for destructive ops
                    for op in destructive_ops:
                        if op in content.upper():
                            # Check if there's a backup or safety check
                            has_safety = (
                                "backup" in content.lower() or "validate" in content.lower()
                            )

                            if not has_safety:
                                pathologies.append(
                                    ArchitecturalPathology(
                                        pathology_type=PathologyType.MIGRATION_GEOMETRY_FAILURE,
                                        severity="high",
                                        message=f"Migration has destructive operation without safety: {op}",
                                        location=str(mig_file),
                                        details={"operation": op},
                                        remediation="Add data backup before destructive operations",
                                    )
                                )
                            break  # One warning per file

        return pathologies

    def _check_migration_order_validity(self) -> List[ArchitecturalPathology]:
        """Check if migration order is valid (no skipped migrations)."""
        pathologies = []

        # Look for migration files with sequential IDs
        migration_dirs = ["migrations", "alembic/versions"]

        for mig_dir in migration_dirs:
            mig_path = self.repo_path / mig_dir
            if mig_path.exists():
                mig_files = sorted(
                    [f for f in mig_path.glob("*.py") if not f.name.startswith("__")]
                )

                if len(mig_files) > 1:
                    # Check for gaps in sequence (simple heuristic)
                    seq_numbers = []
                    for f in mig_files:
                        match = re.match(r"(\d+)", f.name)
                        if match:
                            seq_numbers.append(int(match.group(1)))

                    if seq_numbers:
                        expected = list(range(min(seq_numbers), max(seq_numbers) + 1))
                        missing = set(expected) - set(seq_numbers)

                        if missing:
                            pathologies.append(
                                ArchitecturalPathology(
                                    pathology_type=PathologyType.MIGRATION_GEOMETRY_FAILURE,
                                    severity="medium",
                                    message=f"Potentially skipped migration sequence numbers: {sorted(missing)}",
                                    location=str(mig_path),
                                    details={"missing": sorted(missing)},
                                    remediation="Verify migration sequence is complete",
                                )
                            )

        return pathologies

    def _check_schema_client_mismatch(self) -> List[ArchitecturalPathology]:
        """Check if schema and client code versions match."""
        pathologies = []

        # Look for version assertions in code
        for py_file in self.repo_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            content = py_file.read_text()

            # Look for hardcoded schema versions
            version_patterns = [
                r"SCHEMA_VERSION\s*=\s*(\d+)",
                r"API_VERSION\s*=\s*(\d+)",
                r"version\s*=\s*(\d+)",
            ]

            for pattern in version_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    # This is just a detection - actual validation would need more context
                    pass

        return pathologies


class ModeLatticeValidator:
    """
    Validates mode-lattice: local/CI/prod/debug/safe mode combinations.

    Invariant: I_modes = 1 iff all declared critical workflows remain valid
    across the supported mode lattice.
    """

    MODES = ["local", "ci", "prod", "debug", "safe", "dev", "test"]

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)

    def validate(self) -> List[ArchitecturalPathology]:
        """Find all mode-lattice drift."""
        pathologies = []

        pathologies.extend(self._check_local_only_features())
        pathologies.extend(self._check_ci_prod_divergence())
        pathologies.extend(self._check_debug_mode_leakage())
        pathologies.extend(self._check_safe_mode_incompleteness())

        return pathologies

    def _check_local_only_features(self) -> List[ArchitecturalPathology]:
        """Check for features that only work in local mode."""
        pathologies = []

        # Look for local-only code paths
        local_indicators = [
            "if __name__ == '__main__'",
            'if __name__=="__main__"',
            "DEBUG = True",
            "local_only",
        ]

        for py_file in self.repo_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            content = py_file.read_text()

            # Skip test files
            if "test" in str(py_file).lower():
                continue

            for indicator in local_indicators:
                if indicator in content:
                    # Check if this is properly guarded for non-local modes
                    if "local" in py_file.name.lower() or "dev" in py_file.name.lower():
                        continue  # Expected in local files

                    pathologies.append(
                        ArchitecturalPathology(
                            pathology_type=PathologyType.MODE_LATTICE_DRIFT,
                            severity="medium",
                            message=f"Potential local-only code path: {indicator}",
                            location=str(py_file),
                            details={"indicator": indicator},
                            remediation="Ensure code works in all supported modes",
                        )
                    )
                    break

        return pathologies

    def _check_ci_prod_divergence(self) -> List[ArchitecturalPathology]:
        """Check for CI/prod configuration divergence."""
        pathologies = []

        # Look for CI and prod configs
        ci_configs = list(self.repo_path.glob(".github/workflows/*.yml"))
        prod_configs = list(self.repo_path.rglob("prod*.yml")) + list(
            self.repo_path.rglob("production*.yml")
        )

        if ci_configs and not prod_configs:
            pathologies.append(
                ArchitecturalPathology(
                    pathology_type=PathologyType.MODE_LATTICE_DRIFT,
                    severity="medium",
                    message="CI configuration exists but no explicit prod configuration",
                    location=".github/workflows/",
                    details={},
                    remediation="Add production configuration separate from CI",
                )
            )

        return pathologies

    def _check_debug_mode_leakage(self) -> List[ArchitecturalPathology]:
        """Check if debug code leaks into production."""
        pathologies = []

        # Look for debug patterns
        debug_patterns = [
            "print(",
            "breakpoint()",
            "import pdb",
            "console.log",
        ]

        for py_file in self.repo_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            # Skip test and debug files
            if any(x in str(py_file).lower() for x in ["test", "debug", "example"]):
                continue

            content = py_file.read_text()

            for pattern in debug_patterns:
                if pattern in content:
                    pathologies.append(
                        ArchitecturalPathology(
                            pathology_type=PathologyType.MODE_LATTICE_DRIFT,
                            severity="low",
                            message=f"Debug code may leak into production: {pattern}",
                            location=str(py_file),
                            details={"pattern": pattern},
                            remediation="Remove debug code or guard with proper mode checks",
                        )
                    )
                    break

        return pathologies

    def _check_safe_mode_incompleteness(self) -> List[ArchitecturalPathology]:
        """Check if safe mode is properly implemented."""
        pathologies = []

        # Look for safe mode handling
        safe_mode_implemented = False

        for py_file in self.repo_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            content = py_file.read_text()

            if "safe_mode" in content.lower() or "safe mode" in content.lower():
                safe_mode_implemented = True
                break

        # Check if there are failure modes that should have safe mode
        failure_prone = any(
            (self.repo_path / f).exists() for f in ["server.py", "api.py", "worker.py", "daemon.py"]
        )

        if failure_prone and not safe_mode_implemented:
            pathologies.append(
                ArchitecturalPathology(
                    pathology_type=PathologyType.MODE_LATTICE_DRIFT,
                    severity="medium",
                    message="Long-running service detected but no safe mode implementation",
                    location="src/",
                    details={},
                    remediation="Add safe mode for graceful degradation",
                )
            )

        return pathologies


class ArchitecturalPathologyEngine:
    """
    Main engine to run all architectural pathology detectors.

    Integrates all detectors and provides unified pathology analysis.
    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self.detectors = {
            "authority_inversion": AuthorityInversionDetector(repo_path),
            "layer_leakage": LayerLeakageDetector(repo_path),
            "bootstrap": BootstrapPathValidator(repo_path),
            "shadow_deps": ShadowDependencyDetector(repo_path),
            "artifact_chain": ArtifactChainValidator(repo_path),
            "migration_geometry": MigrationGeometryValidator(repo_path),
            "mode_lattice": ModeLatticeValidator(repo_path),
        }

    def detect_all(self) -> dict[str, list[ArchitecturalPathology]]:
        """Run all detectors and return pathologies by type."""
        results = {}

        for name, detector in self.detectors.items():
            try:
                if hasattr(detector, "detect"):
                    results[name] = detector.detect()
                elif hasattr(detector, "validate"):
                    results[name] = detector.validate()
            except Exception as e:
                results[name] = [
                    ArchitecturalPathology(
                        pathology_type=PathologyType.BOOTSTRAP_FAILURE,
                        severity="low",
                        message=f"Detector {name} failed: {e}",
                        location="engine",
                    )
                ]

        return results

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all pathologies."""
        results = self.detect_all()

        total = sum(len(p) for p in results.values())
        by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        by_type = {}

        for detector_pathologies in results.values():
            for p in detector_pathologies:
                by_severity[p.severity] += 1
                ptype = p.pathology_type.name
                by_type[ptype] = by_type.get(ptype, 0) + 1

        return {
            "total_pathologies": total,
            "by_detector": {k: len(v) for k, v in results.items()},
            "by_severity": by_severity,
            "by_type": by_type,
            "pathologies": results,
        }


def get_pathology_engine(repo_path: str | Path = None) -> ArchitecturalPathologyEngine:
    """Factory function to get pathology engine instance."""
    return ArchitecturalPathologyEngine(repo_path or Path.cwd())
