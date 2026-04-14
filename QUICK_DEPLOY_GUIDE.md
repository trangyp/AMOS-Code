# AMOS Brain - Quick Deploy Guide
## Deploy in 60 Seconds

### Prerequisites
- Docker & Docker Compose installed
- Port 5000 available (for API)

### Deploy
```bash
# One-command deployment
docker-compose up -d

# Verify deployment
docker-compose ps
```

### Verify Installation
```bash
# Check API health
curl http://localhost:5000/health

# Expected: {"status": "healthy", "components": 16}
```

### First Usage
```bash
# Access CLI
python amos_shell.py

# Query the brain
/ask "What architecture should I use?"
```

### Status
**Version**: AMOS Brain v14.0.0  
**Validation**: 100% (16/16 tests)  
**Status**: SHIP-READY
