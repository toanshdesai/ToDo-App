#!/bin/bash
# Create DMG installer for TODO app (Simple version)
# This creates a disk image for easy distribution

set -e

APP_NAME="TODO"
APP_PATH="dist/TODO.app"
DMG_NAME="TODO-Installer"
DMG_PATH="dist/${DMG_NAME}.dmg"
VOLUME_NAME="TODO Installer"

echo "📦 Creating DMG installer for TODO app..."
echo ""

# Check if app exists
if [ ! -d "$APP_PATH" ]; then
    echo "❌ Error: TODO.app not found at $APP_PATH"
    echo "   Please run ./build.sh first to build the app."
    exit 1
fi

# Remove old DMG if it exists
if [ -f "$DMG_PATH" ]; then
    echo "🗑️  Removing old DMG..."
    rm "$DMG_PATH"
fi

# Create temporary directory for DMG contents
echo "📁 Creating temporary staging directory..."
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

# Copy app to temporary directory
echo "📋 Copying TODO.app to staging..."
cp -R "$APP_PATH" "$TMP_DIR/"

# Create symbolic link to Applications folder
echo "🔗 Creating Applications shortcut..."
ln -s /Applications "$TMP_DIR/Applications"

# Create compressed DMG directly
echo "💿 Creating compressed disk image..."
hdiutil create \
    -volname "$VOLUME_NAME" \
    -srcfolder "$TMP_DIR" \
    -ov \
    -format UDZO \
    "$DMG_PATH"

# Make the DMG internet-enabled (optional, removes quarantine on download)
echo "🌐 Setting internet-enable flag..."
hdiutil internet-enable -yes "$DMG_PATH" 2>/dev/null || true

echo ""
echo "✅ DMG created successfully!"
echo ""
echo "📦 Your installer is ready at: $DMG_PATH"
echo ""
echo "📊 DMG Info:"
ls -lh "$DMG_PATH" | awk '{print "   Size: " $5}'
echo ""
echo "📤 To distribute:"
echo "   1. Share the DMG file with users"
echo "   2. Users double-click to mount the DMG"
echo "   3. Users drag TODO.app to Applications"
echo "   4. Done!"
echo ""