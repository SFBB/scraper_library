"""
Scraper implementation for 69shu.net
"""
from typing import Dict, List, Any
import sys
import os

# Add correct path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from interfaces import NovelScraper
from scrape_util import scrape_util

class Scraper69Shu(NovelScraper):
    """Scraper for 69shu.net novels"""
    
    def __init__(self, **kwargs):
        """Initialize the scraper"""
        super().__init__(**kwargs)
        self.base_url = "https://69shu.net"
    
    def get_source_info(self) -> Dict[str, str]:
        """Return information about the source website"""
        return {
            "name": "69shu.net",
            "url": self.base_url,
            "language": "Chinese",
            "type": "text"
        }
    
    def get_novel_info(self, url: str) -> Dict[str, Any]:
        """Get basic novel information"""
        page = scrape_util.scrape_url(url)
        
        # Extract novel information
        try:
            # Title is in h3 tag
            title_elem = page.select("div.booknav2")[0].select("h1")[0]
            title = title_elem.text.strip()
            
            # Author information
            author_elem = page.select("div.booknav2")[0].select("h2 a")[0]
            author = author_elem.text.strip()
            
            # Description
            description_elem = page.select("div.navtxt")[0]
            description = scrape_util.html_to_text(description_elem).strip()
            
            return {
                "title": title,
                "author": author,
                "description": description,
                "url": url,
                "source_website": "69shu.net"
            }
        except Exception as e:
            raise ValueError(f"Failed to extract novel info: {str(e)}")
    
    def get_index_pages(self, url: str) -> List[str]:
        """Get list of index pages containing chapter links"""
        page = scrape_util.scrape_url(url)
        
        try:
            page_options = page.select('div.listpage')[0].find_all("option")
            return [f"{self.base_url}{option['value']}" for option in page_options]
        except Exception as e:
            raise ValueError(f"Failed to extract index pages: {str(e)}")
    
    def get_chapter_urls(self, index_url: str) -> List[str]:
        """Get list of chapter URLs from an index page"""
        page = scrape_util.scrape_url(index_url)
        
        try:
            chapter_elements = page.select("div.info_chapters ul.p2")[1].find_all("li")
            return [f"{self.base_url}{chapter.select('a')[0]['href']}" for chapter in chapter_elements]
        except Exception as e:
            raise ValueError(f"Failed to extract chapter URLs: {str(e)}")
    
    def get_chapter_content(self, chapter_url: str) -> Dict[str, Any]:
        """Get content from a chapter URL"""
        page = scrape_util.scrape_url(chapter_url)
        
        try:
            # Extract chapter title
            chapter_title = page.select("h2")[0].text.strip()
            
            # Extract chapter content
            content_elem = page.select("div.novelcontent")[0]
            chapter_content = scrape_util.html_to_text(content_elem).strip()
            
            return {
                "title": chapter_title,
                "content": chapter_content,
                "url": chapter_url
            }
        except Exception as e:
            raise ValueError(f"Failed to extract chapter content: {str(e)}")