# API Configuration Guide for FlashVideoBot

This document provides step-by-step instructions on how to obtain all the API keys required for FlashVideoBot to function properly. These APIs enable news fetching, image searching, text-to-speech conversion, and other features of the application.

## Table of Contents
- [News APIs](#news-apis)
  - [NewsAPI](#newsapi)
- [Image APIs](#image-apis)
  - [Unsplash API](#unsplash-api)
  - [Pixabay API](#pixabay-api)
- [Text-to-Speech APIs](#text-to-speech-apis)
  - [Google Text-to-Speech](#google-text-to-speech)
- [Configuration Setup](#configuration-setup)

## News APIs

### NewsAPI
NewsAPI provides access to breaking news headlines and historical news articles from over 80,000 sources worldwide.

1. Visit [NewsAPI.org](https://newsapi.org/)
2. Click "Get API Key"
3. Register for a free account
4. Verify your email address
5. Your API key will be displayed on your account dashboard
6. Copy this key to `config_local.yaml` under `news.newsapi_key`

**Free Plan Limits:**
- 100 requests per day
- Limited to headlines and metadata
- No historical data beyond 1 month

**Note:** If you exceed the free tier limits, consider upgrading to a paid plan or relying more on the RSS feeds that don't require API keys.

## Image APIs

### Unsplash API
Unsplash offers high-quality, royalty-free images that can be used as backgrounds for your videos.

1. Visit [Unsplash Developers](https://unsplash.com/developers)
2. Click "Register as a Developer"
3. Create an account or sign in
4. Create a new application and accept the API terms
5. Fill in the required information about your application
6. Once approved, obtain your Access Key from the application dashboard
7. Copy this key to `config_local.yaml` under `images.unsplash_access_key`

**Free Plan Limits:**
- 50 requests per hour
- 500 requests per month

### Pixabay API
Pixabay provides over 2.3 million high-quality stock images, videos, and music.

1. Visit [Pixabay API Documentation](https://pixabay.com/api/docs/)
2. Create a Pixabay account or sign in
3. Navigate to your profile and click "API"
4. Your API key will be displayed
5. Copy this key to `config_local.yaml` under `images.pixabay_api_key`

**Free Plan Limits:**
- 5,000 requests per hour
- No daily/monthly limits
- Cannot be used for some commercial purposes (check terms)



## Text-to-Speech APIs

### Google Text-to-Speech
The default TTS engine (gTTS) doesn't require an API key but has limitations:

1. FlashVideoBot uses the `gtts` library by default which doesn't require an API key
2. Set `audio.tts.engine` to "gtts" in your config file
3. This will use Google's free TTS service with limited voices and features

**Limitations:**
- Limited voice options
- Internet connection required
- Usage limits may apply

Alternatively, you can use the local pyttsx3 engine by setting `audio.tts.engine` to "pyttsx3" in your config file.



## Configuration Setup

1. Copy the example configuration file to create your local configuration:
   ```
   cp config/config.example.yaml config/config_local.yaml
   ```

2. Open `config_local.yaml` in your preferred text editor

3. Replace all instances of `YOUR_*_KEY_HERE` with your actual API keys

4. Save the file

5. The application will automatically use your `config_local.yaml` file when running

**Important Notes:**
- Never commit your `config_local.yaml` file to version control
- The file is already added to `.gitignore` to prevent accidental commits
- If you need to share your configuration, remove all API keys first
- Consider using environment variables for sensitive API keys in production

## Testing Your Configuration

You can test if your API keys are working properly by running the following command:

```bash
python test_apis.py
```

This will validate your configuration and test each API connection.

---

For support or questions about API configuration, please open an issue on the GitHub repository.