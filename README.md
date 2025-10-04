# FlashVideoBot 🎬⚡

**Automated News Video Generator for YouTube Shorts**

FlashVideoBot is a comprehensive Python application that automatically fetches the latest news from multiple sources and creates engaging, eye-catching videos optimized for YouTube-style retention. The bot generates short (15-30 second) videos with dynamic text animations, visual effects, and professional audio narration.

## 🚀 Features

### 📰 News Fetching
- **Multiple Sources**: NewsAPI, RSS feeds from major news outlets
- **Smart Filtering**: Removes duplicates and low-quality content
- **Category Support**: Technology, business, health, sports, and more
- **Caching**: Intelligent caching to avoid duplicate API calls

### 🧠 Content Summarization
- **NLP-Powered**: Uses transformers, sumy, and NLTK for intelligent summarization
- **Engaging Hooks**: Generates attention-grabbing opening statements
- **Key Points**: Extracts main points for bullet-point presentation
- **Readability**: Optimizes text for video consumption

### 🎬 Video Creation
- **YouTube Shorts Format**: Optimized 1080x1920 vertical videos
- **Dynamic Text Effects**: Typewriter, pulse, slide, and bounce animations
- **Professional Transitions**: Fade, zoom, and slide effects between segments
- **Visual Effects**: Ken Burns effect, vignette, progress bars
- **Retention Optimization**: Fast pacing with strategic visual hooks

### 🎵 Audio Enhancement
- **Text-to-Speech**: Support for gTTS and pyttsx3 engines
- **Background Music**: Automatic music selection based on content sentiment
- **Natural Pacing**: Strategic pauses and emphasis for better engagement
- **Audio Mixing**: Balanced narration and background audio

### 🖼️ Visual Assets
- **Stock Images**: Integration with Unsplash and Pixabay APIs
- **Smart Keywords**: Automatic keyword extraction for relevant visuals
- **Image Processing**: Automatic resizing, enhancement, and optimization
- **Fallback System**: Ensures videos always have appropriate visuals

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 2GB free space for cache and output files

### Optional Dependencies
- **FFmpeg**: For advanced audio/video processing (recommended)
- **ImageMagick**: For enhanced image processing

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/TheUnknown550/FlashVideoBot.git
cd FlashVideoBot
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download NLTK Data
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

### 5. Install FFmpeg (Optional but Recommended)
- **Windows**: Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian)

## ⚙️ Configuration

### 1. API Keys Setup
Copy the example configuration file and add your API keys:

```bash
cp config/config.example.yaml config/config_local.yaml
```

Edit `config/config_local.yaml` with your API keys:

```yaml
news:
  # Get free key at https://newsapi.org
  newsapi_key: "your_newsapi_key_here"

images:
  # Get free key at https://unsplash.com/developers
  unsplash_access_key: "your_unsplash_key_here"
  
  # Get free key at https://pixabay.com/api/docs/
  pixabay_api_key: "your_pixabay_key_here"
```

### 2. API Configuration Guide
For detailed instructions on how to obtain all the required API keys:

1. Read our comprehensive [API Setup Guide](docs/API_SETUP_GUIDE.md)
2. The guide covers NewsAPI, Unsplash, Pixabay, Pexels, TTS services, and AI APIs
3. Free tier options are available for all required APIs

### 3. Testing Your API Configuration
You can test if all your API keys are working correctly by running:

```bash
python test_apis.py
```

This will check all configured APIs and report their status.

### 4. Environment Variables (Alternative)
You can also set API keys via environment variables:

```bash
export NEWSAPI_KEY="your_newsapi_key_here"
export UNSPLASH_ACCESS_KEY="your_unsplash_key_here"
export PIXABAY_API_KEY="your_pixabay_key_here"
```

### 3. Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `news.max_articles` | Number of articles to process | 5 |
| `video.duration` | Maximum video length (seconds) | 30 |
| `video.width` | Video width (pixels) | 1080 |
| `video.height` | Video height (pixels) | 1920 |
| `audio.tts.engine` | TTS engine (gtts/pyttsx3) | gtts |
| `audio.music.enabled` | Enable background music | true |

## 🚀 Usage

### Basic Usage
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Run the bot
python main.py
```

### Custom Configuration
```bash
# Use custom config file
python main.py --config custom_config.yaml

# Set maximum articles
python main.py --max-articles 10

# Disable background music
python main.py --no-music
```

### Programmatic Usage
```python
from main import FlashVideoBot
import asyncio

async def create_videos():
    bot = FlashVideoBot()
    await bot.run()

# Run the bot
asyncio.run(create_videos())
```

## 📁 Project Structure

```
FlashVideoBot/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── config/
│   └── config.yaml        # Configuration template
├── src/
│   ├── config_manager.py  # Configuration handling
│   ├── news_fetcher.py    # News source integration
│   ├── text_summarizer.py # NLP and summarization
│   ├── video_creator.py   # Video generation with effects
│   ├── audio_manager.py   # TTS and audio processing
│   ├── image_manager.py   # Image fetching and processing
│   └── utils/
│       └── logger.py      # Logging utilities
├── assets/
│   ├── fonts/            # Custom fonts (optional)
│   ├── music/            # Background music files
│   └── temp/             # Temporary files and cache
├── videos/               # Generated video output
└── logs/                 # Application logs
```

## 🎯 Video Generation Process

1. **News Fetching**: Retrieves latest articles from configured sources
2. **Content Analysis**: Extracts keywords and generates summaries
3. **Hook Creation**: Creates attention-grabbing opening statements
4. **Visual Assets**: Downloads relevant images based on content
5. **Audio Generation**: Creates TTS narration with natural pacing
6. **Video Assembly**: Combines all elements with dynamic effects
7. **Optimization**: Applies retention-focused enhancements

## 🎨 Customization

### Adding Custom Fonts
1. Place font files (.ttf, .otf) in `assets/fonts/`
2. Update configuration to reference new fonts

### Adding Background Music
1. Place audio files (.mp3, .wav) in `assets/music/`
2. Name files with mood keywords (e.g., "upbeat_news.mp3", "dramatic_breaking.mp3")

### Custom Video Effects
Modify `src/video_creator.py` to add new:
- Text animations
- Transition effects
- Visual filters
- Color schemes

## 🔧 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Install missing packages
pip install -r requirements.txt

# Update packages
pip install --upgrade -r requirements.txt
```

**API Rate Limits**
- Ensure API keys are valid and have sufficient quota
- Check API usage limits on provider websites
- Implement rate limiting in configuration

**Video Generation Fails**
- Check FFmpeg installation
- Verify sufficient disk space
- Review logs for specific error messages

**Poor Video Quality**
- Increase image resolution settings
- Use higher quality TTS engine
- Add better background music

### Performance Optimization

**Memory Usage**
- Reduce `news.max_articles` for lower memory usage
- Enable image caching
- Clear temp files regularly

**Speed Improvements**
- Use local TTS engine (pyttsx3) instead of gTTS
- Increase `performance.max_workers`
- Cache images and audio files

## 📊 Output

Generated videos include:
- **File Format**: MP4 (H.264/AAC)
- **Resolution**: 1080x1920 (YouTube Shorts optimized)
- **Duration**: 15-30 seconds
- **Naming**: `news_video_YYYYMMDD_HHMMSS.mp4`
- **Location**: `videos/` directory

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- [Quick Start Guide](docs/QUICKSTART.md) - Get up and running quickly
- [API Setup Guide](docs/API_SETUP_GUIDE.md) - How to obtain all required API keys
- [Configuration Options](docs/CONFIGURATION.md) - Detailed configuration settings
- [Full Documentation Index](docs/README.md) - Complete documentation reference

## 📝 Logs

Application logs are saved to:
- **Main Log**: `logs/flashvideobot.log`
- **Error Log**: `logs/errors.log`
- **Rotation**: Logs rotate automatically to prevent large files

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NewsAPI** for news data
- **Unsplash & Pixabay** for stock images
- **OpenAI Transformers** for text summarization
- **MoviePy** for video processing
- **NLTK & Sumy** for natural language processing

## 🆘 Support

- **Issues**: Report bugs on [GitHub Issues](https://github.com/TheUnknown550/FlashVideoBot/issues)
- **Discussions**: Join discussions on [GitHub Discussions](https://github.com/TheUnknown550/FlashVideoBot/discussions)
- **Documentation**: Full docs at [docs/](docs/)

## 🔮 Roadmap

- [ ] Real-time news monitoring
- [ ] Multiple video formats (landscape, square)
- [ ] Advanced AI voice generation
- [ ] Social media platform integration
- [ ] Custom branding and overlays
- [ ] Analytics and performance tracking
- [ ] Multi-language support
- [ ] Live streaming integration

---

**Made with ❤️ for creators who want to automate engaging news content**