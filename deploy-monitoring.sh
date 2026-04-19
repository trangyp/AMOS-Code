#!/bin/bash
# Deploy AMOS Equation API with full monitoring stack

echo "=== AMOS Equation System - Production Monitoring Deployment ==="
echo "Building and starting services..."

docker-compose -f docker-compose.monitoring.yml up -d --build

echo ""
echo "=== Services Started ==="
echo "API:       http://localhost:8000"
echo "Prometheus: http://localhost:9090"
echo "Grafana:    http://localhost:3000 (admin/admin)"
echo ""
echo "=== Endpoints ==="
echo "Status:    http://localhost:8000/api/equations/status"
echo "Verify:    POST http://localhost:8000/api/equations/verify"
echo "Metrics:   http://localhost:8000/metrics"
echo "WebSocket: ws://localhost:8000/ws/verify"
