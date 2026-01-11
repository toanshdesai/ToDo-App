#!/bin/bash
# Build script for TODO app macOS bundle
# This creates a standalone .app that works on any Mac without Python

set -e

echo "🔨 Building TODO app for macOS..."
echo ""

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "️  PyInstaller not found. Installing..."
    pip install pyinstaller>=6.0.0
fi

echo " Building standalone .app bundle..."
pyinstaller TODO.spec

echo ""
echo "Build complete!"
echo ""
echo " Your app is ready at: dist/TODO.app"
echo ""
echo " To run it:"
echo "   open dist/TODO.app"
echo ""
echo " To share with others:"
echo "   1. Zip the app: zip -r TODO.app.zip dist/TODO.app"
echo "   2. Share the ZIP file"
echo "   3. Users can extract and double-click TODO.app to run"
echo ""

