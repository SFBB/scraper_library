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