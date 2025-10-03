#!/usr/bin/env python3
"""
Quick Start Script for FlashVideoBot

This script provides a simple way to get started with FlashVideoBot
with minimal configuration required.

Author: FlashVideoBot Team
Date: October 2025
"""

import os
import sys
import asyncio
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def check_setup():
    """Check if basic setup is complete."""
    issues = []
    
    # Check if virtual environment is active
    if not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
        issues.append("Virtual environment not activated")
    
    # Check if required directories exist
    required_dirs = ['videos', 'logs', 'assets/temp']
    for directory in required_dirs:
        if not os.path.exists(directory):
            issues.append(f"Missing directory: {directory}")
    
    # Check if config exists
    if not os.path.exists('config/config.yaml'):
        issues.append("Missing configuration file")
    
    return issues


def create_minimal_config():
    """Create a minimal configuration for quick testing."""
    config_content = """# Minimal FlashVideoBot Configuration for Quick Start
news:
  max_articles: 3
  rss_feeds:
    - "https://feeds.bbci.co.uk/news/rss.xml"
    - "https://rss.cnn.com/rss/edition.rss"
  categories: ["general", "technology"]

video:
  width: 1080
  height: 1920
  fps: 30
  duration: 20
  text:
    font_size: 60
    title_font_size: 80
    font_color: "#FFFFFF"
    bg_color: "#000000"

audio:
  tts:
    engine: "gtts"
    language: "en"
    speed: 1.2
  music:
    enabled: false
    volume: 0.3

logging:
  level: "INFO"
  log_to_file: true

performance:
  max_workers: 2
"""
    
    os.makedirs('config', exist_ok=True)
    with open('config/config_local.yaml', 'w') as f:
        f.write(config_content)
    
    print("✅ Created minimal configuration: config/config_local.yaml")


async def quick_demo():
    """Run a quick demonstration with RSS feeds only."""
    print("🚀 FlashVideoBot Quick Demo")
    print("=" * 40)
    print("This demo uses RSS feeds (no API keys required)")
    print("")
    
    try:
        from main import FlashVideoBot
        
        # Create bot with minimal config
        bot = FlashVideoBot('config/config_local.yaml')
        
        # Override settings for demo
        bot.config.config['news']['max_articles'] = 2
        bot.config.config['audio']['music']['enabled'] = False
        bot.config.config['video']['duration'] = 15
        
        print("📰 Fetching news from RSS feeds...")
        print("🎬 Creating videos (this may take a few minutes)...")
        print("")
        
        # Run the bot
        await bot.run()
        
        print("\n🎉 Demo completed!")
        print("Check the 'videos' folder for generated content.")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check internet connection for RSS feeds")
        print("3. Run setup.py for full environment check")


def main():
    """Main quick start function."""
    print("🚀 FlashVideoBot Quick Start")
    print("=" * 35)
    
    # Check basic setup
    issues = check_setup()
    
    if issues:
        print("⚠️  Setup issues detected:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nFixing basic setup...")
        
        # Create required directories
        os.makedirs('videos', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        os.makedirs('assets/temp', exist_ok=True)
        
        # Create minimal config
        create_minimal_config()
        
        print("✅ Basic setup completed")
    
    print("\nSelect an option:")
    print("1. Run quick demo (RSS feeds only, no API keys needed)")
    print("2. Run full bot (requires API keys in config)")
    print("3. Test configuration")
    print("4. Exit")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            print("\nStarting quick demo...")
            asyncio.run(quick_demo())
        
        elif choice == "2":
            print("\nStarting full bot...")
            from main import main as main_bot
            asyncio.run(main_bot())
        
        elif choice == "3":
            print("\nTesting configuration...")
            try:
                from src.config_manager import ConfigManager
                config = ConfigManager()
                config.print_config_summary()
                print("\n✅ Configuration loaded successfully")
            except Exception as e:
                print(f"❌ Configuration error: {str(e)}")
        
        elif choice == "4":
            print("👋 Goodbye!")
            return
        
        else:
            print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()