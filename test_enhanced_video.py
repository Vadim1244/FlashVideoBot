#!/usr/bin/env python3
"""
Test script to create an enhanced news video with proper fallback content
"""

import asyncio
import os
import sys
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from enhanced_video_creator import EnhancedVideoCreator
from config_manager import ConfigManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_enhanced_video():
    """Test creating an enhanced video with text content"""
    print("🎬 Testing Enhanced Video Creation")
    print("=" * 50)
    
    try:
        # Load config
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        # Create enhanced video creator
        video_creator = EnhancedVideoCreator(config)
        
        # Sample article data with real content
        article = {
            'title': 'Breaking: Major Tech Company Announces Revolutionary AI Breakthrough',
            'summary': 'Scientists have developed a new artificial intelligence system that can process information 10 times faster than previous models. This breakthrough could revolutionize industries from healthcare to transportation. The new system uses advanced neural networks and quantum computing principles.',
            'content': 'In a groundbreaking announcement today, researchers unveiled an AI system that represents a significant leap forward in machine learning capabilities...',
            'published_date': '2025-10-04_12-00-00'
        }
        
        print(f"📰 Creating video for: {article['title'][:60]}...")
        
        # Force creation with no external images to test fallback
        images = []  # Empty list to force fallback creation
        
        # Create video
        print("🎬 Creating enhanced video with fallback content...")
        video_path = await video_creator.create_video(
            article=article,
            images=images,  # Empty to force fallback
            audio_path=None
        )
        
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            print(f"✅ Enhanced video created successfully!")
            print(f"📁 Location: {video_path}")
            print(f"📊 Size: {file_size:.1f} MB")
            
            # Check if fallback images were created
            temp_dir = os.path.join(os.getcwd(), 'assets', 'temp')
            fallback_files = [f for f in os.listdir(temp_dir) if f.startswith('fallback_')]
            if fallback_files:
                print(f"🖼️  Created {len(fallback_files)} fallback images")
                for f in fallback_files:
                    print(f"   - {f}")
            
            return True
        else:
            print("❌ Enhanced video creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_video())
    if success:
        print("\n🎉 Enhanced video test completed successfully!")
        print("Your video should now have text content and proper visuals.")
        print("Check the 'videos' folder and 'assets/temp' for generated content.")
    else:
        print("\n💥 Enhanced video test failed!")