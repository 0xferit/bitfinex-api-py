#!/bin/bash

# PyPI Upload Script for bitfinex-api-py-postonly
# Usage: PYPI_TOKEN=your-token-here ./publish.sh

set -e

echo "==========================================

echo "PyPI Package Publisher"
echo "Package: bitfinex-api-py-postonly"
echo "Version: 3.0.5.post1"
echo "=========================================="
echo ""

# Check if token is provided
if [ -z "$PYPI_TOKEN" ]; then
    echo "❌ Error: PYPI_TOKEN environment variable not set"
    echo ""
    echo "Usage:"
    echo "  PYPI_TOKEN=pypi-your-token-here ./publish.sh"
    echo ""
    echo "To get a token:"
    echo "  1. Go to https://pypi.org/manage/account/token/"
    echo "  2. Create a new API token"
    echo "  3. Copy the token (starts with 'pypi-')"
    echo ""
    exit 1
fi

# Validate token format
if [[ ! "$PYPI_TOKEN" =~ ^pypi- ]]; then
    echo "⚠️  Warning: Token should start with 'pypi-'"
    echo "Make sure you're using a PyPI API token, not your password"
    echo ""
fi

echo "📦 Package files to upload:"
ls -lh dist/*.whl dist/*.tar.gz
echo ""

echo "🔍 Running final checks..."
twine check dist/* || exit 1
echo "✅ Package validation passed"
echo ""

echo "📤 Uploading to PyPI..."
echo "(Using token: ${PYPI_TOKEN:0:10}...)"
echo ""

# Upload using the token
TWINE_USERNAME=__token__ TWINE_PASSWORD="$PYPI_TOKEN" twine upload dist/* --verbose

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Success! Package uploaded to PyPI"
    echo ""
    echo "📦 View your package at:"
    echo "   https://pypi.org/project/bitfinex-api-py-postonly/"
    echo ""
    echo "📥 Install with:"
    echo "   pip install bitfinex-api-py-postonly"
    echo ""
    echo "Next steps:"
    echo "  1. Test installation: pip install bitfinex-api-py-postonly"
    echo "  2. Create GitHub release with tag v3.0.5.post1"
    echo "  3. Update repository topics for discoverability"
else
    echo ""
    echo "❌ Upload failed. Please check your token and try again."
    echo ""
    echo "Common issues:"
    echo "  - Invalid token: Get a new one from https://pypi.org/manage/account/token/"
    echo "  - Package exists: You may need to increment version in setup.py"
    echo "  - Network issues: Try again in a few minutes"
    exit 1
fi