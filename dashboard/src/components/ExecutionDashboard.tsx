/**
 * ExecutionDashboard - AMOS Execution Platform UI
 *
 * Provides visual interface for:
 * - Secure code execution (E2B/Daytona/Docker)
 * - Browser automation (Playwright)
 * - Web research (Tavily/Brave)
 * - Real-time execution monitoring
 *
 * Architecture: Integrates with amos_execution_platform via MCP
 * Design: Glassmorphism 2.0 with execution-themed color palette
 *
 * @author Trang Phan
 * @version 2.0.0
 */

import React, { useState, useEffect, useRef } from 'react';
import { executionService, ExecutionResult, ExecutionStatus } from '../services/executionService';

// Types
interface ExecutionJob {
  id: string;
  type: 'code' | 'browser' | 'research';
  status: 'pending' | 'running' | 'success' | 'error';
  startTime: Date;
  endTime?: Date;
  result?: ExecutionResult;
  error?: string;
}

interface BrowserAction {
  action: 'navigate' | 'click' | 'type' | 'scroll' | 'wait' | 'screenshot' | 'extract';
  selector?: string;
  text?: string;
  timeout_ms?: number;
}

// Default code templates
const CODE_TEMPLATES: Record<string, string> = {
  python: `import math
import json

# AMOS Sandbox Execution
def calculate_statistics(data):
    """Calculate basic statistics."""
    n = len(data)
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / n
    std_dev = math.sqrt(variance)
    return {
        "count": n,
        "mean": mean,
        "std_dev": std_dev,
        "min": min(data),
        "max": max(data)
    }

# Example usage
data = [12, 45, 67, 23, 89, 34, 56, 78, 91, 15]
result = calculate_statistics(data)
print(json.dumps(result, indent=2))`,

  javascript: `// AMOS Sandbox Execution
const fs = require('fs');
const path = require('path');

// Example: Process data
const data = {
    timestamp: new Date().toISOString(),
    items: [1, 2, 3, 4, 5],
    metadata: {
        source: 'AMOS Sandbox',
        version: '2.0.0'
    }
};

// Calculate statistics
const stats = {
    count: data.items.length,
    sum: data.items.reduce((a, b) => a + b, 0),
    average: data.items.reduce((a, b) => a + b, 0) / data.items.length
};

console.log('Data:', JSON.stringify(data, null, 2));
console.log('Statistics:', JSON.stringify(stats, null, 2));`,

  typescript: `// AMOS Sandbox TypeScript Execution
interface DataPoint {
    id: number;
    value: number;
    label: string;
}

const processData = (data: DataPoint[]): Map<number, string> => {
    const result = new Map<number, string>();
    data.forEach(point => {
        result.set(point.id, \`\${point.label}: \${point.value}\`);
    });
    return result;
};

const sampleData: DataPoint[] = [
    { id: 1, value: 42, label: 'Alpha' },
    { id: 2, value: 84, label: 'Beta' },
    { id: 3, value: 126, label: 'Gamma' }
];

const processed = processData(sampleData);
console.log('Processed data:');
processed.forEach((value, key) => {
    console.log(\`  \${key}: \${value}\`);
});`,

  bash: `#!/bin/bash
# AMOS Sandbox Bash Execution

echo "=== AMOS Sandbox Environment ==="
echo "Date: $(date)"
echo "Working Directory: $(pwd)"
echo "User: $(whoami)"
echo ""

echo "=== System Info ==="
uname -a
echo ""

echo "=== Environment Variables ==="
env | grep -E '^(PATH|HOME|USER|HOSTNAME)' | head -10
echo ""

echo "=== Execution Complete ==="`,
};

// Languages supported
const SUPPORTED_LANGUAGES = [
  { id: 'python', name: 'Python', icon: '🐍', providers: ['e2b', 'daytona', 'docker'] },
  { id: 'javascript', name: 'JavaScript', icon: '📜', providers: ['e2b', 'daytona'] },
  { id: 'typescript', name: 'TypeScript', icon: '📘', providers: ['e2b', 'daytona'] },
  { id: 'bash', name: 'Bash/Shell', icon: '🐚', providers: ['docker'] },
  { id: 'rust', name: 'Rust', icon: '🦀', providers: ['e2b'] },
  { id: 'go', name: 'Go', icon: '🐹', providers: ['e2b', 'daytona'] },
];

// Research providers
const RESEARCH_PROVIDERS = [
  { id: 'tavily', name: 'Tavily AI', description: 'AI-optimized search (1000 free/mo)' },
  { id: 'brave', name: 'Brave Search', description: 'Privacy-focused (2000 free/mo)' },
];

export const ExecutionDashboard: React.FC = () => {
  // State
  const [activeTab, setActiveTab] = useState<'code' | 'browser' | 'research' | 'history'>('code');
  const [platformStatus, setPlatformStatus] = useState<ExecutionStatus | null>(null);
  const [jobs, setJobs] = useState<ExecutionJob[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Code execution state
  const [code, setCode] = useState(CODE_TEMPLATES.python);
  const [selectedLanguage, setSelectedLanguage] = useState('python');
  const [selectedProvider, setSelectedProvider] = useState('auto');
  const [timeoutSeconds, setTimeoutSeconds] = useState(30);

  // Browser state
  const [browserUrl, setBrowserUrl] = useState('https://example.com');
  const [browserActions] = useState<BrowserAction[]>([]);
  const [captureScreenshot, setCaptureScreenshot] = useState(true);

  // Research state
  const [researchQuery, setResearchQuery] = useState('');
  const [numResults, setNumResults] = useState(10);
  const [includeCitations, setIncludeCitations] = useState(true);
  const [researchProvider, setResearchProvider] = useState('tavily');

  // Refs
  const outputRef = useRef<HTMLDivElement>(null);

  // Fetch platform status on mount
  useEffect(() => {
    fetchPlatformStatus();
    const interval = setInterval(fetchPlatformStatus, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchPlatformStatus = async () => {
    try {
      const status = await executionService.getStatus();
      setPlatformStatus(status);
    } catch (error) {
      console.error('Failed to fetch platform status:', error);
    }
  };

  // Auto-scroll output
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [jobs]);

  // Handle language change
  const handleLanguageChange = (lang: string) => {
    setSelectedLanguage(lang);
    if (CODE_TEMPLATES[lang]) {
      setCode(CODE_TEMPLATES[lang]);
    }
    // Update available providers
    const langInfo = SUPPORTED_LANGUAGES.find(l => l.id === lang);
    if (langInfo && !langInfo.providers.includes(selectedProvider) && selectedProvider !== 'auto') {
      setSelectedProvider('auto');
    }
  };

  // Execute code
  const executeCode = async () => {
    if (!code.trim()) return;

    const jobId = `code-${Date.now()}`;
    const newJob: ExecutionJob = {
      id: jobId,
      type: 'code',
      status: 'running',
      startTime: new Date(),
    };

    setJobs(prev => [...prev, newJob]);
    setIsLoading(true);

    try {
      const result = await executionService.executeCode({
        code,
        language: selectedLanguage,
        timeoutSeconds,
        provider: selectedProvider === 'auto' ? undefined : selectedProvider,
      });

      setJobs(prev => prev.map(job =>
        job.id === jobId
          ? { ...job, status: result.status === 'success' ? 'success' : 'error', endTime: new Date(), result }
          : job
      ));
    } catch (error) {
      setJobs(prev => prev.map(job =>
        job.id === jobId
          ? { ...job, status: 'error', endTime: new Date(), error: String(error) }
          : job
      ));
    } finally {
      setIsLoading(false);
    }
  };

  // Browse web
  const browseWeb = async () => {
    if (!browserUrl.trim()) return;

    const jobId = `browser-${Date.now()}`;
    const newJob: ExecutionJob = {
      id: jobId,
      type: 'browser',
      status: 'running',
      startTime: new Date(),
    };

    setJobs(prev => [...prev, newJob]);
    setIsLoading(true);

    try {
      const result = await executionService.browseWeb({
        url: browserUrl,
        actions: browserActions,
        captureScreenshot,
      });

      setJobs(prev => prev.map(job =>
        job.id === jobId
          ? { ...job, status: result.status === 'success' ? 'success' : 'error', endTime: new Date(), result }
          : job
      ));
    } catch (error) {
      setJobs(prev => prev.map(job =>
        job.id === jobId
          ? { ...job, status: 'error', endTime: new Date(), error: String(error) }
          : job
      ));
    } finally {
      setIsLoading(false);
    }
  };

  // Research topic
  const researchTopic = async () => {
    if (!researchQuery.trim()) return;

    const jobId = `research-${Date.now()}`;
    const newJob: ExecutionJob = {
      id: jobId,
      type: 'research',
      status: 'running',
      startTime: new Date(),
    };

    setJobs(prev => [...prev, newJob]);
    setIsLoading(true);

    try {
      const result = await executionService.researchTopic({
        query: researchQuery,
        numResults: numResults,
        includeCitations,
        provider: researchProvider,
      });

      setJobs(prev => prev.map(job =>
        job.id === jobId
          ? { ...job, status: result.status === 'success' ? 'success' : 'error', endTime: new Date(), result }
          : job
      ));
    } catch (error) {
      setJobs(prev => prev.map(job =>
        job.id === jobId
          ? { ...job, status: 'error', endTime: new Date(), error: String(error) }
          : job
      ));
    } finally {
      setIsLoading(false);
    }
  };

  // Clear jobs
  const clearJobs = () => setJobs([]);

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return '#4ade80';
      case 'error': return '#f87171';
      case 'running': return '#60a5fa';
      case 'pending': return '#fbbf24';
      default: return '#9ca3af';
    }
  };

  // Render provider badges
  const renderProviderBadges = () => {
    if (!platformStatus) return null;

    const allProviders = [
      ...platformStatus.sandbox_providers.map(p => ({ name: p, type: 'sandbox' })),
      ...platformStatus.browser_providers.map(p => ({ name: p, type: 'browser' })),
      ...platformStatus.research_providers.map(p => ({ name: p, type: 'research' })),
    ];

    return (
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '12px' }}>
        {allProviders.map(provider => (
          <span
            key={provider.name}
            style={{
              padding: '4px 12px',
              borderRadius: '12px',
              fontSize: '12px',
              fontWeight: 500,
              background: provider.type === 'sandbox' ? 'rgba(96, 165, 250, 0.2)' :
                         provider.type === 'browser' ? 'rgba(251, 191, 36, 0.2)' :
                         'rgba(74, 222, 128, 0.2)',
              color: provider.type === 'sandbox' ? '#60a5fa' :
                     provider.type === 'browser' ? '#fbbf24' :
                     '#4ade80',
              border: `1px solid ${provider.type === 'sandbox' ? 'rgba(96, 165, 250, 0.3)' :
                                     provider.type === 'browser' ? 'rgba(251, 191, 36, 0.3)' :
                                     'rgba(74, 222, 128, 0.3)'}`,
            }}
          >
            {provider.type === 'sandbox' && '📦 '}
            {provider.type === 'browser' && '🌐 '}
            {provider.type === 'research' && '🔍 '}
            {provider.name}
          </span>
        ))}
      </div>
    );
  };

  return (
    <div style={{
      padding: '24px',
      background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%)',
      minHeight: '100vh',
      color: '#e2e8f0',
      fontFamily: 'system-ui, -apple-system, sans-serif',
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px',
        padding: '20px',
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        borderRadius: '16px',
        border: '1px solid rgba(255, 255, 255, 0.1)',
      }}>
        <div>
          <h1 style={{
            margin: 0,
            fontSize: '28px',
            fontWeight: 700,
            background: 'linear-gradient(135deg, #60a5fa, #a78bfa)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            🚀 Execution Platform
          </h1>
          <p style={{
            margin: '8px 0 0 0',
            fontSize: '14px',
            color: '#94a3b8',
          }}>
            Secure sandbox, browser automation, and web research
          </p>
          {renderProviderBadges()}
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
        }}>
          <div style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            background: platformStatus?.healthy ? '#4ade80' : '#f87171',
            boxShadow: platformStatus?.healthy ? '0 0 10px rgba(74, 222, 128, 0.5)' : '0 0 10px rgba(248, 113, 113, 0.5)',
            animation: platformStatus?.healthy ? 'pulse 2s infinite' : 'none',
          }} />
          <span style={{ fontSize: '14px', color: '#94a3b8' }}>
            {platformStatus?.healthy ? 'Platform Ready' : 'Platform Offline'}
          </span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div style={{
        display: 'flex',
        gap: '8px',
        marginBottom: '24px',
        padding: '4px',
        background: 'rgba(255, 255, 255, 0.05)',
        borderRadius: '12px',
        width: 'fit-content',
      }}>
        {[
          { id: 'code', label: '💻 Code', desc: 'Sandbox execution' },
          { id: 'browser', label: '🌐 Browser', desc: 'Web automation' },
          { id: 'research', label: '🔍 Research', desc: 'Web search' },
          { id: 'history', label: '📜 History', desc: `${jobs.length} jobs` },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            style={{
              padding: '12px 20px',
              borderRadius: '10px',
              border: 'none',
              background: activeTab === tab.id ? 'rgba(96, 165, 250, 0.2)' : 'transparent',
              color: activeTab === tab.id ? '#60a5fa' : '#94a3b8',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 500,
              transition: 'all 0.2s',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <span>{tab.label}</span>
            <span style={{ fontSize: '11px', opacity: 0.7 }}>{tab.desc}</span>
          </button>
        ))}
      </div>

      {/* Content Area */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 400px',
        gap: '24px',
      }}>
        {/* Left Panel - Input */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          borderRadius: '16px',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          padding: '24px',
        }}>
          {activeTab === 'code' && (
            <>
              {/* Language Selector */}
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '1px' }}>
                  Language
                </label>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {SUPPORTED_LANGUAGES.map((lang) => (
                    <button
                      key={lang.id}
                      onClick={() => handleLanguageChange(lang.id)}
                      style={{
                        padding: '8px 16px',
                        borderRadius: '8px',
                        border: 'none',
                        background: selectedLanguage === lang.id ? 'rgba(96, 165, 250, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                        color: selectedLanguage === lang.id ? '#60a5fa' : '#94a3b8',
                        cursor: 'pointer',
                        fontSize: '13px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                      }}
                    >
                      <span>{lang.icon}</span>
                      <span>{lang.name}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Provider & Timeout */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '1px' }}>
                    Provider
                  </label>
                  <select
                    value={selectedProvider}
                    onChange={(e) => setSelectedProvider(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '10px 14px',
                      borderRadius: '8px',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      background: 'rgba(0, 0, 0, 0.2)',
                      color: '#e2e8f0',
                      fontSize: '14px',
                    }}
                  >
                    <option value="auto">🔄 Auto-select</option>
                    {SUPPORTED_LANGUAGES.find(l => l.id === selectedLanguage)?.providers.map(p => (
                      <option key={p} value={p}>
                        {p === 'e2b' && '📦 E2B (Cloud)'}
                        {p === 'daytona' && '⚡ Daytona (Fast)'}
                        {p === 'docker' && '🐳 Docker (Local)'}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '1px' }}>
                    Timeout (seconds)
                  </label>
                  <input
                    type="number"
                    value={timeoutSeconds}
                    onChange={(e) => setTimeoutSeconds(Number(e.target.value))}
                    min={5}
                    max={300}
                    style={{
                      width: '100%',
                      padding: '10px 14px',
                      borderRadius: '8px',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      background: 'rgba(0, 0, 0, 0.2)',
                      color: '#e2e8f0',
                      fontSize: '14px',
                    }}
                  />
                </div>
              </div>

              {/* Code Editor */}
              <div>
                <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '1px' }}>
                  Code
                </label>
                <textarea
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  style={{
                    width: '100%',
                    height: '300px',
                    padding: '16px',
                    borderRadius: '12px',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    background: 'rgba(0, 0, 0, 0.3)',
                    color: '#e2e8f0',
                    fontFamily: 'monospace',
                    fontSize: '13px',
                    lineHeight: '1.6',
                    resize: 'vertical',
                  }}
                  spellCheck={false}
                />
              </div>

              {/* Execute Button */}
              <button
                onClick={executeCode}
                disabled={isLoading || !code.trim()}
                style={{
                  marginTop: '16px',
                  width: '100%',
                  padding: '14px 24px',
                  borderRadius: '12px',
                  border: 'none',
                  background: isLoading ? 'rgba(255, 255, 255, 0.1)' : 'linear-gradient(135deg, #60a5fa, #a78bfa)',
                  color: '#fff',
                  fontSize: '16px',
                  fontWeight: 600,
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  opacity: isLoading ? 0.5 : 1,
                  transition: 'all 0.2s',
                }}
              >
                {isLoading ? '⏳ Executing...' : '▶️ Execute Code'}
              </button>
            </>
          )}

          {activeTab === 'browser' && (
            <>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '1px' }}>
                  URL to Browse
                </label>
                <input
                  type="url"
                  value={browserUrl}
                  onChange={(e) => setBrowserUrl(e.target.value)}
                  placeholder="https://example.com"
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    background: 'rgba(0, 0, 0, 0.2)',
                    color: '#e2e8f0',
                    fontSize: '14px',
                  }}
                />
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={captureScreenshot}
                    onChange={(e) => setCaptureScreenshot(e.target.checked)}
                  />
                  <span style={{ fontSize: '14px', color: '#e2e8f0' }}>Capture screenshot</span>
                </label>
              </div>

              <button
                onClick={browseWeb}
                disabled={isLoading || !browserUrl.trim()}
                style={{
                  width: '100%',
                  padding: '14px 24px',
                  borderRadius: '12px',
                  border: 'none',
                  background: isLoading ? 'rgba(255, 255, 255, 0.1)' : 'linear-gradient(135deg, #fbbf24, #f59e0b)',
                  color: '#fff',
                  fontSize: '16px',
                  fontWeight: 600,
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  opacity: isLoading ? 0.5 : 1,
                }}
              >
                {isLoading ? '⏳ Browsing...' : '🌐 Browse Web'}
              </button>
            </>
          )}

          {activeTab === 'research' && (
            <>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '1px' }}>
                  Research Query
                </label>
                <input
                  type="text"
                  value={researchQuery}
                  onChange={(e) => setResearchQuery(e.target.value)}
                  placeholder="Enter your research question..."
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    background: 'rgba(0, 0, 0, 0.2)',
                    color: '#e2e8f0',
                    fontSize: '14px',
                  }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '1px' }}>
                    Provider
                  </label>
                  <select
                    value={researchProvider}
                    onChange={(e) => setResearchProvider(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '10px 14px',
                      borderRadius: '8px',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      background: 'rgba(0, 0, 0, 0.2)',
                      color: '#e2e8f0',
                      fontSize: '14px',
                    }}
                  >
                    {RESEARCH_PROVIDERS.map(p => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '1px' }}>
                    Results Count
                  </label>
                  <input
                    type="number"
                    value={numResults}
                    onChange={(e) => setNumResults(Number(e.target.value))}
                    min={1}
                    max={20}
                    style={{
                      width: '100%',
                      padding: '10px 14px',
                      borderRadius: '8px',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      background: 'rgba(0, 0, 0, 0.2)',
                      color: '#e2e8f0',
                      fontSize: '14px',
                    }}
                  />
                </div>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={includeCitations}
                    onChange={(e) => setIncludeCitations(e.target.checked)}
                  />
                  <span style={{ fontSize: '14px', color: '#e2e8f0' }}>Include citations for RAG</span>
                </label>
              </div>

              <button
                onClick={researchTopic}
                disabled={isLoading || !researchQuery.trim()}
                style={{
                  width: '100%',
                  padding: '14px 24px',
                  borderRadius: '12px',
                  border: 'none',
                  background: isLoading ? 'rgba(255, 255, 255, 0.1)' : 'linear-gradient(135deg, #4ade80, #22c55e)',
                  color: '#fff',
                  fontSize: '16px',
                  fontWeight: 600,
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  opacity: isLoading ? 0.5 : 1,
                }}
              >
                {isLoading ? '⏳ Researching...' : '🔍 Research Topic'}
              </button>
            </>
          )}

          {activeTab === 'history' && (
            <div style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>📜</div>
              <h3>Execution History</h3>
              <p>View all execution jobs in the right panel</p>
            </div>
          )}
        </div>

        {/* Right Panel - Output */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          borderRadius: '16px',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          padding: '24px',
          display: 'flex',
          flexDirection: 'column',
          maxHeight: 'calc(100vh - 200px)',
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '16px',
          }}>
            <h3 style={{ margin: 0, fontSize: '16px', color: '#e2e8f0' }}>
              📤 Execution Output
            </h3>
            {jobs.length > 0 && (
              <button
                onClick={clearJobs}
                style={{
                  padding: '6px 12px',
                  borderRadius: '6px',
                  border: 'none',
                  background: 'rgba(248, 113, 113, 0.2)',
                  color: '#f87171',
                  fontSize: '12px',
                  cursor: 'pointer',
                }}
              >
                Clear All
              </button>
            )}
          </div>

          <div
            ref={outputRef}
            style={{
              flex: 1,
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
            }}
          >
            {jobs.length === 0 ? (
              <div style={{
                textAlign: 'center',
                padding: '40px',
                color: '#64748b',
              }}>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>🚀</div>
                <p>No executions yet</p>
                <p style={{ fontSize: '12px' }}>Run code, browse the web, or research a topic</p>
              </div>
            ) : (
              jobs.slice().reverse().map((job) => (
                <div
                  key={job.id}
                  style={{
                    padding: '16px',
                    borderRadius: '12px',
                    background: 'rgba(0, 0, 0, 0.3)',
                    border: `1px solid ${getStatusColor(job.status)}30`,
                  }}
                >
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '8px',
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '16px' }}>
                        {job.type === 'code' && '💻'}
                        {job.type === 'browser' && '🌐'}
                        {job.type === 'research' && '🔍'}
                      </span>
                      <span style={{
                        fontSize: '12px',
                        textTransform: 'uppercase',
                        letterSpacing: '1px',
                        color: '#94a3b8',
                      }}>
                        {job.type}
                      </span>
                    </div>
                    <span style={{
                      fontSize: '11px',
                      padding: '4px 8px',
                      borderRadius: '6px',
                      background: `${getStatusColor(job.status)}20`,
                      color: getStatusColor(job.status),
                      fontWeight: 600,
                    }}>
                      {job.status}
                    </span>
                  </div>

                  {job.status === 'running' && (
                    <div style={{
                      height: '4px',
                      background: 'rgba(255, 255, 255, 0.1)',
                      borderRadius: '2px',
                      overflow: 'hidden',
                      marginBottom: '8px',
                    }}>
                      <div style={{
                        height: '100%',
                        width: '50%',
                        background: 'linear-gradient(90deg, #60a5fa, #a78bfa)',
                        borderRadius: '2px',
                        animation: 'shimmer 1.5s infinite',
                      }} />
                    </div>
                  )}

                  {job.result && (
                    <div style={{
                      fontFamily: 'monospace',
                      fontSize: '12px',
                      color: '#e2e8f0',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      maxHeight: '200px',
                      overflowY: 'auto',
                    }}>
                      {job.result.stdout && (
                        <div style={{ color: '#4ade80', marginBottom: '8px' }}>
                          {job.result.stdout}
                        </div>
                      )}
                      {job.result.stderr && (
                        <div style={{ color: '#f87171', marginBottom: '8px' }}>
                          {job.result.stderr}
                        </div>
                      )}
                      {job.result.results && (
                        <div style={{ color: '#60a5fa' }}>
                          {JSON.stringify(job.result.results, null, 2)}
                        </div>
                      )}
                    </div>
                  )}

                  {job.error && (
                    <div style={{
                      fontFamily: 'monospace',
                      fontSize: '12px',
                      color: '#f87171',
                      padding: '8px',
                      background: 'rgba(248, 113, 113, 0.1)',
                      borderRadius: '6px',
                    }}>
                      {job.error}
                    </div>
                  )}

                  <div style={{
                    fontSize: '11px',
                    color: '#64748b',
                    marginTop: '8px',
                  }}>
                    {job.startTime.toLocaleTimeString()}
                    {job.endTime && ` • ${((job.endTime.getTime() - job.startTime.getTime()) / 1000).toFixed(1)}s`}
                    {job.result?.provider && ` • ${job.result.provider}`}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(200%); }
        }
      `}</style>
    </div>
  );
};

export default ExecutionDashboard;
