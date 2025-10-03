# FlashVideoBot - Windows Setup Script
# Run this script to set up the environment on Windows

Write-Host "🚀 FlashVideoBot Windows Setup" -ForegroundColor Green
Write-Host "=" * 50

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8 or higher" -ForegroundColor Red
    Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Create virtual environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor Blue
if (Test-Path "venv") {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Blue
& "venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📚 Installing dependencies..." -ForegroundColor Blue
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Run setup script
Write-Host "⚙️ Running setup script..." -ForegroundColor Blue
python setup.py

Write-Host ""
Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit config/config_local.yaml with your API keys" -ForegroundColor Yellow
Write-Host "2. Run: python main.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "To activate the environment in the future:" -ForegroundColor Cyan
Write-Host "   venv\Scripts\activate" -ForegroundColor Cyan