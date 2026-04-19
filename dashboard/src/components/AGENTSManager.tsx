/**
 * AMOS AGENTS.md Manager
 *
 * AGENTS.md is the emerging 2026 standard for guiding AI coding agents.
 *
 * Research shows:
 * - "5x Performance Boost for AI Coding Agents" with proper AGENTS.md
 * - Supported by OpenAI Codex, Augment, Jules, Claude Code
 * - "Think of it as a README for agents" - agents.md official
 *
 * This component provides:
 * - Visual AGENTS.md editor
 * - Hierarchical file browser (global → project → package)
 * - Template library
 * - Validation and optimization hints
 * - Preview mode
 *
 * Based on the official AGENTS.md specification from agents.md
 */

import React, { useState } from 'react';

interface AGENTSection {
  id: string;
  title: string;
  content: string;
  required: boolean;
  description: string;
}

interface AGENTSFile {
  id: string;
  path: string;
  scope: 'global' | 'project' | 'package';
  sections: AGENTSection[];
  lastModified: string;
  isActive: boolean;
}

const DEFAULT_SECTIONS: AGENTSection[] = [
  {
    id: 'overview',
    title: 'Overview',
    content: '',
    required: true,
    description: 'High-level description of the project and its purpose',
  },
  {
    id: 'architecture',
    title: 'Architecture',
    content: '',
    required: true,
    description: 'System architecture, key components, and design patterns',
  },
  {
    id: 'tech-stack',
    title: 'Tech Stack',
    content: '',
    required: true,
    description: 'Programming languages, frameworks, and tools used',
  },
  {
    id: 'commands',
    title: 'Common Commands',
    content: '',
    required: false,
    description: 'Build, test, lint, and other frequently used commands',
  },
  {
    id: 'testing',
    title: 'Testing Guidelines',
    content: '',
    required: false,
    description: 'How to run tests, test patterns, and coverage requirements',
  },
  {
    id: 'patterns',
    title: 'Code Patterns',
    content: '',
    required: false,
    description: 'Preferred coding patterns and conventions',
  },
  {
    id: 'constraints',
    title: 'Constraints & Rules',
    content: '',
    required: false,
    description: 'Specific constraints, limitations, or rules to follow',
  },
];

const TEMPLATES = {
  'react-ts': {
    name: 'React + TypeScript',
    description: 'Modern React app with TypeScript',
    sections: {
      'overview': 'A React application built with TypeScript, following modern best practices.',
      'architecture': 'Component-based architecture with clear separation of concerns.\n\n- Components: Reusable UI components\n- Hooks: Custom React hooks for logic\n- Services: API and external service integrations\n- Utils: Helper functions and utilities',
      'tech-stack': '- React 18+\n- TypeScript 5+\n- Vite (build tool)\n- Vitest (testing)\n- ESLint + Prettier (code quality)',
      'commands': '```bash\n# Development\nnpm run dev\n\n# Build\nnpm run build\n\n# Test\nnpm run test\n\n# Lint\nnpm run lint\n\n# Type check\nnpm run type-check\n```',
      'testing': 'All new features must include tests.\n\n- Unit tests for utilities\n- Component tests with React Testing Library\n- E2E tests for critical user flows\n\nRun tests: `npm run test`',
      'patterns': '- Use functional components with hooks\n- Prefer composition over inheritance\n- Use TypeScript strict mode\n- Follow React best practices from the React team',
      'constraints': '- No class components (use hooks instead)\n- No any types (use unknown with type guards)\n- No console.log in production code',
    },
  },
  'python-api': {
    name: 'Python FastAPI',
    description: 'Python API with FastAPI framework',
    sections: {
      'overview': 'A Python API built with FastAPI, providing RESTful endpoints.',
      'architecture': 'Clean architecture with separation of concerns.\n\n- Routes: API endpoint definitions\n- Services: Business logic\n- Models: Pydantic models for validation\n- Database: SQLAlchemy ORM models',
      'tech-stack': '- Python 3.11+\n- FastAPI (web framework)\n- SQLAlchemy (ORM)\n- Pydantic (validation)\n- pytest (testing)\n- Ruff (linting)',
      'commands': '```bash\n# Install dependencies\npip install -r requirements.txt\n\n# Run development server\nuvicorn main:app --reload\n\n# Run tests\npytest\n\n# Lint\nruff check .\n\n# Format\nruff format .\n```',
      'testing': 'All endpoints must have tests.\n\n- Unit tests for services\n- Integration tests for endpoints\n- Use pytest fixtures for database setup\n\nRun tests: `pytest`',
      'patterns': '- Use Pydantic models for request/response validation\n- Use dependency injection for services\n- Follow RESTful conventions\n- Use type hints everywhere',
      'constraints': '- No raw SQL (use ORM)\n- No global state\n- Always handle exceptions with proper HTTP status codes',
    },
  },
  'node-backend': {
    name: 'Node.js Backend',
    description: 'Node.js API with Express',
    sections: {
      'overview': 'A Node.js backend API built with Express and TypeScript.',
      'architecture': 'Layered architecture with clear separation.\n\n- Controllers: Request handling\n- Services: Business logic\n- Models: Data access\n- Middleware: Cross-cutting concerns',
      'tech-stack': '- Node.js 20+\n- Express (web framework)\n- TypeScript 5+\n- Prisma (ORM)\n- Jest (testing)\n- ESLint + Prettier',
      'commands': '```bash\n# Install\nnpm install\n\n# Development\nnpm run dev\n\n# Build\nnpm run build\n\n# Test\nnpm test\n\n# Lint\nnpm run lint\n```',
      'testing': 'Comprehensive test coverage required.\n\n- Unit tests for services\n- Integration tests for routes\n- Use jest mocks for external services\n\nRun tests: `npm test`',
      'patterns': '- Use async/await for async operations\n- Use middleware for auth, logging, error handling\n- Follow RESTful API conventions\n- Use dependency injection',
      'constraints': '- No callback hell (use async/await)\n- No var (use const/let)\n- Always validate input with Zod or similar',
    },
  },
};

export const AGENTSManager: React.FC = () => {
  const [files, setFiles] = useState<AGENTSFile[]>([
    {
      id: 'global',
      path: '~/.config/AMOS/AGENTS.md',
      scope: 'global',
      sections: DEFAULT_SECTIONS.map(s => ({
        ...s,
        content: s.id === 'overview' ? 'Global preferences for all AMOS projects' : '',
      })),
      lastModified: new Date(Date.now() - 86400000).toISOString(),
      isActive: true,
    },
    {
      id: 'project',
      path: './AGENTS.md',
      scope: 'project',
      sections: DEFAULT_SECTIONS.map(s => ({
        ...s,
        content: s.id === 'overview' ? 'AMOS Dashboard Project' : '',
      })),
      lastModified: new Date().toISOString(),
      isActive: true,
    },
  ]);

  const [selectedFile, setSelectedFile] = useState<string>('project');
  const [selectedSection, setSelectedSection] = useState<string>('overview');
  const [activeTab, setActiveTab] = useState<'edit' | 'preview' | 'templates'>('edit');
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');

  const currentFile = files.find(f => f.id === selectedFile);
  const currentSection = currentFile?.sections.find(s => s.id === selectedSection);

  const updateSectionContent = (fileId: string, sectionId: string, content: string) => {
    setFiles(prev => prev.map(f =>
      f.id === fileId
        ? {
            ...f,
            sections: f.sections.map(s =>
              s.id === sectionId ? { ...s, content } : s
            ),
            lastModified: new Date().toISOString(),
          }
        : f
    ));
  };

  const applyTemplate = (templateKey: string) => {
    const template = TEMPLATES[templateKey as keyof typeof TEMPLATES];
    if (!template) return;

    setFiles(prev => prev.map(f =>
      f.id === selectedFile
        ? {
            ...f,
            sections: f.sections.map(s => ({
              ...s,
              content: template.sections[s.id as keyof typeof template.sections] || s.content,
            })),
            lastModified: new Date().toISOString(),
          }
        : f
    ));
    setActiveTab('edit');
  };

  const getScopeColor = (scope: string) => {
    switch (scope) {
      case 'global': return '#8b5cf6';
      case 'project': return '#3b82f6';
      case 'package': return '#10b981';
      default: return '#6b7280';
    }
  };

  const getCompletionPercentage = (file: AGENTSFile) => {
    const requiredSections = file.sections.filter(s => s.required);
    const completedRequired = requiredSections.filter(s => s.content.trim().length > 0).length;
    return Math.round((completedRequired / requiredSections.length) * 100);
  };

  return (
    <div style={containerStyle}>
      {/* Header */}
      <div style={headerStyle}>
        <div>
          <h3 style={titleStyle}>📋 AGENTS.md Manager</h3>
          <p style={subtitleStyle}>
            Standard agent instructions • 5x performance boost with proper context
          </p>
        </div>
        <div style={statsContainerStyle}>
          <div style={statBoxStyle}>
            <span style={statNumberStyle}>{files.length}</span>
            <span style={statLabelStyle}>Files</span>
          </div>
          <div style={statBoxStyle}>
            <span style={statNumberStyle}>
              {currentFile ? getCompletionPercentage(currentFile) : 0}%
            </span>
            <span style={statLabelStyle}>Complete</span>
          </div>
        </div>
      </div>

      {/* Quote Banner */}
      <div style={quoteBannerStyle}>
        <em>"AGENTS.md is a simple, open format for guiding coding agents. Think of it as a README for agents."</em>
        <span style={quoteAuthorStyle}>— agents.md official, 2026</span>
      </div>

      {/* Main Layout */}
      <div style={mainLayoutStyle}>
        {/* Sidebar - File Browser */}
        <div style={sidebarStyle}>
          <div style={sidebarTitleStyle}>AGENTS.md Files</div>

          {files.map(file => (
            <div
              key={file.id}
              onClick={() => setSelectedFile(file.id)}
              style={{
                ...fileItemStyle,
                backgroundColor: selectedFile === file.id ? 'rgba(99, 102, 241, 0.2)' : 'transparent',
                borderColor: selectedFile === file.id ? 'rgba(99, 102, 241, 0.5)' : 'transparent',
              }}
            >
              <div style={fileHeaderStyle}>
                <span style={{
                  ...fileScopeBadgeStyle,
                  backgroundColor: `${getScopeColor(file.scope)}20`,
                  color: getScopeColor(file.scope),
                }}>
                  {file.scope}
                </span>
                <span style={fileActiveStyle}>
                  {file.isActive ? '●' : '○'}
                </span>
              </div>
              <div style={filePathStyle}>{file.path}</div>
              <div style={fileProgressStyle}>
                <div style={fileProgressBarStyle}>
                  <div
                    style={{
                      ...fileProgressFillStyle,
                      width: `${getCompletionPercentage(file)}%`,
                    }}
                  />
                </div>
                <span style={fileProgressTextStyle}>{getCompletionPercentage(file)}%</span>
              </div>
            </div>
          ))}

          <button style={addFileButtonStyle}>
            + New AGENTS.md
          </button>
        </div>

        {/* Content Area */}
        <div style={contentStyle}>
          {/* Tabs */}
          <div style={tabsContainerStyle}>
            <button
              onClick={() => setActiveTab('edit')}
              style={{
                ...tabButtonStyle,
                backgroundColor: activeTab === 'edit' ? 'rgba(99, 102, 241, 0.3)' : 'transparent',
                borderBottom: activeTab === 'edit' ? '2px solid #6366f1' : '2px solid transparent',
              }}
            >
              ✏️ Edit
            </button>
            <button
              onClick={() => setActiveTab('preview')}
              style={{
                ...tabButtonStyle,
                backgroundColor: activeTab === 'preview' ? 'rgba(99, 102, 241, 0.3)' : 'transparent',
                borderBottom: activeTab === 'preview' ? '2px solid #6366f1' : '2px solid transparent',
              }}
            >
              👁️ Preview
            </button>
            <button
              onClick={() => setActiveTab('templates')}
              style={{
                ...tabButtonStyle,
                backgroundColor: activeTab === 'templates' ? 'rgba(99, 102, 241, 0.3)' : 'transparent',
                borderBottom: activeTab === 'templates' ? '2px solid #6366f1' : '2px solid transparent',
              }}
            >
              📚 Templates
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'edit' && currentFile && (
            <div style={editContainerStyle}>
              {/* Section Selector */}
              <div style={sectionSelectorStyle}>
                {currentFile.sections.map(section => (
                  <button
                    key={section.id}
                    onClick={() => setSelectedSection(section.id)}
                    style={{
                      ...sectionButtonStyle,
                      backgroundColor: selectedSection === section.id ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255,255,255,0.05)',
                      borderColor: selectedSection === section.id ? 'rgba(99, 102, 241, 0.5)' : 'rgba(255,255,255,0.1)',
                      borderLeft: `4px solid ${section.content.trim() ? '#10b981' : section.required ? '#ef4444' : '#6b7280'}`,
                    }}
                  >
                    <div style={sectionButtonTitleStyle}>
                      {section.title}
                      {section.required && <span style={requiredBadgeStyle}>Required</span>}
                    </div>
                    <div style={sectionButtonDescStyle}>{section.description}</div>
                    <div style={sectionStatusStyle}>
                      {section.content.trim() ? '✓ Completed' : section.required ? '⚠️ Required' : 'Optional'}
                    </div>
                  </button>
                ))}
              </div>

              {/* Editor */}
              {currentSection && (
                <div style={editorContainerStyle}>
                  <div style={editorHeaderStyle}>
                    <span style={editorTitleStyle}>{currentSection.title}</span>
                    {currentSection.required && <span style={editorRequiredStyle}>Required</span>}
                  </div>
                  <div style={editorDescriptionStyle}>{currentSection.description}</div>
                  <textarea
                    value={currentSection.content}
                    onChange={(e) => updateSectionContent(currentFile.id, currentSection.id, e.target.value)}
                    placeholder={`Enter ${currentSection.title.toLowerCase()}...`}
                    style={textareaStyle}
                  />
                  <div style={editorHintsStyle}>
                    <span style={hintStyle}>💡 Tip: Be specific and include examples</span>
                    <span style={charCountStyle}>{currentSection.content.length} chars</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'preview' && currentFile && (
            <div style={previewContainerStyle}>
              <div style={previewHeaderStyle}>
                <span style={previewPathStyle}>{currentFile.path}</span>
                <span style={previewScopeStyle} style={{ color: getScopeColor(currentFile.scope) }}>
                  {currentFile.scope} scope
                </span>
              </div>
              <div style={previewContentStyle}>
                {currentFile.sections.map(section => (
                  <div key={section.id} style={previewSectionStyle}>
                    <h4 style={previewSectionTitleStyle}>{section.title}</h4>
                    {section.content ? (
                      <div style={previewSectionContentStyle}>
                        {section.content.split('\n').map((line, i) => (
                          <p key={i} style={previewLineStyle}>{line || <br />}</p>
                        ))}
                      </div>
                    ) : (
                      <div style={previewEmptyStyle}>
                        {section.required ? '⚠️ Required section not completed' : '(Optional section - empty)'}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'templates' && (
            <div style={templatesContainerStyle}>
              <div style={templatesHeaderStyle}>
                <h4 style={templatesTitleStyle}>Choose a Template</h4>
                <p style={templatesSubtitleStyle}>Pre-configured AGENTS.md files for common project types</p>
              </div>
              <div style={templatesGridStyle}>
                {Object.entries(TEMPLATES).map(([key, template]) => (
                  <div
                    key={key}
                    onClick={() => setSelectedTemplate(key)}
                    style={{
                      ...templateCardStyle,
                      borderColor: selectedTemplate === key ? '#6366f1' : 'rgba(255,255,255,0.1)',
                      backgroundColor: selectedTemplate === key ? 'rgba(99, 102, 241, 0.1)' : 'rgba(255,255,255,0.03)',
                    }}
                  >
                    <div style={templateNameStyle}>{template.name}</div>
                    <div style={templateDescStyle}>{template.description}</div>
                    <div style={templateFeaturesStyle}>
                      {Object.keys(template.sections).length} sections configured
                    </div>
                    {selectedTemplate === key && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          applyTemplate(key);
                        }}
                        style={applyTemplateButtonStyle}
                      >
                        Apply Template
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer Info */}
      <div style={footerStyle}>
        <div style={footerLeftStyle}>
          <span style={footerBadgeStyle}>Standard v1.0</span>
          <span style={footerTextStyle}>Compatible with Codex, Augment, Claude</span>
        </div>
        <div style={footerRightStyle}>
          <a href="https://agents.md" target="_blank" rel="noopener noreferrer" style={footerLinkStyle}>
            agents.md ↗
          </a>
        </div>
      </div>
    </div>
  );
};

// Styles
const containerStyle: React.CSSProperties = {
  background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(15, 23, 42, 0.95) 100%)',
  backdropFilter: 'blur(20px)',
  borderRadius: '24px',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  padding: '24px',
  maxWidth: '1200px',
  fontFamily: 'Inter, system-ui, sans-serif',
  color: '#f8fafc',
  boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
};

const headerStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '20px',
  flexWrap: 'wrap',
  gap: '16px',
};

const titleStyle: React.CSSProperties = {
  fontSize: '22px',
  fontWeight: 700,
  margin: '0 0 4px 0',
  background: 'linear-gradient(90deg, #6366f1, #8b5cf6)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
};

const subtitleStyle: React.CSSProperties = {
  fontSize: '13px',
  opacity: 0.7,
  margin: 0,
};

const statsContainerStyle: React.CSSProperties = {
  display: 'flex',
  gap: '12px',
};

const statBoxStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.05)',
  padding: '12px 16px',
  borderRadius: '12px',
  textAlign: 'center',
  minWidth: '70px',
};

const statNumberStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '20px',
  fontWeight: 700,
  color: '#818cf8',
};

const statLabelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '11px',
  opacity: 0.7,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
  marginTop: '4px',
};

const quoteBannerStyle: React.CSSProperties = {
  background: 'rgba(99, 102, 241, 0.1)',
  border: '1px solid rgba(99, 102, 241, 0.3)',
  borderRadius: '12px',
  padding: '16px 20px',
  fontSize: '14px',
  color: '#818cf8',
  marginBottom: '20px',
  lineHeight: 1.5,
};

const quoteAuthorStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '12px',
  opacity: 0.7,
  marginTop: '8px',
  fontStyle: 'normal',
};

const mainLayoutStyle: React.CSSProperties = {
  display: 'flex',
  gap: '20px',
  marginBottom: '20px',
  minHeight: '500px',
};

const sidebarStyle: React.CSSProperties = {
  width: '280px',
  background: 'rgba(255, 255, 255, 0.03)',
  borderRadius: '16px',
  padding: '16px',
};

const sidebarTitleStyle: React.CSSProperties = {
  fontSize: '12px',
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
  opacity: 0.6,
  marginBottom: '12px',
};

const fileItemStyle: React.CSSProperties = {
  padding: '12px',
  borderRadius: '10px',
  border: '2px solid',
  marginBottom: '8px',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
};

const fileHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '8px',
};

const fileScopeBadgeStyle: React.CSSProperties = {
  fontSize: '10px',
  padding: '3px 8px',
  borderRadius: '4px',
  fontWeight: 600,
  textTransform: 'uppercase',
};

const fileActiveStyle: React.CSSProperties = {
  fontSize: '10px',
  color: '#10b981',
};

const filePathStyle: React.CSSProperties = {
  fontSize: '12px',
  fontFamily: 'JetBrains Mono, monospace',
  opacity: 0.8,
  marginBottom: '8px',
  wordBreak: 'break-all',
};

const fileProgressStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
};

const fileProgressBarStyle: React.CSSProperties = {
  flex: 1,
  height: '4px',
  background: 'rgba(255, 255, 255, 0.1)',
  borderRadius: '2px',
  overflow: 'hidden',
};

const fileProgressFillStyle: React.CSSProperties = {
  height: '100%',
  background: '#10b981',
  borderRadius: '2px',
  transition: 'width 0.3s ease',
};

const fileProgressTextStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.7,
  minWidth: '30px',
};

const addFileButtonStyle: React.CSSProperties = {
  width: '100%',
  padding: '12px',
  background: 'rgba(255, 255, 255, 0.05)',
  border: '2px dashed rgba(255, 255, 255, 0.2)',
  borderRadius: '10px',
  color: '#f8fafc',
  cursor: 'pointer',
  fontSize: '13px',
  marginTop: '8px',
  transition: 'all 0.3s ease',
};

const contentStyle: React.CSSProperties = {
  flex: 1,
  background: 'rgba(255, 255, 255, 0.03)',
  borderRadius: '16px',
  overflow: 'hidden',
  display: 'flex',
  flexDirection: 'column',
};

const tabsContainerStyle: React.CSSProperties = {
  display: 'flex',
  borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
};

const tabButtonStyle: React.CSSProperties = {
  flex: 1,
  padding: '14px',
  background: 'transparent',
  border: 'none',
  color: '#f8fafc',
  cursor: 'pointer',
  fontSize: '14px',
  fontWeight: 500,
  transition: 'all 0.3s ease',
};

const editContainerStyle: React.CSSProperties = {
  display: 'flex',
  flex: 1,
  overflow: 'hidden',
};

const sectionSelectorStyle: React.CSSProperties = {
  width: '280px',
  borderRight: '1px solid rgba(255, 255, 255, 0.1)',
  padding: '16px',
  overflow: 'auto',
};

const sectionButtonStyle: React.CSSProperties = {
  width: '100%',
  padding: '12px',
  border: '1px solid',
  borderRadius: '10px',
  background: 'rgba(255, 255, 255, 0.05)',
  color: '#f8fafc',
  cursor: 'pointer',
  textAlign: 'left',
  marginBottom: '8px',
  transition: 'all 0.3s ease',
};

const sectionButtonTitleStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  fontWeight: 600,
  fontSize: '14px',
  marginBottom: '4px',
};

const requiredBadgeStyle: React.CSSProperties = {
  fontSize: '9px',
  background: 'rgba(239, 68, 68, 0.2)',
  color: '#ef4444',
  padding: '2px 6px',
  borderRadius: '4px',
  fontWeight: 600,
};

const sectionButtonDescStyle: React.CSSProperties = {
  fontSize: '11px',
  opacity: 0.6,
  marginBottom: '4px',
};

const sectionStatusStyle: React.CSSProperties = {
  fontSize: '10px',
  opacity: 0.7,
};

const editorContainerStyle: React.CSSProperties = {
  flex: 1,
  padding: '20px',
  display: 'flex',
  flexDirection: 'column',
};

const editorHeaderStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  marginBottom: '8px',
};

const editorTitleStyle: React.CSSProperties = {
  fontSize: '18px',
  fontWeight: 700,
};

const editorRequiredStyle: React.CSSProperties = {
  fontSize: '10px',
  background: 'rgba(239, 68, 68, 0.2)',
  color: '#ef4444',
  padding: '3px 8px',
  borderRadius: '4px',
  fontWeight: 600,
};

const editorDescriptionStyle: React.CSSProperties = {
  fontSize: '13px',
  opacity: 0.7,
  marginBottom: '16px',
};

const textareaStyle: React.CSSProperties = {
  flex: 1,
  padding: '16px',
  background: 'rgba(0, 0, 0, 0.3)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '10px',
  color: '#f8fafc',
  fontSize: '14px',
  fontFamily: 'JetBrains Mono, monospace',
  lineHeight: 1.6,
  resize: 'none',
  outline: 'none',
  minHeight: '200px',
};

const editorHintsStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  marginTop: '12px',
  fontSize: '12px',
};

const hintStyle: React.CSSProperties = {
  opacity: 0.7,
};

const charCountStyle: React.CSSProperties = {
  opacity: 0.5,
};

const previewContainerStyle: React.CSSProperties = {
  flex: 1,
  padding: '24px',
  overflow: 'auto',
};

const previewHeaderStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '12px 16px',
  background: 'rgba(0, 0, 0, 0.2)',
  borderRadius: '8px',
  marginBottom: '20px',
};

const previewPathStyle: React.CSSProperties = {
  fontFamily: 'JetBrains Mono, monospace',
  fontSize: '13px',
  opacity: 0.8,
};

const previewScopeStyle: React.CSSProperties = {
  fontSize: '12px',
  fontWeight: 600,
  textTransform: 'uppercase',
};

const previewContentStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: '24px',
};

const previewSectionStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.03)',
  borderRadius: '12px',
  padding: '20px',
};

const previewSectionTitleStyle: React.CSSProperties = {
  fontSize: '16px',
  fontWeight: 700,
  marginBottom: '12px',
  color: '#818cf8',
};

const previewSectionContentStyle: React.CSSProperties = {};

const previewLineStyle: React.CSSProperties = {
  margin: 0,
  lineHeight: 1.6,
  fontSize: '14px',
};

const previewEmptyStyle: React.CSSProperties = {
  fontSize: '13px',
  opacity: 0.5,
  fontStyle: 'italic',
};

const templatesContainerStyle: React.CSSProperties = {
  flex: 1,
  padding: '24px',
  overflow: 'auto',
};

const templatesHeaderStyle: React.CSSProperties = {
  marginBottom: '24px',
};

const templatesTitleStyle: React.CSSProperties = {
  fontSize: '18px',
  fontWeight: 700,
  marginBottom: '8px',
};

const templatesSubtitleStyle: React.CSSProperties = {
  fontSize: '13px',
  opacity: 0.7,
};

const templatesGridStyle: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
  gap: '16px',
};

const templateCardStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.03)',
  border: '2px solid',
  borderRadius: '16px',
  padding: '20px',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
};

const templateNameStyle: React.CSSProperties = {
  fontSize: '16px',
  fontWeight: 700,
  marginBottom: '8px',
};

const templateDescStyle: React.CSSProperties = {
  fontSize: '13px',
  opacity: 0.7,
  marginBottom: '12px',
};

const templateFeaturesStyle: React.CSSProperties = {
  fontSize: '12px',
  opacity: 0.6,
  marginBottom: '16px',
};

const applyTemplateButtonStyle: React.CSSProperties = {
  width: '100%',
  padding: '10px',
  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
  border: 'none',
  borderRadius: '8px',
  color: 'white',
  fontSize: '13px',
  fontWeight: 600,
  cursor: 'pointer',
};

const footerStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '12px 16px',
  background: 'rgba(255, 255, 255, 0.03)',
  borderRadius: '10px',
  fontSize: '12px',
};

const footerLeftStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
};

const footerBadgeStyle: React.CSSProperties = {
  background: 'rgba(16, 185, 129, 0.2)',
  color: '#10b981',
  padding: '4px 10px',
  borderRadius: '6px',
  fontWeight: 600,
};

const footerTextStyle: React.CSSProperties = {
  opacity: 0.7,
};

const footerRightStyle: React.CSSProperties = {};

const footerLinkStyle: React.CSSProperties = {
  color: '#818cf8',
  textDecoration: 'none',
  opacity: 0.8,
  transition: 'opacity 0.3s ease',
};

export default AGENTSManager;
