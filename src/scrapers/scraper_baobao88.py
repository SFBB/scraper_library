"""
Scraper implementation for Baobao88 audio novels
"""
from typing import Dict, List, Any
import sys
import os

# Add correct path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from interfaces import AudioNovelScraper
from scrape_util import scrape_util

class ScraperBaobao88(AudioNovelScraper):
    """Scraper for Baobao88 audio novels"""
    
    def __init__(self, **kwargs):
        """Initialize the scraper"""
        super().__init__(**kwargs)
        self.base_url = "http://www.baobao88.com"
        self.audio_base_url = "http://play.baobao88.com/bbfile/media/000007/%E5%B0%8F%E8%AF%B4"
    
    def get_source_info(self) -> Dict[str, str]:
        """Return information about the source website"""
        return {
            "name": "Baobao88",
            "url": self.base_url,
            "language": "Chinese",
            "type": "audio"
        }
    
    def get_novel_info(self, url: str) -> Dict[str, Any]:
        """Get basic novel information"""
        page = scrape_util.scrape_url(url, "html.parser")
        
        try:
            # Extract title and author from the page
            title = page.select("div.bookintro h1")[0].text.strip() if page.select("div.bookintro h1") else "Unknown Title"
            
            # Author info might be in a different location, trying to extract it
            author = "Unknown Author"  # Default value
            author_info = page.select("div.bookintro p")
            for p in author_info:
                text = p.text.strip()
                if "作者：" in text:
                    author = text.split("作者：")[1].strip()
                    break
            
            # Description
            description = ""
            desc_elements = page.select("div.jianjie")
            if desc_elements:
                description = scrape_util.html_to_text(desc_elements[0])
            
            return {
                "title": title,
                "author": author,
                "description": description,
                "url": url,
                "source_website": "Baobao88"
            }
        except Exception as e:
            raise ValueError(f"Failed to extract novel info: {str(e)}")
    
    def get_index_pages(self, url: str) -> List[str]:
        """
        Get list of index pages containing chapter links
        
        For Baobao88, we typically have a single index page.
        """
        return [url]
    
    def get_chapter_urls(self, index_url: str) -> List[str]:
        """Get list of chapter URLs from an index page"""
        try:
            page = scrape_util.scrape_url(index_url, "html.parser")
            chapter_links = []
            
            # Find the audio links in the page
            audio_list = page.select("div.listbox ul li a")
            for link in audio_list:
                href = link.get("href")
                if href and href.startswith("/yousheng/"):
                    # Extract audio ID from the URL
                    audio_id = href.split('/')[-1].replace(".html", "")
                    chapter_links.append(audio_id)
            
            return chapter_links
        except Exception as e:
            raise ValueError(f"Failed to extract chapter URLs: {str(e)}")
    
    def get_chapter_content(self, chapter_url: str) -> Dict[str, Any]:
        """Get audio content from a chapter URL"""
        try:
            # For Baobao88, the chapter_url is actually the audio ID
            # We construct the full audio URL based on the pattern
            audio_url = f"{self.audio_base_url}/{chapter_url}.mp3"
            
            # Title is derived from the ID, we could fetch the actual page
            # to get the title but that would require an extra request
            # for each chapter which might be inefficient
            title = f"Chapter_{chapter_url}"
            
            return {
                "title": title,
                "audio_url": audio_url,
                "url": f"{self.base_url}/yousheng/{chapter_url}.html",
                "track_id": chapter_url,
                "format": "mp3"
            }
        except Exception as e:
            raise ValueError(f"Failed to extract audio content: {str(e)}")