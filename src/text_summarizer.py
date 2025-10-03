"""
Text Summarizer Module for FlashVideoBot

Uses NLP libraries to generate concise, engaging summaries and hooks
for news articles optimized for video content and viewer retention.

Author: FlashVideoBot Team
Date: October 2025
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from textstat import flesch_reading_ease, automated_readability_index


class TextSummarizer:
    """
    Generates concise summaries and engaging hooks for news articles
    using multiple NLP techniques optimized for video content.
    """
    
    def __init__(self, config):
        """
        Initialize the text summarizer with configuration.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.logger = logging.getLogger('FlashVideoBot.TextSummarizer')
        
        # Summarization settings
        self.max_length = config.get('ai.summarization.max_length', 100)
        self.min_length = config.get('ai.summarization.min_length', 30)
        self.model_name = config.get('ai.summarization.model', 'facebook/bart-large-cnn')
        
        # Download required NLTK data
        self._download_nltk_data()
        
        # Initialize transformers model (lazy loading)
        self.transformers_model = None
        self.transformers_tokenizer = None
    
    def _download_nltk_data(self):
        """Download required NLTK data packages."""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            self.logger.info("Downloading NLTK data...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
    
    def _load_transformers_model(self):
        """Lazy load transformers model to save memory."""
        if self.transformers_model is None:
            try:
                from transformers import pipeline
                self.transformers_model = pipeline(
                    "summarization",
                    model=self.model_name,
                    device=-1  # Use CPU
                )
                self.logger.info(f"Loaded summarization model: {self.model_name}")
            except Exception as e:
                self.logger.warning(f"Could not load transformers model: {str(e)}")
                self.transformers_model = False  # Mark as failed
    
    def summarize(self, text: str, method: str = "auto") -> str:
        """
        Generate a concise summary of the given text.
        
        Args:
            text: Input text to summarize
            method: Summarization method ("auto", "transformers", "extractive")
            
        Returns:
            Generated summary
        """
        if not text or len(text.strip()) < 50:
            return text.strip()
        
        try:
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            if method == "auto":
                # Choose best method based on text length and model availability
                if len(cleaned_text) > 500:
                    summary = self._summarize_with_transformers(cleaned_text)
                    if summary:
                        return summary
                
                # Fallback to extractive methods
                return self._summarize_extractive(cleaned_text)
            
            elif method == "transformers":
                return self._summarize_with_transformers(cleaned_text)
            
            elif method == "extractive":
                return self._summarize_extractive(cleaned_text)
            
            else:
                self.logger.warning(f"Unknown summarization method: {method}")
                return self._summarize_extractive(cleaned_text)
                
        except Exception as e:
            self.logger.error(f"Error summarizing text: {str(e)}")
            # Return first sentence as fallback
            sentences = nltk.sent_tokenize(text)
            return sentences[0] if sentences else text[:200]
    
    def _preprocess_text(self, text: str) -> str:
        """
        Clean and preprocess text for summarization.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove HTML tags and extra whitespace
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove unwanted phrases
        unwanted_phrases = [
            r'\[.*?\]',  # Text in square brackets
            r'Read more.*',
            r'Click here.*',
            r'Subscribe.*',
            r'Follow us.*'
        ]
        
        for pattern in unwanted_phrases:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _summarize_with_transformers(self, text: str) -> Optional[str]:
        """
        Summarize text using transformers model.
        
        Args:
            text: Text to summarize
            
        Returns:
            Generated summary or None if failed
        """
        try:
            # Load model if not already loaded
            self._load_transformers_model()
            
            if self.transformers_model is False:
                return None  # Model failed to load
            
            # Truncate text if too long for model
            max_input_length = 1000  # Conservative limit
            if len(text) > max_input_length:
                sentences = nltk.sent_tokenize(text)
                truncated_text = ""
                for sentence in sentences:
                    if len(truncated_text + sentence) > max_input_length:
                        break
                    truncated_text += sentence + " "
                text = truncated_text.strip()
            
            # Generate summary
            summary_result = self.transformers_model(
                text,
                max_length=self.max_length,
                min_length=self.min_length,
                do_sample=False
            )
            
            if summary_result and len(summary_result) > 0:
                summary = summary_result[0]['summary_text']
                return self._post_process_summary(summary)
            
        except Exception as e:
            self.logger.warning(f"Transformers summarization failed: {str(e)}")
        
        return None
    
    def _summarize_extractive(self, text: str, method: str = "textrank") -> str:
        """
        Summarize text using extractive methods.
        
        Args:
            text: Text to summarize
            method: Extractive method to use
            
        Returns:
            Generated summary
        """
        try:
            # Parse text
            parser = PlaintextParser.from_string(text, Tokenizer('english'))
            
            # Choose summarizer
            if method == "textrank":
                summarizer = TextRankSummarizer()
            elif method == "lsa":
                summarizer = LsaSummarizer()
            else:
                summarizer = LuhnSummarizer()
            
            # Generate summary (aim for 2-3 sentences)
            sentences_count = min(3, max(1, len(text) // 200))
            summary_sentences = summarizer(parser.document, sentences_count)
            
            # Combine sentences
            summary = " ".join([str(sentence) for sentence in summary_sentences])
            return self._post_process_summary(summary)
            
        except Exception as e:
            self.logger.warning(f"Extractive summarization failed: {str(e)}")
            # Fallback: return first few sentences
            sentences = nltk.sent_tokenize(text)
            return ". ".join(sentences[:2]) + "." if len(sentences) >= 2 else sentences[0] if sentences else text[:200]
    
    def _post_process_summary(self, summary: str) -> str:
        """
        Post-process generated summary for better readability.
        
        Args:
            summary: Raw summary
            
        Returns:
            Cleaned summary
        """
        # Clean up summary
        summary = summary.strip()
        
        # Ensure it ends with proper punctuation
        if summary and summary[-1] not in '.!?':
            summary += '.'
        
        # Remove duplicate sentences
        sentences = nltk.sent_tokenize(summary)
        unique_sentences = []
        seen = set()
        
        for sentence in sentences:
            sentence_key = sentence.lower().strip()
            if sentence_key not in seen:
                seen.add(sentence_key)
                unique_sentences.append(sentence)
        
        final_summary = " ".join(unique_sentences)
        
        # Ensure length constraints
        if len(final_summary) > self.max_length * 2:  # Allow some flexibility
            words = final_summary.split()
            final_summary = " ".join(words[:self.max_length // 5]) + "..."
        
        return final_summary
    
    def generate_hook(self, article: Dict[str, Any]) -> str:
        """
        Generate an engaging hook for the video opening.
        
        Args:
            article: Article dictionary
            
        Returns:
            Engaging hook text
        """
        try:
            title = article.get('title', '')
            description = article.get('description', '')
            source = article.get('source', 'Breaking News')
            
            # Hook templates based on content type
            hook_templates = [
                "🚨 BREAKING: {title}",
                "You won't believe what just happened: {key_point}",
                "URGENT UPDATE: {title}",
                "This changes everything: {key_point}",
                "JUST IN: {title}",
                "SHOCKING: {key_point}",
                "MAJOR NEWS: {title}",
                "This is huge: {key_point}"
            ]
            
            # Extract key point from description
            key_point = self._extract_key_point(description or title)
            
            # Choose template based on content sentiment and urgency
            urgency_keywords = ['breaking', 'urgent', 'emergency', 'crisis', 'shock']
            if any(keyword in title.lower() for keyword in urgency_keywords):
                template = hook_templates[0]  # Breaking news format
            else:
                # Rotate through templates for variety
                import random
                template = random.choice(hook_templates[1:])
            
            # Format hook
            hook = template.format(
                title=title.upper()[:50],
                key_point=key_point,
                source=source
            )
            
            return hook[:80]  # Keep it short for video
            
        except Exception as e:
            self.logger.warning(f"Error generating hook: {str(e)}")
            return f"🔥 {article.get('title', 'BREAKING NEWS')}"[:80]
    
    def _extract_key_point(self, text: str) -> str:
        """
        Extract the most important point from text.
        
        Args:
            text: Input text
            
        Returns:
            Key point
        """
        if not text:
            return "Big news story"
        
        # Extract first sentence as key point
        sentences = nltk.sent_tokenize(text)
        if sentences:
            key_point = sentences[0]
            
            # Truncate if too long
            if len(key_point) > 60:
                words = key_point.split()
                key_point = " ".join(words[:10]) + "..."
            
            return key_point
        
        return text[:60] + "..." if len(text) > 60 else text
    
    def generate_key_points(self, article: Dict[str, Any], max_points: int = 3) -> List[str]:
        """
        Generate key bullet points from article content.
        
        Args:
            article: Article dictionary
            max_points: Maximum number of points to generate
            
        Returns:
            List of key points
        """
        try:
            content = article.get('content') or article.get('description', '')
            if not content:
                return []
            
            # Extract sentences
            sentences = nltk.sent_tokenize(content)
            
            if len(sentences) <= max_points:
                return [self._format_bullet_point(s) for s in sentences]
            
            # Use extractive summarization to get key sentences
            try:
                parser = PlaintextParser.from_string(content, Tokenizer('english'))
                summarizer = TextRankSummarizer()
                key_sentences = summarizer(parser.document, max_points)
                
                points = [self._format_bullet_point(str(sentence)) for sentence in key_sentences]
                return points[:max_points]
                
            except Exception:
                # Fallback: take first N sentences
                return [self._format_bullet_point(s) for s in sentences[:max_points]]
        
        except Exception as e:
            self.logger.warning(f"Error generating key points: {str(e)}")
            return []
    
    def _format_bullet_point(self, text: str) -> str:
        """
        Format text as a bullet point.
        
        Args:
            text: Raw text
            
        Returns:
            Formatted bullet point
        """
        # Clean and truncate
        text = text.strip()
        if len(text) > 80:
            words = text.split()
            text = " ".join(words[:12]) + "..."
        
        # Ensure it starts with capital letter
        if text:
            text = text[0].upper() + text[1:]
        
        return f"• {text}"
    
    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze text sentiment for music/tone selection.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment label ('positive', 'negative', 'neutral')
        """
        try:
            # Simple keyword-based sentiment analysis
            positive_keywords = ['good', 'great', 'amazing', 'success', 'win', 'breakthrough', 'celebrate']
            negative_keywords = ['bad', 'terrible', 'crisis', 'disaster', 'fail', 'death', 'war', 'attack']
            
            text_lower = text.lower()
            
            positive_count = sum(1 for word in positive_keywords if word in text_lower)
            negative_count = sum(1 for word in negative_keywords if word in text_lower)
            
            if positive_count > negative_count:
                return 'positive'
            elif negative_count > positive_count:
                return 'negative'
            else:
                return 'neutral'
                
        except Exception as e:
            self.logger.warning(f"Error analyzing sentiment: {str(e)}")
            return 'neutral'
    
    def calculate_readability(self, text: str) -> Dict[str, float]:
        """
        Calculate readability metrics for text optimization.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of readability metrics
        """
        try:
            return {
                'flesch_reading_ease': flesch_reading_ease(text),
                'automated_readability_index': automated_readability_index(text),
                'sentence_count': len(nltk.sent_tokenize(text)),
                'word_count': len(nltk.word_tokenize(text))
            }
        except Exception as e:
            self.logger.warning(f"Error calculating readability: {str(e)}")
            return {
                'flesch_reading_ease': 0,
                'automated_readability_index': 0,
                'sentence_count': 0,
                'word_count': 0
            }