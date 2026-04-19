/**
 * ExecutionTerminal - Real-time terminal component
 *
 * Provides terminal-like interface for real-time execution streaming.
 * Uses WebSocket for live stdout/stderr streaming.
 *
 * Features:
 * - Live output streaming
 * - ANSI color support
 * - Terminal scrollback
 * - Copy to clipboard
 * - Download output
 *
 * @author Trang Phan
 * @version 2.0.0
 */

import React, { useRef, useEffect, useState } from 'react';
import { useExecutionWebSocket } from '../hooks/useExecutionWebSocket';

interface ExecutionTerminalProps {
  executionId: string | null;
  onClose?: () => void;
  height?: string;
}

export const ExecutionTerminal: React.FC<ExecutionTerminalProps> = ({
  executionId,
  onClose,
  height = '400px',
}) => {
  const { state, connect, disconnect, clearMessages } = useExecutionWebSocket();
  const terminalRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  // Connect when executionId changes
  useEffect(() => {
    if (executionId) {
      connect(executionId);
    }
    return () => {
      disconnect();
    };
  }, [executionId, connect, disconnect]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (autoScroll && terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [state.messages, autoScroll]);

  // Filter messages based on search
  const filteredMessages = searchTerm
    ? state.messages.filter((m) =>
        m.data.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : state.messages;

  // Copy to clipboard
  const copyOutput = () => {
    const text = state.messages.map((m) => m.data).join('\n');
    navigator.clipboard.writeText(text);
  };

  // Download output
  const downloadOutput = () => {
    const text = state.messages.map((m) => m.data).join('\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `execution-${executionId}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Get status color
  const getStatusColor = () => {
    switch (state.status) {
      case 'running':
        return '#60a5fa';
      case 'completed':
        return '#4ade80';
      case 'error':
        return '#f87171';
      default:
        return '#94a3b8';
    }
  };

  // Format timestamp
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <div
      style={{
        background: 'rgba(0, 0, 0, 0.9)',
        borderRadius: '12px',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '12px 16px',
          background: 'rgba(255, 255, 255, 0.05)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              background: getStatusColor(),
              boxShadow: `0 0 8px ${getStatusColor()}`,
              animation: state.status === 'running' ? 'pulse 1s infinite' : 'none',
            }}
          />
          <span
            style={{
              fontSize: '14px',
              fontWeight: 600,
              color: '#e2e8f0',
              textTransform: 'uppercase',
              letterSpacing: '1px',
            }}
          >
            {state.status === 'idle' && 'Terminal'}
            {state.status === 'connecting' && 'Connecting...'}
            {state.status === 'running' && 'Running...'}
            {state.status === 'completed' && 'Completed'}
            {state.status === 'error' && 'Error'}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* Search */}
          <input
            type="text"
            placeholder="Search..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              padding: '6px 12px',
              borderRadius: '6px',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              background: 'rgba(0, 0, 0, 0.5)',
              color: '#e2e8f0',
              fontSize: '12px',
              width: '150px',
            }}
          />

          {/* Auto-scroll toggle */}
          <button
            onClick={() => setAutoScroll(!autoScroll)}
            style={{
              padding: '6px 10px',
              borderRadius: '6px',
              border: 'none',
              background: autoScroll ? 'rgba(96, 165, 250, 0.2)' : 'transparent',
              color: autoScroll ? '#60a5fa' : '#64748b',
              cursor: 'pointer',
              fontSize: '12px',
            }}
            title="Auto-scroll"
          >
            ↓
          </button>

          {/* Clear */}
          <button
            onClick={clearMessages}
            style={{
              padding: '6px 10px',
              borderRadius: '6px',
              border: 'none',
              background: 'transparent',
              color: '#64748b',
              cursor: 'pointer',
              fontSize: '12px',
            }}
            title="Clear"
          >
            🗑️
          </button>

          {/* Copy */}
          <button
            onClick={copyOutput}
            style={{
              padding: '6px 10px',
              borderRadius: '6px',
              border: 'none',
              background: 'transparent',
              color: '#64748b',
              cursor: 'pointer',
              fontSize: '12px',
            }}
            title="Copy to clipboard"
          >
            📋
          </button>

          {/* Download */}
          <button
            onClick={downloadOutput}
            style={{
              padding: '6px 10px',
              borderRadius: '6px',
              border: 'none',
              background: 'transparent',
              color: '#64748b',
              cursor: 'pointer',
              fontSize: '12px',
            }}
            title="Download"
          >
            💾
          </button>

          {/* Close */}
          {onClose && (
            <button
              onClick={onClose}
              style={{
                padding: '6px 10px',
                borderRadius: '6px',
                border: 'none',
                background: 'transparent',
                color: '#64748b',
                cursor: 'pointer',
                fontSize: '12px',
              }}
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Terminal Output */}
      <div
        ref={terminalRef}
        style={{
          flex: 1,
          height,
          overflowY: 'auto',
          padding: '16px',
          fontFamily: 'Consolas, Monaco, "Courier New", monospace',
          fontSize: '13px',
          lineHeight: '1.6',
          background: 'rgba(0, 0, 0, 0.8)',
        }}
        onScroll={() => {
          if (terminalRef.current) {
            const { scrollTop, scrollHeight, clientHeight } = terminalRef.current;
            setAutoScroll(scrollHeight - scrollTop - clientHeight < 50);
          }
        }}
      >
        {filteredMessages.length === 0 ? (
          <div
            style={{
              textAlign: 'center',
              color: '#475569',
              paddingTop: '100px',
            }}
          >
            {state.status === 'idle' ? (
              <>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>⌨️</div>
                <p>Execute code to see output here</p>
              </>
            ) : state.status === 'connecting' ? (
              <>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔌</div>
                <p>Connecting to execution stream...</p>
              </>
            ) : null}
          </div>
        ) : (
          filteredMessages.map((message, index) => (
            <div
              key={index}
              style={{
                display: 'flex',
                gap: '12px',
                marginBottom: '4px',
              }}
            >
              {/* Timestamp */}
              <span
                style={{
                  color: '#475569',
                  fontSize: '11px',
                  minWidth: '70px',
                  userSelect: 'none',
                }}
              >
                {formatTime(message.timestamp)}
              </span>

              {/* Message Type Indicator */}
              <span
                style={{
                  color:
                    message.type === 'stderr'
                      ? '#f87171'
                      : message.type === 'error'
                      ? '#ef4444'
                      : '#64748b',
                  fontSize: '11px',
                  minWidth: '50px',
                  userSelect: 'none',
                  textTransform: 'uppercase',
                }}
              >
                {message.type}
              </span>

              {/* Message Content */}
              <span
                style={{
                  color:
                    message.type === 'stderr'
                      ? '#f87171'
                      : message.type === 'error'
                      ? '#ef4444'
                      : message.type === 'status'
                      ? '#60a5fa'
                      : '#e2e8f0',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {message.data}
              </span>
            </div>
          ))
        )}

        {state.status === 'running' && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginTop: '8px',
              color: '#60a5fa',
            }}
          >
            <span style={{ animation: 'blink 1s infinite' }}>▊</span>
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '8px 16px',
          background: 'rgba(255, 255, 255, 0.03)',
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
          fontSize: '12px',
          color: '#64748b',
        }}
      >
        <div>
          {state.error ? (
            <span style={{ color: '#f87171' }}>❌ {state.error}</span>
          ) : (
            <>
              {filteredMessages.length} lines
              {searchTerm && ` (filtered from ${state.messages.length})`}
            </>
          )}
        </div>
        <div>
          {executionId && (
            <span style={{ fontFamily: 'monospace' }}>ID: {executionId.slice(0, 8)}</span>
          )}
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0; }
        }
      `}</style>
    </div>
  );
};

export default ExecutionTerminal;
