/**
 * AMOS React Hooks
 *
 * Custom hooks for data fetching, state management, and API integration.
 *
 * Creator: Trang Phan
 * Version: 3.0.0
 */

// Dashboard data management
export { default as useDashboardDefault } from './useDashboard';
export { default as useExecutionWebSocketDefault } from './useExecutionWebSocket';
export { useExecutionWebSocket } from './useExecutionWebSocket';

// AGENTS.md management
export { useAgentsMD } from './useAgentsMD';

// AMOS API Integration hooks
export {
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
} from './useAMOS';

// Re-export context hooks for convenience
export {
  useDashboardContext,
  useCognitiveMode,
  useReasoningLevels,
  useMCPServers,
  useAgentTasks,
  useMemoryEntries,
  useCheckpoints,
  useOrchestraAgents,
  useDashboardActions,
} from '../contexts/DashboardContext';
