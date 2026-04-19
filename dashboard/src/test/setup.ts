/**
 * Vitest Test Setup
 *
 * Configure testing environment and global mocks.
 *
 * Creator: Trang Phan
 * Version: 3.0.0
 */

import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock fetch globally
global.fetch = vi.fn();

// Mock WebSocket
global.WebSocket = vi.fn().mockImplementation(() => ({
  send: vi.fn(),
  close: vi.fn(),
  onopen: null,
  onclose: null,
  onmessage: null,
  onerror: null,
  readyState: 1, // WebSocket.OPEN
}));

// Mock import.meta.env
vi.mock('import.meta', () => ({
  env: {
    VITE_API_URL: 'http://localhost:8000',
    VITE_WS_URL: 'ws://localhost:8000/ws',
    DEV: true,
    PROD: false,
  },
}));

// Cleanup after each test
afterEach(() => {
  vi.clearAllMocks();
});
