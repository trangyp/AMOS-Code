import React, { useEffect, useState, useRef, useCallback } from 'react';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
);

// Types
interface Agent {
  id: string;
  type: string;
  status: 'active' | 'busy' | 'paused' | 'error';
  capabilities: string[];
  total_tasks: number;
  success_rate: number;
}

interface NetworkNode {
  id: string;
  label: string;
  type: string;
  status: string;
  capabilities: string[];
  x?: number;
  y?: number;
}

interface NetworkEdge {
  source: string;
  target: string;
  type: string;
  timestamp: string;
}

interface Metrics {
  agents: number;
  active_agents: number;
  busy_agents: number;
  queued_tasks: number;
  running_tasks: number;
  total_messages: number;
  governance_violations: number;
  active_budgets: number;
}

interface DashboardEvent {
  event_type: string;
  timestamp: string;
  event_id: string;
  data: any;
}

// Status color mapping
const statusColors: Record<string, string> = {
  active: '#10b981',
  busy: '#3b82f6',
  paused: '#f59e0b',
  error: '#ef4444',
  initializing: '#6b7280'
};

const CollaborationDashboard: React.FC = () => {
  // State
  const [agents, setAgents] = useState<Agent[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [networkTopology, setNetworkTopology] = useState<{ nodes: NetworkNode[]; edges: NetworkEdge[] }>({ nodes: [], edges: [] });
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [events, setEvents] = useState<DashboardEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [agentDetails, setAgentDetails] = useState<any>(null);

  // WebSocket ref
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  // Connect to WebSocket
  const connectWebSocket = useCallback(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/dashboard');

    ws.onopen = () => {
      console.log('Connected to AMOS Collaboration Dashboard');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      const data: DashboardEvent = JSON.parse(event.data);
      handleEvent(data);
    };

    ws.onclose = () => {
      console.log('Disconnected from dashboard');
      setIsConnected(false);

      // Reconnect after 5 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connectWebSocket();
      }, 5000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    wsRef.current = ws;
  }, []);

  // Handle incoming events
  const handleEvent = (event: DashboardEvent) => {
    // Add to event log
    setEvents(prev => [event, ...prev].slice(0, 50));

    switch (event.event_type) {
      case 'initial_state':
        setAgents(event.data.agents);
        setNetworkTopology(event.data.network_topology);
        break;

      case 'agent_created':
        // Refresh agents list
        fetchAgents();
        break;

      case 'agent_status_change':
        setAgents(prev => prev.map(agent =>
          agent.id === event.data.agent_id
            ? { ...agent, status: event.data.new_status }
            : agent
        ));
        break;

      case 'metrics_update':
        setMetrics(event.data);
        break;

      case 'network_topology':
        setNetworkTopology(event.data);
        break;

      case 'task_completed':
        // Update agent metrics
        fetchAgents();
        break;

      case 'improvement_applied':
        // Show improvement notification
        console.log(`Agent ${event.data.agent_id} improved by ${event.data.improvement_percent}%`);
        break;
    }
  };

  // Fetch agents
  const fetchAgents = async () => {
    try {
      const response = await fetch('http://localhost:8000/ai/agents/list');
      const data = await response.json();
      setAgents(data);
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    }
  };

  // Fetch agent details
  const fetchAgentDetails = async (agentId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/ai/agents/${agentId}/status`);
      const data = await response.json();
      setAgentDetails(data);
      setSelectedAgent(agents.find(a => a.id === agentId) || null);
    } catch (error) {
      console.error('Failed to fetch agent details:', error);
    }
  };

  // Trigger manual improvement
  const triggerImprovement = async (agentId: string) => {
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({
        command: 'trigger_improvement',
        agent_id: agentId
      }));
    }
  };

  // Connect on mount
  useEffect(() => {
    connectWebSocket();
    fetchAgents();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connectWebSocket]);

  // Chart data for agent status
  const statusChartData = {
    labels: ['Active', 'Busy', 'Paused', 'Error'],
    datasets: [{
      data: [
        agents.filter(a => a.status === 'active').length,
        agents.filter(a => a.status === 'busy').length,
        agents.filter(a => a.status === 'paused').length,
        agents.filter(a => a.status === 'error').length
      ],
      backgroundColor: [
        statusColors.active,
        statusColors.busy,
        statusColors.paused,
        statusColors.error
      ],
      borderWidth: 0
    }]
  };

  // Chart data for task metrics
  const taskMetricsData = {
    labels: agents.map(a => a.id.slice(0, 8)),
    datasets: [{
      label: 'Success Rate (%)',
      data: agents.map(a => a.success_rate),
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      fill: true,
      tension: 0.4
    }]
  };

  // Network graph SVG
  const renderNetworkGraph = () => {
    const width = 600;
    const height = 400;
    const nodeRadius = 30;

    // Position nodes in a circle
    const positionedNodes = networkTopology.nodes.map((node, index) => {
      const angle = (2 * Math.PI * index) / networkTopology.nodes.length;
      const x = width / 2 + (width / 3) * Math.cos(angle);
      const y = height / 2 + (height / 3) * Math.sin(angle);
      return { ...node, x, y };
    });

    return (
      <svg width={width} height={height} className="network-graph">
        {/* Edges */}
        {networkTopology.edges.map((edge, idx) => {
          const sourceNode = positionedNodes.find(n => n.id === edge.source);
          const targetNode = positionedNodes.find(n => n.id === edge.target);
          if (!sourceNode || !targetNode) return null;

          return (
            <line
              key={idx}
              x1={sourceNode.x}
              y1={sourceNode.y}
              x2={targetNode.x}
              y2={targetNode.y}
              stroke="#94a3b8"
              strokeWidth="2"
              strokeOpacity="0.6"
            />
          );
        })}

        {/* Nodes */}
        {positionedNodes.map((node) => (
          <g
            key={node.id}
            transform={`translate(${node.x}, ${node.y})`}
            className="network-node"
            onClick={() => fetchAgentDetails(node.id)}
            style={{ cursor: 'pointer' }}
          >
            <circle
              r={nodeRadius}
              fill={statusColors[node.status] || '#6b7280'}
              stroke="#fff"
              strokeWidth="3"
            />
            <text
              textAnchor="middle"
              dy="-5"
              fill="white"
              fontSize="12"
              fontWeight="bold"
            >
              {node.type.slice(0, 3)}
            </text>
            <text
              textAnchor="middle"
              dy="10"
              fill="white"
              fontSize="10"
            >
              {node.id.slice(0, 6)}
            </text>
          </g>
        ))}
      </svg>
    );
  };

  return (
    <div className="collaboration-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <h1>AMOS Collaboration Dashboard</h1>
        <div className="connection-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`} />
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      </div>

      {/* Metrics Overview */}
      {metrics && (
        <div className="metrics-grid">
          <div className="metric-card">
            <h3>Total Agents</h3>
            <p className="metric-value">{metrics.agents}</p>
            <p className="metric-subtext">{metrics.active_agents} active, {metrics.busy_agents} busy</p>
          </div>
          <div className="metric-card">
            <h3>Tasks</h3>
            <p className="metric-value">{metrics.running_tasks}</p>
            <p className="metric-subtext">{metrics.queued_tasks} queued</p>
          </div>
          <div className="metric-card">
            <h3>Messages</h3>
            <p className="metric-value">{metrics.total_messages}</p>
            <p className="metric-subtext">Total exchanged</p>
          </div>
          <div className="metric-card">
            <h3>Violations</h3>
            <p className="metric-value warning">{metrics.governance_violations}</p>
            <p className="metric-subtext">Governance issues</p>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="dashboard-content">
        {/* Left Panel - Network Graph */}
        <div className="panel network-panel">
          <h2>Agent Network Topology</h2>
          <div className="graph-container">
            {renderNetworkGraph()}
          </div>
          <div className="legend">
            <div className="legend-item">
              <span className="legend-dot" style={{ backgroundColor: statusColors.active }} />
              Active
            </div>
            <div className="legend-item">
              <span className="legend-dot" style={{ backgroundColor: statusColors.busy }} />
              Busy
            </div>
            <div className="legend-item">
              <span className="legend-dot" style={{ backgroundColor: statusColors.paused }} />
              Paused
            </div>
            <div className="legend-item">
              <span className="legend-dot" style={{ backgroundColor: statusColors.error }} />
              Error
            </div>
          </div>
        </div>

        {/* Middle Panel - Charts */}
        <div className="panel charts-panel">
          <h2>Performance Metrics</h2>
          <div className="chart-container">
            <h3>Agent Status Distribution</h3>
            <Doughnut data={statusChartData} options={{ responsive: true, maintainAspectRatio: false }} />
          </div>
          <div className="chart-container">
            <h3>Success Rates by Agent</h3>
            <Line data={taskMetricsData} options={{ responsive: true, maintainAspectRatio: false }} />
          </div>
        </div>

        {/* Right Panel - Agent Details & Events */}
        <div className="panel details-panel">
          {selectedAgent ? (
            <div className="agent-details">
              <div className="panel-header">
                <h2>Agent: {selectedAgent.id.slice(0, 8)}</h2>
                <button onClick={() => setSelectedAgent(null)}>Close</button>
              </div>
              <div className="agent-info">
                <p><strong>Type:</strong> {selectedAgent.type}</p>
                <p><strong>Status:</strong>
                  <span className={`status-badge ${selectedAgent.status}`}>
                    {selectedAgent.status}
                  </span>
                </p>
                <p><strong>Capabilities:</strong> {selectedAgent.capabilities.join(', ')}</p>
                <p><strong>Total Tasks:</strong> {selectedAgent.total_tasks}</p>
                <p><strong>Success Rate:</strong> {selectedAgent.success_rate}%</p>
              </div>
              {agentDetails?.evolution && (
                <div className="evolution-section">
                  <h3>Self-Evolution Progress</h3>
                  <p>Improvements Applied: {agentDetails.evolution.improvements_applied}</p>
                  <p>Regression Detected: {agentDetails.evolution.regression_detected ? 'Yes' : 'No'}</p>
                  <button
                    onClick={() => triggerImprovement(selectedAgent.id)}
                    className="improve-button"
                  >
                    Trigger Improvement
                  </button>
                </div>
              )}
            </div>
          ) : (
            <>
              <h2>Agents List</h2>
              <div className="agents-list">
                {agents.map(agent => (
                  <div
                    key={agent.id}
                    className="agent-item"
                    onClick={() => fetchAgentDetails(agent.id)}
                  >
                    <div className="agent-status-dot" style={{ backgroundColor: statusColors[agent.status] }} />
                    <div className="agent-info-short">
                      <span className="agent-type">{agent.type}</span>
                      <span className="agent-id">{agent.id.slice(0, 8)}</span>
                    </div>
                    <span className="agent-success-rate">{agent.success_rate}%</span>
                  </div>
                ))}
              </div>
            </>
          )}

          <div className="events-section">
            <h2>Live Events</h2>
            <div className="events-list">
              {events.map(event => (
                <div key={event.event_id} className={`event-item ${event.event_type}`}>
                  <span className="event-time">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </span>
                  <span className="event-type">{event.event_type.replace('_', ' ')}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Styles */}
      <style>{`
        .collaboration-dashboard {
          padding: 20px;
          background: #f1f5f9;
          min-height: 100vh;
        }

        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .dashboard-header h1 {
          margin: 0;
          color: #1e293b;
        }

        .connection-status {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .status-indicator {
          width: 12px;
          height: 12px;
          border-radius: 50%;
        }

        .status-indicator.connected {
          background-color: #10b981;
        }

        .status-indicator.disconnected {
          background-color: #ef4444;
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 16px;
          margin-bottom: 20px;
        }

        .metric-card {
          background: white;
          padding: 16px;
          border-radius: 8px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .metric-card h3 {
          margin: 0 0 8px 0;
          font-size: 14px;
          color: #64748b;
        }

        .metric-value {
          font-size: 32px;
          font-weight: bold;
          color: #1e293b;
          margin: 0;
        }

        .metric-value.warning {
          color: #ef4444;
        }

        .metric-subtext {
          font-size: 12px;
          color: #94a3b8;
          margin: 4px 0 0 0;
        }

        .dashboard-content {
          display: grid;
          grid-template-columns: 1.2fr 1fr 0.8fr;
          gap: 20px;
        }

        .panel {
          background: white;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .panel h2 {
          margin: 0 0 16px 0;
          font-size: 18px;
          color: #1e293b;
        }

        .graph-container {
          display: flex;
          justify-content: center;
          align-items: center;
          height: 400px;
        }

        .network-graph {
          border: 1px solid #e2e8f0;
          border-radius: 8px;
          background: #f8fafc;
        }

        .network-node:hover circle {
          filter: brightness(1.1);
          stroke-width: 4;
        }

        .legend {
          display: flex;
          justify-content: center;
          gap: 16px;
          margin-top: 16px;
        }

        .legend-item {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          color: #64748b;
        }

        .legend-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
        }

        .chart-container {
          height: 200px;
          margin-bottom: 20px;
        }

        .chart-container h3 {
          font-size: 14px;
          color: #64748b;
          margin-bottom: 8px;
        }

        .agents-list {
          max-height: 300px;
          overflow-y: auto;
        }

        .agent-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px;
          border-bottom: 1px solid #e2e8f0;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .agent-item:hover {
          background-color: #f8fafc;
        }

        .agent-status-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
        }

        .agent-info-short {
          flex: 1;
          display: flex;
          flex-direction: column;
        }

        .agent-type {
          font-weight: 500;
          color: #1e293b;
        }

        .agent-id {
          font-size: 12px;
          color: #94a3b8;
        }

        .agent-success-rate {
          font-weight: 600;
          color: #10b981;
        }

        .panel-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .panel-header button {
          padding: 6px 12px;
          background: #e2e8f0;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }

        .agent-info p {
          margin: 8px 0;
          color: #475569;
        }

        .status-badge {
          display: inline-block;
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 12px;
          margin-left: 8px;
        }

        .status-badge.active {
          background: #dcfce7;
          color: #166534;
        }

        .status-badge.busy {
          background: #dbeafe;
          color: #1e40af;
        }

        .evolution-section {
          margin-top: 20px;
          padding-top: 20px;
          border-top: 1px solid #e2e8f0;
        }

        .improve-button {
          margin-top: 12px;
          padding: 8px 16px;
          background: #3b82f6;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }

        .improve-button:hover {
          background: #2563eb;
        }

        .events-section {
          margin-top: 20px;
          padding-top: 20px;
          border-top: 1px solid #e2e8f0;
        }

        .events-list {
          max-height: 200px;
          overflow-y: auto;
        }

        .event-item {
          display: flex;
          justify-content: space-between;
          padding: 8px 0;
          border-bottom: 1px solid #f1f5f9;
          font-size: 13px;
        }

        .event-time {
          color: #94a3b8;
        }

        .event-type {
          color: #475569;
          text-transform: capitalize;
        }

        .event-item.agent_created .event-type {
          color: #10b981;
        }

        .event-item.improvement_applied .event-type {
          color: #3b82f6;
        }

        .event-item.governance_violation .event-type {
          color: #ef4444;
        }
      `}</style>
    </div>
  );
};

export default CollaborationDashboard;
