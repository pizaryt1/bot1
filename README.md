# 🤖 Telegram Media Downloader Bot

A comprehensive Telegram bot for downloading media from multiple platforms including YouTube, Instagram, Twitter, Facebook, and Spotify.

## ✨ Features

### 🌍 Multi-Language Support
- Arabic (العربية) 🇸🇦
- English 🇺🇸

### 📱 Supported Platforms
- **🎬 YouTube**: Videos, playlists, audio extraction
- **📷 Instagram**: Reels, posts, profile pictures  
- **🐦 Twitter/X**: Videos, profile pictures, post images
- **📘 Facebook**: Reels, videos, post images
- **🎵 Spotify**: Songs, audio content

### 🎯 Content Types
- **🎬 Video Downloads**: Multiple quality options (720p, 1080p, 480p, 360p)
- **🖼️ Image Downloads**: High-quality image downloads
- **🎵 Audio Downloads**: Various audio formats (MP3, FLAC, WAV, M4A)

### 🔧 Advanced Features
- **Quality Selection**: Choose from multiple video quality options
- **Format Selection**: Popular video (MP4, MKV, AVI, MOV) and audio formats
- **Playlist Support**: Download entire playlists or specific videos
- **Progress Tracking**: Real-time download progress with time estimation
- **Error Handling**: Comprehensive error reporting system
- **Report System**: Built-in complaint/report functionality

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Telegram Bot Token

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/pizaryt1/bot1.git
   cd bot1
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or using the included dependencies:
   ```bash
   pip install python-telegram-bot yt-dlp requests aiofiles pillow
   ```

3. **Configure the bot**
   
   Edit `config.py` with your bot token:
   ```python
   TELEGRAM_TOKEN = "YOUR_BOT_TOKEN_HERE"
   ERROR_CHANNEL_ID = -1234567890  # Your error reporting channel
   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

5. **Test the structure** (optional)
   ```bash
   python test_bot.py
   ```

## 🎮 How to Use

### 1. Start the Bot
Send `/start` to begin and select your preferred language.

### 2. Choose Content Type
Select from the main menu:
- 🎬 Download Video
- 🖼️ Download Image  
- 🎵 Download Audio
- ℹ️ Bot Info
- ⚠️ Report Issue

### 3. Select Platform
Choose the platform where your content is hosted (YouTube, Instagram, etc.).

### 4. Send Link
Paste the URL of the content you want to download.

### 5. Choose Quality/Format
Select your preferred quality and format options.

### 6. Download
Wait for the bot to process and send your media!

## 🏗️ Bot Structure

```
bot1/
├── bot.py           # Main bot application
├── config.py        # Configuration settings
├── test_bot.py      # Structure validation tests
├── pyproject.toml   # Project dependencies
└── README.md        # This file
```

## ⚙️ Configuration

### Environment Variables
- `TELEGRAM_TOKEN`: Your Telegram bot token
- `ERROR_CHANNEL_ID`: Channel ID for error reporting

### Supported Formats
- **Video**: MP4, MKV, AVI, MOV
- **Audio**: MP3, FLAC, WAV, M4A
- **Quality**: 720p, 1080p, 480p, 360p, Best, Worst

## 🛠️ Development

### Testing
Run the validation tests:
```bash
python test_bot.py
```

### Adding New Platforms
1. Add platform info to `SUPPORTED_PLATFORMS` in `config.py`
2. Implement platform-specific download logic in `bot.py`
3. Add appropriate URL validation

### Error Handling
- All errors are automatically logged
- Critical errors are sent to the configured error channel
- User-friendly error messages in both languages

## 🔒 Security Features

- Input validation for all URLs
- File size limits (50MB for Telegram)
- Temporary file handling with automatic cleanup
- Error reporting to designated channel

## 📋 Commands

- `/start` - Start the bot and select language
- `/menu` - Show the main menu

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- Use the built-in report system in the bot
- Check the error channel for technical issues
- Review the test script for structural problems

## 🔄 Updates

The bot is actively maintained with regular updates for:
- New platform support
- Enhanced download capabilities  
- Bug fixes and improvements
- Security updates

---

**Developed by 7MOD** 🚀