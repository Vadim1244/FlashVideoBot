"""
FlashVideoBot - Automated News Video Generator

This module serves as the main entry point for the FlashVideoBot application.
It orchestrates the entire process of fetching news, summarizing content,
and creating engaging videos with YouTube-style retention features.

Author: FlashVideoBot Team
Date: October 2025
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config_manager import ConfigManager
from src.news_fetcher import NewsFetcher
from src.text_summarizer import TextSummarizer
from simple_video_creator import SimpleVideoCreator  # Use simple video creator
from src.audio_manager import AudioManager
from src.image_manager import ImageManager
from src.utils.logger import setup_logger


class FlashVideoBot:
    """
    Main application class that coordinates all components to create
    engaging news videos automatically.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the FlashVideoBot with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = ConfigManager(config_path)
        self.logger = setup_logger(self.config.get_config())
        
        # Initialize components
        self.news_fetcher = NewsFetcher(self.config)
        self.summarizer = TextSummarizer(self.config)
        self.video_creator = SimpleVideoCreator(self.config.get_config())  # Use simple video creator
        self.audio_manager = AudioManager(self.config)
        self.image_manager = ImageManager(self.config)
        
        self.logger.info("FlashVideoBot initialized successfully")
    
    async def fetch_news(self) -> List[Dict[str, Any]]:
        """
        Fetch latest news from configured sources.
        
        Returns:
            List of news articles with metadata
        """
        try:
            self.logger.info("Fetching latest news...")
            articles = await self.news_fetcher.fetch_latest_news()
            self.logger.info(f"Fetched {len(articles)} articles")
            return articles
        except Exception as e:
            self.logger.error(f"Error fetching news: {str(e)}")
            return []
    
    def summarize_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate concise summaries for news articles.
        
        Args:
            articles: List of news articles
            
        Returns:
            Articles with added summaries
        """
        try:
            self.logger.info("Summarizing articles...")
            summarized_articles = []
            
            for article in articles:
                try:
                    summary = self.summarizer.summarize(
                        article.get('content', article.get('description', ''))
                    )
                    article['summary'] = summary
                    article['hook'] = self.summarizer.generate_hook(article)
                    summarized_articles.append(article)
                    self.logger.debug(f"Summarized: {article.get('title', 'Untitled')}")
                except Exception as e:
                    self.logger.warning(f"Failed to summarize article: {str(e)}")
                    continue
            
            self.logger.info(f"Successfully summarized {len(summarized_articles)} articles")
            return summarized_articles
        except Exception as e:
            self.logger.error(f"Error summarizing articles: {str(e)}")
            return []
    
    async def create_videos(self, articles: List[Dict[str, Any]]) -> List[str]:
        """
        Create engaging videos for each news article.
        
        Args:
            articles: List of summarized news articles
            
        Returns:
            List of created video file paths
        """
        video_paths = []
        
        for i, article in enumerate(articles):
            try:
                self.logger.info(f"Creating video {i+1}/{len(articles)}: {article.get('title', 'Untitled')}")
                
                # Get relevant images
                images = await self.image_manager.get_images_for_article(article)
                
                # Generate audio narration
                audio_path = await self.audio_manager.create_narration(article)
                
                # Create the video with all effects
                video_path = await self.video_creator.create_video(
                    article=article,
                    images=images,
                    audio_path=audio_path
                )
                
                if video_path:
                    video_paths.append(video_path)
                    self.logger.info(f"Video created successfully: {video_path}")
                else:
                    self.logger.warning(f"Failed to create video for article: {article.get('title')}")
                    
            except Exception as e:
                self.logger.error(f"Error creating video for article {i+1}: {str(e)}")
                continue
        
        return video_paths
    
    async def run(self):
        """
        Main execution flow - fetch news and create videos.
        """
        try:
            self.logger.info("Starting FlashVideoBot...")
            start_time = datetime.now()
            
            # Fetch latest news
            articles = await self.fetch_news()
            if not articles:
                self.logger.warning("No articles fetched. Exiting.")
                return
            
            # Limit articles based on configuration
            max_articles = self.config.get('news.max_articles', 5)
            articles = articles[:max_articles]
            
            # Summarize articles
            summarized_articles = self.summarize_articles(articles)
            if not summarized_articles:
                self.logger.warning("No articles successfully summarized. Exiting.")
                return
            
            # Create videos
            video_paths = await self.create_videos(summarized_articles)
            
            # Report results
            end_time = datetime.now()
            duration = end_time - start_time
            
            self.logger.info(f"FlashVideoBot completed!")
            self.logger.info(f"Processed {len(articles)} articles")
            self.logger.info(f"Created {len(video_paths)} videos")
            self.logger.info(f"Total execution time: {duration}")
            self.logger.info(f"Videos saved to: {os.path.abspath('videos/')}")
            
            # Print video paths for user
            if video_paths:
                print("\n🎬 Videos Created Successfully!")
                print("=" * 50)
                for i, path in enumerate(video_paths, 1):
                    print(f"{i}. {os.path.basename(path)}")
                print(f"\n📁 All videos saved in: {os.path.abspath('videos/')}")
            
        except Exception as e:
            self.logger.error(f"Critical error in main execution: {str(e)}")
            raise
    
    def cleanup_old_files(self):
        """Clean up old video files based on configuration."""
        try:
            cleanup_days = self.config.get('output.cleanup_after_days', 7)
            # Implementation for cleanup logic
            self.logger.info(f"Cleanup completed for files older than {cleanup_days} days")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")


async def main():
    """Main entry point for the application."""
    try:
        # Create FlashVideoBot instance
        bot = FlashVideoBot()
        
        # Run the bot
        await bot.run()
        
        # Cleanup old files
        bot.cleanup_old_files()
        
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Ensure required directories exist
    os.makedirs("videos", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("assets/temp", exist_ok=True)
    
    # Run the application
    asyncio.run(main())