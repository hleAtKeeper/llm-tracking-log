#!/bin/bash
# Start unified monitoring system

cd "$(dirname "$0")"

echo "========================================"
echo "Starting Unified Monitoring System"
echo "========================================"
echo ""

# Check Python dependencies
echo "Checking dependencies..."
python3 -c "import watchdog; from AppKit import NSWorkspace" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "⚠️  Missing dependencies!"
    echo ""
    echo "Install with:"
    echo "  pip install watchdog pyobjc-framework-Cocoa"
    exit 1
fi

echo "✓ Dependencies OK"
echo ""

# Start monitor
echo "Starting monitor..."
python3 monitor.py

echo ""
echo "Monitor stopped."
