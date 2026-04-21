#!/usr/bin/env python3
"""
Actually USE the 6 repos - Run AMOS-Code repo_doctor on this codebase.
"""
import sys
from pathlib import Path

REPO_ROOT = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
AMOS_REPOS = REPO_ROOT / "AMOS_REPOS"

# Add repos to path
sys.path.insert(0, str(AMOS_REPOS / "AMOS-Code"))

# Import AMOS-Code's repo_doctor
try:
    from repo_doctor.ingest.treesitter_ingest import TreeSitterIngest, ParsedFile
    from repo_doctor.ingest.codeql_bridge import CodeQLBridge
    HAS_REPO_DOCTOR = True
    print("✅ Loaded AMOS-Code repo_doctor")
except ImportError as e:
    print(f"⚠️  repo_doctor not available: {e}")
    HAS_REPO_DOCTOR = False

# Import AMOS brain
try:
    from amos_brain.api_contracts import RepoScanResult, RepoScanRequest
    HAS_CONTRACTS = True
    print("✅ Loaded AMOS-Code api_contracts")
except ImportError as e:
    print(f"⚠️  api_contracts not available: {e}")
    HAS_CONTRACTS = False

import json
from datetime import datetime, timezone
UTC = timezone.utc


def main():
    print("\n" + "="*60)
    print("🔧 USING AMOS-Code repo_doctor on this codebase")
    print("="*60)

    if not HAS_REPO_DOCTOR:
        print("❌ Cannot proceed without repo_doctor")
        return

    # Initialize TreeSitter from AMOS-Code
    ingest = TreeSitterIngest(REPO_ROOT)

    # Find Python files
    py_files = list(REPO_ROOT.rglob("*.py"))
    py_files = [f for f in py_files if not any(x in str(f) for x in [
        ".venv", "__pycache__", ".git", "node_modules", "AMOS_REPOS"
    ])]

    print(f"\n📁 Found {len(py_files)} Python files")
    print("🔍 Parsing first 20 files with AMOS-Code TreeSitter...\n")

    results = []
    for filepath in py_files[:20]:
        try:
            parsed = ingest.parse_file(filepath)
            results.append({
                "file": str(filepath.relative_to(REPO_ROOT)),
                "valid": parsed.is_valid,
                "language": parsed.language,
                "errors": len(parsed.errors),
                "imports": len(parsed.imports),
                "exports": len(parsed.exports)
            })
            status = "✅" if parsed.is_valid else "❌"
            print(f"{status} {filepath.name:40s} ({len(parsed.imports)} imports, {len(parsed.exports)} exports)")
        except Exception as e:
            print(f"❌ {filepath.name:40s} ERROR: {e}")

    # Summary
    valid_count = sum(1 for r in results if r["valid"])
    print("\n" + "="*60)
    print("📊 RESULTS (from AMOS-Code repo_doctor)")
    print("="*60)
    print(f"   Files parsed: {len(results)}")
    print(f"   Valid: {valid_count}")
    print(f"   With errors: {len(results) - valid_count}")

    # Use api_contracts if available
    if HAS_CONTRACTS:
        print("\n📦 Creating RepoScanResult via AMOS-Code api_contracts...")
        scan_result = RepoScanResult(
            scan_id=f"scan-{int(datetime.now(UTC).timestamp())}",
            repo_path=str(REPO_ROOT),
            issues=[],
            summary={
                "total": len(results),
                "valid": valid_count,
                "invalid": len(results) - valid_count
            },
            status="completed"
        )
        print(f"   ✅ Created: {scan_result.scan_id}")

    # Save report
    report_path = REPO_ROOT / ".amos_repo_doctor_report.json"
    report_path.write_text(json.dumps({
        "tool": "AMOS-Code repo_doctor",
        "timestamp": datetime.now(UTC).isoformat(),
        "files_parsed": len(results),
        "valid": valid_count,
        "invalid": len(results) - valid_count,
        "details": results
    }, indent=2))
    print(f"\n💾 Report: {report_path}")

    print("\n" + "="*60)
    print("✅ ACTUALLY USED AMOS-Code repo_doctor!")
    print("="*60)


if __name__ == "__main__":
    main()
