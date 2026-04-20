"""
Tree-sitter Activation Script for Repo Doctor Omega
====================================================

Activates incremental parsing capability for the repository
verification engine. This enables fast, error-resilient AST analysis.

Usage:
    python3 repo_doctor/activate_treesitter.py
    python3 repo_doctor/activate_treesitter.py --test-parse <file.py>
    python3 repo_doctor/activate_treesitter.py --analyze-repo
"""

import os
import sys


def check_treesitter_installation() -> dict:
    """Verify tree-sitter and tree-sitter-python are installed."""
    results = {
        "tree_sitter_core": False,
        "tree_sitter_python": False,
        "python_parser": None,
        "errors": [],
    }

    try:
        from tree_sitter import Language, Parser

        results["tree_sitter_core"] = True
        results["Language"] = Language
        results["Parser"] = Parser
    except ImportError as e:
        results["errors"].append(f"tree_sitter core not installed: {e}")
        return results

    try:
        import tree_sitter_python as tspython

        results["tree_sitter_python"] = True
        results["python_parser"] = tspython
    except ImportError as e:
        results["errors"].append(f"tree_sitter_python not installed: {e}")

    return results


def test_parse_file(filepath: str, results: dict) -> dict:
    """Test parsing a Python file with Tree-sitter."""
    Language = results["Language"]
    Parser = results["Parser"]
    tspython = results["python_parser"]

    PY_LANGUAGE = Language(tspython.language())
    parser = Parser(PY_LANGUAGE)

    try:
        with open(filepath) as f:
            source_code = f.read()

        tree = parser.parse(bytes(source_code, "utf8"))
        root_node = tree.root_node

        return {
            "success": True,
            "filepath": filepath,
            "root_type": root_node.type,
            "child_count": len(root_node.children),
            "tree": tree,
        }
    except Exception as e:
        return {"success": False, "filepath": filepath, "error": str(e)}


def analyze_repository(results: dict, repo_path: str = ".") -> dict:
    """Analyze all Python files in the repository."""
    Language = results["Language"]
    Parser = results["Parser"]
    tspython = results["python_parser"]

    PY_LANGUAGE = Language(tspython.language())
    parser = Parser(PY_LANGUAGE)

    stats = {
        "total_files": 0,
        "parsed_successfully": 0,
        "parse_errors": 0,
        "total_nodes": 0,
        "files": [],
    }

    for root, dirs, files in os.walk(repo_path):
        # Skip hidden and cache directories
        dirs[:] = [
            d for d in dirs if not d.startswith(".") and d not in ["__pycache__", "venv", ".venv"]
        ]

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                stats["total_files"] += 1

                try:
                    with open(filepath) as f:
                        source_code = f.read()

                    tree = parser.parse(bytes(source_code, "utf8"))

                    # Count nodes recursively
                    def count_nodes(node):
                        count = 1
                        for child in node.children:
                            count += count_nodes(child)
                        return count

                    node_count = count_nodes(tree.root_node)
                    stats["total_nodes"] += node_count
                    stats["parsed_successfully"] += 1
                    stats["files"].append(
                        {
                            "filepath": filepath,
                            "status": "success",
                            "nodes": node_count,
                            "root_type": tree.root_node.type,
                        }
                    )

                except Exception as e:
                    stats["parse_errors"] += 1
                    stats["files"].append(
                        {"filepath": filepath, "status": "error", "error": str(e)}
                    )

    return stats


def main():
    """Main activation routine."""
    import argparse

    parser = argparse.ArgumentParser(description="Activate Tree-sitter for Repo Doctor Omega")
    parser.add_argument("--test-parse", metavar="FILE", help="Test parse a specific Python file")
    parser.add_argument(
        "--analyze-repo", action="store_true", help="Analyze all Python files in the repository"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    print("=" * 70)
    print("TREE-SITTER ACTIVATION FOR REPO DOCTOR OMEGA")
    print("=" * 70)
    print()

    # Step 1: Check installation
    print("Step 1: Checking Tree-sitter installation...")
    results = check_treesitter_installation()

    if results["tree_sitter_core"]:
        print("  ✓ tree-sitter core: INSTALLED")
    else:
        print("  ✗ tree-sitter core: NOT INSTALLED")
        print("  Run: pip install tree-sitter")
        return 1

    if results["tree_sitter_python"]:
        print("  ✓ tree-sitter-python: INSTALLED")
    else:
        print("  ✗ tree-sitter-python: NOT INSTALLED")
        print("  Run: pip install tree-sitter-python")
        return 1

    print()
    print("Step 2: Initializing parser...")
    Language = results["Language"]
    Parser = results["Parser"]
    tspython = results["python_parser"]

    PY_LANGUAGE = Language(tspython.language())
    parser = Parser(PY_LANGUAGE)
    print("  ✓ Python parser initialized")

    # Step 3: Test parse if requested
    if args.test_parse:
        print()
        print(f"Step 3: Testing parse of {args.test_parse}...")
        result = test_parse_file(args.test_parse, results)

        if result["success"]:
            print("  ✓ Parsed successfully")
            print(f"    Root type: {result['root_type']}")
            print(f"    Children: {result['child_count']}")
        else:
            print(f"  ✗ Parse failed: {result.get('error', 'Unknown error')}")

    # Step 4: Repository analysis if requested
    if args.analyze_repo:
        print()
        print("Step 4: Analyzing repository...")
        stats = analyze_repository(results)

        print(f"  Files analyzed: {stats['total_files']}")
        print(f"  Parsed successfully: {stats['parsed_successfully']}")
        print(f"  Parse errors: {stats['parse_errors']}")
        print(f"  Total AST nodes: {stats['total_nodes']:,}")

        if args.verbose:
            print()
            print("  Files breakdown:")
            for f in stats["files"][:10]:  # Show first 10
                status_icon = "✓" if f["status"] == "success" else "✗"
                print(f"    {status_icon} {f['filepath']}")
            if len(stats["files"]) > 10:
                print(f"    ... and {len(stats['files']) - 10} more")

    print()
    print("=" * 70)
    print("TREE-SITTER ACTIVATION: SUCCESS")
    print("=" * 70)
    print()
    print("Repo Doctor Omega can now perform:")
    print("  • Incremental code parsing")
    print("  • Fast AST analysis")
    print("  • Error-resilient parsing")
    print("  • Multi-language support (Python active)")
    print()
    print("Next: Use --analyze-repo to scan the entire codebase")
    print("      or --test-parse <file.py> to test specific files")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
