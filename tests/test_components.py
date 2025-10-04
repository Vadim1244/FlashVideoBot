#!/usr/bin/env python3
"""
Unit tests for FlashVideoBot components
"""

import os
import sys
import unittest
import asyncio
from unittest.mock import Mock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components
from src.config_manager import ConfigManager
from src.audio_manager import AudioManager


class TestConfigManager(unittest.TestCase):
    """Test the ConfigManager class"""
    
    def test_load_config(self):
        """Test that config can be loaded from example file"""
        config_mgr = ConfigManager(config_path="config/config.example.yaml")
        config = config_mgr.get_config()
        
        self.assertIsNotNone(config)
        self.assertIn('news', config)
        self.assertIn('video', config)


class TestAudioManager(unittest.TestCase):
    """Test the AudioManager class"""
    
    @patch('src.audio_manager.pyttsx3')
    @patch('src.audio_manager.gTTS')
    async def test_create_narration(self, mock_gtts, mock_pyttsx3):
        """Test that narration can be created"""
        # Setup mocks
        mock_gtts_instance = Mock()
        mock_gtts.return_value = mock_gtts_instance
        mock_gtts_instance.save = Mock()
        
        # Create test article
        article = {
            'title': 'Test Article',
            'summary': 'This is a test summary',
            'content': 'This is test content for the article',
            'published_date': '2025-10-05'
        }
        
        # Create config with test settings
        config = {
            'audio': {
                'tts': {
                    'engine': 'gtts',
                    'voice': 'en-us'
                }
            }
        }
        
        # Create AudioManager instance
        audio_mgr = AudioManager(config)
        
        # Call the method with test data
        result = await audio_mgr.create_narration(article)
        
        # Verify results
        self.assertIsNotNone(result)
        mock_gtts_instance.save.assert_called()


if __name__ == '__main__':
    unittest.main()