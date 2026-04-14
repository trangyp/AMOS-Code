/**
 * AMOS SDK - JavaScript Client
 * Official JavaScript/TypeScript SDK for AMOS Brain API
 *
 * @example
 * const client = new AmosClient({ apiKey: 'your_key' });
 * const result = await client.think('What is the next step?');
 * console.log(result.content);
 */

class AmosError extends Error {
    constructor(message, statusCode) {
        super(message);
        this.name = 'AmosError';
        this.statusCode = statusCode;
    }
}

class AmosClient {
    /**
     * Create an AMOS Brain API client
     * @param {Object} config - Client configuration
     * @param {string} config.apiKey - API key for authentication
     * @param {string} [config.baseUrl='https://neurosyncai.tech'] - API base URL
     * @param {number} [config.timeout=30000] - Request timeout in ms
     */
    constructor(config = {}) {
        this.apiKey = config.apiKey || process.env.AMOS_API_KEY;
        this.baseUrl = config.baseUrl || 'https://neurosyncai.tech';
        this.timeout = config.timeout || 30000;

        if (!this.apiKey) {
            throw new AmosError('API key is required');
        }
    }

    /**
     * Make HTTP request to API
     * @private
     */
    async _request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json',
                    'User-Agent': 'AMOS-SDK-JS/1.0.0',
                    ...options.headers
                },
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                if (response.status === 401) {
                    throw new AmosError('Invalid API key', 401);
                } else if (response.status === 429) {
                    throw new AmosError('Rate limit exceeded', 429);
                } else if (response.status >= 500) {
                    throw new AmosError(`Server error: ${response.status}`, response.status);
                } else {
                    throw new AmosError(`Request error: ${response.statusText}`, response.status);
                }
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new AmosError('Request timeout', 408);
            }
            throw error;
        }
    }

    /**
     * Send a think request to AMOS Brain
     * @param {string} query - The question or problem to analyze
     * @param {string} [domain='general'] - Knowledge domain
     * @returns {Promise<Object>} Think result with content, reasoning, confidence
     */
    async think(query, domain = 'general') {
        const data = { query, domain };
        return await this._request('/think', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * Request a decision from AMOS Brain
     * @param {string} question - The decision to be made
     * @param {string[]} options - List of possible options
     * @returns {Promise<Object>} Decision result with recommendation
     */
    async decide(question, options) {
        const data = { question, options };
        return await this._request('/decide', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * Validate an action against AMOS global laws
     * @param {string} action - The action description
     * @returns {Promise<boolean>} True if valid
     */
    async validate(action) {
        const data = { action };
        const result = await this._request('/validate', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        return result.valid;
    }

    /**
     * Compile AMOSL source code
     * @param {string} source - AMOSL source code
     * @returns {Promise<Object>} Compilation result
     */
    async amoslCompile(source) {
        const data = { source };
        return await this._request('/amosl/compile', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * Get query history
     * @param {number} [limit=100] - Maximum records to return
     * @returns {Promise<Object[]>} Query history records
     */
    async getHistory(limit = 100) {
        return await this._request(`/api/history?limit=${limit}`);
    }

    /**
     * Get usage statistics
     * @param {number} [days=7] - Number of days
     * @returns {Promise<Object>} Usage statistics
     */
    async getStats(days = 7) {
        return await this._request(`/api/stats?days=${days}`);
    }

    /**
     * Check API health
     * @returns {Promise<boolean>} True if healthy
     */
    async healthCheck() {
        try {
            const result = await this._request('/health');
            return result.status === 'healthy';
        } catch {
            return false;
        }
    }
}

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AmosClient, AmosError };
}

if (typeof window !== 'undefined') {
    window.AmosClient = AmosClient;
    window.AmosError = AmosError;
}
