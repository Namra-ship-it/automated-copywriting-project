#!/bin/bash
# Setup script for Automated Copywriting & Tone Transformer

set -e

echo "🔧 Setting up Automated Copywriting & Tone Transformer..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📌 Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists."
fi

# Activate virtual environment
echo "🚀 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Copy environment file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your DEEPSEEK_API_KEY"
else
    echo "✅ .env already exists."
fi

# Create output directories
echo "📁 Creating output directories..."
mkdir -p outputs/real_time
mkdir -p outputs/batch
mkdir -p logs

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your DEEPSEEK_API_KEY"
echo "  2. Run: python src/cli.py --interactive"
echo "  3. Or run: bash scripts/run_real_time.sh"
echo "  4. Or run tests: pytest tests/ -v"
echo ""
