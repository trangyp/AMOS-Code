/**
 * AMOS Background Agents Component
 *
 * #1 on RedMonk 2025 "10 Things Developers Want"
 *
 * The promise of "fire and forget" has captured the developer imagination.
 * Developers want to queue up tasks, let agents work in the background
 * or even overnight, and return to review completed pull requests.
 *
 * As Addy Osmani writes: "Imagine coming into work to find overnight AI PRs
 * for all the refactoring tasks you queued up – ready for your review."
 *
 * Simon Willison's "parallel coding agent lifestyle" - supervise multiple
 * AI "developers" working simultaneously rather than being tethered to a
 * single synchronous assistant.
 *
 * Features:
 * - Task queue management
 * - Parallel agent orchestration
 * - Fire-and-forget task submission
 * - Progress tracking for long-running tasks
 * - Results/PR review interface
 * - Agent performance metrics
 */

import React, { useState, useEffect } from 'react';

// Agent Types
interface Agent {
  id: string;
  name: string;
  status: 'idle' | 'working' | 'paused' | 'error' | 'completed';
  currentTask?: string;
  progress: number;
  startTime?: string;
  estimatedCompletion?: string;
  workspace: string;
  gitBranch: string;
  commits: number;
  filesModified: number;
  linesChanged: number;
}

interface Task {
  id: string;
  title: string;
  description: string;
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  agentId?: string;
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
  estimatedDuration: number; // minutes
  progress: number;
  result?: {
    prUrl?: string;
    summary: string;
    filesChanged: string[];
    commits: number;
  };
  tags: string[];
}

// Mock Data
const MOCK_AGENTS: Agent[] = [
  {
    id: 'agent-1',
    name: 'Refactoring Agent',
    status: 'working',
    currentTask: 'Extract utility functions from auth module',
    progress: 65,
    startTime: new Date(Date.now() - 3600000).toISOString(),
    estimatedCompletion: new Date(Date.now() + 1800000).toISOString(),
    workspace: 'worktree-refactor-1',
    gitBranch: 'amos/refactor/auth-utils',
    commits: 3,
    filesModified: 12,
    linesChanged: 450,
  },
  {
    id: 'agent-2',
    name: 'Test Writer',
    status: 'working',
    currentTask: 'Generate unit tests for payment service',
    progress: 40,
    startTime: new Date(Date.now() - 2400000).toISOString(),
    estimatedCompletion: new Date(Date.now() + 3600000).toISOString(),
    workspace: 'worktree-tests-2',
    gitBranch: 'amos/tests/payment-coverage',
    commits: 1,
    filesModified: 8,
    linesChanged: 320,
  },
  {
    id: 'agent-3',
    name: 'Documentation Agent',
    status: 'idle',
    progress: 0,
    workspace: 'worktree-docs-3',
    gitBranch: 'amos/docs/api-reference',
    commits: 0,
    filesModified: 0,
    linesChanged: 0,
  },
  {
    id: 'agent-4',
    name: 'Security Auditor',
    status: 'completed',
    currentTask: 'Audit dependencies for vulnerabilities',
    progress: 100,
    startTime: new Date(Date.now() - 7200000).toISOString(),
    completedAt: new Date(Date.now() - 600000).toISOString(),
    workspace: 'worktree-security-4',
    gitBranch: 'amos/security/audit-fixes',
    commits: 2,
    filesModified: 5,
    linesChanged: 89,
  },
];

const MOCK_TASKS: Task[] = [
  {
    id: 'task-1',
    title: 'Refactor authentication module',
    description: 'Extract utility functions, improve error handling, add type safety',
    status: 'running',
    priority: 'high',
    agentId: 'agent-1',
    createdAt: new Date(Date.now() - 7200000).toISOString(),
    startedAt: new Date(Date.now() - 3600000).toISOString(),
    estimatedDuration: 120,
    progress: 65,
    tags: ['refactoring', 'auth', 'typescript'],
  },
  {
    id: 'task-2',
    title: 'Generate comprehensive test suite',
    description: 'Create unit tests for payment service, aiming for 80% coverage',
    status: 'running',
    priority: 'medium',
    agentId: 'agent-2',
    createdAt: new Date(Date.now() - 6000000).toISOString(),
    startedAt: new Date(Date.now() - 2400000).toISOString(),
    estimatedDuration: 180,
    progress: 40,
    tags: ['testing', 'payment', 'jest'],
  },
  {
    id: 'task-3',
    title: 'Update API documentation',
    description: 'Refresh OpenAPI specs, add examples, improve descriptions',
    status: 'queued',
    priority: 'low',
    createdAt: new Date(Date.now() - 3600000).toISOString(),
    estimatedDuration: 90,
    progress: 0,
    tags: ['documentation', 'openapi'],
  },
  {
    id: 'task-4',
    title: 'Security audit and dependency updates',
    description: 'Run security audit, update vulnerable dependencies, create PR',
    status: 'completed',
    priority: 'urgent',
    agentId: 'agent-4',
    createdAt: new Date(Date.now() - 10800000).toISOString(),
    startedAt: new Date(Date.now() - 7200000).toISOString(),
    completedAt: new Date(Date.now() - 600000).toISOString(),
    estimatedDuration: 120,
    progress: 100,
    result: {
      prUrl: 'https://github.com/trangyp/AMOS-Code/pull/42',
      summary: 'Fixed 3 critical vulnerabilities, updated 12 dependencies',
      filesChanged: ['package.json', 'package-lock.json', 'requirements.txt'],
      commits: 2,
    },
    tags: ['security', 'dependencies'],
  },
  {
    id: 'task-5',
    title: 'Migrate to new database schema',
    description: 'Update all queries to use new schema, create migration script',
    status: 'queued',
    priority: 'high',
    createdAt: new Date(Date.now() - 1800000).toISOString(),
    estimatedDuration: 240,
    progress: 0,
    tags: ['database', 'migration', 'sql'],
  },
];

export const BackgroundAgents: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>(MOCK_AGENTS);
  const [tasks, setTasks] = useState<Task[]>(MOCK_TASKS);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [showNewTaskDialog, setShowNewTaskDialog] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDescription, setNewTaskDescription] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState<'low' | 'medium' | 'high' | 'urgent'>('medium');
  const [filter, setFilter] = useState<'all' | 'running' | 'queued' | 'completed'>('all');

  // Stats
  const activeAgents = agents.filter(a => a.status === 'working').length;
  const completedTasks = tasks.filter(t => t.status === 'completed').length;
  const queuedTasks = tasks.filter(t => t.status === 'queued').length;
  const totalProgress = tasks.reduce((sum, t) => sum + t.progress, 0) / tasks.length;

  // Filter tasks
  const filteredTasks = filter === 'all'
    ? tasks
    : tasks.filter(t => t.status === filter);

  // Create new task
  const createTask = () => {
    if (!newTaskTitle) return;

    const newTask: Task = {
      id: `task-${Date.now()}`,
      title: newTaskTitle,
      description: newTaskDescription,
      status: 'queued',
      priority: newTaskPriority,
      createdAt: new Date().toISOString(),
      estimatedDuration: 120,
      progress: 0,
      tags: [],
    };

    setTasks(prev => [newTask, ...prev]);
    setShowNewTaskDialog(false);
    setNewTaskTitle('');
    setNewTaskDescription('');
  };

  // Cancel task
  const cancelTask = (taskId: string) => {
    setTasks(prev => prev.map(t =>
      t.id === taskId ? { ...t, status: 'cancelled' as const } : t
    ));
  };

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'working':
      case 'running': return '#3b82f6';
      case 'completed': return '#10b981';
      case 'queued': return '#f59e0b';
      case 'failed':
      case 'error': return '#ef4444';
      case 'idle': return '#6b7280';
      default: return '#6b7280';
    }
  };

  // Get priority color
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return '#ef4444';
      case 'high': return '#f59e0b';
      case 'medium': return '#3b82f6';
      case 'low': return '#6b7280';
      default: return '#6b7280';
    }
  };

  // Format duration
  const formatDuration = (minutes: number) => {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  };

  // Format time ago
  const formatTimeAgo = (date: string) => {
    const seconds = Math.floor((Date.now() - new Date(date).getTime()) / 1000);
    if (seconds < 60) return 'just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  return (
    <div style={containerStyle}>
      {/* Header */}
      <div style={headerStyle}>
        <div>
          <h3 style={titleStyle}>🚀 Background Agents</h3>
          <p style={subtitleStyle}>
            Fire-and-forget task execution. Wake up to completed PRs.
          </p>
        </div>
        <div style={statsContainerStyle}>
          <div style={statBoxStyle}>
            <span style={statNumberStyle}>{activeAgents}</span>
            <span style={statLabelStyle}>Active</span>
          </div>
          <div style={statBoxStyle}>
            <span style={statNumberStyle}>{completedTasks}</span>
            <span style={statLabelStyle}>Done</span>
          </div>
          <div style={statBoxStyle}>
            <span style={statNumberStyle}>{queuedTasks}</span>
            <span style={statLabelStyle}>Queued</span>
          </div>
          <div style={statBoxStyle}>
            <span style={statNumberStyle}>{Math.round(totalProgress)}%</span>
            <span style={statLabelStyle}>Progress</span>
          </div>
        </div>
      </div>

      {/* Quote Banner */}
      <div style={quoteBannerStyle}>
        <em>"Imagine coming into work to find overnight AI PRs for all the refactoring tasks you queued up – ready for your review."</em>
        <span style={quoteAuthorStyle}>— Addy Osmani, 2025</span>
      </div>

      {/* Active Agents */}
      <div style={sectionStyle}>
        <h4 style={sectionTitleStyle}>Active Agents</h4>
        <div style={agentsGridStyle}>
          {agents.map(agent => (
            <div
              key={agent.id}
              style={{
                ...agentCardStyle,
                borderColor: getStatusColor(agent.status),
              }}
            >
              <div style={agentHeaderStyle}>
                <div>
                  <div style={agentNameStyle}>{agent.name}</div>
                  <div style={agentStatusStyle}>
                    <span style={{ color: getStatusColor(agent.status) }}>●</span>
                    {' '}{agent.status}
                  </div>
                </div>
                <div style={agentStatsStyle}>
                  <div style={agentStatStyle}>{agent.commits} commits</div>
                  <div style={agentStatStyle}>{agent.filesModified} files</div>
                </div>
              </div>

              {agent.currentTask && (
                <div style={currentTaskStyle}>
                  <div style={taskLabelStyle}>Current Task:</div>
                  <div style={taskValueStyle}>{agent.currentTask}</div>
                </div>
              )}

              {agent.status === 'working' && (
                <>
                  <div style={progressBarContainerStyle}>
                    <div
                      style={{
                        ...progressBarStyle,
                        width: `${agent.progress}%`,
                        backgroundColor: getStatusColor(agent.status),
                      }}
                    />
                  </div>
                  <div style={progressTextStyle}>{agent.progress}% complete</div>
                </>
              )}

              <div style={workspaceStyle}>
                <span style={workspaceLabelStyle}>Branch:</span>
                <code style={branchCodeStyle}>{agent.gitBranch}</code>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Task Queue */}
      <div style={sectionStyle}>
        <div style={taskQueueHeaderStyle}>
          <h4 style={sectionTitleStyle}>Task Queue</h4>
          <div style={filterButtonsStyle}>
            {(['all', 'queued', 'running', 'completed'] as const).map(f => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                style={{
                  ...filterButtonStyle,
                  backgroundColor: filter === f ? 'rgba(99, 102, 241, 0.3)' : 'rgba(255,255,255,0.05)',
                }}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div style={taskListStyle}>
          {filteredTasks.map(task => (
            <div
              key={task.id}
              style={taskCardStyle}
              onClick={() => setSelectedTask(task)}
            >
              <div style={taskHeaderStyle}>
                <div>
                  <div style={taskTitleStyle}>{task.title}</div>
                  <div style={taskDescriptionStyle}>{task.description}</div>
                  <div style={taskMetaStyle}>
                    <span style={{
                      ...priorityBadgeStyle,
                      backgroundColor: `${getPriorityColor(task.priority)}20`,
                      color: getPriorityColor(task.priority),
                    }}>
                      {task.priority}
                    </span>
                    <span style={timeStyle}>{formatTimeAgo(task.createdAt)}</span>
                    {task.estimatedDuration > 0 && (
                      <span style={durationStyle}>
                        ⏱️ {formatDuration(task.estimatedDuration)}
                      </span>
                    )}
                  </div>
                </div>
                <div style={taskActionsStyle}>
                  {task.status === 'running' && (
                    <div style={taskProgressStyle}>
                      <div style={miniProgressContainerStyle}>
                        <div
                          style={{
                            ...miniProgressBarStyle,
                            width: `${task.progress}%`,
                          }}
                        />
                      </div>
                      <span style={miniProgressTextStyle}>{task.progress}%</span>
                    </div>
                  )}
                  {task.status === 'completed' && task.result?.prUrl && (
                    <a
                      href={task.result.prUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={prLinkStyle}
                    >
                      View PR →
                    </a>
                  )}
                  {task.status === 'queued' && (
                    <button
                      onClick={(e) => { e.stopPropagation(); cancelTask(task.id); }}
                      style={cancelButtonStyle}
                    >
                      Cancel
                    </button>
                  )}
                </div>
              </div>

              {task.tags.length > 0 && (
                <div style={tagsStyle}>
                  {task.tags.map(tag => (
                    <span key={tag} style={tagStyle}>{tag}</span>
                  ))}
                </div>
              )}

              {task.status === 'completed' && task.result && (
                <div style={resultPreviewStyle}>
                  <div style={resultSummaryStyle}>{task.result.summary}</div>
                  <div style={resultStatsStyle}>
                    <span>{task.result.commits} commits</span>
                    <span>•</span>
                    <span>{task.result.filesChanged.length} files</span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* New Task Button */}
      <button onClick={() => setShowNewTaskDialog(true)} style={newTaskButtonStyle}>
        + Queue New Task
      </button>

      {/* New Task Dialog */}
      {showNewTaskDialog && (
        <div style={dialogOverlayStyle}>
          <div style={dialogStyle}>
            <h4 style={dialogTitleStyle}>Queue Background Task</h4>

            <div style={formGroupStyle}>
              <label style={labelStyle}>Task Title</label>
              <input
                type="text"
                value={newTaskTitle}
                onChange={(e) => setNewTaskTitle(e.target.value)}
                placeholder="e.g., Refactor authentication module"
                style={inputStyle}
              />
            </div>

            <div style={formGroupStyle}>
              <label style={labelStyle}>Description</label>
              <textarea
                value={newTaskDescription}
                onChange={(e) => setNewTaskDescription(e.target.value)}
                placeholder="Describe what the agent should do..."
                style={textareaStyle}
              />
            </div>

            <div style={formGroupStyle}>
              <label style={labelStyle}>Priority</label>
              <select
                value={newTaskPriority}
                onChange={(e) => setNewTaskPriority(e.target.value as any)}
                style={selectStyle}
              >
                <option value="low">Low - When available</option>
                <option value="medium">Medium - Normal queue</option>
                <option value="high">High - Prioritize</option>
                <option value="urgent">Urgent - Start immediately</option>
              </select>
            </div>

            <div style={dialogButtonsStyle}>
              <button onClick={() => setShowNewTaskDialog(false)} style={cancelButtonStyle}>
                Cancel
              </button>
              <button onClick={createTask} style={submitButtonStyle}>
                Queue Task
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Task Detail Panel */}
      {selectedTask && (
        <div style={detailOverlayStyle} onClick={() => setSelectedTask(null)}>
          <div style={detailPanelStyle} onClick={(e) => e.stopPropagation()}>
            <div style={detailHeaderStyle}>
              <h4 style={detailTitleStyle}>{selectedTask.title}</h4>
              <button onClick={() => setSelectedTask(null)} style={closeButtonStyle}>✕</button>
            </div>

            <div style={detailContentStyle}>
              <p style={detailDescriptionStyle}>{selectedTask.description}</p>

              <div style={detailStatsStyle}>
                <div style={detailStatStyle}>
                  <span style={detailStatLabelStyle}>Status</span>
                  <span style={{
                    ...detailStatValueStyle,
                    color: getStatusColor(selectedTask.status),
                  }}>
                    {selectedTask.status}
                  </span>
                </div>
                <div style={detailStatStyle}>
                  <span style={detailStatLabelStyle}>Priority</span>
                  <span style={{
                    ...detailStatValueStyle,
                    color: getPriorityColor(selectedTask.priority),
                  }}>
                    {selectedTask.priority}
                  </span>
                </div>
                <div style={detailStatStyle}>
                  <span style={detailStatLabelStyle}>Progress</span>
                  <span style={detailStatValueStyle}>{selectedTask.progress}%</span>
                </div>
              </div>

              {selectedTask.result && (
                <div style={detailResultStyle}>
                  <h5 style={detailResultTitleStyle}>Result</h5>
                  <p style={detailResultSummaryStyle}>{selectedTask.result.summary}</p>

                  {selectedTask.result.prUrl && (
                    <a
                      href={selectedTask.result.prUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={detailPrLinkStyle}
                    >
                      View Pull Request →
                    </a>
                  )}

                  <div style={detailFilesStyle}>
                    <h6 style={detailFilesTitleStyle}>Files Changed</h6>
                    <ul style={detailFilesListStyle}>
                      {selectedTask.result.filesChanged.map((file, idx) => (
                        <li key={idx} style={detailFileItemStyle}>{file}</li>
                      ))}
                    </ul>
                  </div>
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
  maxWidth: '900px',
  fontFamily: 'Inter, system-ui, sans-serif',
  color: '#f8fafc',
  boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
};

const headerStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'flex-start',
  marginBottom: '20px',
  flexWrap: 'wrap',
  gap: '16px',
};

const titleStyle: React.CSSProperties = {
  fontSize: '22px',
  fontWeight: 700,
  margin: '0 0 4px 0',
  background: 'linear-gradient(90deg, #6366f1, #a855f7)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
};

const subtitleStyle: React.CSSProperties = {
  fontSize: '13px',
  opacity: 0.7,
  margin: 0,
};

const statsContainerStyle: React.CSSProperties = {
  display: 'flex',
  gap: '12px',
};

const statBoxStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.05)',
  padding: '12px 16px',
  borderRadius: '12px',
  textAlign: 'center',
  minWidth: '70px',
};

const statNumberStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '20px',
  fontWeight: 700,
  color: '#818cf8',
};

const statLabelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '11px',
  opacity: 0.7,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
  marginTop: '4px',
};

const quoteBannerStyle: React.CSSProperties = {
  background: 'rgba(59, 130, 246, 0.1)',
  border: '1px solid rgba(59, 130, 246, 0.3)',
  borderRadius: '12px',
  padding: '16px 20px',
  fontSize: '14px',
  color: '#60a5fa',
  marginBottom: '24px',
  lineHeight: 1.5,
};

const quoteAuthorStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '12px',
  opacity: 0.7,
  marginTop: '8px',
  fontStyle: 'normal',
};

const sectionStyle: React.CSSProperties = {
  marginBottom: '24px',
};

const sectionTitleStyle: React.CSSProperties = {
  fontSize: '16px',
  fontWeight: 600,
  margin: '0 0 16px 0',
};

const agentsGridStyle: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
  gap: '16px',
};

const agentCardStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.03)',
  border: '2px solid',
  borderRadius: '16px',
  padding: '16px',
  transition: 'all 0.3s ease',
};

const agentHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'flex-start',
  marginBottom: '12px',
};

const agentNameStyle: React.CSSProperties = {
  fontWeight: 600,
  fontSize: '15px',
  marginBottom: '4px',
};

const agentStatusStyle: React.CSSProperties = {
  fontSize: '12px',
  opacity: 0.8,
  textTransform: 'capitalize',
};

const agentStatsStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '2px',
  alignItems: 'flex-end',
};

const agentStatStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.6,
};

const currentTaskStyle: React.CSSProperties = {
  marginBottom: '12px',
};

const taskLabelStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.6,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
  marginBottom: '4px',
};

const taskValueStyle: React.CSSProperties = {
  fontSize: '13px',
  lineHeight: 1.4,
};

const progressBarContainerStyle: React.CSSProperties = {
  height: '6px',
  background: 'rgba(255, 255, 255, 0.1)',
  borderRadius: '3px',
  overflow: 'hidden',
  marginBottom: '6px',
};

const progressBarStyle: React.CSSProperties = {
  height: '100%',
  borderRadius: '3px',
  transition: 'width 0.3s ease',
};

const progressTextStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.6,
};

const workspaceStyle: React.CSSProperties = {
  marginTop: '12px',
  paddingTop: '12px',
  borderTop: '1px solid rgba(255, 255, 255, 0.1)',
};

const workspaceLabelStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.6,
  marginRight: '8px',
};

const branchCodeStyle: React.CSSProperties = {
  fontSize: '12px',
  background: 'rgba(99, 102, 241, 0.1)',
  padding: '4px 8px',
  borderRadius: '6px',
  fontFamily: 'JetBrains Mono, monospace',
};

const taskQueueHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '16px',
  flexWrap: 'wrap',
  gap: '12px',
};

const filterButtonsStyle: React.CSSProperties = {
  display: 'flex',
  gap: '8px',
};

const filterButtonStyle: React.CSSProperties = {
  padding: '6px 12px',
  borderRadius: '8px',
  border: 'none',
  fontSize: '12px',
  cursor: 'pointer',
  color: '#f8fafc',
  transition: 'all 0.3s ease',
};

const taskListStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '12px',
};

const taskCardStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.03)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '12px',
  padding: '16px',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
};

const taskHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'flex-start',
  marginBottom: '8px',
};

const taskTitleStyle: React.CSSProperties = {
  fontWeight: 600,
  fontSize: '14px',
  marginBottom: '4px',
};

const taskDescriptionStyle: React.CSSProperties = {
  fontSize: '12px',
  opacity: 0.7,
  marginBottom: '8px',
  lineHeight: 1.4,
};

const taskMetaStyle: React.CSSProperties = {
  display: 'flex',
  gap: '12px',
  alignItems: 'center',
};

const priorityBadgeStyle: React.CSSProperties = {
  fontSize: '10px',
  padding: '2px 8px',
  borderRadius: '4px',
  fontWeight: 600,
  textTransform: 'uppercase',
};

const timeStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.5,
};

const durationStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.6,
};

const taskActionsStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'flex-end',
  gap: '8px',
};

const taskProgressStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
};

const miniProgressContainerStyle: React.CSSProperties = {
  width: '60px',
  height: '4px',
  background: 'rgba(255, 255, 255, 0.1)',
  borderRadius: '2px',
  overflow: 'hidden',
};

const miniProgressBarStyle: React.CSSProperties = {
  height: '100%',
  background: '#3b82f6',
  borderRadius: '2px',
  transition: 'width 0.3s ease',
};

const miniProgressTextStyle: React.CSSProperties = {
  fontSize: '11px',
  fontWeight: 600,
  color: '#3b82f6',
};

const prLinkStyle: React.CSSProperties = {
  fontSize: '12px',
  color: '#10b981',
  textDecoration: 'none',
  fontWeight: 600,
};

const cancelButtonStyle: React.CSSProperties = {
  background: 'rgba(239, 68, 68, 0.2)',
  color: '#ef4444',
  border: 'none',
  padding: '4px 12px',
  borderRadius: '6px',
  fontSize: '11px',
  cursor: 'pointer',
};

const tagsStyle: React.CSSProperties = {
  display: 'flex',
  gap: '6px',
  flexWrap: 'wrap',
  marginTop: '8px',
};

const tagStyle: React.CSSProperties = {
  fontSize: '10px',
  background: 'rgba(99, 102, 241, 0.15)',
  color: '#818cf8',
  padding: '2px 8px',
  borderRadius: '4px',
};

const resultPreviewStyle: React.CSSProperties = {
  marginTop: '12px',
  padding: '12px',
  background: 'rgba(16, 185, 129, 0.1)',
  border: '1px solid rgba(16, 185, 129, 0.3)',
  borderRadius: '8px',
};

const resultSummaryStyle: React.CSSProperties = {
  fontSize: '12px',
  color: '#10b981',
  marginBottom: '4px',
};

const resultStatsStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.6,
  display: 'flex',
  gap: '8px',
};

const newTaskButtonStyle: React.CSSProperties = {
  width: '100%',
  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
  border: 'none',
  color: 'white',
  padding: '14px',
  borderRadius: '12px',
  fontSize: '14px',
  fontWeight: 600,
  cursor: 'pointer',
  transition: 'all 0.3s ease',
};

const dialogOverlayStyle: React.CSSProperties = {
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

const dialogStyle: React.CSSProperties = {
  background: 'linear-gradient(135deg, #1e293b, #0f172a)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '20px',
  padding: '24px',
  width: '90%',
  maxWidth: '500px',
  maxHeight: '80vh',
  overflow: 'auto',
};

const dialogTitleStyle: React.CSSProperties = {
  fontSize: '18px',
  fontWeight: 700,
  margin: '0 0 20px 0',
};

const formGroupStyle: React.CSSProperties = {
  marginBottom: '16px',
};

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '12px',
  fontWeight: 600,
  marginBottom: '6px',
  opacity: 0.8,
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '10px 14px',
  background: 'rgba(255, 255, 255, 0.05)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '10px',
  color: '#f8fafc',
  fontSize: '14px',
  outline: 'none',
};

const textareaStyle: React.CSSProperties = {
  width: '100%',
  padding: '10px 14px',
  background: 'rgba(255, 255, 255, 0.05)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '10px',
  color: '#f8fafc',
  fontSize: '14px',
  outline: 'none',
  minHeight: '100px',
  resize: 'vertical',
};

const selectStyle: React.CSSProperties = {
  width: '100%',
  padding: '10px 14px',
  background: 'rgba(255, 255, 255, 0.05)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '10px',
  color: '#f8fafc',
  fontSize: '14px',
  outline: 'none',
  cursor: 'pointer',
};

const dialogButtonsStyle: React.CSSProperties = {
  display: 'flex',
  gap: '12px',
  marginTop: '20px',
};

const cancelButtonStyle: React.CSSProperties = {
  flex: 1,
  background: 'rgba(255, 255, 255, 0.05)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  color: '#f8fafc',
  padding: '10px',
  borderRadius: '10px',
  cursor: 'pointer',
  fontWeight: 600,
};

const submitButtonStyle: React.CSSProperties = {
  flex: 1,
  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
  border: 'none',
  color: 'white',
  padding: '10px',
  borderRadius: '10px',
  cursor: 'pointer',
  fontWeight: 600,
};

const detailOverlayStyle: React.CSSProperties = {
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

const detailPanelStyle: React.CSSProperties = {
  background: 'linear-gradient(135deg, #1e293b, #0f172a)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '20px',
  padding: '24px',
  width: '90%',
  maxWidth: '600px',
  maxHeight: '80vh',
  overflow: 'auto',
};

const detailHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '20px',
};

const detailTitleStyle: React.CSSProperties = {
  fontSize: '18px',
  fontWeight: 700,
  margin: 0,
};

const closeButtonStyle: React.CSSProperties = {
  background: 'none',
  border: 'none',
  color: '#f8fafc',
  fontSize: '20px',
  cursor: 'pointer',
  opacity: 0.6,
};

const detailContentStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '20px',
};

const detailDescriptionStyle: React.CSSProperties = {
  fontSize: '14px',
  lineHeight: 1.6,
  opacity: 0.9,
};

const detailStatsStyle: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(3, 1fr)',
  gap: '16px',
};

const detailStatStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.05)',
  padding: '12px',
  borderRadius: '10px',
  textAlign: 'center',
};

const detailStatLabelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '11px',
  opacity: 0.6,
  marginBottom: '4px',
};

const detailStatValueStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '16px',
  fontWeight: 700,
};

const detailResultStyle: React.CSSProperties = {
  background: 'rgba(16, 185, 129, 0.1)',
  border: '1px solid rgba(16, 185, 129, 0.3)',
  borderRadius: '12px',
  padding: '16px',
};

const detailResultTitleStyle: React.CSSProperties = {
  fontSize: '14px',
  fontWeight: 600,
  margin: '0 0 12px 0',
  color: '#10b981',
};

const detailResultSummaryStyle: React.CSSProperties = {
  fontSize: '14px',
  marginBottom: '16px',
};

const detailPrLinkStyle: React.CSSProperties = {
  display: 'inline-block',
  background: 'linear-gradient(135deg, #10b981, #059669)',
  color: 'white',
  padding: '8px 16px',
  borderRadius: '8px',
  textDecoration: 'none',
  fontWeight: 600,
  marginBottom: '16px',
};

const detailFilesStyle: React.CSSProperties = {
  marginTop: '12px',
};

const detailFilesTitleStyle: React.CSSProperties = {
  fontSize: '12px',
  fontWeight: 600,
  margin: '0 0 8px 0',
  opacity: 0.8,
};

const detailFilesListStyle: React.CSSProperties = {
  listStyle: 'none',
  padding: 0,
  margin: 0,
  fontSize: '12px',
  fontFamily: 'JetBrains Mono, monospace',
};

const detailFileItemStyle: React.CSSProperties = {
  padding: '4px 0',
  borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
};

export default BackgroundAgents;
