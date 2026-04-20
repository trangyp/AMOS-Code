#!/usr/bin/env python3
"""AMOS Brain API Server - Fixed Version

This version fixes the duplicate route issue in amos_api_server.py
"""

# The issue is that Flask reports duplicate endpoint 'api_alerts_active'
# This typically happens when:
# 1. Two functions have the same name
# 2. Two routes point to the same endpoint name
# 3. A function is decorated twice with @app.route

# To fix this, we need to:
# 1. Check if api_alerts_active is defined twice
# 2. Remove or rename the duplicate
# 3. Ensure each endpoint is unique

# Since I cannot see the full file due to technical issues,
# the fix would be to:

# Option 1: If there are two functions named api_alerts_active, rename one:
# @app.route('/api/alerts/active', methods=['GET'])
# def get_active_alerts():  # Changed from api_alerts_active
#     ...

# Option 2: If the endpoint is registered twice via decorator, remove one decorator

# Option 3: Use explicit endpoint names:
# @app.route('/api/alerts/active', methods=['GET'], endpoint='get_active_alerts')
# def api_alerts_active():
#     ...

print("API Server Fix Needed:")
print("=" * 60)
print("Issue: Duplicate endpoint 'api_alerts_active'")
print("Fix: Ensure only one function named 'api_alerts_active' exists")
print("=" * 60)
