"""
News Fetcher Module for FlashVideoBot

Handles fetching news from multiple sources including NewsAPI and RSS feeds.
Implements caching, error handling, and content filtering for optimal results.

Author: FlashVideoBot Team
Date: October 2025
"""

import asyncio
import aiohttp
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import hashlib
import json
import os
from urllib.parse import urlparse


class NewsFetcher:
    """
    Fetches news articles from multiple sources including NewsAPI and RSS feeds.
    Implements intelligent filtering and caching for optimal performance.
    """
    
    def __init__(self, config):
        """
        Initialize the news fetcher with configuration.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.logger = logging.getLogger('FlashVideoBot.NewsFetcher')
        
        # API keys and settings
        self.newsapi_key = config.get('news.newsapi_key')
        self.rss_feeds = config.get('news.rss_feeds', [])
        self.categories = config.get('news.categories', ['general'])
        self.max_articles = config.get('news.max_articles', 5)
        
        # Cache settings
        self.cache_dir = "assets/temp/news_cache"
        self.cache_duration = config.get('performance.cache_duration_hours', 1)
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Request session for better performance
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FlashVideoBot/1.0 (News Video Generator)'
        })
    
    async def fetch_latest_news(self) -> List[Dict[str, Any]]:
        """
        Fetch latest news from all configured sources.
        
        Returns:
            List of news articles with standardized format
        """
        all_articles = []
        
        try:
            # Fetch from NewsAPI if key is available
            if self.newsapi_key and self.newsapi_key != "YOUR_NEWSAPI_KEY_HERE":
                newsapi_articles = await self._fetch_from_newsapi()
                all_articles.extend(newsapi_articles)
                self.logger.info(f"Fetched {len(newsapi_articles)} articles from NewsAPI")
            
            # Fetch from RSS feeds
            rss_articles = await self._fetch_from_rss()
            all_articles.extend(rss_articles)
            self.logger.info(f"Fetched {len(rss_articles)} articles from RSS feeds")
            
            # Remove duplicates and filter
            unique_articles = self._remove_duplicates(all_articles)
            filtered_articles = self._filter_articles(unique_articles)
            
            # Sort by publication date (newest first)
            sorted_articles = sorted(
                filtered_articles,
                key=lambda x: x.get('published_at', datetime.min),
                reverse=True
            )
            
            # Limit to max articles
            final_articles = sorted_articles[:self.max_articles]
            
            self.logger.info(f"Final selection: {len(final_articles)} articles")
            return final_articles
            
        except Exception as e:
            self.logger.error(f"Error fetching news: {str(e)}")
            return []
    
    async def _fetch_from_newsapi(self) -> List[Dict[str, Any]]:
        """
        Fetch news from NewsAPI.
        
        Returns:
            List of articles from NewsAPI
        """
        articles = []
        
        try:
            # Check cache first
            cache_key = f"newsapi_{hashlib.md5('_'.join(self.categories).encode()).hexdigest()}"
            cached_articles = self._get_cached_articles(cache_key)
            if cached_articles:
                return cached_articles
            
            # Fetch from NewsAPI for each category
            for category in self.categories:
                try:
                    url = "https://newsapi.org/v2/top-headlines"
                    params = {
                        'apiKey': self.newsapi_key,
                        'category': category,
                        'language': 'en',
                        'sortBy': 'publishedAt',
                        'pageSize': 20
                    }
                    
                    response = self.session.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    
                    data = response.json()
                    if data.get('status') == 'ok':
                        for article in data.get('articles', []):
                            if article.get('title') and article.get('description'):
                                standardized_article = self._standardize_newsapi_article(article)
                                articles.append(standardized_article)
                    
                    # Rate limiting - wait between requests
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    self.logger.warning(f"Error fetching NewsAPI category {category}: {str(e)}")
                    continue
            
            # Cache the results
            self._cache_articles(cache_key, articles)
            
        except Exception as e:
            self.logger.error(f"Error in NewsAPI fetch: {str(e)}")
        
        return articles
    
    async def _fetch_from_rss(self) -> List[Dict[str, Any]]:
        """
        Fetch news from RSS feeds.
        
        Returns:
            List of articles from RSS feeds
        """
        articles = []
        
        async def fetch_single_feed(feed_url: str) -> List[Dict[str, Any]]:
            """Fetch articles from a single RSS feed."""
            try:
                # Check cache first
                cache_key = f"rss_{hashlib.md5(feed_url.encode()).hexdigest()}"
                cached_articles = self._get_cached_articles(cache_key)
                if cached_articles:
                    return cached_articles
                
                # Fetch RSS feed
                feed = feedparser.parse(feed_url)
                feed_articles = []
                
                if feed.bozo == 0 or len(feed.entries) > 0:  # Valid feed or has entries
                    for entry in feed.entries[:10]:  # Limit per feed
                        if hasattr(entry, 'title') and hasattr(entry, 'summary'):
                            standardized_article = self._standardize_rss_article(entry, feed_url)
                            feed_articles.append(standardized_article)
                
                # Cache the results
                self._cache_articles(cache_key, feed_articles)
                return feed_articles
                
            except Exception as e:
                self.logger.warning(f"Error fetching RSS feed {feed_url}: {str(e)}")
                return []
        
        # Fetch all RSS feeds concurrently
        if self.rss_feeds:
            tasks = [fetch_single_feed(feed_url) for feed_url in self.rss_feeds]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    articles.extend(result)
        
        return articles
    
    def _standardize_newsapi_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize NewsAPI article format.
        
        Args:
            article: Raw NewsAPI article
            
        Returns:
            Standardized article dictionary
        """
        return {
            'title': article.get('title', '').strip(),
            'description': article.get('description', '').strip(),
            'content': article.get('content', '').strip(),
            'url': article.get('url', ''),
            'url_to_image': article.get('urlToImage'),
            'published_at': self._parse_date(article.get('publishedAt')),
            'source': article.get('source', {}).get('name', 'Unknown'),
            'author': article.get('author', 'Unknown'),
            'category': 'general',
            'language': 'en',
            'source_type': 'newsapi'
        }
    
    def _standardize_rss_article(self, entry: Any, feed_url: str) -> Dict[str, Any]:
        """
        Standardize RSS article format.
        
        Args:
            entry: RSS feed entry
            feed_url: RSS feed URL
            
        Returns:
            Standardized article dictionary
        """
        # Extract content with fallback
        content = ""
        if hasattr(entry, 'content'):
            content = entry.content[0].value if entry.content else ""
        elif hasattr(entry, 'description'):
            content = entry.description
        elif hasattr(entry, 'summary'):
            content = entry.summary
        
        # Clean HTML content
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text().strip()
        
        # Extract image URL
        image_url = None
        if hasattr(entry, 'media_content'):
            image_url = entry.media_content[0].get('url') if entry.media_content else None
        elif hasattr(entry, 'enclosures'):
            for enclosure in entry.enclosures:
                if enclosure.type.startswith('image/'):
                    image_url = enclosure.href
                    break
        
        # Extract source name from feed URL
        parsed_url = urlparse(feed_url)
        source_name = parsed_url.netloc.replace('www.', '').split('.')[0].title()
        
        return {
            'title': entry.title.strip() if hasattr(entry, 'title') else '',
            'description': entry.summary.strip() if hasattr(entry, 'summary') else '',
            'content': content,
            'url': entry.link if hasattr(entry, 'link') else '',
            'url_to_image': image_url,
            'published_at': self._parse_date(entry.published if hasattr(entry, 'published') else None),
            'source': source_name,
            'author': entry.author if hasattr(entry, 'author') else 'Unknown',
            'category': 'general',
            'language': 'en',
            'source_type': 'rss'
        }
    
    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """
        Parse date string to datetime object.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Parsed datetime object
        """
        if not date_str:
            return datetime.now()
        
        try:
            # Try different date formats
            formats = [
                '%Y-%m-%dT%H:%M:%SZ',           # ISO format
                '%Y-%m-%dT%H:%M:%S.%fZ',        # ISO with microseconds
                '%a, %d %b %Y %H:%M:%S %Z',     # RSS format
                '%a, %d %b %Y %H:%M:%S %z',     # RSS with timezone
                '%Y-%m-%d %H:%M:%S',            # Simple format
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If all formats fail, try feedparser's parsing
            import time
            parsed_time = feedparser._parse_date(date_str)
            if parsed_time:
                return datetime.fromtimestamp(time.mktime(parsed_time))
                
        except Exception:
            pass
        
        # Return current time if parsing fails
        return datetime.now()
    
    def _remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate articles based on title similarity.
        
        Args:
            articles: List of articles
            
        Returns:
            List with duplicates removed
        """
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            title = article.get('title', '').lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)
        
        return unique_articles
    
    def _filter_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter articles based on quality criteria.
        
        Args:
            articles: List of articles
            
        Returns:
            Filtered articles
        """
        filtered = []
        
        for article in articles:
            # Check minimum content requirements
            title = article.get('title', '')
            description = article.get('description', '')
            
            if len(title) < 10 or len(description) < 20:
                continue
            
            # Filter out unwanted content
            skip_keywords = ['[removed]', 'subscribe', 'sign up', 'paywall']
            if any(keyword in description.lower() for keyword in skip_keywords):
                continue
            
            # Check recency (articles from last 24 hours preferred)
            published_at = article.get('published_at', datetime.min)
            if isinstance(published_at, datetime):
                age_hours = (datetime.now() - published_at).total_seconds() / 3600
                if age_hours > 48:  # Skip articles older than 48 hours
                    continue
            
            filtered.append(article)
        
        return filtered
    
    def _get_cached_articles(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Get articles from cache if still valid."""
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            if os.path.exists(cache_file):
                # Check if cache is still valid
                cache_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
                if cache_age.total_seconds() < self.cache_duration * 3600:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
        except Exception as e:
            self.logger.debug(f"Error reading cache: {str(e)}")
        return None
    
    def _cache_articles(self, cache_key: str, articles: List[Dict[str, Any]]):
        """Cache articles to disk."""
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            
            # Convert datetime objects to strings for JSON serialization
            serializable_articles = []
            for article in articles:
                serializable_article = article.copy()
                if isinstance(serializable_article.get('published_at'), datetime):
                    serializable_article['published_at'] = serializable_article['published_at'].isoformat()
                serializable_articles.append(serializable_article)
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_articles, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.debug(f"Error caching articles: {str(e)}")
    
    def get_trending_keywords(self, articles: List[Dict[str, Any]]) -> List[str]:
        """
        Extract trending keywords from articles for better image search.
        
        Args:
            articles: List of articles
            
        Returns:
            List of trending keywords
        """
        from collections import Counter
        import re
        
        all_text = ""
        for article in articles:
            all_text += f" {article.get('title', '')} {article.get('description', '')}"
        
        # Extract meaningful words (excluding common stop words)
        words = re.findall(r'\b[A-Za-z]{4,}\b', all_text.lower())
        stop_words = {'that', 'with', 'have', 'this', 'will', 'from', 'they', 'been', 'said', 'each', 'which', 'their', 'time', 'year'}
        meaningful_words = [word for word in words if word not in stop_words]
        
        # Get most common words
        word_counts = Counter(meaningful_words)
        trending_keywords = [word for word, count in word_counts.most_common(10)]
        
        return trending_keywords