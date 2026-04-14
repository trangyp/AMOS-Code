"""AMOS Persistence - Data persistence and archival system.

Manages long-term data storage, archival, and retrieval for the AMOS system.
"""

import json
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from amos_database import get_database


class PersistenceManager:
    """Manages data persistence and archival."""
    
    def __init__(self, base_path: str = "AMOS_ORGANISM_OS/memory"):
        self.base_path = Path(base_path)
        self.archive_path = self.base_path / "archives"
        self.archive_path.mkdir(parents=True, exist_ok=True)
    
    def archive_old_data(self, days: int = 30) -> Dict[str, int]:
        """Archive data older than specified days."""
        db = get_database()
        stats = {"queries": 0, "metrics": 0, "events": 0}
        
        cutoff = datetime.now() - timedelta(days=days)
        
        with db.get_connection() as conn:
            # Archive old queries
            cursor = conn.execute("""
                SELECT * FROM query_history 
                WHERE timestamp < ?
            """, (cutoff.isoformat(),))
            
            old_queries = cursor.fetchall()
            if old_queries:
                archive_file = self.archive_path / f"queries_{cutoff.date()}.json.gz"
                with gzip.open(archive_file, 'wt') as f:
                    json.dump([dict(row) for row in old_queries], f)
                
                conn.execute("""
                    DELETE FROM query_history WHERE timestamp < ?
                """, (cutoff.isoformat(),))
                stats["queries"] = len(old_queries)
            
            # Archive old metrics
            cursor = conn.execute("""
                SELECT * FROM metrics_snapshots 
                WHERE timestamp < ?
            """, (cutoff.isoformat(),))
            
            old_metrics = cursor.fetchall()
            if old_metrics:
                archive_file = self.archive_path / f"metrics_{cutoff.date()}.json.gz"
                with gzip.open(archive_file, 'wt') as f:
                    json.dump([dict(row) for row in old_metrics], f)
                
                conn.execute("""
                    DELETE FROM metrics_snapshots WHERE timestamp < ?
                """, (cutoff.isoformat(),))
                stats["metrics"] = len(old_metrics)
            
            conn.commit()
        
        return stats
    
    def restore_archived_data(self, date: str, data_type: str = "all") -> int:
        """Restore archived data for a specific date."""
        restored = 0
        db = get_database()
        
        for archive_file in self.archive_path.glob(f"*_{date}.json.gz"):
            with gzip.open(archive_file, 'rt') as f:
                data = json.load(f)
            
            with db.get_connection() as conn:
                if "queries" in str(archive_file):
                    for item in data:
                        conn.execute("""
                            INSERT OR IGNORE INTO query_history 
                            (id, query, context, response, timestamp, latency_ms, user_id, session_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, tuple(item.values()))
                    restored += len(data)
                
                conn.commit()
        
        return restored
    
    def get_archive_summary(self) -> Dict[str, Any]:
        """Get summary of archived data."""
        archives = list(self.archive_path.glob("*.json.gz"))
        
        by_type = {}
        total_size = 0
        
        for archive in archives:
            size = archive.stat().st_size
            total_size += size
            
            data_type = archive.stem.split('_')[0]
            if data_type not in by_type:
                by_type[data_type] = {"count": 0, "size": 0}
            
            by_type[data_type]["count"] += 1
            by_type[data_type]["size"] += size
        
        return {
            "total_archives": len(archives),
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "by_type": by_type
        }
    
    def export_data(self, start_date: str, end_date: str,
                   data_type: str = "all") -> List[Dict[str, Any]]:
        """Export data for a date range."""
        db = get_database()
        results = []
        
        with db.get_connection() as conn:
            if data_type in ["all", "queries"]:
                cursor = conn.execute("""
                    SELECT * FROM query_history 
                    WHERE timestamp BETWEEN ? AND ?
                """, (start_date, end_date))
                
                for row in cursor.fetchall():
                    results.append({
                        "type": "query",
                        "data": dict(row)
                    })
        
        return results
    
    def cleanup_orphaned_data(self) -> Dict[str, int]:
        """Clean up orphaned or corrupted data."""
        db = get_database()
        stats = {"queries_removed": 0, "events_removed": 0}
        
        with db.get_connection() as conn:
            # Remove queries with null timestamps
            cursor = conn.execute("""
                DELETE FROM query_history WHERE timestamp IS NULL
            """)
            stats["queries_removed"] = cursor.rowcount
            
            # Remove empty events
            cursor = conn.execute("""
                DELETE FROM system_events WHERE message IS NULL OR message = ''
            """)
            stats["events_removed"] = cursor.rowcount
            
            conn.commit()
        
        return stats


# Global persistence manager
_persistence: Optional[PersistenceManager] = None


def get_persistence() -> PersistenceManager:
    """Get global persistence manager."""
    global _persistence
    if _persistence is None:
        _persistence = PersistenceManager()
    return _persistence


if __name__ == "__main__":
    # Demo
    persistence = get_persistence()
    
    # Get archive summary
    summary = persistence.get_archive_summary()
    print(json.dumps(summary, indent=2))
