/**
 * AMOS Frontend Application - Main Entry Point
 *
 * Integrates all 9 AMOS cognitive subsystems into a unified interface:
 * 1. ModeSwitcher - 3 cognitive modes (Seed/Growth/Full)
 * 2. ReasoningBars - L1-L3 reasoning visualization
 * 3. MCPIntegration - Model Context Protocol servers
 * 4. BackgroundAgents - Task queue management
 * 5. PersistentMemory - 5-system memory architecture
 * 6. RewindCheckpoints - Time travel debugging
 * 7. AMOSDashboard - Master control panel
 * 8. AgentOrchestra - Multi-agent orchestration
 * 9. AGENTSManager - AGENTS.md editor
 *
 * Architecture: AMOS Brain 14-Layer Cognitive System
 * Design: Glassmorphism 2.0
 * Creator: Trang Phan
 */

import React, { useState } from 'react';
import { ModeSwitcher } from './components/ModeSwitcher';
import { ReasoningBars } from './components/ReasoningBars';
import { MCPIntegration } from './components/MCPIntegration';
import { BackgroundAgents } from './components/BackgroundAgents';
import { PersistentMemory } from './components/PersistentMemory';
import { RewindCheckpoints } from './components/RewindCheckpoints';
import { AMOSDashboard } from './components/AMOSDashboard';
import { AgentOrchestra } from './components/AgentOrchestra';
import { AGENTSManager } from './components/AGENTSManager';
import { EquationDashboard } from './components/EquationDashboard';
import { ExecutionDashboard } from './components/ExecutionDashboard';

type ViewMode = 'dashboard' | 'mode' | 'reasoning' | 'mcp' | 'agents' | 'memory' | 'checkpoints' | 'orchestra' | 'agents-md' | 'equations' | 'execution';

interface NavItem {
  id: ViewMode;
  label: string;
  icon: string;
  description: string;
}

const NAV_ITEMS: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: '🎛️', description: 'Master control panel' },
  { id: 'mode', label: 'Cognitive Mode', icon: '🧠', description: 'Seed/Growth/Full' },
  { id: 'reasoning', label: 'Reasoning', icon: '📊', description: 'L1-L3 visualization' },
  { id: 'equations', label: 'Equations', icon: '🔬', description: 'Equation system' },
  { id: 'execution', label: 'Execution', icon: '🚀', description: 'Sandbox & Browser' },
  { id: 'mcp', label: 'MCP', icon: '🔌', description: 'Model Context Protocol' },
  { id: 'agents', label: 'Background Agents', icon: '🤖', description: 'Task queue' },
  { id: 'memory', label: 'Memory', icon: '💾', description: '5-system memory' },
  { id: 'checkpoints', label: 'Checkpoints', icon: '⏪', description: 'Time travel' },
  { id: 'orchestra', label: 'Orchestra', icon: '🎼', description: 'Multi-agent viz' },
  { id: 'agents-md', label: 'AGENTS.md', icon: '📋', description: 'Standard editor' },
];

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewMode>('dashboard');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [cognitiveMode, setCognitiveMode] = useState<'seed' | 'growth' | 'full'>('growth');

  // Get visible nav items based on cognitive mode
  const getVisibleNavItems = () => {
    switch (cognitiveMode) {
      case 'seed':
        return NAV_ITEMS.filter(item => ['dashboard', 'mode', 'reasoning'].includes(item.id));
      case 'growth':
        return NAV_ITEMS.filter(item =>
          ['dashboard', 'mode', 'reasoning', 'equations', 'execution', 'mcp', 'agents', 'memory'].includes(item.id)
        );
      case 'full':
        return NAV_ITEMS;
    }
  };

  const visibleNavItems = getVisibleNavItems();

  // Render current view
  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <AMOSDashboard />;
      case 'mode':
        return <ModeSwitcher />;
      case 'reasoning':
        return <ReasoningBars />;
      case 'equations':
        return <EquationDashboard />;
      case 'execution':
        return <ExecutionDashboard />;
      case 'mcp':
        return <MCPIntegration />;
      case 'agents':
        return <BackgroundAgents />;
      case 'memory':
        return <PersistentMemory />;
      case 'checkpoints':
        return <RewindCheckpoints />;
      case 'orchestra':
        return <AgentOrchestra />;
      case 'agents-md':
        return <AGENTSManager />;
      default:
        return <AMOSDashboard />;
    }
  };

  return (
    <div style={appContainerStyle}>
      {/* Header */}
      <header style={headerStyle}>
        <div style={headerLeftStyle}>
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            style={menuButtonStyle}
          >
            {isSidebarOpen ? '◀' : '▶'}
          </button>
          <div style={brandStyle}>
            <span style={logoStyle}>∞</span>
            <div>
              <h1 style={titleStyle}>AMOS</h1>
              <p style={taglineStyle}>Absolute Meta Operating System</p>
            </div>
          </div>
        </div>
        <div style={headerCenterStyle}>
          <div style={modeIndicatorStyle}>
            <span style={modeIconStyle}>
              {cognitiveMode === 'seed' ? '🌱' : cognitiveMode === 'growth' ? '🌿' : '🌳'}
            </span>
            <span style={modeTextStyle}>
              {cognitiveMode.charAt(0).toUpperCase() + cognitiveMode.slice(1)} Mode
            </span>
            <span style={modeLayersStyle}>
              ({cognitiveMode === 'seed' ? 1 : cognitiveMode === 'growth' ? 3 : 14} layers)
            </span>
          </div>
        </div>
        <div style={headerRightStyle}>
          <button
            onClick={() => setCognitiveMode('seed')}
            style={{
              ...modeToggleStyle,
              backgroundColor: cognitiveMode === 'seed' ? 'rgba(245, 158, 11, 0.3)' : 'rgba(255,255,255,0.05)',
            }}
          >
            🌱
          </button>
          <button
            onClick={() => setCognitiveMode('growth')}
            style={{
              ...modeToggleStyle,
              backgroundColor: cognitiveMode === 'growth' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(255,255,255,0.05)',
            }}
          >
            🌿
          </button>
          <button
            onClick={() => setCognitiveMode('full')}
            style={{
              ...modeToggleStyle,
              backgroundColor: cognitiveMode === 'full' ? 'rgba(99, 102, 241, 0.3)' : 'rgba(255,255,255,0.05)',
            }}
          >
            🌳
          </button>
        </div>
      </header>

      {/* Main Layout */}
      <div style={mainLayoutStyle}>
        {/* Sidebar Navigation */}
        {isSidebarOpen && (
          <nav style={sidebarStyle}>
            <div style={sidebarHeaderStyle}>
              <span style={sidebarTitleStyle}>Cognitive Systems</span>
              <span style={sidebarCountStyle}>{visibleNavItems.length}/9</span>
            </div>

            {visibleNavItems.map(item => (
              <button
                key={item.id}
                onClick={() => setCurrentView(item.id)}
                style={{
                  ...navButtonStyle,
                  backgroundColor: currentView === item.id ? 'rgba(99, 102, 241, 0.2)' : 'transparent',
                  borderLeft: currentView === item.id ? '4px solid #6366f1' : '4px solid transparent',
                }}
              >
                <span style={navIconStyle}>{item.icon}</span>
                <div style={navContentStyle}>
                  <span style={navLabelStyle}>{item.label}</span>
                  <span style={navDescStyle}>{item.description}</span>
                </div>
              </button>
            ))}

            {cognitiveMode !== 'full' && (
              <div style={upgradePromptStyle}>
                <span style={upgradeIconStyle}>🔒</span>
                <span style={upgradeTextStyle}>
                  {cognitiveMode === 'seed'
                    ? '6 more systems in Growth'
                    : '3 more systems in Full'}
                </span>
              </div>
            )}
          </nav>
        )}

        {/* Main Content Area */}
        <main style={contentStyle}>
          <div style={viewContainerStyle}>
            {renderView()}
          </div>
        </main>
      </div>

      {/* Footer */}
      <footer style={footerStyle}>
        <div style={footerLeftStyle}>
          <span style={versionBadgeStyle}>v3.0.0</span>
          <span style={footerTextStyle}>AMOS Brain vInfinity</span>
        </div>
        <div style={footerCenterStyle}>
          <span style={statusStyle}>🟢 All Systems Operational</span>
          <span style={separatorStyle}>•</span>
          <span style={complianceStyle}>✓ L1-L3 Compliant</span>
          <span style={separatorStyle}>•</span>
          <span style={lawsStyle}>✓ 6 Global Laws Active</span>
        </div>
        <div style={footerRightStyle}>
          <span style={creatorStyle}>by Trang Phan</span>
        </div>
      </footer>
    </div>
  );
};

// Styles
const appContainerStyle: React.CSSProperties = {
  minHeight: '100vh',
  background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)',
  color: '#f8fafc',
  fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
  display: 'flex',
  flexDirection: 'column',
};

const headerStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '16px 24px',
  background: 'rgba(15, 23, 42, 0.8)',
  backdropFilter: 'blur(20px)',
  borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
  position: 'sticky',
  top: 0,
  zIndex: 100,
};

const headerLeftStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '16px',
};

const menuButtonStyle: React.CSSProperties = {
  width: '40px',
  height: '40px',
  borderRadius: '10px',
  border: '1px solid rgba(255,255,255,0.2)',
  background: 'rgba(255,255,255,0.05)',
  color: '#f8fafc',
  fontSize: '16px',
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  transition: 'all 0.3s ease',
};

const brandStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
};

const logoStyle: React.CSSProperties = {
  fontSize: '32px',
  fontWeight: 700,
  background: 'linear-gradient(135deg, #6366f1, #a855f7)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
};

const titleStyle: React.CSSProperties = {
  fontSize: '20px',
  fontWeight: 700,
  margin: 0,
  background: 'linear-gradient(90deg, #6366f1, #a855f7)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
};

const taglineStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.6,
  margin: 0,
  letterSpacing: '0.5px',
};

const headerCenterStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
};

const modeIndicatorStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  padding: '8px 16px',
  background: 'rgba(255, 255, 255, 0.05)',
  borderRadius: '20px',
  border: '1px solid rgba(255, 255, 255, 0.1)',
};

const modeIconStyle: React.CSSProperties = {
  fontSize: '16px',
};

const modeTextStyle: React.CSSProperties = {
  fontSize: '13px',
  fontWeight: 600,
  textTransform: 'capitalize',
};

const modeLayersStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.6,
};

const headerRightStyle: React.CSSProperties = {
  display: 'flex',
  gap: '8px',
};

const modeToggleStyle: React.CSSProperties = {
  width: '40px',
  height: '40px',
  borderRadius: '10px',
  border: '1px solid rgba(255,255,255,0.2)',
  fontSize: '18px',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
};

const mainLayoutStyle: React.CSSProperties = {
  display: 'flex',
  flex: 1,
  overflow: 'hidden',
};

const sidebarStyle: React.CSSProperties = {
  width: '280px',
  background: 'rgba(15, 23, 42, 0.5)',
  borderRight: '1px solid rgba(255, 255, 255, 0.1)',
  padding: '20px',
  overflowY: 'auto',
  display: 'flex',
  flexDirection: 'column',
};

const sidebarHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '16px',
  paddingBottom: '12px',
  borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
};

const sidebarTitleStyle: React.CSSProperties = {
  fontSize: '11px',
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
  opacity: 0.5,
};

const sidebarCountStyle: React.CSSProperties = {
  fontSize: '11px',
  background: 'rgba(99, 102, 241, 0.2)',
  color: '#818cf8',
  padding: '2px 8px',
  borderRadius: '10px',
};

const navButtonStyle: React.CSSProperties = {
  width: '100%',
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  padding: '12px',
  borderRadius: '10px',
  border: 'none',
  background: 'transparent',
  color: '#f8fafc',
  cursor: 'pointer',
  textAlign: 'left',
  marginBottom: '8px',
  transition: 'all 0.3s ease',
};

const navIconStyle: React.CSSProperties = {
  fontSize: '20px',
  width: '28px',
  textAlign: 'center',
};

const navContentStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  flex: 1,
};

const navLabelStyle: React.CSSProperties = {
  fontSize: '14px',
  fontWeight: 500,
};

const navDescStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.6,
  marginTop: '2px',
};

const upgradePromptStyle: React.CSSProperties = {
  marginTop: 'auto',
  padding: '12px',
  background: 'rgba(99, 102, 241, 0.1)',
  borderRadius: '10px',
  border: '1px dashed rgba(99, 102, 241, 0.3)',
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  fontSize: '12px',
};

const upgradeIconStyle: React.CSSProperties = {
  fontSize: '14px',
};

const upgradeTextStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.8,
};

const contentStyle: React.CSSProperties = {
  flex: 1,
  overflow: 'auto',
  padding: '24px',
};

const viewContainerStyle: React.CSSProperties = {
  maxWidth: '1400px',
  margin: '0 auto',
};

const footerStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '12px 24px',
  background: 'rgba(15, 23, 42, 0.8)',
  backdropFilter: 'blur(20px)',
  borderTop: '1px solid rgba(255, 255, 255, 0.1)',
  fontSize: '12px',
};

const footerLeftStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
};

const versionBadgeStyle: React.CSSProperties = {
  background: 'rgba(99, 102, 241, 0.2)',
  color: '#818cf8',
  padding: '4px 10px',
  borderRadius: '6px',
  fontWeight: 600,
};

const footerTextStyle: React.CSSProperties = {
  opacity: 0.6,
};

const footerCenterStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
};

const statusStyle: React.CSSProperties = {
  color: '#10b981',
};

const separatorStyle: React.CSSProperties = {
  opacity: 0.3,
};

const complianceStyle: React.CSSProperties = {
  color: '#818cf8',
};

const lawsStyle: React.CSSProperties = {
  color: '#a855f7',
};

const footerRightStyle: React.CSSProperties = {};

const creatorStyle: React.CSSProperties = {
  opacity: 0.6,
};

export default App;
