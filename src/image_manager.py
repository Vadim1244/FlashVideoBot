"""
Image Manager Module for FlashVideoBot

Handles fetching and processing relevant images from various sources
including Unsplash, Pixabay, and local assets for video backgrounds.

Author: FlashVideoBot Team
Date: October 2025
"""

import os
import logging
import asyncio
import aiohttp
import hashlib
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse
import requests
from PIL import Image, ImageEnhance, ImageFilter
import re


class ImageManager:
    """
    Manages image fetching, processing, and caching for video backgrounds.
    Supports multiple image sources with intelligent keyword extraction.
    """
    
    def __init__(self, config):
        """
        Initialize the image manager with configuration.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.logger = logging.getLogger('FlashVideoBot.ImageManager')
        
        # API keys
        self.unsplash_key = config.get('images.unsplash_access_key')
        self.pixabay_key = config.get('images.pixabay_api_key')
        
        # Cache settings
        self.cache_enabled = config.get('performance.cache_images', True)
        self.cache_duration = config.get('performance.cache_duration_hours', 24)
        self.cache_dir = "assets/temp/image_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Image processing settings
        self.target_width = config.get('video.width', 1080)
        self.target_height = config.get('video.height', 1920)
        self.min_image_size = (800, 600)
        
        # Fallback keywords
        self.fallback_keywords = config.get('images.fallback_keywords', [
            'news', 'breaking news', 'media', 'journalism', 'newspaper'
        ])
        
        # Request session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FlashVideoBot/1.0 (News Video Generator)'
        })
    
    async def get_images_for_article(self, article: Dict[str, Any], count: int = 3) -> List[str]:
        """
        Get relevant images for a news article.
        
        Args:
            article: Article data with title, description, etc.
            count: Number of images to fetch
            
        Returns:
            List of local image file paths
        """
        try:
            self.logger.info(f"Fetching {count} images for article: {article.get('title', 'Untitled')}")
            
            # Extract keywords from article
            keywords = self._extract_keywords(article)
            
            # Try to get images from article URL first
            article_images = []
            if article.get('url_to_image'):
                article_image = await self._download_image_from_url(article['url_to_image'], 'article_image')
                if article_image:
                    article_images.append(article_image)
            
            # Get additional images from external sources
            external_images = await self._fetch_external_images(keywords, count - len(article_images))
            
            # Combine all images
            all_images = article_images + external_images
            
            # Process images for video use
            processed_images = []
            for image_path in all_images:
                if os.path.exists(image_path):
                    processed_path = await self._process_image_for_video(image_path)
                    if processed_path:
                        processed_images.append(processed_path)
            
            # Ensure we have enough images
            while len(processed_images) < count:
                # Use fallback images
                fallback_image = await self._get_fallback_image(len(processed_images))
                if fallback_image:
                    processed_images.append(fallback_image)
                else:
                    break
            
            self.logger.info(f"Retrieved {len(processed_images)} images for video")
            return processed_images[:count]
            
        except Exception as e:
            self.logger.error(f"Error getting images for article: {str(e)}")
            return await self._get_fallback_images(count)
    
    def _extract_keywords(self, article: Dict[str, Any]) -> List[str]:
        """
        Extract relevant keywords from article for image search.
        
        Args:
            article: Article data
            
        Returns:
            List of search keywords
        """
        try:
            # Combine title and description
            text = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}"
            
            # Clean text
            text = re.sub(r'[^\w\s]', ' ', text)
            text = text.lower()
            
            # Extract meaningful words
            words = text.split()
            
            # Remove common stop words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
                'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does',
                'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that',
                'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
                'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'said', 'says'
            }
            
            # Filter meaningful words
            meaningful_words = [
                word for word in words 
                if len(word) > 3 and word not in stop_words and word.isalpha()
            ]
            
            # Get most frequent words
            from collections import Counter
            word_counts = Counter(meaningful_words)
            
            # Extract top keywords
            keywords = [word for word, count in word_counts.most_common(10)]
            
            # Add category-specific keywords
            category = article.get('category', 'general')
            if category == 'technology':
                keywords.extend(['technology', 'computer', 'digital', 'innovation'])
            elif category == 'business':
                keywords.extend(['business', 'finance', 'economy', 'market'])
            elif category == 'health':
                keywords.extend(['health', 'medical', 'hospital', 'medicine'])
            elif category == 'sports':
                keywords.extend(['sports', 'athlete', 'game', 'competition'])
            
            # Add general news keywords
            keywords.extend(['news', 'breaking', 'update', 'report'])
            
            # Remove duplicates and return
            return list(dict.fromkeys(keywords))[:5]  # Top 5 unique keywords
            
        except Exception as e:
            self.logger.warning(f"Error extracting keywords: {str(e)}")
            return self.fallback_keywords
    
    async def _fetch_external_images(self, keywords: List[str], count: int) -> List[str]:
        """
        Fetch images from external sources.
        
        Args:
            keywords: Search keywords
            count: Number of images to fetch
            
        Returns:
            List of downloaded image paths
        """
        images = []
        
        try:
            # Try different keyword combinations
            search_terms = []
            
            # Individual keywords
            search_terms.extend(keywords[:3])
            
            # Keyword combinations
            if len(keywords) >= 2:
                search_terms.append(f"{keywords[0]} {keywords[1]}")
            
            # Fallback terms
            search_terms.extend(self.fallback_keywords)
            
            for term in search_terms:
                if len(images) >= count:
                    break
                
                # Try Unsplash first
                if self.unsplash_key and self.unsplash_key != "YOUR_UNSPLASH_KEY_HERE":
                    unsplash_images = await self._fetch_from_unsplash(term, min(2, count - len(images)))
                    images.extend(unsplash_images)
                
                if len(images) >= count:
                    break
                
                # Try Pixabay
                if self.pixabay_key and self.pixabay_key != "YOUR_PIXABAY_KEY_HERE":
                    pixabay_images = await self._fetch_from_pixabay(term, min(2, count - len(images)))
                    images.extend(pixabay_images)
                
                if len(images) >= count:
                    break
            
            return images[:count]
            
        except Exception as e:
            self.logger.error(f"Error fetching external images: {str(e)}")
            return []
    
    async def _fetch_from_unsplash(self, query: str, count: int) -> List[str]:
        """
        Fetch images from Unsplash API.
        
        Args:
            query: Search query
            count: Number of images to fetch
            
        Returns:
            List of downloaded image paths
        """
        try:
            # Check cache first
            cache_key = f"unsplash_{hashlib.md5(query.encode()).hexdigest()}"
            cached_urls = self._get_cached_urls(cache_key)
            
            if not cached_urls:
                # Fetch from API
                url = "https://api.unsplash.com/search/photos"
                headers = {
                    'Authorization': f'Client-ID {self.unsplash_key}'
                }
                params = {
                    'query': query,
                    'per_page': count,
                    'orientation': 'portrait',  # Better for vertical videos
                    'content_filter': 'high'
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            image_urls = []
                            for photo in data.get('results', []):
                                # Get high quality image URL
                                image_url = photo.get('urls', {}).get('regular')
                                if image_url:
                                    image_urls.append(image_url)
                            
                            # Cache URLs
                            self._cache_urls(cache_key, image_urls)
                            cached_urls = image_urls
                        else:
                            self.logger.warning(f"Unsplash API error: {response.status}")
                            return []
            
            # Download images
            downloaded_images = []
            for i, url in enumerate(cached_urls[:count]):
                filename = f"unsplash_{query.replace(' ', '_')}_{i}"
                image_path = await self._download_image_from_url(url, filename)
                if image_path:
                    downloaded_images.append(image_path)
            
            return downloaded_images
            
        except Exception as e:
            self.logger.warning(f"Error fetching from Unsplash: {str(e)}")
            return []
    
    async def _fetch_from_pixabay(self, query: str, count: int) -> List[str]:
        """
        Fetch images from Pixabay API.
        
        Args:
            query: Search query
            count: Number of images to fetch
            
        Returns:
            List of downloaded image paths
        """
        try:
            # Check cache first
            cache_key = f"pixabay_{hashlib.md5(query.encode()).hexdigest()}"
            cached_urls = self._get_cached_urls(cache_key)
            
            if not cached_urls:
                # Fetch from API
                url = "https://pixabay.com/api/"
                params = {
                    'key': self.pixabay_key,
                    'q': query,
                    'image_type': 'photo',
                    'orientation': 'vertical',
                    'min_width': self.min_image_size[0],
                    'min_height': self.min_image_size[1],
                    'per_page': count,
                    'safesearch': 'true'
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            image_urls = []
                            for hit in data.get('hits', []):
                                # Get high quality image URL
                                image_url = hit.get('webformatURL') or hit.get('largeImageURL')
                                if image_url:
                                    image_urls.append(image_url)
                            
                            # Cache URLs
                            self._cache_urls(cache_key, image_urls)
                            cached_urls = image_urls
                        else:
                            self.logger.warning(f"Pixabay API error: {response.status}")
                            return []
            
            # Download images
            downloaded_images = []
            for i, url in enumerate(cached_urls[:count]):
                filename = f"pixabay_{query.replace(' ', '_')}_{i}"
                image_path = await self._download_image_from_url(url, filename)
                if image_path:
                    downloaded_images.append(image_path)
            
            return downloaded_images
            
        except Exception as e:
            self.logger.warning(f"Error fetching from Pixabay: {str(e)}")
            return []
    
    async def _download_image_from_url(self, url: str, filename: str) -> Optional[str]:
        """
        Download image from URL.
        
        Args:
            url: Image URL
            filename: Base filename (without extension)
            
        Returns:
            Path to downloaded image file
        """
        try:
            # Generate cache filename
            url_hash = hashlib.md5(url.encode()).hexdigest()
            file_ext = self._get_file_extension(url)
            cache_filename = f"{filename}_{url_hash}{file_ext}"
            cache_path = os.path.join(self.cache_dir, cache_filename)
            
            # Check if already cached
            if os.path.exists(cache_path):
                # Check if cache is still valid
                cache_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_path))
                if cache_age.total_seconds() < self.cache_duration * 3600:
                    return cache_path
            
            # Download image
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Save to cache
                        with open(cache_path, 'wb') as f:
                            f.write(content)
                        
                        # Validate image
                        if self._validate_image(cache_path):
                            return cache_path
                        else:
                            os.remove(cache_path)
                            return None
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error downloading image from {url}: {str(e)}")
            return None
    
    def _get_file_extension(self, url: str) -> str:
        """
        Get file extension from URL.
        
        Args:
            url: Image URL
            
        Returns:
            File extension with dot
        """
        try:
            parsed_url = urlparse(url)
            path = parsed_url.path
            
            # Extract extension
            if '.' in path:
                ext = path.split('.')[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
                    return f'.{ext}'
            
            return '.jpg'  # Default
            
        except Exception:
            return '.jpg'
    
    def _validate_image(self, image_path: str) -> bool:
        """
        Validate that downloaded file is a valid image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if valid image
        """
        try:
            with Image.open(image_path) as img:
                # Check minimum size
                if img.width < self.min_image_size[0] or img.height < self.min_image_size[1]:
                    return False
                
                # Verify image can be loaded
                img.verify()
                return True
                
        except Exception:
            return False
    
    async def _process_image_for_video(self, image_path: str) -> Optional[str]:
        """
        Process image for video use (resize, enhance, etc.).
        
        Args:
            image_path: Path to original image
            
        Returns:
            Path to processed image
        """
        try:
            # Generate processed filename
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            processed_filename = f"processed_{base_name}.jpg"
            processed_path = os.path.join(self.cache_dir, processed_filename)
            
            # Check if already processed
            if os.path.exists(processed_path):
                return processed_path
            
            # Load and process image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Calculate target size maintaining aspect ratio
                img_ratio = img.width / img.height
                target_ratio = self.target_width / self.target_height
                
                if img_ratio > target_ratio:
                    # Image is wider, fit to height
                    new_height = self.target_height
                    new_width = int(new_height * img_ratio)
                else:
                    # Image is taller, fit to width
                    new_width = self.target_width
                    new_height = int(new_width / img_ratio)
                
                # Resize image
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Center crop to exact target dimensions
                left = (new_width - self.target_width) // 2
                top = (new_height - self.target_height) // 2
                img = img.crop((left, top, left + self.target_width, top + self.target_height))
                
                # Enhance image quality
                img = self._enhance_image(img)
                
                # Save processed image
                img.save(processed_path, 'JPEG', quality=85, optimize=True)
                
            return processed_path
            
        except Exception as e:
            self.logger.warning(f"Error processing image {image_path}: {str(e)}")
            return image_path  # Return original if processing fails
    
    def _enhance_image(self, img: Image.Image) -> Image.Image:
        """
        Enhance image for better video quality.
        
        Args:
            img: PIL Image object
            
        Returns:
            Enhanced image
        """
        try:
            # Increase contrast slightly
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)
            
            # Increase saturation slightly
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.1)
            
            # Sharpen image slightly
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.1)
            
            return img
            
        except Exception as e:
            self.logger.warning(f"Error enhancing image: {str(e)}")
            return img
    
    async def _get_fallback_image(self, index: int) -> Optional[str]:
        """
        Get fallback image when external sources fail.
        
        Args:
            index: Image index for variety
            
        Returns:
            Path to fallback image
        """
        try:
            # Try to download from a generic news source
            fallback_queries = ['breaking news', 'news studio', 'newspaper', 'media', 'journalism']
            query = fallback_queries[index % len(fallback_queries)]
            
            # Try Unsplash with fallback keywords
            images = await self._fetch_from_unsplash(query, 1)
            if images:
                return images[0]
            
            # Try Pixabay with fallback keywords
            images = await self._fetch_from_pixabay(query, 1)
            if images:
                return images[0]
            
            # Generate solid color fallback
            return self._create_solid_color_image(index)
            
        except Exception as e:
            self.logger.warning(f"Error getting fallback image: {str(e)}")
            return self._create_solid_color_image(index)
    
    async def _get_fallback_images(self, count: int) -> List[str]:
        """
        Get multiple fallback images.
        
        Args:
            count: Number of fallback images needed
            
        Returns:
            List of fallback image paths
        """
        fallback_images = []
        
        for i in range(count):
            fallback_image = await self._get_fallback_image(i)
            if fallback_image:
                fallback_images.append(fallback_image)
        
        return fallback_images
    
    def _create_solid_color_image(self, index: int) -> str:
        """
        Create a solid color image as ultimate fallback.
        
        Args:
            index: Index for color variety
            
        Returns:
            Path to created image
        """
        try:
            # Define color schemes
            colors = [
                (30, 30, 30),    # Dark gray
                (50, 50, 100),   # Dark blue
                (100, 30, 30),   # Dark red
                (30, 100, 30),   # Dark green
                (100, 50, 30),   # Dark orange
            ]
            
            color = colors[index % len(colors)]
            
            # Create image
            img = Image.new('RGB', (self.target_width, self.target_height), color)
            
            # Save fallback image
            fallback_filename = f"fallback_color_{index}.jpg"
            fallback_path = os.path.join(self.cache_dir, fallback_filename)
            img.save(fallback_path, 'JPEG', quality=85)
            
            return fallback_path
            
        except Exception as e:
            self.logger.error(f"Error creating solid color image: {str(e)}")
            return None
    
    def _get_cached_urls(self, cache_key: str) -> Optional[List[str]]:
        """Get cached image URLs."""
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}_urls.json")
            if os.path.exists(cache_file):
                # Check cache age
                cache_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
                if cache_age.total_seconds() < self.cache_duration * 3600:
                    with open(cache_file, 'r') as f:
                        return json.load(f)
        except Exception:
            pass
        return None
    
    def _cache_urls(self, cache_key: str, urls: List[str]):
        """Cache image URLs."""
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}_urls.json")
            with open(cache_file, 'w') as f:
                json.dump(urls, f)
        except Exception as e:
            self.logger.debug(f"Error caching URLs: {str(e)}")
    
    def cleanup_cache(self):
        """Clean up old cached images."""
        try:
            current_time = datetime.now()
            cleanup_count = 0
            
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    file_age = current_time - datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_age.total_seconds() > self.cache_duration * 3600 * 7:  # Keep for 7x cache duration
                        os.remove(file_path)
                        cleanup_count += 1
                except Exception:
                    pass
            
            if cleanup_count > 0:
                self.logger.info(f"Cleaned up {cleanup_count} old cached images")
                
        except Exception as e:
            self.logger.warning(f"Error cleaning up cache: {str(e)}")