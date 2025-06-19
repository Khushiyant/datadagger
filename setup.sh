#!/usr/bin/env bash

# DataDagger Setup and Test Script

echo "🔧 Setting up DataDagger OSINT Tool..."

# Create output directory
mkdir -p output

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    exit 1
fi

echo "✅ pip3 found"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys before using DataDagger"
fi

# Make CLI executable
chmod +x datadagger.py

echo "🎉 DataDagger setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: ./datadagger.py --help"
echo "3. Try: ./datadagger.py search 'your query here'"
echo ""
echo "📖 For more information, see README.md"
