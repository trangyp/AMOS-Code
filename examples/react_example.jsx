// AMOS Brain API React Hook Example
// Usage: import { useAMOSBrain } from './useAMOSBrain';

import { useState, useCallback } from 'react';

const API_URL = 'https://neurosyncai.tech';

export function useAMOSBrain(apiKey = null) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const request = useCallback(async (endpoint, method = 'GET', body = null) => {
        setLoading(true);
        setError(null);
        
        try {
            const headers = { 'Content-Type': 'application/json' };
            if (apiKey) headers['X-API-Key'] = apiKey;
            
            const response = await fetch(`${API_URL}${endpoint}`, {
                method,
                headers,
                body: body ? JSON.stringify(body) : null
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            setLoading(false);
            return data;
        } catch (err) {
            setError(err.message);
            setLoading(false);
            throw err;
        }
    }, [apiKey]);

    const think = useCallback((query, domain = 'general') => {
        return request('/think', 'POST', { query, domain });
    }, [request]);

    const decide = useCallback((question, options) => {
        return request('/decide', 'POST', { question, options });
    }, [request]);

    const validate = useCallback((action) => {
        return request('/validate', 'POST', { action });
    }, [request]);

    return { think, decide, validate, loading, error };
}

// Example component:
/*
function BrainAssistant() {
    const { think, loading, error } = useAMOSBrain('your-api-key');
    const [result, setResult] = useState(null);

    const handleAsk = async (query) => {
        const response = await think(query);
        setResult(response.content);
    };

    return (
        <div>
            {loading && <p>Thinking...</p>}
            {error && <p>Error: {error}</p>}
            {result && <pre>{result}</pre>}
        </div>
    );
}
*/
