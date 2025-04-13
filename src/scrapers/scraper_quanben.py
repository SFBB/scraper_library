"""
Scraper implementation for Quanben novels
"""
from typing import Dict, List, Any
import sys
import os

# Add correct path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from interfaces import NovelScraper
from scrape_util import scrape_util

class ScraperQuanben(NovelScraper):
    """Scraper for Quanben novels"""
    
    def __init__(self, **kwargs):
        """Initialize the scraper"""
        super().__init__(**kwargs)
        self.base_url = "https://www.quanben.io"
    
    def get_source_info(self) -> Dict[str, str]:
        """Return information about the source website"""
        return {
            "name": "Quanben",
            "url": self.base_url,
            "language": "Chinese",
            "type": "text"
        }
    
    def get_novel_info(self, url: str) -> Dict[str, Any]:
        """Get basic novel information"""
        page = scrape_util.scrape_url(url, "xml")
        
        try:
            # Extract novel information
            # Typically the novel title and author should be on the page
            title = "Unknown Title"
            author = "Unknown Author"
            description = ""
            
            # Try to extract title from URL if not found on page
            if url.endswith('/list.html'):
                novel_id = url.split('/')[-2]
                if novel_id:
                    title = novel_id.replace('-', ' ').title()
            
            # Get a more accurate title and author from the first chapter if available
            chapter_urls = self.get_chapter_urls(url)
            if chapter_urls:
                first_chapter = self.get_chapter_content(chapter_urls[0])
                if first_chapter.get('title'):
                    # Titles in Quanben often include book name
                    chapter_title = first_chapter.get('title')
                    if '第一章' in chapter_title or 'Chapter' in chapter_title:
                        title_parts = chapter_title.split('：' if '：' in chapter_title else ':')
                        if len(title_parts) > 1:
                            title = title_parts[0].strip()
            
            return {
                "title": title,
                "author": author,
                "description": description,
                "url": url,
                "source_website": "Quanben"
            }
        except Exception as e:
            raise ValueError(f"Failed to extract novel info: {str(e)}")
    
    def get_index_pages(self, url: str) -> List[str]:
        """Get list of index pages containing chapter links"""
        # Quanben typically has all chapters on a single page
        return [url]
    
    def get_chapter_urls(self, index_url: str) -> List[str]:
        """Get list of chapter URLs from an index page"""
        page = scrape_util.scrape_url(index_url, "xml")
        
        try:
            # For Quanben, we need to determine the pattern of chapter URLs
            chapter_list = []
            
            # Extract the novel ID from the URL
            if '/n/' in index_url:
                novel_id = index_url.split('/n/')[1].split('/')[0]
                
                # Find the last chapter to determine the chapter count
                last_chapter = page.select("li")[-1].select("a")[0]["href"] if page.select("li") else None
                if last_chapter:
                    # Extract the chapter number from the URL
                    last_chapter_num = last_chapter.replace(f"/n/{novel_id}/", "").replace(".html", "")
                    try:
                        # Generate URLs for all chapters
                        for i in range(1, int(last_chapter_num) + 1):
                            chapter_list.append(f"{self.base_url}/n/{novel_id}/{i}.html")
                    except ValueError:
                        # If we can't determine the pattern, try to extract links directly
                        for link in page.select("li a"):
                            href = link.get("href")
                            if href and href.startswith(f"/n/{novel_id}/"):
                                chapter_list.append(f"{self.base_url}{href}")
            
            return chapter_list
        except Exception as e:
            raise ValueError(f"Failed to extract chapter URLs: {str(e)}")
    
    def get_chapter_content(self, chapter_url: str) -> Dict[str, Any]:
        """Get content from a chapter URL"""
        page = scrape_util.scrape_url(chapter_url)
        
        try:
            # Extract chapter title and content
            chapter_title = page.select("h1.headline")[0].text.strip() if page.select("h1.headline") else "Unknown Chapter"
            chapter_content = ""
            
            # Extract chapter content
            content_elem = page.select("div.articlebody")
            if content_elem:
                chapter_content = scrape_util.html_to_text(content_elem[0])
            
            return {
                "title": chapter_title,
                "content": chapter_content,
                "url": chapter_url
            }
        except Exception as e:
            raise ValueError(f"Failed to extract chapter content: {str(e)}")