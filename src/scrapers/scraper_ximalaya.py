"""
Scraper implementation for Ximalaya audio novels
"""
from typing import Dict, List, Any
import json
import sys
import os

# Add correct path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from interfaces import AudioNovelScraper
from scrape_util import scrape_util

class ScraperXimalaya(AudioNovelScraper):
    """Scraper for Ximalaya audio novels"""
    
    def __init__(self, **kwargs):
        """Initialize the scraper"""
        super().__init__(**kwargs)
        self.base_url = "https://www.ximalaya.com"
    
    def get_source_info(self) -> Dict[str, str]:
        """Return information about the source website"""
        return {
            "name": "Ximalaya",
            "url": self.base_url,
            "language": "Chinese",
            "type": "audio"
        }
    
    def get_novel_info(self, url: str) -> Dict[str, Any]:
        """Get basic novel information"""
        page = scrape_util.scrape_url(url)
        
        try:
            # Extract album ID from URL
            album_id = url.rstrip('/').split('/')[-1]
            
            # Get album info from the API
            album_api_url = f"{self.base_url}/revision/album/v1/getAlbumDetailInfo?albumId={album_id}"
            album_data = json.loads(scrape_util.scrape_url(album_api_url).text)
            
            title = album_data.get("data", {}).get("mainInfo", {}).get("albumTitle", "Unknown Title")
            author = album_data.get("data", {}).get("anchorInfo", {}).get("anchorName", "Unknown Author")
            description = album_data.get("data", {}).get("mainInfo", {}).get("richIntro", "")
            
            # Clean HTML from description if needed
            if description and "<" in description:
                description = scrape_util.html_to_text(description)
            
            cover_url = album_data.get("data", {}).get("mainInfo", {}).get("cover", "")
            
            return {
                "title": title,
                "author": author,
                "description": description,
                "url": url,
                "source_website": "Ximalaya",
                "cover_url": cover_url,
                "album_id": album_id
            }
        except Exception as e:
            raise ValueError(f"Failed to extract novel info: {str(e)}")
    
    def get_index_pages(self, url: str) -> List[str]:
        """
        Get list of index pages containing chapter links
        
        For Ximalaya, we use a single index page and API requests for pagination
        """
        return [url]
    
    def get_chapter_urls(self, index_url: str) -> List[str]:
        """Get list of chapter URLs from an index page"""
        try:
            # Extract album ID from URL
            album_id = index_url.rstrip('/').split('/')[-1]
            
            chapter_url_list = []
            page_number = 1
            
            # API has pagination; we need to keep requesting until no more tracks
            while True:
                api_url = f"{self.base_url}/revision/album/v1/getTracksList?albumId={album_id}&pageNum={page_number}&sort=1&pageSize=30"
                response = scrape_util.scrape_url(api_url)
                
                tracks = json.loads(response.text).get("data", {}).get("tracks", [])
                if not tracks:
                    break
                    
                for track in tracks:
                    track_id = track.get("trackId")
                    if track_id:
                        chapter_url_list.append(str(track_id))
                
                page_number += 1
            
            return chapter_url_list
            
        except Exception as e:
            raise ValueError(f"Failed to extract chapter URLs: {str(e)}")
    
    def get_chapter_content(self, chapter_url: str) -> Dict[str, Any]:
        """Get audio content from a chapter URL"""
        try:
            # Get track details from API
            api_url = f"{self.base_url}/tracks/{chapter_url}.json"
            response = scrape_util.scrape_url(api_url, cookies=self.authentication_cookies)
            metadata = json.loads(response.text)
            
            audio_url = metadata.get("play_path", "")
            title = metadata.get("title", f"Chapter_{chapter_url}")
            
            return {
                "title": title,
                "audio_url": audio_url,
                "url": f"{self.base_url}/sound/{chapter_url}",
                "track_id": chapter_url,
                "duration": metadata.get("duration", 0),
                "file_size": metadata.get("play_path_32", ""),  # For size estimation
                "format": "m4a"  # Ximalaya typically uses m4a format
            }
        except Exception as e:
            raise ValueError(f"Failed to extract audio content: {str(e)}")