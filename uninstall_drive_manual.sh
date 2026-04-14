#!/bin/bash
# Paste this entire block into Terminal and press Enter

echo "=== Uninstalling Google Drive ==="

# Kill processes
killall "Google Drive" 2>/dev/null
killall "GoogleDriveFinderExtension" 2>/dev/null
sleep 2

# Remove app (requires sudo password)
echo "Removing Google Drive.app..."
sudo rm -rf "/Applications/Google Drive.app"

# Remove user files
echo "Removing user data..."
rm -rf ~/Library/Application\ Support/Google/Drive*
rm -rf ~/Library/Application\ Support/FileProvider/com.google.drivefs*
rm -rf ~/Library/Application\ Scripts/com.google.drivefs*
rm -rf ~/Library/Group\ Containers/*com.google.drivefs*
rm -rf ~/Library/Caches/com.google.drive*
rm -rf ~/Library/Preferences/com.google.drive*
rm -rf ~/Library/Logs/DriveFS
rm -rf ~/Library/Saved\ Application\ State/com.google.drive*

# Remove mount
sudo rm -rf /Volumes/Google\ Drive

echo "=== Done ==="
echo "Restart your Mac and check System Settings > Login Items"
