#!/usr/bin/env python3
"""
Test script for the refactored scraper library.
This script makes it easy to test our new implementation with a specified website.
"""

import sys
import os

# Add the parent directory to the Python path so we can import modules properly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scrapers.scraper_69shu import Scraper69Shu
from src.scrapers.scraper_ximalaya import ScraperXimalaya
from src.scrapers.scraper_syosetu import ScraperSyosetu
from src.adapters.text_file_adapter import TextFileAdapter
from src.adapters.audio_file_adapter import AudioFileAdapter
from src.components.progress_reporter import ConsoleProgressReporter
from src.coordinator import NovelScraperCoordinator, AudioNovelScraperCoordinator

def test_69shu():
    """Test the 69shu.net scraper"""
    print("Testing 69shu.net scraper...")
    
    # Create a test URL
    url = "https://69shu.net/1/1426_30/#all"
    
    # Initialize components
    scraper = Scraper69Shu()
    adapter = TextFileAdapter({"file_path": "test_69shu_novel.txt"})
    progress_reporter = ConsoleProgressReporter()
    
    # Create coordinator
    coordinator = NovelScraperCoordinator(
        scraper=scraper,
        adapter=adapter,
        progress_reporter=progress_reporter,
        max_threads=2,
        delay_between_requests=1.0
    )
    
    # Limit to 3 chapters for testing
    result = coordinator.scrape_novel(url, max_chapters=3)
    
    # Print result
    print("\nTest result:", result)
    return result

def test_syosetu():
    """Test the Syosetu scraper"""
    print("Testing Syosetu scraper...")
    
    # Create a test URL
    url = "https://ncode.syosetu.com/n2267be/"  # Re:Zero
    
    # Initialize components
    scraper = ScraperSyosetu()
    adapter = TextFileAdapter({"file_path": "test_syosetu_novel.txt"})
    progress_reporter = ConsoleProgressReporter()
    
    # Create coordinator
    coordinator = NovelScraperCoordinator(
        scraper=scraper,
        adapter=adapter,
        progress_reporter=progress_reporter,
        max_threads=2,
        delay_between_requests=1.0
    )
    
    # Limit to 3 chapters for testing
    result = coordinator.scrape_novel(url, max_chapters=3)
    
    # Print result
    print("\nTest result:", result)
    return result

def test_ximalaya():
    """Test the ximalaya.com scraper"""
    print("Testing ximalaya.com scraper...")
    
    # Create a test URL
    url = "https://www.ximalaya.com/album/57367509/"
    
    # Initialize components
    scraper = ScraperXimalaya()
    adapter = AudioFileAdapter({"folder_path": "test_ximalaya_audio", "file_extension": "m4a"})
    progress_reporter = ConsoleProgressReporter()
    
    # Create coordinator
    coordinator = AudioNovelScraperCoordinator(
        scraper=scraper,
        adapter=adapter,
        progress_reporter=progress_reporter,
        max_threads=2,
        delay_between_requests=1.0
    )
    
    # Limit to 1 audio file for testing
    result = coordinator.scrape_novel(url, max_chapters=1)
    
    # Print result
    print("\nTest result:", result)
    return result

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        if test_name == "69shu":
            test_69shu()
        elif test_name == "syosetu":
            test_syosetu()
        elif test_name == "ximalaya":
            test_ximalaya()
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: 69shu, syosetu, ximalaya")
    else:
        print("Testing Syosetu scraper by default...")
        test_syosetu()