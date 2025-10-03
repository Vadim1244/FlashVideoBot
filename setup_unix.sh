#!/bin/bash
# FlashVideoBot - Linux/macOS Setup Script

echo "🚀 FlashVideoBot Setup for Linux/macOS"
echo "================================================"

# Check if Python is installed
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python found: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "✅ Python found: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.8 or higher"
    echo "   Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "   macOS: brew install python"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "✅ Virtual environment already exists"
else
    $PYTHON_CMD -m venv venv
    if [ $? -eq 0 ]; then
        echo "✅ Virtual environment created"
    else
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📈 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check for FFmpeg
echo "🎵 Checking for FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg is installed"
else
    echo "⚠️  FFmpeg not found (optional but recommended)"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   Install with: brew install ffmpeg"
    else
        echo "   Ubuntu/Debian: sudo apt install ffmpeg"
        echo "   CentOS/RHEL: sudo yum install ffmpeg"
    fi
fi

# Run setup script
echo "⚙️ Running setup script..."
python setup.py

echo ""
echo "🎉 Setup complete!"
echo "Next steps:"
echo "1. Edit config/config_local.yaml with your API keys"
echo "2. Run: python main.py"
echo ""
echo "To activate the environment in the future:"
echo "   source venv/bin/activate"