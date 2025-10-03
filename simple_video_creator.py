#!/usr/bin/env python3
"""
Simple Video Creator - Basic version without ImageMagick dependency
Creates videos using just images and audio without text overlays
"""

import os
import logging
from typing import Dict, List, Optional, Any
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip, 
    concatenate_videoclips, ColorClip
)
import random

logger = logging.getLogger('FlashVideoBot.SimpleVideoCreator')

class SimpleVideoCreator:
    """Simple video creator that doesn't require ImageMagick"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.video_config = config.get('video', {})
        self.width = self.video_config.get('width', 1080)
        self.height = self.video_config.get('height', 1920)
        self.fps = self.video_config.get('fps', 30)
        self.max_duration = self.video_config.get('duration', 30)
    
    async def create_video(self, article: Dict[str, Any], images: List[str], audio_path: Optional[str] = None) -> Optional[str]:
        """
        Create a simple video with images and audio
        
        Args:
            article: Article data
            images: List of image paths
            audio_path: Path to audio file
            
        Returns:
            Path to created video file
        """
        try:
            title = article.get('title', 'News Video')
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()[:50]
            
            # Output path
            output_dir = os.path.join(os.getcwd(), 'videos')
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = article.get('published_date', '').replace(':', '-').replace(' ', '_')
            output_file = os.path.join(output_dir, f"news_video_{safe_title}_{timestamp}.mp4")
            
            logger.info(f"Creating simple video for: {title}")
            
            # Create video clips from images
            video_clips = []
            
            if not images:
                # Create a simple colored background if no images
                logger.warning("No images available, creating colored background")
                color_clip = ColorClip(
                    size=(self.width, self.height),
                    color=(30, 30, 60),  # Dark blue
                    duration=self.max_duration
                )
                video_clips.append(color_clip)
            else:
                # Calculate duration per image
                duration_per_image = self.max_duration / len(images)
                
                for i, image_path in enumerate(images):
                    try:
                        if os.path.exists(image_path):
                            # Create image clip
                            img_clip = ImageClip(image_path)
                            
                            # Resize to fit screen
                            img_clip = img_clip.resize(height=self.height)
                            if img_clip.w > self.width:
                                img_clip = img_clip.resize(width=self.width)
                            
                            # Center the image
                            img_clip = img_clip.set_position('center')
                            img_clip = img_clip.set_duration(duration_per_image)
                            
                            # Add simple zoom effect
                            zoom_factor = 1.05 + (i * 0.02)  # Slight zoom variation
                            img_clip = img_clip.resize(zoom_factor)
                            
                            video_clips.append(img_clip)
                            
                    except Exception as e:
                        logger.warning(f"Failed to process image {image_path}: {e}")
                        continue
            
            if not video_clips:
                logger.error("No video clips created")
                return None
            
            # Concatenate video clips
            if len(video_clips) == 1:
                final_video = video_clips[0]
            else:
                final_video = concatenate_videoclips(video_clips, method="compose")
            
            # Add audio if available
            if audio_path and os.path.exists(audio_path):
                try:
                    audio_clip = AudioFileClip(audio_path)
                    # Match audio duration to video
                    if audio_clip.duration > final_video.duration:
                        audio_clip = audio_clip.subclip(0, final_video.duration)
                    elif audio_clip.duration < final_video.duration:
                        final_video = final_video.subclip(0, audio_clip.duration)
                    
                    final_video = final_video.set_audio(audio_clip)
                    
                except Exception as e:
                    logger.warning(f"Failed to add audio: {e}")
            
            # Write video file
            logger.info(f"Writing video to: {output_file}")
            final_video.write_videofile(
                output_file,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Clean up
            final_video.close()
            if audio_path and os.path.exists(audio_path):
                try:
                    AudioFileClip(audio_path).close()
                except:
                    pass
            
            logger.info(f"Video created successfully: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            return None