"""
Video Creator Module for FlashVideoBot

Creates engaging videos with YouTube-style retention features including
dynamic text animations, transitions, effects, and optimized pacing.

Author: FlashVideoBot Team
Date: October 2025
"""

import os
import logging
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from moviepy.editor import *
from moviepy.video.fx import resize, fadein, fadeout
from moviepy.video.tools.drawing import color_gradient
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


class VideoCreator:
    """
    Creates engaging videos with dynamic effects, text animations,
    and YouTube-style retention optimization features.
    """
    
    def __init__(self, config):
        """
        Initialize the video creator with configuration.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.logger = logging.getLogger('FlashVideoBot.VideoCreator')
        
        # Video settings
        self.width = config.get('video.width', 1080)
        self.height = config.get('video.height', 1920)
        self.fps = config.get('video.fps', 30)
        self.duration = config.get('video.duration', 30)
        
        # Text settings
        self.font_size = config.get('video.text.font_size', 60)
        self.title_font_size = config.get('video.text.title_font_size', 80)
        self.font_color = config.get('video.text.font_color', '#FFFFFF')
        self.bg_color = config.get('video.text.bg_color', '#000000')
        self.stroke_color = config.get('video.text.stroke_color', '#FF0000')
        self.stroke_width = config.get('video.text.stroke_width', 2)
        
        # Transition settings
        self.fade_duration = config.get('video.transitions.fade_duration', 0.5)
        self.zoom_factor = config.get('video.transitions.zoom_factor', 1.2)
        self.slide_duration = config.get('video.transitions.slide_duration', 0.3)
        
        # Output settings
        self.output_dir = "videos"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load fonts
        self.fonts = self._load_fonts()
    
    def _load_fonts(self) -> Dict[str, str]:
        """Load available fonts for text rendering."""
        fonts = {}
        
        # Default system fonts
        default_fonts = {
            'bold': 'arial-bold.ttf',
            'regular': 'arial.ttf',
            'impact': 'impact.ttf'
        }
        
        # Check for custom fonts in assets/fonts
        font_dir = "assets/fonts"
        if os.path.exists(font_dir):
            for font_file in os.listdir(font_dir):
                if font_file.endswith(('.ttf', '.otf')):
                    font_name = os.path.splitext(font_file)[0]
                    fonts[font_name] = os.path.join(font_dir, font_file)
        
        # Add system fonts if available
        for name, font_file in default_fonts.items():
            if not fonts.get(name):
                fonts[name] = font_file
        
        return fonts
    
    async def create_video(self, article: Dict[str, Any], images: List[str], audio_path: Optional[str] = None) -> Optional[str]:
        """
        Create an engaging video for a news article.
        
        Args:
            article: Article data with title, summary, etc.
            images: List of image file paths
            audio_path: Path to audio narration file
            
        Returns:
            Path to created video file or None if failed
        """
        try:
            self.logger.info(f"Creating video for: {article.get('title', 'Untitled')}")
            
            # Generate timestamp for unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_filename = f"news_video_{timestamp}.mp4"
            video_path = os.path.join(self.output_dir, video_filename)
            
            # Create video segments
            segments = await self._create_video_segments(article, images, audio_path)
            
            if not segments:
                self.logger.error("No video segments created")
                return None
            
            # Combine segments into final video
            final_video = self._combine_segments(segments)
            
            # Add final effects and optimize for YouTube Shorts
            optimized_video = self._optimize_for_retention(final_video, article)
            
            # Write final video
            self.logger.info(f"Rendering video: {video_path}")
            optimized_video.write_videofile(
                video_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Cleanup
            optimized_video.close()
            for segment in segments:
                segment.close()
            
            self.logger.info(f"Video created successfully: {video_path}")
            return video_path
            
        except Exception as e:
            self.logger.error(f"Error creating video: {str(e)}")
            return None
    
    async def _create_video_segments(self, article: Dict[str, Any], images: List[str], audio_path: Optional[str]) -> List[VideoClip]:
        """
        Create individual video segments for different parts of the story.
        
        Args:
            article: Article data
            images: List of image paths
            audio_path: Path to audio file
            
        Returns:
            List of video segments
        """
        segments = []
        
        try:
            # Segment 1: Hook with dramatic effect (3-5 seconds)
            hook_segment = self._create_hook_segment(article, images[0] if images else None)
            segments.append(hook_segment)
            
            # Segment 2: Title reveal with animation (3-4 seconds)
            title_segment = self._create_title_segment(article, images[1] if len(images) > 1 else images[0] if images else None)
            segments.append(title_segment)
            
            # Segment 3: Main content with key points (15-20 seconds)
            content_segments = self._create_content_segments(article, images[2:] if len(images) > 2 else images)
            segments.extend(content_segments)
            
            # Segment 4: Call-to-action ending (2-3 seconds)
            cta_segment = self._create_cta_segment(article)
            segments.append(cta_segment)
            
            # Adjust durations to fit total duration
            total_duration = sum(segment.duration for segment in segments)
            if total_duration > self.duration:
                scale_factor = self.duration / total_duration
                for segment in segments:
                    segment = segment.set_duration(segment.duration * scale_factor)
            
            return segments
            
        except Exception as e:
            self.logger.error(f"Error creating video segments: {str(e)}")
            return []
    
    def _create_hook_segment(self, article: Dict[str, Any], image_path: Optional[str]) -> VideoClip:
        """
        Create an attention-grabbing hook segment.
        
        Args:
            article: Article data
            image_path: Background image path
            
        Returns:
            Hook video segment
        """
        duration = 4.0
        
        # Create background
        if image_path and os.path.exists(image_path):
            background = self._create_image_background(image_path, duration)
            # Add dramatic zoom effect
            background = background.resize(lambda t: 1 + 0.1 * t)  # Slow zoom
        else:
            background = self._create_color_background("#000000", duration)
        
        # Create dramatic text overlay
        hook_text = article.get('hook', '🚨 BREAKING NEWS 🚨')
        
        # Create pulsing text effect
        text_clip = self._create_animated_text(
            hook_text,
            duration=duration,
            font_size=self.title_font_size,
            color='red',
            animation='pulse',
            position='center'
        )
        
        # Add red flash effect at start
        flash = ColorClip(size=(self.width, self.height), color=(255, 0, 0))
        flash = flash.set_duration(0.2).set_opacity(0.3)
        
        # Combine elements
        segment = CompositeVideoClip([
            background,
            flash,
            text_clip
        ])
        
        return segment.set_duration(duration)
    
    def _create_title_segment(self, article: Dict[str, Any], image_path: Optional[str]) -> VideoClip:
        """
        Create title reveal segment with animation.
        
        Args:
            article: Article data
            image_path: Background image path
            
        Returns:
            Title video segment
        """
        duration = 4.0
        title = article.get('title', 'News Update')
        
        # Create background with blur effect
        if image_path and os.path.exists(image_path):
            background = self._create_image_background(image_path, duration, blur=True)
        else:
            background = self._create_gradient_background(duration)
        
        # Create typewriter text effect
        title_clip = self._create_animated_text(
            title,
            duration=duration,
            font_size=self.title_font_size,
            color='white',
            animation='typewriter',
            position='center',
            stroke_color='black',
            stroke_width=3
        )
        
        # Add source badge
        source = article.get('source', 'News')
        source_clip = self._create_source_badge(source, duration)
        
        # Combine elements
        segment = CompositeVideoClip([
            background,
            title_clip,
            source_clip
        ])
        
        return segment.set_duration(duration)
    
    def _create_content_segments(self, article: Dict[str, Any], images: List[str]) -> List[VideoClip]:
        """
        Create main content segments with key points.
        
        Args:
            article: Article data
            images: List of background images
            
        Returns:
            List of content segments
        """
        segments = []
        key_points = article.get('key_points', [])
        summary = article.get('summary', '')
        
        # If no key points, create from summary
        if not key_points and summary:
            sentences = summary.split('. ')
            key_points = [f"• {sentence.strip()}" for sentence in sentences[:3] if sentence.strip()]
        
        # Create segments for each key point
        segment_duration = 6.0
        for i, point in enumerate(key_points[:3]):  # Max 3 points
            image_path = images[i % len(images)] if images else None
            
            # Create background
            if image_path and os.path.exists(image_path):
                background = self._create_image_background(image_path, segment_duration)
                # Add ken burns effect (pan and zoom)
                background = self._add_ken_burns_effect(background)
            else:
                background = self._create_gradient_background(segment_duration, color_scheme='blue')
            
            # Create animated bullet point
            point_clip = self._create_animated_text(
                point,
                duration=segment_duration,
                font_size=self.font_size,
                color='white',
                animation='slide_left',
                position=('center', 'center'),
                stroke_color='black',
                stroke_width=2
            )
            
            # Add number indicator
            number_clip = self._create_number_indicator(i + 1, segment_duration)
            
            # Combine elements
            segment = CompositeVideoClip([
                background,
                point_clip,
                number_clip
            ])
            
            segments.append(segment.set_duration(segment_duration))
        
        return segments
    
    def _create_cta_segment(self, article: Dict[str, Any]) -> VideoClip:
        """
        Create call-to-action ending segment.
        
        Args:
            article: Article data
            
        Returns:
            CTA video segment
        """
        duration = 3.0
        
        # Create dynamic background
        background = self._create_gradient_background(duration, color_scheme='purple')
        
        # CTA text
        cta_texts = [
            "LIKE & SUBSCRIBE FOR MORE!",
            "FOLLOW FOR BREAKING NEWS!",
            "WHAT DO YOU THINK?",
            "SHARE YOUR THOUGHTS!"
        ]
        
        import random
        cta_text = random.choice(cta_texts)
        
        # Create bouncing text
        cta_clip = self._create_animated_text(
            cta_text,
            duration=duration,
            font_size=self.title_font_size,
            color='yellow',
            animation='bounce',
            position='center',
            stroke_color='black',
            stroke_width=3
        )
        
        # Add social media icons (if available)
        icons_clip = self._create_social_icons(duration)
        
        # Combine elements
        segment = CompositeVideoClip([
            background,
            cta_clip,
            icons_clip
        ])
        
        return segment.set_duration(duration)
    
    def _create_image_background(self, image_path: str, duration: float, blur: bool = False) -> VideoClip:
        """
        Create video background from image with effects.
        
        Args:
            image_path: Path to image file
            duration: Duration of clip
            blur: Whether to apply blur effect
            
        Returns:
            Background video clip
        """
        try:
            # Load and process image
            img = Image.open(image_path)
            
            # Resize to fit video dimensions while maintaining aspect ratio
            img_ratio = img.width / img.height
            video_ratio = self.width / self.height
            
            if img_ratio > video_ratio:
                # Image is wider, fit to height
                new_height = self.height
                new_width = int(new_height * img_ratio)
            else:
                # Image is taller, fit to width
                new_width = self.width
                new_height = int(new_width / img_ratio)
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Center crop to video dimensions
            left = (new_width - self.width) // 2
            top = (new_height - self.height) // 2
            img = img.crop((left, top, left + self.width, top + self.height))
            
            # Apply blur if requested
            if blur:
                img = img.filter(ImageFilter.GaussianBlur(radius=3))
            
            # Enhance image
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.8)  # Slightly darker for text readability
            
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)  # Increase contrast
            
            # Convert to numpy array and create video clip
            img_array = np.array(img)
            clip = ImageClip(img_array).set_duration(duration)
            
            return clip
            
        except Exception as e:
            self.logger.warning(f"Error creating image background: {str(e)}")
            return self._create_color_background("#000000", duration)
    
    def _create_color_background(self, color: str, duration: float) -> VideoClip:
        """
        Create solid color background.
        
        Args:
            color: Color hex string or name
            duration: Duration of clip
            
        Returns:
            Color background clip
        """
        if color.startswith('#'):
            # Convert hex to RGB
            hex_color = color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        else:
            rgb = (0, 0, 0)  # Default to black
        
        clip = ColorClip(size=(self.width, self.height), color=rgb)
        return clip.set_duration(duration)
    
    def _create_gradient_background(self, duration: float, color_scheme: str = 'red') -> VideoClip:
        """
        Create gradient background.
        
        Args:
            duration: Duration of clip
            color_scheme: Color scheme name
            
        Returns:
            Gradient background clip
        """
        # Define color schemes
        schemes = {
            'red': [(255, 0, 0), (0, 0, 0)],
            'blue': [(0, 100, 255), (0, 0, 50)],
            'purple': [(128, 0, 128), (0, 0, 0)],
            'green': [(0, 255, 0), (0, 50, 0)]
        }
        
        colors = schemes.get(color_scheme, schemes['red'])
        
        # Create gradient image
        gradient = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(gradient)
        
        for y in range(self.height):
            ratio = y / self.height
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        gradient_array = np.array(gradient)
        clip = ImageClip(gradient_array).set_duration(duration)
        
        return clip
    
    def _create_animated_text(self, text: str, duration: float, font_size: int, color: str, 
                             animation: str, position: Tuple, stroke_color: str = None, 
                             stroke_width: int = 0) -> VideoClip:
        """
        Create animated text clip with various effects.
        
        Args:
            text: Text content
            duration: Duration of animation
            font_size: Font size
            color: Text color
            animation: Animation type
            position: Text position
            stroke_color: Stroke color
            stroke_width: Stroke width
            
        Returns:
            Animated text clip
        """
        try:
            # Create text clip
            fontpath = self.fonts.get('bold', 'Arial-Bold')
            
            text_clip = TextClip(
                text,
                fontsize=font_size,
                font=fontpath,
                color=color,
                stroke_color=stroke_color,
                stroke_width=stroke_width
            ).set_duration(duration)
            
            # Apply animation
            if animation == 'typewriter':
                # Typewriter effect
                def typewriter_effect(get_frame, t):
                    chars_to_show = int(len(text) * t / duration)
                    partial_text = text[:chars_to_show]
                    if partial_text != text:
                        partial_clip = TextClip(
                            partial_text,
                            fontsize=font_size,
                            font=fontpath,
                            color=color,
                            stroke_color=stroke_color,
                            stroke_width=stroke_width
                        )
                        return partial_clip.get_frame(0)
                    return get_frame(t)
                
                text_clip = text_clip.fl(typewriter_effect)
            
            elif animation == 'pulse':
                # Pulsing scale effect
                text_clip = text_clip.resize(lambda t: 1 + 0.2 * np.sin(4 * np.pi * t))
            
            elif animation == 'slide_left':
                # Slide in from left
                text_clip = text_clip.set_position(lambda t: (max(-text_clip.w, -text_clip.w + (text_clip.w + self.width) * t / 2), position[1]))
            
            elif animation == 'bounce':
                # Bouncing effect
                text_clip = text_clip.set_position(lambda t: (position[0], position[1] + 20 * abs(np.sin(6 * np.pi * t))))
            
            # Set final position if not animated
            if animation not in ['slide_left', 'bounce']:
                text_clip = text_clip.set_position(position)
            
            return text_clip
            
        except Exception as e:
            self.logger.warning(f"Error creating animated text: {str(e)}")
            # Fallback to simple text
            return TextClip(text, fontsize=font_size, color=color).set_duration(duration).set_position(position)
    
    def _create_source_badge(self, source: str, duration: float) -> VideoClip:
        """
        Create source badge overlay.
        
        Args:
            source: Source name
            duration: Duration of clip
            
        Returns:
            Source badge clip
        """
        try:
            badge_text = f"📺 {source.upper()}"
            badge_clip = TextClip(
                badge_text,
                fontsize=30,
                color='white',
                bg_color='red',
                font=self.fonts.get('bold', 'Arial-Bold')
            ).set_duration(duration).set_position(('right', 'top')).set_margin(20)
            
            return badge_clip
            
        except Exception as e:
            self.logger.warning(f"Error creating source badge: {str(e)}")
            return ColorClip(size=(1, 1), color=(0, 0, 0), duration=duration)
    
    def _create_number_indicator(self, number: int, duration: float) -> VideoClip:
        """
        Create number indicator for key points.
        
        Args:
            number: Point number
            duration: Duration of clip
            
        Returns:
            Number indicator clip
        """
        try:
            circle_clip = TextClip(
                str(number),
                fontsize=40,
                color='white',
                bg_color='red',
                font=self.fonts.get('bold', 'Arial-Bold')
            ).set_duration(duration).set_position(('left', 'top')).set_margin(20)
            
            return circle_clip
            
        except Exception as e:
            self.logger.warning(f"Error creating number indicator: {str(e)}")
            return ColorClip(size=(1, 1), color=(0, 0, 0), duration=duration)
    
    def _create_social_icons(self, duration: float) -> VideoClip:
        """
        Create social media icons overlay.
        
        Args:
            duration: Duration of clip
            
        Returns:
            Social icons clip
        """
        try:
            icons_text = "👍 💬 🔔 📤"
            icons_clip = TextClip(
                icons_text,
                fontsize=40,
                color='white'
            ).set_duration(duration).set_position(('center', 'bottom')).set_margin(50)
            
            return icons_clip
            
        except Exception as e:
            self.logger.warning(f"Error creating social icons: {str(e)}")
            return ColorClip(size=(1, 1), color=(0, 0, 0), duration=duration)
    
    def _add_ken_burns_effect(self, clip: VideoClip) -> VideoClip:
        """
        Add Ken Burns effect (pan and zoom) to video clip.
        
        Args:
            clip: Input video clip
            
        Returns:
            Clip with Ken Burns effect
        """
        try:
            # Apply slow zoom and slight pan
            return clip.resize(lambda t: 1 + 0.05 * t).set_position(lambda t: (-10 * t, -5 * t))
        except Exception as e:
            self.logger.warning(f"Error adding Ken Burns effect: {str(e)}")
            return clip
    
    def _combine_segments(self, segments: List[VideoClip]) -> VideoClip:
        """
        Combine video segments with transitions.
        
        Args:
            segments: List of video segments
            
        Returns:
            Combined video clip
        """
        if not segments:
            return None
        
        if len(segments) == 1:
            return segments[0]
        
        # Add transitions between segments
        final_segments = []
        
        for i, segment in enumerate(segments):
            if i == 0:
                # First segment: fade in
                segment = segment.fadein(self.fade_duration)
            elif i == len(segments) - 1:
                # Last segment: fade out
                segment = segment.fadeout(self.fade_duration)
            else:
                # Middle segments: crossfade
                segment = segment.fadein(self.fade_duration / 2).fadeout(self.fade_duration / 2)
            
            final_segments.append(segment)
        
        # Concatenate with overlap for smooth transitions
        return concatenate_videoclips(final_segments, method='compose')
    
    def _optimize_for_retention(self, video: VideoClip, article: Dict[str, Any]) -> VideoClip:
        """
        Optimize video for YouTube retention with final effects.
        
        Args:
            video: Input video clip
            article: Article data
            
        Returns:
            Optimized video clip
        """
        try:
            # Add subtle vignette effect
            vignette = self._create_vignette_effect(video.duration)
            
            # Add progress bar at bottom
            progress_bar = self._create_progress_bar(video.duration)
            
            # Combine final effects
            final_video = CompositeVideoClip([
                video,
                vignette,
                progress_bar
            ])
            
            # Ensure exact duration
            final_video = final_video.set_duration(min(video.duration, self.duration))
            
            return final_video
            
        except Exception as e:
            self.logger.warning(f"Error optimizing video: {str(e)}")
            return video
    
    def _create_vignette_effect(self, duration: float) -> VideoClip:
        """
        Create subtle vignette effect.
        
        Args:
            duration: Duration of effect
            
        Returns:
            Vignette overlay clip
        """
        try:
            # Create vignette mask
            center_x, center_y = self.width // 2, self.height // 2
            Y, X = np.ogrid[:self.height, :self.width]
            
            # Distance from center
            distance = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
            max_distance = np.sqrt(center_x**2 + center_y**2)
            
            # Create vignette mask (darker at edges)
            vignette_mask = 1 - (distance / max_distance) * 0.3
            vignette_mask = np.clip(vignette_mask, 0.7, 1.0)
            
            # Convert to 3-channel image
            vignette_img = np.stack([vignette_mask] * 3, axis=-1)
            vignette_img = (vignette_img * 255).astype(np.uint8)
            
            # Create clip
            vignette_clip = ImageClip(vignette_img).set_duration(duration).set_opacity(0.3)
            
            return vignette_clip
            
        except Exception as e:
            self.logger.warning(f"Error creating vignette: {str(e)}")
            return ColorClip(size=(1, 1), color=(0, 0, 0), duration=duration)
    
    def _create_progress_bar(self, duration: float) -> VideoClip:
        """
        Create progress bar at bottom of video.
        
        Args:
            duration: Total video duration
            
        Returns:
            Progress bar clip
        """
        try:
            bar_height = 4
            bar_y = self.height - bar_height - 10
            
            def progress_frame(t):
                progress = t / duration
                progress_width = int(self.width * progress)
                
                # Create progress bar image
                bar_img = np.zeros((bar_height, self.width, 3), dtype=np.uint8)
                bar_img[:, :progress_width] = [255, 0, 0]  # Red progress
                
                return bar_img
            
            progress_clip = VideoClip(progress_frame, duration=duration)
            progress_clip = progress_clip.set_position((0, bar_y))
            
            return progress_clip
            
        except Exception as e:
            self.logger.warning(f"Error creating progress bar: {str(e)}")
            return ColorClip(size=(1, 1), color=(0, 0, 0), duration=duration)