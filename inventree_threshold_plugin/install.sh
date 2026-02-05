#!/bin/bash
# Installation script for InvenTree Stock Threshold Plugin

set -e

echo "Installing InvenTree Stock Threshold Plugin..."

# Check if we're in a virtual environment
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "Warning: Not in a virtual environment. It's recommended to use a virtual environment."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install the plugin
echo "Installing plugin package..."
pip install -e .

# Check if InvenTree is installed
if ! python -c "import InvenTree" 2>/dev/null; then
    echo "Warning: InvenTree doesn't seem to be installed in this environment."
    echo "Please ensure InvenTree is installed before using this plugin."
    exit 1
fi

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Enable plugins in your InvenTree settings"
echo "2. Run migrations: python manage.py migrate"
echo "3. Restart InvenTree server"
echo "4. Configure plugin settings in Admin > Plugin Configuration"
echo ""
echo "For more information, see USAGE.md"
