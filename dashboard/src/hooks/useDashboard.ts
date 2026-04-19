/**
 * React Hook: Dashboard Data Management
 *
 * Fetches and manages all dashboard data from FastAPI backend.
 * Includes auto-refresh, caching, and real-time WebSocket updates.
 *
 * Creator: Trang Phan
 * Version: 3.0.0
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  DashboardData,
  DashboardState,
} from '../types/api';
import * as api from '../services/api';
import { wsManager, ConnectionState } from '../services/websocket';

interface UseDashboardReturn extends DashboardData, DashboardState {
  // Actions
  refresh: () => Promise<void>;
  setCognitiveMode: (mode: 'seed' | 'growth' | 'full') => Promise<void>;
  activateReasoningLevel: (id: string) => Promise<void>;
  connectMCPServer: (id: string) => Promise<void>;
  disconnectMCPServer: (id: string) => Promise<void>;
  cancelAgentTask: (id: string) => Promise<void>;
  createCheckpoint: (label?: string) => Promise<void>;
  rewindToCheckpoint: (id: string) => Promise<void>;
  toggleOrchestraAgent: (id: string, active: boolean) => Promise<void>;

  // WebSocket
  wsState: ConnectionState;
  reconnectWebSocket: () => void;
}

// Initial empty state
const initialData: DashboardData = {
  cognitiveMode: {
    mode: 'seed',
    activatedAt: new Date().toISOString(),
    reasoningLevel: 1,
    features: [],
    description: '',
  },
  reasoningLevels: [],
  mcpServers: [],
  agentTasks: [],
  memoryEntries: [],
  checkpoints: [],
  orchestraAgents: [],
  systemStatus: {
    status: 'healthy',
    version: '3.0.0',
    uptime: 0,
    activeConnections: 0,
    timestamp: new Date().toISOString(),
  },
  systemMetrics: {
    cpu: 0,
    memory: 0,
    activeTasks: 0,
    completedTasks: 0,
    mcpConnections: 0,
    websocketClients: 0,
    timestamp: new Date().toISOString(),
  },
};

export function useDashboard(): UseDashboardReturn {
  // Data state
  const [data, setData] = useState<DashboardData>(initialData);
  const [state, setState] = useState<DashboardState>({
    isLoading: true,
    isConnected: false,
    lastUpdated: '',
    error: null,
  });
  const [wsState, setWsState] = useState<ConnectionState>('disconnected');

  // Refs for managing async operations
  const refreshInterval = useRef<ReturnType<typeof setInterval> | null>(null);

  // ============================================
  // Data Fetching
  // ============================================

  const fetchData = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));

      const dashboardData = await api.getDashboardData();

      setData(dashboardData);
      setState({
        isLoading: false,
        isConnected: true,
        lastUpdated: new Date().toLocaleTimeString(),
        error: null,
      });
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setState(prev => ({
        ...prev,
        isLoading: false,
        isConnected: false,
        error: error instanceof Error ? error.message : 'Failed to fetch data',
      }));
    }
  }, []);

  // Refresh function
  const refresh = useCallback(async () => {
    await fetchData();
  }, [fetchData]);

  // ============================================
  // Actions
  // ============================================

  const setCognitiveMode = useCallback(async (mode: 'seed' | 'growth' | 'full') => {
    try {
      const result = await api.setCognitiveMode(mode);
      setData(prev => ({ ...prev, cognitiveMode: result }));
    } catch (error) {
      console.error('Failed to set cognitive mode:', error);
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to set mode',
      }));
    }
  }, []);

  const activateReasoningLevel = useCallback(async (id: string) => {
    try {
      const result = await api.activateReasoningLevel(id);
      setData(prev => ({
        ...prev,
        reasoningLevels: prev.reasoningLevels.map(l =>
          l.id === id ? result : { ...l, active: false }
        ),
      }));
    } catch (error) {
      console.error('Failed to activate reasoning level:', error);
    }
  }, []);

  const connectMCPServer = useCallback(async (id: string) => {
    try {
      const result = await api.connectMCPServer(id);
      setData(prev => ({
        ...prev,
        mcpServers: prev.mcpServers.map(s =>
          s.id === id ? result : s
        ),
      }));
    } catch (error) {
      console.error('Failed to connect MCP server:', error);
    }
  }, []);

  const disconnectMCPServer = useCallback(async (id: string) => {
    try {
      const result = await api.disconnectMCPServer(id);
      setData(prev => ({
        ...prev,
        mcpServers: prev.mcpServers.map(s =>
          s.id === id ? result : s
        ),
      }));
    } catch (error) {
      console.error('Failed to disconnect MCP server:', error);
    }
  }, []);

  const cancelAgentTask = useCallback(async (id: string) => {
    try {
      const result = await api.cancelAgentTask(id);
      setData(prev => ({
        ...prev,
        agentTasks: prev.agentTasks.map(t =>
          t.id === id ? result : t
        ),
      }));
    } catch (error) {
      console.error('Failed to cancel agent task:', error);
    }
  }, []);

  const createCheckpoint = useCallback(async (label?: string) => {
    try {
      const result = await api.createCheckpoint(label);
      setData(prev => ({
        ...prev,
        checkpoints: [result, ...prev.checkpoints],
      }));
    } catch (error) {
      console.error('Failed to create checkpoint:', error);
    }
  }, []);

  const rewindToCheckpoint = useCallback(async (id: string) => {
    try {
      await api.rewindToCheckpoint(id);
      // Refresh all data after rewind
      await fetchData();
    } catch (error) {
      console.error('Failed to rewind to checkpoint:', error);
    }
  }, [fetchData]);

  const toggleOrchestraAgent = useCallback(async (id: string, active: boolean) => {
    try {
      const result = await api.toggleOrchestraAgent(id, active);
      setData(prev => ({
        ...prev,
        orchestraAgents: prev.orchestraAgents.map(a =>
          a.id === id ? result : a
        ),
      }));
    } catch (error) {
      console.error('Failed to toggle orchestra agent:', error);
    }
  }, []);

  // ============================================
  // WebSocket Integration
  // ============================================

  useEffect(() => {
    // Connect WebSocket
    wsManager.connect();

    // Subscribe to state changes
    const unsubscribeState = wsManager.onStateChange((newState) => {
      setWsState(newState);
      setState(prev => ({ ...prev, isConnected: newState === 'connected' }));
    });

    // Subscribe to real-time updates
    const unsubscribeCognitive = wsManager.onCognitiveModeChange((mode) => {
      setData(prev => ({ ...prev, cognitiveMode: mode }));
    });

    const unsubscribeReasoning = wsManager.onReasoningLevelChange((level) => {
      setData(prev => ({
        ...prev,
        reasoningLevels: prev.reasoningLevels.map(l =>
          l.id === level.id ? level : l
        ),
      }));
    });

    const unsubscribeMCP = wsManager.onMCPServerUpdate((server) => {
      setData(prev => ({
        ...prev,
        mcpServers: prev.mcpServers.map(s =>
          s.id === server.id ? server : s
        ),
      }));
    });

    const unsubscribeAgent = wsManager.onAgentTaskUpdate((task) => {
      setData(prev => ({
        ...prev,
        agentTasks: prev.agentTasks.map(t =>
          t.id === task.id ? task : t
        ),
      }));
    });

    const unsubscribeMemory = wsManager.onMemoryEntryCreate((entry) => {
      setData(prev => ({
        ...prev,
        memoryEntries: [entry, ...prev.memoryEntries].slice(0, 100), // Keep last 100
      }));
    });

    const unsubscribeCheckpoint = wsManager.onCheckpointCreate((checkpoint) => {
      setData(prev => ({
        ...prev,
        checkpoints: [checkpoint, ...prev.checkpoints],
      }));
    });

    const unsubscribeOrchestra = wsManager.onOrchestraStatusUpdate((status) => {
      setData(prev => ({
        ...prev,
        orchestraAgents: status.agents || prev.orchestraAgents,
      }));
    });

    const unsubscribeMetrics = wsManager.onSystemMetricsUpdate((metrics) => {
      setData(prev => ({ ...prev, systemMetrics: metrics }));
    });

    // Cleanup
    return () => {
      unsubscribeState();
      unsubscribeCognitive();
      unsubscribeReasoning();
      unsubscribeMCP();
      unsubscribeAgent();
      unsubscribeMemory();
      unsubscribeCheckpoint();
      unsubscribeOrchestra();
      unsubscribeMetrics();
      wsManager.disconnect();
    };
  }, []);

  // ============================================
  // Auto-refresh
  // ============================================

  useEffect(() => {
    // Initial fetch
    fetchData();

    // Setup auto-refresh every 30 seconds
    refreshInterval.current = setInterval(() => {
      fetchData();
    }, 30000);

    return () => {
      if (refreshInterval.current) {
        clearInterval(refreshInterval.current);
      }
    };
  }, [fetchData]);

  // Reconnect WebSocket
  const reconnectWebSocket = useCallback(() => {
    wsManager.connect();
  }, []);

  return {
    // Data
    ...data,
    // State
    ...state,
    wsState,
    // Actions
    refresh,
    setCognitiveMode,
    activateReasoningLevel,
    connectMCPServer,
    disconnectMCPServer,
    cancelAgentTask,
    createCheckpoint,
    rewindToCheckpoint,
    toggleOrchestraAgent,
    reconnectWebSocket,
  };
}

export default useDashboard;
