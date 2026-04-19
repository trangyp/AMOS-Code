/**
 * AMOS System Hooks
 *
 * React hooks for integrating the dashboard with the AMOS backend API.
 * Provides data fetching, real-time updates, and state management.
 *
 * Usage:
 *   const { status, loading, error } = useSystemStatus();
 *   const { evolution, toggleEvolution } = useEvolution();
 *
 * Creator: Trang Phan
 * Version: 1.0.0
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { api, WebSocketClient, SystemStatus, HealthStatus, MetricsResponse, EvolutionStatus, GovernanceRule, Agent, LLMProvider } from '../api';

// Generic loading state hook
interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

function useApi<T>(fetchFn: () => Promise<T>, deps: React.DependencyList = []): UseApiState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchFn();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, deps);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

// System Status Hook
export function useSystemStatus(pollInterval?: number): UseApiState<SystemStatus> {
  const state = useApi(() => api.getSystemStatus(), []);

  useEffect(() => {
    if (!pollInterval) return;

    const interval = setInterval(() => {
      state.refetch();
    }, pollInterval);

    return () => clearInterval(interval);
  }, [pollInterval, state.refetch]);

  return state;
}

// Health Status Hook
export function useHealthStatus(): UseApiState<HealthStatus> {
  return useApi(() => api.getHealthStatus(), []);
}

// Metrics Hook
export function useMetrics(pollInterval = 5000): UseApiState<MetricsResponse> {
  const state = useApi(() => api.getMetrics(), []);

  useEffect(() => {
    const interval = setInterval(() => {
      state.refetch();
    }, pollInterval);

    return () => clearInterval(interval);
  }, [pollInterval, state.refetch]);

  return state;
}

// Evolution Hook
interface UseEvolutionReturn extends UseApiState<EvolutionStatus> {
  toggleEvolution: (enabled: boolean) => Promise<void>;
  toggling: boolean;
}

export function useEvolution(): UseEvolutionReturn {
  const [toggling, setToggling] = useState(false);
  const state = useApi(() => api.getEvolutionStatus(), []);

  const toggleEvolution = useCallback(async (enabled: boolean) => {
    setToggling(true);
    try {
      await api.toggleEvolution(enabled);
      await state.refetch();
    } catch (err) {
      console.error('Failed to toggle evolution:', err);
      throw err;
    } finally {
      setToggling(false);
    }
  }, [state.refetch]);

  return {
    ...state,
    toggleEvolution,
    toggling,
  };
}

// Governance Rules Hook
export function useGovernanceRules(): UseApiState<GovernanceRule[]> {
  return useApi(() => api.getGovernanceRules(), []);
}

// Agents Hook
export function useAgents(): UseApiState<Agent[]> {
  return useApi(() => api.getAgents(), []);
}

// LLM Providers Hook
export function useLLMProviders(): UseApiState<LLMProvider[]> {
  return useApi(() => api.getLLMProviders(), []);
}

// WebSocket Hook for Real-time Updates
interface UseWebSocketReturn {
  connected: boolean;
  lastMessage: unknown | null;
  error: string | null;
}

export function useWebSocket(endpoint: string = '/ws/health'): UseWebSocketReturn {
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<unknown | null>(null);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocketClient | null>(null);

  useEffect(() => {
    const ws = new WebSocketClient();
    wsRef.current = ws;

    ws.on('message', (data) => {
      setLastMessage(data);
      setConnected(true);
      setError(null);
    });

    ws.connect(endpoint);

    // Check connection status periodically
    const checkInterval = setInterval(() => {
      // WebSocket state would be checked here
    }, 5000);

    return () => {
      clearInterval(checkInterval);
      ws.disconnect();
      wsRef.current = null;
    };
  }, [endpoint]);

  return { connected, lastMessage, error };
}

// Combined Dashboard Hook
interface DashboardData {
  status: SystemStatus | null;
  health: HealthStatus | null;
  metrics: MetricsResponse | null;
  evolution: EvolutionStatus | null;
  agents: Agent[] | null;
}

interface UseDashboardReturn {
  data: DashboardData;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

export function useDashboard(): UseDashboardReturn {
  const status = useSystemStatus(30000); // Poll every 30s
  const health = useHealthStatus();
  const metrics = useMetrics(5000); // Poll every 5s
  const evolution = useEvolution();
  const agents = useAgents();

  const refresh = useCallback(() => {
    status.refetch();
    health.refetch();
    metrics.refetch();
    evolution.refetch();
    agents.refetch();
  }, [status.refetch, health.refetch, metrics.refetch, evolution.refetch, agents.refetch]);

  const loading = status.loading || health.loading || metrics.loading || evolution.loading || agents.loading;

  const error = [
    status.error,
    health.error,
    metrics.error,
    evolution.error,
    agents.error,
  ].filter(Boolean).join(', ') || null;

  const data: DashboardData = {
    status: status.data,
    health: health.data,
    metrics: metrics.data,
    evolution: evolution.data,
    agents: agents.data,
  };

  return { data, loading, error, refresh };
}

// Signal-Noise Kernel Hook
interface SignalNoiseResult {
  input: string;
  signal_quality: number;
  noise_distortion: number;
  ambiguity_count: number;
  execution_safe: boolean;
  signals: Array<{ signal_class: string; content: string; confidence: number }>;
  noise_units: Array<{ noise_class: string; content: string; distortion_score: number }>;
  ambiguities: Array<{ ambiguity_type: string; references: string[]; severity: number }>;
}

export function useSignalNoise() {
  const [result, setResult] = useState<SignalNoiseResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = useCallback(async (text: string, context?: Record<string, unknown>) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.analyzeSignalNoise(text, context);
      setResult(data as SignalNoiseResult);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { analyze, result, loading, error };
}

// Cognitive Processing Hook
interface CognitiveResult {
  request_id: string;
  input: string;
  signal_noise: { signal_quality: number; noise_distortion: number; execution_safe: boolean };
  semantic: { goal_type: string; objective: string; confidence: number };
  brain: { status: string; legality: number; sigma: number; mode: string };
  final_output: string;
  total_time_ms: number;
}

export function useCognitive() {
  const [result, setResult] = useState<CognitiveResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const process = useCallback(async (
    input: string,
    options?: { priority?: string; enableExecution?: boolean; context?: Record<string, unknown> }
  ) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.processCognitive(input, options);
      setResult(data as CognitiveResult);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Processing failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { process, result, loading, error };
}

// Export all hooks
export default {
  useSystemStatus,
  useHealthStatus,
  useMetrics,
  useEvolution,
  useGovernanceRules,
  useAgents,
  useLLMProviders,
  useWebSocket,
  useDashboard,
  useSignalNoise,
  useCognitive,
};
