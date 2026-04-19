#!/usr/bin/env python3
"""
AMOS Equation System v2.0 - SDK Client Generator

Generates API client SDKs from OpenAPI specification for multiple languages.

Supported Languages:
    - Python (async/sync)
    - TypeScript/JavaScript
    - Go
    - Java
    - Rust

Usage:
    python sdk/generate_clients.py --all
    python sdk/generate_clients.py --lang python
    python sdk/generate_clients.py --lang typescript --output ./clients/ts

Requirements:
    - Docker (for OpenAPI Generator)
    - Running API server (to fetch OpenAPI spec)

Author: AMOS Team
Version: 2.0.0
"""

import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"
OPENAPI_URL = f"{API_URL}/openapi.json"
SDK_DIR = Path(__file__).parent
OUTPUT_DIR = SDK_DIR / "clients"
GENERATOR_IMAGE = "openapitools/openapi-generator-cli:latest"

# Language configurations
LANGUAGE_CONFIGS = {
    "python": {
        "generator": "python",
        "config": "openapi-generator-config.json",
        "output_subdir": "python",
        "post_process": ["black", "isort"],
    },
    "typescript": {
        "generator": "typescript-fetch",
        "config": None,
        "output_subdir": "typescript",
        "post_process": ["prettier"],
    },
    "javascript": {
        "generator": "javascript",
        "config": None,
        "output_subdir": "javascript",
        "post_process": ["prettier"],
    },
    "go": {
        "generator": "go",
        "config": None,
        "output_subdir": "go",
        "post_process": ["gofmt"],
    },
    "java": {
        "generator": "java",
        "config": None,
        "output_subdir": "java",
        "post_process": [],
    },
    "rust": {
        "generator": "rust",
        "config": None,
        "output_subdir": "rust",
        "post_process": ["rustfmt"],
    },
}


def fetch_openapi_spec() -> dict:
    """Fetch OpenAPI spec from running API server."""
    print(f"Fetching OpenAPI spec from {OPENAPI_URL}...")
    try:
        with urllib.request.urlopen(OPENAPI_URL, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching OpenAPI spec: {e}")
        print("Make sure the API server is running: python equation_app.py")
        sys.exit(1)


def save_openapi_spec(spec: dict, output_path: Path) -> None:
    """Save OpenAPI spec to file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(spec, f, indent=2)
    print(f"Saved OpenAPI spec to {output_path}")


def generate_client(
    lang: str,
    spec_path: Path,
    output_dir: Path,
    config: Optional[Path] = None,
) -> bool:
    """Generate client SDK for specified language."""
    if lang not in LANGUAGE_CONFIGS:
        print(f"Unsupported language: {lang}")
        return False

    lang_config = LANGUAGE_CONFIGS[lang]
    generator = lang_config["generator"]
    output_path = output_dir / lang_config["output_subdir"]

    # Build docker command
    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{spec_path.parent.absolute()}:/spec",
        "-v",
        f"{output_path.absolute()}:/output",
        GENERATOR_IMAGE,
        "generate",
        "-i",
        f"/spec/{spec_path.name}",
        "-g",
        generator,
        "-o",
        "/output",
    ]

    if config and config.exists():
        cmd.extend(["-c", f"/spec/{config.name}"])

    print(f"\nGenerating {lang} client...")
    print(f"Output: {output_path}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Generated {lang} client successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error generating {lang} client:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("Docker not found. Please install Docker to generate clients.")
        return False


def post_process(lang: str, output_dir: Path) -> None:
    """Run post-processing on generated code."""
    if lang not in LANGUAGE_CONFIGS:
        return

    tools = LANGUAGE_CONFIGS[lang].get("post_process", [])
    lang_output = output_dir / LANGUAGE_CONFIGS[lang]["output_subdir"]

    for tool in tools:
        print(f"Running {tool} on {lang} client...")
        try:
            if tool == "black":
                subprocess.run(["black", str(lang_output)], capture_output=True, check=False)
            elif tool == "isort":
                subprocess.run(["isort", str(lang_output)], capture_output=True, check=False)
        except FileNotFoundError:
            print(f"  {tool} not found, skipping")


def create_package_files(lang: str, output_dir: Path) -> None:
    """Create package configuration files for the generated client."""
    lang_output = output_dir / LANGUAGE_CONFIGS[lang]["output_subdir"]

    if lang == "python":
        # Create pyproject.toml if it doesn't exist
        pyproject_path = lang_output / "pyproject.toml"
        if not pyproject_path.exists():
            content = """[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "amos-equation-client"
version = "2.0.0"
description = "AMOS Equation System API Client"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "AMOS Team", email = "team@amos.dev"}
]
keywords = ["amos", "equation", "api", "client"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "urllib3>=1.25.3",
    "python-dateutil>=2.8.0",
    "aiohttp>=3.8.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "black>=23.0",
    "isort>=5.12",
    "mypy>=1.0",
]

[project.urls]
Homepage = "https://github.com/example/amos-equation-system"
Repository = "https://github.com/example/amos-equation-system"
"""
            pyproject_path.write_text(content)
            print(f"Created {pyproject_path}")

    elif lang == "typescript":
        # Create package.json if it doesn't exist
        package_path = lang_output / "package.json"
        if not package_path.exists():
            content = """{
  "name": "@amos/equation-client",
  "version": "2.0.0",
  "description": "AMOS Equation System API Client",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "files": [
    "dist"
  ],
  "scripts": {
    "build": "tsc",
    "prepublishOnly": "npm run build"
  },
  "keywords": ["amos", "equation", "api", "client"],
  "author": "AMOS Team",
  "license": "MIT",
  "dependencies": {
    "cross-fetch": "^4.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/node": "^20.0.0"
  }
}
"""
            package_path.write_text(content)
            print(f"Created {package_path}")


def generate_readme(languages: List[str], output_dir: Path) -> None:
    """Generate README with usage examples for all clients."""
    readme_path = output_dir / "README.md"

    content = """# AMOS Equation System API Clients

Auto-generated API client SDKs for the AMOS Equation System v2.0.

## Available Clients

"""

    for lang in languages:
        content += f"- [{lang.capitalize()}](./{lang}/)\n"

    content += """
## Quick Start

### Python

```bash
pip install amos-equation-client
```

```python
import asyncio
from amos_equation_client import ApiClient, Configuration
from amos_equation_client.api.equations_api import EquationsApi

async def main():
    config = Configuration(host="http://localhost:8000")
    async with ApiClient(config) as client:
        api = EquationsApi(client)
        equations = await api.list_equations_api_v1_equations_get()
        print(equations)

asyncio.run(main())
```

### TypeScript

```bash
npm install @amos/equation-client
```

```typescript
import { Configuration, EquationsApi } from '@amos/equation-client';

const config = new Configuration({ basePath: 'http://localhost:8000' });
const api = new EquationsApi(config);

const equations = await api.listEquationsApiV1EquationsGet();
console.log(equations);
```

## Regenerating Clients

To regenerate clients from the latest OpenAPI spec:

```bash
python sdk/generate_clients.py --all
```

## API Documentation

See the full API documentation at:
- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json
"""

    readme_path.write_text(content)
    print(f"Created {readme_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate API client SDKs for AMOS Equation System"
    )
    parser.add_argument(
        "--lang",
        choices=list(LANGUAGE_CONFIGS.keys()),
        help="Language to generate client for",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate clients for all supported languages",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_DIR,
        help="Output directory for generated clients",
    )
    parser.add_argument(
        "--spec",
        type=Path,
        help="Path to OpenAPI spec file (auto-fetched if not provided)",
    )

    args = parser.parse_args()

    if not args.lang and not args.all:
        parser.print_help()
        sys.exit(1)

    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)

    # Get OpenAPI spec
    if args.spec:
        spec_path = args.spec
    else:
        spec = fetch_openapi_spec()
        spec_path = args.output / "openapi.json"
        save_openapi_spec(spec, spec_path)

    # Determine languages to generate
    languages = list(LANGUAGE_CONFIGS.keys()) if args.all else [args.lang]

    # Generate clients
    success_count = 0
    for lang in languages:
        config_path = (
            SDK_DIR / LANGUAGE_CONFIGS[lang]["config"] if LANGUAGE_CONFIGS[lang]["config"] else None
        )
        if generate_client(lang, spec_path, args.output, config_path):
            post_process(lang, args.output)
            create_package_files(lang, args.output)
            success_count += 1

    # Generate README
    if success_count > 0:
        generate_readme(languages, args.output)

    print(f"\n{success_count}/{len(languages)} clients generated successfully")
    print(f"Output directory: {args.output.absolute()}")

    if success_count < len(languages):
        sys.exit(1)


if __name__ == "__main__":
    main()
