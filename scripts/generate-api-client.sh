#!/bin/bash
#
# AMOS API Client Generator
#
# Automatically generates TypeScript API client from OpenAPI spec
# Ensures frontend-backend type safety and eliminates API drift.
#
# Usage:
#   ./scripts/generate-api-client.sh          # Generate client
#   ./scripts/generate-api-client.sh --watch  # Watch mode for development
#
# Creator: Trang Phan
# Version: 3.0.0

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           AMOS API Client Generator                        ║"
echo "║                                                            ║"
echo "║   Auto-generates TypeScript client from OpenAPI spec       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Configuration
BACKEND_URL="http://localhost:8000"
OPENAPI_URL="${BACKEND_URL}/openapi.json"
OUTPUT_DIR="./dashboard/src/generated"
TEMP_DIR="/tmp/amos-api-gen"

# Check dependencies
check_dependencies() {
    if ! command -v npx &> /dev/null; then
        echo -e "${RED}✗ Node.js/npx is not installed${NC}"
        exit 1
    fi

    if ! command -v curl &> /dev/null; then
        echo -e "${RED}✗ curl is not installed${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Dependencies check passed${NC}"
}

# Wait for backend
wait_for_backend() {
    echo -e "${YELLOW}⏳ Waiting for backend at ${BACKEND_URL}...${NC}"

    local retries=30
    local count=0

    while [ $count -lt $retries ]; do
        if curl -s "${BACKEND_URL}/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Backend is ready${NC}"
            return 0
        fi

        echo -n "."
        sleep 2
        count=$((count + 1))
    done

    echo -e "${RED}✗ Backend failed to start${NC}"
    echo "  Please start the backend first: ./start.sh"
    exit 1
}

# Fetch OpenAPI spec
fetch_openapi() {
    echo -e "${BLUE}📥 Fetching OpenAPI specification...${NC}"

    mkdir -p "${TEMP_DIR}"

    if ! curl -s "${OPENAPI_URL}" -o "${TEMP_DIR}/openapi.json"; then
        echo -e "${RED}✗ Failed to fetch OpenAPI spec${NC}"
        exit 1
    fi

    # Validate JSON
    if ! python3 -c "import json; json.load(open('${TEMP_DIR}/openapi.json'))" 2>/dev/null; then
        echo -e "${RED}✗ Invalid OpenAPI JSON${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ OpenAPI spec fetched successfully${NC}"
}

# Generate TypeScript client
generate_client() {
    echo -e "${BLUE}🔧 Generating TypeScript API client...${NC}"

    # Clean output directory
    rm -rf "${OUTPUT_DIR}"
    mkdir -p "${OUTPUT_DIR}"

    # Use openapi-typescript to generate types
    echo -e "${YELLOW}  → Generating TypeScript types...${NC}"
    npx openapi-typescript "${TEMP_DIR}/openapi.json" \
        --output "${OUTPUT_DIR}/api.types.ts" \
        --support-array-length \
        --immutable-types

    # Generate fetch client
    echo -e "${YELLOW}  → Generating API client...${NC}"
    cat > "${OUTPUT_DIR}/api.client.ts" << 'EOF'
/**
 * AMOS API Client - Auto-generated from OpenAPI spec
 *
 * This file is auto-generated. Do not edit manually.
 * Run: ./scripts/generate-api-client.sh
 *
 * Creator: Trang Phan
 * Version: 3.0.0
 */

import type { paths, components } from './api.types';

// API Base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Type exports
type ApiPaths = paths;
type ApiComponents = components;
type ApiSchemas = components['schemas'];

// API Client class
export class AmosApiClient {
    private baseUrl: string;
    private headers: Record<string, string>;

    constructor(baseUrl: string = API_BASE_URL) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Content-Type': 'application/json',
        };
    }

    // Set auth token
    setAuthToken(token: string): void {
        this.headers['Authorization'] = `Bearer ${token}`;
    }

    // Generic request method
    private async request<T>(
        method: string,
        path: string,
        body?: unknown,
        queryParams?: Record<string, string>
    ): Promise<T> {
        let url = `${this.baseUrl}${path}`;

        // Add query parameters
        if (queryParams) {
            const params = new URLSearchParams();
            Object.entries(queryParams).forEach(([key, value]) => {
                if (value !== undefined && value !== null) {
                    params.append(key, value);
                }
            });
            const queryString = params.toString();
            if (queryString) {
                url += `?${queryString}`;
            }
        }

        const response = await fetch(url, {
            method,
            headers: this.headers,
            body: body ? JSON.stringify(body) : undefined,
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(`API Error ${response.status}: ${error}`);
        }

        // Check if response has content
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return response.json() as Promise<T>;
        }

        return null as T;
    }

    // ============================================
    // Health Endpoints
    // ============================================

    async getHealth(): Promise<ApiSchemas['HealthResponse']> {
        return this.request('GET', '/health');
    }

    async getLiveness(): Promise<ApiSchemas['LivenessResponse']> {
        return this.request('GET', '/health/live');
    }

    async getReadiness(): Promise<ApiSchemas['ReadinessResponse']> {
        return this.request('GET', '/health/ready');
    }

    async getStartup(): Promise<ApiSchemas['StartupResponse']> {
        return this.request('GET', '/health/startup');
    }

    async getFullHealth(): Promise<ApiSchemas['FullHealthResponse']> {
        return this.request('GET', '/health/full');
    }

    // ============================================
    // LLM Endpoints
    // ============================================

    async getProviders(): Promise<ApiSchemas['ProvidersResponse']> {
        return this.request('GET', '/api/v1/llm/providers');
    }

    async getModels(): Promise<ApiSchemas['ModelsResponse']> {
        return this.request('GET', '/api/v1/llm/models');
    }

    async chat(request: ApiSchemas['ChatRequest']): Promise<ApiSchemas['ChatResponse']> {
        return this.request('POST', '/api/v1/llm/chat', request);
    }

    // ============================================
    // Agent Endpoints
    // ============================================

    async listTasks(): Promise<ApiSchemas['TasksResponse']> {
        return this.request('GET', '/api/v1/agents/tasks');
    }

    async createTask(task: ApiSchemas['CreateTaskRequest']): Promise<ApiSchemas['TaskResponse']> {
        return this.request('POST', '/api/v1/agents/tasks', task);
    }

    async getTask(taskId: string): Promise<ApiSchemas['TaskResponse']> {
        return this.request('GET', `/api/v1/agents/tasks/${taskId}`);
    }

    async cancelTask(taskId: string): Promise<ApiSchemas['TaskResponse']> {
        return this.request('POST', `/api/v1/agents/tasks/${taskId}/cancel`);
    }

    async deleteTask(taskId: string): Promise<void> {
        return this.request('DELETE', `/api/v1/agents/tasks/${taskId}`);
    }

    // ============================================
    // System Endpoints
    // ============================================

    async getSystemStatus(): Promise<ApiSchemas['SystemStatusResponse']> {
        return this.request('GET', '/api/v1/system/status');
    }

    async getSystemMetrics(): Promise<ApiSchemas['SystemMetricsResponse']> {
        return this.request('GET', '/api/v1/system/metrics');
    }

    async getCognitiveMode(): Promise<ApiSchemas['CognitiveModeResponse']> {
        return this.request('GET', '/api/v1/system/cognitive/mode');
    }

    async setCognitiveMode(mode: string): Promise<ApiSchemas['CognitiveModeResponse']> {
        return this.request('POST', '/api/v1/system/cognitive/mode', { mode });
    }

    async getReasoningLevels(): Promise<ApiSchemas['ReasoningLevelsResponse']> {
        return this.request('GET', '/api/v1/system/reasoning/levels');
    }

    async getMemoryEntries(system?: string): Promise<ApiSchemas['MemoryEntriesResponse']> {
        const params = system ? { system } : undefined;
        return this.request('GET', '/api/v1/system/memory/entries', undefined, params);
    }

    async getCheckpoints(): Promise<ApiSchemas['CheckpointsResponse']> {
        return this.request('GET', '/api/v1/system/checkpoints');
    }

    async getMcpServers(): Promise<ApiSchemas['McpServersResponse']> {
        return this.request('GET', '/api/v1/system/mcp/servers');
    }

    async getOrchestraAgents(): Promise<ApiSchemas['OrchestraAgentsResponse']> {
        return this.request('GET', '/api/v1/system/orchestra/agents');
    }

    async getAgentsMdFiles(): Promise<ApiSchemas['AgentsMdFilesResponse']> {
        return this.request('GET', '/api/v1/system/agents-md/files');
    }

    async getGovernanceRules(): Promise<ApiSchemas['GovernanceRulesResponse']> {
        return this.request('GET', '/api/v1/system/governance/rules');
    }
}

// Export singleton instance
export const apiClient = new AmosApiClient();

// Export types
export type {
    ApiPaths,
    ApiComponents,
    ApiSchemas,
};
EOF

    echo -e "${GREEN}✓ API client generated successfully${NC}"
}

# Generate index file
generate_index() {
    echo -e "${BLUE}📦 Generating index...${NC}"

    cat > "${OUTPUT_DIR}/index.ts" << 'EOF'
/**
 * AMOS Generated API Client - Index
 *
 * Auto-generated from OpenAPI spec. Do not edit manually.
 *
 * Creator: Trang Phan
 * Version: 3.0.0
 */

export { AmosApiClient, apiClient } from './api.client';
export type { ApiPaths, ApiComponents, ApiSchemas } from './api.client';
export type * from './api.types';
EOF

    echo -e "${GREEN}✓ Index generated${NC}"
}

# Watch mode
watch_mode() {
    echo -e "${YELLOW}👀 Watch mode enabled${NC}"
    echo "  Press Ctrl+C to stop"

    while true; do
        echo -e "${BLUE}🔄 Regenerating client...${NC}"

        if curl -s "${OPENAPI_URL}" -o "${TEMP_DIR}/openapi.json" 2>/dev/null; then
            generate_client
            generate_index
            echo -e "${GREEN}✓ Client updated at $(date)${NC}"
        else
            echo -e "${YELLOW}⚠ Backend not available, skipping...${NC}"
        fi

        sleep 5
    done
}

# Cleanup
cleanup() {
    rm -rf "${TEMP_DIR}"
}

# Main
case "${1:-}" in
    --watch)
        check_dependencies
        wait_for_backend
        watch_mode
        ;;
    --help|-h)
        echo "AMOS API Client Generator"
        echo ""
        echo "Usage:"
        echo "  ./scripts/generate-api-client.sh           Generate client once"
        echo "  ./scripts/generate-api-client.sh --watch  Watch mode (auto-regenerate)"
        echo "  ./scripts/generate-api-client.sh --help    Show this help"
        echo ""
        echo "Requirements:"
        echo "  - Backend must be running at ${BACKEND_URL}"
        echo "  - Node.js with npx"
        echo "  - curl"
        ;;
    *)
        check_dependencies
        wait_for_backend
        fetch_openapi
        generate_client
        generate_index
        cleanup

        echo ""
        echo -e "${GREEN}✅ API client generation complete!${NC}"
        echo ""
        echo "  Generated files:"
        echo "    - ${OUTPUT_DIR}/api.types.ts"
        echo "    - ${OUTPUT_DIR}/api.client.ts"
        echo "    - ${OUTPUT_DIR}/index.ts"
        echo ""
        echo "  Usage in frontend:"
        echo "    import { apiClient } from './generated';"
        echo "    const status = await apiClient.getSystemStatus();"
        echo ""
        ;;
esac
