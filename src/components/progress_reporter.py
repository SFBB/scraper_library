from typing import Dict, List, Any, Optional
import sys
import os

# Add correct path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from interfaces import ProgressReporter
from tqdm import tqdm

class ConsoleProgressReporter(ProgressReporter):
    """Progress reporter that uses tqdm for console output"""
    
    def __init__(self):
        """Initialize the progress reporter"""
        self.progress_bar = None
        
    def print(self, message: str) -> None:
        """Print a message to the console"""
        # If we have an active progress bar, use tqdm.write to avoid conflicts
        if self.progress_bar:
            tqdm.write(message)
        else:
            print(message)
    
    def initialize_progress(self, total: int) -> None:
        """Initialize a new progress bar with the given total"""
        # Close existing progress bar if any
        if self.progress_bar:
            self.progress_bar.close()
            
        self.progress_bar = tqdm(total=total, desc="Processing", unit="items")
    
    def update_progress(self, delta: int = 1) -> None:
        """Update the progress bar by the given amount"""
        if self.progress_bar:
            self.progress_bar.update(delta)
    
    def set_description(self, description: str) -> None:
        """Set the progress bar description"""
        if self.progress_bar:
            self.progress_bar.set_description(description)
            
    def close(self) -> None:
        """Close the progress bar"""
        if self.progress_bar:
            self.progress_bar.close()
            self.progress_bar = None