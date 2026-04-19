/**
 * Dashboard Context Provider
 *
 * Provides global dashboard state to all components.
 * Wraps useDashboard hook for application-wide data access.
 *
 * Creator: Trang Phan
 * Version: 3.0.0
 */

import { createContext, useContext, ReactNode } from 'react';
import { useDashboard } from '../hooks/useDashboard';
import { DashboardData, DashboardState } from '../types/api';
import { ConnectionState } from '../services/websocket';

// Context type
interface DashboardContextType extends DashboardData, DashboardState {
  // WebSocket
  wsState: ConnectionState;
  reconnectWebSocket: () => void;

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
}

// Create context
const DashboardContext = createContext<DashboardContextType | null>(null);

// Provider component
interface DashboardProviderProps {
  children: ReactNode;
}

export function DashboardProvider({ children }: DashboardProviderProps) {
  const dashboard = useDashboard();

  return (
    <DashboardContext.Provider value={dashboard}>
      {children}
    </DashboardContext.Provider>
  );
}

// Custom hook for consuming the context
export function useDashboardContext(): DashboardContextType {
  const context = useContext(DashboardContext);

  if (!context) {
    throw new Error('useDashboardContext must be used within a DashboardProvider');
  }

  return context;
}

// Convenience hooks for specific data slices

export function useCognitiveMode() {
  const { cognitiveMode, setCognitiveMode } = useDashboardContext();
  return { cognitiveMode, setCognitiveMode };
}

export function useReasoningLevels() {
  const { reasoningLevels, activateReasoningLevel } = useDashboardContext();
  return { reasoningLevels, activateReasoningLevel };
}

export function useMCPServers() {
  const { mcpServers, connectMCPServer, disconnectMCPServer } = useDashboardContext();
  return { mcpServers, connectMCPServer, disconnectMCPServer };
}

export function useAgentTasks() {
  const { agentTasks, cancelAgentTask } = useDashboardContext();
  return { agentTasks, cancelAgentTask };
}

export function useMemoryEntries() {
  const { memoryEntries } = useDashboardContext();
  return { memoryEntries };
}

export function useCheckpoints() {
  const { checkpoints, createCheckpoint, rewindToCheckpoint } = useDashboardContext();
  return { checkpoints, createCheckpoint, rewindToCheckpoint };
}

export function useOrchestraAgents() {
  const { orchestraAgents, toggleOrchestraAgent } = useDashboardContext();
  return { orchestraAgents, toggleOrchestraAgent };
}

export function useSystemStatus() {
  const { systemStatus, systemMetrics, wsState, isConnected } = useDashboardContext();
  return { systemStatus, systemMetrics, wsState, isConnected };
}

export function useDashboardActions() {
  const { refresh, reconnectWebSocket } = useDashboardContext();
  return { refresh, reconnectWebSocket };
}

export default DashboardContext;
