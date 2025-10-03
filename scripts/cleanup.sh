#!/bin/bash
# Clean up temporary and outdated files from the project

set -e

echo "🧹 GitCommit AI - Project Cleanup"
echo "=================================="

# Track what we're cleaning
CLEANED=0

echo ""
echo "📋 Cleaning Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.pyd" -delete 2>/dev/null || true
echo "✅ Python cache cleaned"
((CLEANED++))

echo ""
echo "📋 Cleaning pytest cache..."
rm -rf .pytest_cache/ 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
echo "✅ Pytest cache cleaned"
((CLEANED++))

echo ""
echo "📋 Cleaning coverage files..."
rm -f .coverage coverage.json 2>/dev/null || true
rm -rf htmlcov/ 2>/dev/null || true
echo "✅ Coverage files cleaned"
((CLEANED++))

echo ""
echo "📋 Cleaning build artifacts..."
rm -rf build/ dist/ *.egg-info 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
echo "✅ Build artifacts cleaned"
((CLEANED++))

echo ""
echo "📋 Cleaning macOS files..."
find . -name ".DS_Store" -delete 2>/dev/null || true
echo "✅ macOS files cleaned"
((CLEANED++))

echo ""
echo "📋 Cleaning mypy cache..."
rm -rf .mypy_cache/ 2>/dev/null || true
find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
echo "✅ Mypy cache cleaned"
((CLEANED++))

echo ""
echo "📋 Cleaning ruff cache..."
rm -rf .ruff_cache/ 2>/dev/null || true
find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
echo "✅ Ruff cache cleaned"
((CLEANED++))

echo ""
echo "✨ Cleanup complete! ($CLEANED categories cleaned)"
echo ""
echo "⚠️  Note: .env file kept (contains API keys)"
echo "⚠️  Note: .git folder kept (version control)"
