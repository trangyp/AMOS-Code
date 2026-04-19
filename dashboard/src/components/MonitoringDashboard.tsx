/**
 * AMOS Monitoring Dashboard
 *
 * Observability and monitoring interface for the AMOS system.
 * Displays real-time metrics, logs, system health, and performance data.
 *
 * Creator: Trang Phan
 * Version: 3.0.0
 */

import React, { useState, useEffect } from 'react';
import { useDashboardContext } from '../contexts/DashboardContext';

// Metric card component
interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  icon: string;
  color: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit,
  trend,
  trendValue,
  icon,
  color,
}) => {
  const trendColor = trend === 'up' ? '#10b981' : trend === 'down' ? '#ef4444' : '#6b7280';
  const trendIcon = trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→';

  return (
    <div
      style={{
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        borderRadius: '12px',
        padding: '20px',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        minWidth: '200px',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
        <span style={{ fontSize: '24px' }}>{icon}</span>
        <span style={{ color: '#94a3b8', fontSize: '14px', fontWeight: 500 }}>{title}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
        <span style={{ fontSize: '32px', fontWeight: 700, color }}>{value}</span>
        {unit && <span style={{ color: '#64748b', fontSize: '14px' }}>{unit}</span>}
      </div>
      {trend && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginTop: '8px' }}>
          <span style={{ color: trendColor }}>{trendIcon}</span>
          <span style={{ color: trendColor, fontSize: '12px' }}>{trendValue}</span>
        </div>
      )}
    </div>
  );
};

// Log entry type
interface LogEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'debug';
  source: string;
  message: string;
  metadata?: Record<string, any>;
}

// Mock logs for demonstration
const generateMockLogs = (): LogEntry[] => [
  {
    id: 'log-001',
    timestamp: new Date(Date.now() - 1000).toISOString(),
    level: 'info',
    source: 'backend',
    message: 'API request completed: GET /api/system/status',
    metadata: { duration: '45ms', statusCode: 200 },
  },
  {
    id: 'log-002',
    timestamp: new Date(Date.now() - 5000).toISOString(),
    level: 'info',
    source: 'websocket',
    message: 'Client connected to WebSocket',
    metadata: { clientId: 'ws-client-001' },
  },
  {
    id: 'log-003',
    timestamp: new Date(Date.now() - 10000).toISOString(),
    level: 'warning',
    source: 'backend',
    message: 'High memory usage detected',
    metadata: { memoryUsage: '78%', threshold: '75%' },
  },
  {
    id: 'log-004',
    timestamp: new Date(Date.now() - 15000).toISOString(),
    level: 'info',
    source: 'frontend',
    message: 'Dashboard initialized successfully',
    metadata: { version: '3.0.0', userAgent: 'Chrome/120.0' },
  },
  {
    id: 'log-005',
    timestamp: new Date(Date.now() - 30000).toISOString(),
    level: 'error',
    source: 'backend',
    message: 'Failed to connect to MCP server: mcp-002',
    metadata: { error: 'Connection timeout', retry: 3 },
  },
];

// Log level badge
const LogLevelBadge: React.FC<{ level: LogEntry['level'] }> = ({ level }) => {
  const colors = {
    info: { bg: 'rgba(59, 130, 246, 0.2)', text: '#60a5fa' },
    warning: { bg: 'rgba(245, 158, 11, 0.2)', text: '#fbbf24' },
    error: { bg: 'rgba(239, 68, 68, 0.2)', text: '#f87171' },
    debug: { bg: 'rgba(107, 114, 128, 0.2)', text: '#9ca3af' },
  };

  return (
    <span
      style={{
        background: colors[level].bg,
        color: colors[level].text,
        padding: '2px 8px',
        borderRadius: '4px',
        fontSize: '12px',
        fontWeight: 600,
        textTransform: 'uppercase',
      }}
    >
      {level}
    </span>
  );
};

// Main Monitoring Dashboard component
export const MonitoringDashboard: React.FC = () => {
  const { systemMetrics, systemStatus, wsState, isConnected } = useDashboardContext();
  const [logs, setLogs] = useState<LogEntry[]>(generateMockLogs());
  const [logFilter, setLogFilter] = useState<'all' | 'info' | 'warning' | 'error'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTimeRange, setSelectedTimeRange] = useState<'1h' | '24h' | '7d'>('1h');
  const [expandedLog, setExpandedLog] = useState<string | null>(null);

  // Add new log entries periodically
  useEffect(() => {
    const interval = setInterval(() => {
      const newLog: LogEntry = {
        id: `log-${Date.now()}`,
        timestamp: new Date().toISOString(),
        level: Math.random() > 0.8 ? 'warning' : 'info',
        source: Math.random() > 0.5 ? 'backend' : 'frontend',
        message: `System heartbeat - ${new Date().toLocaleTimeString()}`,
        metadata: { uptime: systemStatus?.uptime || 0 },
      };
      setLogs((prev) => [newLog, ...prev].slice(0, 100));
    }, 10000);

    return () => clearInterval(interval);
  }, [systemStatus?.uptime]);

  // Filter logs
  const filteredLogs = logs.filter((log) => {
    if (logFilter !== 'all' && log.level !== logFilter) return false;
    if (searchQuery && !log.message.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  // Calculate metrics
  const errorRate = Math.round((logs.filter((l) => l.level === 'error').length / logs.length) * 100) || 0;
  const avgResponseTime = 45; // Mock value
  const activeConnections = systemStatus?.activeConnections || 0;
  const wsConnections = systemMetrics?.websocketClients || 0;

  // Service health status
  const services = [
    { name: 'Backend API', status: 'healthy', latency: '45ms' },
    { name: 'WebSocket', status: wsState === 'connected' ? 'healthy' : 'degraded', latency: '12ms' },
    { name: 'Frontend', status: isConnected ? 'healthy' : 'degraded', latency: '23ms' },
    { name: 'Database', status: 'healthy', latency: '8ms' },
  ];

  return (
    <div
      style={{
        padding: '24px',
        maxWidth: '1400px',
        margin: '0 auto',
        color: '#f8fafc',
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '8px' }}>
          🔍 Monitoring & Observability
        </h1>
        <p style={{ color: '#94a3b8' }}>
          Real-time system metrics, logs, and health monitoring
        </p>
      </div>

      {/* Metrics Overview */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px',
          marginBottom: '24px',
        }}
      >
        <MetricCard
          title="CPU Usage"
          value={systemMetrics?.cpu || 0}
          unit="%"
          trend="neutral"
          trendValue="stable"
          icon="🖥️"
          color="#6366f1"
        />
        <MetricCard
          title="Memory"
          value={systemMetrics?.memory || 0}
          unit="%"
          trend={systemMetrics?.memory && systemMetrics.memory > 80 ? 'up' : 'neutral'}
          trendValue={systemMetrics?.memory && systemMetrics.memory > 80 ? 'high' : 'normal'}
          icon="🧠"
          color="#a855f7"
        />
        <MetricCard
          title="Error Rate"
          value={errorRate}
          unit="%"
          trend={errorRate > 5 ? 'up' : 'neutral'}
          trendValue={errorRate > 5 ? 'elevated' : 'normal'}
          icon="⚠️"
          color={errorRate > 5 ? '#ef4444' : '#10b981'}
        />
        <MetricCard
          title="Active Tasks"
          value={systemMetrics?.activeTasks || 0}
          trend="neutral"
          trendValue={`${systemMetrics?.completedTasks || 0} completed`}
          icon="🚀"
          color="#10b981"
        />
        <MetricCard
          title="WebSocket Clients"
          value={wsConnections}
          trend="neutral"
          trendValue={`${activeConnections} HTTP connections`}
          icon="🔌"
          color="#f59e0b"
        />
        <MetricCard
          title="Avg Response Time"
          value={avgResponseTime}
          unit="ms"
          trend="neutral"
          trendValue="optimal"
          icon="⚡"
          color="#3b82f6"
        />
      </div>

      {/* Main Content Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '24px',
        }}
      >
        {/* Service Health Panel */}
        <div
          style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            borderRadius: '12px',
            padding: '20px',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>
            🏥 Service Health
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {services.map((service) => (
              <div
                key={service.name}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '12px',
                  background: 'rgba(255, 255, 255, 0.03)',
                  borderRadius: '8px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div
                    style={{
                      width: '10px',
                      height: '10px',
                      borderRadius: '50%',
                      background:
                        service.status === 'healthy'
                          ? '#10b981'
                          : service.status === 'degraded'
                          ? '#f59e0b'
                          : '#ef4444',
                      boxShadow: `0 0 10px ${
                        service.status === 'healthy'
                          ? 'rgba(16, 185, 129, 0.5)'
                          : service.status === 'degraded'
                          ? 'rgba(245, 158, 11, 0.5)'
                          : 'rgba(239, 68, 68, 0.5)'
                      }`,
                    }}
                  />
                  <span style={{ fontWeight: 500 }}>{service.name}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <span
                    style={{
                      color:
                        service.status === 'healthy'
                          ? '#10b981'
                          : service.status === 'degraded'
                          ? '#f59e0b'
                          : '#ef4444',
                      fontSize: '14px',
                      textTransform: 'capitalize',
                    }}
                  >
                    {service.status}
                  </span>
                  <span style={{ color: '#64748b', fontSize: '14px', fontFamily: 'monospace' }}>
                    {service.latency}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* System Status Panel */}
        <div
          style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            borderRadius: '12px',
            padding: '20px',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>
            📊 System Status
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#94a3b8' }}>Version</span>
              <span style={{ fontFamily: 'monospace' }}>{systemStatus?.version || '3.0.0'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#94a3b8' }}>Status</span>
              <span
                style={{
                  color:
                    systemStatus?.status === 'healthy'
                      ? '#10b981'
                      : systemStatus?.status === 'degraded'
                      ? '#f59e0b'
                      : '#ef4444',
                }}
              >
                {systemStatus?.status || 'healthy'}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#94a3b8' }}>Uptime</span>
              <span>{Math.floor((systemStatus?.uptime || 0) / 3600)}h {Math.floor(((systemStatus?.uptime || 0) % 3600) / 60)}m</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#94a3b8' }}>Active Connections</span>
              <span>{activeConnections}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#94a3b8' }}>WebSocket State</span>
              <span style={{ color: wsState === 'connected' ? '#10b981' : '#f59e0b' }}>{wsState}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#94a3b8' }}>Last Updated</span>
              <span>{new Date(systemStatus?.timestamp || Date.now()).toLocaleTimeString()}</span>
            </div>
          </div>
        </div>

        {/* Logs Panel - Full Width */}
        <div
          style={{
            gridColumn: '1 / -1',
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            borderRadius: '12px',
            padding: '20px',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '16px',
            }}
          >
            <h2 style={{ fontSize: '18px', fontWeight: 600 }}>📝 System Logs</h2>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              {/* Search */}
              <input
                type="text"
                placeholder="Search logs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  background: 'rgba(255, 255, 255, 0.1)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '6px',
                  padding: '6px 12px',
                  color: '#f8fafc',
                  fontSize: '14px',
                  outline: 'none',
                }}
              />
              {/* Filter */}
              <select
                value={logFilter}
                onChange={(e) => setLogFilter(e.target.value as any)}
                style={{
                  background: 'rgba(255, 255, 255, 0.1)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '6px',
                  padding: '6px 12px',
                  color: '#f8fafc',
                  fontSize: '14px',
                  outline: 'none',
                  cursor: 'pointer',
                }}
              >
                <option value="all">All Levels</option>
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="error">Error</option>
              </select>
              {/* Time Range */}
              <div style={{ display: 'flex', gap: '4px' }}>
                {(['1h', '24h', '7d'] as const).map((range) => (
                  <button
                    key={range}
                    onClick={() => setSelectedTimeRange(range)}
                    style={{
                      background: selectedTimeRange === range ? 'rgba(99, 102, 241, 0.5)' : 'rgba(255, 255, 255, 0.1)',
                      border: 'none',
                      borderRadius: '4px',
                      padding: '6px 12px',
                      color: '#f8fafc',
                      fontSize: '12px',
                      cursor: 'pointer',
                    }}
                  >
                    {range}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Log Table */}
          <div
            style={{
              maxHeight: '400px',
              overflow: 'auto',
              fontFamily: 'monospace',
              fontSize: '13px',
            }}
          >
            {filteredLogs.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
                No logs found matching your criteria
              </div>
            ) : (
              filteredLogs.map((log) => (
                <div
                  key={log.id}
                  onClick={() => setExpandedLog(expandedLog === log.id ? null : log.id)}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    padding: '12px',
                    borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                    cursor: 'pointer',
                    transition: 'background 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLDivElement).style.background = 'rgba(255, 255, 255, 0.03)';
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLDivElement).style.background = 'transparent';
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <LogLevelBadge level={log.level} />
                    <span style={{ color: '#64748b', fontSize: '12px' }}>
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                    <span
                      style={{
                        background: 'rgba(99, 102, 241, 0.2)',
                        color: '#818cf8',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        fontSize: '11px',
                      }}
                    >
                      {log.source}
                    </span>
                    <span style={{ flex: 1, color: '#e2e8f0' }}>{log.message}</span>
                    {log.metadata && <span style={{ color: '#64748b' }}>📎</span>}
                  </div>
                  {expandedLog === log.id && log.metadata && (
                    <div
                      style={{
                        marginTop: '8px',
                        padding: '12px',
                        background: 'rgba(0, 0, 0, 0.2)',
                        borderRadius: '6px',
                        color: '#94a3b8',
                        fontSize: '12px',
                      }}
                    >
                      <pre style={{ margin: 0, overflow: 'auto' }}>
                        {JSON.stringify(log.metadata, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>

          {/* Log Stats */}
          <div
            style={{
              display: 'flex',
              gap: '16px',
              marginTop: '16px',
              paddingTop: '16px',
              borderTop: '1px solid rgba(255, 255, 255, 0.1)',
              fontSize: '12px',
              color: '#64748b',
            }}
          >
            <span>Total: {logs.length}</span>
            <span style={{ color: '#60a5fa' }}>Info: {logs.filter((l) => l.level === 'info').length}</span>
            <span style={{ color: '#fbbf24' }}>Warnings: {logs.filter((l) => l.level === 'warning').length}</span>
            <span style={{ color: '#f87171' }}>Errors: {logs.filter((l) => l.level === 'error').length}</span>
            <span>Filtered: {filteredLogs.length}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MonitoringDashboard;
