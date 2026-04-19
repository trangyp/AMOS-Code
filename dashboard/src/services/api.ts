/**
 * AMOS API Service
 *
 * HTTP client for FastAPI backend integration.
 * Provides typed API calls for all cognitive subsystems.
 *
 * Creator: Trang Phan
 * Version: 3.0.0
 */

import {
  CognitiveMode,
  ReasoningLevel,
  MCPServer,
  AgentTask,
  MemoryEntry,
  Checkpoint,
  OrchestraAgent,
  AGENTSFile,
  SystemMetrics,
  SystemStatus
} from '../types/api';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// HTTP Client
async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

// ============================================
// Cognitive Mode API
// ============================================

export async function getCognitiveMode(): Promise<CognitiveMode> {
  return fetchAPI<CognitiveMode>('/api/v1/system/cognitive/mode');
}

export async function setCognitiveMode(mode: 'seed' | 'growth' | 'full'): Promise<CognitiveMode> {
  return fetchAPI<CognitiveMode>('/api/v1/system/cognitive/mode', {
    method: 'POST',
    body: JSON.stringify({ mode }),
  });
}

// ============================================
// Reasoning Levels API
// ============================================

export async function getReasoningLevels(): Promise<ReasoningLevel[]> {
  return fetchAPI<ReasoningLevel[]>('/api/v1/system/reasoning/levels');
}

export async function getReasoningLevel(id: string): Promise<ReasoningLevel> {
  return fetchAPI<ReasoningLevel>(`/api/v1/system/reasoning/level/${id}`);
}

export async function activateReasoningLevel(id: string): Promise<ReasoningLevel> {
  return fetchAPI<ReasoningLevel>(`/api/v1/system/reasoning/level/${id}/activate`, {
    method: 'POST',
  });
}

// ============================================
// MCP Servers API
// ============================================

export async function getMCPServers(): Promise<MCPServer[]> {
  return fetchAPI<MCPServer[]>('/api/v1/system/mcp/servers');
}

export async function getMCPServer(id: string): Promise<MCPServer> {
  return fetchAPI<MCPServer>(`/api/v1/system/mcp/servers/${id}`);
}

export async function connectMCPServer(id: string): Promise<MCPServer> {
  return fetchAPI<MCPServer>(`/api/v1/system/mcp/servers/${id}/connect`, {
    method: 'POST',
  });
}

export async function disconnectMCPServer(id: string): Promise<MCPServer> {
  return fetchAPI<MCPServer>(`/api/v1/system/mcp/servers/${id}/disconnect`, {
    method: 'POST',
  });
}

// ============================================
// Background Agents API
// ============================================

export async function getAgentTasks(): Promise<AgentTask[]> {
  return fetchAPI<AgentTask[]>('/api/v1/agents/tasks');
}

export async function createAgentTask(task: Omit<AgentTask, 'id' | 'createdAt' | 'updatedAt'>): Promise<AgentTask> {
  return fetchAPI<AgentTask>('/api/v1/agents/tasks', {
    method: 'POST',
    body: JSON.stringify(task),
  });
}

export async function cancelAgentTask(id: string): Promise<AgentTask> {
  return fetchAPI<AgentTask>(`/api/v1/agents/tasks/${id}/cancel`, {
    method: 'POST',
  });
}

// ============================================
// Persistent Memory API
// ============================================

export async function getMemoryEntries(system?: string, limit?: number): Promise<MemoryEntry[]> {
  const params = new URLSearchParams();
  if (system) params.append('system', system);
  if (limit) params.append('limit', limit.toString());

  return fetchAPI<MemoryEntry[]>(`/api/v1/system/memory/entries?${params}`);
}

export async function searchMemory(query: string, system?: string): Promise<MemoryEntry[]> {
  const params = new URLSearchParams();
  params.append('q', query);
  if (system) params.append('system', system);

  return fetchAPI<MemoryEntry[]>(`/api/v1/system/memory/search?${params}`);
}

export async function createMemoryEntry(entry: Omit<MemoryEntry, 'id' | 'timestamp'>): Promise<MemoryEntry> {
  return fetchAPI<MemoryEntry>('/api/v1/system/memory/entries', {
    method: 'POST',
    body: JSON.stringify(entry),
  });
}

// ============================================
// Checkpoints API
// ============================================

export async function getCheckpoints(): Promise<Checkpoint[]> {
  return fetchAPI<Checkpoint[]>('/api/v1/system/checkpoints');
}

export async function createCheckpoint(label?: string): Promise<Checkpoint> {
  return fetchAPI<Checkpoint>('/api/v1/system/checkpoints', {
    method: 'POST',
    body: JSON.stringify({ label }),
  });
}

export async function rewindToCheckpoint(id: string): Promise<{ success: boolean; restored: string }> {
  return fetchAPI<{ success: boolean; restored: string }>(`/api/v1/system/checkpoints/${id}/rewind`, {
    method: 'POST',
  });
}

// ============================================
// Agent Orchestra API
// ============================================

export async function getOrchestraAgents(): Promise<OrchestraAgent[]> {
  return fetchAPI<OrchestraAgent[]>('/api/v1/system/orchestra/agents');
}

export async function getOrchestraStatus(): Promise<{
  activeAgents: number;
  totalTasks: number;
  completedTasks: number;
  failedTasks: number;
  avgResponseTime: number;
  timestamp: string;
}> {
  return fetchAPI('/api/v1/system/orchestra/status');
}

export async function toggleOrchestraAgent(id: string, active: boolean): Promise<OrchestraAgent> {
  return fetchAPI<OrchestraAgent>(`/api/v1/system/orchestra/agents/${id}/toggle`, {
    method: 'POST',
    body: JSON.stringify({ active }),
  });
}

// ============================================
// AGENTS.md API
// ============================================

export async function getAGENTSFiles(): Promise<AGENTSFile[]> {
  return fetchAPI<AGENTSFile[]>('/api/v1/system/agents-md/files');
}

export async function getAGENTSFile(id: string): Promise<AGENTSFile> {
  return fetchAPI<AGENTSFile>(`/api/v1/system/agents-md/files/${id}`);
}

export async function updateAGENTSFile(id: string, content: string): Promise<AGENTSFile> {
  return fetchAPI<AGENTSFile>(`/api/v1/system/agents-md/files/${id}`, {
    method: 'PUT',
    body: JSON.stringify({ content }),
  });
}

// ============================================
// System Status API
// ============================================

export async function getSystemStatus(): Promise<SystemStatus> {
  return fetchAPI<SystemStatus>('/api/v1/system/status');
}

export async function getSystemMetrics(): Promise<SystemMetrics> {
  return fetchAPI<SystemMetrics>('/api/v1/system/metrics');
}

// ============================================
// Health Check
// ============================================

export async function healthCheck(): Promise<{ status: string; version: string }> {
  return fetchAPI<{ status: string; version: string }>('/health');
}

// ============================================
// Batch Operations
// ============================================

export async function getDashboardData(): Promise<{
  cognitiveMode: CognitiveMode;
  reasoningLevels: ReasoningLevel[];
  mcpServers: MCPServer[];
  agentTasks: AgentTask[];
  memoryEntries: MemoryEntry[];
  checkpoints: Checkpoint[];
  orchestraAgents: OrchestraAgent[];
  systemStatus: SystemStatus;
  systemMetrics: SystemMetrics;
}> {
  const [
    cognitiveMode,
    reasoningLevels,
    mcpServers,
    agentTasks,
    memoryEntries,
    checkpoints,
    orchestraAgents,
    systemStatus,
    systemMetrics,
  ] = await Promise.all([
    getCognitiveMode(),
    getReasoningLevels(),
    getMCPServers(),
    getAgentTasks(),
    getMemoryEntries(undefined, 10),
    getCheckpoints(),
    getOrchestraAgents(),
    getSystemStatus(),
    getSystemMetrics(),
  ]);

  return {
    cognitiveMode,
    reasoningLevels,
    mcpServers,
    agentTasks,
    memoryEntries,
    checkpoints,
    orchestraAgents,
    systemStatus,
    systemMetrics,
  };
}

export default {
  // Cognitive
  getCognitiveMode,
  setCognitiveMode,

  // Reasoning
  getReasoningLevels,
  getReasoningLevel,
  activateReasoningLevel,

  // MCP
  getMCPServers,
  getMCPServer,
  connectMCPServer,
  disconnectMCPServer,

  // Agents
  getAgentTasks,
  createAgentTask,
  cancelAgentTask,

  // Memory
  getMemoryEntries,
  searchMemory,
  createMemoryEntry,

  // Checkpoints
  getCheckpoints,
  createCheckpoint,
  rewindToCheckpoint,

  // Orchestra
  getOrchestraAgents,
  getOrchestraStatus,
  toggleOrchestraAgent,

  // AGENTS.md
  getAGENTSFiles,
  getAGENTSFile,
  updateAGENTSFile,

  // System
  getSystemStatus,
  getSystemMetrics,
  healthCheck,

  // Batch
  getDashboardData,
};
