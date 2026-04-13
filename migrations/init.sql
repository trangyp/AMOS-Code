-- AMOS Database Schema Migration
-- Initial schema for production database

-- API Query History
CREATE TABLE IF NOT EXISTS queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    api_key_hash TEXT,
    endpoint TEXT NOT NULL,
    query TEXT,
    domain TEXT,
    response_summary TEXT,
    confidence TEXT,
    law_compliant BOOLEAN DEFAULT 1,
    processing_time_ms INTEGER,
    client_ip TEXT,
    user_agent TEXT
);

-- System Metrics
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    metric_type TEXT NOT NULL,
    value REAL NOT NULL,
    labels TEXT,
    period_seconds INTEGER DEFAULT 60
);

-- Health Check History
CREATE TABLE IF NOT EXISTS health_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    overall_status TEXT NOT NULL,
    checks_json TEXT,
    uptime_seconds REAL
);

-- Alerts
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id TEXT UNIQUE NOT NULL,
    rule_name TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT,
    value REAL,
    threshold REAL,
    timestamp TEXT NOT NULL,
    acknowledged_by TEXT,
    acknowledged_at TEXT,
    resolved_at TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_queries_time ON queries(timestamp);
CREATE INDEX IF NOT EXISTS idx_queries_endpoint ON queries(endpoint);
CREATE INDEX IF NOT EXISTS idx_metrics_time ON metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_type ON metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_health_time ON health_history(timestamp);
