#!/usr/bin/env python3
"""AMOS Project Generator - Intelligent project scaffolding with brain integration.

Integrates: Brain (reasoning) + Knowledge Explorer (engines) + Multi-Agent (fabrication)

Usage:
    python amos_project_generator.py
    python amos_project_generator.py create "A decision support tool for doctors"
    python amos_project_generator.py create "An API for brain analytics"
"""

import sys
from datetime import datetime
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from amos_brain import get_amos_integration
from amos_knowledge_explorer import KnowledgeExplorer


class ProjectScaffold:
    """Represents a generated project scaffold."""

    def __init__(self, name: str, description: str, project_type: str):
        self.name = name
        self.description = description
        self.project_type = project_type
        self.engines: List[dict] = []
        self.files: Dict[str, str] = {}
        self.brain_analysis: dict = {}


class AMOSProjectGenerator:
    """Intelligent project generator using AMOS cognitive architecture.

    Orchestrates:
    1. Brain analysis (Rule of 2/4, L1-L6)
    2. Knowledge exploration (find relevant engines)
    3. Project scaffolding (generate working code)
    """

    def __init__(self):
        self.brain = None
        self.explorer = None
        self.output_dir = Path.cwd() / "generated_projects"

    def initialize(self) -> AMOSProjectGenerator:
        """Initialize brain and knowledge systems."""
        print("🔧 Initializing AMOS Project Generator...")

        # Lazy initialization
        self.brain = get_amos_integration()
        self.explorer = KnowledgeExplorer()
        self.explorer.index()

        print("✓ Brain: 12 engines, 6 laws active")
        print(f"✓ Knowledge: {len(self.explorer._index)} files indexed")
        return self

    def analyze_requirement(self, description: str) -> dict:
        """Use brain to analyze project requirement."""
        print("\n🧠 PHASE 1: Brain Analysis (Rule of 2 + Rule of 4)")
        print("─" * 60)

        analysis = self.brain.analyze_with_rules(description)

        # Extract insights
        recommendations = analysis.get("recommendations", [])
        confidence = analysis.get("structural_integrity_score", 0.0)

        print(f"✓ Confidence: {confidence:.0%}")
        print(f"✓ Recommendations: {len(recommendations)}")

        if recommendations:
            print("\n🎯 Brain recommends:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"   {i}. {rec}")

        return analysis

    def find_engines(self, description: str) -> List[dict]:
        """Find relevant cognitive engines."""
        print("\n📚 PHASE 2: Knowledge Exploration")
        print("─" * 60)

        recommendations = self.explorer.recommend_engines(description)

        print(f"✓ Found {len(recommendations)} relevant engines")

        if recommendations:
            print("\n🔌 Recommended engines:")
            for i, engine in enumerate(recommendations[:5], 1):
                print(f"   {i}. {engine.name} ({engine.engine_type})")
                print(f"      Size: {engine.size_human} | Match: {engine.relevance_score:.1f}")

        return [
            {
                "name": e.name,
                "type": e.engine_type,
                "domain": e.domain,
                "size": e.size_human,
                "score": e.relevance_score,
                "path": str(e.path),
            }
            for e in recommendations[:5]
        ]

    def determine_project_type(self, description: str) -> str:
        """Determine project type from description."""
        desc_lower = description.lower()

        if any(kw in desc_lower for kw in ["api", "rest", "endpoint", "server"]):
            return "api"
        elif any(kw in desc_lower for kw in ["cli", "command", "terminal", "tool"]):
            return "cli"
        elif any(kw in desc_lower for kw in ["web", "dashboard", "ui", "interface"]):
            return "web"
        elif any(kw in desc_lower for kw in ["agent", "bot", "automation", "workflow"]):
            return "agent"
        elif any(kw in desc_lower for kw in ["analysis", "decision", "analytics"]):
            return "analytics"
        else:
            return "general"

    def generate_scaffold(
        self, name: str, description: str, analysis: dict, engines: List[dict]
    ) -> ProjectScaffold:
        """Generate project scaffold."""
        print("\n🏗️  PHASE 3: Project Scaffolding")
        print("─" * 60)

        project_type = self.determine_project_type(description)
        scaffold = ProjectScaffold(name, description, project_type)
        scaffold.engines = engines
        scaffold.brain_analysis = analysis

        # Generate main module
        scaffold.files["main.py"] = self._generate_main_py(name, description, project_type, engines)

        # Generate config
        scaffold.files["config.py"] = self._generate_config_py(name, engines)

        # Generate README
        scaffold.files["README.md"] = self._generate_readme(
            name, description, project_type, engines, analysis
        )

        # Generate decision analysis template
        scaffold.files["decision_analysis.md"] = self._generate_decision_template(name)

        # Generate requirements
        scaffold.files["requirements.txt"] = self._generate_requirements()

        print(f"✓ Generated {len(scaffold.files)} files")
        print(f"✓ Project type: {project_type}")

        return scaffold

    def _generate_main_py(
        self, name: str, description: str, project_type: str, engines: List[dict]
    ) -> str:
        """Generate main Python module."""
        class_name = "".join(word.capitalize() for word in name.replace("-", "_").split("_"))

        engine_refs = (
            "\n".join([f"#   - {e['name']}: {e['type']} ({e['size']})" for e in engines[:3]])
            if engines
            else "#   - No specific engines selected"
        )

        template = f'''#!/usr/bin/env python3
"""
{class_name} - {description}

Generated by AMOS Project Generator
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Recommended cognitive engines:
{engine_refs}
"""

import sys
from pathlib import Path

# Add AMOS brain to path (adjust as needed)
sys.path.insert(0, str(Path(__file__).parent.parent / "AMOS-code"))

from amos_brain import get_amos_integration
from amos_brain.facade import BrainClient


class {class_name}:
    """
    {description}

    This project uses AMOS brain for structured reasoning.
    """

    def __init__(self):
        self.brain = get_amos_integration()
        self.client = BrainClient()

    def analyze(self, problem: str) -> dict:
        """
        Analyze a problem using AMOS Rule of 2 and Rule of 4.

        Args:
            problem: The problem or decision to analyze

        Returns:
            Analysis results with recommendations
        """
        print(f"Analyzing: {{problem}}")

        # Use brain for structured analysis
        result = self.brain.analyze_with_rules(problem)

        return result

    def run(self):
        """Main entry point."""
        print("=" * 60)
        print("  {class_name}")
        print("  {description}")
        print("=" * 60)

        # Example usage
        sample_problem = "Should we implement feature X?"
        analysis = self.analyze(sample_problem)

        print(f"\\nAnalysis complete. Confidence: {{analysis.get('structural_integrity_score', 0):.0%}}")

        return analysis


def main():
    """CLI entry point."""
    app = {class_name}()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
'''
        return template

    def _generate_config_py(self, name: str, engines: List[dict]) -> str:
        """Generate configuration module."""
        engine_list = (
            "\n".join([f'    "{e["name"]}",  # {e["type"]}' for e in engines[:3]])
            if engines
            else "    # No specific engines configured"
        )

        return f'''"""Configuration for {name}."""


class Config:
    """Project configuration."""

    # Project info
    NAME = "{name}"
    VERSION = "0.1.0"

    # AMOS brain settings
    BRAIN_LAZY_LOAD = True
    ENFORCE_GLOBAL_LAWS = True

    # Recommended cognitive engines
    COGNITIVE_ENGINES = [
{engine_list}
    ]

    # Memory settings
    SAVE_REASONING = True
    MEMORY_TAGS = ["{name}", "auto_generated"]

    # Output settings
    EXPORT_DECISIONS = True
    DECISION_FORMAT = "markdown"
'''

    def _generate_readme(
        self, name: str, description: str, project_type: str, engines: List[dict], analysis: dict
    ) -> str:
        """Generate README."""
        engine_section = (
            "\n".join([f"- **{e['name']}**: {e['type']} ({e['size']})" for e in engines[:3]])
            if engines
            else "- No specific engines selected"
        )

        confidence = analysis.get("structural_integrity_score", 0.0)

        return f"""# {name}

{description}

Generated by AMOS Project Generator on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Overview

This project uses the AMOS cognitive architecture for structured reasoning.

- **Project Type**: {project_type}
- **Brain Confidence**: {confidence:.0%}
- **Cognitive Engines**: {len(engines)} recommended

## Recommended Engines

{engine_section}

## Quick Start

```bash
# Run the main application
python main.py

# Or import and use programmatically
from main import {name.replace("-", "_").title().replace(" ", "")}
from typing import Final, Optional

app = {name.replace("-", "_").title().replace(" ", "")}()
result = app.analyze("Your problem here")
```

## AMOS Brain Integration

This project demonstrates:
- Rule of 2 (dual perspectives)
- Rule of 4 (four quadrants)
- Global Laws L1-L6 compliance
- Knowledge engine selection
- Structured decision analysis

## Project Structure

```
{name}/
├── main.py              # Main application
├── config.py            # Configuration
├── decision_analysis.md # Decision template
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Next Steps

1. Review `decision_analysis.md` for decision tracking
2. Customize `config.py` with your settings
3. Extend `main.py` with your specific logic
4. Run with: `python main.py`

---
*Generated by AMOS Brain Project Generator*
"""

    def _generate_decision_template(self, name: str) -> str:
        """Generate decision analysis template."""
        return f"""# Decision Analysis Template

Project: {name}
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Decision to Make

[Describe the decision or problem here]

## Rule of 2 - Dual Perspectives

### Primary Perspective (Internal/Micro)
-

### Alternative Perspective (External/Macro)
-

### Synthesis
-

## Rule of 4 - Four Quadrants

### Biological/Human
-

### Technical/Infrastructural
-

### Economic/Organizational
-

### Environmental/Planetary
-

## Global Laws Check

- [ ] L1: Constraints respected
- [ ] L2: Dual perspectives checked
- [ ] L3: Four quadrants analyzed
- [ ] L4: Logical consistency maintained
- [ ] L5: Clear communication
- [ ] L6: UBI alignment verified

## Recommendations

1.
2.
3.

## Final Decision

**Decision:** [Your decision]
**Confidence:** [0-100%]
**Next Actions:**
1.
2.

---
*Use AMOS brain to analyze: `python main.py`*
"""

    def _generate_requirements(self) -> str:
        """Generate requirements.txt."""
        return """# AMOS Brain Project Requirements
# Install AMOS brain from parent directory
# Or use: pip install -e /path/to/AMOS-code

# Core dependencies (already in AMOS)
# - python >= 3.9
# - dataclasses
# - typing

# Optional for specific engines
# pandas>=1.3.0
# requests>=2.25.0
"""

    def write_project(self, scaffold: ProjectScaffold) -> Path:
        """Write scaffold to disk."""
        project_dir = self.output_dir / scaffold.name.replace(" ", "_").replace("-", "_")
        project_dir.mkdir(parents=True, exist_ok=True)

        for filename, content in scaffold.files.items():
            file_path = project_dir / filename
            file_path.write_text(content)

        return project_dir

    def generate(self, name: str, description: str) -> Path:
        """Generate complete project."""
        print("\n" + "=" * 60)
        print("  AMOS PROJECT GENERATOR")
        print("  Brain-Powered Project Scaffolding")
        print("=" * 60)

        # Initialize
        self.initialize()

        # Phase 1: Brain analysis
        analysis = self.analyze_requirement(description)

        # Phase 2: Knowledge exploration
        engines = self.find_engines(description)

        # Phase 3: Generate scaffold
        scaffold = self.generate_scaffold(name, description, analysis, engines)

        # Write to disk
        project_dir = self.write_project(scaffold)

        # Summary
        print("\n" + "=" * 60)
        print("  PROJECT GENERATED SUCCESSFULLY")
        print("=" * 60)
        print(f"\n📁 Location: {project_dir}")
        print(f"📄 Files: {len(scaffold.files)}")
        print(f"🧠 Brain Analysis: {analysis.get('structural_integrity_score', 0):.0%} confidence")
        print(f"🔌 Engines: {len(engines)} recommended")
        print("\n🚀 To run:")
        print(f"   cd {project_dir}")
        print("   python main.py")

        return project_dir


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate AMOS brain-powered projects")
    parser.add_argument(
        "command", choices=["create", "interactive"], default="interactive", nargs="?"
    )
    parser.add_argument("name", nargs="?", help="Project name")
    parser.add_argument("description", nargs="?", help="Project description")

    args = parser.parse_args()

    generator = AMOSProjectGenerator()

    if args.command == "create":
        if not args.name:
            args.name = input("Project name: ")
        if not args.description:
            args.description = input("Project description: ")

        generator.generate(args.name, args.description)

    else:  # interactive
        print("\n" + "=" * 60)
        print("  AMOS PROJECT GENERATOR - Interactive Mode")
        print("=" * 60)
        print("\nThis tool uses the AMOS brain to:")
        print("  1. Analyze your project with Rule of 2/4")
        print("  2. Find relevant cognitive engines")
        print("  3. Generate working project scaffold")

        name = input("\nProject name: ")
        description = input("What should this project do? ")

        generator.generate(name, description)

        print("\n✨ Project generation complete!")
        print("The brain has analyzed, decided, and built.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
