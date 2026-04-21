#!/usr/bin/env python3
"""Generate duplicate file report across AMOS codebase."""
import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timezone


def get_file_hash(filepath):
    """Calculate MD5 hash of file content."""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return None


def find_duplicates():
    """Find duplicate files across the codebase."""
    key_files = [
        "AMOS_Brain_Master_Os_v0.json",
        "AMOS_Cognition_Engine_v0.json",
        "AMOS_Design_Engine_v0.json",
        "AMOS_Consciousness_Engine_v0.json",
        "AMOS_Design_Language_Engine_v0.json",
        "AMOS_Biology_And_Cognition_Engine_v0.json",
        "AMOS.config.json",
        "AMOS.brain"
    ]

    duplicates = defaultdict(list)
    base_path = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")

    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        for file in files:
            if file in key_files:
                filepath = Path(root) / file
                file_hash = get_file_hash(filepath)
                if file_hash:
                    duplicates[file].append({
                        'path': str(filepath.relative_to(base_path)),
                        'hash': file_hash,
                        'size': filepath.stat().st_size
                    })

    return duplicates


def main():
    print("=" * 70)
    print("AMOS DUPLICATE FILE REPORT")
    print("=" * 70)

    duplicates = find_duplicates()

    summary = []
    for filename, locations in sorted(duplicates.items()):
        if len(locations) > 1:
            hash_groups = defaultdict(list)
            for loc in locations:
                hash_groups[loc['hash']].append(loc['path'])

            for file_hash, paths in hash_groups.items():
                if len(paths) > 1:
                    summary.append({
                        'file': filename,
                        'hash': file_hash[:8],
                        'count': len(paths),
                        'paths': sorted(paths)
                    })

    print(f"\nFound {len(summary)} files with duplicates:\n")

    for item in summary:
        print(f"\n{item['file']} (hash: {item['hash']})")
        print(f"  Copies: {item['count']}")
        for p in item['paths']:
            marker = "  [CANON]" if '_00_AMOS_CANON' in p or '_AMOS_CANON' in p else ""
            print(f"    - {p}{marker}")

    report = {
        'generated': datetime.now(timezone.utc).isoformat(),
        'duplicates_found': len(summary),
        'total_duplicate_copies': sum(d['count'] for d in summary),
        'files': summary
    }

    report_path = Path("duplicate_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n\nReport saved: {report_path}")
    print(f"  Total duplicate groups: {len(summary)}")
    print(f"  Total duplicate copies: {sum(d['count'] for d in summary)}")


if __name__ == "__main__":
    main()
