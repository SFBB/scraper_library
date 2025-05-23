from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Protocol, runtime_checkable

class Scraper(ABC):
    """Base interface for all scrapers"""
    
    def __init__(self, **kwargs):
        """Initialize with optional authentication cookies"""
        self.authentication_cookies = kwargs.get("authentication_cookies", {})
    
    @abstractmethod
    def get_source_info(self) -> Dict[str, str]:
        """Return information about the source website"""
        pass

class NovelScraper(Scraper):
    """Interface for text-based novel scrapers"""
    
    @abstractmethod
    def get_novel_info(self, url: str) -> Dict[str, Any]:
        """
        Get basic novel information.
        
        Args:
            url: Main novel URL
            
        Returns:
            Dictionary with novel metadata (title, author, etc.)
        """
        pass
    
    @abstractmethod
    def get_index_pages(self, url: str) -> List[str]:
        """
        Get list of index pages containing chapter links.
        
        Args:
            url: Main novel URL
            
        Returns:
            List of URLs for index pages
        """
        pass
    
    @abstractmethod
    def get_chapter_urls(self, index_url: str) -> List[str]:
        """
        Get list of chapter URLs from an index page.
        
        Args:
            index_url: URL of the index page
            
        Returns:
            List of chapter URLs
        """
        pass
    
    def get_chapter_list(self, url: str) -> List[str]:
        """
        Get list of all chapter URLs for a novel.
        
        This method combines get_index_pages() and get_chapter_urls() to provide
        a simplified interface for getting all chapter URLs in one call.
        
        Args:
            url: Main novel URL
            
        Returns:
            List of all chapter URLs
        """
        # Get all index pages
        index_pages = self.get_index_pages(url)
        
        # Get chapter URLs from each index page
        all_chapter_urls = []
        for index_url in index_pages:
            chapter_urls = self.get_chapter_urls(index_url)
            all_chapter_urls.extend(chapter_urls)
        
        return all_chapter_urls
    
    @abstractmethod
    def get_chapter_content(self, chapter_url: str) -> Dict[str, Any]:
        """
        Get content from a chapter URL.
        
        Args:
            chapter_url: URL of the chapter
            
        Returns:
            Dictionary with chapter data (title, content, etc.)
        """
        pass

class AudioNovelScraper(NovelScraper):
    """Interface for audio novel scrapers"""
    
    @abstractmethod
    def get_chapter_content(self, chapter_url: str) -> Dict[str, Any]:
        """
        Get audio content from a chapter URL.
        
        Args:
            chapter_url: URL of the chapter
            
        Returns:
            Dictionary with chapter data (title, audio_url, etc.)
        """
        pass

class Adapter(ABC):
    """Base interface for all adapters"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the adapter with configuration.
        
        Args:
            config: Dictionary of configuration parameters
        """
        self.config = config or {}
    
    @abstractmethod
    def process_novel(self, novel_info: Dict[str, Any], chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process novel information and chapter content.
        
        Args:
            novel_info: Dictionary containing novel metadata
            chapters: List of dictionaries containing chapter data
            
        Returns:
            Dictionary with processing results
        """
        pass

class ProgressReporter(ABC):
    """Interface for reporting progress"""
    
    @abstractmethod
    def print(self, message: str) -> None:
        """Print a message"""
        pass
    
    @abstractmethod
    def update_progress(self, delta: int = 1) -> None:
        """Update the progress bar"""
        pass
    
    @abstractmethod
    def set_description(self, description: str) -> None:
        """Set the progress bar description"""
        pass
    
    @abstractmethod
    def initialize_progress(self, total: int) -> None:
        """Initialize a new progress bar"""
        pass

@runtime_checkable
class QAScraper(Protocol):
    """Protocol for question-and-answer scrapers"""
    
    def scrape_qa_source(self, url: str) -> Dict[str, Any]:
        """
        Scrape a Q&A source (website, social media profile, etc.)
        
        Args:
            url: URL of the Q&A source
            
        Returns:
            Dictionary containing scraped Q&A content
        """
        ...
    
    def filter_qa_content(self, content: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter Q&A content based on criteria
        
        Args:
            content: The Q&A content to filter
            filters: Dictionary of filter criteria
            
        Returns:
            Filtered Q&A content
        """
        ...
    
    def extract_qa_pairs(self, raw_content: str) -> List[Dict[str, str]]:
        """
        Extract question-and-answer pairs from raw content
        
        Args:
            raw_content: Raw text containing Q&A content
            
        Returns:
            List of dictionaries with 'question' and 'answer' keys
        """
        ...