"""
Scraper implementation for Syosetu (Japanese novel site)
"""
from typing import Dict, List, Any
import sys
import os

# Add correct path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from interfaces import NovelScraper
from scrape_util import scrape_util

class ScraperSyosetu(NovelScraper):
    """Scraper for Syosetu (Japanese novel site)"""
    
    def __init__(self, **kwargs):
        """Initialize the scraper"""
        super().__init__(**kwargs)
        self.base_url = "https://ncode.syosetu.com"
    
    def get_source_info(self) -> Dict[str, str]:
        """Return information about the source website"""
        return {
            "name": "Syosetu",
            "url": self.base_url,
            "language": "Japanese",
            "type": "text"
        }
    
    def get_novel_info(self, url: str) -> Dict[str, Any]:
        """Get basic novel information"""
        page = scrape_util.scrape_url(url, "html.parser")
        
        try:
            # Extract title
            title_elem = page.select("p.novel_title")
            if title_elem:
                title = title_elem[0].text.strip()
            else:
                # Try alternative selector
                title_elem = page.select("title")
                title = title_elem[0].text.strip().split(" - ")[0] if title_elem else "Unknown Title"
            
            # Extract author
            author_elem = page.select("div.novel_writername a")
            if author_elem:
                author = author_elem[0].text.strip().replace("作者：", "")
            else:
                author_elem = page.select("div.novel_writername")
                author = author_elem[0].text.strip().replace("作者：", "") if author_elem else "Unknown Author"
            
            # Extract description
            description_elem = page.select("div#novel_ex")
            description = scrape_util.html_to_text(description_elem[0]).strip() if description_elem else ""
            
            return {
                "title": title,
                "author": author,
                "description": description,
                "url": url,
                "source_website": "Syosetu"
            }
        except Exception as e:
            raise ValueError(f"Failed to extract novel info: {str(e)}")
    
    def get_index_pages(self, url: str) -> List[str]:
        """Get list of index pages containing chapter links"""
        # Syosetu typically has a single index page
        return [url]
    
    def get_chapter_urls(self, index_url: str) -> List[str]:
        """Get list of chapter URLs from an index page"""
        page = scrape_util.scrape_url(index_url, "html.parser")
        
        try:
            chapter_links = page.select("a.subtitle") or page.select("a.p-eplist__subtitle") or page.select("dl.novel_sublist2 a")
            
            return [f"{self.base_url}{link['href']}" for link in chapter_links if 'href' in link.attrs]
        except Exception as e:
            raise ValueError(f"Failed to extract chapter URLs: {str(e)}")
    
    def get_chapter_content(self, chapter_url: str) -> Dict[str, Any]:
        """Get content from a chapter URL"""
        page = scrape_util.scrape_url(chapter_url)
        
        try:
            # Try multiple possible selectors for chapter title
            title_selectors = [
                ".novel_subtitle",
                ".p-novel__subtitle", 
                "h1.novel_title",
                "h2.novel_subtitle"
            ]
            
            chapter_title = ""
            for selector in title_selectors:
                elements = page.select(selector)
                if elements:
                    chapter_title = elements[0].text.strip()
                    break
            
            # If still no title found, try to get it from the URL or page title
            if not chapter_title:
                # Try to get from page title
                title_element = page.select("title")
                if title_element:
                    full_title = title_element[0].text.strip()
                    if " - " in full_title:
                        chapter_title = full_title.split(" - ")[1]
            
            # Try multiple possible selectors for chapter content
            content_selectors = [
                "#novel_honbun", 
                "#novel_color", 
                ".novel_view",
                ".p-novel__body",
                ".p-novel_main"
            ]
            
            chapter_content = ""
            for selector in content_selectors:
                elements = page.select(selector)
                if elements:
                    chapter_content = scrape_util.html_to_text(elements[0])
                    break
            
            if not chapter_title or not chapter_content:
                raise ValueError("Could not find chapter title or content")
                
            return {
                "title": chapter_title,
                "content": chapter_content,
                "url": chapter_url
            }
        except Exception as e:
            raise ValueError(f"Failed to extract chapter content: {str(e)}")