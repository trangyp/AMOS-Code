#!/usr/bin/env bash
set -euo pipefail

echo "=== AMOS MEGA SETUP START ==="

# 1) Resolve source folder (from cleaned zip in Downloads)
SRC_BASE="$HOME/Downloads/AMOS-PUBLIC-AUTO-CLEAN"
if [ -d "$SRC_BASE/AMOS-PUBLIC" ]; then
  SRC="$SRC_BASE/AMOS-PUBLIC"
elif [ -d "$HOME/Downloads/AMOS-PUBLIC" ]; then
  SRC="$HOME/Downloads/AMOS-PUBLIC"
else
  echo "ERROR: Could not find cleaned AMOS-PUBLIC in Downloads."
  echo "Expected: \$HOME/Downloads/AMOS-PUBLIC-AUTO-CLEAN/AMOS-PUBLIC"
  exit 1
fi

echo "Source repo: $SRC"

# 2) Destination in Documents/GitHub
DEST_ROOT="$HOME/Documents/GitHub"
mkdir -p "$DEST_ROOT"

DEST="$DEST_ROOT/AMOS-PUBLIC-CLEAN"
if [ -d "$DEST" ]; then
  TS="$(date +"%Y%m%d_%H%M%S")"
  BACKUP="${DEST_ROOT}/AMOS-PUBLIC-CLEAN.bak_${TS}"
  echo "Existing AMOS-PUBLIC-CLEAN found. Moving to backup:"
  echo "  $BACKUP"
  mv "$DEST" "$BACKUP"
fi

echo "Copying cleaned repo to: $DEST"
mkdir -p "$DEST"
rsync -a "$SRC"/ "$DEST"/

cd "$DEST"
echo "Now in: $(pwd)"

# 3) Virtual environment
if [ ! -d "amos_env" ]; then
  echo "Creating virtualenv amos_env..."
  python3 -m venv amos_env
else
  echo "Using existing amos_env..."
fi

echo "Upgrading pip/setuptools/wheel..."
./amos_env/bin/python -m ensurepip --upgrade || true
./amos_env/bin/python -m pip install --upgrade pip setuptools wheel || true

if [ -f "requirements.txt" ]; then
  echo "Installing from requirements.txt..."
  ./amos_env/bin/python -m pip install -r requirements.txt || true
fi

echo "Installing core runtime packages..."
./amos_env/bin/python -m pip install requests flask rich psutil uvicorn || true

# 4) Core folders
mkdir -p _AMOS_REPORTS _AMOS_QUARANTINE _AMOS_STATE_LOG

# 5) Reports + cleanup (if scripts exist)
if [ -f "scripts/dev/amos_reports_scan.py" ]; then
  echo "Running scripts/dev/amos_reports_scan.py..."
  ./amos_env/bin/python scripts/dev/amos_reports_scan.py || true
fi

if [ -x "scripts/dev/amos_clean_mega.sh" ]; then
  echo "Running scripts/dev/amos_clean_mega.sh..."
  bash scripts/dev/amos_clean_mega.sh || true
fi

# 6) Restart GOD_MODE + dashboards if scripts exist
echo "Restarting GOD_MODE + dashboards (if available)..."

pkill -f "AMOS_ORGANISM_OS.runtime_core.god_mode_ultra_core" >/dev/null 2>&1 || true
pkill -f "AMOS_ORGANISM_OS.runtime_core.god_mode_introspect_daemon" >/dev/null 2>&1 || true
pkill -f "AMOS_ORGANISM_OS.dashboard_live_fast" >/dev/null 2>&1 || true
pkill -f "AMOS_ORGANISM_OS.dashboard_live_hyper" >/dev/null 2>&1 || true
pkill -f "night_god_mode.sh" >/dev/null 2>&1 || true

sleep 1

if [ -x "scripts/run/night_god_mode.sh" ]; then
  echo "Starting scripts/run/night_god_mode.sh..."
  scripts/run/night_god_mode.sh > /tmp/night_god_mode.log 2>&1 &
  sleep 3
else
  echo "NOTE: scripts/run/night_god_mode.sh not found or not executable."
fi

if [ -x "scripts/run/god_mode_introspect_daemon.sh" ]; then
  echo "Starting scripts/run/god_mode_introspect_daemon.sh..."
  scripts/run/god_mode_introspect_daemon.sh > /tmp/god_mode_introspect_daemon.log 2>&1 &
  sleep 2
fi

echo
echo "=== PROCESS SNAPSHOT ==="
ps aux | egrep "god_mode_ultra_core|god_mode_introspect_daemon|dashboard_live_fast|dashboard_live_hyper" | egrep -v egrep || echo "No GOD_MODE processes found."

echo
echo "=== FAST /state (5056) ==="
curl -s http://127.0.0.1:5056/state || echo "5056 not responding"

echo
echo "=== HYPER /hyper (5057) ==="
curl -s http://127.0.0.1:5057/hyper || echo "5057 not responding"

echo
echo "=== AMOS MEGA SETUP COMPLETE ==="
echo "Project root: $DEST"
echo "Activate venv later with:"
echo "  cd \"$DEST\""
echo "  source amos_env/bin/activate"
