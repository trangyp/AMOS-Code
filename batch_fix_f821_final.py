#!/usr/bin/env python3
"""Batch fix remaining F821 Undefined name errors."""

import re
import subprocess
from collections import defaultdict
from pathlib import Path

IMPORT_MAP = {
    "Any": "from typing import Optional, Any",
    "Optional": "from typing import Optional, Optional",
    "Dict": "from typing import Optional, Dict",
    "List": "from typing import Optional, List",
    "Set": "from typing import Optional, Set",
    "Tuple": "from typing import Optional, Tuple",
    "Union": "from typing import Optional, Union",
    "Callable": "from typing import Optional, Callable",
    "Protocol": "from typing import Optional, Protocol",
    "TypeVar": "from typing import Optional, TypeVar",
    "Generic": "from typing import Optional, Generic",
    "Task": "from typing import Optional, Task",
    "timedelta": "from datetime import timedelta",
    "timezone": "from datetime import timezone",
    "datetime": "from datetime import datetime",
    "Thread": "from threading import Thread",
    "Tracer": "from opentelemetry.trace import Tracer",
    "Redis": "import redis.asyncio as redis",
    "Annotated": "from typing import Optional, Annotated",
    "AsyncGenerator": "from typing import Optional, AsyncGenerator",
    "AsyncIterator": "from typing import Optional, AsyncIterator",
    "Awaitable": "from typing import Optional, Awaitable",
    "Coroutine": "from typing import Optional, Coroutine",
    "Final": "from typing import Optional, Final",
    "Literal": "from typing import Optional, Literal",
    "NamedTuple": "from typing import Optional, NamedTuple",
    "Pattern": "from typing import Optional, Pattern",
    "TypedDict": "from typing import Optional, TypedDict",
    "Self": "from typing import Optional, Self",
    "Deque": "from typing import Optional, Deque",
    "Iterable": "from typing import Optional, Iterable",
    "Iterator": "from typing import Optional, Iterator",
    "Mapping": "from typing import Optional, Mapping",
    "Sequence": "from typing import Optional, Sequence",
    "Counter": "from typing import Optional, Counter",
}


def get_undefined_names_by_file():
    result = subprocess.run(
        ["ruff", "check", "--select", "F821"],
        capture_output=True,
        text=True,
        cwd="/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code",
    )

    files_to_names = defaultdict(set)
    current_file = None
    current_name = None

    for line in result.stdout.split("\n"):
        match = re.search(r"F821 Undefined name `([^`]+)`", line)
        if match:
            current_name = match.group(1)
            if current_file:
                files_to_names[current_file].add(current_name)
            continue

        match = re.search(r" --> ([^:]+):", line)
        if match:
            current_file = match.group(1)
            if current_name:
                files_to_names[current_file].add(current_name)
                current_name = None

    return dict(files_to_names)


def add_imports_to_file(filepath, undefined_names):
    full_path = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code") / filepath

    try:
        content = full_path.read_text()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False

    typing_names = []
    other_imports = []

    for name in undefined_names:
        if name in IMPORT_MAP:
            import_stmt = IMPORT_MAP[name]
            if import_stmt.startswith("from typing import Optional,"):
                typing_names.append(name)
            elif import_stmt not in content:
                other_imports.append(import_stmt)

    typing_pattern = r"from typing import Optional, ([^\n]+)"
    match = re.search(typing_pattern, content)

    if match:
        existing = match.group(1)
        new_names = [n for n in typing_names if n not in existing]
        if new_names:
            new_import = f"from typing import Optional, {existing}, {', '.join(sorted(new_names))}"
            content = content.replace(f"from typing import Optional, {existing}", new_import)
            print(f"  Updated {filepath}: added {', '.join(new_names)}")
    elif typing_names:
        import_line = f"from typing import Optional, {', '.join(sorted(typing_names))}\n"
        lines = content.split("\n")
        insert_idx = 0

        for i, line in enumerate(lines):
            if i == 0 and line.startswith("#!"):
                insert_idx = i + 1
            elif "from __future__" in line:
                insert_idx = i + 1
            elif insert_idx > 0 and line.strip() and not line.startswith("#"):
                break

        lines.insert(insert_idx, import_line)
        content = "\n".join(lines)
        print(f"  Added typing import to {filepath}: {', '.join(typing_names)}")

    for import_stmt in other_imports:
        if import_stmt not in content:
            lines = content.split("\n")
            insert_idx = 0
            for i, line in enumerate(lines):
                if i == 0 and line.startswith("#!"):
                    insert_idx = i + 1
                elif line.startswith("import ") or line.startswith("from "):
                    insert_idx = i + 1
            lines.insert(insert_idx, import_stmt)
            content = "\n".join(lines)
            print(f"  Added {import_stmt} to {filepath}")

    try:
        full_path.write_text(content)
        return True
    except Exception as e:
        print(f"Error writing {filepath}: {e}")
        return False


def main():
    print("Scanning for F821 errors...")
    files_to_names = get_undefined_names_by_file()
    print(f"Found {len(files_to_names)} files with F821 errors")

    fixed_count = 0
    for filepath, undefined_names in files_to_names.items():
        if add_imports_to_file(filepath, undefined_names):
            fixed_count += 1

    print(f"\nProcessed {fixed_count} files")
    print("\nVerifying fixes...")

    result = subprocess.run(
        ["ruff", "check", "--select", "F821"],
        capture_output=True,
        text=True,
        cwd="/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code",
    )
    remaining = result.stdout.count("F821 Undefined name")
    print(f"Remaining F821 errors: {remaining}")


if __name__ == "__main__":
    main()
