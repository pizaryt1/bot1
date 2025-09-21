#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Media Downloader Bot
Downloads media from YouTube, Instagram, Twitter, Facebook, and Spotify
"""

import asyncio
import logging
import os
import tempfile
import traceback
from datetime import datetime
from typing import Dict, Optional, Tuple

import yt_dlp
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    Bot, BotCommand
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)

from config import (
    TELEGRAM_TOKEN, ERROR_CHANNEL_ID, SUPPORTED_PLATFORMS,
    VIDEO_FORMATS, AUDIO_FORMATS, VIDEO_QUALITIES
)
from downloaders import (
    PlatformDownloader, YouTubeDownloader, 
    get_downloader
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# User sessions to track language and state
user_sessions: Dict[int, Dict] = {}

# Language texts
MESSAGES = {
    'ar': {
        'welcome': """
🤖 مرحباً بك في بوت تحميل الوسائط!

يمكنني تحميل المحتوى من:
🎬 يوتيوب (فيديو، قوائم تشغيل، صوت)
📷 انستقرام (ريلز، منشورات، صور بروفايل)
🐦 تويتر (فيديو، صور بروفايل، صور منشورات)
📘 فيسبوك (ريلز، فيديو، صور منشورات)
🎵 سبوتيفاي (أغاني، صوتيات)

اختر اللغة المفضلة:
        """,
        'main_menu': '📋 القائمة الرئيسية',
        'download_video': '🎬 تحميل فيديو',
        'download_image': '🖼️ تحميل صورة', 
        'download_audio': '🎵 تحميل صوت',
        'bot_info': 'ℹ️ شرح البوت',
        'report_issue': '⚠️ شكوى أو إبلاغ',
        'back': '⬅️ رجوع',
        'choose_platform': 'اختر المنصة:',
        'send_link': 'أرسل الرابط من المنصة المختارة:',
        'processing': '⏳ جاري المعالجة...',
        'invalid_link': '❌ رابط غير صالح، يرجى إرسال رابط صحيح.',
        'error_occurred': '❌ حدث خطأ أثناء المعالجة.',
        'download_complete': '✅ تم التحميل بنجاح!',
        'bot_explanation': """
🤖 شرح البوت:

هذا البوت يساعدك في تحميل المحتوى من منصات مختلفة:

🎬 يوتيوب:
- تحميل فيديو مفرد
- تحميل قائمة تشغيل كاملة أو جزء منها
- تحميل الصوت فقط

📷 انستقرام:
- تحميل ريلز
- تحميل منشورات (صور/فيديو)
- تحميل صور البروفايل

🐦 تويتر/X:
- تحميل فيديوهات
- تحميل صور المنشورات
- تحميل صور البروفايل

📘 فيسبوك:
- تحميل ريلز
- تحميل فيديوهات
- تحميل صور المنشورات

🎵 سبوتيفاي:
- تحميل الأغاني
- تحميل الصوتيات

✨ المميزات:
- اختيار الجودة (للفيديو)
- اختيار الصيغة
- شريط التقدم
- دعم قوائم التشغيل

📝 طريقة الاستخدام:
1. اختر نوع المحتوى
2. اختر المنصة
3. أرسل الرابط
4. اختر الجودة والصيغة
5. انتظر التحميل
        """,
        'report_sent': '✅ تم إرسال البلاغ بنجاح!',
        'send_report': 'اكتب شكواك أو بلاغك:',
        'cancelled': '❌ تم الإلغاء.',
    },
    'en': {
        'welcome': """
🤖 Welcome to the Media Downloader Bot!

I can download content from:
🎬 YouTube (videos, playlists, audio)
📷 Instagram (reels, posts, profile pictures)
🐦 Twitter (videos, profile pictures, post images)
📘 Facebook (reels, videos, post images)
🎵 Spotify (songs, audio)

Choose your preferred language:
        """,
        'main_menu': '📋 Main Menu',
        'download_video': '🎬 Download Video',
        'download_image': '🖼️ Download Image',
        'download_audio': '🎵 Download Audio',
        'bot_info': 'ℹ️ Bot Info',
        'report_issue': '⚠️ Report Issue',
        'back': '⬅️ Back',
        'choose_platform': 'Choose platform:',
        'send_link': 'Send the link from the selected platform:',
        'processing': '⏳ Processing...',
        'invalid_link': '❌ Invalid link, please send a valid link.',
        'error_occurred': '❌ An error occurred during processing.',
        'download_complete': '✅ Download completed successfully!',
        'bot_explanation': """
🤖 Bot Explanation:

This bot helps you download content from various platforms:

🎬 YouTube:
- Download single video
- Download complete or partial playlists
- Download audio only

📷 Instagram:
- Download reels
- Download posts (images/videos)
- Download profile pictures

🐦 Twitter/X:
- Download videos
- Download post images
- Download profile pictures

📘 Facebook:
- Download reels
- Download videos
- Download post images

🎵 Spotify:
- Download songs
- Download audio

✨ Features:
- Quality selection (for videos)
- Format selection
- Progress bar
- Playlist support

📝 How to use:
1. Choose content type
2. Choose platform
3. Send the link
4. Choose quality and format
5. Wait for download
        """,
        'report_sent': '✅ Report sent successfully!',
        'send_report': 'Write your complaint or report:',
        'cancelled': '❌ Cancelled.',
    }
}

class TelegramDownloaderBot:
    def __init__(self):
        self.application = None
        
    async def send_error_to_channel(self, error_msg: str, user_id: int = None):
        """Send error message to the error reporting channel"""
        try:
            bot = Bot(token=TELEGRAM_TOKEN)
            error_text = f"🚨 Bot Error Report\n\n"
            error_text += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            if user_id:
                error_text += f"User ID: {user_id}\n"
            error_text += f"Error: {error_msg}"
            
            await bot.send_message(chat_id=ERROR_CHANNEL_ID, text=error_text)
        except Exception as e:
            logger.error(f"Failed to send error to channel: {e}")

    def get_text(self, user_id: int, key: str) -> str:
        """Get text in user's language"""
        lang = user_sessions.get(user_id, {}).get('language', 'en')
        return MESSAGES.get(lang, MESSAGES['en']).get(key, key)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        user_id = update.effective_user.id
        
        # Initialize user session
        if user_id not in user_sessions:
            user_sessions[user_id] = {}
            
        # Language selection keyboard
        keyboard = [
            [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")],
            [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            MESSAGES['en']['welcome'], 
            reply_markup=reply_markup
        )

    async def language_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle language selection"""
        query = update.callback_query
        user_id = query.from_user.id
        
        if query.data == "lang_ar":
            user_sessions[user_id]['language'] = 'ar'
        elif query.data == "lang_en":
            user_sessions[user_id]['language'] = 'en'
            
        await query.answer()
        await self.show_main_menu(query, user_id)

    async def show_main_menu(self, query_or_update, user_id: int):
        """Show the main menu"""
        keyboard = [
            [InlineKeyboardButton(
                self.get_text(user_id, 'download_video'), 
                callback_data="menu_video"
            )],
            [InlineKeyboardButton(
                self.get_text(user_id, 'download_image'), 
                callback_data="menu_image"
            )],
            [InlineKeyboardButton(
                self.get_text(user_id, 'download_audio'), 
                callback_data="menu_audio"
            )],
            [InlineKeyboardButton(
                self.get_text(user_id, 'bot_info'), 
                callback_data="bot_info"
            )],
            [InlineKeyboardButton(
                self.get_text(user_id, 'report_issue'), 
                callback_data="report_issue"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = self.get_text(user_id, 'main_menu')
        
        if hasattr(query_or_update, 'edit_message_text'):
            await query_or_update.edit_message_text(text, reply_markup=reply_markup)
        else:
            await query_or_update.message.reply_text(text, reply_markup=reply_markup)

    async def platform_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle platform selection for downloads"""
        query = update.callback_query
        user_id = query.from_user.id
        
        # Extract content type from callback data
        content_type = query.data.split('_')[1]  # video, image, or audio
        user_sessions[user_id]['content_type'] = content_type
        
        # Create platform buttons based on content type
        keyboard = []
        for platform_id, platform_info in SUPPORTED_PLATFORMS.items():
            lang = user_sessions[user_id].get('language', 'en')
            platform_name = platform_info[f'name_{lang}']
            emoji = platform_info['emoji']
            
            keyboard.append([InlineKeyboardButton(
                f"{emoji} {platform_name}",
                callback_data=f"platform_{platform_id}"
            )])
        
        # Add back button
        keyboard.append([InlineKeyboardButton(
            self.get_text(user_id, 'back'), 
            callback_data="back_main"
        )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = self.get_text(user_id, 'choose_platform')
        
        await query.answer()
        await query.edit_message_text(text, reply_markup=reply_markup)

    async def platform_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle when a platform is selected"""
        query = update.callback_query
        user_id = query.from_user.id
        
        platform = query.data.split('_')[1]
        user_sessions[user_id]['platform'] = platform
        user_sessions[user_id]['waiting_for_link'] = True
        
        await query.answer()
        await query.edit_message_text(self.get_text(user_id, 'send_link'))

    async def bot_info_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot information"""
        query = update.callback_query
        user_id = query.from_user.id
        
        keyboard = [[InlineKeyboardButton(
            self.get_text(user_id, 'back'), 
            callback_data="back_main"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.answer()
        await query.edit_message_text(
            self.get_text(user_id, 'bot_explanation'),
            reply_markup=reply_markup
        )

    async def report_issue_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle report issue button"""
        query = update.callback_query
        user_id = query.from_user.id
        
        user_sessions[user_id]['waiting_for_report'] = True
        
        keyboard = [[InlineKeyboardButton(
            self.get_text(user_id, 'back'), 
            callback_data="back_main"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.answer()
        await query.edit_message_text(
            self.get_text(user_id, 'send_report'),
            reply_markup=reply_markup
        )

    async def back_to_main(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Go back to main menu"""
        query = update.callback_query
        user_id = query.from_user.id
        
        # Clear session state
        user_sessions[user_id] = {
            'language': user_sessions[user_id].get('language', 'en')
        }
        
        await query.answer()
        await self.show_main_menu(query, user_id)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (links, reports, etc.)"""
        user_id = update.effective_user.id
        text = update.message.text
        
        if user_id not in user_sessions:
            await self.start(update, context)
            return
            
        session = user_sessions[user_id]
        
        try:
            if session.get('waiting_for_report'):
                # Handle report submission
                await self.handle_report(update, context, text)
            elif session.get('waiting_for_link'):
                # Handle link submission
                await self.handle_link(update, context, text)
            else:
                # Default: show main menu
                await self.show_main_menu(update, user_id)
                
        except Exception as e:
            error_msg = f"Error in handle_message: {str(e)}\n{traceback.format_exc()}"
            await self.send_error_to_channel(error_msg, user_id)
            await update.message.reply_text(self.get_text(user_id, 'error_occurred'))

    async def handle_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Handle report submission"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        # Send report to error channel
        report_text = f"📝 User Report\n\n"
        report_text += f"User: @{username} (ID: {user_id})\n"
        report_text += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report_text += f"Report: {text}"
        
        try:
            bot = Bot(token=TELEGRAM_TOKEN)
            await bot.send_message(chat_id=ERROR_CHANNEL_ID, text=report_text)
            
            # Clear session state
            user_sessions[user_id]['waiting_for_report'] = False
            
            await update.message.reply_text(self.get_text(user_id, 'report_sent'))
            await self.show_main_menu(update, user_id)
            
        except Exception as e:
            error_msg = f"Failed to send report: {str(e)}"
            await self.send_error_to_channel(error_msg, user_id)
            await update.message.reply_text(self.get_text(user_id, 'error_occurred'))

    async def handle_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE, link: str):
        """Handle link processing and downloading"""
        user_id = update.effective_user.id
        session = user_sessions[user_id]
        
        # Send processing message
        processing_msg = await update.message.reply_text(
            self.get_text(user_id, 'processing')
        )
        
        try:
            # Basic link validation
            if not any(domain in link.lower() for domain in ['youtube.', 'youtu.be', 'instagram.', 'twitter.', 'x.com', 'facebook.', 'spotify.']):
                await processing_msg.edit_text(self.get_text(user_id, 'invalid_link'))
                return
            
            # For now, we'll implement a basic download using yt-dlp
            # This is a simplified version - full implementation would need
            # platform-specific handling
            await self.start_download(processing_msg, user_id, session)
            
        except Exception as e:
            error_msg = f"Error in handle_link: {str(e)}\n{traceback.format_exc()}"
            await self.send_error_to_channel(error_msg, user_id)
            await processing_msg.edit_text(self.get_text(user_id, 'error_occurred'))
        finally:
            # Clear session state
            session['waiting_for_link'] = False

    async def handle_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE, link: str):
        """Handle link processing and downloading"""
        user_id = update.effective_user.id
        session = user_sessions[user_id]
        
        # Send processing message
        processing_msg = await update.message.reply_text(
            self.get_text(user_id, 'processing')
        )
        
        try:
            # Detect platform from URL
            detected_platform = PlatformDownloader.get_platform_from_url(link)
            expected_platform = session.get('platform')
            
            # Validate URL
            if not detected_platform:
                await processing_msg.edit_text(self.get_text(user_id, 'invalid_link'))
                return
                
            if detected_platform != expected_platform:
                await processing_msg.edit_text(
                    f"❌ URL doesn't match selected platform. Expected {expected_platform}, got {detected_platform}"
                )
                return
            
            # Validate URL format
            if not PlatformDownloader.validate_url(link, detected_platform):
                await processing_msg.edit_text(self.get_text(user_id, 'invalid_link'))
                return
            
            # Store URL in session
            session['url'] = link
            session['platform'] = detected_platform
            
            # For video downloads, show quality/format selection
            content_type = session.get('content_type')
            
            if content_type == 'video' and detected_platform == 'youtube':
                await self.show_quality_selection(processing_msg, user_id, link)
            elif content_type == 'audio' and detected_platform == 'youtube':
                await self.show_audio_format_selection(processing_msg, user_id)
            else:
                # Direct download for other platforms/types
                await self.start_download(processing_msg, user_id, session)
            
        except Exception as e:
            error_msg = f"Error in handle_link: {str(e)}\n{traceback.format_exc()}"
            await self.send_error_to_channel(error_msg, user_id)
            await processing_msg.edit_text(self.get_text(user_id, 'error_occurred'))
        finally:
            # Clear waiting state
            session['waiting_for_link'] = False

    async def show_quality_selection(self, message, user_id: int, url: str):
        """Show quality selection for video downloads"""
        try:
            # Get video info
            video_info = YouTubeDownloader.get_video_info(url)
            available_qualities = YouTubeDownloader.get_available_qualities(video_info['formats'])
            
            if video_info.get('is_playlist'):
                # Handle playlist
                await self.show_playlist_options(message, user_id, video_info)
                return
            
            # Create quality selection keyboard
            keyboard = []
            for quality in available_qualities[:6]:  # Limit to 6 options
                keyboard.append([InlineKeyboardButton(
                    f"📺 {quality}",
                    callback_data=f"quality_{quality}"
                )])
            
            keyboard.append([InlineKeyboardButton(
                self.get_text(user_id, 'back'), 
                callback_data="back_main"
            )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            lang = user_sessions[user_id].get('language', 'en')
            text = "اختر الجودة:" if lang == 'ar' else "Choose quality:"
            
            await message.edit_text(text, reply_markup=reply_markup)
            
        except Exception as e:
            error_msg = f"Error in show_quality_selection: {str(e)}"
            await self.send_error_to_channel(error_msg, user_id)
            await message.edit_text(self.get_text(user_id, 'error_occurred'))

    async def show_audio_format_selection(self, message, user_id: int):
        """Show audio format selection"""
        keyboard = []
        for fmt in AUDIO_FORMATS:
            keyboard.append([InlineKeyboardButton(
                f"🎵 {fmt.upper()}",
                callback_data=f"audio_format_{fmt}"
            )])
        
        keyboard.append([InlineKeyboardButton(
            self.get_text(user_id, 'back'), 
            callback_data="back_main"
        )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        lang = user_sessions[user_id].get('language', 'en')
        text = "اختر صيغة الصوت:" if lang == 'ar' else "Choose audio format:"
        
        await message.edit_text(text, reply_markup=reply_markup)

    async def show_video_format_selection(self, message, user_id: int):
        """Show video format selection"""
        keyboard = []
        for fmt in VIDEO_FORMATS:
            keyboard.append([InlineKeyboardButton(
                f"🎬 {fmt.upper()}",
                callback_data=f"video_format_{fmt}"
            )])
        
        keyboard.append([InlineKeyboardButton(
            self.get_text(user_id, 'back'), 
            callback_data="back_main"
        )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        lang = user_sessions[user_id].get('language', 'en')
        text = "اختر صيغة الفيديو:" if lang == 'ar' else "Choose video format:"
        
        await message.edit_text(text, reply_markup=reply_markup)

    async def show_playlist_options(self, message, user_id: int, video_info: Dict):
        """Show playlist download options"""
        entry_count = len(video_info.get('entries', []))
        
        keyboard = [
            [InlineKeyboardButton(
                f"📋 تحميل جميع المقاطع ({entry_count})" if user_sessions[user_id].get('language') == 'ar' 
                else f"📋 Download All Videos ({entry_count})",
                callback_data="playlist_all"
            )],
            [InlineKeyboardButton(
                "🎯 تحميل مقاطع محددة" if user_sessions[user_id].get('language') == 'ar' 
                else "🎯 Download Specific Videos",
                callback_data="playlist_specific"
            )],
            [InlineKeyboardButton(
                self.get_text(user_id, 'back'), 
                callback_data="back_main"
            )]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        lang = user_sessions[user_id].get('language', 'en')
        title = video_info.get('title', 'Unknown Playlist')
        text = f"📋 قائمة تشغيل: {title}\n\nعدد المقاطع: {entry_count}\n\nاختر خيار التحميل:" if lang == 'ar' else f"📋 Playlist: {title}\n\nVideo count: {entry_count}\n\nChoose download option:"
        
        await message.edit_text(text, reply_markup=reply_markup)

    async def start_download(self, message, user_id: int, session: Dict):
        """Start the actual download process"""
        try:
            url = session['url']
            platform = session['platform']
            content_type = session['content_type']
            quality = session.get('quality', 'best')
            format_type = session.get('format', 'mp4' if content_type == 'video' else 'mp3')
            
            # Update message to show download started
            lang = user_sessions[user_id].get('language', 'en')
            downloading_text = "⬇️ جاري التحميل..." if lang == 'ar' else "⬇️ Downloading..."
            await message.edit_text(downloading_text)
            
            # Get appropriate downloader
            downloader_class = get_downloader(platform)
            if not downloader_class:
                raise Exception(f"No downloader available for {platform}")
            
            # Download based on content type and platform
            with tempfile.TemporaryDirectory() as temp_dir:
                if platform == 'youtube':
                    if content_type == 'audio':
                        file_path, info = YouTubeDownloader.download_audio(url, format_type, temp_dir)
                    else:
                        file_path, info = YouTubeDownloader.download_video(url, quality, format_type, temp_dir)
                else:
                    # Other platforms use generic download
                    file_path, info = downloader_class.download_content(url, temp_dir)
                
                # Check file size (Telegram limit is 50MB for bots)
                file_size = os.path.getsize(file_path)
                if file_size > 50 * 1024 * 1024:  # 50MB
                    size_mb = file_size / (1024 * 1024)
                    error_text = f"❌ الملف كبير جداً ({size_mb:.1f}MB). الحد الأقصى 50MB" if lang == 'ar' else f"❌ File too large ({size_mb:.1f}MB). Max 50MB"
                    await message.edit_text(error_text)
                    return
                
                # Send file based on content type
                title = info.get('title', 'Downloaded content')
                
                with open(file_path, 'rb') as file:
                    if content_type == 'audio':
                        await message.reply_audio(
                            file, 
                            caption=title[:1024],  # Telegram caption limit
                            title=title
                        )
                    elif content_type == 'video':
                        await message.reply_video(
                            file, 
                            caption=title[:1024],
                            supports_streaming=True
                        )
                    else:  # image
                        await message.reply_photo(file, caption=title[:1024])
                
                # Update message to show completion
                complete_text = "✅ تم التحميل بنجاح!" if lang == 'ar' else "✅ Download completed successfully!"
                await message.edit_text(complete_text)
                
        except Exception as e:
            error_msg = f"Download error: {str(e)}"
            await self.send_error_to_channel(error_msg, user_id)
            
            lang = user_sessions[user_id].get('language', 'en')
            error_text = "❌ فشل التحميل. يرجى المحاولة مرة أخرى." if lang == 'ar' else "❌ Download failed. Please try again."
            await message.edit_text(error_text)

    async def callback_query_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all callback queries"""
        query = update.callback_query
        data = query.data
        user_id = query.from_user.id
        
        try:
            if data.startswith("lang_"):
                await self.language_callback(update, context)
            elif data.startswith("menu_"):
                await self.platform_selection(update, context)
            elif data.startswith("platform_"):
                await self.platform_selected(update, context)
            elif data.startswith("quality_"):
                await self.quality_selected(update, context)
            elif data.startswith("video_format_"):
                await self.video_format_selected(update, context)
            elif data.startswith("audio_format_"):
                await self.audio_format_selected(update, context)
            elif data.startswith("playlist_"):
                await self.playlist_option_selected(update, context)
            elif data == "bot_info":
                await self.bot_info_callback(update, context)
            elif data == "report_issue":
                await self.report_issue_callback(update, context)
            elif data == "back_main":
                await self.back_to_main(update, context)
                
        except Exception as e:
            error_msg = f"Error in callback_query_handler: {str(e)}\n{traceback.format_exc()}"
            await self.send_error_to_channel(error_msg, query.from_user.id)
            await query.answer("❌ حدث خطأ / Error occurred")

    async def quality_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle quality selection"""
        query = update.callback_query
        user_id = query.from_user.id
        
        quality = query.data.split('_')[1]
        user_sessions[user_id]['quality'] = quality
        
        await query.answer()
        
        # Show format selection for video
        await self.show_video_format_selection(query, user_id)

    async def video_format_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle video format selection"""
        query = update.callback_query
        user_id = query.from_user.id
        
        format_type = query.data.split('_')[2]
        user_sessions[user_id]['format'] = format_type
        
        await query.answer()
        
        # Start download
        session = user_sessions[user_id]
        await self.start_download(query, user_id, session)

    async def audio_format_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle audio format selection"""
        query = update.callback_query
        user_id = query.from_user.id
        
        format_type = query.data.split('_')[2]
        user_sessions[user_id]['format'] = format_type
        
        await query.answer()
        
        # Start download
        session = user_sessions[user_id]
        await self.start_download(query, user_id, session)

    async def playlist_option_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle playlist download option selection"""
        query = update.callback_query
        user_id = query.from_user.id
        
        option = query.data.split('_')[1]
        user_sessions[user_id]['playlist_option'] = option
        
        await query.answer()
        
        if option == 'all':
            # Download all videos in playlist
            await self.show_quality_selection_for_playlist(query, user_id)
        else:
            # Show specific video selection (simplified for now)
            lang = user_sessions[user_id].get('language', 'en')
            text = "⚠️ خيار التحميل المحدد غير متاح حالياً. يرجى اختيار تحميل جميع المقاطع." if lang == 'ar' else "⚠️ Specific video selection not available yet. Please choose download all."
            await query.edit_message_text(text)

    async def show_quality_selection_for_playlist(self, query, user_id: int):
        """Show quality selection for playlist downloads"""
        # For playlists, we'll use standard quality options
        keyboard = []
        for quality in VIDEO_QUALITIES[:4]:  # Limit options
            keyboard.append([InlineKeyboardButton(
                f"📺 {quality}",
                callback_data=f"playlist_quality_{quality}"
            )])
        
        keyboard.append([InlineKeyboardButton(
            self.get_text(user_id, 'back'), 
            callback_data="back_main"
        )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        lang = user_sessions[user_id].get('language', 'en')
        text = "اختر الجودة للقائمة:" if lang == 'ar' else "Choose quality for playlist:"
        
        await query.edit_message_text(text, reply_markup=reply_markup)

    async def setup_bot_commands(self):
        """Set up bot commands"""
        commands = [
            BotCommand("start", "Start the bot / بدء البوت"),
            BotCommand("menu", "Show main menu / القائمة الرئيسية"),
        ]
        
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.set_my_commands(commands)

    async def post_init(self, application: Application):
        """Post initialization setup"""
        await self.setup_bot_commands()

    def run(self):
        """Run the bot"""
        # Create application
        self.application = Application.builder().token(TELEGRAM_TOKEN).post_init(self.post_init).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("menu", self.start))
        self.application.add_handler(CallbackQueryHandler(self.callback_query_handler))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Start bot
        logger.info("Starting Telegram Media Downloader Bot...")
        self.application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    bot = TelegramDownloaderBot()
    bot.run()
