"""
Scraper implementation for Q&A content from X (formerly Twitter) and other sources
This scraper is optimized for extracting question-answer pairs from various sources,
particularly X posts that contain ask.fm links or other Q&A content.
"""
from typing import Dict, List, Any, Optional, Tuple
import sys
import os
import re
import time
import json
from datetime import datetime
import logging
from bs4 import BeautifulSoup
import requests

# Add correct path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from interfaces import Scraper
from scrape_util import scrape_util
from scrapers.scraper_x_timeline import ScraperXTimeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("scraper_qa")

class ScraperQA(Scraper):
    """
    Scraper for Q&A content from X (Twitter) posts and other sources
    Extracts structured question-answer pairs from various sources
    """
    
    def __init__(self, **kwargs):
        """Initialize the scraper with optional parameters"""
        super().__init__(**kwargs)
        self.x_scraper = ScraperXTimeline(**kwargs)
        self.rate_limit_wait = kwargs.get("rate_limit_wait", 5)  # seconds between requests
        self.max_qa_per_source = kwargs.get("max_qa", 100)  # maximum number of Q&A pairs to extract
        
    def get_source_info(self) -> Dict[str, str]:
        """Return information about the source"""
        return {
            "name": "Q&A Scraper",
            "description": "Extracts Q&A content from X posts and other sources",
            "version": "1.0.0"
        }
        
    def scrape_from_x(self, username: str, filter_pattern: str = "ask.fm") -> List[Dict[str, Any]]:
        """
        Scrape Q&A content from X posts
        
        Args:
            username: X username to scrape
            filter_pattern: Regex pattern to filter posts (default: "ask.fm")
            
        Returns:
            List of Q&A dictionaries
        """
        try:
            # Use the X timeline scraper to get posts from the user
            scraped_data = self.x_scraper.scrape_page(username)
            
            # Filter posts containing the specified pattern
            pattern = re.compile(filter_pattern, re.IGNORECASE)
            qa_posts = []
            
            for post in scraped_data["posts"]:
                if pattern.search(post["text"]):
                    qa_posts.append(post)
            
            # Extract Q&A pairs from the filtered posts
            qa_pairs = []
            for post in qa_posts:
                extracted_pairs = self._extract_qa_from_x_post(post)
                qa_pairs.extend(extracted_pairs)
                
            # Limit to max_qa_per_source
            qa_pairs = qa_pairs[:self.max_qa_per_source]
            
            return {
                "username": username,
                "source": "x_qa",
                "qa_count": len(qa_pairs),
                "qa_pairs": qa_pairs,
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping Q&A from X for {username}: {str(e)}")
            raise
    
    def scrape_from_askfm(self, username: str) -> Dict[str, Any]:
        """
        Scrape Q&A content directly from ask.fm
        
        Args:
            username: ask.fm username to scrape
            
        Returns:
            Dictionary with Q&A pairs
        """
        try:
            url = f"https://ask.fm/{username}"
            soup = scrape_util.scrape_url(url)
            
            qa_pairs = []
            qa_elements = soup.select(".questionBox")
            
            for qa_element in qa_elements:
                try:
                    question_elem = qa_element.select_one(".question")
                    answer_elem = qa_element.select_one(".answer")
                    
                    if question_elem and answer_elem:
                        question = scrape_util.html_to_text(question_elem).strip()
                        answer = scrape_util.html_to_text(answer_elem).strip()
                        
                        if question and answer:
                            qa_pairs.append({
                                "question": question,
                                "answer": answer,
                                "source_url": url,
                                "timestamp": datetime.now().isoformat()
                            })
                except Exception as e:
                    logger.warning(f"Error extracting Q&A element: {str(e)}")
                    continue
                    
            # Limit to max_qa_per_source
            qa_pairs = qa_pairs[:self.max_qa_per_source]
            
            return {
                "username": username,
                "source": "askfm",
                "qa_count": len(qa_pairs),
                "qa_pairs": qa_pairs,
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping Q&A from ask.fm for {username}: {str(e)}")
            raise
    
    def scrape_from_custom_site(self, url: str, question_selector: str, answer_selector: str) -> Dict[str, Any]:
        """
        Scrape Q&A content from a custom website using CSS selectors
        
        Args:
            url: URL of the Q&A page
            question_selector: CSS selector for question elements
            answer_selector: CSS selector for answer elements
            
        Returns:
            Dictionary with Q&A pairs
        """
        try:
            soup = scrape_util.scrape_url(url)
            
            qa_pairs = []
            question_elements = soup.select(question_selector)
            answer_elements = soup.select(answer_selector)
            
            # Ensure we have matching question-answer pairs
            min_length = min(len(question_elements), len(answer_elements))
            
            for i in range(min_length):
                question = scrape_util.html_to_text(question_elements[i]).strip()
                answer = scrape_util.html_to_text(answer_elements[i]).strip()
                
                if question and answer:
                    qa_pairs.append({
                        "question": question,
                        "answer": answer,
                        "source_url": url,
                        "timestamp": datetime.now().isoformat()
                    })
                    
            # Limit to max_qa_per_source
            qa_pairs = qa_pairs[:self.max_qa_per_source]
            
            return {
                "source": "custom_site",
                "url": url,
                "qa_count": len(qa_pairs),
                "qa_pairs": qa_pairs,
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping Q&A from custom site {url}: {str(e)}")
            raise
    
    def _extract_qa_from_x_post(self, post: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract Q&A pairs from a single X post
        
        Args:
            post: X post dictionary
            
        Returns:
            List of extracted Q&A pairs
        """
        qa_pairs = []
        text = post.get("text", "")
        
        # Common patterns for Q&A in X posts
        patterns = [
            # askfm style: "Q: question\nA: answer"
            r"Q:\s*(.+?)[\n\r]+A:\s*(.+?)(?:$|[\n\r]+Q:)",
            # Generic Q&A format: "Question: question\nAnswer: answer"
            r"Question:\s*(.+?)[\n\r]+Answer:\s*(.+?)(?:$|[\n\r]+Question:)",
            # Alternative format with quotes: "Q: "question"\nA: "answer""
            r'Q:\s*"(.+?)"[\n\r]+A:\s*"(.+?)"',
            # Simple Q&A with just Q and A indicators
            r"Q\s*[:.-]?\s*(.+?)[\n\r]+A\s*[:.-]?\s*(.+?)(?:$|[\n\r]+Q)"
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    question = match.group(1).strip()
                    answer = match.group(2).strip()
                    
                    if question and answer:
                        # Create a structured Q&A entry
                        qa_pair = {
                            "question": question,
                            "answer": answer,
                            "source": "x_post",
                            "post_id": post.get("id"),
                            "timestamp": post.get("created_at"),
                            "engagement": {
                                "likes": post.get("like_count", 0),
                                "retweets": post.get("retweet_count", 0),
                                "replies": post.get("reply_count", 0)
                            }
                        }
                        
                        # Extract hashtags if present in the post
                        if "hashtags" in post:
                            qa_pair["tags"] = post["hashtags"]
                            
                        qa_pairs.append(qa_pair)
                except Exception as e:
                    logger.warning(f"Error parsing Q&A match: {str(e)}")
                    continue
        
        # If we found ask.fm links, try to extract Q&A directly
        askfm_pattern = r"https?://ask\.fm/\w+/answers/(\d+)"
        askfm_matches = re.finditer(askfm_pattern, text)
        
        for match in askfm_matches:
            try:
                answer_id = match.group(1)
                answer_url = match.group(0)
                
                # Attempt to scrape the specific ask.fm answer
                qa_pair = self._scrape_askfm_answer(answer_url)
                if qa_pair:
                    # Add metadata from the X post
                    qa_pair["source"] = "askfm_via_x"
                    qa_pair["post_id"] = post.get("id")
                    qa_pair["timestamp"] = post.get("created_at")
                    
                    if "hashtags" in post:
                        qa_pair["tags"] = post["hashtags"]
                        
                    qa_pairs.append(qa_pair)
                    
            except Exception as e:
                logger.warning(f"Error extracting ask.fm answer: {str(e)}")
                continue
        
        return qa_pairs
    
    def _scrape_askfm_answer(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a specific ask.fm answer
        
        Args:
            url: URL to the ask.fm answer
            
        Returns:
            Q&A pair dictionary or None if extraction failed
        """
        try:
            soup = scrape_util.scrape_url(url)
            
            question_elem = soup.select_one(".question")
            answer_elem = soup.select_one(".answer")
            
            if question_elem and answer_elem:
                question = scrape_util.html_to_text(question_elem).strip()
                answer = scrape_util.html_to_text(answer_elem).strip()
                
                if question and answer:
                    return {
                        "question": question,
                        "answer": answer,
                        "source_url": url
                    }
            
            return None
        except Exception as e:
            logger.warning(f"Error scraping ask.fm answer {url}: {str(e)}")
            return None
    
    def format_for_database(self, qa_data: Dict[str, Any], novel_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Format scraped Q&A data for database storage
        
        Args:
            qa_data: Scraped Q&A data
            novel_id: Optional novel ID to associate with the Q&A data
            
        Returns:
            List of Q&A entries formatted for database storage
        """
        formatted_entries = []
        
        for qa_pair in qa_data.get("qa_pairs", []):
            # Extract tags from hashtags if available
            tags = qa_pair.get("tags", [])
            if not tags and "hashtags" in qa_pair:
                tags = qa_pair["hashtags"]
                
            # Format the entry for the database
            entry = {
                "question": qa_pair["question"],
                "answer": qa_pair["answer"],
                "source": qa_data.get("source", "unknown"),
                "source_url": qa_pair.get("source_url", ""),
                "tags": tags,
                "timestamp": qa_pair.get("timestamp", datetime.now().isoformat()),
            }
            
            # Add novel ID if provided
            if novel_id:
                entry["novel_id"] = novel_id
                
            # Add key points for token efficiency
            entry["key_points"] = self._extract_key_points(qa_pair["answer"])
                
            formatted_entries.append(entry)
            
        return formatted_entries
    
    def _extract_key_points(self, text: str, max_points: int = 3) -> List[str]:
        """
        Extract key points from text for token-efficient storage
        
        Args:
            text: Text to extract key points from
            max_points: Maximum number of key points to extract
            
        Returns:
            List of key points
        """
        # Split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Filter out very short sentences
        sentences = [s for s in sentences if len(s.split()) > 3]
        
        # If we have very few sentences, return them all
        if len(sentences) <= max_points:
            return sentences
        
        # Select sentences that likely contain key information
        key_indicators = [
            "important", "key", "critical", "essential", "significant",
            "primarily", "mainly", "especially", "notably", "particularly",
            "in summary", "to summarize", "in conclusion", "finally"
        ]
        
        scored_sentences = []
        for sentence in sentences:
            score = 0
            # Score based on key indicator words
            for indicator in key_indicators:
                if indicator.lower() in sentence.lower():
                    score += 2
                    
            # Score based on sentence position (first and last sentences often contain key info)
            if sentence == sentences[0]:
                score += 2
            elif sentence == sentences[-1]:
                score += 2
                
            # Score based on sentence length (not too short, not too long)
            words = len(sentence.split())
            if 5 <= words <= 20:
                score += 1
                
            scored_sentences.append((score, sentence))
            
        # Sort by score (descending) and take top max_points
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        key_points = [sentence for score, sentence in scored_sentences[:max_points]]
        
        return key_points