#!/bin/bash
# Script to publish GitCommit AI to PyPI

set -e  # Exit on error

echo "🚀 GitCommit AI - Publishing to PyPI"
echo "===================================="

# 1. Check tests
echo ""
echo "📋 Step 1: Running tests..."
pytest tests/ -v || { echo "❌ Tests failed!"; exit 1; }
echo "✅ All tests passed"

# 2. Check git status
echo ""
echo "📋 Step 2: Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: Uncommitted changes detected"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 3. Clean build artifacts
echo ""
echo "📋 Step 3: Cleaning build artifacts..."
rm -rf dist/ build/ *.egg-info
echo "✅ Clean"

# 4. Build package
echo ""
echo "📋 Step 4: Building package..."
python -m build
echo "✅ Package built"

# 5. Check package
echo ""
echo "📋 Step 5: Checking package..."
twine check dist/*
echo "✅ Package valid"

# 6. Ask for upload destination
echo ""
echo "📋 Step 6: Upload package"
echo "Where to upload?"
echo "  1) TestPyPI (recommended for first upload)"
echo "  2) PyPI (production)"
read -p "Choose (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "🔄 Uploading to TestPyPI..."
        twine upload --repository testpypi dist/*
        echo ""
        echo "✅ Uploaded to TestPyPI!"
        echo "Test installation: pip install --index-url https://test.pypi.org/simple/ gitcommit-ai"
        ;;
    2)
        echo ""
        read -p "⚠️  Upload to production PyPI? This cannot be undone! (yes/no) " confirm
        if [ "$confirm" = "yes" ]; then
            echo "🔄 Uploading to PyPI..."
            twine upload dist/*
            echo ""
            echo "✅ Uploaded to PyPI!"
            echo "Anyone can now install: pip install gitcommit-ai"
        else
            echo "❌ Cancelled"
            exit 1
        fi
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎉 Done!"
