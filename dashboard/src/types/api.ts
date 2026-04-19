/**
 * AMOS API Type Definitions
 *
 * TypeScript interfaces for FastAPI backend.
 * Mirrors Pydantic models from backend/main.py
 *
 * Creator: Trang Phan
 * Version: 3.0.0
 */

// ============================================
// Cognitive Subsystem Types
// ============================================

export interface CognitiveMode {
  mode: 'seed' | 'growth' | 'full';
  activatedAt: string;
  reasoningLevel: number;
  features: string[];
  description: string;
}

export interface ReasoningLevel {
  id: string;
  name: string;
  level: number;
  confidence: number;
  description: string;
  features: string[];
  active: boolean;
  icon: string;
}

// ============================================
// MCP Types
// ============================================

export interface MCPServer {
  id: string;
  name: string;
  type: 'ide' | 'database' | 'search' | 'storage' | 'custom';
  status: 'connected' | 'disconnected' | 'error';
  url: string;
  connectedAt?: string;
  capabilities: string[];
  icon: string;
  lastError?: string;
}

// ============================================
// Agent Types
// ============================================

export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
export type TaskType = 'analysis' | 'refactor' | 'documentation' | 'testing' | 'deployment' | 'custom';

export interface AgentTask {
  id: string;
  name: string;
  type: TaskType;
  status: TaskStatus;
  priority: 'low' | 'medium' | 'high' | 'critical';
  progress: number;
  description: string;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  result?: string;
  error?: string;
}

// ============================================
// Memory Types
// ============================================

export type MemorySystem = 'episodic' | 'semantic' | 'procedural' | 'working' | 'long-term';
export type MemoryPriority = 'low' | 'medium' | 'high' | 'critical';

export interface MemoryEntry {
  id: string;
  system: MemorySystem;
  content: string;
  timestamp: string;
  priority: MemoryPriority;
  tags: string[];
  relatedIds?: string[];
  metadata?: Record<string, any>;
}

// ============================================
// Checkpoint Types
// ============================================

export interface Checkpoint {
  id: string;
  label: string;
  timestamp: string;
  state: {
    cognitiveMode: string;
    activeAgents: string[];
    memorySnapshot: string[];
  };
  description: string;
  tags: string[];
}

// ============================================
// Orchestra Types
// ============================================

export type AgentStatus = 'idle' | 'working' | 'paused' | 'error';
export type AgentType = 'analyzer' | 'planner' | 'executor' | 'reviewer' | 'learner';

export interface OrchestraAgent {
  id: string;
  name: string;
  type: AgentType;
  status: AgentStatus;
  capabilities: string[];
  currentTask?: string;
  completedTasks: number;
  successRate: number;
  lastActivity: string;
  color: string;
  icon: string;
}

// ============================================
// AGENTS.md Types
// ============================================

export interface AGENTSFile {
  id: string;
  path: string;
  name: string;
  content: string;
  updatedAt: string;
  version: string;
  projectType?: 'web' | 'python' | 'node' | 'generic';
  sections: string[];
}

// ============================================
// System Types
// ============================================

export interface SystemStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  uptime: number;
  activeConnections: number;
  timestamp: string;
}

export interface SystemMetrics {
  cpu: number;
  memory: number;
  activeTasks: number;
  completedTasks: number;
  mcpConnections: number;
  websocketClients: number;
  timestamp: string;
}

// ============================================
// WebSocket Types
// ============================================

export type WebSocketMessageType =
  | 'cognitive_mode_changed'
  | 'reasoning_level_changed'
  | 'mcp_server_updated'
  | 'agent_task_updated'
  | 'memory_entry_created'
  | 'checkpoint_created'
  | 'orchestra_status_updated'
  | 'system_metrics_updated'
  | 'ping';

export interface WebSocketMessage {
  type: WebSocketMessageType;
  data: any;
  timestamp: string;
}

// ============================================
// API Response Types
// ============================================

export interface APIError {
  detail: string;
  status: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// ============================================
// Dashboard State Types
// ============================================

export interface DashboardState {
  isLoading: boolean;
  isConnected: boolean;
  lastUpdated: string;
  error: string | null;
}

export interface DashboardData {
  cognitiveMode: CognitiveMode;
  reasoningLevels: ReasoningLevel[];
  mcpServers: MCPServer[];
  agentTasks: AgentTask[];
  memoryEntries: MemoryEntry[];
  checkpoints: Checkpoint[];
  orchestraAgents: OrchestraAgent[];
  systemStatus: SystemStatus;
  systemMetrics: SystemMetrics;
}
