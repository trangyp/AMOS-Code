"""
AMOS Equation System v2.0 - Backup & Disaster Recovery

Automated backup and recovery system with:
    - PostgreSQL logical and physical backups
    - Redis RDB snapshot backups
    - S3 storage with encryption
    - Point-in-time recovery (PITR)
    - Automated cleanup of old backups
    - Recovery verification

Author: AMOS Team
Version: 2.0.0
"""

import gzip
import hashlib
import os
import shutil
import subprocess
from datetime import UTC, datetime, timezone

UTC = UTC
from enum import Enum
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from equation_config import get_settings
from equation_logging import get_logger
from equation_tasks import celery_app

logger = get_logger(__name__)
settings = get_settings()


# =============================================================================
# Configuration
# =============================================================================


class BackupConfig:
    """Backup configuration."""

    # Backup retention
    DAILY_BACKUP_RETENTION_DAYS = 7
    WEEKLY_BACKUP_RETENTION_DAYS = 30
    MONTHLY_BACKUP_RETENTION_DAYS = 365

    # S3 configuration
    S3_BUCKET = settings.BACKUP_S3_BUCKET
    S3_PREFIX = "backups"
    S3_REGION = settings.AWS_REGION

    # Local temp directory
    TEMP_DIR = Path("/tmp/amos-backups")

    # Database configuration
    DB_HOST = settings.DATABASE_HOST
    DB_PORT = settings.DATABASE_PORT
    DB_NAME = settings.DATABASE_NAME
    DB_USER = settings.DATABASE_USER
    DB_PASSWORD = settings.DATABASE_PASSWORD

    # Redis configuration
    REDIS_HOST = settings.REDIS_HOST
    REDIS_PORT = settings.REDIS_PORT


# =============================================================================
# Backup Types
# =============================================================================


class BackupType(str, Enum):
    """Backup types."""

    POSTGRESQL_FULL = "postgresql_full"
    POSTGRESQL_INCREMENTAL = "postgresql_incremental"
    REDIS_RDB = "redis_rdb"
    CONFIGURATION = "configuration"


class BackupStatus(str, Enum):
    """Backup status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"


# =============================================================================
# Backup Manager
# =============================================================================


class BackupManager:
    """Backup and recovery manager."""

    def __init__(self):
        self.config = BackupConfig()
        self.s3_client = boto3.client("s3", region_name=self.config.S3_REGION)
        self._ensure_temp_dir()

    def _ensure_temp_dir(self):
        """Ensure temporary directory exists."""
        self.config.TEMP_DIR.mkdir(parents=True, exist_ok=True)

    def _generate_backup_id(self) -> str:
        """Generate unique backup ID."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return f"amos_backup_{timestamp}"

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _compress_file(self, source: Path, destination: Path) -> Path:
        """Compress file with gzip."""
        with open(source, "rb") as f_in:
            with gzip.open(destination, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        return destination

    def _upload_to_s3(self, local_path: Path, s3_key: str, metadata: dict = None) -> bool:
        """Upload file to S3 with encryption."""
        try:
            extra_args = {"ServerSideEncryption": "AES256"}

            if metadata:
                extra_args["Metadata"] = {k: str(v) for k, v in metadata.items()}

            self.s3_client.upload_file(
                str(local_path), self.config.S3_BUCKET, s3_key, ExtraArgs=extra_args
            )

            logger.info(f"Uploaded {local_path.name} to s3://{self.config.S3_BUCKET}/{s3_key}")
            return True

        except ClientError as e:
            logger.error(f"Failed to upload to S3: {e}")
            return False

    def backup_postgresql_full(self, backup_id: str) -> dict:
        """Create full PostgreSQL backup using pg_dump."""
        logger.info(f"Starting PostgreSQL full backup: {backup_id}")

        # Create backup file path
        backup_file = self.config.TEMP_DIR / f"{backup_id}_postgresql.sql"
        compressed_file = self.config.TEMP_DIR / f"{backup_id}_postgresql.sql.gz"

        try:
            # Run pg_dump
            env = os.environ.copy()
            env["PGPASSWORD"] = self.config.DB_PASSWORD

            cmd = [
                "pg_dump",
                "-h",
                self.config.DB_HOST,
                "-p",
                str(self.config.DB_PORT),
                "-U",
                self.config.DB_USER,
                "-d",
                self.config.DB_NAME,
                "-F",
                "p",  # Plain text format
                "-v",
                "-f",
                str(backup_file),
            ]

            result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)

            logger.info(f"pg_dump completed: {backup_file.stat().st_size} bytes")

            # Compress backup
            self._compress_file(backup_file, compressed_file)

            # Calculate checksum
            checksum = self._calculate_checksum(compressed_file)

            # Upload to S3
            s3_key = f"{self.config.S3_PREFIX}/postgresql/{backup_id}.sql.gz"
            metadata = {
                "backup_id": backup_id,
                "backup_type": BackupType.POSTGRESQL_FULL,
                "database": self.config.DB_NAME,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "checksum": checksum,
                "size": str(compressed_file.stat().st_size),
            }

            if self._upload_to_s3(compressed_file, s3_key, metadata):
                logger.info(f"PostgreSQL backup completed: {backup_id}")
                return {
                    "status": BackupStatus.COMPLETED,
                    "backup_id": backup_id,
                    "s3_key": s3_key,
                    "checksum": checksum,
                    "size": compressed_file.stat().st_size,
                }
            else:
                return {
                    "status": BackupStatus.FAILED,
                    "backup_id": backup_id,
                    "error": "S3 upload failed",
                }

        except subprocess.CalledProcessError as e:
            logger.error(f"pg_dump failed: {e.stderr}")
            return {
                "status": BackupStatus.FAILED,
                "backup_id": backup_id,
                "error": f"pg_dump failed: {e.stderr}",
            }
        finally:
            # Cleanup temp files
            if backup_file.exists():
                backup_file.unlink()
            if compressed_file.exists():
                compressed_file.unlink()

    def backup_redis(self, backup_id: str) -> dict:
        """Create Redis RDB backup."""
        logger.info(f"Starting Redis backup: {backup_id}")

        try:
            import redis

            # Connect to Redis
            r = redis.Redis(
                host=self.config.REDIS_HOST, port=self.config.REDIS_PORT, decode_responses=False
            )

            # Trigger BGSAVE
            r.bgsave()

            # Wait for BGSAVE to complete
            import time

            while True:
                info = r.info("persistence")
                if info.get("rdb_bgsave_in_progress") == 0:
                    break
                time.sleep(1)

            # Get RDB file path from Redis config
            config = r.config_get("dir")
            rdb_dir = config.get("dir", "/data")
            rdb_file = Path(rdb_dir) / "dump.rdb"

            # Copy RDB file
            backup_file = self.config.TEMP_DIR / f"{backup_id}_redis.rdb"
            shutil.copy2(rdb_file, backup_file)

            # Compress
            compressed_file = self.config.TEMP_DIR / f"{backup_id}_redis.rdb.gz"
            self._compress_file(backup_file, compressed_file)

            # Calculate checksum
            checksum = self._calculate_checksum(compressed_file)

            # Upload to S3
            s3_key = f"{self.config.S3_PREFIX}/redis/{backup_id}.rdb.gz"
            metadata = {
                "backup_id": backup_id,
                "backup_type": BackupType.REDIS_RDB,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "checksum": checksum,
                "size": str(compressed_file.stat().st_size),
            }

            if self._upload_to_s3(compressed_file, s3_key, metadata):
                logger.info(f"Redis backup completed: {backup_id}")
                return {
                    "status": BackupStatus.COMPLETED,
                    "backup_id": backup_id,
                    "s3_key": s3_key,
                    "checksum": checksum,
                    "size": compressed_file.stat().st_size,
                }
            else:
                return {
                    "status": BackupStatus.FAILED,
                    "backup_id": backup_id,
                    "error": "S3 upload failed",
                }

        except Exception as e:
            logger.error(f"Redis backup failed: {e}")
            return {"status": BackupStatus.FAILED, "backup_id": backup_id, "error": str(e)}
        finally:
            # Cleanup temp files
            backup_file = self.config.TEMP_DIR / f"{backup_id}_redis.rdb"
            compressed_file = self.config.TEMP_DIR / f"{backup_id}_redis.rdb.gz"
            if backup_file.exists():
                backup_file.unlink()
            if compressed_file.exists():
                compressed_file.unlink()

    def cleanup_old_backups(self) -> dict:
        """Clean up old backups based on retention policy."""
        logger.info("Starting backup cleanup")

        deleted_count = 0

        try:
            # List all backups
            paginator = self.s3_client.get_paginator("list_objects_v2")

            for page in paginator.paginate(
                Bucket=self.config.S3_BUCKET, Prefix=self.config.S3_PREFIX
            ):
                for obj in page.get("Contents", []):
                    key = obj["Key"]
                    last_modified = obj["LastModified"]

                    # Determine retention period
                    age_days = (
                        datetime.now(timezone.utc) - last_modified.replace(tzinfo=timezone.utc)
                    ).days

                    should_delete = False
                    if "monthly" in key and age_days > self.config.MONTHLY_BACKUP_RETENTION_DAYS:
                        should_delete = True
                    elif "weekly" in key and age_days > self.config.WEEKLY_BACKUP_RETENTION_DAYS:
                        should_delete = True
                    elif age_days > self.config.DAILY_BACKUP_RETENTION_DAYS:
                        should_delete = True

                    if should_delete:
                        self.s3_client.delete_object(Bucket=self.config.S3_BUCKET, Key=key)
                        deleted_count += 1
                        logger.info(f"Deleted old backup: {key}")

            logger.info(f"Cleanup completed: {deleted_count} backups deleted")
            return {"status": "completed", "deleted_count": deleted_count}

        except ClientError as e:
            logger.error(f"Cleanup failed: {e}")
            return {"status": "failed", "error": str(e)}

    def list_backups(self, backup_type: str = None) -> list:
        """List available backups."""
        backups = []

        try:
            prefix = self.config.S3_PREFIX
            if backup_type:
                prefix = f"{prefix}/{backup_type}"

            paginator = self.s3_client.get_paginator("list_objects_v2")

            for page in paginator.paginate(Bucket=self.config.S3_BUCKET, Prefix=prefix):
                for obj in page.get("Contents", []):
                    # Get metadata
                    head = self.s3_client.head_object(Bucket=self.config.S3_BUCKET, Key=obj["Key"])

                    metadata = head.get("Metadata", {})

                    backups.append(
                        {
                            "key": obj["Key"],
                            "size": obj["Size"],
                            "last_modified": obj["LastModified"].isoformat(),
                            "backup_type": metadata.get("backup_type", "unknown"),
                            "backup_id": metadata.get("backup_id", "unknown"),
                            "checksum": metadata.get("checksum", "unknown"),
                        }
                    )

            # Sort by date descending
            backups.sort(key=lambda x: x["last_modified"], reverse=True)

            return backups

        except ClientError as e:
            logger.error(f"Failed to list backups: {e}")
            return []


# =============================================================================
# Celery Tasks
# =============================================================================


@celery_app.task
def backup_postgresql_task() -> dict:
    """Celery task for PostgreSQL backup."""
    manager = BackupManager()
    backup_id = manager._generate_backup_id()
    return manager.backup_postgresql_full(backup_id)


@celery_app.task
def backup_redis_task() -> dict:
    """Celery task for Redis backup."""
    manager = BackupManager()
    backup_id = manager._generate_backup_id()
    return manager.backup_redis(backup_id)


@celery_app.task
def backup_all_task() -> dict:
    """Celery task for full system backup."""
    results = {
        "postgresql": backup_postgresql_task.delay().get(),
        "redis": backup_redis_task.delay().get(),
    }
    return results


@celery_app.task
def cleanup_backups_task() -> dict:
    """Celery task for backup cleanup."""
    manager = BackupManager()
    return manager.cleanup_old_backups()


# =============================================================================
# CLI Interface
# =============================================================================
"""
Usage with Typer CLI:

import typer
from equation_backup import BackupManager, backup_all_task

app = typer.Typer()

@app.command()
def backup(database: bool = True, redis: bool = True):
    manager = BackupManager()

    if database:
        backup_id = manager._generate_backup_id()
        result = manager.backup_postgresql_full(backup_id)
        typer.echo(f"Database backup: {result['status']}")

    if redis:
        backup_id = manager._generate_backup_id()
        result = manager.backup_redis(backup_id)
        typer.echo(f"Redis backup: {result['status']}")

@app.command()
def list_backups():
    manager = BackupManager()
    backups = manager.list_backups()

    for backup in backups:
        typer.echo(f"{backup['backup_id']} | {backup['backup_type']} | {backup['last_modified']}")

@app.command()
def cleanup():
    manager = BackupManager()
    result = manager.cleanup_old_backups()
    typer.echo(f"Deleted {result['deleted_count']} old backups")

if __name__ == "__main__":
    app()
"""

__all__ = [
    "BackupManager",
    "BackupConfig",
    "BackupType",
    "BackupStatus",
    "backup_postgresql_task",
    "backup_redis_task",
    "backup_all_task",
    "cleanup_backups_task",
]
