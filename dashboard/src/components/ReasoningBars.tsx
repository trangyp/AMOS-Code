/**
 * AMOS Reasoning Bars Component
 * Real-time visualization of L1-L3 cognitive layer activation
 * Shows Rule of 2 (dual perspectives) and Rule of 4 (four quadrants) progress
 *
 * Based on 2025 UI research:
 * - Streaming reasoning (OpenAI o1, Claude 3.5)
 * - Deterministic feedback loops (System 2 thinking)
 * - Real-time cognitive transparency
 */

import React, { useState, useEffect } from 'react';

interface LayerState {
  id: string;
  name: string;
  description: string;
  progress: number;
  status: 'idle' | 'active' | 'complete' | 'error';
  details?: string[];
  color: string;
}

interface ReasoningBarsProps {
  isThinking: boolean;
  currentStep?: string;
  onComplete?: () => void;
}

export const ReasoningBars: React.FC<ReasoningBarsProps> = ({
  isThinking,
  currentStep,
  onComplete,
}) => {
  const [layers, setLayers] = useState<LayerState[]>([
    {
      id: 'L1',
      name: 'L1: Brain Loader',
      description: 'Initialize cognitive engines',
      progress: 0,
      status: 'idle',
      details: ['Loading knowledge base', 'Activating kernels', 'Checking laws'],
      color: '#6366f1',
    },
    {
      id: 'L2',
      name: 'L2: Rule of 2',
      description: 'Dual perspective analysis',
      progress: 0,
      status: 'idle',
      details: ['Perspective 1: Technical', 'Perspective 2: User', 'Synthesizing'],
      color: '#8b5cf6',
    },
    {
      id: 'L3',
      name: 'L3: Rule of 4',
      description: 'Four quadrant analysis',
      progress: 0,
      status: 'idle',
      details: ['🧬 Biological', '⚙️ Technical', '💰 Economic', '🌍 Environmental'],
      color: '#a855f7',
    },
  ]);

  const [elapsedTime, setElapsedTime] = useState(0);
  const [confidence, setConfidence] = useState(0);

  // Simulate reasoning progress
  useEffect(() => {
    if (!isThinking) {
      setLayers(prev => prev.map(l => ({ ...l, progress: 0, status: 'idle' })));
      setElapsedTime(0);
      setConfidence(0);
      return;
    }

    const interval = setInterval(() => {
      setElapsedTime(prev => prev + 100);

      setLayers(prevLayers => {
        const newLayers = [...prevLayers];

        // L1 activates first
        if (newLayers[0].progress < 100) {
          newLayers[0].progress = Math.min(100, newLayers[0].progress + 15);
          newLayers[0].status = 'active';
        } else {
          newLayers[0].status = 'complete';

          // L2 activates after L1 completes
          if (newLayers[1].progress < 100) {
            newLayers[1].progress = Math.min(100, newLayers[1].progress + 12);
            newLayers[1].status = 'active';
          } else {
            newLayers[1].status = 'complete';

            // L3 activates after L2
            if (newLayers[2].progress < 100) {
              newLayers[2].progress = Math.min(100, newLayers[2].progress + 10);
              newLayers[2].status = 'active';
            } else {
              newLayers[2].status = 'complete';
              onComplete?.();
            }
          }
        }

        // Calculate overall confidence based on progress
        const totalProgress = newLayers.reduce((sum, l) => sum + l.progress, 0);
        setConfidence(Math.round(totalProgress / 3));

        return newLayers;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [isThinking, onComplete]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'complete':
        return '✓';
      case 'active':
        return '◐';
      case 'error':
        return '✗';
      default:
        return '○';
    }
  };

  return (
    <div style={containerStyle}>
      {/* Header */}
      <div style={headerStyle}>
        <div style={headerLeftStyle}>
          <span style={brainIconStyle}>🧠</span>
          <div>
            <h3 style={titleStyle}>AMOS is thinking...</h3>
            <p style={subtitleStyle}>14-layer cognitive architecture active</p>
          </div>
        </div>
        <div style={statsStyle}>
          <span style={timeStyle}>{(elapsedTime / 1000).toFixed(1)}s</span>
          <span style={confidenceStyle}>Confidence: {confidence}%</span>
        </div>
      </div>

      {/* Progress Bars */}
      <div style={barsContainerStyle}>
        {layers.map((layer) => (
          <div key={layer.id} style={barRowStyle}>
            {/* Label */}
            <div style={labelStyle}>
              <span style={{ ...statusIconStyle, color: layer.color }}>
                {getStatusIcon(layer.status)}
              </span>
              <span style={layerNameStyle}>{layer.name}</span>
            </div>

            {/* Progress Bar */}
            <div style={progressContainerStyle}>
              <div
                style={{
                  ...progressBarStyle,
                  width: `${layer.progress}%`,
                  backgroundColor: layer.color,
                  boxShadow: layer.status === 'active'
                    ? `0 0 10px ${layer.color}`
                    : 'none',
                }}
              />
              <span style={progressTextStyle}>{layer.progress}%</span>
            </div>

            {/* Details (shown when active) */}
            {layer.status === 'active' && layer.details && (
              <div style={detailsStyle}>
                {layer.details.map((detail, idx) => (
                  <span
                    key={idx}
                    style={{
                      ...detailTagStyle,
                      opacity: idx < (layer.progress / 33) ? 1 : 0.3,
                    }}
                  >
                    {detail}
                  </span>
                ))}
              </div>
            )}

            {/* Completion checkmark */}
            {layer.status === 'complete' && (
              <div style={completeBadgeStyle}>
                ✓ {layer.id} complete
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Current Step Indicator */}
      {currentStep && (
        <div style={currentStepStyle}>
          <span style={stepLabelStyle}>Current:</span>
          <span style={stepValueStyle}>{currentStep}</span>
        </div>
      )}

      {/* Law Compliance Mini-Indicator */}
      <div style={lawsContainerStyle}>
        <span style={lawsLabelStyle}>Global Laws L1-L3:</span>
        <div style={lawsListStyle}>
          {['L1', 'L2', 'L3'].map((law, idx) => (
            <span
              key={law}
              style={{
                ...lawBadgeStyle,
                backgroundColor: idx < Math.floor(confidence / 34)
                  ? 'rgba(16, 185, 129, 0.2)'
                  : 'rgba(255, 255, 255, 0.1)',
                color: idx < Math.floor(confidence / 34)
                  ? '#10b981'
                  : 'rgba(255, 255, 255, 0.5)',
              }}
            >
              {idx < Math.floor(confidence / 34) ? '✓' : '○'} {law}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

// Glassmorphism 2.0 Styles
const containerStyle: React.CSSProperties = {
  background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%)',
  backdropFilter: 'blur(20px)',
  borderRadius: '20px',
  border: '1px solid rgba(99, 102, 241, 0.3)',
  padding: '24px',
  maxWidth: '520px',
  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
  color: '#f8fafc',
  boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 30px rgba(99, 102, 241, 0.1)',
};

const headerStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'flex-start',
  marginBottom: '20px',
};

const headerLeftStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
};

const brainIconStyle: React.CSSProperties = {
  fontSize: '28px',
  animation: 'pulse 2s infinite',
};

const titleStyle: React.CSSProperties = {
  fontSize: '18px',
  fontWeight: 700,
  margin: '0 0 4px 0',
  background: 'linear-gradient(90deg, #6366f1, #a855f7)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
};

const subtitleStyle: React.CSSProperties = {
  fontSize: '12px',
  opacity: 0.6,
  margin: 0,
};

const statsStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'flex-end',
  gap: '4px',
};

const timeStyle: React.CSSProperties = {
  fontSize: '14px',
  fontWeight: 600,
  fontFamily: 'JetBrains Mono, monospace',
  color: '#818cf8',
};

const confidenceStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.7,
  backgroundColor: 'rgba(255, 255, 255, 0.05)',
  padding: '4px 10px',
  borderRadius: '12px',
};

const barsContainerStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '16px',
};

const barRowStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '8px',
};

const labelStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  fontSize: '13px',
  fontWeight: 600,
};

const statusIconStyle: React.CSSProperties = {
  fontSize: '14px',
  width: '20px',
  textAlign: 'center',
};

const layerNameStyle: React.CSSProperties = {
  opacity: 0.9,
};

const progressContainerStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  height: '24px',
};

const progressBarStyle: React.CSSProperties = {
  height: '100%',
  borderRadius: '12px',
  transition: 'width 0.3s ease, box-shadow 0.3s ease',
  background: 'linear-gradient(90deg, currentColor, currentColor)',
  opacity: 0.9,
};

const progressTextStyle: React.CSSProperties = {
  fontSize: '12px',
  fontWeight: 600,
  fontFamily: 'JetBrains Mono, monospace',
  minWidth: '40px',
  textAlign: 'right',
  opacity: 0.8,
};

const detailsStyle: React.CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: '6px',
  marginLeft: '28px',
  marginTop: '4px',
};

const detailTagStyle: React.CSSProperties = {
  fontSize: '11px',
  backgroundColor: 'rgba(255, 255, 255, 0.05)',
  padding: '4px 10px',
  borderRadius: '8px',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  transition: 'opacity 0.3s ease',
};

const completeBadgeStyle: React.CSSProperties = {
  marginLeft: '28px',
  fontSize: '11px',
  color: '#10b981',
  opacity: 0.8,
};

const currentStepStyle: React.CSSProperties = {
  marginTop: '16px',
  padding: '12px 16px',
  backgroundColor: 'rgba(99, 102, 241, 0.1)',
  border: '1px solid rgba(99, 102, 241, 0.3)',
  borderRadius: '12px',
  display: 'flex',
  gap: '8px',
  alignItems: 'center',
};

const stepLabelStyle: React.CSSProperties = {
  fontSize: '12px',
  opacity: 0.6,
  fontWeight: 500,
};

const stepValueStyle: React.CSSProperties = {
  fontSize: '13px',
  fontWeight: 600,
  color: '#818cf8',
};

const lawsContainerStyle: React.CSSProperties = {
  marginTop: '16px',
  paddingTop: '16px',
  borderTop: '1px solid rgba(255, 255, 255, 0.1)',
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
};

const lawsLabelStyle: React.CSSProperties = {
  fontSize: '12px',
  opacity: 0.7,
  fontWeight: 500,
};

const lawsListStyle: React.CSSProperties = {
  display: 'flex',
  gap: '8px',
};

const lawBadgeStyle: React.CSSProperties = {
  fontSize: '11px',
  padding: '4px 10px',
  borderRadius: '8px',
  fontWeight: 600,
  transition: 'all 0.3s ease',
};

export default ReasoningBars;
