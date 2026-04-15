/**
 * AMOS Brain Dashboard - Interactive JavaScript
 * Real-time visualization and API integration
 */

// Configuration
const API_BASE = window.location.origin.includes('localhost')
    ? 'http://localhost:5000'
    : 'https://neurosyncai.tech';

// State
let currentEndpoint = 'think';
let metricsInterval = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('🧠 AMOS Brain Dashboard initialized');

    initTabs();
    initApiConsole();
    initMemoryQuery();
    initDomainClick();
    fetchRealHistory();
    fetchStats();
    startMetricsUpdate();
    animateLevels();
    initWebSocket();
});

// Fetch real query history from API
async function fetchRealHistory() {
    try {
        const response = await fetch(`${API_BASE}/api/history?limit=10`);
        const data = await response.json();

        if (data.success && data.history) {
            displayHistory(data.history);
        }
    } catch (error) {
        console.error('Failed to fetch history:', error);
    }
}

// Display history from API
function displayHistory(history) {
    const resultsEl = document.getElementById('memory-results');
    resultsEl.innerHTML = '';

    history.forEach(item => {
        const div = document.createElement('div');
        div.className = 'memory-item';
        div.innerHTML = `
            <span class="memory-id">#${item.id}</span>
            <span class="memory-type">${item.endpoint.toUpperCase()}</span>
            <span class="memory-time">${new Date(item.created_at).toLocaleString()}</span>
            <p class="memory-content">${item.query || item.response_summary || 'No content'}</p>
        `;
        resultsEl.appendChild(div);
    });
}

// Fetch and display stats
async function fetchStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats?days=7`);
        const data = await response.json();

        if (data.success && data.stats) {
            document.getElementById('sessions').textContent = data.stats.total_requests || 0;
        }
    } catch (error) {
        console.error('Failed to fetch stats:', error);
    }
}

// Tab switching
function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentEndpoint = tab.dataset.endpoint;

            // Update placeholder
            const textarea = document.getElementById('api-request');
            const placeholders = {
                think: '{"query": "What is the next logical step?", "domain": "software"}',
                decide: '{"question": "Should we build X?", "options": ["yes", "no"]}',
                amosl: '{"source": "ontology { classical { entity Cell { x: Int } } }"}'
            };
            textarea.placeholder = placeholders[currentEndpoint];
        });
    });
}

// API Console
function initApiConsole() {
    const sendBtn = document.getElementById('api-send');
    const responseEl = document.getElementById('api-response');

    sendBtn.addEventListener('click', async () => {
        const requestEl = document.getElementById('api-request');
        const requestBody = requestEl.value.trim();

        if (!requestBody) {
            responseEl.textContent = 'Error: Empty request body';
            return;
        }

        sendBtn.textContent = 'Sending...';
        sendBtn.disabled = true;

        try {
            const endpoint = `/api/${currentEndpoint}`;
            const response = await fetch(`${API_BASE}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: requestBody
            });

            const data = await response.json();
            responseEl.textContent = JSON.stringify(data, null, 2);

            // Add to memory if successful
            if (data.success !== false) {
                addToMemory(currentEndpoint, requestBody.substring(0, 50));
            }
        } catch (error) {
            responseEl.textContent = `Error: ${error.message}`;
            console.error('API Error:', error);
        } finally {
            sendBtn.textContent = 'Send Request';
            sendBtn.disabled = false;
        }
    });
}

// Memory Query
function initMemoryQuery() {
    const queryBtn = document.getElementById('query-btn');
    const queryInput = document.getElementById('memory-query');
    const resultsEl = document.getElementById('memory-results');

    queryBtn.addEventListener('click', () => {
        const query = queryInput.value.trim().toLowerCase();
        if (!query) return;

        // Filter memory items
        const items = resultsEl.querySelectorAll('.memory-item');
        items.forEach(item => {
            const content = item.textContent.toLowerCase();
            item.style.display = content.includes(query) ? 'block' : 'none';
        });
    });

    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') queryBtn.click();
    });
}

// Add to memory display
function addToMemory(type, content) {
    const resultsEl = document.getElementById('memory-results');
    const id = Math.random().toString(36).substring(2, 8);

    const item = document.createElement('div');
    item.className = 'memory-item';
    item.innerHTML = `
        <span class="memory-id">#${id}</span>
        <span class="memory-type">${type.toUpperCase()}</span>
        <span class="memory-time">Just now</span>
        <p class="memory-content">${content}...</p>
    `;

    resultsEl.insertBefore(item, resultsEl.firstChild);

    // Keep only last 10 items
    while (resultsEl.children.length > 10) {
        resultsEl.removeChild(resultsEl.lastChild);
    }
}

// Domain click interaction
function initDomainClick() {
    const domains = document.querySelectorAll('.domain');
    domains.forEach(domain => {
        domain.addEventListener('click', () => {
            domains.forEach(d => d.classList.remove('active'));
            domain.classList.add('active');

            const domainName = domain.dataset.domain;
            console.log(`Domain selected: ${domainName}`);

            // Update API console with domain context
            const textarea = document.getElementById('api-request');
            if (currentEndpoint === 'think') {
                textarea.value = JSON.stringify({
                    query: `Analyze in ${domainName} domain`,
                    domain: domainName
                }, null, 2);
            }
        });
    });
}

// Metrics update simulation
function startMetricsUpdate() {
    const metrics = {
        confidence: document.getElementById('confidence'),
        compliance: document.getElementById('compliance'),
        sessions: document.getElementById('sessions'),
        rate: document.getElementById('rate')
    };

    // Update every 3 seconds
    metricsInterval = setInterval(() => {
        // Simulate live metric changes
        const confidence = 90 + Math.floor(Math.random() * 10);
        const rate = 120 + Math.floor(Math.random() * 20);

        if (metrics.confidence) metrics.confidence.textContent = `${confidence}%`;
        if (metrics.rate) metrics.rate.textContent = `${rate}/s`;

        // Update sparklines
        updateSparklines();
    }, 3000);
}

// Update sparkline visualizations
function updateSparklines() {
    const sparklines = document.querySelectorAll('.metric-sparkline');
    sparklines.forEach(spark => {
        const width = 30 + Math.floor(Math.random() * 70);
        spark.style.background = `linear-gradient(90deg, var(--primary) ${width}%, transparent 100%)`;
    });
}

// Animate L1-L6 levels
function animateLevels() {
    const levels = document.querySelectorAll('.level-fill');

    setInterval(() => {
        levels.forEach(level => {
            const currentHeight = parseInt(level.style.height);
            const change = Math.floor(Math.random() * 10) - 5;
            const newHeight = Math.max(50, Math.min(100, currentHeight + change));
            level.style.height = `${newHeight}%`;
        });
    }, 5000);
}

// Initialize WebSocket connection
function initWebSocket() {
    const wsUrl = window.location.protocol === 'https:'
        ? `wss://${window.location.host}/ws`
        : `ws://${window.location.host}:8766`;

    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('WebSocket connected');
        document.querySelector('.status-indicator').classList.add('online');
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        switch(data.type) {
            case 'step':
                addToMemory('think', `Step ${data.number}: ${data.content.substring(0, 40)}`);
                break;
            case 'analysis':
                addToMemory('decide', data.step);
                break;
            case 'complete':
                updateMetricsFromResult(data);
                break;
            case 'error':
                console.error('WebSocket error:', data.message);
                break;
        }
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        document.querySelector('.status-indicator').classList.remove('online');
    };

    ws.onclose = () => {
        console.log('WebSocket disconnected');
        document.querySelector('.status-indicator').classList.remove('online');
        // Reconnect after 5 seconds
        setTimeout(initWebSocket, 5000);
    };

    // Store for global access
    window.amosWebSocket = ws;
}

// Update metrics from WebSocket result
function updateMetricsFromResult(data) {
    if (data.confidence) {
        document.getElementById('confidence').textContent = `${Math.round(data.confidence * 100)}%`;
    }
    if (data.law_compliant !== undefined) {
        document.getElementById('compliance').textContent = data.law_compliant ? '100%' : '95%';
    }
}

// Update metrics from WebSocket
function updateRealtimeMetrics(data) {
    if (data.confidence) {
        document.getElementById('confidence').textContent = `${data.confidence}%`;
    }
    if (data.sessions) {
        document.getElementById('sessions').textContent = data.sessions;
    }
}

// Fetch brain status
async function fetchBrainStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();

        if (data.success) {
            updateDashboardFromStatus(data.status);
        }
    } catch (error) {
        console.error('Status fetch error:', error);
    }
}

// Update dashboard from API status
function updateDashboardFromStatus(status) {
    // Update levels
    if (status.levels) {
        Object.entries(status.levels).forEach(([level, value]) => {
            const bar = document.querySelector(`[data-level="${level}"] .level-fill`);
            if (bar) bar.style.height = `${value}%`;
        });
    }

    // Update metrics
    if (status.confidence) {
        document.getElementById('confidence').textContent = `${status.confidence}%`;
    }
}

// Export functions for testing
window.AMOSDashboard = {
    addToMemory,
    updateMetrics: updateSparklines,
    fetchStatus: fetchBrainStatus
};

// Connection status check
async function checkServerConnection() {
    const statusText = document.querySelector('.status-text');
    const statusIndicator = document.querySelector('.status-indicator');

    try {
        const response = await fetch(`${API_BASE}/health`);
        if (response.ok) {
            const data = await response.json();
            if (data.status === 'healthy' || data.status === 'initializing') {
                statusText.textContent = 'System Online';
                statusIndicator.classList.add('online');
            } else {
                statusText.textContent = 'System Degraded';
                statusIndicator.classList.remove('online');
            }
        } else {
            statusText.textContent = 'Server Error';
            statusIndicator.classList.remove('online');
        }
    } catch (error) {
        statusText.textContent = 'Not Connected';
        statusIndicator.classList.remove('online');
        console.error('Server connection failed:', error);
    }
}

// Check connection on load
checkServerConnection();

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (metricsInterval) clearInterval(metricsInterval);
});
