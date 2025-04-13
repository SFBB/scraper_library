from abc import ABC, abstractmethod
from typing import Dict, List, Any, Protocol, Optional, Callable, runtime_checkable

# Scraper component interfaces
class ContentScraper(Protocol):
    """Defines the interface for scraping content"""
    
    @abstractmethod
    def scrape_index_list(self, url: str) -> List[str]:
        """Scrape the list of index pages"""
        pass
        
    @abstractmethod
    def scrape_chapter_list(self, page_index_url: str) -> List[str]:
        """Scrape the list of chapter URLs from an index page"""
        pass
        
    @abstractmethod
    def scrape_chapter(self, chapter_url: str) -> Any:
        """Scrape the content of a chapter"""
        pass

# Storage component interfaces
class StorageHandler(Protocol):
    """Defines the interface for storing scraped content"""
    
    @abstractmethod
    def initialize(self, metadata: Dict[str, Any]) -> None:
        """Initialize the storage with metadata"""
        pass
        
    @abstractmethod
    def store(self, index: int, url: str, content: Any) -> None:
        """Store the scraped content"""
        pass
        
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up in case of failure"""
        pass

# Progress reporting interface
class ProgressReporter(Protocol):
    """Defines the interface for reporting progress"""
    
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

# Threading management interface
class ThreadingManager(Protocol):
    """Defines the interface for managing multi-threaded operations"""
    
    @abstractmethod
    def process_in_parallel(self, 
                          items: List[Any], 
                          process_func: Callable[[Any, int], Any],
                          chunk_handler: Optional[Callable[[int, List[Any], Dict[int, Any]], List[Any]]] = None,
                          max_threads: int = 6) -> List[Any]:
        """Process items in parallel"""
        pass

@runtime_checkable
class Scraper(Protocol):
    """Protocol for scraper components"""
    
    def scrape_page(self, url: str) -> Dict[str, Any]:
        """
        Scrape a single page and return its content
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dictionary containing scraped content
        """
        ...
    
    def scrape_multiple_pages(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape multiple pages and return their content
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of dictionaries containing scraped content
        """
        ...

@runtime_checkable
class DataSaver(Protocol):
    """Protocol for data saving components"""
    
    def save(self, data: Any, path: str, filename: str) -> str:
        """
        Save data to a file
        
        Args:
            data: The data to save
            path: Directory path to save to
            filename: Name of the file
            
        Returns:
            The full path to the saved file
        """
        ...
    
    def load(self, path: str) -> Any:
        """
        Load data from a file
        
        Args:
            path: Path to the file to load
            
        Returns:
            The loaded data
        """
        ...

@runtime_checkable
class ProgressReporter(Protocol):
    """Protocol for progress reporting components"""
    
    def print(self, message: str) -> None:
        """
        Print a message to the user
        
        Args:
            message: Message to print
        """
        ...
    
    def update_progress(self, delta: int = 1) -> None:
        """
        Update the progress bar by a delta
        
        Args:
            delta: Amount to increment progress
        """
        ...
    
    def set_description(self, description: str) -> None:
        """
        Set the progress bar description
        
        Args:
            description: The description to set
        """
        ...
    
    def initialize_progress(self, total: int) -> None:
        """
        Initialize a new progress bar
        
        Args:
            total: Total number of items for the progress bar
        """
        ...

@runtime_checkable
class ThreadingManager(Protocol):
    """Protocol for threading manager components"""
    
    def run_in_parallel(self, func, items, max_workers: int) -> List[Any]:
        """
        Run a function on multiple items in parallel
        
        Args:
            func: Function to run on each item
            items: List of items to process
            max_workers: Maximum number of worker threads
            
        Returns:
            List of results from the function calls
        """
        ...