#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to validate bot structure without running
"""

import sys
import importlib.util

def test_imports():
    """Test if all imports work correctly"""
    try:
        # Test telegram imports
        import telegram
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, BotCommand
        from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
        print("✅ Telegram imports successful")
        
        # Test yt-dlp import
        import yt_dlp
        print("✅ yt-dlp import successful")
        
        # Test config import
        from config import TELEGRAM_TOKEN, ERROR_CHANNEL_ID, SUPPORTED_PLATFORMS
        print("✅ Config import successful")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_bot_class():
    """Test bot class structure"""
    try:
        # Import the bot module
        import bot
        
        # Check if TelegramDownloaderBot class exists
        if hasattr(bot, 'TelegramDownloaderBot'):
            print("✅ TelegramDownloaderBot class exists")
            
            # Try to instantiate it
            bot_instance = bot.TelegramDownloaderBot()
            print("✅ TelegramDownloaderBot can be instantiated")
            return True
        else:
            print("❌ TelegramDownloaderBot class not found")
            return False
            
    except Exception as e:
        print(f"❌ Bot class test error: {e}")
        return False

def test_config():
    """Test configuration"""
    try:
        from config import TELEGRAM_TOKEN, ERROR_CHANNEL_ID, SUPPORTED_PLATFORMS
        
        # Check token format
        if TELEGRAM_TOKEN and ':' in TELEGRAM_TOKEN:
            print("✅ Telegram token format looks correct")
        else:
            print("❌ Invalid telegram token format")
            return False
            
        # Check error channel ID
        if isinstance(ERROR_CHANNEL_ID, int) and ERROR_CHANNEL_ID < 0:
            print("✅ Error channel ID format correct")
        else:
            print("❌ Invalid error channel ID format")
            return False
            
        # Check platforms
        if isinstance(SUPPORTED_PLATFORMS, dict) and len(SUPPORTED_PLATFORMS) > 0:
            print("✅ Supported platforms configured")
        else:
            print("❌ Supported platforms not configured")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Config test error: {e}")
        return False

def test_yt_dlp():
    """Test yt-dlp functionality"""
    try:
        import yt_dlp
        
        # Test yt-dlp initialization
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("✅ yt-dlp initialized successfully")
            
        return True
        
    except Exception as e:
        print(f"❌ yt-dlp test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Telegram Media Downloader Bot Structure\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Bot Class Test", test_bot_class), 
        ("Config Test", test_config),
        ("yt-dlp Test", test_yt_dlp),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
        
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bot structure is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())