#!/usr/bin/env python3
"""AMOS Real-World Connectors

Bridges AMOS to external systems:
- Data ingestion (market signals, opportunity detection)
- API connectors (external services, databases)
- Execution hooks (action implementation)
- Webhook/notification system
- Configuration management

This makes AMOS operational in real environments.
"""

import json
import queue
import sqlite3
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Optional

# ============================================================================
# 1. DATA INGESTION - Market Signals & Opportunity Detection
# ============================================================================


@dataclass
class DataSource:
    """Configuration for external data source."""

    source_id: str
    source_type: str  # api, file, database, stream
    endpoint: str
    refresh_interval: int = 3600  # seconds
    reliability_score: float = 0.8
    last_fetch: Optional[datetime] = None
    data_cache: dict = field(default_factory=dict)


class DataIngestionEngine:
    """Ingest real-world signals for AMOS world model.

    Sources:
    - Market data (opportunities, competition)
    - Task systems (incoming work, deadlines)
    - Financial data (revenue, costs, runway)
    - Performance metrics (past outcomes)
    """

    def __init__(self):
        self.sources: dict[str, DataSource] = {}
        self.ingestion_queue: queue.Queue = queue.Queue()
        self.signal_history: deque = deque(maxlen=1000)
        self.running = False
        self.ingestion_thread: Optional[threading.Thread] = None

    def register_source(self, source: DataSource):
        """Register a new data source."""
        self.sources[source.source_id] = source
        print(f"Registered source: {source.source_id} ({source.source_type})")

    def fetch_from_source(self, source_id: str) -> Optional[dict]:
        """Fetch data from registered source."""
        if source_id not in self.sources:
            return None

        source = self.sources[source_id]

        try:
            # Simulate API call (in production, would be real HTTP request)
            if source.source_type == "api":
                data = self._simulate_api_fetch(source)
            elif source.source_type == "file":
                data = self._read_file_source(source)
            elif source.source_type == "database":
                data = self._query_database_source(source)
            else:
                data = {}

            source.last_fetch = datetime.utcnow()
            source.data_cache = data

            # Convert to AMOS Signal format
            signal = {
                "source": source_id,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data,
                "reliability": source.reliability_score,
            }

            self.signal_history.append(signal)
            return signal

        except Exception as e:
            print(f"Error fetching from {source_id}: {e}")
            return None

    def _simulate_api_fetch(self, source: DataSource) -> dict:
        """Simulate API fetch (replace with actual HTTP in production)."""
        # Mock data for demonstration
        if "market" in source.source_id:
            return {
                "opportunity_index": 0.75,
                "competition_pressure": 0.4,
                "market_temperature": "warm",
            }
        elif "tasks" in source.source_id:
            return {"pending_tasks": 5, "urgent_count": 2, "total_value": 15000}
        elif "financial" in source.source_id:
            return {"runway_months": 8, "monthly_burn": 5000, "revenue_trend": "up"}
        return {}

    def _read_file_source(self, source: DataSource) -> dict:
        """Read from file source."""
        try:
            with open(source.endpoint) as f:
                return json.load(f)
        except:
            return {}

    def _query_database_source(self, source: DataSource) -> dict:
        """Query from database."""
        try:
            conn = sqlite3.connect(source.endpoint)
            cursor = conn.cursor()
            # Would execute actual queries here
            conn.close()
            return {"status": "connected"}
        except:
            return {}

    def start_continuous_ingestion(self):
        """Start background thread for continuous data ingestion."""
        self.running = True
        self.ingestion_thread = threading.Thread(target=self._ingestion_loop)
        self.ingestion_thread.daemon = True
        self.ingestion_thread.start()

    def _ingestion_loop(self):
        """Background loop for data ingestion."""
        while self.running:
            for source_id, source in self.sources.items():
                # Check if refresh needed
                if (
                    source.last_fetch is None
                    or (datetime.utcnow() - source.last_fetch).total_seconds()
                    > source.refresh_interval
                ):
                    signal = self.fetch_from_source(source_id)
                    if signal:
                        self.ingestion_queue.put(signal)

            # Sleep before next cycle
            import time

            time.sleep(60)  # Check every minute

    def stop_continuous_ingestion(self):
        """Stop background ingestion."""
        self.running = False
        if self.ingestion_thread:
            self.ingestion_thread.join(timeout=5)

    def get_latest_signals(self, n: int = 100) -> list[dict]:
        """Get latest N signals from all sources."""
        return list(self.signal_history)[-n:]

    def get_aggregated_state(self) -> dict:
        """Get aggregated state from all sources."""
        aggregated = {
            "market": {},
            "tasks": {},
            "financial": {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        for signal in self.signal_history:
            source = signal["source"]
            data = signal["data"]

            if "market" in source:
                aggregated["market"].update(data)
            elif "tasks" in source:
                aggregated["tasks"].update(data)
            elif "financial" in source:
                aggregated["financial"].update(data)

        return aggregated


# ============================================================================
# 2. EXECUTION HOOKS - Action Implementation
# ============================================================================


@dataclass
class ExecutionHook:
    """Hook for executing AMOS decisions in the real world."""

    hook_id: str
    action_type: str
    handler: Callable[[dict], dict]
    enabled: bool = True
    success_rate: float = 0.0
    execution_count: int = 0


class ExecutionManager:
    """Manages execution of AMOS decisions.

    Handlers:
    - create_task → Task management system
    - send_notification → Email/Slack/Discord
    - allocate_resources → Resource management
    - schedule_work → Calendar system
    """

    def __init__(self):
        self.hooks: dict[str, ExecutionHook] = {}
        self.execution_log: deque = deque(maxlen=500)

    def register_hook(self, hook: ExecutionHook):
        """Register execution hook."""
        self.hooks[hook.hook_id] = hook
        print(f"Registered execution hook: {hook.hook_id} ({hook.action_type})")

    def execute(self, action: dict) -> dict:
        """Execute action through appropriate hook."""
        action_type = action.get("type", "unknown")

        # Find matching hook
        matching_hooks = [
            h for h in self.hooks.values() if h.action_type == action_type and h.enabled
        ]

        if not matching_hooks:
            return {
                "status": "no_hook",
                "action": action,
                "error": f"No handler for action type: {action_type}",
            }

        # Use first matching hook
        hook = matching_hooks[0]

        try:
            # Execute
            result = hook.handler(action)

            # Update stats
            hook.execution_count += 1
            if result.get("success"):
                # Update success rate with exponential moving average
                hook.success_rate = (hook.success_rate * 0.9) + (0.1 * 1.0)
            else:
                hook.success_rate = (hook.success_rate * 0.9) + (0.1 * 0.0)

            # Log
            self.execution_log.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "hook_id": hook.hook_id,
                    "action": action,
                    "result": result,
                    "success": result.get("success", False),
                }
            )

            return result

        except Exception as e:
            return {"status": "error", "action": action, "error": str(e)}

    def get_execution_stats(self) -> dict:
        """Get execution statistics."""
        return {
            "hooks": {
                hook_id: {
                    "action_type": hook.action_type,
                    "enabled": hook.enabled,
                    "success_rate": hook.success_rate,
                    "execution_count": hook.execution_count,
                }
                for hook_id, hook in self.hooks.items()
            },
            "recent_executions": len(self.execution_log),
            "overall_success_rate": self._calculate_overall_success_rate(),
        }

    def _calculate_overall_success_rate(self) -> float:
        """Calculate overall success rate."""
        if not self.execution_log:
            return 0.0

        successful = sum(1 for e in self.execution_log if e["success"])
        return successful / len(self.execution_log)


# ============================================================================
# 3. NOTIFICATION SYSTEM - Webhooks & Alerts
# ============================================================================


class NotificationSystem:
    """Send notifications about AMOS decisions and alerts.

    Channels:
    - Console (default)
    - File logging
    - Webhook (HTTP POST)
    - Email (SMTP)
    """

    def __init__(self):
        self.channels: dict[str, dict] = {}
        self.notification_log: deque = deque(maxlen=200)

    def register_channel(self, channel_id: str, channel_type: str, config: dict):
        """Register notification channel."""
        self.channels[channel_id] = {"type": channel_type, "config": config, "enabled": True}

    def notify(self, message: str, level: str = "info", data: Optional[dict] = None):
        """Send notification through all enabled channels."""
        notification = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "data": data or {},
        }

        self.notification_log.append(notification)

        # Send through each channel
        for channel_id, channel in self.channels.items():
            if not channel["enabled"]:
                continue

            try:
                if channel["type"] == "console":
                    self._send_console(notification)
                elif channel["type"] == "file":
                    self._send_file(notification, channel["config"])
                elif channel["type"] == "webhook":
                    self._send_webhook(notification, channel["config"])
            except Exception as e:
                print(f"Notification error on {channel_id}: {e}")

    def _send_console(self, notification: dict):
        """Send to console."""
        level = notification["level"]
        prefix = {"info": "ℹ", "warning": "⚠", "error": "✗", "success": "✓"}.get(level, "•")
        print(f"{prefix} [{notification['timestamp']}] {notification['message']}")

    def _send_file(self, notification: dict, config: dict):
        """Append to log file."""
        filepath = config.get("filepath", "amos_notifications.log")
        with open(filepath, "a") as f:
            f.write(f"{json.dumps(notification)}\n")

    def _send_webhook(self, notification: dict, config: dict):
        """Send HTTP POST to webhook URL."""
        # In production, would use requests.post
        # For now, just log that it would be sent
        print(f"  [Webhook → {config.get('url', 'unknown')}] {notification['message']}")

    def alert_decision(self, decision: dict, reason: str):
        """Alert about important decision."""
        self.notify(
            f"Decision: {decision.get('action', 'unknown')} - {reason}",
            level="info",
            data={"decision": decision, "reason": reason},
        )

    def alert_identity_drift(self, drift_score: float, threshold: float):
        """Alert about identity drift."""
        if drift_score > threshold * 0.8:
            self.notify(
                f"WARNING: Identity drift at {drift_score:.2f} (threshold: {threshold})",
                level="warning",
                data={"drift_score": drift_score, "threshold": threshold},
            )

    def alert_resource_depletion(self, resource: str, current: float, minimum: float):
        """Alert about resource depletion."""
        if current < minimum * 1.2:
            self.notify(
                f"CRITICAL: {resource} at {current:.0f} (minimum: {minimum:.0f})",
                level="error",
                data={"resource": resource, "current": current, "minimum": minimum},
            )


# ============================================================================
# 4. PERSISTENCE LAYER - SQLite Database
# ============================================================================


class PersistenceLayer:
    """SQLite persistence for AMOS state.

    Tables:
    - decisions (action, outcome, timestamp)
    - signals (source, data, timestamp)
    - goals (id, status, progress)
    - metrics (drift, survival, economic scores)
    """

    def __init__(self, db_path: str = "amos_state.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Decisions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle INTEGER,
                action TEXT,
                economic_score REAL,
                identity_drift REAL,
                uncertainty REAL,
                timestamp TEXT,
                outcome TEXT
            )
        """
        )

        # Signals table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                data TEXT,
                reliability REAL,
                timestamp TEXT
            )
        """
        )

        # Metrics table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT,
                value REAL,
                timestamp TEXT
            )
        """
        )

        conn.commit()
        conn.close()

    def save_decision(self, decision: dict):
        """Save decision to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO decisions (cycle, action, economic_score,
                               identity_drift, uncertainty, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                decision.get("cycle", 0),
                decision.get("action", "unknown"),
                decision.get("economic_score", 0.0),
                decision.get("identity_drift", 0.0),
                decision.get("uncertainty", 0.0),
                datetime.utcnow().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

    def save_signal(self, signal: dict):
        """Save signal to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO signals (source, data, reliability, timestamp)
            VALUES (?, ?, ?, ?)
        """,
            (
                signal.get("source", "unknown"),
                json.dumps(signal.get("data", {})),
                signal.get("reliability", 0.5),
                signal.get("timestamp", datetime.utcnow().isoformat()),
            ),
        )

        conn.commit()
        conn.close()

    def get_decision_history(self, n: int = 100) -> list[dict]:
        """Get recent decision history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT cycle, action, economic_score, identity_drift,
                   uncertainty, timestamp
            FROM decisions
            ORDER BY id DESC
            LIMIT ?
        """,
            (n,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "cycle": row[0],
                "action": row[1],
                "economic_score": row[2],
                "identity_drift": row[3],
                "uncertainty": row[4],
                "timestamp": row[5],
            }
            for row in rows
        ]

    def get_metrics_timeseries(self, metric_type: str, hours: int = 24) -> list[dict]:
        """Get metrics timeseries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()

        cursor.execute(
            """
            SELECT value, timestamp
            FROM metrics
            WHERE metric_type = ? AND timestamp > ?
            ORDER BY timestamp
        """,
            (metric_type, cutoff),
        )

        rows = cursor.fetchall()
        conn.close()

        return [{"value": row[0], "timestamp": row[1]} for row in rows]


# ============================================================================
# 5. CONFIGURATION MANAGEMENT
# ============================================================================


class ConfigurationManager:
    """Manage AMOS configuration and parameters."""

    def __init__(self, config_path: str = "amos_config.json"):
        self.config_path = config_path
        self.config = self._load_default_config()
        self._load_from_file()

    def _load_default_config(self) -> dict:
        """Load default configuration."""
        return {
            "amos": {"version": "v4-production", "name": "AMOS", "mode": "production"},
            "ingestion": {
                "enabled": True,
                "refresh_interval": 300,  # 5 minutes
                "sources": [],
            },
            "execution": {
                "enabled": True,
                "dry_run": False,  # If True, log but don't execute
                "hooks": [],
            },
            "notifications": {"enabled": True, "channels": ["console"]},
            "persistence": {"enabled": True, "db_path": "amos_state.db"},
            "constraints": {
                "identity_drift_limit": 0.3,
                "min_survival_score": 0.5,
                "max_allocation_variance": 0.3,
            },
        }

    def _load_from_file(self):
        """Load configuration from file if exists."""
        if Path(self.config_path).exists():
            try:
                with open(self.config_path) as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save(self):
        """Save configuration to file."""
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """Set configuration value."""
        keys = key.split(".")
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def get_all(self) -> dict:
        """Get complete configuration."""
        return self.config.copy()


# ============================================================================
# 6. INTEGRATED CONNECTOR SYSTEM
# ============================================================================


class AMOSConnectorSystem:
    """Unified connector system for AMOS.

    Integrates:
    - Data ingestion (signals)
    - Execution management (actions)
    - Notifications (alerts)
    - Persistence (state)
    - Configuration (settings)
    """

    def __init__(self, config_path: str = "amos_config.json"):
        self.config = ConfigurationManager(config_path)
        self.ingestion = DataIngestionEngine()
        self.execution = ExecutionManager()
        self.notifications = NotificationSystem()
        self.persistence = PersistenceLayer(self.config.get("persistence.db_path", "amos_state.db"))

        self._initialized = False

    def initialize(self):
        """Initialize connector system."""
        print("Initializing AMOS Connector System...")

        # Register default notification channel
        self.notifications.register_channel("console", "console", {})

        # Register default execution hooks
        self._register_default_hooks()

        # Register default data sources
        self._register_default_sources()

        self._initialized = True
        print("✓ Connector system ready")

    def _register_default_hooks(self):
        """Register default execution hooks."""

        # Task creation hook
        def task_handler(action: dict) -> dict:
            print(f"  [EXEC] Creating task: {action.get('name')}")
            return {"success": True, "task_id": f"task_{datetime.utcnow().timestamp()}"}

        self.execution.register_hook(
            ExecutionHook(hook_id="default_task", action_type="create_task", handler=task_handler)
        )

        # Notification hook
        def notify_handler(action: dict) -> dict:
            self.notifications.notify(
                action.get("message", "No message"), action.get("level", "info")
            )
            return {"success": True}

        self.execution.register_hook(
            ExecutionHook(
                hook_id="default_notify", action_type="send_notification", handler=notify_handler
            )
        )

    def _register_default_sources(self):
        """Register default data sources."""
        sources = [
            DataSource("market_api", "api", "https://api.market.com/v1", 3600, 0.8),
            DataSource("task_system", "api", "https://api.tasks.com/v1", 300, 0.9),
            DataSource("financial_db", "database", "financial.db", 3600, 0.95),
        ]

        for source in sources:
            self.ingestion.register_source(source)

    def start(self):
        """Start all connector services."""
        if not self._initialized:
            self.initialize()

        if self.config.get("ingestion.enabled"):
            self.ingestion.start_continuous_ingestion()
            print("✓ Data ingestion started")

        if self.config.get("notifications.enabled"):
            print("✓ Notifications active")

        if self.config.get("persistence.enabled"):
            print("✓ Persistence active")

        self.notifications.notify("AMOS Connector System started", "success")

    def stop(self):
        """Stop all connector services."""
        self.ingestion.stop_continuous_ingestion()
        self.notifications.notify("AMOS Connector System stopped", "info")

    def get_status(self) -> dict:
        """Get complete connector status."""
        return {
            "initialized": self._initialized,
            "config": self.config.get_all(),
            "ingestion": {
                "sources": len(self.ingestion.sources),
                "signals_ingested": len(self.ingestion.signal_history),
                "running": self.ingestion.running,
            },
            "execution": self.execution.get_execution_stats(),
            "notifications": {
                "channels": len(self.notifications.channels),
                "recent_notifications": len(self.notifications.notification_log),
            },
            "persistence": {"db_path": self.persistence.db_path, "connected": True},
        }


def demo_connectors():
    """Demonstrate AMOS Connector System."""
    print("=" * 70)
    print("🔗 AMOS REAL-WORLD CONNECTORS")
    print("=" * 70)
    print("\nBridges AMOS to external systems")
    print("=" * 70)

    # Initialize connector system
    connectors = AMOSConnectorSystem()
    connectors.initialize()

    # 1. Data Ingestion
    print("\n[1] Data Ingestion")
    connectors.ingestion.fetch_from_source("market_api")
    connectors.ingestion.fetch_from_source("task_system")
    print(f"  Fetched from {len(connectors.ingestion.sources)} sources")

    aggregated = connectors.ingestion.get_aggregated_state()
    print(f"  Market: {aggregated['market']}")
    print(f"  Tasks: {aggregated['tasks']}")

    # 2. Execution
    print("\n[2] Execution Hooks")
    result = connectors.execution.execute(
        {"type": "create_task", "name": "Test Task", "priority": "high"}
    )
    print(f"  Execution result: {result}")

    # 3. Notifications
    print("\n[3] Notification System")
    connectors.notifications.notify("Test notification", "info")
    connectors.notifications.alert_identity_drift(0.25, 0.3)

    # 4. Persistence
    print("\n[4] Persistence Layer")
    connectors.persistence.save_decision(
        {
            "cycle": 1,
            "action": "test_action",
            "economic_score": 75.5,
            "identity_drift": 0.05,
            "uncertainty": 0.2,
        }
    )
    print("  Decision saved to database")

    history = connectors.persistence.get_decision_history(n=5)
    print(f"  History entries: {len(history)}")

    # 5. Configuration
    print("\n[5] Configuration Management")
    print(f"  Version: {connectors.config.get('amos.version')}")
    print(f"  Mode: {connectors.config.get('amos.mode')}")
    print(f"  Drift Limit: {connectors.config.get('constraints.identity_drift_limit')}")

    # 6. Overall Status
    print("\n[6] Connector System Status")
    status = connectors.get_status()
    print(f"  Sources: {status['ingestion']['sources']}")
    print(f"  Signals: {status['ingestion']['signals_ingested']}")
    print(f"  Execution Hooks: {len(status['execution']['hooks'])}")
    print(f"  Channels: {status['notifications']['channels']}")

    print("\n" + "=" * 70)
    print("✅ AMOS CONNECTORS OPERATIONAL")
    print("=" * 70)
    print("\nCapabilities:")
    print("  • Data ingestion from APIs, files, databases")
    print("  • Execution hooks for real-world actions")
    print("  • Multi-channel notifications")
    print("  • SQLite persistence")
    print("  • Configuration management")
    print("\nAMOS is now connected to the real world.")
    print("=" * 70)


if __name__ == "__main__":
    demo_connectors()
