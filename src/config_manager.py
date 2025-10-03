"""
Configuration Manager for FlashVideoBot

Handles loading and accessing configuration settings from YAML files
with support for environment variable overrides and local configuration.

Author: FlashVideoBot Team
Date: October 2025
"""

import os
import yaml
from typing import Any, Dict, Optional
from dotenv import load_dotenv


class ConfigManager:
    """
    Manages configuration loading and access with support for
    environment variables and local overrides.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to the main configuration file
        """
        self.config_path = config_path
        self.config = {}
        
        # Load environment variables
        load_dotenv()
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file with local overrides."""
        try:
            # Load main config
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    self.config = yaml.safe_load(file) or {}
            
            # Load local config overrides
            local_config_path = self.config_path.replace('.yaml', '_local.yaml')
            if os.path.exists(local_config_path):
                with open(local_config_path, 'r', encoding='utf-8') as file:
                    local_config = yaml.safe_load(file) or {}
                    self._merge_configs(self.config, local_config)
            
            # Apply environment variable overrides
            self._apply_env_overrides()
            
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            print("Using default configuration...")
            self.config = self._get_default_config()
    
    def _merge_configs(self, base: Dict, override: Dict):
        """Recursively merge configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides to configuration."""
        env_mappings = {
            'NEWSAPI_KEY': 'news.newsapi_key',
            'UNSPLASH_ACCESS_KEY': 'images.unsplash_access_key',
            'PIXABAY_API_KEY': 'images.pixabay_api_key',
            'LOG_LEVEL': 'logging.level',
            'MAX_ARTICLES': 'news.max_articles',
            'VIDEO_DURATION': 'video.duration',
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self._set_nested_value(config_path, env_value)
    
    def _set_nested_value(self, path: str, value: Any):
        """Set a nested configuration value using dot notation."""
        keys = path.split('.')
        current = self.config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Convert string values to appropriate types
        if isinstance(value, str):
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '').isdigit():
                value = float(value)
        
        current[keys[-1]] = value
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            path: Configuration path (e.g., 'video.width')
            default: Default value if path doesn't exist
            
        Returns:
            Configuration value or default
        """
        try:
            keys = path.split('.')
            current = self.config
            
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return default
            
            return current
        except Exception:
            return default
    
    def get_config(self) -> Dict[str, Any]:
        """Get the complete configuration dictionary."""
        return self.config.copy()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when file loading fails."""
        return {
            'news': {
                'max_articles': 5,
                'categories': ['general', 'technology'],
                'rss_feeds': [
                    'https://feeds.bbci.co.uk/news/rss.xml',
                    'https://rss.cnn.com/rss/edition.rss'
                ]
            },
            'video': {
                'width': 1080,
                'height': 1920,
                'fps': 30,
                'duration': 30,
                'text': {
                    'font_size': 60,
                    'title_font_size': 80,
                    'font_color': '#FFFFFF',
                    'bg_color': '#000000'
                }
            },
            'audio': {
                'tts': {
                    'engine': 'gtts',
                    'language': 'en',
                    'speed': 1.2
                },
                'music': {
                    'enabled': False,
                    'volume': 0.3
                }
            },
            'logging': {
                'level': 'INFO',
                'log_to_file': True
            },
            'performance': {
                'max_workers': 2
            }
        }
    
    def validate_config(self) -> bool:
        """
        Validate that required configuration values are present.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        required_paths = [
            'video.width',
            'video.height',
            'video.fps',
            'news.max_articles'
        ]
        
        missing_configs = []
        for path in required_paths:
            if self.get(path) is None:
                missing_configs.append(path)
        
        if missing_configs:
            print(f"Missing required configuration: {', '.join(missing_configs)}")
            return False
        
        return True
    
    def get_api_keys(self) -> Dict[str, Optional[str]]:
        """
        Get all API keys for validation.
        
        Returns:
            Dictionary of API key names and values
        """
        return {
            'newsapi_key': self.get('news.newsapi_key'),
            'unsplash_access_key': self.get('images.unsplash_access_key'),
            'pixabay_api_key': self.get('images.pixabay_api_key')
        }
    
    def print_config_summary(self):
        """Print a summary of the current configuration."""
        print("\n📋 Configuration Summary")
        print("=" * 40)
        print(f"Max Articles: {self.get('news.max_articles')}")
        print(f"Video Duration: {self.get('video.duration')}s")
        print(f"Video Size: {self.get('video.width')}x{self.get('video.height')}")
        print(f"TTS Engine: {self.get('audio.tts.engine')}")
        print(f"Log Level: {self.get('logging.level')}")
        
        # Check API keys
        api_keys = self.get_api_keys()
        print(f"\n🔑 API Keys Status:")
        for key_name, key_value in api_keys.items():
            status = "✅ Configured" if key_value and key_value != f"YOUR_{key_name.upper()}_HERE" else "❌ Missing"
            print(f"  {key_name}: {status}")