#!/usr/bin/env python3
"""
Enhanced Simple Video Creator with fallback images and text overlays
"""

import os
import logging
import re
import numpy as np
import sys
from typing import Dict, List, Optional, Any

# Import moviepy components
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip, 
    concatenate_videoclips, ColorClip
)
    
import PIL
from PIL import Image, ImageDraw, ImageFont
import textwrap
import random
import nltk

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
                    # Make sure we have the absolute path
                    img_path = os.path.abspath(img) if not os.path.isabs(img) else img
                    
                    if os.path.exists(img_path):
                        # Skip solid color fallback images from image manager
                        if 'fallback_color_' in os.path.basename(img_path):
                            logger.info(f"Skipping solid color fallback: {img_path}")
                            continue
                        try:
                            # Try to open the image to verify it's valid
                            # Import PIL here to avoid the "referenced before assignment" issue
                            import PIL.Image
                            test_img = PIL.Image.open(img_path)
                            test_img.close()
                            valid_images.append(img_path)
                        except Exception as e:
                            logger.warning(f"Image file is corrupted or invalid: {img_path} - {e}")
                
                if not valid_images:
                    logger.info("All provided images are invalid or solid color fallbacks, creating text content instead")
                    images = self._create_fallback_images(article)
                else:
                    images = valid_images
            
            # Filter valid images
            valid_images = []
            for img in images:
                abs_path = os.path.abspath(img) if not os.path.isabs(img) else img
                if os.path.exists(abs_path):
                    valid_images.append(abs_path)
                else:
                    logger.warning(f"Image path does not exist: {abs_path}")
            
            if not valid_images:
                logger.error("No valid images available")
                return None
            
            # Create video clips from images
            video_clips = []
            duration_per_image = self.max_duration / len(valid_images)
            
            for i, image_path in enumerate(valid_images):
                try:
                    # Import needed modules within the try block
                    from moviepy.editor import ImageClip, ColorClip
                    import PIL.Image
                    
                    # First verify the image file
                    try:
                        # Ensure we have the absolute path
                        abs_image_path = os.path.abspath(image_path) if not os.path.isabs(image_path) else image_path
                        
                        # Import PIL here to avoid the "referenced before assignment" issue
                        import PIL.Image
                        pil_img = PIL.Image.open(abs_image_path)
                        pil_img.verify()  # Verify it's a valid image
                        pil_img.close()
                        
                        # Reopen the image after verify (which closes the file)
                        pil_img = PIL.Image.open(abs_image_path)
                        
                        # Create image clip - Import inside try block to avoid errors
                        from moviepy.editor import ImageClip
                        img_clip = ImageClip(abs_image_path)
                        
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
                        
                    except (IOError, SyntaxError) as e:
                        # Create a fallback color clip with text if image is invalid
                        logger.warning(f"Invalid image {image_path}, creating color clip instead: {e}")
                        
                        # Use a color from a list based on index
                        colors = [(30, 64, 175), (67, 56, 202), (15, 23, 42)]
                        bg_color = colors[i % len(colors)]
                        
                        # Create a color clip as fallback
                        img_clip = ColorClip((self.width, self.height), col=bg_color)
                        img_clip = img_clip.set_duration(duration_per_image)
                    
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
            if audio_path:
                try:
                    # First check if the WAV file exists
                    if os.path.exists(audio_path):
                        logger.info(f"Adding audio from WAV: {audio_path}")
                        audio_file_path = audio_path
                    # Then check if an MP3 version exists
                    elif os.path.exists(audio_path.replace('.wav', '.mp3')):
                        mp3_path = audio_path.replace('.wav', '.mp3')
                        logger.info(f"Using MP3 audio instead: {mp3_path}")
                        audio_file_path = mp3_path
                    # Also check for mp3 if we were given a wav path
                    elif audio_path.endswith('.mp3') and os.path.exists(audio_path.replace('.mp3', '.wav')):
                        wav_path = audio_path.replace('.mp3', '.wav')
                        logger.info(f"Using WAV audio instead: {wav_path}")
                        audio_file_path = wav_path
                    # Check if audio file exists in assets/temp/audio directory
                    elif not os.path.dirname(audio_path).endswith('audio'):
                        audio_temp_dir = os.path.join('assets', 'temp', 'audio')
                        audio_base = os.path.basename(audio_path)
                        temp_audio_path = os.path.join(audio_temp_dir, audio_base)
                        
                        if os.path.exists(temp_audio_path):
                            logger.info(f"Found audio in temp directory: {temp_audio_path}")
                            audio_file_path = temp_audio_path
                        elif os.path.exists(temp_audio_path.replace('.wav', '.mp3')):
                            mp3_path = temp_audio_path.replace('.wav', '.mp3')
                            logger.info(f"Found MP3 in temp directory: {mp3_path}")
                            audio_file_path = mp3_path
                        else:
                            # Fall through to the name pattern search
                            audio_file_path = None
                    # Finally check if there's any audio file in the temp directory with a similar name
                    else:
                        audio_dir = os.path.dirname(audio_path)
                        # Make sure audio_dir exists
                        if not os.path.exists(audio_dir):
                            audio_dir = os.path.join('assets', 'temp', 'audio')
                            
                        base_name = os.path.basename(audio_path).split('_')[0]
                        
                        # Look for any audio file with a similar name pattern
                        if os.path.exists(audio_dir):
                            potential_audio_files = [
                                os.path.join(audio_dir, f) for f in os.listdir(audio_dir)
                                if (f.startswith(base_name) or 'narration_' in f) and (f.endswith('.mp3') or f.endswith('.wav'))
                            ]
                        
                            if potential_audio_files:
                                # Use the most recent one
                                potential_audio_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                                audio_file_path = potential_audio_files[0]
                                logger.info(f"Found alternative audio file: {audio_file_path}")
                            else:
                                logger.warning(f"No audio files found in {audio_dir}")
                                audio_file_path = None
                        else:
                            logger.warning(f"Audio directory does not exist: {audio_dir}")
                            audio_file_path = None
                    
                    # If we found an audio file, add it to the video
                    if audio_file_path and os.path.exists(audio_file_path):
                        audio_clip = AudioFileClip(audio_file_path)
                        logger.info(f"Audio duration: {audio_clip.duration}, Video duration: {final_video.duration}")
                        
                        # Match audio duration to video
                        if audio_clip.duration > final_video.duration:
                            audio_clip = audio_clip.subclip(0, final_video.duration)
                        elif audio_clip.duration < final_video.duration:
                            final_video = final_video.subclip(0, audio_clip.duration)
                        
                        final_video = final_video.set_audio(audio_clip)
                        logger.info("Audio added successfully")
                    else:
                        logger.warning(f"No valid audio file found")
                        
                except Exception as e:
                    logger.error(f"Failed to add audio: {e}")
            else:
                logger.warning(f"No audio path provided")
            
            # Add captions using PIL instead of TextClip (no ImageMagick needed)
            try:
                # Use both title and summary for better captions
                title = article.get('title', '')
                summary = article.get('summary', '')
                caption_text = summary[:200] + '...' if len(summary) > 200 else summary

                if caption_text:
                    logger.info("Adding sentence-by-sentence captions using PIL method")

                    # Split text into sentences
                    import re
                    sentences = re.split(r'(?<=[.!?])\s+', caption_text.strip())
                    sentences = [s.strip() for s in sentences if s.strip()]

                    if sentences:
                        # Calculate timing for each sentence
                        total_duration = final_video.duration
                        sentence_duration = total_duration / len(sentences)

                        caption_clips = []

                        for i, sentence in enumerate(sentences):
                            try:
                                # Create caption for this sentence
                                caption_height = 200  # Taller for middle positioning
                                from PIL import Image, ImageDraw, ImageFont

                                # Create caption background with gradient
                                caption_bg = Image.new('RGBA', (self.width, caption_height), (0, 0, 0, 0))
                                draw = ImageDraw.Draw(caption_bg)

                                # Create semi-transparent black background
                                draw.rectangle([(0, 0), (self.width, caption_height)], fill=(0, 0, 0, 160))

                                # Try to load a font
                                try:
                                    font_paths = [
                                        "C:/Windows/Fonts/Arial.ttf",
                                        "C:/Windows/Fonts/arial.ttf",
                                        "C:/Windows/Fonts/calibri.ttf",
                                        "C:/Windows/Fonts/segoeui.ttf"
                                    ]

                                    font = None
                                    for font_path in font_paths:
                                        try:
                                            if os.path.exists(font_path):
                                                font = ImageFont.truetype(font_path, 36)  # Slightly larger font
                                                break
                                        except:
                                            pass

                                    if font is None:
                                        font = ImageFont.load_default()
                                except:
                                    font = ImageFont.load_default()

                                # Wrap sentence text to fit width
                                import textwrap
                                wrapped_text = textwrap.fill(sentence, width=40)  # Shorter lines for middle positioning

                                # Draw caption text
                                text_color = (255, 255, 255, 255)  # White

                                # Calculate text dimensions for centering
                                try:
                                    lines = wrapped_text.split('\n')
                                    line_height = 42
                                    text_height = len(lines) * line_height

                                    # Draw each line separately for better positioning
                                    for j, line in enumerate(lines):
                                        try:
                                            text_bbox = draw.textbbox((0, 0), line, font=font)
                                            text_width = text_bbox[2] - text_bbox[0]
                                            y_position = (caption_height - text_height) // 2 + (j * line_height)
                                            x_position = (self.width - text_width) // 2
                                            draw.text((x_position, y_position), line, font=font, fill=text_color)
                                        except:
                                            # Fallback positioning
                                            draw.text((50, 20 + j*line_height), line, font=font, fill=text_color)
                                except Exception as text_error:
                                    logger.warning(f"Error in text rendering: {text_error}")
                                    # Simple fallback
                                    draw.text((50, 50), wrapped_text, font=font, fill=text_color)

                                # Save the caption
                                caption_path = os.path.join(self.temp_dir, f"caption_{i}_{os.path.basename(output_file).split('.')[0]}.png")
                                caption_bg.save(caption_path)

                                # Create a clip from the caption image
                                from moviepy.editor import ImageClip
                                caption_clip = ImageClip(caption_path, transparent=True)

                                # Position in the middle of the screen
                                caption_clip = caption_clip.set_position('center')

                                # Set duration and start time for this sentence
                                start_time = i * sentence_duration
                                end_time = min((i + 1) * sentence_duration, total_duration)
                                caption_clip = caption_clip.set_start(start_time).set_duration(end_time - start_time)

                                caption_clips.append(caption_clip)
                                logger.info(f"Created caption {i+1}/{len(sentences)}: '{sentence[:30]}...'")

                            except Exception as e:
                                logger.error(f"Failed to create caption for sentence {i+1}: {e}")
                                continue

                        # Composite the video with all caption clips
                        if caption_clips:
                            final_video = CompositeVideoClip([final_video] + caption_clips)
                            logger.info(f"Added {len(caption_clips)} sentence captions to video")
                        else:
                            logger.warning("No caption clips were created successfully")
                    else:
                        logger.warning("No sentences found in caption text")
                else:
                    logger.info("No caption text available")
            except Exception as e:
                logger.error(f"Failed to add captions: {e}")
            
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