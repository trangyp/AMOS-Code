/**
 * AMOS Mode Switcher Component
 * Adaptive UI with Seed/Growth/Full modes based on 2025 UI/UX research
 * Glassmorphism 2.0 design with cognitive load management
 *
 * Research basis:
 * - Cognitive Load Theory (Sweller): 4±1 chunks → 3-action Seed Mode
 * - Miller's Law: 7±2 items → 6-action Growth Mode
 * - Progressive Disclosure (Nielsen Norman): Hide complexity until needed
 * - Flow State (Csikszentmihalyi): Match challenge to skill level
 */

import React, { useState, useEffect } from 'react';

interface ModeConfig {
  id: 'seed' | 'growth' | 'full';
  name: string;
  icon: string;
  description: string;
  actions: string[];
  layers: string[];
  complexity: 'low' | 'medium' | 'high';
  targetUsers: string;
  color: string;
}

const MODES: ModeConfig[] = [
  {
    id: 'seed',
    name: '🌱 Seed Mode',
    icon: '🌱',
    description: 'Beginner-friendly. 3 essential actions. Hides 14-layer complexity.',
    actions: ['Ask AMOS', 'Browse Knowledge', 'View Results'],
    layers: ['L1: Brain Loader'],
    complexity: 'low',
    targetUsers: '70% of users',
    color: '#10b981', // emerald
  },
  {
    id: 'growth',
    name: '🌿 Growth Mode',
    icon: '🌿',
    description: 'Intermediate. 6 actions (Miller\'s Law). Shows L1-L3 reasoning.',
    actions: ['Ask', '12 Domains', 'Memory', 'History', 'API', 'Settings'],
    layers: ['L1: Brain Loader', 'L2: Rule of 2', 'L3: Rule of 4'],
    complexity: 'medium',
    targetUsers: '25% of users',
    color: '#3b82f6', // blue
  },
  {
    id: 'full',
    name: '🌳 Full Mode',
    icon: '🌳',
    description: 'Expert. All 14 layers + 14 subsystems. Complete transparency.',
    actions: ['All Features', 'Agent Orchestra', 'Workflows', 'Subsystems', 'L1-L14', 'API', 'Memory', 'Settings'],
    layers: ['L1-L14: All Layers', '14 Subsystems', 'Organism OS'],
    complexity: 'high',
    targetUsers: '5% of users',
    color: '#6366f1', // indigo
  },
];

interface ModeSwitcherProps {
  currentMode: 'seed' | 'growth' | 'full';
  onModeChange: (mode: 'seed' | 'growth' | 'full') => void;
  userExpertise?: 'beginner' | 'intermediate' | 'expert';
  autoAdjust?: boolean;
}

export const ModeSwitcher: React.FC<ModeSwitcherProps> = ({
  currentMode,
  onModeChange,
  userExpertise = 'beginner',
  autoAdjust = true,
}) => {
  const [recommendedMode, setRecommendedMode] = useState<'seed' | 'growth' | 'full'>('seed');

  // Auto-adjust based on user expertise (Flow State - Csikszentmihalyi)
  useEffect(() => {
    if (!autoAdjust) return;
    const expertiseMap: Record<string, 'seed' | 'growth' | 'full'> = {
      beginner: 'seed',
      intermediate: 'growth',
      expert: 'full',
    };
    setRecommendedMode(expertiseMap[userExpertise] || 'seed');
  }, [userExpertise, autoAdjust]);

  const currentConfig = MODES.find(m => m.id === currentMode);

  return (
    <div className="amos-mode-switcher" style={containerStyle}>
      {/* Header */}
      <div style={headerStyle}>
        <h3 style={titleStyle}>AMOS Cognitive Interface</h3>
        <p style={subtitleStyle}>
          Adaptive Mode: <span style={{ color: currentConfig?.color }}>{currentConfig?.name}</span>
        </p>
      </div>

      {/* Mode Cards - Glassmorphism 2.0 */}
      <div style={cardsContainerStyle}>
        {MODES.map((mode) => {
          const isActive = currentMode === mode.id;
          const isRecommended = recommendedMode === mode.id;

          return (
            <button
              key={mode.id}
              onClick={() => onModeChange(mode.id)}
              style={{
                ...cardStyle,
                ...(isActive ? cardActiveStyle : {}),
                borderColor: isActive ? mode.color : 'rgba(255,255,255,0.1)',
              }}
            >
              {/* Icon & Name */}
              <div style={cardHeaderStyle}>
                <span style={{ fontSize: '24px' }}>{mode.icon}</span>
                <div style={{ flex: 1, textAlign: 'left' }}>
                  <div style={{ fontWeight: 600, fontSize: '15px' }}>
                    {mode.name}
                  </div>
                  {isRecommended && (
                    <span style={recommendedBadgeStyle}>✨ Recommended</span>
                  )}
                </div>
                {isActive && <span style={{ color: mode.color }}>●</span>}
              </div>

              {/* Description */}
              <p style={descriptionStyle}>{mode.description}</p>

              {/* Stats */}
              <div style={statsStyle}>
                <span style={statStyle}>
                  <strong>{mode.actions.length}</strong> actions
                </span>
                <span style={statStyle}>
                  <strong>{mode.layers.length}</strong> layer{mode.layers.length > 1 ? 's' : ''}
                </span>
                <span style={{ ...statStyle, opacity: 0.6 }}>
                  {mode.targetUsers}
                </span>
              </div>

              {/* Active Indicator */}
              {isActive && (
                <div
                  style={{
                    position: 'absolute',
                    left: 0,
                    top: '20%',
                    bottom: '20%',
                    width: '4px',
                    borderRadius: '2px',
                    backgroundColor: mode.color,
                  }}
                />
              )}
            </button>
          );
        })}
      </div>

      {/* Cognitive Load Warning for Full Mode */}
      {currentMode === 'full' && (
        <div style={warningStyle}>
          <strong>⚠️ High Cognitive Load:</strong> Full Mode exposes all 14 cognitive layers.
          <br />
          Consider <strong>Growth Mode</strong> for better focus and productivity.
        </div>
      )}

      {/* Current Mode Features */}
      <div style={featuresContainerStyle}>
        <h4 style={featuresTitleStyle}>Available Actions:</h4>
        <div style={featuresListStyle}>
          {currentConfig?.actions.map((action, idx) => (
            <span key={idx} style={featureTagStyle}>
              {action}
            </span>
          ))}
        </div>
      </div>

      {/* Expertise Selector */}
      <div style={expertiseContainerStyle}>
        <label style={expertiseLabelStyle}>Your Experience Level:</label>
        <select
          value={userExpertise}
          onChange={(e) => setRecommendedMode(e.target.value as any)}
          style={expertiseSelectStyle}
        >
          <option value="beginner">🌱 Beginner (Start with Seed)</option>
          <option value="intermediate">🌿 Intermediate (Try Growth)</option>
          <option value="expert">🌳 Expert (Use Full)</option>
        </select>
      </div>
    </div>
  );
};

// Glassmorphism 2.0 Styles
const containerStyle: React.CSSProperties = {
  background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(15, 23, 42, 0.95) 100%)',
  backdropFilter: 'blur(20px)',
  borderRadius: '24px',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  padding: '28px',
  maxWidth: '480px',
  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
  color: '#f8fafc',
  boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255,255,255,0.1)',
};

const headerStyle: React.CSSProperties = {
  marginBottom: '24px',
  textAlign: 'center',
};

const titleStyle: React.CSSProperties = {
  fontSize: '22px',
  fontWeight: 700,
  margin: '0 0 8px 0',
  background: 'linear-gradient(90deg, #6366f1, #a855f7)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
};

const subtitleStyle: React.CSSProperties = {
  fontSize: '14px',
  opacity: 0.8,
  margin: 0,
};

const cardsContainerStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '12px',
  marginBottom: '20px',
};

const cardStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.03)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '16px',
  padding: '16px 20px',
  cursor: 'pointer',
  textAlign: 'left',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  position: 'relative',
  overflow: 'hidden',
  display: 'flex',
  flexDirection: 'column',
  gap: '8px',
};

const cardActiveStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.08)',
  boxShadow: '0 4px 20px rgba(99, 102, 241, 0.25), inset 0 1px 0 rgba(255,255,255,0.1)',
  transform: 'translateX(4px)',
};

const cardHeaderStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
};

const recommendedBadgeStyle: React.CSSProperties = {
  fontSize: '10px',
  backgroundColor: 'rgba(16, 185, 129, 0.2)',
  color: '#10b981',
  padding: '2px 8px',
  borderRadius: '12px',
  marginTop: '2px',
  display: 'inline-block',
};

const descriptionStyle: React.CSSProperties = {
  fontSize: '13px',
  opacity: 0.7,
  margin: 0,
  lineHeight: 1.4,
};

const statsStyle: React.CSSProperties = {
  display: 'flex',
  gap: '12px',
  fontSize: '12px',
  marginTop: '4px',
};

const statStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.05)',
  padding: '4px 10px',
  borderRadius: '8px',
  fontWeight: 500,
};

const warningStyle: React.CSSProperties = {
  marginTop: '16px',
  padding: '14px 18px',
  backgroundColor: 'rgba(245, 158, 11, 0.1)',
  border: '1px solid rgba(245, 158, 11, 0.3)',
  borderRadius: '12px',
  fontSize: '13px',
  color: '#fbbf24',
  lineHeight: 1.5,
};

const featuresContainerStyle: React.CSSProperties = {
  marginTop: '20px',
  paddingTop: '20px',
  borderTop: '1px solid rgba(255, 255, 255, 0.1)',
};

const featuresTitleStyle: React.CSSProperties = {
  fontSize: '13px',
  fontWeight: 600,
  margin: '0 0 12px 0',
  opacity: 0.9,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
};

const featuresListStyle: React.CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: '8px',
};

const featureTagStyle: React.CSSProperties = {
  fontSize: '12px',
  backgroundColor: 'rgba(99, 102, 241, 0.15)',
  color: '#818cf8',
  padding: '6px 14px',
  borderRadius: '20px',
  border: '1px solid rgba(99, 102, 241, 0.3)',
  fontWeight: 500,
};

const expertiseContainerStyle: React.CSSProperties = {
  marginTop: '20px',
  paddingTop: '20px',
  borderTop: '1px solid rgba(255, 255, 255, 0.1)',
};

const expertiseLabelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '12px',
  fontWeight: 600,
  marginBottom: '8px',
  opacity: 0.8,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
};

const expertiseSelectStyle: React.CSSProperties = {
  width: '100%',
  padding: '10px 14px',
  borderRadius: '10px',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  backgroundColor: 'rgba(255, 255, 255, 0.05)',
  color: '#f8fafc',
  fontSize: '14px',
  cursor: 'pointer',
  outline: 'none',
};

export default ModeSwitcher;
