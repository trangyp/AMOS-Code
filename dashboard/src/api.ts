/**
 * AMOS Dashboard API Client
 *
 * TypeScript API client for connecting the React dashboard to the FastAPI backend.
 * Provides typed methods for all backend endpoints.
 *
 * Usage:
 *   import { api } from './api';
 *   const status = await api.getSystemStatus();
 *
 * Creator: Trang Phan
 * Version: 1.0.0
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Types matching backend Pydantic schemas
export interface SystemStatus {
  version: string;
  status: string;
  uptime_seconds: number;
  components: Record<string, string>;
}

export interface HealthStatus {
  status: string;
  timestamp: string;
  version: string;
}

export interface MetricsResponse {
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
  active_connections: number;
  requests_per_minute: number;
}

export interface EvolutionStatus {
  enabled: boolean;
  active_contracts: number;
  pending_changes: number;
  last_execution: string | null;
}

export interface GovernanceRule {
  id: string;
  name: string;
  description: string;
  priority: number;
  enabled: boolean;
}

export interface LLMProvider {
  id: string;
  name: string;
  available: boolean;
  models: string[];
}

export interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'idle' | 'error';
  last_activity: string;
}

// API Error class
export class APIError extends Error {
  constructor(
    public status: number,
    public message: string,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// Base request function
async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  const response = await fetch(url, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new APIError(response.status, error.detail || 'Request failed', error);
  }

  // Handle empty responses
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

// API Client
export const api = {
  // System API
  getSystemStatus: () => request<SystemStatus>('/api/v1/system/status'),
  getHealth: () => request<HealthStatus>('/api/v1/system/health'),
  getMetrics: () => request<MetricsResponse>('/api/v1/system/metrics'),

  // Evolution API
  getEvolutionStatus: () => request<EvolutionStatus>('/api/v1/system/evolution'),
  toggleEvolution: (enabled: boolean) =>
    request<EvolutionStatus>(`/api/v1/system/evolution/toggle?enabled=${enabled}`, {
      method: 'POST',
    }),

  // Governance API
  getGovernanceRules: () => request<GovernanceRule[]>('/api/v1/system/governance/rules'),
  updateGovernanceMode: (mode: string) =>
    request('/api/v1/system/governance/mode', {
      method: 'POST',
      body: JSON.stringify({ mode }),
    }),

  // LLM API
  getLLMProviders: () => request<LLMProvider[]>('/api/v1/llm/providers'),

  // Agents API
  getAgents: () => request<Agent[]>('/api/v1/agents'),

  // Health API
  getHealthStatus: () => request<HealthStatus>('/health'),

  // Signal-Noise Kernel API
  analyzeSignalNoise: (text: string, context?: Record<string, unknown>) =>
    request('/api/v1/signal-noise/analyze', {
      method: 'POST',
      body: JSON.stringify({ text, context: context || {} }),
    }),
  getSignalNoiseStatus: () =>
    request('/api/v1/signal-noise/status'),

  // Cognitive Processing API
  processCognitive: (input: string, options?: { priority?: string; enableExecution?: boolean; context?: Record<string, unknown> }) =>
    request('/api/v1/cognitive/process', {
      method: 'POST',
      body: JSON.stringify({
        input,
        priority: options?.priority || 'MEDIUM',
        enable_execution: options?.enableExecution || false,
        context: options?.context || {},
      }),
    }),
  getCognitiveHealth: () =>
    request('/api/v1/cognitive/health'),

  // Fast Thinking API (<100ms)
  thinkFast: (query: string, context?: Record<string, unknown>) =>
    request<{
      response: string;
      thinking_mode: string;
      confidence: number;
      latency_ms: number;
      fast_latency_ms: number | null;
      success: boolean;
    }>('/api/brain/think-fast?query=' + encodeURIComponent(query), {
      method: 'POST',
      body: JSON.stringify({ context: context || {} }),
    }),

  processFast: (observation: Record<string, unknown>, context?: Record<string, unknown>, goal?: Record<string, unknown>) =>
    request<{
      decision: { action: string };
      thinking_mode: string;
      confidence: number;
      latency_ms: number;
      fast_latency_ms: number | null;
      success: boolean;
    }>('/cognitive/process-fast', {
      method: 'POST',
      body: JSON.stringify({
        observation,
        context: context || {},
        goal: goal || {},
      }),
    }),

  // Brain Dashboard API
  getBrainHealth: () =>
    request<{
      status: string;
      kernel_available: boolean;
      memory_entries: number;
      last_activity: string | null;
      cognitive_cycles_today: number;
      avg_response_time_ms: number;
    }>('/api/v1/brain-dashboard/health'),

  getBrainSummary: (days?: number) =>
    request<{
      total_decisions: number;
      rule_of_two_applied: number;
      rule_of_four_applied: number;
      avg_confidence: number;
      compliance_rate: number;
    }>(`/api/v1/brain-dashboard/summary?days=${days || 7}`),

  getRecentCycles: (limit?: number) =>
    request<Array<{
      timestamp: string;
      observation_type: string;
      goal_type: string;
      status: string;
      legality_score: number;
      sigma: number;
      latency_ms: number;
    }>>(`/api/v1/brain-dashboard/recent-cycles?limit=${limit || 10}`),

  getDomainPatterns: (days?: number) =>
    request<Array<{
      domain: string;
      count: number;
      avg_confidence: number;
      trend: string;
    }>>(`/api/v1/brain-dashboard/domain-patterns?days=${days || 7}`),

  getBrainInsights: (days?: number) =>
    request<{
      insights: string[];
      status: string;
      generated_at: string;
      period_days: number;
    }>(`/api/v1/brain-dashboard/insights?days=${days || 7}`),

  getFullDashboard: (days?: number) =>
    request<{
      timestamp: string;
      health: {
        status: string;
        kernel_available: boolean;
        memory_entries: number;
        last_activity: string | null;
        cognitive_cycles_today: number;
        avg_response_time_ms: number;
      };
      summary: {
        total_decisions: number;
        rule_of_two_applied: number;
        rule_of_four_applied: number;
        avg_confidence: number;
        compliance_rate: number;
      };
      recent_cycles: Array<{
        timestamp: string;
        observation_type: string;
        goal_type: string;
        status: string;
        legality_score: number;
        sigma: number;
        latency_ms: number;
      }>;
      domain_patterns: Array<{
        domain: string;
        count: number;
        avg_confidence: number;
        trend: string;
      }>;
      insights: string[];
    }>(`/api/v1/brain-dashboard/full?days=${days || 7}`),

  getRealtimeBrainData: () =>
    request<{
      timestamp: string;
      status: string;
      metrics: {
        last_activity: string | null;
        memory_size: number;
        cycle_rate: string;
      };
    }>('/api/v1/brain-dashboard/realtime'),

  // Enhanced Task Processor API
  processEnhancedTask: (task: {
    task_type: 'code_analysis' | 'equation_execution' | 'document_processing' | 'data_transformation' | 'cognitive_reasoning';
    payload: Record<string, unknown>;
    priority?: 1 | 2 | 3 | 4;
    use_brain?: boolean;
    timeout_seconds?: number;
    context?: Record<string, unknown>;
  }) =>
    request<{
      task_id: string;
      status: string;
      result: {
        success: boolean;
        result: unknown;
        processing_time_ms: number;
        brain_enhanced: boolean;
        cognitive_score: number | null;
        error_message: string | null;
      } | null;
      timestamp: string;
    }>('/api/v1/enhanced-tasks/process', {
      method: 'POST',
      body: JSON.stringify(task),
    }),

  // Brain Kernel Direct API
  executeKernelCycle: (observation: Record<string, unknown>, goal?: Record<string, unknown>, timeout_ms?: number) =>
    request<{
      success: boolean;
      status: string;
      legality_score: number;
      sigma: number;
      selected_branch: string | null;
      latency_ms: number;
      timestamp: string;
      details: Record<string, unknown>;
    }>('/api/v1/brain-kernel/cycle', {
      method: 'POST',
      body: JSON.stringify({
        observation: observation || {},
        goal: goal || {},
        timeout_ms: timeout_ms || 5000,
      }),
    }),

  analyzeStateGraph: (vertices: string[], edges: Array<{source: string; target: string; properties?: Record<string, unknown>}>, state_vars?: Record<string, number>) =>
    request<{
      success: boolean;
      state_hash: string;
      vertex_count: number;
      edge_count: number;
      omega: number;
      kappa: number;
      phi: number;
      drift: number;
      legality: number;
    }>('/api/v1/brain-kernel/state/analyze', {
      method: 'POST',
      body: JSON.stringify({ vertices, edges, state_vars: state_vars || {} }),
    }),

  checkLegality: (state_data: Record<string, unknown>, invariants?: string[]) =>
    request<{
      is_legal: boolean;
      legality_score: number;
      drift_coefficient: number;
      violations: Array<{law_id: string; description: string; severity: number}>;
      mode: string;
    }>('/api/v1/brain-kernel/legality/check', {
      method: 'POST',
      body: JSON.stringify({ state_data, invariants: invariants || [] }),
    }),
};

// WebSocket connection for real-time updates
export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private listeners: Map<string, Set<(data: unknown) => void>> = new Map();

  connect(endpoint: string = '/ws/health'): void {
    const wsUrl = `${API_BASE_URL.replace('http', 'ws')}${endpoint}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.emit('message', data);
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.attemptReconnect(endpoint);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  private attemptReconnect(endpoint: string): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
      setTimeout(() => this.connect(endpoint), delay);
    }
  }

  on(event: string, callback: (data: unknown) => void): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
  }

  off(event: string, callback: (data: unknown) => void): void {
    this.listeners.get(event)?.delete(callback);
  }

  private emit(event: string, data: unknown): void {
    this.listeners.get(event)?.forEach((callback) => callback(data));
  }

  disconnect(): void {
    this.ws?.close();
    this.ws = null;
  }
}

export default api;
