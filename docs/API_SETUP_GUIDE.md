# API Configuration Guide for FlashVideoBot

This document provides step-by-step instructions on how to obtain all the API keys required for FlashVideoBot to function properly. These APIs enable news fetching, image searching, text-to-speech conversion, and other features of the application.

## Table of Contents
- [News APIs](#news-apis)
  - [NewsAPI](#newsapi)
- [Image APIs](#image-apis)
  - [Unsplash API](#unsplash-api)
  - [Pixabay API](#pixabay-api)
  - [Pexels API](#pexels-api)
- [Text-to-Speech APIs](#text-to-speech-apis)
  - [Google Text-to-Speech](#google-text-to-speech)
  - [ElevenLabs API](#elevenlabs-api)
  - [Microsoft Azure Text-to-Speech](#microsoft-azure-text-to-speech)
- [AI and NLP APIs](#ai-and-nlp-apis)
  - [OpenAI API](#openai-api)
  - [HuggingFace API](#huggingface-api)
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

### Pexels API
Pexels offers high-quality, free stock photos and videos.

1. Visit [Pexels API](https://www.pexels.com/api/)
2. Click "Get Started"
3. Sign up for an account or sign in
4. Your API key will be displayed on your dashboard
5. Copy this key to `config_local.yaml` under `images.pexels_api_key`

**Free Plan Limits:**
- 200 requests per hour
- 20,000 requests per month
- Must include attribution in your application

## Text-to-Speech APIs

### Google Text-to-Speech
The default TTS engine (gTTS) doesn't require an API key but has limitations. For higher quality or more features:

1. FlashVideoBot uses the `gtts` library by default which doesn't require an API key
2. Set `audio.tts.engine` to "gtts" in your config file
3. This will use Google's free TTS service with limited voices and features

**Limitations:**
- Limited voice options
- Internet connection required
- Usage limits may apply

### ElevenLabs API
For premium, highly realistic voice synthesis:

1. Visit [ElevenLabs](https://elevenlabs.io/)
2. Create an account
3. Navigate to your profile settings
4. Copy your API key
5. Set `audio.tts.engine` to "elevenlabs" in your config file
6. Copy the API key to `config_local.yaml` under `audio.tts.elevenlabs_api_key`
7. Select a voice ID from your ElevenLabs dashboard and add it under `audio.tts.elevenlabs_voice_id`

**Free Plan Limits:**
- 10,000 characters per month
- Access to basic voices

### Microsoft Azure Text-to-Speech
For high-quality neural voices with multiple language support:

1. Create an [Azure account](https://azure.microsoft.com/free/)
2. Create a Speech service resource in the Azure portal
3. Navigate to your resource and copy the API key and region
4. Set `audio.tts.engine` to "azure" in your config file
5. Copy the key to `config_local.yaml` under `audio.tts.azure_tts_key`
6. Add your Azure region under `audio.tts.azure_region`
7. Choose a voice from the [Azure Neural Voice list](https://learn.microsoft.com/azure/ai-services/speech-service/language-support?tabs=tts) and add it under `audio.tts.azure_voice_name`

**Free Tier Limits:**
- 5 hours of audio per month
- Full neural voice access

## AI and NLP APIs

### OpenAI API
For enhanced text summarization and content generation:

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to the API section
4. Create an API key
5. Copy this key to `config_local.yaml` under `ai.openai.api_key`
6. Set your preferred model under `ai.openai.model`

**Free Tier:**
- Limited or no free tier (check current OpenAI pricing)
- Pay-as-you-go pricing available

### HuggingFace API
For access to various open-source AI models:

1. Create a [HuggingFace account](https://huggingface.co/join)
2. Navigate to your profile and click on "Access Tokens"
3. Create a new token with "read" access
4. Copy this token to `config_local.yaml` under `ai.huggingface.api_key`

**Free Plan Limits:**
- Rate limits apply based on model popularity
- Some models may have restrictions

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

```python
python main.py --test-apis
```

This will validate your configuration and test each API connection.

---

For support or questions about API configuration, please open an issue on the GitHub repository.