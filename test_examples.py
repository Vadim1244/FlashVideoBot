"""
Example usage and testing script for FlashVideoBot

This script demonstrates various ways to use the FlashVideoBot
and provides testing functionality for development.

Author: FlashVideoBot Team
Date: October 2025
"""

import asyncio
import sys
import os
import argparse
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config_manager import ConfigManager
from src.news_fetcher import NewsFetcher
from src.text_summarizer import TextSummarizer
from main import FlashVideoBot


async def test_news_fetching():
    """Test news fetching functionality."""
    print("🧪 Testing News Fetching...")
    
    config = ConfigManager()
    fetcher = NewsFetcher(config)
    
    articles = await fetcher.fetch_latest_news()
    
    if articles:
        print(f"✅ Successfully fetched {len(articles)} articles")
        for i, article in enumerate(articles[:3], 1):
            print(f"\n{i}. {article.get('title', 'No title')}")
            print(f"   Source: {article.get('source', 'Unknown')}")
            print(f"   Published: {article.get('published_at', 'Unknown')}")
    else:
        print("❌ No articles fetched")
    
    return len(articles) > 0


async def test_summarization():
    """Test text summarization functionality."""
    print("\n🧪 Testing Text Summarization...")
    
    config = ConfigManager()
    summarizer = TextSummarizer(config)
    
    # Test article
    test_article = {
        'title': 'Breaking: Major Technology Breakthrough Announced',
        'description': 'Scientists at a leading university have announced a major breakthrough in quantum computing technology. The new development could revolutionize how we process information and solve complex problems. Researchers say this advancement brings us closer to practical quantum computers that could outperform traditional computers in specific tasks.',
        'content': 'The research team, led by Dr. Jane Smith, has successfully demonstrated a new quantum error correction method that significantly improves the stability of quantum bits. This breakthrough addresses one of the major challenges in quantum computing and could accelerate the development of practical quantum computers for commercial use.'
    }
    
    # Test summarization
    summary = summarizer.summarize(test_article['content'])
    hook = summarizer.generate_hook(test_article)
    key_points = summarizer.generate_key_points(test_article)
    
    print(f"✅ Summary: {summary}")
    print(f"✅ Hook: {hook}")
    print(f"✅ Key Points: {len(key_points)} generated")
    for point in key_points:
        print(f"   {point}")
    
    return True


async def test_image_fetching():
    """Test image fetching functionality."""
    print("\n🧪 Testing Image Fetching...")
    
    try:
        from src.image_manager import ImageManager
        
        config = ConfigManager()
        image_manager = ImageManager(config)
        
        # Test article
        test_article = {
            'title': 'Technology Breakthrough in AI',
            'description': 'Artificial intelligence researchers achieve new milestone',
            'category': 'technology'
        }
        
        images = await image_manager.get_images_for_article(test_article, count=2)
        
        if images:
            print(f"✅ Successfully fetched {len(images)} images")
            for i, image_path in enumerate(images, 1):
                print(f"   {i}. {os.path.basename(image_path)}")
        else:
            print("⚠️  No images fetched (API keys may be missing)")
        
        return True
        
    except Exception as e:
        print(f"❌ Image fetching test failed: {str(e)}")
        return False


async def test_audio_generation():
    """Test audio generation functionality."""
    print("\n🧪 Testing Audio Generation...")
    
    try:
        from src.audio_manager import AudioManager
        
        config = ConfigManager()
        audio_manager = AudioManager(config)
        
        # Test article
        test_article = {
            'title': 'Breaking News Update',
            'summary': 'This is a test summary for audio generation.',
            'hook': 'Breaking: Important news development'
        }
        
        audio_path = await audio_manager.create_narration(test_article)
        
        if audio_path and os.path.exists(audio_path):
            print(f"✅ Audio generated: {os.path.basename(audio_path)}")
            return True
        else:
            print("⚠️  Audio generation failed (TTS may not be available)")
            return False
            
    except Exception as e:
        print(f"❌ Audio generation test failed: {str(e)}")
        return False


async def run_full_test():
    """Run a complete test of the FlashVideoBot."""
    print("\n🧪 Running Full FlashVideoBot Test...")
    
    try:
        # Create a test bot with limited articles
        bot = FlashVideoBot()
        
        # Override max articles for testing
        bot.config.config['news']['max_articles'] = 1
        
        # Run the bot
        await bot.run()
        
        # Check if video was created
        video_dir = "videos"
        if os.path.exists(video_dir):
            videos = [f for f in os.listdir(video_dir) if f.endswith('.mp4')]
            if videos:
                print(f"✅ Full test successful - created {len(videos)} video(s)")
                return True
        
        print("⚠️  Full test completed but no videos were created")
        return False
        
    except Exception as e:
        print(f"❌ Full test failed: {str(e)}")
        return False


async def create_sample_video():
    """Create a sample video with predefined content."""
    print("\n🎬 Creating Sample Video...")
    
    try:
        from src.video_creator import VideoCreator
        from src.image_manager import ImageManager
        from src.audio_manager import AudioManager
        
        config = ConfigManager()
        
        # Sample article
        sample_article = {
            'title': 'FlashVideoBot Sample Video',
            'summary': 'This is a demonstration of FlashVideoBot\'s capabilities. The system can create engaging videos automatically from news content.',
            'hook': '🚀 Welcome to FlashVideoBot!',
            'key_points': [
                '• Automated video generation',
                '• Professional text animations',
                '• Dynamic visual effects'
            ],
            'source': 'FlashVideoBot Demo',
            'sentiment': 'positive'
        }
        
        # Create managers
        video_creator = VideoCreator(config)
        image_manager = ImageManager(config)
        audio_manager = AudioManager(config)
        
        # Get sample images
        images = await image_manager.get_images_for_article(sample_article, count=3)
        
        # Generate audio
        audio_path = await audio_manager.create_narration(sample_article)
        
        # Create video
        video_path = await video_creator.create_video(sample_article, images, audio_path)
        
        if video_path and os.path.exists(video_path):
            print(f"✅ Sample video created: {os.path.basename(video_path)}")
            return True
        else:
            print("❌ Sample video creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Sample video creation failed: {str(e)}")
        return False


def print_config_status():
    """Print current configuration status."""
    print("\n📋 Configuration Status")
    print("=" * 30)
    
    try:
        config = ConfigManager()
        config.print_config_summary()
    except Exception as e:
        print(f"❌ Error reading configuration: {str(e)}")


async def main():
    """Main testing function."""
    parser = argparse.ArgumentParser(description='FlashVideoBot Testing and Examples')
    parser.add_argument('--test', choices=[
        'news', 'summarization', 'images', 'audio', 'full', 'sample'
    ], help='Run specific test')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    parser.add_argument('--config', action='store_true', help='Show configuration status')
    
    args = parser.parse_args()
    
    if args.config:
        print_config_status()
        return
    
    print("🧪 FlashVideoBot Testing Suite")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 0
    
    if args.test == 'news' or args.all:
        total_tests += 1
        if await test_news_fetching():
            tests_passed += 1
    
    if args.test == 'summarization' or args.all:
        total_tests += 1
        if await test_summarization():
            tests_passed += 1
    
    if args.test == 'images' or args.all:
        total_tests += 1
        if await test_image_fetching():
            tests_passed += 1
    
    if args.test == 'audio' or args.all:
        total_tests += 1
        if await test_audio_generation():
            tests_passed += 1
    
    if args.test == 'full':
        total_tests += 1
        if await run_full_test():
            tests_passed += 1
    
    if args.test == 'sample':
        total_tests += 1
        if await create_sample_video():
            tests_passed += 1
    
    if not any([args.test, args.all, args.config]):
        # Default: run basic tests
        total_tests = 2
        if await test_news_fetching():
            tests_passed += 1
        if await test_summarization():
            tests_passed += 1
        
        print_config_status()
    
    if total_tests > 0:
        print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
        
        if tests_passed == total_tests:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed - check configuration and dependencies")


if __name__ == "__main__":
    asyncio.run(main())