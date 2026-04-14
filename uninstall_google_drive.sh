#!/bin/bash
# Complete Google Drive Uninstaller for macOS

echo "=== Google Drive Complete Uninstaller ==="
echo ""

# 1. Quit Google Drive processes
echo "[1/8] Stopping Google Drive processes..."
killall "Google Drive" 2>/dev/null
killall "GoogleDriveFinderExtension" 2>/dev/null
killall "drivefs" 2>/dev/null
sleep 2
echo "✓ Processes stopped"

# 2. Remove the Application
echo ""
echo "[2/8] Removing Google Drive application..."
sudo rm -rf "/Applications/Google Drive.app"
sudo rm -rf "/Applications/Backup and Sync.app"
sudo rm -rf "/Applications/Google Drive File Stream.app"
echo "✓ Applications removed"

# 3. Remove Application Support
echo ""
echo "[3/8] Removing Application Support files..."
rm -rf ~/Library/Application\ Support/Google/Drive*
rm -rf ~/Library/Application\ Support/Google/DriveFS
rm -rf ~/Library/Application\ Support/Google/DriveFileStream
rm -rf ~/Library/Application\ Support/DriveFS
echo "✓ Application Support removed"

# 4. Remove Caches
echo ""
echo "[4/8] Removing cache files..."
rm -rf ~/Library/Caches/com.google.drive*
rm -rf ~/Library/Caches/com.google.Drive*
rm -rf ~/Library/Caches/Google/Drive*
rm -rf ~/Library/Caches/DriveFS
rm -rf ~/Library/Caches/GoogleDrive*
echo "✓ Caches removed"

# 5. Remove Preferences
echo ""
echo "[5/8] Removing preferences..."
rm -rf ~/Library/Preferences/com.google.drive*.plist
rm -rf ~/Library/Preferences/com.google.Drive*.plist
rm -rf ~/Library/Preferences/com.google.DriveFileStream*.plist
rm -rf ~/Library/Preferences/com.google.DriveFS*.plist
rm -rf ~/Library/Preferences/com.google.Backup*.plist
echo "✓ Preferences removed"

# 6. Remove Logs and other files
echo ""
echo "[6/8] Removing logs and additional files..."
rm -rf ~/Library/Logs/DriveFS
rm -rf ~/Library/Logs/GoogleDrive*
rm -rf ~/Library/Saved\ Application\ State/com.google.drive*.savedState
rm -rf ~/Library/Group\ Containers/*.com.google.drive*
rm -rf ~/Library/Group\ Containers/*.com.google.Drive*
rm -rf ~/Library/LaunchAgents/com.google.drive*
rm -rf ~/Library/LaunchAgents/com.google.Drive*
rm -rf ~/Library/Containers/com.google.drive*
rm -rf ~/Library/Containers/com.google.Drive*
rm -rf ~/Library/Application\ Scripts/com.google.drive*
rm -rf ~/Library/FileProvider/com.google.drivefs*
rm -rf ~/Library/Daemon\ Containers/*/Data/Library/Caches/com.google.drivefs*
echo "✓ Additional files removed"

# 7. Remove mount points
echo ""
echo "[7/8] Removing mount points..."
sudo rm -rf /Volumes/Google\ Drive
sudo rm -rf /Volumes/DriveFS
echo "✓ Mount points removed"

# 8. Remove from Keychain (will prompt)
echo ""
echo "[8/8] Removing Keychain items..."
security delete-generic-password -s "com.google.drivefs" 2>/dev/null || true
security delete-generic-password -s "com.google.drivefs.settings" 2>/dev/null || true
echo "✓ Keychain items removed"

echo ""
echo "=== Google Drive Uninstall Complete ==="
echo ""
echo "Note: You may need to manually remove Google Drive from:"
echo "  - System Settings > General > Login Items"
echo "  - Finder > Favorites (if Google Drive folder was pinned)"
echo ""
echo "Please restart your Mac to complete the cleanup."
