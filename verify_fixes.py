#!/usr/bin/env python3
"""
Verification script to check that audio, images, and captions are all working correctly
"""

import os
import logging
import sys
import asyncio

# Add the current directory to path to ensure imports work
sys.path.append(os.getcwd())

from src.config_manager import ConfigManager
from enhanced_video_creator import EnhancedVideoCreator
from src.audio_manager import AudioManager
from PIL import Image, ImageDraw, ImageFont

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'flashvideobot.log'))
    ]
)
logger = logging.getLogger('FlashVideoBot.Verification')

def create_test_image(filename, text, color):
    """Create a test image with text"""
    width, height = 1080, 1920
    img = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a standard font
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 60)
        except:
            font = ImageFont.load_default()
    
    # Draw text in the center
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(text_position, text, fill=(255, 255, 255), font=font)
    
    # Save the image
    img_path = os.path.join('assets', 'temp', filename)
    img.save(img_path)
    logger.info(f"Created test image: {img_path}")
    return img_path

async def main():
    # Load config
    config = ConfigManager().get_config()
    
    # Initialize components
    audio_manager = AudioManager(config)
    video_creator = EnhancedVideoCreator(config)
    
    # Create a simple test article
    article = {
        'title': 'Verification Test: Audio, Images, and Captions',
        'summary': 'This video tests that all three components (audio narration, images, and captions) are working correctly after the fixes.',
        'content': 'This is a verification test to ensure that audio narration, images, and captions are all working correctly in the final video output.',
        'published_date': '2025-10-05'
    }
    
    # Create temp directories if they don't exist
    os.makedirs('assets/temp', exist_ok=True)
    os.makedirs('assets/temp/audio', exist_ok=True)
    
    # Create test images with different colors
    logger.info("Creating test images...")
    images = [
        create_test_image('test_image_1.png', 'TEST IMAGE 1', (30, 64, 175)),  # Blue
        create_test_image('test_image_2.png', 'TEST IMAGE 2', (67, 56, 202)),  # Purple
        create_test_image('test_image_3.png', 'TEST IMAGE 3', (15, 23, 42))    # Dark
    ]
    
    # Generate audio narration
    logger.info("Generating audio narration...")
    audio_path = await audio_manager.create_narration(article)
    
    if audio_path:
        logger.info(f"Generated audio at: {audio_path}")
    else:
        logger.error("Failed to generate audio")
        return
    
    # Create the video with our test images
    logger.info("Creating video with test images, audio, and captions...")
    video_path = await video_creator.create_video(article, images, audio_path)
    
    if video_path:
        logger.info(f"Verification video created successfully at: {video_path}")
        logger.info("✅ All components (audio, images, and captions) should now be working!")
    else:
        logger.error("Failed to create verification video")

if __name__ == "__main__":
    asyncio.run(main())