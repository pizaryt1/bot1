#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Platform-specific downloaders for the Telegram Media Downloader Bot
"""

import os
import tempfile
import re
from typing import Dict, List, Optional, Tuple
import yt_dlp
import requests

class PlatformDownloader:
    """Base class for platform-specific downloaders"""
    
    @staticmethod
    def get_platform_from_url(url: str) -> Optional[str]:
        """Detect platform from URL"""
        url = url.lower()
        
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        elif 'instagram.com' in url:
            return 'instagram'
        elif 'twitter.com' in url or 'x.com' in url:
            return 'twitter'
        elif 'facebook.com' in url or 'fb.watch' in url:
            return 'facebook'
        elif 'spotify.com' in url:
            return 'spotify'
        
        return None
    
    @staticmethod
    def validate_url(url: str, platform: str) -> bool:
        """Validate URL for specific platform"""
        if platform == 'youtube':
            return bool(re.match(r'https?://(www\.)?(youtube\.com|youtu\.be)/', url))
        elif platform == 'instagram':
            return bool(re.match(r'https?://(www\.)?instagram\.com/', url))
        elif platform == 'twitter':
            return bool(re.match(r'https?://(www\.)?(twitter\.com|x\.com)/', url))
        elif platform == 'facebook':
            return bool(re.match(r'https?://(www\.)?(facebook\.com|fb\.watch)/', url))
        elif platform == 'spotify':
            return bool(re.match(r'https?://(www\.)?spotify\.com/', url))
        
        return False

class YouTubeDownloader:
    """YouTube-specific downloader"""
    
    @staticmethod
    def get_video_info(url: str) -> Dict:
        """Get video information without downloading"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
        return {
            'title': info.get('title', 'Unknown'),
            'duration': info.get('duration', 0),
            'formats': info.get('formats', []),
            'is_playlist': 'entries' in info,
            'entries': info.get('entries', []) if 'entries' in info else None
        }
    
    @staticmethod
    def get_available_qualities(formats: List[Dict]) -> List[str]:
        """Extract available video qualities"""
        qualities = set()
        
        for fmt in formats:
            if fmt.get('height'):
                qualities.add(f"{fmt['height']}p")
        
        # Add standard options
        qualities.update(['best', 'worst'])
        
        # Sort by quality (highest first)
        quality_order = ['1080p', '720p', '480p', '360p', '240p', '144p', 'best', 'worst']
        return [q for q in quality_order if q in qualities]
    
    @staticmethod
    def download_video(url: str, quality: str = 'best', format_type: str = 'mp4', temp_dir: str = None) -> Tuple[str, Dict]:
        """Download YouTube video"""
        if not temp_dir:
            temp_dir = tempfile.mkdtemp()
        
        # Configure quality selector
        if quality == 'best':
            format_selector = 'best'
        elif quality == 'worst':
            format_selector = 'worst'
        else:
            height = quality.replace('p', '')
            format_selector = f'best[height<={height}]'
        
        ydl_opts = {
            'format': format_selector,
            'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
            'merge_output_format': format_type,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
        # Find the downloaded file
        files = os.listdir(temp_dir)
        if files:
            return os.path.join(temp_dir, files[0]), info
        
        raise Exception("Download failed - no file created")
    
    @staticmethod
    def download_audio(url: str, format_type: str = 'mp3', temp_dir: str = None) -> Tuple[str, Dict]:
        """Download YouTube audio"""
        if not temp_dir:
            temp_dir = tempfile.mkdtemp()
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format_type,
                'preferredquality': '192',
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
        # Find the downloaded file
        files = os.listdir(temp_dir)
        if files:
            return os.path.join(temp_dir, files[0]), info
        
        raise Exception("Download failed - no file created")

class InstagramDownloader:
    """Instagram-specific downloader"""
    
    @staticmethod
    def download_content(url: str, temp_dir: str = None) -> Tuple[str, Dict]:
        """Download Instagram content using yt-dlp"""
        if not temp_dir:
            temp_dir = tempfile.mkdtemp()
        
        ydl_opts = {
            'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
        files = os.listdir(temp_dir)
        if files:
            return os.path.join(temp_dir, files[0]), info
        
        raise Exception("Download failed - no file created")

class TwitterDownloader:
    """Twitter/X-specific downloader"""
    
    @staticmethod
    def download_content(url: str, temp_dir: str = None) -> Tuple[str, Dict]:
        """Download Twitter content using yt-dlp"""
        if not temp_dir:
            temp_dir = tempfile.mkdtemp()
        
        ydl_opts = {
            'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
        files = os.listdir(temp_dir)
        if files:
            return os.path.join(temp_dir, files[0]), info
        
        raise Exception("Download failed - no file created")

class FacebookDownloader:
    """Facebook-specific downloader"""
    
    @staticmethod
    def download_content(url: str, temp_dir: str = None) -> Tuple[str, Dict]:
        """Download Facebook content using yt-dlp"""
        if not temp_dir:
            temp_dir = tempfile.mkdtemp()
        
        ydl_opts = {
            'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
        files = os.listdir(temp_dir)
        if files:
            return os.path.join(temp_dir, files[0]), info
        
        raise Exception("Download failed - no file created")

class SpotifyDownloader:
    """Spotify-specific downloader (Note: Spotify requires special handling)"""
    
    @staticmethod
    def download_content(url: str, temp_dir: str = None) -> Tuple[str, Dict]:
        """Download Spotify content (limited functionality)"""
        # Note: Spotify downloads require special authentication and may not work
        # This is a placeholder for future implementation
        if not temp_dir:
            temp_dir = tempfile.mkdtemp()
        
        # For now, we'll try with yt-dlp but it likely won't work for Spotify
        ydl_opts = {
            'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
            files = os.listdir(temp_dir)
            if files:
                return os.path.join(temp_dir, files[0]), info
        except:
            pass
        
        raise Exception("Spotify downloads not yet fully supported")

# Downloader factory
def get_downloader(platform: str):
    """Get appropriate downloader for platform"""
    downloaders = {
        'youtube': YouTubeDownloader,
        'instagram': InstagramDownloader,
        'twitter': TwitterDownloader,
        'facebook': FacebookDownloader,
        'spotify': SpotifyDownloader,
    }
    
    return downloaders.get(platform)