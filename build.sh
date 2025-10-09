#!/bin/bash
# Script to build the django-scotty package using uv

set -e

echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info django_scotty.egg-info

echo "📦 Building package with uv..."
uv build

echo "✅ Build complete! Package files are in dist/"
ls -lh dist/

echo ""
echo "📝 Next steps:"
echo "  - Test locally: uv pip install dist/*.whl"
echo "  - Publish to TestPyPI: uv publish --publish-url https://test.pypi.org/legacy/"
echo "  - Publish to PyPI: uv publish"
