/**
 * AMOS Persistent Memory Component
 *
 * #2 on RedMonk 2025 "10 Things Developers Want"
 *
 * Developers are frustrated by agents that forget everything between sessions.
 * They want agents that:
 * - Remember past decisions
 * - Recognize patterns from previous work
 * - Maintain awareness of project history
 * - Become a "living system of record"
 *
 * AMOS implements 5 memory systems:
 * 1. Episodic Memory - Conversations and sessions
 * 2. Semantic Memory - Knowledge and facts about the codebase
 * 3. Procedural Memory - Skills and workflows
 * 4. Working Memory - Current active context
 * 5. Long-term Memory - Persistent storage across projects
 *
 * Based on research from Claude Code, Windsurf Cascade, and Redis AI memory patterns.
 */

import React, { useState } from 'react';

// Memory Types
interface Memory {
  id: string;
  type: 'episodic' | 'semantic' | 'procedural' | 'working' | 'longterm';
  content: string;
  summary: string;
  importance: number; // 1-10
  createdAt: string;
  lastAccessed: string;
  accessCount: number;
  tags: string[];
  sessionId?: string;
  projectId?: string;
  relatedMemories?: string[];
  embeddings?: number[];
}

interface MemoryStats {
  totalMemories: number;
  episodicCount: number;
  semanticCount: number;
  proceduralCount: number;
  workingCount: number;
  longtermCount: number;
  totalSize: string; // e.g., "2.4 MB"
  consolidationScore: number; // 0-100
}

interface MemorySearchResult {
  memory: Memory;
  relevanceScore: number;
  context: string;
}

// Mock Memory Data
const MOCK_MEMORIES: Memory[] = [
  {
    id: 'mem-1',
    type: 'semantic',
    content: 'The authentication system uses JWT tokens with refresh token rotation. Access tokens expire every 15 minutes, refresh tokens every 7 days.',
    summary: 'Auth system: JWT with refresh rotation (15min/7day)',
    importance: 9,
    createdAt: new Date(Date.now() - 86400000 * 5).toISOString(),
    lastAccessed: new Date(Date.now() - 3600000).toISOString(),
    accessCount: 12,
    tags: ['auth', 'jwt', 'security', 'architecture'],
    projectId: 'amos-core',
    relatedMemories: ['mem-2', 'mem-3'],
  },
  {
    id: 'mem-2',
    type: 'procedural',
    content: 'When implementing new API endpoints: 1) Add to OpenAPI spec first, 2) Generate types, 3) Implement handler, 4) Add tests, 5) Update docs',
    summary: 'API endpoint implementation workflow (5 steps)',
    importance: 8,
    createdAt: new Date(Date.now() - 86400000 * 3).toISOString(),
    lastAccessed: new Date(Date.now() - 7200000).toISOString(),
    accessCount: 8,
    tags: ['api', 'workflow', 'best-practices'],
    projectId: 'amos-core',
    relatedMemories: ['mem-1'],
  },
  {
    id: 'mem-3',
    type: 'episodic',
    content: 'User asked to refactor the payment module. We extracted 3 utility functions, improved error handling, and added type safety. Result: 40% less code, better test coverage.',
    summary: 'Payment module refactoring session - extracted 3 utils, added types',
    importance: 7,
    createdAt: new Date(Date.now() - 86400000 * 2).toISOString(),
    lastAccessed: new Date(Date.now() - 86400000).toISOString(),
    accessCount: 5,
    tags: ['refactoring', 'payment', 'typescript'],
    sessionId: 'session-2025-04-10-001',
    projectId: 'amos-core',
    relatedMemories: ['mem-1', 'mem-4'],
  },
  {
    id: 'mem-4',
    type: 'semantic',
    content: 'User prefers concise error messages without stack traces in production. Development mode should show full traces. Configure via LOG_LEVEL env var.',
    summary: 'User preference: concise errors in prod, full traces in dev',
    importance: 6,
    createdAt: new Date(Date.now() - 86400000 * 4).toISOString(),
    lastAccessed: new Date(Date.now() - 86400000 * 2).toISOString(),
    accessCount: 3,
    tags: ['preferences', 'error-handling', 'logging'],
    projectId: 'amos-core',
  },
  {
    id: 'mem-5',
    type: 'working',
    content: 'Currently working on: Implementing the Background Agents task queue UI. Need to support filtering by status, priority levels, and progress tracking.',
    summary: 'Current task: Background Agents UI implementation',
    importance: 10,
    createdAt: new Date(Date.now() - 3600000).toISOString(),
    lastAccessed: new Date(Date.now() - 600000).toISOString(),
    accessCount: 15,
    tags: ['current', 'ui', 'background-agents'],
    sessionId: 'session-2025-04-15-001',
    projectId: 'amos-core',
  },
  {
    id: 'mem-6',
    type: 'longterm',
    content: 'Project uses React 18, TypeScript 5.5, Tailwind CSS, and Vite. Testing with Vitest and React Testing Library. Backend uses FastAPI and PostgreSQL.',
    summary: 'Tech stack: React 18, TS 5.5, Tailwind, Vite, Vitest, FastAPI, Postgres',
    importance: 9,
    createdAt: new Date(Date.now() - 86400000 * 10).toISOString(),
    lastAccessed: new Date(Date.now() - 1800000).toISOString(),
    accessCount: 20,
    tags: ['tech-stack', 'architecture', 'project-info'],
    projectId: 'amos-core',
  },
  {
    id: 'mem-7',
    type: 'semantic',
    content: 'Database schema: Users table has id, email, created_at. Projects table has id, name, owner_id (FK to users). Tasks table has id, project_id, status, assigned_to.',
    summary: 'DB schema: Users-Projects-Tasks relationships',
    importance: 8,
    createdAt: new Date(Date.now() - 86400000 * 6).toISOString(),
    lastAccessed: new Date(Date.now() - 10800000).toISOString(),
    accessCount: 10,
    tags: ['database', 'schema', 'postgres'],
    projectId: 'amos-core',
    relatedMemories: ['mem-6'],
  },
  {
    id: 'mem-8',
    type: 'procedural',
    content: 'Code review checklist: 1) Check for security issues, 2) Verify test coverage, 3) Check performance implications, 4) Verify documentation updated, 5) Check for breaking changes',
    summary: 'Code review checklist (5 items)',
    importance: 7,
    createdAt: new Date(Date.now() - 86400000 * 7).toISOString(),
    lastAccessed: new Date(Date.now() - 86400000 * 3).toISOString(),
    accessCount: 6,
    tags: ['code-review', 'workflow', 'quality'],
    projectId: 'amos-core',
  },
];

const MOCK_STATS: MemoryStats = {
  totalMemories: 156,
  episodicCount: 42,
  semanticCount: 58,
  proceduralCount: 24,
  workingCount: 12,
  longtermCount: 20,
  totalSize: '4.2 MB',
  consolidationScore: 87,
};

export const PersistentMemory: React.FC = () => {
  const [memories, setMemories] = useState<Memory[]>(MOCK_MEMORIES);
  const [stats, setStats] = useState<MemoryStats>(MOCK_STATS);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState<Memory['type'] | 'all'>('all');
  const [selectedMemory, setSelectedMemory] = useState<Memory | null>(null);
  const [showConsolidateDialog, setShowConsolidateDialog] = useState(false);
  const [searchResults, setSearchResults] = useState<MemorySearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Filter memories
  const filteredMemories = memories.filter(m => {
    const matchesType = selectedType === 'all' || m.type === selectedType;
    const matchesSearch = !searchQuery ||
      m.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.tags.some(t => t.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesType && matchesSearch;
  });

  // Sort by importance and last accessed
  const sortedMemories = filteredMemories.sort((a, b) => {
    if (b.importance !== a.importance) return b.importance - a.importance;
    return new Date(b.lastAccessed).getTime() - new Date(a.lastAccessed).getTime();
  });

  // Simulate semantic search
  const performSearch = () => {
    if (!searchQuery) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);

    // Simulate search delay
    setTimeout(() => {
      const results: MemorySearchResult[] = memories
        .filter(m =>
          m.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
          m.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
          m.tags.some(t => t.toLowerCase().includes(searchQuery.toLowerCase()))
        )
        .map(m => ({
          memory: m,
          relevanceScore: Math.random() * 0.3 + 0.7, // 0.7-1.0
          context: m.summary.substring(0, 100) + '...',
        }))
        .sort((a, b) => b.relevanceScore - a.relevanceScore);

      setSearchResults(results);
      setIsSearching(false);
    }, 800);
  };

  // Consolidate memories (extract long-term insights)
  const consolidateMemories = () => {
    setShowConsolidateDialog(true);

    // Simulate consolidation
    setTimeout(() => {
      setStats(prev => ({
        ...prev,
        consolidationScore: Math.min(100, prev.consolidationScore + 5),
      }));
      setShowConsolidateDialog(false);
    }, 2000);
  };

  // Delete memory
  const deleteMemory = (memoryId: string) => {
    setMemories(prev => prev.filter(m => m.id !== memoryId));
    if (selectedMemory?.id === memoryId) {
      setSelectedMemory(null);
    }
  };

  // Update memory importance
  const updateImportance = (memoryId: string, newImportance: number) => {
    setMemories(prev => prev.map(m =>
      m.id === memoryId ? { ...m, importance: newImportance } : m
    ));
  };

  // Get type color
  const getTypeColor = (type: Memory['type']) => {
    switch (type) {
      case 'episodic': return '#f59e0b'; // amber
      case 'semantic': return '#3b82f6'; // blue
      case 'procedural': return '#10b981'; // green
      case 'working': return '#ef4444'; // red
      case 'longterm': return '#8b5cf6'; // purple
      default: return '#6b7280';
    }
  };

  // Get type label
  const getTypeLabel = (type: Memory['type']) => {
    switch (type) {
      case 'episodic': return '📖 Episodic';
      case 'semantic': return '🧠 Semantic';
      case 'procedural': return '⚙️ Procedural';
      case 'working': return '💭 Working';
      case 'longterm': return '🔮 Long-term';
      default: return type;
    }
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

  // Get importance stars
  const getImportanceStars = (importance: number) => {
    return '★'.repeat(importance) + '☆'.repeat(10 - importance);
  };

  return (
    <div style={containerStyle}>
      {/* Header */}
      <div style={headerStyle}>
        <div>
          <h3 style={titleStyle}>🧠 Persistent Memory</h3>
          <p style={subtitleStyle}>
            5-System Memory Architecture. Never forget.
          </p>
        </div>
        <div style={statsContainerStyle}>
          <div style={statBoxStyle}>
            <span style={statNumberStyle}>{stats.totalMemories}</span>
            <span style={statLabelStyle}>Memories</span>
          </div>
          <div style={statBoxStyle}>
            <span style={statNumberStyle}>{stats.totalSize}</span>
            <span style={statLabelStyle}>Size</span>
          </div>
          <div style={statBoxStyle}>
            <span style={statNumberStyle}>{stats.consolidationScore}%</span>
            <span style={statLabelStyle}>Organized</span>
          </div>
        </div>
      </div>

      {/* Quote Banner */}
      <div style={quoteBannerStyle}>
        <em>"Developers want their agentic IDE to become a living system of record that captures not just code but reasoning."</em>
        <span style={quoteAuthorStyle}>— RedMonk, 2025</span>
      </div>

      {/* Memory Type Legend */}
      <div style={legendStyle}>
        <div style={legendItemStyle}>
          <span style={{ ...legendDotStyle, backgroundColor: '#f59e0b' }} />
          <span style={legendTextStyle}>Episodic (Sessions)</span>
        </div>
        <div style={legendItemStyle}>
          <span style={{ ...legendDotStyle, backgroundColor: '#3b82f6' }} />
          <span style={legendTextStyle}>Semantic (Knowledge)</span>
        </div>
        <div style={legendItemStyle}>
          <span style={{ ...legendDotStyle, backgroundColor: '#10b981' }} />
          <span style={legendTextStyle}>Procedural (Skills)</span>
        </div>
        <div style={legendItemStyle}>
          <span style={{ ...legendDotStyle, backgroundColor: '#ef4444' }} />
          <span style={legendTextStyle}>Working (Active)</span>
        </div>
        <div style={legendItemStyle}>
          <span style={{ ...legendDotStyle, backgroundColor: '#8b5cf6' }} />
          <span style={legendTextStyle}>Long-term (Archive)</span>
        </div>
      </div>

      {/* Search Bar */}
      <div style={searchContainerStyle}>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search memories... (e.g., 'auth', 'database schema', 'user preferences')"
          style={searchInputStyle}
          onKeyPress={(e) => e.key === 'Enter' && performSearch()}
        />
        <button onClick={performSearch} style={searchButtonStyle}>
          {isSearching ? '🔍 Searching...' : '🔍 Search'}
        </button>
      </div>

      {/* Type Filter */}
      <div style={filterContainerStyle}>
        {(['all', 'episodic', 'semantic', 'procedural', 'working', 'longterm'] as const).map(type => (
          <button
            key={type}
            onClick={() => setSelectedType(type)}
            style={{
              ...filterButtonStyle,
              backgroundColor: selectedType === type ? 'rgba(99, 102, 241, 0.3)' : 'rgba(255,255,255,0.05)',
              borderColor: selectedType === type ? 'rgba(99, 102, 241, 0.5)' : 'rgba(255,255,255,0.1)',
            }}
          >
            {type === 'all' ? 'All Types' : getTypeLabel(type as Memory['type'])}
          </button>
        ))}
      </div>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <div style={searchResultsStyle}>
          <h4 style={searchResultsTitleStyle}>Search Results ({searchResults.length})</h4>
          {searchResults.slice(0, 3).map(result => (
            <div
              key={result.memory.id}
              style={searchResultItemStyle}
              onClick={() => setSelectedMemory(result.memory)}
            >
              <div style={resultRelevanceStyle}>
                {Math.round(result.relevanceScore * 100)}% match
              </div>
              <div style={resultSummaryStyle}>{result.memory.summary}</div>
              <div style={resultContextStyle}>{result.context}</div>
            </div>
          ))}
        </div>
      )}

      {/* Memory Grid */}
      <div style={memoryGridStyle}>
        {sortedMemories.map(memory => (
          <div
            key={memory.id}
            style={{
              ...memoryCardStyle,
              borderColor: getTypeColor(memory.type),
            }}
            onClick={() => setSelectedMemory(memory)}
          >
            {/* Card Header */}
            <div style={cardHeaderStyle}>
              <span style={{
                ...typeBadgeStyle,
                backgroundColor: `${getTypeColor(memory.type)}20`,
                color: getTypeColor(memory.type),
              }}>
                {getTypeLabel(memory.type)}
              </span>
              <span style={importanceStyle} title={`Importance: ${memory.importance}/10`}>
                {getImportanceStars(memory.importance)}
              </span>
            </div>

            {/* Summary */}
            <div style={cardSummaryStyle}>{memory.summary}</div>

            {/* Meta */}
            <div style={cardMetaStyle}>
              <span style={accessCountStyle}>👁️ {memory.accessCount} views</span>
              <span style={timeStyle}>{formatTimeAgo(memory.lastAccessed)}</span>
            </div>

            {/* Tags */}
            <div style={cardTagsStyle}>
              {memory.tags.slice(0, 3).map(tag => (
                <span key={tag} style={cardTagStyle}>{tag}</span>
              ))}
              {memory.tags.length > 3 && (
                <span style={moreTagsStyle}>+{memory.tags.length - 3}</span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Consolidate Button */}
      <div style={actionsStyle}>
        <button onClick={consolidateMemories} style={consolidateButtonStyle}>
          🧹 Consolidate Memories
        </button>
        <span style={consolidateHintStyle}>
          Extract long-term insights from recent sessions
        </span>
      </div>

      {/* Memory Detail Modal */}
      {selectedMemory && (
        <div style={modalOverlayStyle} onClick={() => setSelectedMemory(null)}>
          <div style={modalStyle} onClick={(e) => e.stopPropagation()}>
            <div style={modalHeaderStyle}>
              <div>
                <span style={{
                  ...modalTypeBadgeStyle,
                  backgroundColor: `${getTypeColor(selectedMemory.type)}20`,
                  color: getTypeColor(selectedMemory.type),
                }}>
                  {getTypeLabel(selectedMemory.type)}
                </span>
                <h4 style={modalTitleStyle}>{selectedMemory.summary}</h4>
              </div>
              <button onClick={() => setSelectedMemory(null)} style={closeButtonStyle}>✕</button>
            </div>

            <div style={modalContentStyle}>
              <div style={contentSectionStyle}>
                <h5 style={sectionLabelStyle}>Full Content</h5>
                <p style={contentTextStyle}>{selectedMemory.content}</p>
              </div>

              <div style={statsGridStyle}>
                <div style={statItemStyle}>
                  <span style={statItemLabelStyle}>Importance</span>
                  <span style={statItemValueStyle}>
                    {getImportanceStars(selectedMemory.importance)} ({selectedMemory.importance}/10)
                  </span>
                </div>
                <div style={statItemStyle}>
                  <span style={statItemLabelStyle}>Access Count</span>
                  <span style={statItemValueStyle}>{selectedMemory.accessCount} times</span>
                </div>
                <div style={statItemStyle}>
                  <span style={statItemLabelStyle}>Created</span>
                  <span style={statItemValueStyle}>{formatTimeAgo(selectedMemory.createdAt)}</span>
                </div>
                <div style={statItemStyle}>
                  <span style={statItemLabelStyle}>Last Accessed</span>
                  <span style={statItemValueStyle}>{formatTimeAgo(selectedMemory.lastAccessed)}</span>
                </div>
              </div>

              {selectedMemory.relatedMemories && selectedMemory.relatedMemories.length > 0 && (
                <div style={relatedSectionStyle}>
                  <h5 style={sectionLabelStyle}>Related Memories</h5>
                  <div style={relatedListStyle}>
                    {selectedMemory.relatedMemories.map(relId => {
                      const rel = memories.find(m => m.id === relId);
                      return rel ? (
                        <div
                          key={relId}
                          style={relatedItemStyle}
                          onClick={() => setSelectedMemory(rel)}
                        >
                          {rel.summary}
                        </div>
                      ) : null;
                    })}
                  </div>
                </div>
              )}

              <div style={modalActionsStyle}>
                <div style={importanceControlStyle}>
                  <span style={controlLabelStyle}>Importance:</span>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={selectedMemory.importance}
                    onChange={(e) => updateImportance(selectedMemory.id, parseInt(e.target.value))}
                    style={importanceSliderStyle}
                  />
                </div>
                <button
                  onClick={() => deleteMemory(selectedMemory.id)}
                  style={deleteButtonStyle}
                >
                  🗑️ Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Consolidation Dialog */}
      {showConsolidateDialog && (
        <div style={dialogOverlayStyle}>
          <div style={dialogStyle}>
            <div style={dialogContentStyle}>
              <div style={consolidatingAnimationStyle}>🧠</div>
              <h4 style={dialogTitleStyle}>Consolidating Memories...</h4>
              <p style={dialogTextStyle}>
                Extracting long-term insights from episodic memories and
                organizing semantic knowledge for better retrieval.
              </p>
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
  background: 'rgba(139, 92, 246, 0.1)',
  border: '1px solid rgba(139, 92, 246, 0.3)',
  borderRadius: '12px',
  padding: '16px 20px',
  fontSize: '14px',
  color: '#a78bfa',
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

const legendStyle: React.CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: '16px',
  marginBottom: '20px',
  padding: '12px 16px',
  background: 'rgba(255, 255, 255, 0.03)',
  borderRadius: '12px',
};

const legendItemStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '6px',
  fontSize: '12px',
};

const legendDotStyle: React.CSSProperties = {
  width: '10px',
  height: '10px',
  borderRadius: '50%',
};

const legendTextStyle: React.CSSProperties = {
  opacity: 0.8,
};

const searchContainerStyle: React.CSSProperties = {
  display: 'flex',
  gap: '12px',
  marginBottom: '16px',
};

const searchInputStyle: React.CSSProperties = {
  flex: 1,
  padding: '12px 16px',
  background: 'rgba(255, 255, 255, 0.05)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '12px',
  color: '#f8fafc',
  fontSize: '14px',
  outline: 'none',
};

const searchButtonStyle: React.CSSProperties = {
  padding: '12px 20px',
  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
  border: 'none',
  borderRadius: '12px',
  color: 'white',
  fontWeight: 600,
  cursor: 'pointer',
  fontSize: '14px',
};

const filterContainerStyle: React.CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: '8px',
  marginBottom: '20px',
};

const filterButtonStyle: React.CSSProperties = {
  padding: '8px 14px',
  borderRadius: '8px',
  border: '1px solid',
  fontSize: '12px',
  cursor: 'pointer',
  color: '#f8fafc',
  transition: 'all 0.3s ease',
};

const searchResultsStyle: React.CSSProperties = {
  background: 'rgba(59, 130, 246, 0.1)',
  border: '1px solid rgba(59, 130, 246, 0.3)',
  borderRadius: '12px',
  padding: '16px',
  marginBottom: '20px',
};

const searchResultsTitleStyle: React.CSSProperties = {
  fontSize: '14px',
  fontWeight: 600,
  margin: '0 0 12px 0',
  color: '#60a5fa',
};

const searchResultItemStyle: React.CSSProperties = {
  padding: '12px',
  background: 'rgba(255, 255, 255, 0.05)',
  borderRadius: '8px',
  marginBottom: '8px',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
};

const resultRelevanceStyle: React.CSSProperties = {
  fontSize: '11px',
  color: '#10b981',
  fontWeight: 600,
  marginBottom: '4px',
};

const resultSummaryStyle: React.CSSProperties = {
  fontSize: '13px',
  fontWeight: 600,
  marginBottom: '4px',
};

const resultContextStyle: React.CSSProperties = {
  fontSize: '12px',
  opacity: 0.7,
};

const memoryGridStyle: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
  gap: '16px',
  marginBottom: '20px',
};

const memoryCardStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.03)',
  border: '2px solid',
  borderRadius: '16px',
  padding: '16px',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
};

const cardHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '12px',
};

const typeBadgeStyle: React.CSSProperties = {
  fontSize: '10px',
  padding: '4px 10px',
  borderRadius: '20px',
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
};

const importanceStyle: React.CSSProperties = {
  fontSize: '11px',
  color: '#fbbf24',
  letterSpacing: '1px',
};

const cardSummaryStyle: React.CSSProperties = {
  fontSize: '14px',
  fontWeight: 600,
  lineHeight: 1.4,
  marginBottom: '12px',
};

const cardMetaStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  fontSize: '11px',
  opacity: 0.6,
  marginBottom: '8px',
};

const accessCountStyle: React.CSSProperties = {};

const timeStyle: React.CSSProperties = {};

const cardTagsStyle: React.CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: '6px',
};

const cardTagStyle: React.CSSProperties = {
  fontSize: '10px',
  background: 'rgba(99, 102, 241, 0.15)',
  color: '#818cf8',
  padding: '3px 8px',
  borderRadius: '4px',
};

const moreTagsStyle: React.CSSProperties = {
  fontSize: '10px',
  opacity: 0.5,
  padding: '3px 0',
};

const actionsStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '16px',
  padding: '16px',
  background: 'rgba(255, 255, 255, 0.03)',
  borderRadius: '12px',
};

const consolidateButtonStyle: React.CSSProperties = {
  padding: '12px 20px',
  background: 'linear-gradient(135deg, #10b981, #059669)',
  border: 'none',
  borderRadius: '10px',
  color: 'white',
  fontWeight: 600,
  cursor: 'pointer',
  fontSize: '14px',
};

const consolidateHintStyle: React.CSSProperties = {
  fontSize: '12px',
  opacity: 0.6,
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
  fontSize: '11px',
  padding: '6px 12px',
  borderRadius: '20px',
  fontWeight: 600,
  textTransform: 'uppercase',
  display: 'inline-block',
  marginBottom: '8px',
};

const modalTitleStyle: React.CSSProperties = {
  fontSize: '18px',
  fontWeight: 700,
  margin: 0,
  lineHeight: 1.4,
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

const contentSectionStyle: React.CSSProperties = {};

const sectionLabelStyle: React.CSSProperties = {
  fontSize: '12px',
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
  opacity: 0.6,
  margin: '0 0 8px 0',
};

const contentTextStyle: React.CSSProperties = {
  fontSize: '14px',
  lineHeight: 1.6,
  background: 'rgba(255, 255, 255, 0.05)',
  padding: '12px',
  borderRadius: '8px',
};

const statsGridStyle: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(2, 1fr)',
  gap: '12px',
};

const statItemStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.05)',
  padding: '12px',
  borderRadius: '8px',
};

const statItemLabelStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.6,
  display: 'block',
  marginBottom: '4px',
};

const statItemValueStyle: React.CSSProperties = {
  fontSize: '14px',
  fontWeight: 600,
};

const relatedSectionStyle: React.CSSProperties = {};

const relatedListStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '8px',
};

const relatedItemStyle: React.CSSProperties = {
  padding: '10px',
  background: 'rgba(255, 255, 255, 0.05)',
  borderRadius: '8px',
  fontSize: '13px',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
};

const modalActionsStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  paddingTop: '16px',
  borderTop: '1px solid rgba(255, 255, 255, 0.1)',
};

const importanceControlStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
};

const controlLabelStyle: React.CSSProperties = {
  fontSize: '13px',
  fontWeight: 600,
};

const importanceSliderStyle: React.CSSProperties = {
  width: '120px',
};

const deleteButtonStyle: React.CSSProperties = {
  padding: '8px 16px',
  background: 'rgba(239, 68, 68, 0.2)',
  color: '#ef4444',
  border: '1px solid rgba(239, 68, 68, 0.3)',
  borderRadius: '8px',
  fontSize: '13px',
  cursor: 'pointer',
};

const dialogOverlayStyle: React.CSSProperties = {
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  background: 'rgba(0, 0, 0, 0.8)',
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
  padding: '32px',
  textAlign: 'center',
  maxWidth: '400px',
};

const dialogContentStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
};

const consolidatingAnimationStyle: React.CSSProperties = {
  fontSize: '48px',
  marginBottom: '16px',
  animation: 'pulse 2s infinite',
};

const dialogTitleStyle: React.CSSProperties = {
  fontSize: '18px',
  fontWeight: 700,
  margin: '0 0 8px 0',
};

const dialogTextStyle: React.CSSProperties = {
  fontSize: '14px',
  opacity: 0.7,
  lineHeight: 1.5,
};

export default PersistentMemory;
