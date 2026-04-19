/**
 * AMOS Unified Governance Dashboard
 *
 * Central orchestration hub for autonomous system management.
 * Integrates self-evolution, multi-agent orchestration, and self-healing.
 *
 * Creator: Trang Phan
 * Version: 3.0.0
 */

import React, { useState } from 'react';
import { useDashboardContext } from '../contexts/DashboardContext';

// Governance status type
interface GovernanceStatus {
  mode: 'autonomous' | 'supervised' | 'manual';
  health: 'healthy' | 'degraded' | 'critical';
  activeAgents: number;
  pendingTasks: number;
  evolutionCycles: number;
  lastOptimization: string;
  systemEfficiency: number;
}

// Evolution record type
interface EvolutionRecord {
  id: string;
  timestamp: string;
  type: 'optimization' | 'adaptation' | 'repair' | 'expansion';
  description: string;
  impact: 'high' | 'medium' | 'low';
  status: 'completed' | 'in_progress' | 'pending';
}

// Governance rule type
interface GovernanceRule {
  id: string;
  name: string;
  description: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'active' | 'inactive' | 'suspended';
  trigger: string;
  action: string;
}

export const UnifiedGovernance: React.FC = () => {
  const { orchestraAgents } = useDashboardContext();
  const [governanceMode, setGovernanceMode] = useState<'autonomous' | 'supervised' | 'manual'>('supervised');
  const [selectedTab, setSelectedTab] = useState<'overview' | 'evolution' | 'rules' | 'agents'>('overview');

  // Mock governance status
  const [governanceStatus] = useState<GovernanceStatus>({
    mode: governanceMode,
    health: 'healthy',
    activeAgents: orchestraAgents.length,
    pendingTasks: 12,
    evolutionCycles: 47,
    lastOptimization: new Date(Date.now() - 3600000).toISOString(),
    systemEfficiency: 94,
  });

  // Mock evolution history
  const [evolutionHistory] = useState<EvolutionRecord[]>([
    {
      id: 'evo-001',
      timestamp: new Date(Date.now() - 1800000).toISOString(),
      type: 'optimization',
      description: 'Memory allocation optimized for reasoning engine',
      impact: 'high',
      status: 'completed',
    },
    {
      id: 'evo-002',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      type: 'adaptation',
      description: 'MCP server connection pool resized based on load',
      impact: 'medium',
      status: 'completed',
    },
    {
      id: 'evo-003',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      type: 'repair',
      description: 'Automatic recovery from checkpoint after error',
      impact: 'high',
      status: 'completed',
    },
    {
      id: 'evo-004',
      timestamp: new Date(Date.now() - 900000).toISOString(),
      type: 'expansion',
      description: 'New agent instance spawned for parallel processing',
      impact: 'medium',
      status: 'in_progress',
    },
  ]);

  // Mock governance rules
  const [governanceRules] = useState<GovernanceRule[]>([
    {
      id: 'rule-001',
      name: 'Auto-Recovery',
      description: 'Automatically rewind to checkpoint on system error',
      priority: 'critical',
      status: 'active',
      trigger: 'System error or crash',
      action: 'Rewind to last checkpoint',
    },
    {
      id: 'rule-002',
      name: 'Load Balancing',
      description: 'Spawn additional agents when queue exceeds threshold',
      priority: 'high',
      status: 'active',
      trigger: 'Queue size > 20',
      action: 'Spawn new agent instance',
    },
    {
      id: 'rule-003',
      name: 'Memory Optimization',
      description: 'Compress episodic memory when usage exceeds 80%',
      priority: 'medium',
      status: 'active',
      trigger: 'Memory usage > 80%',
      action: 'Compress old episodic entries',
    },
    {
      id: 'rule-004',
      name: 'Self-Evolution',
      description: 'Analyze performance patterns and suggest optimizations',
      priority: 'medium',
      status: 'active',
      trigger: 'Every 6 hours',
      action: 'Run evolution analysis',
    },
    {
      id: 'rule-005',
      name: 'Security Lockdown',
      description: 'Disable external connections on security breach',
      priority: 'critical',
      status: 'inactive',
      trigger: 'Security anomaly detected',
      action: 'Isolate system and alert',
    },
  ]);

  // Mode selector component
  const ModeSelector = () => (
    <div
      style={{
        display: 'flex',
        gap: '8px',
        padding: '4px',
        background: 'rgba(255, 255, 255, 0.05)',
        borderRadius: '12px',
      }}
    >
      {(['manual', 'supervised', 'autonomous'] as const).map((mode) => (
        <button
          key={mode}
          onClick={() => setGovernanceMode(mode)}
          style={{
            padding: '8px 16px',
            borderRadius: '8px',
            border: 'none',
            background: governanceMode === mode ? 'rgba(99, 102, 241, 0.5)' : 'transparent',
            color: governanceMode === mode ? '#fff' : '#94a3b8',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 500,
            textTransform: 'capitalize',
            transition: 'all 0.2s',
          }}
        >
          {mode === 'autonomous' && '🤖 '}
          {mode === 'supervised' && '👁️ '}
          {mode === 'manual' && '🎮 '}
          {mode}
        </button>
      ))}
    </div>
  );

  // Status card component
  const StatusCard = ({ title, value, subtext, icon, color }: any) => (
    <div
      style={{
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        borderRadius: '12px',
        padding: '20px',
        border: '1px solid rgba(255, 255, 255, 0.1)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
        <span style={{ fontSize: '24px' }}>{icon}</span>
        <span style={{ color: '#94a3b8', fontSize: '14px', fontWeight: 500 }}>{title}</span>
      </div>
      <div style={{ fontSize: '32px', fontWeight: 700, color }}>{value}</div>
      <div style={{ color: '#64748b', fontSize: '12px', marginTop: '4px' }}>{subtext}</div>
    </div>
  );

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', color: '#f8fafc' }}>
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '24px',
        }}
      >
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '8px' }}>
            🏛️ Unified Governance
          </h1>
          <p style={{ color: '#94a3b8' }}>
            Autonomous orchestration, self-evolution, and system governance
          </p>
        </div>
        <ModeSelector />
      </div>

      {/* Governance Mode Banner */}
      <div
        style={{
          background:
            governanceMode === 'autonomous'
              ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1))'
              : governanceMode === 'supervised'
              ? 'linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.1))'
              : 'linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(99, 102, 241, 0.1))',
          borderRadius: '12px',
          padding: '16px 20px',
          marginBottom: '24px',
          border: `1px solid ${
            governanceMode === 'autonomous'
              ? 'rgba(16, 185, 129, 0.3)'
              : governanceMode === 'supervised'
              ? 'rgba(245, 158, 11, 0.3)'
              : 'rgba(99, 102, 241, 0.3)'
          }`,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '24px' }}>
            {governanceMode === 'autonomous' && '🤖'}
            {governanceMode === 'supervised' && '👁️'}
            {governanceMode === 'manual' && '🎮'}
          </span>
          <div>
            <div style={{ fontWeight: 600 }}>
              {governanceMode === 'autonomous' && 'Autonomous Mode Active'}
              {governanceMode === 'supervised' && 'Supervised Mode Active'}
              {governanceMode === 'manual' && 'Manual Mode Active'}
            </div>
            <div style={{ color: '#94a3b8', fontSize: '14px', marginTop: '4px' }}>
              {governanceMode === 'autonomous' &&
                'System is self-managing. All governance rules are automatically enforced.'}
              {governanceMode === 'supervised' &&
                'System suggests actions but requires human approval for major changes.'}
              {governanceMode === 'manual' &&
                'All governance actions are disabled. Manual control only.'}
            </div>
          </div>
        </div>
      </div>

      {/* Status Overview */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px',
          marginBottom: '24px',
        }}
      >
        <StatusCard
          title="System Health"
          value={governanceStatus.health}
          subtext={`${governanceStatus.activeAgents} agents active`}
          icon="🏥"
          color={
            governanceStatus.health === 'healthy'
              ? '#10b981'
              : governanceStatus.health === 'degraded'
              ? '#f59e0b'
              : '#ef4444'
          }
        />
        <StatusCard
          title="Efficiency"
          value={`${governanceStatus.systemEfficiency}%`}
          subtext="System optimization score"
          icon="⚡"
          color="#6366f1"
        />
        <StatusCard
          title="Evolution Cycles"
          value={governanceStatus.evolutionCycles}
          subtext={`Last: ${new Date(governanceStatus.lastOptimization).toLocaleTimeString()}`}
          icon="🧬"
          color="#a855f7"
        />
        <StatusCard
          title="Pending Tasks"
          value={governanceStatus.pendingTasks}
          subtext="Awaiting processing"
          icon="📋"
          color="#f59e0b"
        />
      </div>

      {/* Tab Navigation */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          marginBottom: '24px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          paddingBottom: '16px',
        }}
      >
        {[
          { id: 'overview', label: 'Overview', icon: '📊' },
          { id: 'evolution', label: 'Evolution History', icon: '🧬' },
          { id: 'rules', label: 'Governance Rules', icon: '📜' },
          { id: 'agents', label: 'Agent Orchestra', icon: '🎼' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setSelectedTab(tab.id as any)}
            style={{
              padding: '10px 20px',
              borderRadius: '8px',
              border: 'none',
              background: selectedTab === tab.id ? 'rgba(99, 102, 241, 0.3)' : 'transparent',
              color: selectedTab === tab.id ? '#fff' : '#94a3b8',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 500,
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.2s',
            }}
          >
            <span>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {selectedTab === 'overview' && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '24px',
          }}
        >
          {/* System Architecture */}
          <div
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              backdropFilter: 'blur(10px)',
              borderRadius: '12px',
              padding: '20px',
              border: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>
              🏗️ System Architecture
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {[
                { name: 'Cognitive Core', status: 'operational', load: '45%' },
                { name: 'Agent Orchestra', status: 'operational', load: '62%' },
                { name: 'Memory Systems', status: 'operational', load: '38%' },
                { name: 'Evolution Engine', status: 'operational', load: '23%' },
                { name: 'Governance Layer', status: 'operational', load: '12%' },
              ].map((component) => (
                <div
                  key={component.name}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '12px',
                    background: 'rgba(255, 255, 255, 0.03)',
                    borderRadius: '8px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div
                      style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        background: '#10b981',
                      }}
                    />
                    <span>{component.name}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <span
                      style={{
                        color: '#10b981',
                        fontSize: '14px',
                        textTransform: 'capitalize',
                      }}
                    >
                      {component.status}
                    </span>
                    <span
                      style={{ color: '#64748b', fontSize: '14px', fontFamily: 'monospace' }}
                    >
                      {component.load}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Governance Insights */}
          <div
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              backdropFilter: 'blur(10px)',
              borderRadius: '12px',
              padding: '20px',
              border: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>
              💡 Governance Insights
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {[
                {
                  type: 'optimization',
                  message: 'Consider spawning additional agents during peak hours',
                  confidence: 87,
                },
                {
                  type: 'warning',
                  message: 'Memory usage trending upward - monitor closely',
                  confidence: 72,
                },
                {
                  type: 'info',
                  message: 'Evolution cycle scheduled for 18:00 UTC',
                  confidence: 100,
                },
                {
                  type: 'success',
                  message: 'All governance rules executed successfully',
                  confidence: 99,
                },
              ].map((insight, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '12px',
                    background: 'rgba(255, 255, 255, 0.03)',
                    borderRadius: '8px',
                    borderLeft: `3px solid ${
                      insight.type === 'optimization'
                        ? '#6366f1'
                        : insight.type === 'warning'
                        ? '#f59e0b'
                        : insight.type === 'success'
                        ? '#10b981'
                        : '#3b82f6'
                    }`,
                  }}
                >
                  <div style={{ fontSize: '14px', marginBottom: '4px' }}>{insight.message}</div>
                  <div style={{ fontSize: '12px', color: '#64748b' }}>
                    Confidence: {insight.confidence}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {selectedTab === 'evolution' && (
        <div
          style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            borderRadius: '12px',
            padding: '20px',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>
            🧬 Evolution History
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {evolutionHistory.map((record) => (
              <div
                key={record.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  padding: '16px',
                  background: 'rgba(255, 255, 255, 0.03)',
                  borderRadius: '8px',
                }}
              >
                <div
                  style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background:
                      record.type === 'optimization'
                        ? 'rgba(99, 102, 241, 0.2)'
                        : record.type === 'adaptation'
                        ? 'rgba(16, 185, 129, 0.2)'
                        : record.type === 'repair'
                        ? 'rgba(239, 68, 68, 0.2)'
                        : 'rgba(245, 158, 11, 0.2)',
                    fontSize: '20px',
                  }}
                >
                  {record.type === 'optimization' && '⚡'}
                  {record.type === 'adaptation' && '🔄'}
                  {record.type === 'repair' && '🔧'}
                  {record.type === 'expansion' && '📈'}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 500, marginBottom: '4px' }}>{record.description}</div>
                  <div style={{ fontSize: '12px', color: '#64748b' }}>
                    {new Date(record.timestamp).toLocaleString()} • {record.type}
                  </div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                  <span
                    style={{
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '11px',
                      fontWeight: 600,
                      textTransform: 'uppercase',
                      background:
                        record.impact === 'high'
                          ? 'rgba(239, 68, 68, 0.2)'
                          : record.impact === 'medium'
                          ? 'rgba(245, 158, 11, 0.2)'
                          : 'rgba(59, 130, 246, 0.2)',
                      color:
                        record.impact === 'high'
                          ? '#f87171'
                          : record.impact === 'medium'
                          ? '#fbbf24'
                          : '#60a5fa',
                    }}
                  >
                    {record.impact} impact
                  </span>
                  <span
                    style={{
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '11px',
                      fontWeight: 600,
                      textTransform: 'uppercase',
                      background:
                        record.status === 'completed'
                          ? 'rgba(16, 185, 129, 0.2)'
                          : record.status === 'in_progress'
                          ? 'rgba(245, 158, 11, 0.2)'
                          : 'rgba(107, 114, 128, 0.2)',
                      color:
                        record.status === 'completed'
                          ? '#10b981'
                          : record.status === 'in_progress'
                          ? '#f59e0b'
                          : '#9ca3af',
                    }}
                  >
                    {record.status.replace('_', ' ')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {selectedTab === 'rules' && (
        <div
          style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            borderRadius: '12px',
            padding: '20px',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>
            📜 Governance Rules
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {governanceRules.map((rule) => (
              <div
                key={rule.id}
                style={{
                  padding: '16px',
                  background: 'rgba(255, 255, 255, 0.03)',
                  borderRadius: '8px',
                  borderLeft: `3px solid ${
                    rule.priority === 'critical'
                      ? '#ef4444'
                      : rule.priority === 'high'
                      ? '#f59e0b'
                      : rule.priority === 'medium'
                      ? '#3b82f6'
                      : '#6b7280'
                  }`,
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '8px',
                  }}
                >
                  <div style={{ fontWeight: 600 }}>{rule.name}</div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <span
                      style={{
                        padding: '2px 8px',
                        borderRadius: '4px',
                        fontSize: '11px',
                        fontWeight: 600,
                        textTransform: 'uppercase',
                        background:
                          rule.priority === 'critical'
                            ? 'rgba(239, 68, 68, 0.2)'
                            : rule.priority === 'high'
                            ? 'rgba(245, 158, 11, 0.2)'
                            : 'rgba(59, 130, 246, 0.2)',
                        color:
                          rule.priority === 'critical'
                            ? '#f87171'
                            : rule.priority === 'high'
                            ? '#fbbf24'
                            : '#60a5fa',
                      }}
                    >
                      {rule.priority}
                    </span>
                    <span
                      style={{
                        padding: '2px 8px',
                        borderRadius: '4px',
                        fontSize: '11px',
                        fontWeight: 600,
                        textTransform: 'uppercase',
                        background:
                          rule.status === 'active'
                            ? 'rgba(16, 185, 129, 0.2)'
                            : 'rgba(107, 114, 128, 0.2)',
                        color: rule.status === 'active' ? '#10b981' : '#9ca3af',
                      }}
                    >
                      {rule.status}
                    </span>
                  </div>
                </div>
                <div style={{ color: '#94a3b8', fontSize: '14px', marginBottom: '8px' }}>
                  {rule.description}
                </div>
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '12px',
                    fontSize: '12px',
                    color: '#64748b',
                  }}
                >
                  <div>
                    <strong>Trigger:</strong> {rule.trigger}
                  </div>
                  <div>
                    <strong>Action:</strong> {rule.action}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {selectedTab === 'agents' && (
        <div
          style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            borderRadius: '12px',
            padding: '20px',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>
            🎼 Agent Orchestra
          </h3>
          <div style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🎼</div>
            <div style={{ fontSize: '18px', marginBottom: '8px' }}>Agent Orchestra View</div>
            <div style={{ fontSize: '14px' }}>
              Switch to the Agent Orchestra tab for detailed multi-agent orchestration
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UnifiedGovernance;
