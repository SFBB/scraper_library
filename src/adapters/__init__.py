"""
Adapters package initialization
"""

from .text_file_adapter import TextFileAdapter
from .audio_file_adapter import AudioFileAdapter

# Registry of available adapters
ADAPTERS = {
    "text_file": TextFileAdapter,
    "audio_file": AudioFileAdapter
}

def get_adapter(name):
    """Get an adapter by name"""
    return ADAPTERS.get(name)