#!/usr/bin/env python3
"""
Novel Scraper CLI

Command-line interface for the novel scraper library, allowing flexible
combination of scrapers and adapters to handle different sources and output formats.
"""

import argparse
import sys
import os
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("novel_scraper_cli")

# Add current directory to path to make imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import scraper components
from scrapers import get_scraper, SCRAPERS
from adapters import get_adapter, ADAPTERS
from components.progress_reporter import ConsoleProgressReporter
from coordinator import NovelScraperCoordinator, AudioNovelScraperCoordinator

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Novel Scraper CLI - Download novels from various websites"
    )
    
    # Required arguments
    parser.add_argument(
        "url", 
        help="URL of the novel to scrape"
    )
    
    # Scraper selection
    parser.add_argument(
        "--scraper", "-s",
        choices=list(SCRAPERS.keys()),
        required=True,
        help="Scraper to use for the given URL"
    )
    
    # Adapter selection
    parser.add_argument(
        "--adapter", "-a",
        choices=list(ADAPTERS.keys()),
        default="text_file",
        help="Adapter to use for processing output (default: text_file)"
    )
    
    # Output path
    parser.add_argument(
        "--output", "-o",
        help="Output path (file for text_file adapter, directory for audio_file adapter)"
    )
    
    # Limit number of chapters
    parser.add_argument(
        "--max-chapters", "-m",
        type=int,
        help="Maximum number of chapters to download"
    )
    
    # Threading options
    parser.add_argument(
        "--threads", "-t",
        type=int,
        default=6,
        help="Maximum number of threads to use (default: 6)"
    )
    
    # Delay between requests
    parser.add_argument(
        "--delay", "-d",
        type=float,
        default=1.0,
        help="Delay between requests in seconds (default: 1.0)"
    )
    
    return parser.parse_args()

def create_adapter(adapter_name: str, args: argparse.Namespace) -> Any:
    """Create and configure an adapter based on CLI arguments"""
    adapter_class = get_adapter(adapter_name)
    
    if not adapter_class:
        logger.error(f"Invalid adapter: {adapter_name}")
        sys.exit(1)
    
    # Configure adapter based on type
    config = {}
    
    if adapter_name == "text_file":
        if args.output:
            config["file_path"] = args.output
    
    elif adapter_name == "audio_file":
        if args.output:
            config["folder_path"] = args.output
            
        # Determine file extension based on scraper
        if args.scraper == "ximalaya":
            config["file_extension"] = "m4a"
        else:
            config["file_extension"] = "mp3"
    
    return adapter_class(config)

def main():
    """Main entry point"""
    args = parse_args()
    
    try:
        # Get the scraper class
        scraper_class = get_scraper(args.scraper)
        if not scraper_class:
            logger.error(f"Invalid scraper: {args.scraper}")
            sys.exit(1)
        
        # Create scraper instance
        scraper = scraper_class()
        
        # Create adapter instance
        adapter = create_adapter(args.adapter, args)
        
        # Create progress reporter
        progress_reporter = ConsoleProgressReporter()
        
        # Create appropriate coordinator based on scraper type
        if hasattr(scraper, "get_audio_content"):
            coordinator = AudioNovelScraperCoordinator(
                scraper=scraper,
                adapter=adapter,
                progress_reporter=progress_reporter,
                max_threads=args.threads,
                delay_between_requests=args.delay
            )
        else:
            coordinator = NovelScraperCoordinator(
                scraper=scraper,
                adapter=adapter,
                progress_reporter=progress_reporter,
                max_threads=args.threads,
                delay_between_requests=args.delay
            )
        
        # Start scraping
        result = coordinator.scrape_novel(
            novel_url=args.url,
            max_chapters=args.max_chapters
        )
        
        # Check result
        if result.get("status") == "success":
            logger.info("Novel scraping completed successfully!")
            sys.exit(0)
        else:
            logger.error(f"Scraping failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()