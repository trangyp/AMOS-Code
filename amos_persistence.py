#!/usr/bin/env python3
"""AMOS Persistence Bridge - Integrate Database with Monitoring

Connects the monitoring system to persistent storage:
- Auto-save metrics to database
- Persist alerts for historical analysis
- Query analytics aggregation
- Background data retention cleanup
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from amos_database import get_database, QueryRecord, MetricRecord
from amos_metrics_collector import get_metrics_collector
from amos_health_monitor import get_health_monitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AMOSPersistence:
    """Persistence bridge for AMOS monitoring data."""
    
    def __init__(self, flush_interval: int = 60):
        self.db = get_database()
        self.metrics = get_metrics_collector()
        self.flush_interval = flush_interval
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start background persistence task."""
        self._running = True
        self._task = asyncio.create_task(self._persistence_loop())
        logger.info("Persistence bridge started")
    
    async def stop(self):
        """Stop background persistence task."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Persistence bridge stopped")
    
    async def _persistence_loop(self):
        """Background loop to flush metrics to database."""
        while self._running:
            try:
                await self._flush_metrics()
                await asyncio.sleep(self.flush_interval)
            except Exception as e:
                logger.error(f"Persistence error: {e}")
                await asyncio.sleep(5)  # Short retry on error
    
    async def _flush_metrics(self):
        """Flush current metrics to database."""
        # Get current summary
        summary = self.metrics.get_summary(minutes=self.flush_interval // 60)
        
        # Store key metrics
        timestamp = datetime.utcnow().isoformat()
        
        # Request count
        await self.db.store_metric(MetricRecord(
            timestamp=timestamp,
            metric_type='request_count',
            value=summary.get('total_requests', 0),
            period_seconds=self.flush_interval
        ))
        
        # Error rate
        await self.db.store_metric(MetricRecord(
            timestamp=timestamp,
            metric_type='error_rate',
            value=summary.get('error_rate', 0),
            period_seconds=self.flush_interval
        ))
        
        # Response time
        response_time = summary.get('response_time_ms', {})
        if response_time.get('avg'):
            await self.db.store_metric(MetricRecord(
                timestamp=timestamp,
                metric_type='avg_response_time_ms',
                value=response_time['avg'],
                period_seconds=self.flush_interval
            ))
        
        if response_time.get('p95'):
            await self.db.store_metric(MetricRecord(
                timestamp=timestamp,
                metric_type='p95_response_time_ms',
                value=response_time['p95'],
                period_seconds=self.flush_interval
            ))
        
        # RPS
        await self.db.store_metric(MetricRecord(
            timestamp=timestamp,
            metric_type='requests_per_second',
            value=summary.get('requests_per_second', 0),
            period_seconds=self.flush_interval
        ))
        
        logger.debug(f"Flushed metrics to database: {self.flush_interval}s period")
    
    async def log_api_query(self, endpoint: str, query: str, domain: str,
                            response_summary: str, confidence: str, 
                            law_compliant: bool, processing_time_ms: int,
                            api_key_hash: str = '', client_ip: str = '',
                            user_agent: str = '') -> int:
        """Log an API query to database."""
        record = QueryRecord(
            timestamp=datetime.utcnow().isoformat(),
            api_key_hash=api_key_hash,
            endpoint=endpoint,
            query=query,
            domain=domain,
            response_summary=response_summary,
            confidence=confidence,
            law_compliant=law_compliant,
            processing_time_ms=processing_time_ms,
            client_ip=client_ip,
            user_agent=user_agent
        )
        return await self.db.log_query(record)
    
    async def store_health_snapshot(self, health_monitor):
        """Store current health status."""
        try:
            health = await health_monitor.check_health()
            checks = [
                {
                    'name': c.name,
                    'status': c.status.value,
                    'response_time_ms': c.response_time_ms,
                    'message': c.message
                }
                for c in health.checks
            ]
            
            await self.db.store_health(
                overall_status=health.overall.value,
                checks=checks,
                uptime_seconds=health.uptime_seconds
            )
            
            logger.debug("Health snapshot stored")
        except Exception as e:
            logger.error(f"Failed to store health: {e}")
    
    async def store_alert(self, alert):
        """Store an alert to database."""
        try:
            await self.db.store_alert(
                alert_id=alert.id,
                rule_name=alert.rule_name,
                severity=alert.severity.value,
                status=alert.status.value,
                message=alert.message,
                value=alert.value,
                threshold=alert.threshold
            )
            
            logger.debug(f"Alert stored: {alert.id}")
        except Exception as e:
            logger.error(f"Failed to store alert: {e}")
    
    async def run_cleanup(self, retention_days: int = 30):
        """Run data cleanup for old records."""
        result = await self.db.cleanup_old_data(retention_days)
        logger.info(f"Cleanup complete: {result}")
        return result
    
    async def get_analytics_report(self, days: int = 7) -> dict:
        """Generate comprehensive analytics report."""
        # Get usage stats
        usage = await self.db.get_usage_stats(days=days)
        
        # Get metrics summary
        metrics = await self.db.get_metrics_summary(hours=days * 24)
        
        # Get recent query sample
        queries = await self.db.get_query_history(limit=5, hours=24)
        
        return {
            'period_days': days,
            'generated_at': datetime.utcnow().isoformat(),
            'usage': usage,
            'metrics': metrics,
            'recent_queries_sample': len(queries),
            'summary': {
                'total_queries': usage.get('total_queries', 0),
                'avg_processing_time_ms': usage.get('avg_processing_time_ms', 0),
                'law_compliance_rate': usage.get('law_compliance_rate', 0),
                'top_endpoint': max(usage.get('by_endpoint', {}).items(), 
                                   key=lambda x: x[1])[0] if usage.get('by_endpoint') else None
            }
        }


# Global persistence instance
_persistence: Optional[AMOSPersistence] = None


def get_persistence() -> AMOSPersistence:
    """Get or create global persistence instance."""
    global _persistence
    if _persistence is None:
        _persistence = AMOSPersistence()
    return _persistence


@asynccontextmanager
async def persistence_context():
    """Async context manager for persistence."""
    p = get_persistence()
    await p.start()
    try:
        yield p
    finally:
        await p.stop()


if __name__ == '__main__':
    # Test persistence
    async def test():
        async with persistence_context() as p:
            # Log some queries
            for i in range(5):
                await p.log_api_query(
                    endpoint='think',
                    query=f'Test query {i}',
                    domain='test',
                    response_summary=f'Response {i}',
                    confidence='high',
                    law_compliant=True,
                    processing_time_ms=100 + i * 10
                )
            
            # Wait for flush
            await asyncio.sleep(2)
            
            # Get analytics
            report = await p.get_analytics_report(days=1)
            import json
            print(json.dumps(report, indent=2))
    
    asyncio.run(test())
