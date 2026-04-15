/**
 * AMOS Agent Orchestra - Multi-Agent Orchestration Visualization
 * 
 * Based on Addy Osmani's "The Code Agent Orchestra" (2026)
 * 
 * Three-Tier Agent Architecture:
 * - Tier 1: Interactive Agents (real-time pair programming)
 * - Tier 2: Parallel Sprint Agents (concurrent feature work)
 * - Tier 3: Backlog Drain Agents (overnight batch processing)
 * 
 * Visual Concept:
 * Agents are represented as musicians in an orchestra, with AMOS as the Conductor.
 * Each agent plays its "instrument" (task), and the Conductor coordinates
their timing, dependencies, and harmony.
 * 
 * Features:
 * - Real-time agent visualization with status indicators
 * - Dependency graph showing agent relationships
 * - Workload distribution visualization
 * - Conductor AI directing the "performance"
 * - Swarm intelligence patterns
 * 
 * Differentiator: While Devin is a solo performer, AMOS is a full orchestra.
 */

import React, { useState, useEffect } from 'react';

// Agent Types
type AgentTier = 1 | 2 | 3;
type AgentStatus = 'idle' | 'warming' | 'performing' | 'waiting' | 'complete' | 'error';
type AgentInstrument = 'strings' | 'winds' | 'percussion' | 'brass' | 'keyboard';

interface Agent {
  id: string;
  name: string;
  tier: AgentTier;
  instrument: AgentInstrument;
  status: AgentStatus;
  task: string;
  progress: number;
  dependencies: string[];
  notes: string[];
  startTime?: string;
  estimatedDuration: number; // minutes
  actualDuration?: number;
  color: string;
}

interface Orchestration {
  id: string;
  name: string;
  tempo: number; // BPM - beats per minute
  key: string;
  agents: string[];
  startTime: string;
  status: 'tuning' | 'performing' | 'finale' | 'complete';
  currentMovement: number;
  totalMovements: number;
}

// Mock Orchestra Data
const MOCK_AGENTS: Agent[] = [
  {
    id: 'agent-1',
    name: 'Frontend Virtuoso',
    tier: 1,
    instrument: 'strings',
    status: 'performing',
    task: 'Implement React component',
    progress: 65,
    dependencies: [],
    notes: ['🎵 Analyzing requirements', '🎵 Generating JSX', '🎵 Adding types'],
    startTime: new Date(Date.now() - 300000).toISOString(),
    estimatedDuration: 15,
    color: '#f59e0b',
  },
  {
    id: 'agent-2',
    name: 'Backend Bassist',
    tier: 1,
    instrument: 'winds',
    status: 'performing',
    task: 'Build API endpoint',
    progress: 80,
    dependencies: [],
    notes: ['🎵 Schema validation', '🎵 Route handler', '🎵 Error handling'],
    startTime: new Date(Date.now() - 400000).toISOString(),
    estimatedDuration: 12,
    color: '#3b82f6',
  },
  {
    id: 'agent-3',
    name: 'Test Percussionist',
    tier: 2,
    instrument: 'percussion',
    status: 'waiting',
    task: 'Write unit tests',
    progress: 0,
    dependencies: ['agent-1', 'agent-2'],
    notes: ['🎼 Waiting for dependencies...'],
    estimatedDuration: 20,
    color: '#ef4444',
  },
  {
    id: 'agent-4',
    name: 'Docs Keyboardist',
    tier: 2,
    instrument: 'keyboard',
    status: 'warming',
    task: 'Update documentation',
    progress: 10,
    dependencies: ['agent-1'],
    notes: ['🎵 Gathering API specs', '🎵 Writing examples'],
    startTime: new Date(Date.now() - 60000).toISOString(),
    estimatedDuration: 25,
    color: '#10b981',
  },
  {
    id: 'agent-5',
    name: 'Refactoring French Horn',
    tier: 3,
    instrument: 'brass',
    status: 'idle',
    task: 'Clean up legacy code',
    progress: 0,
    dependencies: ['agent-3'],
    notes: ['🎼 Queued for overnight batch'],
    estimatedDuration: 45,
    color: '#8b5cf6',
  },
  {
    id: 'agent-6',
    name: 'Security Violin',
    tier: 3,
    instrument: 'strings',
    status: 'idle',
    task: 'Security audit',
    progress: 0,
    dependencies: [],
    notes: ['🎼 Scheduled for 2:00 AM'],
    estimatedDuration: 60,
    color: '#ec4899',
  },
];

const MOCK_ORCHESTRATION: Orchestration = {
  id: 'orch-1',
  name: 'Feature Symphony No. 5',
  tempo: 120,
  key: 'C Major',
  agents: ['agent-1', 'agent-2', 'agent-3', 'agent-4', 'agent-5', 'agent-6'],
  startTime: new Date(Date.now() - 300000).toISOString(),
  status: 'performing',
  currentMovement: 2,
  totalMovements: 4,
};

export const AgentOrchestra: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>(MOCK_AGENTS);
  const [orchestration] = useState<Orchestration>(MOCK_ORCHESTRATION);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [viewMode, setViewMode] = useState<'stage' | 'graph' | 'score'>('stage');
  const [isPaused, setIsPaused] = useState(false);
  const [conductorMessage, setConductorMessage] = useState('Welcome to the Agent Orchestra');

  // Simulate agent progress
  useEffect(() => {
    if (isPaused) return;

    const interval = setInterval(() => {
      setAgents(prev => prev.map(agent => {
        if (agent.status === 'performing' && agent.progress < 100) {
          const newProgress = Math.min(agent.progress + 2, 100);
          return {
            ...agent,
            progress: newProgress,
            status: newProgress === 100 ? 'complete' : 'performing',
          };
        }
        // Check if dependencies are complete
        if (agent.status === 'waiting' && agent.dependencies.length > 0) {
          const depsComplete = agent.dependencies.every(depId => 
            prev.find(a => a.id === depId)?.status === 'complete'
          );
          if (depsComplete) {
            return {
              ...agent,
              status: 'warming',
              notes: ['🎵 Warming up...', '🎵 Preparing to perform'],
            };
          }
        }
        // Warming agents start performing
        if (agent.status === 'warming' && Math.random() > 0.7) {
          return {
            ...agent,
            status: 'performing',
            startTime: new Date().toISOString(),
            notes: ['🎵 Performance started!', ...agent.notes.slice(1)],
          };
        }
        return agent;
      }));
    }, 1000);

    return () => clearInterval(interval);
  }, [isPaused]);

  // Update conductor message based on status
  useEffect(() => {
    const performing = agents.filter(a => a.status === 'performing').length;
    const complete = agents.filter(a => a.status === 'complete').length;
    const total = agents.length;

    if (performing > 0) {
      setConductorMessage(`${performing} agents performing in harmony. Movement ${orchestration.currentMovement} of ${orchestration.totalMovements}.`);
    } else if (complete === total) {
      setConductorMessage('🎉 Symphony complete! All agents finished their performance.');
    } else {
      setConductorMessage('Orchestra tuning... awaiting the downbeat.');
    }
  }, [agents, orchestration]);

  // Get tier label
  const getTierLabel = (tier: AgentTier) => {
    switch (tier) {
      case 1: return 'Tier 1: Interactive';
      case 2: return 'Tier 2: Parallel Sprint';
      case 3: return 'Tier 3: Backlog Drain';
    }
  };

  // Get tier color
  const getTierColor = (tier: AgentTier) => {
    switch (tier) {
      case 1: return '#f59e0b'; // amber
      case 2: return '#3b82f6'; // blue
      case 3: return '#8b5cf6'; // purple
    }
  };

  // Get instrument icon
  const getInstrumentIcon = (instrument: AgentInstrument) => {
    switch (instrument) {
      case 'strings': return '🎻';
      case 'winds': return '🎺';
      case 'percussion': return '🥁';
      case 'brass': return '🎷';
      case 'keyboard': return '🎹';
    }
  };

  // Get status icon
  const getStatusIcon = (status: AgentStatus) => {
    switch (status) {
      case 'idle': return '⚪';
      case 'warming': return '🌡️';
      case 'performing': return '🎵';
      case 'waiting': return '⏸️';
      case 'complete': return '✅';
      case 'error': return '❌';
    }
  };

  // Format time
  const formatTime = (minutes: number) => {
    if (minutes < 1) return '< 1 min';
    return `${minutes} min`;
  };

  return (
    <div style={containerStyle}>
      {/* Header */}
      <div style={headerStyle}>
        <div>
          <h3 style={titleStyle}>🎼 Agent Orchestra</h3>
          <p style={subtitleStyle}>
            Multi-Agent Orchestration • {orchestration.agents.length} musicians • Tempo {orchestration.tempo} BPM
          </p>
        </div>
        <div style={controlsStyle}>
          <button 
            onClick={() => setViewMode('stage')} 
            style={{ ...viewButtonStyle, backgroundColor: viewMode === 'stage' ? 'rgba(99, 102, 241, 0.3)' : 'rgba(255,255,255,0.05)' }}
          >
            🎭 Stage
          </button>
          <button 
            onClick={() => setViewMode('graph')} 
            style={{ ...viewButtonStyle, backgroundColor: viewMode === 'graph' ? 'rgba(99, 102, 241, 0.3)' : 'rgba(255,255,255,0.05)' }}
          >
            🕸️ Graph
          </button>
          <button 
            onClick={() => setViewMode('score')} 
            style={{ ...viewButtonStyle, backgroundColor: viewMode === 'score' ? 'rgba(99, 102, 241, 0.3)' : 'rgba(255,255,255,0.05)' }}
          >
            🎼 Score
          </button>
          <button 
            onClick={() => setIsPaused(!isPaused)}
            style={pauseButtonStyle}
          >
            {isPaused ? '▶️ Resume' : '⏸️ Pause'}
          </button>
        </div>
      </div>

      {/* Conductor Section */}
      <div style={conductorSectionStyle}>
        <div style={conductorAvatarStyle}>🎩</div>
        <div style={conductorInfoStyle}>
          <div style={conductorNameStyle}>AMOS Conductor</div>
          <div style={conductorMessageStyle}>{conductorMessage}</div>
        </div>
        <div style={orchestraStatsStyle}>
          <div style={statItemStyle}>
            <span style={statValueStyle}>{agents.filter(a => a.status === 'performing').length}</span>
            <span style={statLabelStyle}>Performing</span>
          </div>
          <div style={statItemStyle}>
            <span style={statValueStyle}>{agents.filter(a => a.status === 'complete').length}</span>
            <span style={statLabelStyle}>Complete</span>
          </div>
          <div style={statItemStyle}>
            <span style={statValueStyle}>{agents.filter(a => a.status === 'waiting').length}</span>
            <span style={statLabelStyle}>Waiting</span>
          </div>
        </div>
      </div>

      {/* Orchestra Visualization */}
      <div style={orchestraContainerStyle}>
        {/* Stage View */}
        {viewMode === 'stage' && (
          <div style={stageViewStyle}>
            {/* Tier 1 - Front Row (Interactive) */}
            <div style={tierSectionStyle}>
              <div style={tierHeaderStyle}>
                <span style={{ ...tierBadgeStyle, backgroundColor: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24' }}>
                  {getTierLabel(1)}
                </span>
              </div>
              <div style={agentsRowStyle}>
                {agents.filter(a => a.tier === 1).map(agent => (
                  <div 
                    key={agent.id}
                    style={{
                      ...agentCardStyle,
                      borderColor: agent.color,
                      opacity: agent.status === 'idle' ? 0.5 : 1,
                    }}
                    onClick={() => setSelectedAgent(agent)}
                  >
                    <div style={agentHeaderStyle}>
                      <span style={agentIconStyle}>{getInstrumentIcon(agent.instrument)}</span>
                      <span style={agentStatusStyle}>{getStatusIcon(agent.status)}</span>
                    </div>
                    <div style={agentNameStyle}>{agent.name}</div>
                    <div style={agentTaskStyle}>{agent.task}</div>
                    <div style={progressContainerStyle}>
                      <div style={progressBarStyle}>
                        <div 
                          style={{
                            ...progressFillStyle,
                            width: `${agent.progress}%`,
                            backgroundColor: agent.color,
                          }}
                        />
                      </div>
                      <span style={progressTextStyle}>{agent.progress}%</span>
                    </div>
                    {agent.status === 'performing' && (
                      <div style={notesStyle}>
                        {agent.notes.map((note, i) => (
                          <div key={i} style={noteStyle}>{note}</div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Tier 2 - Middle Row (Parallel) */}
            <div style={tierSectionStyle}>
              <div style={tierHeaderStyle}>
                <span style={{ ...tierBadgeStyle, backgroundColor: 'rgba(59, 130, 246, 0.2)', color: '#60a5fa' }}>
                  {getTierLabel(2)}
                </span>
              </div>
              <div style={agentsRowStyle}>
                {agents.filter(a => a.tier === 2).map(agent => (
                  <div 
                    key={agent.id}
                    style={{
                      ...agentCardStyle,
                      borderColor: agent.color,
                      opacity: agent.status === 'idle' ? 0.5 : 1,
                    }}
                    onClick={() => setSelectedAgent(agent)}
                  >
                    <div style={agentHeaderStyle}>
                      <span style={agentIconStyle}>{getInstrumentIcon(agent.instrument)}</span>
                      <span style={agentStatusStyle}>{getStatusIcon(agent.status)}</span>
                    </div>
                    <div style={agentNameStyle}>{agent.name}</div>
                    <div style={agentTaskStyle}>{agent.task}</div>
                    {agent.status === 'waiting' && agent.dependencies.length > 0 && (
                      <div style={dependenciesStyle}>
                        <span style={dependencyLabelStyle}>Waiting for:</span>
                        {agent.dependencies.map(depId => {
                          const dep = agents.find(a => a.id === depId);
                          return dep ? (
                            <span key={depId} style={dependencyBadgeStyle}>
                              {dep.name}
                            </span>
                          ) : null;
                        })}
                      </div>
                    )}
                    <div style={progressContainerStyle}>
                      <div style={progressBarStyle}>
                        <div 
                          style={{
                            ...progressFillStyle,
                            width: `${agent.progress}%`,
                            backgroundColor: agent.color,
                          }}
                        />
                      </div>
                      <span style={progressTextStyle}>{agent.progress}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Tier 3 - Back Row (Overnight) */}
            <div style={tierSectionStyle}>
              <div style={tierHeaderStyle}>
                <span style={{ ...tierBadgeStyle, backgroundColor: 'rgba(139, 92, 246, 0.2)', color: '#a78bfa' }}>
                  {getTierLabel(3)}
                </span>
              </div>
              <div style={agentsRowStyle}>
                {agents.filter(a => a.tier === 3).map(agent => (
                  <div 
                    key={agent.id}
                    style={{
                      ...agentCardStyle,
                      borderColor: agent.color,
                      opacity: agent.status === 'idle' ? 0.5 : 1,
                    }}
                    onClick={() => setSelectedAgent(agent)}
                  >
                    <div style={agentHeaderStyle}>
                      <span style={agentIconStyle}>{getInstrumentIcon(agent.instrument)}</span>
                      <span style={agentStatusStyle}>{getStatusIcon(agent.status)}</span>
                    </div>
                    <div style={agentNameStyle}>{agent.name}</div>
                    <div style={agentTaskStyle}>{agent.task}</div>
                    <div style={scheduledTimeStyle}>
                      ⏰ {formatTime(agent.estimatedDuration)}
                    </div>
                    <div style={progressContainerStyle}>
                      <div style={progressBarStyle}>
                        <div 
                          style={{
                            ...progressFillStyle,
                            width: `${agent.progress}%`,
                            backgroundColor: agent.color,
                          }}
                        />
                      </div>
                      <span style={progressTextStyle}>{agent.progress}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Graph View */}
        {viewMode === 'graph' && (
          <div style={graphViewStyle}>
            <div style={graphContainerStyle}>
              {/* Simple dependency graph visualization */}
              <svg width="100%" height="400" style={graphSvgStyle}>
                {/* Draw connections */}
                {agents.map((agent, index) => {
                  return agent.dependencies.map(depId => {
                    const depIndex = agents.findIndex(a => a.id === depId);
                    if (depIndex === -1) return null;
                    const x1 = 100 + depIndex * 150;
                    const y1 = 100 + depIndex * 50;
                    const x2 = 100 + index * 150;
                    const y2 = 100 + index * 50;
                    return (
                      <line
                        key={`${agent.id}-${depId}`}
                        x1={x1}
                        y1={y1}
                        x2={x2}
                        y2={y2}
                        stroke="rgba(255,255,255,0.2)"
                        strokeWidth="2"
                        strokeDasharray="5,5"
                      />
                    );
                  });
                })}
                
                {/* Draw nodes */}
                {agents.map((agent, index) => (
                  <g key={agent.id} transform={`translate(${100 + index * 150}, ${100 + index * 50})`}>
                    <circle
                      r="30"
                      fill={agent.color}
                      opacity={agent.status === 'complete' ? 0.3 : 0.8}
                    />
                    <text
                      y="-5"
                      textAnchor="middle"
                      fill="white"
                      fontSize="20"
                    >
                      {getInstrumentIcon(agent.instrument)}
                    </text>
                    <text
                      y="50"
                      textAnchor="middle"
                      fill="white"
                      fontSize="10"
                      opacity="0.8"
                    >
                      {agent.name}
                    </text>
                  </g>
                ))}
              </svg>
              <div style={graphLegendStyle}>
                <div style={legendItemStyle}>
                  <span style={legendLineStyle} /> Dependencies
                </div>
                <div style={legendItemStyle}>
                  <span style={legendCircleStyle} /> Agent
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Score View */}
        {viewMode === 'score' && (
          <div style={scoreViewStyle}>
            <div style={scoreHeaderStyle}>
              <div style={scoreTitleStyle}>{orchestration.name}</div>
              <div style={scoreMetaStyle}>
                <span>Key: {orchestration.key}</span>
                <span>•</span>
                <span>Tempo: {orchestration.tempo} BPM</span>
                <span>•</span>
                <span>Movement: {orchestration.currentMovement}/{orchestration.totalMovements}</span>
              </div>
            </div>
            <div style={scoreContentStyle}>
              {agents.map(agent => (
                <div key={agent.id} style={scoreLineStyle}>
                  <div style={scoreAgentNameStyle}>{getInstrumentIcon(agent.instrument)} {agent.name}</div>
                  <div style={scoreTaskStyle}>{agent.task}</div>
                  <div style={scoreStatusStyle}>{getStatusIcon(agent.status)}</div>
                  <div style={scoreBarStyle}>
                    {Array.from({ length: Math.ceil(agent.progress / 10) }).map((_, i) => (
                      <span key={i} style={scoreNoteStyle}>♪</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Agent Detail Modal */}
      {selectedAgent && (
        <div style={modalOverlayStyle} onClick={() => setSelectedAgent(null)}>
          <div style={modalStyle} onClick={(e) => e.stopPropagation()}>
            <div style={modalHeaderStyle}>
              <div>
                <span style={modalIconStyle}>{getInstrumentIcon(selectedAgent.instrument)}</span>
                <span style={modalNameStyle}>{selectedAgent.name}</span>
                <span style={{
                  ...modalTierBadgeStyle,
                  backgroundColor: `${getTierColor(selectedAgent.tier)}20`,
                  color: getTierColor(selectedAgent.tier),
                }}>
                  Tier {selectedAgent.tier}
                </span>
              </div>
              <button onClick={() => setSelectedAgent(null)} style={closeButtonStyle}>✕</button>
            </div>
            <div style={modalContentStyle}>
              <div style={modalTaskStyle}>{selectedAgent.task}</div>
              <div style={modalProgressStyle}>
                <div style={modalProgressBarStyle}>
                  <div 
                    style={{
                      ...modalProgressFillStyle,
                      width: `${selectedAgent.progress}%`,
                      backgroundColor: selectedAgent.color,
                    }}
                  />
                </div>
                <span style={modalProgressTextStyle}>{selectedAgent.progress}%</span>
              </div>
              <div style={modalStatsStyle}>
                <div style={modalStatItemStyle}>
                  <span style={modalStatLabelStyle}>Status</span>
                  <span style={modalStatValueStyle}>{selectedAgent.status}</span>
                </div>
                <div style={modalStatItemStyle}>
                  <span style={modalStatLabelStyle}>Est. Duration</span>
                  <span style={modalStatValueStyle}>{formatTime(selectedAgent.estimatedDuration)}</span>
                </div>
                {selectedAgent.startTime && (
                  <div style={modalStatItemStyle}>
                    <span style={modalStatLabelStyle}>Started</span>
                    <span style={modalStatValueStyle}>
                      {new Date(selectedAgent.startTime).toLocaleTimeString()}
                    </span>
                  </div>
                )}
              </div>
              {selectedAgent.notes.length > 0 && (
                <div style={modalNotesStyle}>
                  <div style={modalNotesTitleStyle}>Performance Notes</div>
                  {selectedAgent.notes.map((note, i) => (
                    <div key={i} style={modalNoteStyle}>{note}</div>
                  ))}
                </div>
              )}
              {selectedAgent.dependencies.length > 0 && (
                <div style={modalDepsStyle}>
                  <div style={modalDepsTitleStyle}>Dependencies</div>
                  {selectedAgent.dependencies.map(depId => {
                    const dep = agents.find(a => a.id === depId);
                    return dep ? (
                      <div key={depId} style={modalDepItemStyle}>
                        <span>{getInstrumentIcon(dep.instrument)} {dep.name}</span>
                        <span style={modalDepStatusStyle}>{getStatusIcon(dep.status)}</span>
                      </div>
                    ) : null;
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Styles
const containerStyle: React.CSSProperties = {
  background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(15, 23, 42, 0.95) 100%)',
  backdropFilter: 'blur(20px)',
  borderRadius: '24px',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  padding: '24px',
  maxWidth: '1200px',
  fontFamily: 'Inter, system-ui, sans-serif',
  color: '#f8fafc',
  boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
};

const headerStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '20px',
  flexWrap: 'wrap',
  gap: '16px',
};

const titleStyle: React.CSSProperties = {
  fontSize: '24px',
  fontWeight: 700,
  margin: '0 0 4px 0',
  background: 'linear-gradient(90deg, #f59e0b, #ec4899)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
};

const subtitleStyle: React.CSSProperties = {
  fontSize: '13px',
  opacity: 0.7,
  margin: 0,
};

const controlsStyle: React.CSSProperties = {
  display: 'flex',
  gap: '8px',
  flexWrap: 'wrap',
};

const viewButtonStyle: React.CSSProperties = {
  padding: '8px 16px',
  borderRadius: '8px',
  border: '1px solid rgba(255,255,255,0.2)',
  color: '#f8fafc',
  cursor: 'pointer',
  fontSize: '13px',
};

const pauseButtonStyle: React.CSSProperties = {
  padding: '8px 16px',
  background: 'rgba(239, 68, 68, 0.2)',
  border: '1px solid rgba(239, 68, 68, 0.3)',
  borderRadius: '8px',
  color: '#ef4444',
  cursor: 'pointer',
  fontSize: '13px',
};

const conductorSectionStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '20px',
  padding: '20px',
  background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.15))',
  borderRadius: '16px',
  marginBottom: '24px',
  border: '1px solid rgba(99, 102, 241, 0.3)',
};

const conductorAvatarStyle: React.CSSProperties = {
  fontSize: '48px',
  animation: 'bounce 2s infinite',
};

const conductorInfoStyle: React.CSSProperties = {
  flex: 1,
};

const conductorNameStyle: React.CSSProperties = {
  fontSize: '16px',
  fontWeight: 600,
  marginBottom: '4px',
  color: '#818cf8',
};

const conductorMessageStyle: React.CSSProperties = {
  fontSize: '14px',
  opacity: 0.9,
  fontStyle: 'italic',
};

const orchestraStatsStyle: React.CSSProperties = {
  display: 'flex',
  gap: '24px',
};

const statItemStyle: React.CSSProperties = {
  textAlign: 'center',
};

const statValueStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '24px',
  fontWeight: 700,
  color: '#818cf8',
};

const statLabelStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.7,
  textTransform: 'uppercase',
};

const orchestraContainerStyle: React.CSSProperties = {
  minHeight: '500px',
};

const stageViewStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '24px',
};

const tierSectionStyle: React.CSSProperties = {};

const tierHeaderStyle: React.CSSProperties = {
  marginBottom: '12px',
};

const tierBadgeStyle: React.CSSProperties = {
  fontSize: '11px',
  padding: '6px 12px',
  borderRadius: '20px',
  fontWeight: 600,
};

const agentsRowStyle: React.CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: '16px',
};

const agentCardStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.03)',
  border: '2px solid',
  borderRadius: '16px',
  padding: '16px',
  width: '200px',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
};

const agentHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '12px',
};

const agentIconStyle: React.CSSProperties = {
  fontSize: '24px',
};

const agentStatusStyle: React.CSSProperties = {
  fontSize: '16px',
};

const agentNameStyle: React.CSSProperties = {
  fontSize: '14px',
  fontWeight: 600,
  marginBottom: '8px',
};

const agentTaskStyle: React.CSSProperties = {
  fontSize: '12px',
  opacity: 0.7,
  marginBottom: '12px',
};

const progressContainerStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
};

const progressBarStyle: React.CSSProperties = {
  flex: 1,
  height: '6px',
  background: 'rgba(255, 255, 255, 0.1)',
  borderRadius: '3px',
  overflow: 'hidden',
};

const progressFillStyle: React.CSSProperties = {
  height: '100%',
  borderRadius: '3px',
  transition: 'width 0.5s ease',
};

const progressTextStyle: React.CSSProperties = {
  fontSize: '11px',
  fontWeight: 600,
  minWidth: '35px',
};

const notesStyle: React.CSSProperties = {
  marginTop: '12px',
  paddingTop: '12px',
  borderTop: '1px solid rgba(255, 255, 255, 0.1)',
};

const noteStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.7,
  marginBottom: '4px',
};

const dependenciesStyle: React.CSSProperties = {
  marginBottom: '8px',
};

const dependencyLabelStyle: React.CSSProperties = {
  fontSize: '10px',
  opacity: 0.6,
  display: 'block',
  marginBottom: '4px',
};

const dependencyBadgeStyle: React.CSSProperties = {
  fontSize: '10px',
  background: 'rgba(255, 255, 255, 0.1)',
  padding: '2px 8px',
  borderRadius: '4px',
  marginRight: '4px',
};

const scheduledTimeStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.6,
  marginBottom: '8px',
};

const graphViewStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  minHeight: '400px',
};

const graphContainerStyle: React.CSSProperties = {
  width: '100%',
};

const graphSvgStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.02)',
  borderRadius: '12px',
};

const graphLegendStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'center',
  gap: '24px',
  marginTop: '16px',
};

const legendItemStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  fontSize: '12px',
  opacity: 0.8,
};

const legendLineStyle: React.CSSProperties = {
  width: '30px',
  height: '2px',
  background: 'rgba(255, 255, 255, 0.2)',
  borderTop: '2px dashed rgba(255, 255, 255, 0.4)',
};

const legendCircleStyle: React.CSSProperties = {
  width: '12px',
  height: '12px',
  borderRadius: '50%',
  background: '#6366f1',
};

const scoreViewStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.02)',
  borderRadius: '16px',
  padding: '24px',
};

const scoreHeaderStyle: React.CSSProperties = {
  textAlign: 'center',
  marginBottom: '24px',
  paddingBottom: '16px',
  borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
};

const scoreTitleStyle: React.CSSProperties = {
  fontSize: '20px',
  fontWeight: 700,
  marginBottom: '8px',
  fontFamily: 'Georgia, serif',
  fontStyle: 'italic',
};

const scoreMetaStyle: React.CSSProperties = {
  fontSize: '13px',
  opacity: 0.7,
  display: 'flex',
  justifyContent: 'center',
  gap: '12px',
};

const scoreContentStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '16px',
};

const scoreLineStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '16px',
  padding: '12px',
  background: 'rgba(255, 255, 255, 0.03)',
  borderRadius: '8px',
};

const scoreAgentNameStyle: React.CSSProperties = {
  width: '180px',
  fontSize: '13px',
  fontWeight: 600,
};

const scoreTaskStyle: React.CSSProperties = {
  flex: 1,
  fontSize: '12px',
  opacity: 0.8,
};

const scoreStatusStyle: React.CSSProperties = {
  fontSize: '16px',
};

const scoreBarStyle: React.CSSProperties = {
  width: '200px',
  display: 'flex',
  gap: '2px',
  color: '#fbbf24',
};

const scoreNoteStyle: React.CSSProperties = {
  fontSize: '14px',
};

const modalOverlayStyle: React.CSSProperties = {
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  background: 'rgba(0, 0, 0, 0.7)',
  backdropFilter: 'blur(5px)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 1000,
};

const modalStyle: React.CSSProperties = {
  background: 'linear-gradient(135deg, #1e293b, #0f172a)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '20px',
  padding: '24px',
  width: '90%',
  maxWidth: '500px',
  maxHeight: '80vh',
  overflow: 'auto',
};

const modalHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '20px',
};

const modalIconStyle: React.CSSProperties = {
  fontSize: '24px',
  marginRight: '8px',
};

const modalNameStyle: React.CSSProperties = {
  fontSize: '18px',
  fontWeight: 700,
  marginRight: '12px',
};

const modalTierBadgeStyle: React.CSSProperties = {
  fontSize: '11px',
  padding: '4px 10px',
  borderRadius: '20px',
  fontWeight: 600,
};

const closeButtonStyle: React.CSSProperties = {
  background: 'none',
  border: 'none',
  color: '#f8fafc',
  fontSize: '20px',
  cursor: 'pointer',
  opacity: 0.6,
};

const modalContentStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '16px',
};

const modalTaskStyle: React.CSSProperties = {
  fontSize: '16px',
  fontWeight: 600,
  color: '#818cf8',
};

const modalProgressStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
};

const modalProgressBarStyle: React.CSSProperties = {
  flex: 1,
  height: '10px',
  background: 'rgba(255, 255, 255, 0.1)',
  borderRadius: '5px',
  overflow: 'hidden',
};

const modalProgressFillStyle: React.CSSProperties = {
  height: '100%',
  borderRadius: '5px',
  transition: 'width 0.5s ease',
};

const modalProgressTextStyle: React.CSSProperties = {
  fontSize: '14px',
  fontWeight: 600,
  minWidth: '40px',
};

const modalStatsStyle: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(3, 1fr)',
  gap: '12px',
};

const modalStatItemStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.05)',
  padding: '12px',
  borderRadius: '8px',
  textAlign: 'center',
};

const modalStatLabelStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.6,
  display: 'block',
  marginBottom: '4px',
};

const modalStatValueStyle: React.CSSProperties = {
  fontSize: '14px',
  fontWeight: 600,
};

const modalNotesStyle: React.CSSProperties = {};

const modalNotesTitleStyle: React.CSSProperties = {
  fontSize: '13px',
  fontWeight: 600,
  marginBottom: '8px',
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
  opacity: 0.7,
};

const modalNoteStyle: React.CSSProperties = {
  fontSize: '13px',
  padding: '8px',
  background: 'rgba(255, 255, 255, 0.05)',
  borderRadius: '6px',
  marginBottom: '6px',
};

const modalDepsStyle: React.CSSProperties = {};

const modalDepsTitleStyle: React.CSSProperties = {
  fontSize: '13px',
  fontWeight: 600,
  marginBottom: '8px',
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
  opacity: 0.7,
};

const modalDepItemStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '8px',
  background: 'rgba(255, 255, 255, 0.05)',
  borderRadius: '6px',
  marginBottom: '6px',
  fontSize: '13px',
};

const modalDepStatusStyle: React.CSSProperties = {
  fontSize: '14px',
};

export default AgentOrchestra;
