"""
Scraper implementation for X (formerly Twitter) timeline posts
This scraper is optimized for token efficiency and small context windows (3k tokens)
"""
from typing import Dict, List, Any, Optional
import sys
import os
import re
import time
import json
from datetime import datetime
import logging

# Add correct path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from interfaces import Scraper
from scrape_util import scrape_util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("scraper_x_timeline")

class ScraperXTimeline(Scraper):
    """
    Scraper for X (Twitter) timeline posts
    Focuses on a specific user's timeline and filters posts by regex pattern
    """
    
    def __init__(self, **kwargs):
        """Initialize the scraper with optional parameters"""
        self.base_url = "https://twitter.com"
        self.api_base_url = "https://api.twitter.com/2"
        self.bearer_token = kwargs.get("bearer_token", os.environ.get("X_BEARER_TOKEN"))
        self.max_results_per_request = kwargs.get("max_results", 100)
        self.rate_limit_wait = kwargs.get("rate_limit_wait", 5)  # seconds between requests
        
        if not self.bearer_token:
            logger.warning("No bearer token provided. Set X_BEARER_TOKEN environment variable or pass as bearer_token parameter")
    
    def scrape_page(self, url: str) -> Dict[str, Any]:
        """
        Scrape a single page (in this case, a user's timeline)
        
        Args:
            url: The URL to scrape (username in format: @username or username)
            
        Returns:
            Dictionary containing scraped content
        """
        # Extract username from URL or direct input
        username = self._extract_username(url)
        
        try:
            # Get user ID from username (required for API)
            user_id = self._get_user_id(username)
            if not user_id:
                raise ValueError(f"Could not find user ID for {username}")
            
            # Get timeline posts
            posts = self._get_timeline_posts(user_id)
            
            return {
                "username": username,
                "user_id": user_id,
                "posts": posts,
                "scraped_at": datetime.now().isoformat(),
                "source": "x_timeline"
            }
        except Exception as e:
            logger.error(f"Error scraping X timeline for {username}: {str(e)}")
            raise
    
    def scrape_multiple_pages(self, urls: List[str], regex_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Scrape multiple user timelines with optional regex filtering
        
        Args:
            urls: List of usernames/URLs to scrape
            regex_filter: Optional regex pattern to filter posts
            
        Returns:
            List of dictionaries containing filtered scraped content
        """
        results = []
        
        for url in urls:
            try:
                # Scrape the timeline
                scraped_data = self.scrape_page(url)
                
                # Apply regex filtering if provided
                if regex_filter:
                    pattern = re.compile(regex_filter, re.IGNORECASE)
                    filtered_posts = []
                    
                    for post in scraped_data["posts"]:
                        if pattern.search(post["text"]):
                            filtered_posts.append(post)
                    
                    # Replace original posts with filtered ones
                    scraped_data["posts"] = filtered_posts
                    scraped_data["filter_applied"] = regex_filter
                
                # Optimize for token efficiency - create summary stats
                scraped_data["post_count"] = len(scraped_data["posts"])
                scraped_data["earliest_post_date"] = min([p["created_at"] for p in scraped_data["posts"]]) if scraped_data["posts"] else None
                scraped_data["latest_post_date"] = max([p["created_at"] for p in scraped_data["posts"]]) if scraped_data["posts"] else None
                
                results.append(scraped_data)
                
                # Respect rate limits
                time.sleep(self.rate_limit_wait)
                
            except Exception as e:
                logger.error(f"Error processing {url}: {str(e)}")
                results.append({
                    "username": self._extract_username(url),
                    "error": str(e),
                    "scraped_at": datetime.now().isoformat(),
                    "source": "x_timeline"
                })
        
        return results
    
    def _extract_username(self, url_or_username: str) -> str:
        """Extract username from URL or direct input"""
        if url_or_username.startswith("http"):
            # Extract from URL
            parts = url_or_username.strip("/").split("/")
            return parts[-1].replace("@", "")
        else:
            # Direct username
            return url_or_username.replace("@", "")
    
    def _get_user_id(self, username: str) -> Optional[str]:
        """Get user ID from username using X API"""
        if not self.bearer_token:
            raise ValueError("Bearer token required to use X API")
        
        url = f"{self.api_base_url}/users/by/username/{username}"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        response = scrape_util.make_request(url, headers=headers)
        if response and response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("id")
        
        return None
    
    def _get_timeline_posts(self, user_id: str, max_posts: int = 1000) -> List[Dict[str, Any]]:
        """
        Get timeline posts for a user
        
        Args:
            user_id: X user ID
            max_posts: Maximum number of posts to retrieve
            
        Returns:
            List of post dictionaries
        """
        if not self.bearer_token:
            raise ValueError("Bearer token required to use X API")
        
        all_posts = []
        pagination_token = None
        params = {
            "max_results": min(self.max_results_per_request, 100),  # API limit is 100
            "tweet.fields": "created_at,public_metrics,entities,context_annotations",
            "expansions": "author_id,referenced_tweets.id",
            "user.fields": "name,username,profile_image_url"
        }
        
        while len(all_posts) < max_posts:
            if pagination_token:
                params["pagination_token"] = pagination_token
            
            url = f"{self.api_base_url}/users/{user_id}/tweets"
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json"
            }
            
            response = scrape_util.make_request(url, params=params, headers=headers)
            
            if not response or response.status_code != 200:
                logger.error(f"Error fetching timeline: {response.text if response else 'No response'}")
                break
            
            data = response.json()
            posts = data.get("data", [])
            
            # Process posts to extract crucial information (optimized for token efficiency)
            for post in posts:
                processed_post = {
                    "id": post.get("id"),
                    "text": post.get("text"),
                    "created_at": post.get("created_at"),
                    "like_count": post.get("public_metrics", {}).get("like_count", 0),
                    "retweet_count": post.get("public_metrics", {}).get("retweet_count", 0),
                    "reply_count": post.get("public_metrics", {}).get("reply_count", 0)
                }
                
                # Extract hashtags and mentions (useful for analysis)
                if "entities" in post and "hashtags" in post["entities"]:
                    processed_post["hashtags"] = [h["tag"] for h in post["entities"]["hashtags"]]
                
                if "entities" in post and "mentions" in post["entities"]:
                    processed_post["mentions"] = [m["username"] for m in post["entities"]["mentions"]]
                
                all_posts.append(processed_post)
            
            # Check for pagination
            meta = data.get("meta", {})
            pagination_token = meta.get("next_token")
            
            # If no more pages or reached max
            if not pagination_token or len(all_posts) >= max_posts:
                break
            
            # Respect rate limits
            time.sleep(self.rate_limit_wait)
        
        return all_posts[:max_posts]