from typing import Dict, List, Any, Optional
import os
import sys

# Add correct path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from interfaces import Adapter

class TextFileAdapter(Adapter):
    """Adapter for saving novels as text files"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the text file adapter.
        
        Config options:
            file_path: Target file path (without extension)
            include_metadata: Whether to include metadata in the file (default: True)
        """
        super().__init__(config)
        self.file_path = self.config.get("file_path", "")
        self.include_metadata = self.config.get("include_metadata", True)
    
    def process_novel(self, novel_info: Dict[str, Any], chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Save novel as a text file.
        
        Args:
            novel_info: Dictionary with novel metadata
            chapters: List of dictionaries with chapter data
            
        Returns:
            Dictionary with processing results including file path
        """
        title = novel_info.get("title", "Unknown Title")
        author = novel_info.get("author", "Unknown Author")
        
        # Create file path if not provided
        if not self.file_path:
            self.file_path = f"{title} - {author}.txt"
        elif not self.file_path.endswith(".txt"):
            self.file_path = f"{self.file_path}.txt"
            
        try:
            # Create the file and write metadata
            with open(self.file_path, "w", encoding="utf-8") as file:
                # Write title and author
                if self.include_metadata:
                    file.write(f"{title}\n\n\n{author}\n\n\n\n\n\n\n\n\n")
                
                # Write each chapter
                for chapter in chapters:
                    chapter_title = chapter.get("title", "")
                    chapter_content = chapter.get("content", "")
                    file.write(f"{chapter_title}\n\n\n{chapter_content}\n\n\n\n\n\n")
                    
            return {
                "status": "success",
                "file_path": os.path.abspath(self.file_path),
                "chapters_saved": len(chapters)
            }
            
        except Exception as e:
            # Clean up on failure
            self.cleanup()
            return {
                "status": "error",
                "error": str(e)
            }
    
    def cleanup(self) -> None:
        """Remove the file if it exists but is incomplete"""
        if os.path.exists(self.file_path):
            os.remove(self.file_path)