#!/bin/bash
# AMOS CANON Consolidation Script
# ================================
# Consolidates duplicate _AMOS_CANON directories across all 6 repos

set -e

REPO_ROOT="/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code"
CANON_MASTER="$REPO_ROOT/_AMOS_CANON"
UNIFIED_BRAIN="$CANON_MASTER/AMOS_UNIFIED.brain"

echo "======================================================================"
echo "AMOS CANON CONSOLIDATION"
echo "======================================================================"
echo "Master: $CANON_MASTER"
echo "Unified Brain: $UNIFIED_BRAIN"
echo "======================================================================"

# Check master exists
if [ ! -f "$UNIFIED_BRAIN" ]; then
    echo "❌ Unified brain not found: $UNIFIED_BRAIN"
    exit 1
fi

echo ""
echo "Step 1: Backup existing brains..."
BACKUP_DIR="$REPO_ROOT/_AMOS_CANON_BACKUP_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup main brain
cp "$CANON_MASTER/AMOS_DESIGNER_OS/AMOS.brain" "$BACKUP_DIR/AMOS.brain.original"
echo "  ✓ Backed up original to $BACKUP_DIR"

echo ""
echo "Step 2: Replace main brain with unified version..."
cp "$UNIFIED_BRAIN" "$CANON_MASTER/AMOS_DESIGNER_OS/AMOS.brain"
echo "  ✓ Updated: $CANON_MASTER/AMOS_DESIGNER_OS/AMOS.brain"

echo ""
echo "Step 3: Propagate to 6 repositories..."

# Define repo locations
REPO_BRAINS=(
    "AMOS_REPOS/AMOS-Code/_AMOS_CANON/AMOS_DESIGNER_OS/AMOS.brain"
    "AMOS_REPOS/AMOS-Code/_AMOS_BRAIN/AMOS_DESIGNER_OS/AMOS.brain"
    "AMOS_REPOS/AMOS-Consulting/_AMOS_CANON/AMOS_DESIGNER_OS/AMOS.brain"
    "AMOS_REPOS/AMOS-Claws/_AMOS_CANON/AMOS_DESIGNER_OS/AMOS.brain"
    "AMOS_REPOS/AMOS-Invest/_AMOS_CANON/AMOS_DESIGNER_OS/AMOS.brain"
    "AMOS_REPOS/Mailinhconect/_AMOS_CANON/AMOS_DESIGNER_OS/AMOS.brain"
)

for brain_path in "${REPO_BRAINS[@]}"; do
    full_path="$REPO_ROOT/$brain_path"
    if [ -f "$full_path" ]; then
        # Backup
        cp "$full_path" "$BACKUP_DIR/$(basename $(dirname $(dirname $brain_path)))_AMOS.brain"
        # Replace with unified
        cp "$UNIFIED_BRAIN" "$full_path"
        echo "  ✓ Updated: $brain_path"
    else
        echo "  ⚠ Missing: $brain_path"
    fi
done

echo ""
echo "Step 4: Create canonical symlinks..."

# Create _00_AMOS_CANON symlink if it doesn't exist
if [ ! -e "$REPO_ROOT/_00_AMOS_CANON" ]; then
    ln -s "$CANON_MASTER" "$REPO_ROOT/_00_AMOS_CANON"
    echo "  ✓ Created symlink: _00_AMOS_CANON -> _AMOS_CANON"
fi

# Create _AMOS_BRAIN symlink if it doesn't exist
if [ ! -e "$REPO_ROOT/_AMOS_BRAIN" ]; then
    ln -s "$CANON_MASTER" "$REPO_ROOT/_AMOS_BRAIN"
    echo "  ✓ Created symlink: _AMOS_BRAIN -> _AMOS_CANON"
fi

echo ""
echo "Step 5: Verify canonical structure..."

# Check expected dirs
EXPECTED_DIRS=("AMOS_OS" "AMOS_WORKERS" "AMOS_ORGANISM_OS" "AMOS_UNIVERSE" "_AMOS_REPORTS" "_AMOS_STATE_LOG")
for dir in "${EXPECTED_DIRS[@]}"; do
    if [ -d "$REPO_ROOT/$dir" ]; then
        echo "  ✓ $dir"
    else
        echo "  ✗ Missing: $dir"
    fi
done

# Check expected files
EXPECTED_FILES=("AMOS_OS.py" "AMOS_RUNTIME.py" "AMOS_GODMODE.py" "start_godmode_full.sh" "vision_run.py")
echo ""
echo "Checking canonical files..."
for file in "${EXPECTED_FILES[@]}"; do
    if [ -f "$REPO_ROOT/$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ Missing: $file"
    fi
done

echo ""
echo "======================================================================"
echo "CONSOLIDATION COMPLETE"
echo "======================================================================"
echo "Backup location: $BACKUP_DIR"
echo ""
echo "Next steps:"
echo "  1. Review unified brain: $UNIFIED_BRAIN"
echo "  2. Test system: ./start_godmode_full.sh"
echo "  3. Commit changes: git add -A && git commit -m 'Consolidate AMOS canon'"
echo "======================================================================"
