#!/usr/bin/env python3
"""
Enhanced Simple Video Creator with fallback images and text overlays
"""

import os
import logging
from typing import Dict, List, Optional, Any
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip, 
    concatenate_videoclips, ColorClip
)
from PIL import Image, ImageDraw, ImageFont
import textwrap
import random

logger = logging.getLogger('FlashVideoBot.EnhancedVideoCreator')

class EnhancedVideoCreator:
    """Enhanced video creator with fallback content and simple text overlays"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.video_config = config.get('video', {})
        self.width = self.video_config.get('width', 1080)
        self.height = self.video_config.get('height', 1920)
        self.fps = self.video_config.get('fps', 30)
        self.max_duration = self.video_config.get('duration', 30)
        
        # Create temp directory for generated images
        self.temp_dir = os.path.join(os.getcwd(), 'assets', 'temp')
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def _create_fallback_images(self, article: Dict[str, Any]) -> List[str]:
        """Create fallback images with article content"""
        images = []
        
        try:
            title = article.get('title', 'News Update')
            summary = article.get('summary', article.get('content', ''))[:200] + "..."
            
            # Create 3 different styled images
            styles = [
                {'bg': (30, 64, 175), 'text': (255, 255, 255), 'accent': (255, 87, 87)},  # Blue
                {'bg': (67, 56, 202), 'text': (255, 255, 255), 'accent': (34, 197, 94)},  # Purple  
                {'bg': (15, 23, 42), 'text': (255, 255, 255), 'accent': (59, 130, 246)}   # Dark
            ]
            
            for i, style in enumerate(styles):
                img_path = self._create_text_image(
                    title if i == 0 else summary,
                    f"fallback_{i}.png",
                    style['bg'],
                    style['text'],
                    style['accent']
                )
                if img_path:
                    images.append(img_path)
                    
        except Exception as e:
            logger.warning(f"Failed to create fallback images: {e}")
            
        return images
    
    def _create_text_image(self, text: str, filename: str, bg_color: tuple, text_color: tuple, accent_color: tuple) -> Optional[str]:
        """Create an image with text overlay"""
        try:
            # Create image
            img = Image.new('RGB', (self.width, self.height), bg_color)
            draw = ImageDraw.Draw(img)
            
            # Try to use a better font, fall back to default
            try:
                title_font = ImageFont.truetype("arial.ttf", 72)
                body_font = ImageFont.truetype("arial.ttf", 48)
            except:
                try:
                    title_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 72)
                    body_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 48)
                except:
                    title_font = ImageFont.load_default()
                    body_font = ImageFont.load_default()
            
            # Add accent bar at top
            draw.rectangle([0, 0, self.width, 20], fill=accent_color)
            
            # Wrap text
            wrapped_text = textwrap.fill(text, width=25)
            lines = wrapped_text.split('\n')
            
            # Calculate text position
            y_offset = 200
            line_height = 80
            
            # Draw text lines
            for line in lines[:8]:  # Max 8 lines
                # Get text size for centering
                bbox = draw.textbbox((0, 0), line, font=title_font if len(lines) <= 3 else body_font)
                text_width = bbox[2] - bbox[0]
                x = (self.width - text_width) // 2
                
                draw.text((x, y_offset), line, fill=text_color, 
                         font=title_font if len(lines) <= 3 else body_font)
                y_offset += line_height
            
            # Add "BREAKING NEWS" badge for first image
            if "fallback_0" in filename:
                badge_text = "BREAKING NEWS"
                bbox = draw.textbbox((0, 0), badge_text, font=body_font)
                badge_width = bbox[2] - bbox[0] + 40
                badge_height = 60
                badge_x = (self.width - badge_width) // 2
                badge_y = 100
                
                # Draw badge background
                draw.rectangle([badge_x, badge_y, badge_x + badge_width, badge_y + badge_height], 
                              fill=accent_color)
                # Draw badge text
                text_x = badge_x + 20
                text_y = badge_y + 10
                draw.text((text_x, text_y), badge_text, fill=(255, 255, 255), font=body_font)
            
            # Save image
            img_path = os.path.join(self.temp_dir, filename)
            img.save(img_path, 'PNG')
            
            logger.info(f"Created fallback image: {filename}")
            return img_path
            
        except Exception as e:
            logger.error(f"Failed to create text image: {e}")
            return None
    
    async def create_video(self, article: Dict[str, Any], images: List[str], audio_path: Optional[str] = None) -> Optional[str]:
        """
        Create an enhanced video with fallback content
        
        Args:
            article: Article data
            images: List of image paths (will create fallbacks if empty)
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
            output_file = os.path.join(output_dir, f"enhanced_news_{safe_title}_{timestamp}.mp4")
            
            logger.info(f"Creating enhanced video for: {title}")
            
            # Use provided images or create fallbacks
            if not images or not any(os.path.exists(img) for img in images):
                logger.info("No valid images found, creating fallback content")
                images = self._create_fallback_images(article)
            else:
                # Check if the provided images are actually valid and not just solid color fallbacks
                valid_images = []
                for img in images:
                    if os.path.exists(img):
                        # Skip solid color fallback images from image manager
                        if 'fallback_color_' in os.path.basename(img):
                            logger.info(f"Skipping solid color fallback: {img}")
                            continue
                        try:
                            # Try to open the image to verify it's valid
                            test_img = Image.open(img)
                            test_img.close()
                            valid_images.append(img)
                        except Exception:
                            logger.warning(f"Image file is corrupted or invalid: {img}")
                
                if not valid_images:
                    logger.info("All provided images are invalid or solid color fallbacks, creating text content instead")
                    images = self._create_fallback_images(article)
                else:
                    images = valid_images
            
            # Filter valid images
            valid_images = [img for img in images if os.path.exists(img)]
            
            if not valid_images:
                logger.error("No valid images available")
                return None
            
            # Create video clips from images
            video_clips = []
            duration_per_image = self.max_duration / len(valid_images)
            
            for i, image_path in enumerate(valid_images):
                try:
                    # Create image clip
                    img_clip = ImageClip(image_path)
                    
                    # Resize to fit screen while maintaining aspect ratio
                    img_clip = img_clip.resize(height=self.height)
                    if img_clip.w > self.width:
                        img_clip = img_clip.resize(width=self.width)
                    
                    # Center the image
                    img_clip = img_clip.set_position('center')
                    img_clip = img_clip.set_duration(duration_per_image)
                    
                    # Add subtle zoom effect
                    if i % 2 == 0:
                        # Zoom in
                        img_clip = img_clip.resize(lambda t: 1 + 0.1 * t / duration_per_image)
                    else:
                        # Zoom out
                        img_clip = img_clip.resize(lambda t: 1.1 - 0.1 * t / duration_per_image)
                    
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
            
            logger.info(f"Enhanced video created successfully: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error creating enhanced video: {e}")
            return None