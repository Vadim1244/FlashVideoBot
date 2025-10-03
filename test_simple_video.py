#!/usr/bin/env python3
"""
Test video creation with simplified approach
"""

import asyncio
import os
import sys
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from simple_video_creator import SimpleVideoCreator
from config_manager import ConfigManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_video_creation():
    """Test creating a simple video"""
    print("🎬 Testing Simple Video Creation")
    print("=" * 50)
    
    try:
        # Load config
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        # Create video creator
        video_creator = SimpleVideoCreator(config)
        
        # Sample article data
        article = {
            'title': 'Test News Video',
            'summary': 'This is a test news article for video creation.',
            'published_date': '2025-10-04_10-00-00'
        }
        
        # Check for sample images
        images = []
        assets_dir = os.path.join(os.getcwd(), 'assets', 'images')
        if os.path.exists(assets_dir):
            for file in os.listdir(assets_dir):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    images.append(os.path.join(assets_dir, file))
        
        if not images:
            print("ℹ️  No sample images found, will create colored background")
        else:
            print(f"📸 Found {len(images)} images to use")
        
        # Create video
        print("🎬 Creating video...")
        video_path = await video_creator.create_video(
            article=article,
            images=images[:3],  # Use max 3 images
            audio_path=None  # No audio for this test
        )
        
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            print(f"✅ Video created successfully!")
            print(f"📁 Location: {video_path}")
            print(f"📊 Size: {file_size:.1f} MB")
            return True
        else:
            print("❌ Video creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_video_creation())
    if success:
        print("\n🎉 Test completed successfully!")
        print("Check the 'videos' folder for the generated video.")
    else:
        print("\n💥 Test failed!")