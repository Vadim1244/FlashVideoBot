# Configuration Options

This document explains all configuration options available in FlashVideoBot's `config.yaml` file.

## Configuration Structure

The configuration file is organized into several sections:

1. **News** - News source settings
2. **Video** - Video generation parameters
3. **Audio** - Text-to-speech and music settings
4. **Images** - Image retrieval settings
5. **AI/NLP** - AI model configurations
6. **Output** - Output formatting options

## News Configuration

```yaml
news:
  # NewsAPI (get free key at https://newsapi.org)
  newsapi_key: "YOUR_NEWSAPI_KEY_HERE"
  
  # RSS Feeds
  rss_feeds:
    - "https://feeds.bbci.co.uk/news/rss.xml"
    - "https://rss.cnn.com/rss/edition.rss"
    # Add more RSS feeds here
  
  # News categories to fetch
  categories: ["general", "technology", "business", "entertainment", "health", "science", "sports"]
  
  # Number of articles to process per run
  max_articles: 5
```

| Option | Description | Default |
|--------|-------------|---------|
| `newsapi_key` | Your NewsAPI API key | None (required) |
| `rss_feeds` | List of RSS feed URLs | Includes major news sources |
| `categories` | News categories to fetch | All major categories |
| `max_articles` | Maximum number of articles to process | 5 |

## Video Configuration

```yaml
video:
  # Video dimensions (YouTube Shorts format)
  width: 1080
  height: 1920
  fps: 30
  duration: 30  # Max video duration in seconds
  
  # Text animation settings
  text:
    font_size: 60
    title_font_size: 80
    font_color: "#FFFFFF"
    bg_color: "#000000"
    stroke_color: "#FF0000"
    stroke_width: 2
    
  # Transition effects
  transitions:
    fade_duration: 0.5
    zoom_factor: 1.2
    slide_duration: 0.3
    
  # Background settings
  background:
    blur_intensity: 2
    brightness_factor: 0.7
    contrast_factor: 1.2
```

| Option | Description | Default |
|--------|-------------|---------|
| `width` | Video width in pixels | 1080 |
| `height` | Video height in pixels | 1920 |
| `fps` | Frames per second | 30 |
| `duration` | Maximum video duration in seconds | 30 |
| `text.font_size` | Default text font size | 60 |
| `text.title_font_size` | Title text font size | 80 |
| `text.font_color` | Text color (hex format) | #FFFFFF |
| `text.bg_color` | Text background color | #000000 |
| `text.stroke_color` | Text outline color | #FF0000 |
| `text.stroke_width` | Text outline width | 2 |
| `transitions.fade_duration` | Duration of fade transitions | 0.5 |
| `transitions.zoom_factor` | Zoom level for zoom transitions | 1.2 |
| `transitions.slide_duration` | Duration of slide transitions | 0.3 |
| `background.blur_intensity` | Background blur strength | 2 |
| `background.brightness_factor` | Background brightness adjustment | 0.7 |
| `background.contrast_factor` | Background contrast adjustment | 1.2 |

## Audio Configuration

```yaml
audio:
  # Text-to-speech settings
  tts:
    engine: "gtts"  # options: "gtts", "pyttsx3"
    language: "en"
    speed: 1.2
    
  # Background music
  music:
    enabled: true
    volume: 0.3
    fade_in: 1.0
    fade_out: 1.0
```

| Option | Description | Default |
|--------|-------------|---------|
| `tts.engine` | TTS engine to use | gtts |
| `tts.language` | Speech language code | en |
| `tts.speed` | Speech speed factor | 1.2 |
| `music.enabled` | Enable background music | true |
| `music.volume` | Music volume (0.0-1.0) | 0.3 |
| `music.fade_in` | Fade-in duration in seconds | 1.0 |
| `music.fade_out` | Fade-out duration in seconds | 1.0 |

## Image Configuration

```yaml
images:
  # Unsplash (get free key at https://unsplash.com/developers)
  unsplash_access_key: "YOUR_UNSPLASH_KEY_HERE"
  
  # Pixabay (get free key at https://pixabay.com/api/docs/)
  pixabay_api_key: "YOUR_PIXABAY_KEY_HERE"
  
  # Fallback keywords for image search
  fallback_keywords: ["news", "breaking news", "media", "journalism", "newspaper"]
```

| Option | Description | Default |
|--------|-------------|---------|
| `unsplash_access_key` | Unsplash API access key | None |
| `pixabay_api_key` | Pixabay API key | None |
| `fallback_keywords` | Keywords for when article keywords aren't available | General news terms |

## AI/NLP Configuration

```yaml
ai:
  # Summarization settings
  summarization:
    max_length: 100
    min_length: 30
    
  # Sentiment analysis for music selection
  sentiment_analysis: true
```

| Option | Description | Default |
|--------|-------------|---------|
| `summarization.max_length` | Maximum summary length in words | 100 |
| `summarization.min_length` | Minimum summary length in words | 30 |
| `sentiment_analysis` | Enable sentiment analysis | true |

## Output Configuration

```yaml
output:
  # Video output format
  format: "mp4"
  quality: "high"  # high, medium, low
  
  # File naming
  filename_format: "news_video_{timestamp}_{index}"
  
  # Cleanup old files (days)
  cleanup_after_days: 7
```

| Option | Description | Default |
|--------|-------------|---------|
| `format` | Video output format | mp4 |
| `quality` | Video quality preset | high |
| `filename_format` | Template for output filenames | news_video_{timestamp}_{index} |
| `cleanup_after_days` | Delete files older than this many days | 7 |

## Environment Variables

You can also use environment variables to override configuration values. Use the following format:

```bash
export NEWSAPI_KEY="YOUR_NEWS_API_KEY"
export UNSPLASH_KEY="YOUR_UNSPLASH_ACCESS_KEY"
export PIXABAY_KEY="YOUR_PIXABAY_API_KEY"
```

Environment variables take precedence over values in the configuration file.

---

For more information, see the [API Setup Guide](./API_SETUP_GUIDE.md) to learn how to obtain all the required API keys.