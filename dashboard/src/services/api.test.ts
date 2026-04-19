/**
 * API Service Tests
 *
 * Unit tests for the AMOS API service layer.
 *
 * Creator: Trang Phan
 * Version: 3.0.0
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  getCognitiveMode,
  setCognitiveMode,
  getReasoningLevels,
  getMCPServers,
  getAgentTasks,
  getMemoryEntries,
  getCheckpoints,
  getOrchestraAgents,
  getSystemStatus,
  healthCheck,
} from './api';

// Mock fetch
global.fetch = vi.fn();

const mockFetch = fetch as ReturnType<typeof vi.fn>;

const API_BASE_URL = 'http://localhost:8000';

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Cognitive Mode', () => {
    it('should fetch cognitive mode', async () => {
      const mockMode = {
        mode: 'growth',
        activatedAt: '2026-01-15T10:00:00Z',
        reasoningLevel: 2,
        features: ['advanced-reasoning', 'background-agents'],
        description: 'Growth mode',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockMode,
      });

      const result = await getCognitiveMode();

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/api/cognitive/mode`,
        { headers: { 'Content-Type': 'application/json' } }
      );
      expect(result).toEqual(mockMode);
    });

    it('should set cognitive mode', async () => {
      const mockMode = {
        mode: 'full',
        activatedAt: '2026-01-15T10:00:00Z',
        reasoningLevel: 3,
        features: ['all-features'],
        description: 'Full mode',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockMode,
      });

      const result = await setCognitiveMode('full');

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/api/cognitive/mode`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mode: 'full' }),
        }
      );
      expect(result).toEqual(mockMode);
    });
  });

  describe('Reasoning Levels', () => {
    it('should fetch reasoning levels', async () => {
      const mockLevels = [
        { id: 'l1', name: 'Level 1', level: 1, confidence: 0.85, active: true },
        { id: 'l2', name: 'Level 2', level: 2, confidence: 0.75, active: false },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockLevels,
      });

      const result = await getReasoningLevels();

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/api/reasoning/levels`,
        { headers: { 'Content-Type': 'application/json' } }
      );
      expect(result).toEqual(mockLevels);
    });
  });

  describe('MCP Servers', () => {
    it('should fetch MCP servers', async () => {
      const mockServers = [
        { id: '1', name: 'PostgreSQL', type: 'database', status: 'connected' },
        { id: '2', name: 'Redis', type: 'database', status: 'disconnected' },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockServers,
      });

      const result = await getMCPServers();

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/api/mcp/servers`,
        { headers: { 'Content-Type': 'application/json' } }
      );
      expect(result).toEqual(mockServers);
    });
  });

  describe('Agent Tasks', () => {
    it('should fetch agent tasks', async () => {
      const mockTasks = [
        { id: '1', name: 'Code Analysis', status: 'running', progress: 45 },
        { id: '2', name: 'Documentation', status: 'pending', progress: 0 },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTasks,
      });

      const result = await getAgentTasks();

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/api/agents/tasks`,
        { headers: { 'Content-Type': 'application/json' } }
      );
      expect(result).toEqual(mockTasks);
    });
  });

  describe('Memory Entries', () => {
    it('should fetch memory entries', async () => {
      const mockEntries = [
        { id: '1', system: 'episodic', content: 'Task completed', timestamp: '2026-01-15T10:00:00Z' },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockEntries,
      });

      const result = await getMemoryEntries();

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/api/memory/entries?`,
        { headers: { 'Content-Type': 'application/json' } }
      );
      expect(result).toEqual(mockEntries);
    });
  });

  describe('Checkpoints', () => {
    it('should fetch checkpoints', async () => {
      const mockCheckpoints = [
        { id: '1', label: 'Before refactor', timestamp: '2026-01-15T10:00:00Z' },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockCheckpoints,
      });

      const result = await getCheckpoints();

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/api/checkpoints`,
        { headers: { 'Content-Type': 'application/json' } }
      );
      expect(result).toEqual(mockCheckpoints);
    });
  });

  describe('Orchestra Agents', () => {
    it('should fetch orchestra agents', async () => {
      const mockAgents = [
        { id: '1', name: 'Analyzer', status: 'working', completedTasks: 42 },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAgents,
      });

      const result = await getOrchestraAgents();

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/api/orchestra/agents`,
        { headers: { 'Content-Type': 'application/json' } }
      );
      expect(result).toEqual(mockAgents);
    });
  });

  describe('System Status', () => {
    it('should fetch system status', async () => {
      const mockStatus = {
        status: 'healthy',
        version: '3.0.0',
        uptime: 3600,
        activeConnections: 5,
        timestamp: '2026-01-15T10:00:00Z',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockStatus,
      });

      const result = await getSystemStatus();

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/api/system/status`,
        { headers: { 'Content-Type': 'application/json' } }
      );
      expect(result).toEqual(mockStatus);
    });
  });

  describe('Health Check', () => {
    it('should check health', async () => {
      const mockHealth = { status: 'healthy', version: '3.0.0' };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockHealth,
      });

      const result = await healthCheck();

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/health`,
        { headers: { 'Content-Type': 'application/json' } }
      );
      expect(result).toEqual(mockHealth);
    });
  });

  describe('Error Handling', () => {
    it('should throw error on HTTP error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ detail: 'Server error' }),
      });

      await expect(getCognitiveMode()).rejects.toThrow('Server error');
    });

    it('should throw generic error on unknown error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({}),
      });

      await expect(getCognitiveMode()).rejects.toThrow('HTTP 404: Not Found');
    });
  });
});
