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

def test_pexels(api_key):
    """Test Pexels API connection."""
    if not api_key or api_key == "YOUR_PEXELS_API_KEY_HERE":
        print_warning("Pexels API key not configured")
        return False
    
    url = "https://api.pexels.com/v1/search?query=news&per_page=1"
    headers = {"Authorization": api_key}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print_success("Pexels API connection successful")
            return True
        else:
            print_error(f"Pexels API error: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Pexels API connection failed: {e}")
        return False

def test_elevenlabs(api_key):
    """Test ElevenLabs API connection."""
    if not api_key or api_key == "YOUR_ELEVENLABS_API_KEY_HERE":
        print_warning("ElevenLabs API key not configured")
        return False
    
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print_success("ElevenLabs API connection successful")
            return True
        else:
            print_error(f"ElevenLabs API error: {response.status_code} - {response.json().get('detail', {}).get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print_error(f"ElevenLabs API connection failed: {e}")
        return False

def test_azure_tts(api_key, region):
    """Test Azure TTS API connection."""
    if not api_key or api_key == "YOUR_AZURE_TTS_KEY_HERE" or not region:
        print_warning("Azure TTS API key or region not configured")
        return False
    
    url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/voices/list"
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print_success("Azure TTS API connection successful")
            return True
        else:
            print_error(f"Azure TTS API error: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Azure TTS API connection failed: {e}")
        return False

def test_openai(api_key):
    """Test OpenAI API connection."""
    if not api_key or api_key == "YOUR_OPENAI_API_KEY_HERE":
        print_warning("OpenAI API key not configured")
        return False
    
    url = "https://api.openai.com/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print_success("OpenAI API connection successful")
            return True
        else:
            print_error(f"OpenAI API error: {response.status_code} - {response.json().get('error', {}).get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print_error(f"OpenAI API connection failed: {e}")
        return False

def test_huggingface(api_key):
    """Test HuggingFace API connection."""
    if not api_key or api_key == "YOUR_HUGGINGFACE_API_KEY_HERE":
        print_warning("HuggingFace API key not configured")
        return False
    
    url = "https://api-inference.huggingface.co/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print_success("HuggingFace API connection successful")
            return True
        else:
            print_error(f"HuggingFace API error: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"HuggingFace API connection failed: {e}")
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
    
    # Test Pexels
    if test_pexels(config.get("images", {}).get("pexels_api_key")):
        results["optional_success"] += 1
    results["optional"] += 1
    
    print_section("Testing TTS APIs")
    
    # Test ElevenLabs
    tts_engine = config.get("audio", {}).get("tts", {}).get("engine", "gtts")
    if tts_engine == "elevenlabs":
        if test_elevenlabs(config.get("audio", {}).get("tts", {}).get("elevenlabs_api_key")):
            results["required_success"] += 1
        results["required"] += 1
    else:
        if test_elevenlabs(config.get("audio", {}).get("tts", {}).get("elevenlabs_api_key")):
            results["optional_success"] += 1
        results["optional"] += 1
    
    # Test Azure TTS
    if tts_engine == "azure":
        if test_azure_tts(
            config.get("audio", {}).get("tts", {}).get("azure_tts_key"),
            config.get("audio", {}).get("tts", {}).get("azure_region")
        ):
            results["required_success"] += 1
        results["required"] += 1
    else:
        if test_azure_tts(
            config.get("audio", {}).get("tts", {}).get("azure_tts_key"),
            config.get("audio", {}).get("tts", {}).get("azure_region")
        ):
            results["optional_success"] += 1
        results["optional"] += 1
    
    print_section("Testing AI APIs")
    
    # Test OpenAI
    if test_openai(config.get("ai", {}).get("openai", {}).get("api_key")):
        results["optional_success"] += 1
    results["optional"] += 1
    
    # Test HuggingFace
    if test_huggingface(config.get("ai", {}).get("huggingface", {}).get("api_key")):
        results["optional_success"] += 1
    results["optional"] += 1
    
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