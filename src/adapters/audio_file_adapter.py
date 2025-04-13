from typing import Dict, List, Any, Optional
import os
import shutil
import sys

# Add correct path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from interfaces import Adapter
from scrape_util import scrape_util

class AudioFileAdapter(Adapter):
    """Adapter for saving audio novel files"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the audio file adapter.
        
        Config options:
            folder_path: Target folder path
            file_extension: Audio file extension (default: "mp3")
            cookies: Authentication cookies for file download
        """
        super().__init__(config)
        self.folder_path = self.config.get("folder_path", "")
        self.file_extension = self.config.get("file_extension", "mp3")
        self.cookies = self.config.get("cookies", {})
    
    def process_novel(self, novel_info: Dict[str, Any], chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Save audio novel files.
        
        Args:
            novel_info: Dictionary with novel metadata
            chapters: List of dictionaries with chapter data including audio URLs
            
        Returns:
            Dictionary with processing results
        """
        title = novel_info.get("title", "Unknown Title")
        author = novel_info.get("author", "Unknown Author")
        
        # Create folder path if not provided
        if not self.folder_path:
            self.folder_path = f"{title} - {author}"
            
        try:
            # Create folder if it doesn't exist
            if not os.path.exists(self.folder_path):
                os.makedirs(self.folder_path)
            
            successful_downloads = 0
            failed_downloads = 0
            
            # Download each audio file
            for i, chapter in enumerate(chapters):
                chapter_title = chapter.get("title", f"Chapter_{i+1}")
                audio_url = chapter.get("audio_url", "")
                
                # Skip if no URL provided
                if not audio_url:
                    failed_downloads += 1
                    continue
                
                # Clean filename
                safe_title = self._sanitize_filename(chapter_title)
                target_path = os.path.join(
                    self.folder_path,
                    f"{safe_title}.{self.file_extension}"
                )
                
                # Download the file
                if scrape_util.write_stream(
                    url=audio_url,
                    cookies=self.cookies,
                    target_path=target_path
                ):
                    successful_downloads += 1
                else:
                    failed_downloads += 1
                    
            return {
                "status": "success",
                "folder_path": os.path.abspath(self.folder_path),
                "successful_downloads": successful_downloads,
                "failed_downloads": failed_downloads,
                "total_chapters": len(chapters)
            }
            
        except Exception as e:
            # Clean up on failure
            self.cleanup()
            return {
                "status": "error",
                "error": str(e)
            }
    
    def cleanup(self) -> None:
        """Remove the folder if it exists but is incomplete"""
        if os.path.exists(self.folder_path):
            shutil.rmtree(self.folder_path, ignore_errors=True)
    
    def _sanitize_filename(self, filename: str) -> str:
        """Remove invalid characters from filename"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename