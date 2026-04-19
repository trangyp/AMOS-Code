#!/usr/bin/env python3
"""Fix remaining F821 errors in AMOS-code."""

from pathlib import Path


def fix_file(filepath, replacements):
    """Apply replacements to a file."""
    content = filepath.read_text()
    original = content
    for old, new in replacements:
        content = content.replace(old, new)
    if content != original:
        filepath.write_text(content)
        print(f"Fixed: {filepath}")
        return True
    return False


# Fix 1: amos_cli.py - add os import
amos_cli = Path(
    "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/AMOS_ORGANISM_OS/14_INTERFACES/amos_cli.py"
)
if amos_cli.exists():
    fix_file(
        amos_cli,
        [
            (
                "import argparse\nimport json\nimport sys\nfrom pathlib import Path",
                "import argparse\nimport json\nimport os\nimport signal\nimport subprocess\nimport sys\nimport time\nfrom pathlib import Path",
            ),
        ],
    )

# Fix 2: run.py - add AmosCLI import
run_py = Path(
    "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/AMOS_ORGANISM_OS/run.py"
)
if run_py.exists():
    fix_file(
        run_py,
        [
            (
                "from organism import AmosOrganism\nfrom organism import main as organism_main\n\n\ndef run_demo():",
                "from organism import AmosOrganism\nfrom organism import main as organism_main\n\n# Import CLI\ntry:\n    from _14_INTERFACES.amos_cli import AmosCLI\nexcept ImportError:\n    AmosCLI = None  # CLI not available\n\n\ndef run_demo():",
            ),
        ],
    )

# Fix 3: amos_brain/performance_engine.py - fix Ordereddict typo
perf_engine = Path(
    "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/amos_brain/performance_engine.py"
)
if perf_engine.exists():
    fix_file(
        perf_engine,
        [
            ("Ordereddict", "OrderedDict"),
        ],
    )

# Fix 4: clawspring/amos_memory_optimization_engine.py - fix Ordereddict typo
mem_opt = Path(
    "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/clawspring/amos_memory_optimization_engine.py"
)
if mem_opt.exists():
    fix_file(
        mem_opt,
        [
            ("Ordereddict", "OrderedDict"),
        ],
    )

# Fix 5: amos_caching_layer.py - fix Ordereddict typo
caching = Path(
    "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/amos_caching_layer.py"
)
if caching.exists():
    fix_file(
        caching,
        [
            ("Ordereddict", "OrderedDict"),
        ],
    )

print("Done fixing remaining F821 errors!")
