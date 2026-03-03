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
            chapters: List of dictionaries with chapter/structural data
            
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
                    file.write(f"{title}\n\n\n{author}\n\n\n")
                    
                    # Generate and write TOC
                    toc = self._generate_toc(chapters)
                    if toc:
                        file.write("TOC\n\n")
                        file.write(toc)
                        file.write("\n\n\n\n\n\n\n")
                
                # Write each item (chapter or volume/part)
                for item in chapters:
                    if item.get("type") in ("volume", "part"):
                        volume_title = item.get("title", "")
                        file.write(f"{volume_title}\n\n\n")
                    else:
                        chapter_title = item.get("title", "")
                        chapter_content = item.get("content", "")
                        if chapter_content: # Only write if we have content
                            file.write(f"{chapter_title}\n\n\n{chapter_content}\n\n\n\n\n\n")
                    
            return {
                "status": "success",
                "file_path": os.path.abspath(self.file_path),
                "chapters_saved": sum(1 for item in chapters if item.get("type") == "chapter")
            }
            
        except Exception as e:
            # Clean up on failure
            self.cleanup()
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _generate_toc(self, items: List[Dict[str, Any]]) -> str:
        """Generate a Table of Contents string from items"""
        toc_lines = []
        for item in items:
            if item.get("type") in ("volume", "part"):
                toc_lines.append(item.get("title", ""))
            elif item.get("type") == "chapter":
                title = item.get("title", "")
                if title:
                    toc_lines.append(f"  {title}")
        return "\n".join(toc_lines)

    def cleanup(self) -> None:
        """Remove the file if it exists but is incomplete"""
        if os.path.exists(self.file_path):
            os.remove(self.file_path)