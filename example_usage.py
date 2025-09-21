#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example usage of the Telegram Media Downloader Bot components
"""

from downloaders import PlatformDownloader, YouTubeDownloader, get_downloader

def test_platform_detection():
    """Test URL platform detection"""
    test_urls = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "youtube"),
        ("https://youtu.be/dQw4w9WgXcQ", "youtube"),
        ("https://www.instagram.com/p/ABC123/", "instagram"),
        ("https://twitter.com/user/status/123", "twitter"),
        ("https://x.com/user/status/123", "twitter"),
        ("https://www.facebook.com/watch?v=123", "facebook"),
        ("https://open.spotify.com/track/123", "spotify"),
    ]
    
    print("🔍 Testing Platform Detection:")
    for url, expected in test_urls:
        detected = PlatformDownloader.get_platform_from_url(url)
        status = "✅" if detected == expected else "❌"
        print(f"{status} {url} -> {detected} (expected: {expected})")

def test_url_validation():
    """Test URL validation"""
    test_cases = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "youtube", True),
        ("https://invalid-url.com", "youtube", False),
        ("https://www.instagram.com/p/ABC123/", "instagram", True),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "instagram", False),
    ]
    
    print("\n✅ Testing URL Validation:")
    for url, platform, expected in test_cases:
        result = PlatformDownloader.validate_url(url, platform)
        status = "✅" if result == expected else "❌"
        print(f"{status} {url} for {platform} -> {result} (expected: {expected})")

def test_downloader_factory():
    """Test downloader factory"""
    platforms = ['youtube', 'instagram', 'twitter', 'facebook', 'spotify']
    
    print("\n🏭 Testing Downloader Factory:")
    for platform in platforms:
        downloader = get_downloader(platform)
        status = "✅" if downloader else "❌"
        print(f"{status} {platform} -> {downloader.__name__ if downloader else None}")

def main():
    """Run all tests"""
    print("🧪 Testing Telegram Media Downloader Components\n")
    
    test_platform_detection()
    test_url_validation()
    test_downloader_factory()
    
    print("\n✨ Component testing completed!")

if __name__ == "__main__":
    main()