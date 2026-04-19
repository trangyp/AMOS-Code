/**
 * useExecutionWebSocket - Real-time execution streaming hook
 *
 * Provides WebSocket connection for live execution output streaming.
 * Connects to FastAPI WebSocket endpoint and handles:
 * - Connection lifecycle
 * - Message streaming
 * - Reconnection logic
 * - Error handling
 *
 * @author Trang Phan
 * @version 2.0.0
 */

import { useState, useEffect, useRef, useCallback } from 'react';

// Types
export interface ExecutionMessage {
  type: 'stdout' | 'stderr' | 'status' | 'error' | 'complete';
  data: string;
  timestamp: string;
  executionId?: string;
}

export interface ExecutionState {
  status: 'idle' | 'connecting' | 'running' | 'completed' | 'error';
  messages: ExecutionMessage[];
  error?: string;
}

export interface UseExecutionWebSocketReturn {
  state: ExecutionState;
  connect: (executionId: string) => void;
  disconnect: () => void;
  sendInput: (input: string) => void;
  clearMessages: () => void;
  isConnected: boolean;
}

// Configuration
const WS_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_WS_URL) || 'ws://localhost:8000';
const RECONNECT_DELAY = 3000;
const MAX_RECONNECT_ATTEMPTS = 5;

export function useExecutionWebSocket(): UseExecutionWebSocketReturn {
  // State
  const [state, setState] = useState<ExecutionState>({
    status: 'idle',
    messages: [],
  });
  const [isConnected, setIsConnected] = useState(false);

  // Refs
  const wsRef = useRef<WebSocket | null>(null);
  const executionIdRef = useRef<string | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Connect to WebSocket
  const connect = useCallback((executionId: string) => {
    // Disconnect existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    executionIdRef.current = executionId;
    reconnectAttemptsRef.current = 0;

    setState(prev => ({
      ...prev,
      status: 'connecting',
      messages: [],
    }));

    const wsUrl = `${WS_BASE_URL}/ws/execution/${executionId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('🔌 WebSocket connected:', executionId);
      setIsConnected(true);
      setState(prev => ({
        ...prev,
        status: 'running',
      }));
      reconnectAttemptsRef.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const message: ExecutionMessage = JSON.parse(event.data);
        setState(prev => ({
          ...prev,
          messages: [...prev.messages, message],
          status: message.type === 'complete' ? 'completed' : prev.status,
        }));
      } catch (error) {
        // Handle plain text messages
        setState(prev => ({
          ...prev,
          messages: [
            ...prev.messages,
            {
              type: 'stdout',
              data: event.data,
              timestamp: new Date().toISOString(),
            },
          ],
        }));
      }
    };

    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setState(prev => ({
        ...prev,
        status: 'error',
        error: 'WebSocket connection error',
      }));
    };

    ws.onclose = (event) => {
      console.log('🔌 WebSocket closed:', event.code, event.reason);
      setIsConnected(false);

      // Attempt reconnection if not completed and not max attempts
      if (
        state.status !== 'completed' &&
        reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS
      ) {
        reconnectAttemptsRef.current++;
        console.log(
          `🔄 Reconnecting... Attempt ${reconnectAttemptsRef.current}/${MAX_RECONNECT_ATTEMPTS}`
        );

        reconnectTimeoutRef.current = setTimeout(() => {
          if (executionIdRef.current) {
            connect(executionIdRef.current);
          }
        }, RECONNECT_DELAY);
      } else if (reconnectAttemptsRef.current >= MAX_RECONNECT_ATTEMPTS) {
        setState(prev => ({
          ...prev,
          status: 'error',
          error: 'Max reconnection attempts reached',
        }));
      }
    };

    wsRef.current = ws;
  }, [state.status]);

  // Disconnect WebSocket
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    executionIdRef.current = null;
    setIsConnected(false);
    setState({
      status: 'idle',
      messages: [],
    });
  }, []);

  // Send input to running process (for interactive execution)
  const sendInput = useCallback((input: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'input',
          data: input,
        })
      );
    }
  }, []);

  // Clear messages
  const clearMessages = useCallback(() => {
    setState(prev => ({
      ...prev,
      messages: [],
    }));
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    state,
    connect,
    disconnect,
    sendInput,
    clearMessages,
    isConnected,
  };
}

export default useExecutionWebSocket;
