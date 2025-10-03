"""
Logger Setup Utility for FlashVideoBot

Configures logging with file and console output based on configuration settings.

Author: FlashVideoBot Team
Date: October 2025
"""

import os
import logging
import logging.handlers
from datetime import datetime
from typing import Dict, Any


def setup_logger(config: Dict[str, Any]) -> logging.Logger:
    """
    Set up logging configuration based on config settings.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured logger instance
    """
    # Get logging configuration
    log_level = config.get('logging', {}).get('level', 'INFO')
    log_to_file = config.get('logging', {}).get('log_to_file', True)
    log_file = config.get('logging', {}).get('log_file', 'logs/flashvideobot.log')
    
    # Create logger
    logger = logging.getLogger('FlashVideoBot')
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if log_to_file:
        try:
            # Ensure log directory exists
            log_dir = os.path.dirname(log_file)
            os.makedirs(log_dir, exist_ok=True)
            
            # Create rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.warning(f"Could not set up file logging: {str(e)}")
    
    return logger


def log_performance(func_name: str, start_time: datetime, end_time: datetime, logger: logging.Logger):
    """
    Log performance metrics for a function.
    
    Args:
        func_name: Name of the function
        start_time: Function start time
        end_time: Function end time
        logger: Logger instance
    """
    duration = end_time - start_time
    logger.info(f"⏱️  {func_name} completed in {duration.total_seconds():.2f} seconds")


def log_memory_usage(logger: logging.Logger):
    """
    Log current memory usage (if psutil is available).
    
    Args:
        logger: Logger instance
    """
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        logger.debug(f"💾 Memory usage: {memory_mb:.1f} MB")
    except ImportError:
        pass  # psutil not available
    except Exception as e:
        logger.debug(f"Could not log memory usage: {str(e)}")


class ProgressLogger:
    """
    Context manager for logging progress of long-running operations.
    """
    
    def __init__(self, logger: logging.Logger, operation: str, total_items: int = None):
        """
        Initialize progress logger.
        
        Args:
            logger: Logger instance
            operation: Description of the operation
            total_items: Total number of items to process
        """
        self.logger = logger
        self.operation = operation
        self.total_items = total_items
        self.start_time = None
        self.current_item = 0
    
    def __enter__(self):
        """Start the progress logging."""
        self.start_time = datetime.now()
        if self.total_items:
            self.logger.info(f"🚀 Starting {self.operation} ({self.total_items} items)")
        else:
            self.logger.info(f"🚀 Starting {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End the progress logging."""
        if self.start_time:
            end_time = datetime.now()
            duration = end_time - self.start_time
            
            if exc_type is None:
                if self.total_items:
                    self.logger.info(f"✅ {self.operation} completed ({self.current_item}/{self.total_items} items) in {duration.total_seconds():.2f}s")
                else:
                    self.logger.info(f"✅ {self.operation} completed in {duration.total_seconds():.2f}s")
            else:
                self.logger.error(f"❌ {self.operation} failed after {duration.total_seconds():.2f}s: {str(exc_val)}")
    
    def update(self, item_count: int = 1, message: str = None):
        """
        Update progress.
        
        Args:
            item_count: Number of items processed
            message: Optional progress message
        """
        self.current_item += item_count
        
        if self.total_items and self.current_item % max(1, self.total_items // 10) == 0:
            percentage = (self.current_item / self.total_items) * 100
            self.logger.info(f"📊 {self.operation}: {percentage:.1f}% ({self.current_item}/{self.total_items})")
        
        if message:
            self.logger.debug(f"📝 {message}")


def create_error_logger(error_log_path: str = "logs/errors.log") -> logging.Logger:
    """
    Create a dedicated error logger for critical issues.
    
    Args:
        error_log_path: Path to error log file
        
    Returns:
        Error logger instance
    """
    error_logger = logging.getLogger('FlashVideoBot.Errors')
    error_logger.setLevel(logging.ERROR)
    
    # Ensure log directory exists
    log_dir = os.path.dirname(error_log_path)
    os.makedirs(log_dir, exist_ok=True)
    
    # File handler for errors only
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_path,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    
    error_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    error_handler.setFormatter(error_formatter)
    
    error_logger.addHandler(error_handler)
    return error_logger