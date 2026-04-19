/**
 * Execution Service - API client for AMOS Execution Platform
 *
 * Provides interface to:
 * - Execute code in sandboxes (E2B/Daytona/Docker)
 * - Browse web with Playwright
 * - Research topics with Tavily/Brave
 * - Get platform status
 *
 * @author Trang Phan
 * @version 2.0.0
 */

// Types
export interface ExecutionResult {
  status: 'success' | 'error' | 'timeout';
  stdout: string;
  stderr: string;
  exit_code: number;
  execution_time_ms: number;
  provider: string;
  artifacts?: Record<string, any>;
  results?: any[];
}

export interface ExecutionStatus {
  healthy: boolean;
  sandbox_providers: string[];
  browser_providers: string[];
  research_providers: string[];
  metrics: {
    sandbox_executions: number;
    browser_sessions: number;
    research_queries: number;
    errors: number;
  };
}

export interface CodeExecutionRequest {
  code: string;
  language: string;
  timeoutSeconds: number;
  provider?: string;
}

export interface BrowserRequest {
  url: string;
  actions?: BrowserAction[];
  captureScreenshot: boolean;
}

export interface BrowserAction {
  action: 'navigate' | 'click' | 'type' | 'scroll' | 'wait' | 'screenshot' | 'extract';
  selector?: string;
  text?: string;
  timeout_ms?: number;
}

export interface ResearchRequest {
  query: string;
  numResults: number;
  includeCitations: boolean;
  provider: string;
}

// API Configuration
const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) || 'http://localhost:8000';

// Helper for API calls
async function apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API Error: ${response.status} - ${error}`);
  }

  return response.json();
}

/**
 * Get execution platform status
 */
export async function getStatus(): Promise<ExecutionStatus> {
  return apiCall<ExecutionStatus>('/execution/status');
}

/**
 * Execute code in secure sandbox
 */
export async function executeCode(
  request: CodeExecutionRequest,
  executionId?: string
): Promise<ExecutionResult> {
  return apiCall<ExecutionResult>('/execution/code', {
    method: 'POST',
    body: JSON.stringify({
      code: request.code,
      language: request.language,
      timeout_seconds: request.timeoutSeconds,
      preferred_provider: request.provider,
      execution_id: executionId,
    }),
  });
}

/**
 * Generate unique execution ID for streaming
 */
export function generateExecutionId(): string {
  return `exec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Browse web with browser automation
 */
export async function browseWeb(request: BrowserRequest): Promise<ExecutionResult> {
  return apiCall<ExecutionResult>('/execution/browse', {
    method: 'POST',
    body: JSON.stringify({
      url: request.url,
      actions: request.actions,
      capture_screenshot: request.captureScreenshot,
    }),
  });
}

/**
 * Research topic with web search
 */
export async function researchTopic(request: ResearchRequest): Promise<ExecutionResult> {
  return apiCall<ExecutionResult>('/execution/research', {
    method: 'POST',
    body: JSON.stringify({
      query: request.query,
      num_results: request.numResults,
      include_citations: request.includeCitations,
      preferred_provider: request.provider,
    }),
  });
}

// Export service object
export const executionService = {
  getStatus,
  executeCode,
  browseWeb,
  researchTopic,
};

export default executionService;
