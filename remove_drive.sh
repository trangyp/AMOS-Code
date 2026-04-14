#!/bin/bash
# Quick Google Drive removal - no sudo needed for most

echo "Removing Google Drive..."

# Kill processes
killall "Google Drive" 2>/dev/null
killall "GoogleDriveFinderExtension" 2>/dev/null
sleep 1

# Remove user files (no sudo needed)
rm -rf ~/Library/Preferences/com.google.drivefs*
rm -rf ~/Library/Caches/com.google.drive*
rm -rf ~/Library/Application\ Support/FileProvider/com.google.drivefs*
rm -rf ~/Library/Application\ Scripts/com.google.drivefs*
rm -rf ~/Library/Group\ Containers/*com.google.drivefs*
rm -rf ~/Library/Logs/DriveFS
rm -rf ~/Library/Saved\ Application\ State/com.google.drive*

echo "✓ User files removed"
echo ""
echo "Now manually:"
echo "1. Drag /Applications/Google Drive.app to Trash"
echo "2. Empty Trash"
echo "3. Restart Mac"
echo "4. Remove from System Settings > General > Login Items"
