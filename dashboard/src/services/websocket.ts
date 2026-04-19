/**
 * AMOS WebSocket Service
 *
 * Real-time connection to FastAPI WebSocket backend.
 * Handles automatic reconnection and message routing.
 *
 * Creator: Trang Phan
 * Version: 3.0.0
 */

import { WebSocketMessage, WebSocketMessageType } from '../types/api';

// WebSocket Configuration
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/dashboard';

// Connection states
export type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

// Event handlers type
export type MessageHandler = (message: WebSocketMessage) => void;

class WebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private heartbeatInterval: ReturnType<typeof setInterval> | null = null;
  private messageHandlers: Map<WebSocketMessageType, Set<MessageHandler>> = new Map();
  private stateChangeHandlers: Set<(state: ConnectionState) => void> = new Set();
  private connectionState: ConnectionState = 'disconnected';

  constructor() {
    // Initialize handler sets for all message types
    const messageTypes: WebSocketMessageType[] = [
      'cognitive_mode_changed',
      'reasoning_level_changed',
      'mcp_server_updated',
      'agent_task_updated',
      'memory_entry_created',
      'checkpoint_created',
      'orchestra_status_updated',
      'system_metrics_updated',
      'ping',
    ];

    messageTypes.forEach(type => {
      this.messageHandlers.set(type, new Set());
    });
  }

  // ============================================
  // Connection Management
  // ============================================

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('[WebSocket] Already connected');
      return;
    }

    this.setConnectionState('connecting');

    try {
      this.ws = new WebSocket(WS_URL);

      this.ws.onopen = () => {
        console.log('[WebSocket] Connected');
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
        this.setConnectionState('connected');
        this.startHeartbeat();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('[WebSocket] Failed to parse message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('[WebSocket] Disconnected');
        this.setConnectionState('disconnected');
        this.stopHeartbeat();
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error);
        this.setConnectionState('error');
      };
    } catch (error) {
      console.error('[WebSocket] Connection failed:', error);
      this.setConnectionState('error');
      this.attemptReconnect();
    }
  }

  disconnect(): void {
    this.stopHeartbeat();

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.setConnectionState('disconnected');
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

    setTimeout(() => {
      this.connect();
    }, delay);
  }

  // ============================================
  // Heartbeat / Keep-Alive
  // ============================================

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      this.send({ type: 'ping', data: {}, timestamp: new Date().toISOString() });
    }, 30000); // Send ping every 30 seconds
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  // ============================================
  // Message Handling
  // ============================================

  private handleMessage(message: WebSocketMessage): void {
    // Route to specific handlers
    const handlers = this.messageHandlers.get(message.type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message);
        } catch (error) {
          console.error(`[WebSocket] Handler error for ${message.type}:`, error);
        }
      });
    }

    // Log message receipt
    if (message.type !== 'ping') {
      console.log(`[WebSocket] Received: ${message.type}`, message.data);
    }
  }

  send(message: WebSocketMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('[WebSocket] Cannot send message - not connected');
    }
  }

  // ============================================
  // Event Subscription
  // ============================================

  subscribe(type: WebSocketMessageType, handler: MessageHandler): () => void {
    const handlers = this.messageHandlers.get(type);
    if (handlers) {
      handlers.add(handler);
    }

    // Return unsubscribe function
    return () => {
      handlers?.delete(handler);
    };
  }

  onStateChange(handler: (state: ConnectionState) => void): () => void {
    this.stateChangeHandlers.add(handler);

    // Return unsubscribe function
    return () => {
      this.stateChangeHandlers.delete(handler);
    };
  }

  private setConnectionState(state: ConnectionState): void {
    this.connectionState = state;
    this.stateChangeHandlers.forEach(handler => handler(state));
  }

  getConnectionState(): ConnectionState {
    return this.connectionState;
  }

  isConnected(): boolean {
    return this.connectionState === 'connected';
  }

  // ============================================
  // Convenience Subscriptions
  // ============================================

  onCognitiveModeChange(handler: (mode: any) => void): () => void {
    return this.subscribe('cognitive_mode_changed', (msg) => handler(msg.data));
  }

  onReasoningLevelChange(handler: (level: any) => void): () => void {
    return this.subscribe('reasoning_level_changed', (msg) => handler(msg.data));
  }

  onMCPServerUpdate(handler: (server: any) => void): () => void {
    return this.subscribe('mcp_server_updated', (msg) => handler(msg.data));
  }

  onAgentTaskUpdate(handler: (task: any) => void): () => void {
    return this.subscribe('agent_task_updated', (msg) => handler(msg.data));
  }

  onMemoryEntryCreate(handler: (entry: any) => void): () => void {
    return this.subscribe('memory_entry_created', (msg) => handler(msg.data));
  }

  onCheckpointCreate(handler: (checkpoint: any) => void): () => void {
    return this.subscribe('checkpoint_created', (msg) => handler(msg.data));
  }

  onOrchestraStatusUpdate(handler: (status: any) => void): () => void {
    return this.subscribe('orchestra_status_updated', (msg) => handler(msg.data));
  }

  onSystemMetricsUpdate(handler: (metrics: any) => void): () => void {
    return this.subscribe('system_metrics_updated', (msg) => handler(msg.data));
  }
}

// Singleton instance
export const wsManager = new WebSocketManager();

// React hook helpers
export function useWebSocket() {
  return {
    connect: () => wsManager.connect(),
    disconnect: () => wsManager.disconnect(),
    send: (message: WebSocketMessage) => wsManager.send(message),
    subscribe: (type: WebSocketMessageType, handler: MessageHandler) => wsManager.subscribe(type, handler),
    onStateChange: (handler: (state: ConnectionState) => void) => wsManager.onStateChange(handler),
    isConnected: () => wsManager.isConnected(),
    getState: () => wsManager.getConnectionState(),

    // Convenience methods
    onCognitiveModeChange: (handler: (mode: any) => void) => wsManager.onCognitiveModeChange(handler),
    onReasoningLevelChange: (handler: (level: any) => void) => wsManager.onReasoningLevelChange(handler),
    onMCPServerUpdate: (handler: (server: any) => void) => wsManager.onMCPServerUpdate(handler),
    onAgentTaskUpdate: (handler: (task: any) => void) => wsManager.onAgentTaskUpdate(handler),
    onMemoryEntryCreate: (handler: (entry: any) => void) => wsManager.onMemoryEntryCreate(handler),
    onCheckpointCreate: (handler: (checkpoint: any) => void) => wsManager.onCheckpointCreate(handler),
    onOrchestraStatusUpdate: (handler: (status: any) => void) => wsManager.onOrchestraStatusUpdate(handler),
    onSystemMetricsUpdate: (handler: (metrics: any) => void) => wsManager.onSystemMetricsUpdate(handler),
  };
}

export default wsManager;
