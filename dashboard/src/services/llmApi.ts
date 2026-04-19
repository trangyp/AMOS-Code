/**
 * AMOS LLM API Service
 *
 * HTTP client for LLM operations with local and cloud providers.
 * Supports chat completion, streaming, and provider management.
 *
 * Creator: Trang Phan
 * Version: 3.0.0
 */

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Types
export interface Message {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  metadata?: Record<string, unknown>;
}

export interface ChatRequest {
  messages: Message[];
  model?: string;
  provider?: 'ollama' | 'openai' | 'anthropic';
  temperature?: number;
  max_tokens?: number;
  stream?: boolean;
}

export interface ChatResponse {
  content: string;
  model: string;
  provider: string;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
  };
  latency_ms: number;
  timestamp: string;
}

export interface ProviderInfo {
  name: string;
  models: string[];
  enabled: boolean;
}

export interface ProvidersResponse {
  providers: ProviderInfo[];
}

// HTTP Client
async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

// ============================================
// LLM Chat API
// ============================================

export async function chatCompletion(request: ChatRequest): Promise<ChatResponse> {
  return fetchAPI<ChatResponse>('/api/v1/llm/chat', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export async function* chatStream(request: ChatRequest): AsyncGenerator<string, void, unknown> {
  const url = `${API_BASE_URL}/api/v1/llm/chat/stream`;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ ...request, stream: true }),
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('No response body');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') {
            return;
          }
          if (data.startsWith('ERROR:')) {
            throw new Error(data.slice(6));
          }
          yield data;
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

// ============================================
// Provider Management API
// ============================================

export async function getProviders(): Promise<ProvidersResponse> {
  return fetchAPI<ProvidersResponse>('/api/v1/llm/providers');
}

export async function getModels(provider?: string): Promise<{
  provider?: string;
  models: string[];
  models_by_provider?: Record<string, string[]>;
}> {
  const params = provider ? `?provider=${encodeURIComponent(provider)}` : '';
  return fetchAPI(`/api/v1/llm/models${params}`);
}

// ============================================
// Convenience Functions
// ============================================

export async function simpleChat(
  message: string,
  options?: { model?: string; provider?: string; systemPrompt?: string }
): Promise<string> {
  const messages: Message[] = [];

  if (options?.systemPrompt) {
    messages.push({ role: 'system', content: options.systemPrompt });
  }

  messages.push({ role: 'user', content: message });

  const response = await chatCompletion({
    messages,
    model: options?.model,
    provider: options?.provider as any,
  });

  return response.content;
}

export async function* simpleChatStream(
  message: string,
  options?: { model?: string; provider?: string; systemPrompt?: string }
): AsyncGenerator<string, void, unknown> {
  const messages: Message[] = [];

  if (options?.systemPrompt) {
    messages.push({ role: 'system', content: options.systemPrompt });
  }

  messages.push({ role: 'user', content: message });

  yield* chatStream({
    messages,
    model: options?.model,
    provider: options?.provider as any,
  });
}

// Default export
export default {
  chatCompletion,
  chatStream,
  getProviders,
  getModels,
  simpleChat,
  simpleChatStream,
};
