# Quick Start Guide

This guide will help you set up and run FlashVideoBot quickly. For more detailed instructions, please refer to the full documentation.

## Prerequisites

- Python 3.9 or higher
- FFmpeg installed and in your PATH
- Git (for cloning the repository)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/FlashVideoBot.git
   cd FlashVideoBot
   ```

2. Install dependencies:
   
   **Windows:**
   ```powershell
   .\setup_windows.ps1
   ```
   
   **Unix/macOS:**
   ```bash
   ./setup_unix.sh
   ```
   
   Or manually with pip:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the example configuration file:
   ```bash
   cp config/config.example.yaml config/config_local.yaml
   ```

2. Edit `config/config_local.yaml` and add your API keys:
   - NewsAPI key
   - Unsplash API key
   - Pixabay API key
   - Other optional APIs as needed

3. See the [API Setup Guide](./API_SETUP_GUIDE.md) for instructions on how to obtain these API keys.

## Running FlashVideoBot

### Basic Usage

Run the main script to generate videos:

```bash
python main.py
```

This will:
1. Fetch news articles from configured sources
2. Generate video content for each article
3. Save videos to the `videos/` directory

### Options

```bash
# Generate videos from a specific number of articles
python main.py --articles 3

# Use a specific configuration file
python main.py --config config/my_custom_config.yaml

# Test your API configurations
python test_apis.py

# Generate a simple test video
python quickstart.py
```

## Sample Videos

After running the application, check the `videos/` directory for the generated videos. The filename format is configurable in your config file.

## Troubleshooting

If you encounter any issues:

1. Check the logs in `logs/flashvideobot.log`
2. Make sure all API keys are correctly entered
3. Verify that FFmpeg is properly installed
4. Check the main README.md for troubleshooting tips

## Next Steps

- Customize your video format in the configuration file
- Add more RSS feeds to increase news sources
- Explore advanced options in the [Configuration Options](./CONFIGURATION.md) guide

For detailed information and advanced usage, please refer to the full documentation.