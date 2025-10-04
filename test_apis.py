#!/usr/bin/env python
"""
API Test Script for FlashVideoBot

This script tests if all configured APIs in config_local.yaml are working properly.
"""

import os
import sys
import yaml
import requests
from colorama import init, Fore, Style
import argparse

# Initialize colorama for cross-platform colored terminal output
init()

def print_success(message):
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")

def print_warning(message):
    print(f"{Fore.YELLOW}⚠️ {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.CYAN}ℹ️ {message}{Style.RESET_ALL}")

def print_section(title):
    print(f"\n{Fore.BLUE}{'=' * 50}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{title.center(50)}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'=' * 50}{Style.RESET_ALL}\n")

def load_config(config_path):
    """Load the configuration file."""
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print_error(f"Configuration file not found: {config_path}")
        print_info("Please create a config_local.yaml file using config.example.yaml as a template")
        sys.exit(1)
    except yaml.YAMLError as e:
        print_error(f"Error parsing configuration file: {e}")
        sys.exit(1)

def test_newsapi(api_key):
    """Test NewsAPI connection."""
    if not api_key or api_key == "YOUR_NEWSAPI_KEY_HERE":
        print_warning("NewsAPI key not configured")
        return False
    
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print_success("NewsAPI connection successful")
            return True
        else:
            print_error(f"NewsAPI error: {response.status_code} - {response.json().get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print_error(f"NewsAPI connection failed: {e}")
        return False

def test_unsplash(api_key):
    """Test Unsplash API connection."""
    if not api_key or api_key == "YOUR_UNSPLASH_KEY_HERE":
        print_warning("Unsplash API key not configured")
        return False
    
    url = f"https://api.unsplash.com/photos/random?query=news&client_id={api_key}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print_success("Unsplash API connection successful")
            return True
        else:
            print_error(f"Unsplash API error: {response.status_code} - {response.json().get('errors', ['Unknown error'])[0]}")
            return False
    except Exception as e:
        print_error(f"Unsplash API connection failed: {e}")
        return False

def test_pixabay(api_key):
    """Test Pixabay API connection."""
    if not api_key or api_key == "YOUR_PIXABAY_API_KEY_HERE":
        print_warning("Pixabay API key not configured")
        return False
    
    url = f"https://pixabay.com/api/?key={api_key}&q=news&image_type=photo"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print_success("Pixabay API connection successful")
            return True
        else:
            print_error(f"Pixabay API error: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Pixabay API connection failed: {e}")
        return False











def test_rss_feeds(feeds):
    """Test RSS feed connections."""
    if not feeds:
        print_warning("No RSS feeds configured")
        return False
    
    success_count = 0
    for feed_url in feeds:
        try:
            response = requests.get(feed_url, timeout=10)
            if response.status_code == 200:
                print_success(f"RSS feed connection successful: {feed_url}")
                success_count += 1
            else:
                print_error(f"RSS feed error ({feed_url}): {response.status_code}")
        except Exception as e:
            print_error(f"RSS feed connection failed ({feed_url}): {e}")
    
    return success_count > 0

def main():
    parser = argparse.ArgumentParser(description="Test FlashVideoBot API configurations")
    parser.add_argument("--config", default="config/config_local.yaml", help="Path to the configuration file")
    parser.add_argument("--verbose", action="store_true", help="Show detailed information")
    args = parser.parse_args()
    
    print_section("FlashVideoBot API Test")
    print_info(f"Testing configuration file: {args.config}")
    
    config = load_config(args.config)
    
    # Track API test results
    results = {
        "required": 0,
        "required_success": 0,
        "optional": 0,
        "optional_success": 0
    }
    
    print_section("Testing News Sources")
    
    # Test NewsAPI
    if test_newsapi(config.get("news", {}).get("newsapi_key")):
        results["required_success"] += 1
    results["required"] += 1
    
    # Test RSS Feeds
    if test_rss_feeds(config.get("news", {}).get("rss_feeds")):
        results["required_success"] += 1
    results["required"] += 1
    
    print_section("Testing Image APIs")
    
    # Test Unsplash
    if test_unsplash(config.get("images", {}).get("unsplash_access_key")):
        results["optional_success"] += 1
    results["optional"] += 1
    
    # Test Pixabay
    if test_pixabay(config.get("images", {}).get("pixabay_api_key")):
        results["optional_success"] += 1
    results["optional"] += 1
    
    # Note: No additional API tests needed for TTS as the default engines don't require API keys
    print_section("TTS Status")
    print_info(f"Using TTS engine: {config.get('audio', {}).get('tts', {}).get('engine', 'gtts')}")
    if config.get('audio', {}).get('tts', {}).get('engine', 'gtts') in ['gtts', 'pyttsx3']:
        print_success("TTS engine is properly configured")
    else:
        print_warning("Unknown TTS engine configured")
    
    print_section("Summary")
    
    print(f"{Fore.GREEN}Required APIs: {results['required_success']}/{results['required']} successful{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Optional APIs: {results['optional_success']}/{results['optional']} successful{Style.RESET_ALL}")
    
    if results["required_success"] == results["required"]:
        print_success("\nAll required APIs are configured and working correctly! 🎉")
        print_info("You can now run FlashVideoBot successfully.")
    else:
        print_warning("\nSome required APIs failed their tests.")
        print_info("Please check your configuration and API keys.")
    
    if results["optional_success"] < results["optional"]:
        print_info("\nSome optional APIs are not configured or failed.")
        print_info("You can still run FlashVideoBot, but with reduced functionality.")
    
    print(f"\n{Fore.BLUE}{'=' * 50}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()