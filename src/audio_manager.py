"""
Audio Manager Module for FlashVideoBot

Handles text-to-speech generation, background music, and audio effects
for creating engaging video narration with natural pacing.

Author: FlashVideoBot Team
Date: October 2025
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import tempfile
import subprocess


class AudioManager:
    """
    Manages audio generation including text-to-speech, background music,
    and audio effects for engaging video content.
    """
    
    def __init__(self, config):
        """
        Initialize the audio manager with configuration.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.logger = logging.getLogger('FlashVideoBot.AudioManager')
        
        # TTS settings
        self.tts_engine = config.get('audio.tts.engine', 'gtts')
        self.tts_language = config.get('audio.tts.language', 'en')
        self.tts_speed = config.get('audio.tts.speed', 1.2)
        
        # Music settings
        self.music_enabled = config.get('audio.music.enabled', True)
        self.music_volume = config.get('audio.music.volume', 0.3)
        self.fade_in = config.get('audio.music.fade_in', 1.0)
        self.fade_out = config.get('audio.music.fade_out', 1.0)
        
        # Audio output settings
        self.temp_dir = "assets/temp/audio"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize TTS engines
        self.pyttsx3_engine = None
        self._init_pyttsx3()
    
    def _init_pyttsx3(self):
        """Initialize pyttsx3 engine if available."""
        try:
            import pyttsx3
            self.pyttsx3_engine = pyttsx3.init()
            
            # Configure voice settings
            voices = self.pyttsx3_engine.getProperty('voices')
            if voices:
                # Try to find a good English voice
                for voice in voices:
                    if 'english' in voice.name.lower() or 'en' in voice.id.lower():
                        self.pyttsx3_engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate
            rate = self.pyttsx3_engine.getProperty('rate')
            self.pyttsx3_engine.setProperty('rate', int(rate * self.tts_speed))
            
            self.logger.info("pyttsx3 TTS engine initialized")
            
        except Exception as e:
            self.logger.warning(f"Could not initialize pyttsx3: {str(e)}")
            self.pyttsx3_engine = None
    
    async def create_narration(self, article: Dict[str, Any]) -> Optional[str]:
        """
        Create audio narration for the article.
        
        Args:
            article: Article data with title, summary, etc.
            
        Returns:
            Path to generated audio file or None if failed
        """
        try:
            self.logger.info(f"Creating narration for: {article.get('title', 'Untitled')}")
            
            # Generate narration script
            script = self._generate_narration_script(article)
            
            if not script:
                self.logger.warning("No narration script generated")
                return None
            
            # Generate TTS audio
            audio_path = await self._generate_tts(script, article)
            
            if not audio_path:
                self.logger.warning("TTS generation failed")
                return None
            
            # Add background music if enabled
            if self.music_enabled:
                final_audio_path = await self._add_background_music(audio_path, article)
                if final_audio_path:
                    # Clean up intermediate file
                    try:
                        os.remove(audio_path)
                    except:
                        pass
                    return final_audio_path
            
            return audio_path
            
        except Exception as e:
            self.logger.error(f"Error creating narration: {str(e)}")
            return None
    
    def _generate_narration_script(self, article: Dict[str, Any]) -> str:
        """
        Generate narration script optimized for video pacing.
        
        Args:
            article: Article data
            
        Returns:
            Narration script text
        """
        try:
            title = article.get('title', '')
            summary = article.get('summary', '')
            hook = article.get('hook', '')
            
            # Build script with natural pacing
            script_parts = []
            
            # Hook (attention grabber)
            if hook:
                script_parts.append(self._add_dramatic_pause(hook))
            
            # Title announcement
            if title:
                script_parts.append(f"Here's what's happening. {title}")
                script_parts.append("[PAUSE]")
            
            # Main content with pacing
            if summary:
                # Break summary into digestible chunks
                sentences = summary.split('. ')
                for i, sentence in enumerate(sentences):
                    if sentence.strip():
                        script_parts.append(sentence.strip() + ".")
                        
                        # Add strategic pauses
                        if i < len(sentences) - 1:
                            script_parts.append("[SHORT_PAUSE]")
            
            # Call to action
            cta_options = [
                "What do you think about this?",
                "Let me know your thoughts in the comments.",
                "Make sure to follow for more breaking news.",
                "This story is developing. Stay tuned."
            ]
            
            import random
            script_parts.append("[PAUSE]")
            script_parts.append(random.choice(cta_options))
            
            return " ".join(script_parts)
            
        except Exception as e:
            self.logger.warning(f"Error generating script: {str(e)}")
            return article.get('summary', article.get('title', ''))
    
    def _add_dramatic_pause(self, text: str) -> str:
        """
        Add dramatic pauses to text for better impact.
        
        Args:
            text: Input text
            
        Returns:
            Text with pause markers
        """
        # Add pauses around dramatic words
        dramatic_words = ['breaking', 'urgent', 'shocking', 'major', 'huge', 'massive']
        
        for word in dramatic_words:
            if word in text.lower():
                text = text.replace(word, f"[PAUSE] {word} [SHORT_PAUSE]")
        
        return text
    
    async def _generate_tts(self, script: str, article: Dict[str, Any]) -> Optional[str]:
        """
        Generate text-to-speech audio from script.
        
        Args:
            script: Narration script
            article: Article data for context
            
        Returns:
            Path to generated audio file
        """
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"narration_{timestamp}.wav"
            audio_path = os.path.join(self.temp_dir, audio_filename)
            
            # Choose TTS engine
            if self.tts_engine == 'gtts':
                success = await self._generate_gtts(script, audio_path)
            elif self.tts_engine == 'pyttsx3':
                success = self._generate_pyttsx3(script, audio_path)
            else:
                self.logger.warning(f"Unknown TTS engine: {self.tts_engine}")
                success = await self._generate_gtts(script, audio_path)  # Fallback
            
            if success and os.path.exists(audio_path):
                # Process audio for better quality
                processed_path = await self._process_audio(audio_path, article)
                return processed_path or audio_path
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error generating TTS: {str(e)}")
            return None
    
    async def _generate_gtts(self, script: str, output_path: str) -> bool:
        """
        Generate TTS using Google Text-to-Speech.
        
        Args:
            script: Text to convert
            output_path: Output audio file path
            
        Returns:
            True if successful
        """
        try:
            from gtts import gTTS
            import io
            
            # Clean script for TTS
            clean_script = self._clean_script_for_tts(script)
            
            if not clean_script:
                return False
            
            # Generate TTS
            tts = gTTS(
                text=clean_script,
                lang=self.tts_language,
                slow=False
            )
            
            # Save to temporary file first
            temp_file = io.BytesIO()
            tts.write_to_fp(temp_file)
            temp_file.seek(0)
            
            # Convert to WAV format using ffmpeg if available
            try:
                # Save as MP3 first
                temp_mp3_path = output_path.replace('.wav', '.mp3')
                with open(temp_mp3_path, 'wb') as f:
                    f.write(temp_file.read())
                
                # Convert to WAV
                if self._convert_audio_format(temp_mp3_path, output_path):
                    os.remove(temp_mp3_path)
                    return True
                else:
                    # Keep MP3 if conversion fails
                    os.rename(temp_mp3_path, output_path.replace('.wav', '.mp3'))
                    return True
                    
            except Exception as e:
                self.logger.warning(f"Audio conversion failed: {str(e)}")
                # Save as MP3
                with open(output_path.replace('.wav', '.mp3'), 'wb') as f:
                    f.write(temp_file.read())
                return True
            
        except Exception as e:
            self.logger.error(f"gTTS generation failed: {str(e)}")
            return False
    
    def _generate_pyttsx3(self, script: str, output_path: str) -> bool:
        """
        Generate TTS using pyttsx3.
        
        Args:
            script: Text to convert
            output_path: Output audio file path
            
        Returns:
            True if successful
        """
        try:
            if not self.pyttsx3_engine:
                return False
            
            # Clean script
            clean_script = self._clean_script_for_tts(script)
            
            if not clean_script:
                return False
            
            # Generate TTS
            self.pyttsx3_engine.save_to_file(clean_script, output_path)
            self.pyttsx3_engine.runAndWait()
            
            return os.path.exists(output_path)
            
        except Exception as e:
            self.logger.error(f"pyttsx3 generation failed: {str(e)}")
            return False
    
    def _clean_script_for_tts(self, script: str) -> str:
        """
        Clean script for TTS processing.
        
        Args:
            script: Raw script text
            
        Returns:
            Cleaned script
        """
        # Remove pause markers and replace with actual pauses
        script = script.replace('[PAUSE]', '. ')
        script = script.replace('[SHORT_PAUSE]', ', ')
        script = script.replace('[LONG_PAUSE]', '... ')
        
        # Remove special characters that might cause issues
        script = script.replace('🚨', 'Breaking:')
        script = script.replace('📺', '')
        script = script.replace('👍', '')
        script = script.replace('💬', '')
        script = script.replace('🔔', '')
        script = script.replace('📤', '')
        
        # Clean up extra spaces
        script = ' '.join(script.split())
        
        return script.strip()
    
    async def _process_audio(self, audio_path: str, article: Dict[str, Any]) -> Optional[str]:
        """
        Process audio for better quality and pacing.
        
        Args:
            audio_path: Path to raw audio file
            article: Article data for context
            
        Returns:
            Path to processed audio file
        """
        try:
            # For now, return the original path
            # In the future, could add audio normalization, noise reduction, etc.
            return audio_path
            
        except Exception as e:
            self.logger.warning(f"Audio processing failed: {str(e)}")
            return audio_path
    
    async def _add_background_music(self, narration_path: str, article: Dict[str, Any]) -> Optional[str]:
        """
        Add background music to narration audio.
        
        Args:
            narration_path: Path to narration audio
            article: Article data for music selection
            
        Returns:
            Path to final audio with background music
        """
        try:
            # Select appropriate background music
            music_path = self._select_background_music(article)
            
            if not music_path or not os.path.exists(music_path):
                self.logger.info("No background music available")
                return narration_path
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"final_audio_{timestamp}.wav"
            output_path = os.path.join(self.temp_dir, output_filename)
            
            # Mix audio using ffmpeg if available
            if self._mix_audio_with_music(narration_path, music_path, output_path):
                return output_path
            else:
                # Fallback: return narration only
                return narration_path
            
        except Exception as e:
            self.logger.warning(f"Failed to add background music: {str(e)}")
            return narration_path
    
    def _select_background_music(self, article: Dict[str, Any]) -> Optional[str]:
        """
        Select appropriate background music based on article content.
        
        Args:
            article: Article data
            
        Returns:
            Path to selected music file
        """
        try:
            music_dir = "assets/music"
            if not os.path.exists(music_dir):
                return None
            
            # Get available music files
            music_files = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.wav', '.m4a'))]
            
            if not music_files:
                return None
            
            # Simple selection based on sentiment
            sentiment = article.get('sentiment', 'neutral')
            
            # Define music preferences by sentiment
            music_preferences = {
                'positive': ['upbeat', 'happy', 'energetic', 'positive'],
                'negative': ['serious', 'dramatic', 'news', 'tension'],
                'neutral': ['background', 'ambient', 'news', 'generic']
            }
            
            preferred_keywords = music_preferences.get(sentiment, music_preferences['neutral'])
            
            # Find matching music file
            for keyword in preferred_keywords:
                for music_file in music_files:
                    if keyword.lower() in music_file.lower():
                        return os.path.join(music_dir, music_file)
            
            # Fallback: return first available file
            return os.path.join(music_dir, music_files[0])
            
        except Exception as e:
            self.logger.warning(f"Error selecting background music: {str(e)}")
            return None
    
    def _convert_audio_format(self, input_path: str, output_path: str) -> bool:
        """
        Convert audio format using ffmpeg.
        
        Args:
            input_path: Input audio file path
            output_path: Output audio file path
            
        Returns:
            True if successful
        """
        try:
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-acodec', 'pcm_s16le',
                '-ar', '44100',
                '-ac', '2',
                '-y',  # Overwrite output
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            self.logger.debug(f"ffmpeg conversion failed: {str(e)}")
            return False
    
    def _mix_audio_with_music(self, narration_path: str, music_path: str, output_path: str) -> bool:
        """
        Mix narration with background music using ffmpeg.
        
        Args:
            narration_path: Path to narration audio
            music_path: Path to background music
            output_path: Path for mixed output
            
        Returns:
            True if successful
        """
        try:
            # Use ffmpeg to mix audio
            cmd = [
                'ffmpeg',
                '-i', narration_path,
                '-i', music_path,
                '-filter_complex',
                f'[1:a]volume={self.music_volume}[music];[0:a][music]amix=inputs=2:duration=first',
                '-acodec', 'pcm_s16le',
                '-ar', '44100',
                '-ac', '2',
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0 and os.path.exists(output_path)
            
        except Exception as e:
            self.logger.debug(f"Audio mixing failed: {str(e)}")
            return False
    
    def cleanup_temp_files(self):
        """Clean up temporary audio files."""
        try:
            for filename in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, filename)
                try:
                    os.remove(file_path)
                except Exception:
                    pass
            self.logger.info("Audio temp files cleaned up")
        except Exception as e:
            self.logger.warning(f"Error cleaning up audio temp files: {str(e)}")
    
    def get_audio_duration(self, audio_path: str) -> float:
        """
        Get duration of audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Duration in seconds
        """
        try:
            cmd = [
                'ffprobe',
                '-i', audio_path,
                '-show_entries', 'format=duration',
                '-v', 'quiet',
                '-of', 'csv=p=0'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return float(result.stdout.strip())
            
        except Exception as e:
            self.logger.debug(f"Could not get audio duration: {str(e)}")
        
        return 30.0  # Default fallback duration