"""
Novel Scraper Coordinator

This module provides a coordinator that combines scrapers and adapters
using a composition pattern, decoupling the scraping and storage logic.
"""

import logging
from typing import List, Dict, Any, Optional
import time
import sys
import os

# Add correct path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interfaces import NovelScraper, AudioNovelScraper, Adapter, ProgressReporter
from threading_utils import BatchProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("novel_coordinator")

class NovelScraperCoordinator:
    """Coordinator for novel scraping operations"""
    
    def __init__(self, 
                 scraper: NovelScraper, 
                 adapter: Adapter,
                 progress_reporter: Optional[ProgressReporter] = None,
                 max_threads: int = 6,
                 delay_between_requests: float = 1.0):
        """
        Initialize the coordinator.
        
        Args:
            scraper: The novel scraper implementation
            adapter: The adapter for processing/saving the scraped data
            progress_reporter: Optional progress reporter
            max_threads: Maximum number of threads for parallel operations
            delay_between_requests: Delay between requests to avoid overloading servers
        """
        self.scraper = scraper
        self.adapter = adapter
        self.progress_reporter = progress_reporter
        self.max_threads = max_threads
        self.delay = delay_between_requests
        self.threading_manager = BatchProcessor()
    
    def scrape_novel(self, novel_url: str, max_chapters: Optional[int] = None) -> Dict[str, Any]:
        """
        Scrape a novel and process it with the adapter.
        
        Args:
            novel_url: URL of the novel to scrape
            max_chapters: Optional limit on number of chapters to scrape
            
        Returns:
            Dictionary with results from the adapter
        """
        try:
            # Report start
            if self.progress_reporter:
                self.progress_reporter.print(f"Starting novel scraping from URL: {novel_url}")
            
            # Get novel information
            novel_info = self.scraper.get_novel_info(novel_url)
            if self.progress_reporter:
                title = novel_info.get("title", "Unknown")
                author = novel_info.get("author", "Unknown")
                self.progress_reporter.print(f"Novel: '{title}' by {author}")
            
            # Get index pages
            if self.progress_reporter:
                self.progress_reporter.print("Retrieving index pages...")
            index_pages = self.scraper.get_index_pages(novel_url)
            
            # Get chapter URLs from all index pages
            if self.progress_reporter:
                self.progress_reporter.print(f"Found {len(index_pages)} index pages")
                self.progress_reporter.print("Retrieving chapter URLs...")
            
            chapter_urls = []
            
            # Use threading for index pages if there are enough of them
            if len(index_pages) >= 3 and self.max_threads > 1:
                # Define the processing function for each index page
                def process_index(index_url: str, index: int) -> List[str]:
                    urls = self.scraper.get_chapter_urls(index_url)
                    time.sleep(self.delay)  # Be nice to the server
                    return urls
                
                # Define the chunk handler to report progress
                def chunk_handler(chunk_start: int, chunk: List[str], results: Dict[int, List[str]]) -> List[str]:
                    all_urls = []
                    for i in range(len(chunk)):
                        index = chunk_start + i
                        if index in results:
                            urls = results[index]
                            all_urls.extend(urls)
                            if self.progress_reporter:
                                self.progress_reporter.print(
                                    f"\t[{index+1}/{len(index_pages)}] Found {len(urls)} chapters"
                                )
                    return all_urls
                
                # Process index pages in parallel
                chapter_urls = self.threading_manager.process_in_parallel(
                    index_pages,
                    process_index,
                    chunk_handler,
                    min(self.max_threads, len(index_pages))
                )
            else:
                # Sequential processing for a small number of index pages
                for i, index_url in enumerate(index_pages):
                    urls = self.scraper.get_chapter_urls(index_url)
                    chapter_urls.extend(urls)
                    if self.progress_reporter:
                        self.progress_reporter.print(
                            f"\t[{i+1}/{len(index_pages)}] Found {len(urls)} chapters"
                        )
                    time.sleep(self.delay)  # Be nice to the server
            
            # Apply chapter limit if specified
            if max_chapters and max_chapters < len(chapter_urls):
                chapter_urls = chapter_urls[:max_chapters]
                if self.progress_reporter:
                    self.progress_reporter.print(
                        f"Limiting to {max_chapters} chapters (out of {len(chapter_urls)} available)"
                    )
            
            # Prepare to scrape chapters
            if self.progress_reporter:
                self.progress_reporter.print(f"Scraping {len(chapter_urls)} chapters...")
                self.progress_reporter.initialize_progress(len(chapter_urls))
            
            chapters = []
            
            # Use threading for chapters if there are enough of them
            if len(chapter_urls) >= 3 and self.max_threads > 1:
                # Define the processing function for each chapter
                def process_chapter(chapter_url: str, index: int) -> Dict[str, Any]:
                    content = self.scraper.get_chapter_content(chapter_url)
                    time.sleep(self.delay)  # Be nice to the server
                    return content
                
                # Define the chunk handler to report progress and collect results
                def chunk_handler(chunk_start: int, chunk: List[str], results: Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
                    chunk_results = []
                    for i in range(len(chunk)):
                        index = chunk_start + i
                        if index in results:
                            chunk_results.append(results[index])
                    
                    # Update progress
                    if self.progress_reporter:
                        self.progress_reporter.update_progress(len(chunk))
                        self.progress_reporter.set_description(
                            f"Scraping {chunk_start + len(chunk)}/{len(chapter_urls)} chapters"
                        )
                    
                    return chunk_results
                
                # Process chapters in parallel
                chapters = self.threading_manager.process_in_parallel(
                    chapter_urls,
                    process_chapter,
                    chunk_handler,
                    min(self.max_threads, len(chapter_urls))
                )
            else:
                # Sequential processing for a small number of chapters
                for i, chapter_url in enumerate(chapter_urls):
                    content = self.scraper.get_chapter_content(chapter_url)
                    chapters.append(content)
                    
                    # Update progress
                    if self.progress_reporter:
                        self.progress_reporter.update_progress(1)
                        self.progress_reporter.set_description(
                            f"Scraping {i+1}/{len(chapter_urls)} chapters"
                        )
                    
                    time.sleep(self.delay)  # Be nice to the server
            
            # Process with the adapter
            if self.progress_reporter:
                self.progress_reporter.print("Processing scraped content...")
            
            result = self.adapter.process_novel(novel_info, chapters)
            
            # Report completion
            if self.progress_reporter:
                if result.get("status") == "success":
                    self.progress_reporter.print("Novel scraping completed successfully!")
                    
                    # Show output location
                    if "file_path" in result:
                        self.progress_reporter.print(f"Saved to: {result['file_path']}")
                    elif "folder_path" in result:
                        self.progress_reporter.print(f"Saved to: {result['folder_path']}")
                else:
                    self.progress_reporter.print(f"Processing failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error scraping novel: {str(e)}")
            if self.progress_reporter:
                self.progress_reporter.print(f"Error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
        finally:
            # Close progress reporter if it has a close method
            if self.progress_reporter and hasattr(self.progress_reporter, "close"):
                self.progress_reporter.close()

class AudioNovelScraperCoordinator(NovelScraperCoordinator):
    """Coordinator specifically for audio novels"""
    
    def __init__(self, 
                 scraper: AudioNovelScraper, 
                 adapter: Adapter,
                 progress_reporter: Optional[ProgressReporter] = None,
                 max_threads: int = 6,
                 delay_between_requests: float = 1.0):
        """
        Initialize the audio novel coordinator.
        
        Args:
            scraper: The audio novel scraper implementation
            adapter: The adapter for processing/saving the scraped data
            progress_reporter: Optional progress reporter
            max_threads: Maximum number of threads for parallel operations
            delay_between_requests: Delay between requests to avoid overloading servers
        """
        super().__init__(scraper, adapter, progress_reporter, max_threads, delay_between_requests)