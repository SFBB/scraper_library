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
from scrape_util import scrape_util

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
    
    def scrape_novel(self, 
                    novel_url: str, 
                    max_chapters: Optional[int] = None,
                    chapter_range: Optional[str] = None,
                    range_callback: Optional[Any] = None) -> Dict[str, Any]:
        """
        Scrape a novel and process it with the adapter.
        
        Args:
            novel_url: URL of the novel to scrape
            max_chapters: Optional limit on number of chapters to scrape
            chapter_range: Optional range of chapters to scrape (e.g., '1-10')
            range_callback: Optional callback to request range after getting total count
            
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
                self.progress_reporter.print("Retrieving index structure...")
            
            # Use get_index_structure instead of get_index_pages + get_chapter_urls
            full_structure = self.scraper.get_index_structure(novel_url)
            
            # Extract only chapter items for downloading
            chapter_items = [item for item in full_structure if item["type"] == "chapter"]
            chapter_urls = [item["url"] for item in chapter_items]
            
            if self.progress_reporter:
                total_parts = sum(1 for item in full_structure if item["type"] in ("volume", "part"))
                self.progress_reporter.print(f"Found {len(chapter_urls)} chapters and {total_parts} parts")
            
            # Handle range selection
            total_chapters = len(chapter_urls)
            selected_range = chapter_range
            
            # If range_callback is provided and no range was explicitly given, use it
            if range_callback and not selected_range:
                selected_range = range_callback(total_chapters)
            
            # Apply range if specified
            if selected_range:
                start, end = scrape_util.parse_range(selected_range, total_chapters)
                selected_chapter_urls = chapter_urls[start:end]
                
                # Rebuild full_structure to only include selected chapters and their preceding parts
                new_structure = []
                current_part = None
                for item in full_structure:
                    if item["type"] in ("volume", "part"):
                        current_part = item
                    elif item["type"] == "chapter":
                        if item["url"] in selected_chapter_urls:
                            if current_part:
                                new_structure.append(current_part)
                                current_part = None # Clear so we don't add it again for the next chapter
                            new_structure.append(item)
                
                full_structure = new_structure
                chapter_urls = selected_chapter_urls
                
                if self.progress_reporter:
                    self.progress_reporter.print(
                        f"Selected range {selected_range}: downloading chapters {start+1} to {end} (Total: {len(chapter_urls)})"
                    )
            # Apply chapter limit if specified and no range was used
            elif max_chapters and max_chapters < total_chapters:
                selected_chapter_urls = chapter_urls[:max_chapters]
                
                new_structure = []
                current_part = None
                for item in full_structure:
                    if item["type"] in ("volume", "part"):
                        current_part = item
                    elif item["type"] == "chapter":
                        if item["url"] in selected_chapter_urls:
                            if current_part:
                                new_structure.append(current_part)
                                current_part = None
                            new_structure.append(item)
                
                full_structure = new_structure
                chapter_urls = selected_chapter_urls
                
                if self.progress_reporter:
                    self.progress_reporter.print(
                        f"Limiting to {max_chapters} chapters (out of {total_chapters} available)"
                    )
            
            # Prepare to scrape chapters
            if self.progress_reporter:
                self.progress_reporter.print(f"Scraping {len(chapter_urls)} chapters...")
                self.progress_reporter.initialize_progress(len(chapter_urls))
            
            # Mapping from URL to downloaded content
            downloaded_chapters = {}
            
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
                            content = results[index]
                            downloaded_chapters[chunk[i]] = content
                            chunk_results.append(content)
                    
                    # Update progress
                    if self.progress_reporter:
                        self.progress_reporter.update_progress(len(chunk))
                        self.progress_reporter.set_description(
                            f"Scraping {chunk_start + len(chunk)}/{len(chapter_urls)} chapters"
                        )
                    
                    return chunk_results
                
                # Process chapters in parallel
                self.threading_manager.process_in_parallel(
                    chapter_urls,
                    process_chapter,
                    chunk_handler,
                    min(self.max_threads, len(chapter_urls))
                )
            else:
                # Sequential processing for a small number of chapters
                for i, chapter_url in enumerate(chapter_urls):
                    content = self.scraper.get_chapter_content(chapter_url)
                    downloaded_chapters[chapter_url] = content
                    
                    # Update progress
                    if self.progress_reporter:
                        self.progress_reporter.update_progress(1)
                        self.progress_reporter.set_description(
                            f"Scraping {i+1}/{len(chapter_urls)} chapters"
                        )
                    
                    time.sleep(self.delay)  # Be nice to the server
            
            # Combine structure with downloaded content
            final_chapters_with_structure = []
            for item in full_structure:
                if item["type"] == "chapter":
                    if item["url"] in downloaded_chapters:
                        # Update the structure item with content
                        chapter_content = downloaded_chapters[item["url"]]
                        item.update(chapter_content)
                        final_chapters_with_structure.append(item)
                else:
                    final_chapters_with_structure.append(item)

            # Process with the adapter
            if self.progress_reporter:
                self.progress_reporter.print("Processing scraped content...")
            
            result = self.adapter.process_novel(novel_info, final_chapters_with_structure)
            
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