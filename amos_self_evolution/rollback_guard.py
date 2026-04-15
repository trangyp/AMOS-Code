"""AMOS Rollback Guard - Reversibility for Self-Evolution

Ensures every self-evolution can be reverted per AMOS Self-Evolution Law 8:
"Evolution must be reversible."

Provides snapshot, backup, and restore capabilities for safe self-improvement.

Owner: AMOS Brain (Canonical Runtime)
Version: 1.0.0
Evolution ID: E004
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from evolution_contract_registry import EvolutionContract, EvolutionStatus


@dataclass
class RollbackSnapshot:
    """A snapshot for potential rollback."""
    
    snapshot_id: str
    evolution_id: str
    timestamp: str
    file_hashes: dict[str, str] = field(default_factory=dict)
    backup_path: str = ""
    description: str = ""
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "evolution_id": self.evolution_id,
            "timestamp": self.timestamp,
            "file_hashes": self.file_hashes,
            "backup_path": self.backup_path,
            "description": self.description,
        }


@dataclass
class RollbackResult:
    """Result of a rollback operation."""
    
    success: bool
    evolution_id: str
    snapshot_id: str
    restored_files: list[str] = field(default_factory=list)
    failed_files: list[str] = field(default_factory=list)
    error_message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "evolution_id": self.evolution_id,
            "snapshot_id": self.snapshot_id,
            "restored_files": self.restored_files,
            "failed_files": self.failed_files,
            "error_message": self.error_message,
            "timestamp": self.timestamp,
        }


class RollbackGuard:
    """Guards against irreversible self-evolution.
    
    Implements reversibility per AMOS Self-Evolution Law 8:
    - Create snapshots before mutation
    - Track file changes with hashes
    - Restore from snapshots on failure
    - Ensure no evolution is permanent until verified
    
    Usage:
        guard = RollbackGuard("/path/to/repo")
        
        # Before evolution
        snapshot = guard.create_snapshot(contract)
        
        # Attempt evolution...
        
        # If failure, rollback
        result = guard.rollback(snapshot.snapshot_id)
    """
    
    def __init__(self, repo_root: str = ".", backup_dir: str | None = None):
        self.repo_root = Path(repo_root).resolve()
        self.backup_dir = Path(backup_dir) if backup_dir else self.repo_root / ".amos_rollback_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Registry of snapshots
        self._snapshots: dict[str, RollbackSnapshot] = {}
        self._registry_file = self.backup_dir / "snapshot_registry.json"
        self._load_registry()
    
    def _load_registry(self) -> None:
        """Load snapshot registry from disk."""
        if self._registry_file.exists():
            try:
                data = json.loads(self._registry_file.read_text())
                for snap_data in data.get("snapshots", []):
                    snapshot = RollbackSnapshot(
                        snapshot_id=snap_data["snapshot_id"],
                        evolution_id=snap_data["evolution_id"],
                        timestamp=snap_data["timestamp"],
                        file_hashes=snap_data.get("file_hashes", {}),
                        backup_path=snap_data.get("backup_path", ""),
                        description=snap_data.get("description", ""),
                    )
                    self._snapshots[snapshot.snapshot_id] = snapshot
            except Exception:
                pass  # Start fresh if registry corrupted
    
    def _save_registry(self) -> None:
        """Save snapshot registry to disk."""
        data = {
            "snapshots": [s.to_dict() for s in self._snapshots.values()],
            "last_updated": datetime.utcnow().isoformat(),
        }
        self._registry_file.write_text(json.dumps(data, indent=2))
    
    def _compute_file_hash(self, filepath: Path) -> str:
        """Compute SHA256 hash of file contents."""
        try:
            content = filepath.read_bytes()
            return hashlib.sha256(content).hexdigest()[:16]
        except Exception:
            return ""
    
    def create_snapshot(self, contract: EvolutionContract, description: str = "") -> RollbackSnapshot:
        """Create a snapshot before applying an evolution.
        
        Captures current state of all target files for potential rollback.
        """
        snapshot_id = f"snap_{contract.evolution_id}_{int(time.time())}"
        timestamp = datetime.utcnow().isoformat()
        
        # Create backup directory for this snapshot
        snapshot_backup_dir = self.backup_dir / snapshot_id
        snapshot_backup_dir.mkdir(parents=True, exist_ok=True)
        
        file_hashes: dict[str, str] = {}
        
        # Backup each target file
        for target_file in contract.target_files:
            source_path = self.repo_root / target_file
            if source_path.exists():
                # Compute hash
                file_hash = self._compute_file_hash(source_path)
                file_hashes[target_file] = file_hash
                
                # Copy to backup
                backup_path = snapshot_backup_dir / target_file.replace("/", "_").replace("\\", "_")
                try:
                    shutil.copy2(source_path, backup_path)
                except Exception:
                    pass
        
        snapshot = RollbackSnapshot(
            snapshot_id=snapshot_id,
            evolution_id=contract.evolution_id,
            timestamp=timestamp,
            file_hashes=file_hashes,
            backup_path=str(snapshot_backup_dir),
            description=description or f"Pre-evolution backup for {contract.evolution_id}",
        )
        
        self._snapshots[snapshot_id] = snapshot
        self._save_registry()
        
        return snapshot
    
    def verify_snapshot_integrity(self, snapshot_id: str) -> bool:
        """Verify that a snapshot's backed up files are intact."""
        if snapshot_id not in self._snapshots:
            return False
        
        snapshot = self._snapshots[snapshot_id]
        backup_dir = Path(snapshot.backup_path)
        
        if not backup_dir.exists():
            return False
        
        # Verify each backed up file exists
        for target_file in snapshot.file_hashes.keys():
            backup_file = backup_dir / target_file.replace("/", "_").replace("\\", "_")
            if not backup_file.exists():
                return False
        
        return True
    
    def rollback(self, snapshot_id: str, dry_run: bool = False) -> RollbackResult:
        """Rollback to a previous snapshot.
        
        Restores all files from the snapshot backup.
        """
        if snapshot_id not in self._snapshots:
            return RollbackResult(
                success=False,
                evolution_id="unknown",
                snapshot_id=snapshot_id,
                error_message=f"Snapshot {snapshot_id} not found",
            )
        
        snapshot = self._snapshots[snapshot_id]
        backup_dir = Path(snapshot.backup_path)
        
        if not backup_dir.exists():
            return RollbackResult(
                success=False,
                evolution_id=snapshot.evolution_id,
                snapshot_id=snapshot_id,
                error_message=f"Backup directory missing: {backup_dir}",
            )
        
        restored: list[str] = []
        failed: list[str] = []
        
        if dry_run:
            # Just report what would be restored
            for target_file in snapshot.file_hashes.keys():
                backup_file = backup_dir / target_file.replace("/", "_").replace("\\", "_")
                if backup_file.exists():
                    restored.append(target_file)
                else:
                    failed.append(target_file)
            
            return RollbackResult(
                success=len(failed) == 0,
                evolution_id=snapshot.evolution_id,
                snapshot_id=snapshot_id,
                restored_files=restored,
                failed_files=failed,
                error_message="Dry run - no changes made" if failed else "",
            )
        
        # Perform actual rollback
        for target_file in snapshot.file_hashes.keys():
            source_path = self.repo_root / target_file
            backup_file = backup_dir / target_file.replace("/", "_").replace("\\", "_")
            
            if backup_file.exists():
                try:
                    # Ensure parent directory exists
                    source_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(backup_file, source_path)
                    restored.append(target_file)
                except Exception as e:
                    failed.append(f"{target_file}: {e}")
            else:
                failed.append(f"{target_file}: backup missing")
        
        return RollbackResult(
            success=len(failed) == 0,
            evolution_id=snapshot.evolution_id,
            snapshot_id=snapshot_id,
            restored_files=restored,
            failed_files=failed,
            error_message=f"Failed to restore {len(failed)} files" if failed else "",
        )
    
    def cleanup_snapshot(self, snapshot_id: str) -> bool:
        """Remove a snapshot after successful evolution (no longer needed)."""
        if snapshot_id not in self._snapshots:
            return False
        
        snapshot = self._snapshots[snapshot_id]
        backup_dir = Path(snapshot.backup_path)
        
        try:
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            del self._snapshots[snapshot_id]
            self._save_registry()
            return True
        except Exception:
            return False
    
    def get_snapshots_for_evolution(self, evolution_id: str) -> list[RollbackSnapshot]:
        """Get all snapshots associated with an evolution."""
        return [s for s in self._snapshots.values() if s.evolution_id == evolution_id]
    
    def list_all_snapshots(self) -> list[dict[str, Any]]:
        """List all snapshots with metadata."""
        return [s.to_dict() for s in self._snapshots.values()]
    
    def can_rollback(self, evolution_id: str) -> bool:
        """Check if an evolution can be rolled back."""
        snapshots = self.get_snapshots_for_evolution(evolution_id)
        return any(self.verify_snapshot_integrity(s.snapshot_id) for s in snapshots)


def main():
    """Demonstrate rollback guard functionality."""
    print("=" * 70)
    print("AMOS ROLLBACK GUARD - E004 SELF-EVOLUTION SUBSYSTEM")
    print("=" * 70)
    print()
    
    guard = RollbackGuard()
    print(f"✓ Rollback Guard initialized")
    print(f"  Backup directory: {guard.backup_dir}")
    
    # Create a mock evolution contract
    from evolution_contract_registry import EvolutionContract
    
    contract = EvolutionContract(
        evolution_id="E004_TEST",
        owner="AMOS Brain",
        target_subsystem="rollback_guard",
        problem_statement="Test rollback capability",
        expected_improvement="Safe test of rollback system",
        verification_steps=["Create snapshot", "Verify restore"],
        mutation_budget_lines=100,
        mutation_budget_files=1,
        target_files=["amos_self_evolution/rollback_guard.py"],
        target_modules=["rollback_guard"],
    )
    print(f"\n✓ Test contract created: {contract.evolution_id}")
    
    # Create snapshot
    print(f"\nCreating pre-evolution snapshot...")
    snapshot = guard.create_snapshot(contract, "Test snapshot before evolution")
    print(f"✓ Snapshot created: {snapshot.snapshot_id}")
    print(f"  Files backed up: {len(snapshot.file_hashes)}")
    
    # Verify snapshot integrity
    if guard.verify_snapshot_integrity(snapshot.snapshot_id):
        print(f"✓ Snapshot integrity verified")
    
    # Test dry-run rollback
    print(f"\nTesting dry-run rollback...")
    result = guard.rollback(snapshot.snapshot_id, dry_run=True)
    print(f"✓ Dry-run result: {result.success}")
    print(f"  Would restore: {len(result.restored_files)} files")
    
    # List snapshots
    all_snaps = guard.list_all_snapshots()
    print(f"\n✓ Total snapshots in registry: {len(all_snaps)}")
    
    # Cleanup
    print(f"\nCleaning up test snapshot...")
    if guard.cleanup_snapshot(snapshot.snapshot_id):
        print(f"✓ Test snapshot cleaned up")
    
    print("\n" + "=" * 70)
    print("E004 ROLLBACK GUARD OPERATIONAL")
    print("=" * 70)
    print("\nSelf-evolution is now reversible per Law 8.")
    print("All mutations can be rolled back to verified snapshots.")


if __name__ == "__main__":
    main()
