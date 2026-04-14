// Admin Dashboard Analytics Component
// Connects to /api/stats and /api/history endpoints

const API_BASE = window.location.origin;

// Fetch and display analytics
async function loadAnalytics() {
    try {
        const response = await fetch(`${API_BASE}/api/stats?days=7`);
        const data = await response.json();

        if (data.success) {
            updateMetrics(data.stats);
            renderCharts(data.stats);
        }
    } catch (error) {
        console.error('Analytics load failed:', error);
    }
}

// Update metric cards
function updateMetrics(stats) {
    document.getElementById('total-requests').textContent = stats.total_requests || 0;
    document.getElementById('avg-response').textContent = `${stats.avg_response_time_ms || 0}ms`;
    document.getElementById('success-rate').textContent = `${stats.success_rate_percent || 0}%`;
}

// Render Chart.js charts
function renderCharts(stats) {
    const ctx = document.getElementById('requests-chart').getContext('2d');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'API Requests',
                data: [12, 19, 15, 25, 22, 30, 28],
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.1)' },
                    ticks: { color: '#888' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#888' }
                }
            }
        }
    });
}

// Load query history
async function loadQueryHistory() {
    try {
        const response = await fetch(`${API_BASE}/api/history?limit=50`);
        const data = await response.json();

        if (data.success) {
            renderHistoryTable(data.history);
        }
    } catch (error) {
        console.error('History load failed:', error);
    }
}

// Render history table
function renderHistoryTable(history) {
    const tbody = document.getElementById('history-table-body');
    tbody.innerHTML = '';

    history.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.id}</td>
            <td><span class="badge badge-${item.endpoint}">${item.endpoint}</span></td>
            <td class="query-cell">${item.query || '-'}</td>
            <td>${item.domain || '-'}</td>
            <td><span class="confidence">${item.confidence || '-'}</span></td>
            <td>${item.law_compliant ? '✓' : '✗'}</td>
            <td>${item.processing_time_ms}ms</td>
            <td>${new Date(item.created_at).toLocaleString()}</td>
        `;
        tbody.appendChild(row);
    });
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadAnalytics();
    loadQueryHistory();

    // Refresh every 30 seconds
    setInterval(() => {
        loadAnalytics();
        loadQueryHistory();
    }, 30000);
});

// Export for use in React components
window.AdminAnalytics = {
    loadAnalytics,
    loadQueryHistory
};
