# AMOS Brain - Complete Deployment Guide

**Domain:** `neurosyncai.tech`

## Quick Start (5 minutes)

```bash
# 1. Clone and enter directory
cd AMOS-code

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Deploy everything
docker-compose up -d

# 4. Verify
python amos-cli.py status
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    neurosyncai.tech                     │
│                      (Nginx :80)                        │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   ┌─────────┐      ┌─────────────┐     ┌──────────────┐
   │ API     │      │ WebSocket   │     │ Dashboard    │
   │ :5000   │      │ :8765       │     │ :8080        │
   └─────────┘      └─────────────┘     └──────────────┘
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| nginx | 80 | Reverse proxy |
| amos-api | 5000 | REST API |
| amos-websocket | 8765 | Real-time streaming |
| admin-dashboard | 8080 | Web admin UI |

## API Endpoints

### Public Endpoints
```
GET  /health          # Health check
GET  /status          # System status
POST /think           # Cognitive analysis
POST /decide          # Decision making
POST /validate        # Action validation
```

### Admin Endpoints (require master key)
```
POST /admin/keys      # Generate API key
GET  /admin/stats     # Usage statistics
GET  /history/queries # Query history
```

### WebSocket
```
ws://neurosyncai.tech:8765
```

## CLI Management

```bash
# Check status
python amos-cli.py status

# Deploy updates
python amos-cli.py deploy

# View logs
python amos-cli.py logs
python amos-cli.py logs amos-api

# Create backup
python amos-cli.py backup

# Generate API key
python amos-cli.py key generate

# View analytics
python amos-cli.py analytics

# Run tests
python amos-cli.py test

# Monitor
python amos-cli.py monitor
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | API server port | 5000 |
| `ADMIN_MASTER_KEY` | Master key for admin | dev-master-key |
| `DATABASE_URL` | Database connection | sqlite:///app/data/amos.db |
| `HOSTINGER_API_KEY` | For auto-deploy | (none) |

## Testing

```bash
# Unit tests
python test_api.py

# Load testing
python load_test.py --duration 60 --concurrent 10

# Verification
python verify-deployment.py
```

## Monitoring

```bash
# Real-time dashboard
python monitor_dashboard.py

# Or open in browser:
# http://neurosyncai.tech:8080
```

## Backup & Restore

```bash
# Create backup
python amos-cli.py backup

# Restore from backup
tar -xzf backups/amos_backup_YYYYMMDD_HHMMSS.tar.gz
```

## Troubleshooting

### API not responding
```bash
docker-compose ps
docker-compose logs amos-api
```

### Database issues
```bash
docker-compose exec amos-api python -c "from database import db; db._init_db()"
```

### Reset everything
```bash
docker-compose down -v
docker-compose up -d
```

## Security

- API keys required for protected endpoints
- Rate limiting: 100 req/min per key
- Master key required for admin operations
- All traffic goes through nginx reverse proxy

## Next Steps

1. Configure SSL/HTTPS
2. Set up monitoring alerts
3. Configure log aggregation
4. Set up automated backups

---

**Complete system documentation:** See `API_README.md` and `QUICKSTART.md`
