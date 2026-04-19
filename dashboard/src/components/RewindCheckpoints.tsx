/**
 * AMOS /rewind Checkpoint System Component
 *
 * #9 on RedMonk 2025 "10 Things Developers Want"
 *
 * "Checkpoints would make Claude Code unstoppable" - Reddit r/ClaudeAI, 160+ comments
 *
 * Developer Problem: "When it's on the right track, it can make numerous files...
 * but when it goes wrong, it can be devastating" - GitHub feature request
 *
 * AMOS Solution: Native checkpoint system beyond git
 * - Automatic checkpoints every N actions
 * - Manual checkpoints with descriptions
 * - One-click rewind to any state
 * - Visual diff between checkpoints
 * - Branching timeline (experiment safely)
 *
 * Based on 2025 research from Claude Code feature requests and Cursor's implementation.
 */

import React, { useState } from 'react';

// Checkpoint Types
interface Checkpoint {
  id: string;
  timestamp: string;
  description: string;
  type: 'auto' | 'manual' | 'pre-action' | 'post-action';
  filesChanged: string[];
  linesAdded: number;
  linesRemoved: number;
  agentActions: string[];
  memorySnapshot: string[];
  tags: string[];
  isCurrent: boolean;
  branch?: string;
}

interface Branch {
  id: string;
  name: string;
  color: string;
  checkpoints: string[];
  createdAt: string;
  parentBranch?: string;
  parentCheckpoint?: string;
}

// Mock Data
const MOCK_CHECKPOINTS: Checkpoint[] = [
  {
    id: 'cp-1',
    timestamp: new Date(Date.now() - 86400000 * 2).toISOString(),
    description: 'Initial project setup complete',
    type: 'manual',
    filesChanged: ['README.md', 'package.json', '.gitignore'],
    linesAdded: 150,
    linesRemoved: 0,
    agentActions: ['Created project structure', 'Initialized git repo'],
    memorySnapshot: ['Project initialized', 'Tech stack: React + TypeScript'],
    tags: ['milestone', 'setup'],
    isCurrent: false,
    branch: 'main',
  },
  {
    id: 'cp-2',
    timestamp: new Date(Date.now() - 86400000).toISOString(),
    description: 'Before implementing auth system',
    type: 'pre-action',
    filesChanged: ['src/components/Login.tsx', 'src/utils/auth.ts'],
    linesAdded: 200,
    linesRemoved: 50,
    agentActions: ['Analyzed auth requirements', 'Created auth utilities'],
    memorySnapshot: ['Auth flow: JWT with refresh tokens', 'User model defined'],
    tags: ['auth', 'pre-change'],
    isCurrent: false,
    branch: 'main',
  },
  {
    id: 'cp-3',
    timestamp: new Date(Date.now() - 43200000).toISOString(),
    description: 'Auth system implemented successfully',
    type: 'post-action',
    filesChanged: ['src/components/Login.tsx', 'src/utils/auth.ts', 'src/hooks/useAuth.ts'],
    linesAdded: 350,
    linesRemoved: 20,
    agentActions: ['Implemented JWT auth', 'Added login/logout flows', 'Created useAuth hook'],
    memorySnapshot: ['Auth system complete', 'Tests passing'],
    tags: ['auth', 'milestone'],
    isCurrent: false,
    branch: 'main',
  },
  {
    id: 'cp-4',
    timestamp: new Date(Date.now() - 3600000 * 4).toISOString(),
    description: 'Auto-checkpoint: Before database migration',
    type: 'auto',
    filesChanged: ['src/db/schema.sql'],
    linesAdded: 50,
    linesRemoved: 0,
    agentActions: ['Analyzed schema changes needed'],
    memorySnapshot: ['Planning Users-Projects-Tasks schema'],
    tags: ['auto', 'database'],
    isCurrent: false,
    branch: 'main',
  },
  {
    id: 'cp-5',
    timestamp: new Date(Date.now() - 3600000 * 2).toISOString(),
    description: 'Working checkpoint: Dashboard UI progress',
    type: 'manual',
    filesChanged: ['src/components/Dashboard.tsx', 'src/styles/dashboard.css'],
    linesAdded: 180,
    linesRemoved: 30,
    agentActions: ['Created dashboard layout', 'Added Glassmorphism styling'],
    memorySnapshot: ['Dashboard 70% complete', 'Need to add charts next'],
    tags: ['ui', 'dashboard'],
    isCurrent: false,
    branch: 'main',
  },
  {
    id: 'cp-6',
    timestamp: new Date(Date.now() - 1800000).toISOString(),
    description: 'Current state - Background Agents implemented',
    type: 'manual',
    filesChanged: ['src/components/BackgroundAgents.tsx'],
    linesAdded: 600,
    linesRemoved: 0,
    agentActions: ['Implemented task queue UI', 'Added agent cards', 'Created progress tracking'],
    memorySnapshot: ['Background Agents complete', 'Ready for Persistent Memory'],
    tags: ['milestone', 'agents'],
    isCurrent: true,
    branch: 'main',
  },
];

const MOCK_BRANCHES: Branch[] = [
  {
    id: 'branch-main',
    name: 'main',
    color: '#3b82f6',
    checkpoints: ['cp-1', 'cp-2', 'cp-3', 'cp-4', 'cp-5', 'cp-6'],
    createdAt: new Date(Date.now() - 86400000 * 2).toISOString(),
  },
  {
    id: 'branch-experiment',
    name: 'experiment/new-ui',
    color: '#f59e0b',
    checkpoints: ['cp-5'],
    createdAt: new Date(Date.now() - 3600000 * 3).toISOString(),
    parentBranch: 'branch-main',
    parentCheckpoint: 'cp-5',
  },
];

export const RewindCheckpoints: React.FC = () => {
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>(MOCK_CHECKPOINTS);
  const [branches] = useState<Branch[]>(MOCK_BRANCHES);
  const [selectedCheckpoint, setSelectedCheckpoint] = useState<Checkpoint | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newCheckpointDesc, setNewCheckpointDesc] = useState('');
  const [activeBranch, setActiveBranch] = useState('branch-main');
  const [isRewinding, setIsRewinding] = useState(false);

  // Stats
  const totalCheckpoints = checkpoints.length;
  const autoCheckpoints = checkpoints.filter(c => c.type === 'auto').length;
  const currentBranch = branches.find(b => b.id === activeBranch);

  // Create new checkpoint
  const createCheckpoint = () => {
    if (!newCheckpointDesc) return;

    const newCheckpoint: Checkpoint = {
      id: `cp-${Date.now()}`,
      timestamp: new Date().toISOString(),
      description: newCheckpointDesc,
      type: 'manual',
      filesChanged: [],
      linesAdded: 0,
      linesRemoved: 0,
      agentActions: [],
      memorySnapshot: [],
      tags: ['manual'],
      isCurrent: true,
      branch: currentBranch?.name,
    };

    // Mark previous current as not current
    setCheckpoints(prev =>
      prev.map(c => c.isCurrent ? { ...c, isCurrent: false } : c)
        .concat(newCheckpoint)
    );

    setShowCreateDialog(false);
    setNewCheckpointDesc('');
  };

  // Rewind to checkpoint
  const rewindToCheckpoint = (checkpoint: Checkpoint) => {
    setIsRewinding(true);
    setSelectedCheckpoint(null);

    // Simulate rewind
    setTimeout(() => {
      setCheckpoints(prev => prev.map(c => ({
        ...c,
        isCurrent: c.id === checkpoint.id
      })));
      setIsRewinding(false);
    }, 2000);
  };

  // Format time
  const formatTime = (date: string) => {
    const d = new Date(date);
    return d.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Get type icon
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'auto': return '🤖';
      case 'manual': return '👤';
      case 'pre-action': return '⚡';
      case 'post-action': return '✓';
      default: return '📝';
    }
  };

  // Get type label
  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'auto': return 'Auto';
      case 'manual': return 'Manual';
      case 'pre-action': return 'Pre-action';
      case 'post-action': return 'Post-action';
      default: return type;
    }
  };

  return (
    <div style={containerStyle}>
      {/* Header */}
      <div style={headerStyle}>
        <div>
          <h3 style={titleStyle}>⏪ /rewind Checkpoints</h3>
          <p style={subtitleStyle}>
            Time-travel for your codebase. Never lose progress.
          </p>
        </div>
        <div style={statsContainerStyle}>
          <div style={statBoxStyle}>
            <span style={statNumberStyle}>{totalCheckpoints}</span>
            <span style={statLabelStyle}>Checkpoints</span>
          </div>
          <div style={statBoxStyle}>
            <span style={statNumberStyle}>{autoCheckpoints}</span>
            <span style={statLabelStyle}>Auto</span>
          </div>
          <div style={statBoxStyle}>
            <span style={statNumberStyle}>{branches.length}</span>
            <span style={statLabelStyle}>Branches</span>
          </div>
        </div>
      </div>

      {/* Quote Banner */}
      <div style={quoteBannerStyle}>
        <em>"Checkpoints would make Claude Code unstoppable. When it's on the right track,
        it can make numerous files... but when it goes wrong, it can be devastating."</em>
        <span style={quoteAuthorStyle}>— Developer community, 2025</span>
      </div>

      {/* Branch Selector */}
      <div style={branchSelectorStyle}>
        <span style={branchLabelStyle}>Active Timeline:</span>
        <div style={branchButtonsStyle}>
          {branches.map(branch => (
            <button
              key={branch.id}
              onClick={() => setActiveBranch(branch.id)}
              style={{
                ...branchButtonStyle,
                backgroundColor: activeBranch === branch.id ? branch.color : 'rgba(255,255,255,0.05)',
                borderColor: branch.color,
              }}
            >
              <span style={{ ...branchDotStyle, backgroundColor: branch.color }} />
              {branch.name}
            </button>
          ))}
        </div>
      </div>

      {/* Timeline */}
      <div style={timelineContainerStyle}>
        <div style={timelineLineStyle}>
          {currentBranch && (
            <div
              style={{
                ...timelineProgressStyle,
                backgroundColor: currentBranch.color,
              }}
            />
          )}
        </div>

        <div style={checkpointsListStyle}>
          {checkpoints
            .filter(c => currentBranch?.checkpoints.includes(c.id))
            .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
            .map((checkpoint) => (
              <div
                key={checkpoint.id}
                style={{
                  ...checkpointCardStyle,
                  borderColor: checkpoint.isCurrent ? '#10b981' : 'rgba(255,255,255,0.1)',
                  backgroundColor: checkpoint.isCurrent ? 'rgba(16, 185, 129, 0.1)' : 'rgba(255,255,255,0.03)',
                }}
                onClick={() => setSelectedCheckpoint(checkpoint)}
              >
                {/* Timeline dot */}
                <div
                  style={{
                    ...timelineDotStyle,
                    backgroundColor: checkpoint.isCurrent ? '#10b981' : (currentBranch?.color || '#6366f1'),
                    boxShadow: checkpoint.isCurrent ? '0 0 20px #10b981' : 'none',
                  }}
                />

                <div style={checkpointContentStyle}>
                  {/* Header */}
                  <div style={checkpointHeaderStyle}>
                    <div style={typeBadgeStyle}>
                      <span style={typeIconStyle}>{getTypeIcon(checkpoint.type)}</span>
                      <span>{getTypeLabel(checkpoint.type)}</span>
                    </div>
                    <span style={timestampStyle}>{formatTime(checkpoint.timestamp)}</span>
                  </div>

                  {/* Description */}
                  <div style={checkpointDescriptionStyle}>
                    {checkpoint.isCurrent && (
                      <span style={currentBadgeStyle}>CURRENT</span>
                    )}
                    {checkpoint.description}
                  </div>

                  {/* Stats */}
                  <div style={checkpointStatsStyle}>
                    <span style={filesChangedStyle}>
                      📁 {checkpoint.filesChanged.length} files
                    </span>
                    <span style={linesStyle}>
                      <span style={addedStyle}>+{checkpoint.linesAdded}</span>
                      {' / '}
                      <span style={removedStyle}>-{checkpoint.linesRemoved}</span>
                    </span>
                  </div>

                  {/* Tags */}
                  <div style={tagsStyle}>
                    {checkpoint.tags.map(tag => (
                      <span key={tag} style={tagStyle}>{tag}</span>
                    ))}
                  </div>

                  {/* Actions Preview */}
                  {checkpoint.agentActions.length > 0 && (
                    <div style={actionsPreviewStyle}>
                      {checkpoint.agentActions.slice(0, 2).map((action, i) => (
                        <div key={i} style={actionItemStyle}>• {action}</div>
                      ))}
                      {checkpoint.agentActions.length > 2 && (
                        <div style={moreActionsStyle}>
                          +{checkpoint.agentActions.length - 2} more actions
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Create Checkpoint Button */}
      <button onClick={() => setShowCreateDialog(true)} style={createButtonStyle}>
        + Create Checkpoint
      </button>

      {/* Checkpoint Detail Modal */}
      {selectedCheckpoint && (
        <div style={modalOverlayStyle} onClick={() => setSelectedCheckpoint(null)}>
          <div style={modalStyle} onClick={(e) => e.stopPropagation()}>
            <div style={modalHeaderStyle}>
              <div>
                <span style={{
                  ...modalTypeBadgeStyle,
                  backgroundColor: selectedCheckpoint.isCurrent ? 'rgba(16, 185, 129, 0.2)' : 'rgba(99, 102, 241, 0.2)',
                  color: selectedCheckpoint.isCurrent ? '#10b981' : '#818cf8',
                }}>
                  {getTypeIcon(selectedCheckpoint.type)} {getTypeLabel(selectedCheckpoint.type)}
                  {selectedCheckpoint.isCurrent && ' • CURRENT'}
                </span>
                <h4 style={modalTitleStyle}>{selectedCheckpoint.description}</h4>
                <p style={modalTimeStyle}>{formatTime(selectedCheckpoint.timestamp)}</p>
              </div>
              <button onClick={() => setSelectedCheckpoint(null)} style={closeButtonStyle}>✕</button>
            </div>

            <div style={modalContentStyle}>
              {/* Stats Grid */}
              <div style={modalStatsGridStyle}>
                <div style={modalStatItemStyle}>
                  <span style={modalStatLabelStyle}>Files Changed</span>
                  <span style={modalStatValueStyle}>{selectedCheckpoint.filesChanged.length}</span>
                </div>
                <div style={modalStatItemStyle}>
                  <span style={modalStatLabelStyle}>Lines Added</span>
                  <span style={{ ...modalStatValueStyle, color: '#10b981' }}>+{selectedCheckpoint.linesAdded}</span>
                </div>
                <div style={modalStatItemStyle}>
                  <span style={modalStatLabelStyle}>Lines Removed</span>
                  <span style={{ ...modalStatValueStyle, color: '#ef4444' }}>-{selectedCheckpoint.linesRemoved}</span>
                </div>
                <div style={modalStatItemStyle}>
                  <span style={modalStatLabelStyle}>Agent Actions</span>
                  <span style={modalStatValueStyle}>{selectedCheckpoint.agentActions.length}</span>
                </div>
              </div>

              {/* Files Changed */}
              <div style={sectionStyle}>
                <h5 style={sectionTitleStyle}>Files Changed</h5>
                <div style={filesListStyle}>
                  {selectedCheckpoint.filesChanged.map((file, i) => (
                    <div key={i} style={fileItemStyle}>{file}</div>
                  ))}
                </div>
              </div>

              {/* Agent Actions */}
              <div style={sectionStyle}>
                <h5 style={sectionTitleStyle}>Agent Actions</h5>
                <div style={actionsListStyle}>
                  {selectedCheckpoint.agentActions.map((action, i) => (
                    <div key={i} style={actionDetailStyle}>{i + 1}. {action}</div>
                  ))}
                </div>
              </div>

              {/* Memory Snapshot */}
              <div style={sectionStyle}>
                <h5 style={sectionTitleStyle}>Memory Snapshot</h5>
                <div style={memorySnapshotStyle}>
                  {selectedCheckpoint.memorySnapshot.map((mem, i) => (
                    <div key={i} style={memoryItemStyle}>🧠 {mem}</div>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div style={modalActionsStyle}>
                {!selectedCheckpoint.isCurrent && (
                  <button
                    onClick={() => rewindToCheckpoint(selectedCheckpoint)}
                    style={rewindButtonStyle}
                  >
                    ⏪ Rewind to This Checkpoint
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Checkpoint Dialog */}
      {showCreateDialog && (
        <div style={dialogOverlayStyle}>
          <div style={dialogStyle}>
            <h4 style={dialogTitleStyle}>Create Checkpoint</h4>
            <p style={dialogDescriptionStyle}>
              Save the current state of your project. You can return to this point at any time.
            </p>
            <input
              type="text"
              value={newCheckpointDesc}
              onChange={(e) => setNewCheckpointDesc(e.target.value)}
              placeholder="e.g., Before refactoring database layer"
              style={dialogInputStyle}
            />
            <div style={dialogButtonsStyle}>
              <button onClick={() => setShowCreateDialog(false)} style={dialogCancelStyle}>
                Cancel
              </button>
              <button onClick={createCheckpoint} style={dialogSubmitStyle}>
                Create Checkpoint
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Rewinding Overlay */}
      {isRewinding && (
        <div style={rewindingOverlayStyle}>
          <div style={rewindingContentStyle}>
            <div style={rewindAnimationStyle}>⏪</div>
            <h3 style={rewindingTitleStyle}>Rewinding...</h3>
            <p style={rewindingTextStyle}>Restoring project state</p>
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
  background: 'rgba(245, 158, 11, 0.1)',
  border: '1px solid rgba(245, 158, 11, 0.3)',
  borderRadius: '12px',
  padding: '16px 20px',
  fontSize: '14px',
  color: '#fbbf24',
  marginBottom: '20px',
  lineHeight: 1.5,
};

const quoteAuthorStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '12px',
  opacity: 0.7,
  marginTop: '8px',
  fontStyle: 'normal',
};

const branchSelectorStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '16px',
  marginBottom: '20px',
  padding: '12px 16px',
  background: 'rgba(255, 255, 255, 0.03)',
  borderRadius: '12px',
};

const branchLabelStyle: React.CSSProperties = {
  fontSize: '13px',
  fontWeight: 600,
  opacity: 0.8,
};

const branchButtonsStyle: React.CSSProperties = {
  display: 'flex',
  gap: '8px',
};

const branchButtonStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  padding: '8px 14px',
  borderRadius: '8px',
  border: '2px solid',
  fontSize: '12px',
  color: '#f8fafc',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
};

const branchDotStyle: React.CSSProperties = {
  width: '8px',
  height: '8px',
  borderRadius: '50%',
};

const timelineContainerStyle: React.CSSProperties = {
  position: 'relative',
  paddingLeft: '20px',
  marginBottom: '20px',
};

const timelineLineStyle: React.CSSProperties = {
  position: 'absolute',
  left: '28px',
  top: '0',
  bottom: '0',
  width: '3px',
  background: 'rgba(255, 255, 255, 0.1)',
  borderRadius: '2px',
};

const timelineProgressStyle: React.CSSProperties = {
  position: 'absolute',
  left: '0',
  top: '0',
  width: '100%',
  height: '60%',
  borderRadius: '2px',
};

const checkpointsListStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '16px',
};

const checkpointCardStyle: React.CSSProperties = {
  position: 'relative',
  display: 'flex',
  gap: '16px',
  padding: '16px',
  border: '2px solid',
  borderRadius: '12px',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
};

const timelineDotStyle: React.CSSProperties = {
  position: 'absolute',
  left: '-28px',
  top: '24px',
  width: '16px',
  height: '16px',
  borderRadius: '50%',
  border: '3px solid #0f172a',
  zIndex: 10,
};

const checkpointContentStyle: React.CSSProperties = {
  flex: 1,
};

const checkpointHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '8px',
};

const typeBadgeStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '6px',
  fontSize: '11px',
  background: 'rgba(255, 255, 255, 0.05)',
  padding: '4px 10px',
  borderRadius: '6px',
};

const typeIconStyle: React.CSSProperties = {
  fontSize: '12px',
};

const timestampStyle: React.CSSProperties = {
  fontSize: '12px',
  opacity: 0.6,
};

const checkpointDescriptionStyle: React.CSSProperties = {
  fontSize: '15px',
  fontWeight: 600,
  marginBottom: '8px',
  lineHeight: 1.4,
};

const currentBadgeStyle: React.CSSProperties = {
  display: 'inline-block',
  background: 'linear-gradient(135deg, #10b981, #059669)',
  color: 'white',
  fontSize: '10px',
  padding: '2px 8px',
  borderRadius: '4px',
  marginRight: '8px',
  fontWeight: 700,
};

const checkpointStatsStyle: React.CSSProperties = {
  display: 'flex',
  gap: '16px',
  fontSize: '12px',
  marginBottom: '8px',
};

const filesChangedStyle: React.CSSProperties = {
  opacity: 0.8,
};

const linesStyle: React.CSSProperties = {
  fontFamily: 'JetBrains Mono, monospace',
};

const addedStyle: React.CSSProperties = {
  color: '#10b981',
};

const removedStyle: React.CSSProperties = {
  color: '#ef4444',
};

const tagsStyle: React.CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: '6px',
  marginBottom: '8px',
};

const tagStyle: React.CSSProperties = {
  fontSize: '10px',
  background: 'rgba(99, 102, 241, 0.15)',
  color: '#818cf8',
  padding: '3px 8px',
  borderRadius: '4px',
};

const actionsPreviewStyle: React.CSSProperties = {
  fontSize: '12px',
  opacity: 0.7,
  paddingTop: '8px',
  borderTop: '1px solid rgba(255, 255, 255, 0.1)',
};

const actionItemStyle: React.CSSProperties = {
  marginBottom: '2px',
};

const moreActionsStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.6,
  marginTop: '4px',
};

const createButtonStyle: React.CSSProperties = {
  width: '100%',
  padding: '14px',
  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
  border: 'none',
  borderRadius: '12px',
  color: 'white',
  fontSize: '14px',
  fontWeight: 600,
  cursor: 'pointer',
  transition: 'all 0.3s ease',
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
  maxWidth: '600px',
  maxHeight: '80vh',
  overflow: 'auto',
};

const modalHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'flex-start',
  marginBottom: '20px',
};

const modalTypeBadgeStyle: React.CSSProperties = {
  display: 'inline-block',
  fontSize: '11px',
  padding: '6px 12px',
  borderRadius: '20px',
  fontWeight: 600,
  marginBottom: '8px',
};

const modalTitleStyle: React.CSSProperties = {
  fontSize: '18px',
  fontWeight: 700,
  margin: '0 0 4px 0',
};

const modalTimeStyle: React.CSSProperties = {
  fontSize: '12px',
  opacity: 0.6,
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

const modalContentStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '20px',
};

const modalStatsGridStyle: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(4, 1fr)',
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
  fontSize: '18px',
  fontWeight: 700,
};

const sectionStyle: React.CSSProperties = {};

const sectionTitleStyle: React.CSSProperties = {
  fontSize: '13px',
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
  opacity: 0.7,
  margin: '0 0 10px 0',
};

const filesListStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '6px',
};

const fileItemStyle: React.CSSProperties = {
  fontSize: '13px',
  fontFamily: 'JetBrains Mono, monospace',
  background: 'rgba(255, 255, 255, 0.05)',
  padding: '8px 12px',
  borderRadius: '6px',
};

const actionsListStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '6px',
};

const actionDetailStyle: React.CSSProperties = {
  fontSize: '13px',
  background: 'rgba(255, 255, 255, 0.05)',
  padding: '8px 12px',
  borderRadius: '6px',
};

const memorySnapshotStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '6px',
};

const memoryItemStyle: React.CSSProperties = {
  fontSize: '13px',
  background: 'rgba(139, 92, 246, 0.1)',
  color: '#a78bfa',
  padding: '8px 12px',
  borderRadius: '6px',
};

const modalActionsStyle: React.CSSProperties = {
  display: 'flex',
  gap: '12px',
  paddingTop: '16px',
  borderTop: '1px solid rgba(255, 255, 255, 0.1)',
};

const rewindButtonStyle: React.CSSProperties = {
  flex: 1,
  padding: '12px',
  background: 'linear-gradient(135deg, #f59e0b, #d97706)',
  border: 'none',
  borderRadius: '10px',
  color: 'white',
  fontWeight: 600,
  cursor: 'pointer',
  fontSize: '14px',
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
  maxWidth: '400px',
};

const dialogTitleStyle: React.CSSProperties = {
  fontSize: '18px',
  fontWeight: 700,
  margin: '0 0 8px 0',
};

const dialogDescriptionStyle: React.CSSProperties = {
  fontSize: '14px',
  opacity: 0.7,
  marginBottom: '16px',
};

const dialogInputStyle: React.CSSProperties = {
  width: '100%',
  padding: '12px',
  background: 'rgba(255, 255, 255, 0.05)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '10px',
  color: '#f8fafc',
  fontSize: '14px',
  marginBottom: '16px',
  outline: 'none',
};

const dialogButtonsStyle: React.CSSProperties = {
  display: 'flex',
  gap: '12px',
};

const dialogCancelStyle: React.CSSProperties = {
  flex: 1,
  padding: '10px',
  background: 'rgba(255, 255, 255, 0.05)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '8px',
  color: '#f8fafc',
  cursor: 'pointer',
};

const dialogSubmitStyle: React.CSSProperties = {
  flex: 1,
  padding: '10px',
  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
  border: 'none',
  borderRadius: '8px',
  color: 'white',
  fontWeight: 600,
  cursor: 'pointer',
};

const rewindingOverlayStyle: React.CSSProperties = {
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  background: 'rgba(0, 0, 0, 0.8)',
  backdropFilter: 'blur(10px)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 2000,
};

const rewindingContentStyle: React.CSSProperties = {
  textAlign: 'center',
};

const rewindAnimationStyle: React.CSSProperties = {
  fontSize: '64px',
  marginBottom: '16px',
  animation: 'spin 1s linear infinite',
};

const rewindingTitleStyle: React.CSSProperties = {
  fontSize: '24px',
  fontWeight: 700,
  margin: '0 0 8px 0',
};

const rewindingTextStyle: React.CSSProperties = {
  fontSize: '14px',
  opacity: 0.7,
};

export default RewindCheckpoints;
