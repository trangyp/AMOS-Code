// AMOS Brain API JavaScript Client
// Usage: Include in browser or Node.js

class AMOSBrainClient {
    constructor(baseUrl = 'https://neurosyncai.tech', apiKey = null) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.apiKey = apiKey;
    }

    async _request(endpoint, method = 'GET', body = null) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json'
        };
        if (this.apiKey) {
            headers['X-API-Key'] = this.apiKey;
        }

        const options = {
            method,
            headers
        };
        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${await response.text()}`);
        }
        return response.json();
    }

    async health() {
        return this._request('/health');
    }

    async status() {
        return this._request('/status');
    }

    async think(query, domain = 'general') {
        return this._request('/think', 'POST', { query, domain });
    }

    async decide(question, options = null) {
        const body = { question };
        if (options) body.options = options;
        return this._request('/decide', 'POST', body);
    }

    async validate(action) {
        return this._request('/validate', 'POST', { action });
    }
}

// Usage examples:
// const client = new AMOSBrainClient('https://neurosyncai.tech', 'your-api-key');
// const result = await client.think('Benefits of microservices?');
// console.log(result.content);

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AMOSBrainClient };
}
