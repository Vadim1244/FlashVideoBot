"""
Setup and Environment Initialization for FlashVideoBot

This script helps set up the development environment and initialize
the project with required dependencies and configuration.

Author: FlashVideoBot Team
Date: October 2025
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True


def create_directories():
    """Create required project directories."""
    directories = [
        "videos",
        "logs", 
        "assets/temp",
        "assets/temp/audio",
        "assets/temp/image_cache",
        "assets/temp/news_cache",
        "assets/fonts",
        "assets/music"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")


def check_virtual_environment():
    """Check if running in virtual environment."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
        return True
    else:
        print("⚠️  Not running in virtual environment")
        print("   Recommendation: Create and activate a virtual environment")
        print("   Commands:")
        print("     python -m venv venv")
        if platform.system() == "Windows":
            print("     venv\\Scripts\\activate")
        else:
            print("     source venv/bin/activate")
        return False


def install_dependencies():
    """Install Python dependencies."""
    try:
        print("📦 Installing Python dependencies...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print("❌ Failed to install dependencies")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {str(e)}")
        return False


def download_nltk_data():
    """Download required NLTK data."""
    try:
        print("📚 Downloading NLTK data...")
        import nltk
        
        # Download required NLTK data
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        
        print("✅ NLTK data downloaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error downloading NLTK data: {str(e)}")
        return False


def check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg is installed")
            return True
        else:
            print("⚠️  FFmpeg not found")
            return False
    except FileNotFoundError:
        print("⚠️  FFmpeg not found")
        print("   FFmpeg is optional but recommended for better audio/video processing")
        print("   Install instructions:")
        
        system = platform.system()
        if system == "Windows":
            print("     - Download from: https://ffmpeg.org/download.html")
            print("     - Add to PATH environment variable")
        elif system == "Darwin":  # macOS
            print("     - brew install ffmpeg")
        else:  # Linux
            print("     - sudo apt install ffmpeg  (Ubuntu/Debian)")
            print("     - sudo yum install ffmpeg  (CentOS/RHEL)")
        
        return False


def create_config_template():
    """Create local configuration template if it doesn't exist."""
    config_local_path = "config/config_local.yaml"
    
    if not os.path.exists(config_local_path):
        try:
            import shutil
            shutil.copy("config/config.yaml", config_local_path)
            print(f"✅ Created local configuration: {config_local_path}")
            print("   Please edit this file to add your API keys")
            return True
        except Exception as e:
            print(f"❌ Error creating config template: {str(e)}")
            return False
    else:
        print(f"✅ Local configuration already exists: {config_local_path}")
        return True


def check_api_keys():
    """Check if API keys are configured."""
    try:
        from src.config_manager import ConfigManager
        config = ConfigManager("config/config_local.yaml")
        
        api_keys = config.get_api_keys()
        missing_keys = []
        
        for key_name, key_value in api_keys.items():
            if not key_value or key_value.startswith("YOUR_"):
                missing_keys.append(key_name)
        
        if missing_keys:
            print("⚠️  Missing API keys:")
            for key in missing_keys:
                print(f"     - {key}")
            print("\n   Get API keys from:")
            print("     - NewsAPI: https://newsapi.org")
            print("     - Unsplash: https://unsplash.com/developers")
            print("     - Pixabay: https://pixabay.com/api/docs/")
            print(f"\n   Add them to: config/config_local.yaml")
            return False
        else:
            print("✅ All API keys configured")
            return True
            
    except Exception as e:
        print(f"⚠️  Could not check API keys: {str(e)}")
        return False


def run_test():
    """Run a basic test to ensure everything works."""
    try:
        print("🧪 Running basic test...")
        
        # Test imports
        from src.config_manager import ConfigManager
        from src.news_fetcher import NewsFetcher
        from src.text_summarizer import TextSummarizer
        
        # Test configuration
        config = ConfigManager()
        
        print("✅ All modules imported successfully")
        print("✅ Configuration loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


def main():
    """Main setup function."""
    print("🚀 FlashVideoBot Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check virtual environment
    check_virtual_environment()
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed - could not install dependencies")
        sys.exit(1)
    
    # Download NLTK data
    download_nltk_data()
    
    # Check FFmpeg
    check_ffmpeg()
    
    # Create config template
    create_config_template()
    
    # Check API keys
    check_api_keys()
    
    # Run basic test
    if run_test():
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Add your API keys to config/config_local.yaml")
        print("2. Run: python main.py")
    else:
        print("\n⚠️  Setup completed with warnings")
        print("   Some features may not work without proper configuration")


if __name__ == "__main__":
    main()