#!/usr/bin/env python3
"""
Quick News Video Creator - Simplified Version
Creates news videos without ImageMagick dependency
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config_manager import ConfigManager
from news_fetcher import NewsFetcher  
from text_summarizer import TextSummarizer
from simple_video_creator import SimpleVideoCreator
from image_manager import ImageManager
from audio_manager import AudioManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def create_simple_news_videos():
    """Create simple news videos without complex effects"""
    print("🚀 Simple News Video Creator")
    print("=" * 50)
    print("Creating videos without text animations (ImageMagick-free)")
    print()
    
    try:
        # Initialize components
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        news_fetcher = NewsFetcher(config)
        text_summarizer = TextSummarizer(config)
        image_manager = ImageManager(config)
        audio_manager = AudioManager(config)
        video_creator = SimpleVideoCreator(config)
        
        print("📰 Fetching latest news...")
        
        # Fetch news (RSS only for this demo)
        articles = await news_fetcher.fetch_latest_news()
        
        if not articles:
            print("❌ No articles found")
            return False
            
        print(f"✅ Found {len(articles)} articles")
        
        # Process up to 2 articles for demo
        max_videos = 2
        created_videos = 0
        
        for i, article in enumerate(articles[:max_videos]):
            print(f"\n🎬 Creating video {i+1}/{min(len(articles), max_videos)}")
            print(f"📰 Title: {article.get('title', 'Unknown')[:60]}...")
            
            try:
                # Summarize article
                summary = await text_summarizer.summarize(article.get('content', ''))
                if summary:
                    article['summary'] = summary
                    article['summary_data'] = {'text': summary}
                
                # Get images
                print("🖼️  Fetching images...")
                images = await image_manager.get_images_for_article(article)
                
                # Create audio (optional)
                audio_path = None
                try:
                    print("🎵 Creating audio narration...")
                    audio_path = await audio_manager.create_narration(article)
                except Exception as e:
                    print(f"⚠️  Audio creation failed: {e}")
                
                # Create video
                print("🎬 Creating video...")
                video_path = await video_creator.create_video(
                    article=article,
                    images=images,
                    audio_path=audio_path
                )
                
                if video_path and os.path.exists(video_path):
                    file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
                    print(f"✅ Video created: {os.path.basename(video_path)}")
                    print(f"📊 Size: {file_size:.1f} MB")
                    created_videos += 1
                else:
                    print("❌ Video creation failed")
                    
            except Exception as e:
                print(f"❌ Error processing article: {e}")
                continue
        
        print(f"\n🎉 Created {created_videos} videos!")
        print(f"📁 Check the 'videos' folder for your content")
        
        return created_videos > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("Simple News Video Creator")
    print("Creates videos using basic MoviePy functionality")
    print("(No ImageMagick required)")
    print()
    
    # Ensure directories exist
    os.makedirs('videos', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('assets/temp', exist_ok=True)
    
    # Run the video creation
    success = asyncio.run(create_simple_news_videos())
    
    if success:
        print("\n✅ Process completed successfully!")
        print("Your news videos are ready in the 'videos' folder")
    else:
        print("\n❌ Process failed")
        print("Check the error messages above for details")

if __name__ == "__main__":
    main()