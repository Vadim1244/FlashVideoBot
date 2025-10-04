#!/usr/bin/env python3
"""
Simple test script to run one video
"""

import os
import logging
import sys

# Add the current directory to path to ensure imports work
sys.path.append(os.getcwd())

from src.config_manager import ConfigManager
from enhanced_video_creator import EnhancedVideoCreator
from src.audio_manager import AudioManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'flashvideobot.log'))
    ]
)
logger = logging.getLogger('FlashVideoBot.Test')

async def main():
    # Load config
    config = ConfigManager().get_config()
    
    # Initialize components
    audio_manager = AudioManager(config)
    video_creator = EnhancedVideoCreator(config)
    
    # Create a simple test article
    article = {
        'title': 'Test Video With Audio and Captions',
        'summary': 'This is a test video to demonstrate that audio and captions are working correctly now. All issues should be fixed and this video should have both audio narration and visible captions.',
        'content': 'Extended content with more details to test the full functionality of the system with proper audio narration.',
        'published_date': '2025-10-05'
    }
    
    # Create temp dir if it doesn't exist
    os.makedirs('assets/temp', exist_ok=True)
    os.makedirs('assets/temp/audio', exist_ok=True)
    
    # Generate audio narration
    audio_path = await audio_manager.create_narration(article)
    
    if audio_path:
        logger.info(f"Generated audio at: {audio_path}")
    else:
        logger.error("Failed to generate audio")
        return
    
    # Create fallback images (we know the image cache isn't working properly)
    images = video_creator._create_fallback_images(article)
    
    # Create the video
    video_path = await video_creator.create_video(article, images, audio_path)
    
    if video_path:
        logger.info(f"Video created successfully at: {video_path}")
    else:
        logger.error("Failed to create video")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())