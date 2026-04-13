from pathlib import Path
import re

# ============================================================
# AMOS UNIVERSAL RENAME ENGINE — CLEAN, SAFE, DETERMINISTIC
# ============================================================

# Toggle: DRY RUN vs REAL RUN
DRY_RUN = False

# Root folder automatically detected
TARGET_ROOT = Path(__file__).resolve().parent / "_AMOS_UNIVERSE"

# Folders we should NEVER modify
SKIP_DIRS = {
    ".git", ".idea", ".vscode", "__pycache__", "_Archive",
}

# Remove these patterns from filenames/folder names
REMOVE_PATTERNS = [
    r"SUPERSTACK", r"SUPER", r"SUPREME",
    r"vInfinity", r"vINFINITY", r"INFINITY",
    r"OMEGA", r"FULL", r"EXPANDED", r"CANON",
    r"ULTRA",
]

# Allowed file extensions to rename
FILE_EXTS = {".json", ".py", ".ts", ".md"}


# ----------------------- HELPERS -----------------------

def clean_base(name: str) -> str:
    """Cleans unwanted patterns and normalizes underscores."""
    cleaned = name

    # Remove all trash patterns
    for pat in REMOVE_PATTERNS:
        cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)

    # Remove duplicate underscores
    cleaned = re.sub(r"__+", "_", cleaned)

    # Remove leading or trailing underscores
    cleaned = cleaned.strip("_")

    return cleaned


def apply_version(name: str) -> str:
    """Adds _v0 if there is no version suffix."""
    if re.search(r"_v\d+$", name):
        return name
    return f"{name}_v0"


def rename_item(path: Path):
    """Renames a single file or directory."""
    parent = path.parent
    old_name = path.name

    # Skip protected directories
    if path.is_dir() and old_name in SKIP_DIRS:
        return

    # Directories: full name
    if path.is_dir():
        new_base = clean_base(old_name)
        new_base = apply_version(new_base)
        new_path = parent / new_base

    # Files: only rename supported extensions
    elif path.suffix in FILE_EXTS:
        stem = clean_base(path.stem)
        stem = apply_version(stem)
        new_path = parent / f"{stem}{path.suffix}"

    else:
        return

    if new_path == path:
        return

    print(f"{'DRY-RUN' if DRY_RUN else 'RENAME'}: {path} → {new_path}")

    if not DRY_RUN:
        path.rename(new_path)


# ----------------------- MAIN -----------------------

def main():
    if not TARGET_ROOT.exists():
        print(f"ERROR: Target root does not exist: {TARGET_ROOT}")
        return

    print(f"Running rename engine on: {TARGET_ROOT}\n")

    # Directories first, deepest → shallowest
    dirs = sorted(
        (p for p in TARGET_ROOT.rglob("*") if p.is_dir()),
        key=lambda p: len(p.parts),
        reverse=True,
    )
    for d in dirs:
        rename_item(d)

    # Then files
    for f in TARGET_ROOT.rglob("*"):
        if f.is_file():
            rename_item(f)

    print("\nDONE.")


if __name__ == "__main__":
    main()