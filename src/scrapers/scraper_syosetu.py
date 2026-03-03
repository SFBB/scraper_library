"""
Scraper implementation for Syosetu (Japanese novel site)
"""

import os
import sys
from typing import Any, Dict, List

# Add correct path for imports
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from interfaces import NovelScraper
from scrape_util import scrape_util


class ScraperSyosetu(NovelScraper):
    """Scraper for Syosetu (Japanese novel site)"""

    def __init__(self, **kwargs):
        """Initialize the scraper"""
        super().__init__(**kwargs)
        self.base_url = "https://ncode.syosetu.com"

    def get_source_info(self) -> Dict[str, str]:
        """Return information about the source website"""
        return {
            "name": "Syosetu",
            "url": self.base_url,
            "language": "Japanese",
            "type": "text",
        }

    def get_novel_info(self, url: str) -> Dict[str, Any]:
        """Get basic novel information"""
        page = scrape_util.scrape_url(url, "html.parser")

        try:
            # Extract title
            title_elem = page.select("p.novel_title")
            if title_elem:
                title = title_elem[0].text.strip()
            else:
                # Try alternative selector
                title_elem = page.select("title")
                title = (
                    title_elem[0].text.strip().split(" - ")[0]
                    if title_elem
                    else "Unknown Title"
                )

            # Extract author
            author_selectors = [
                "div.novel_writername a",
                "div.novel_writername",
                "div.p-novel__author a",
                "div.p-novel__author",
                ".p-eplist__author",
            ]
            
            author = "Unknown Author"
            for selector in author_selectors:
                elements = page.select(selector)
                if elements:
                    author_text = elements[0].text.strip()
                    # Clean up common prefixes
                    for prefix in ["作者：", "作者:", "Author:", "Author："]:
                        if author_text.startswith(prefix):
                            author_text = author_text[len(prefix):].strip()
                    if author_text:
                        author = author_text
                        break

            # Extract description
            description_elem = page.select("div#novel_ex")
            description = (
                scrape_util.html_to_text(description_elem[0]).strip()
                if description_elem
                else ""
            )

            return {
                "title": title,
                "author": author,
                "description": description,
                "url": url,
                "source_website": "Syosetu",
            }
        except Exception as e:
            raise ValueError(f"Failed to extract novel info: {str(e)}")

    def get_index_pages(self, url: str) -> List[str]:
        """Get list of index pages containing chapter links"""
        page = scrape_util.scrape_url(url, "html.parser")
        try:
            last_page = page.select("div.c-pager a.c-pager__item--last")
            if last_page:
                last_page = last_page[0]["href"]
                last_page = int(last_page.split("=")[-1])
            else:
                last_page = 0
        except Exception as e:
            raise ValueError(f"Failed to extract index pages: {str(e)}")

        urls = [url]
        if url.endswith("/"):
            url = url[:-1]
        if last_page > 1:
            for i in range(last_page - 1):
                urls.append(f"{url}/?p={i + 2}")
        return urls

    def get_chapter_urls(self, index_url: str) -> List[str]:
        """Get list of chapter URLs from an index page"""
        page = scrape_util.scrape_url(index_url, "html.parser")

        try:
            chapter_links = (
                page.select("a.subtitle")
                or page.select("a.p-eplist__subtitle")
                or page.select("dl.novel_sublist2 a")
            )

            return [
                f"{self.base_url}{link['href']}"
                for link in chapter_links
                if "href" in link.attrs
            ]
        except Exception as e:
            raise ValueError(f"Failed to extract chapter URLs: {str(e)}")

    def get_index_structure(self, url: str) -> List[Dict[str, Any]]:
        """Get the hierarchical structure of the novel (parts and chapters)"""
        index_pages = self.get_index_pages(url)
        structure = []

        for index_url in index_pages:
            page = scrape_util.scrape_url(index_url, "html.parser")
            
            # Find all potential index items (chapters and parts)
            # In Syosetu, parts are 'div.chapter_title' and chapters are 'dl.novel_sublist2'
            # Or in the newer layout, they might be different
            
            # Use a more general approach: iterate through children of the index box
            index_box = page.select_one("div.index_box") or page.select_one("div.p-eplist")
            
            if not index_box:
                # Fallback to the old method if we can't find the container
                chapter_urls = self.get_chapter_urls(index_url)
                for curl in chapter_urls:
                    structure.append({"type": "chapter", "url": curl, "title": ""})
                continue

            for element in index_box.children:
                if element.name == "div" and ("chapter_title" in element.get("class", []) or "p-eplist__chapter-title" in element.get("class", [])):
                    structure.append({
                        "type": "volume",
                        "title": element.text.strip()
                    })
                elif element.name == "dl" and ("novel_sublist2" in element.get("class", [])):
                    link = element.select_one("a")
                    if link and "href" in link.attrs:
                        structure.append({
                            "type": "chapter",
                            "url": f"{self.base_url}{link['href']}",
                            "title": link.text.strip()
                        })
                elif element.name == "div" and ("p-eplist__sublist" in element.get("class", [])):
                    link = element.select_one("a.p-eplist__subtitle")
                    if link and "href" in link.attrs:
                        structure.append({
                            "type": "chapter",
                            "url": f"{self.base_url}{link['href']}",
                            "title": link.text.strip()
                        })

        return structure

    def get_chapter_content(self, chapter_url: str) -> Dict[str, Any]:
        """Get content from a chapter URL"""
        page = scrape_util.scrape_url(chapter_url)

        try:
            # Try multiple possible selectors for chapter title
            title_selectors = [
                ".novel_subtitle",
                ".p-novel__subtitle",
                "h1.novel_title",
                "h2.novel_subtitle",
            ]

            chapter_title = ""
            for selector in title_selectors:
                elements = page.select(selector)
                if elements:
                    chapter_title = elements[0].text.strip()
                    break

            # If still no title found, try to get it from the URL or page title
            if not chapter_title:
                # Try to get from page title
                title_element = page.select("title")
                if title_element:
                    full_title = title_element[0].text.strip()
                    if " - " in full_title:
                        chapter_title = full_title.split(" - ")[1]

            # Try multiple possible selectors for chapter content
            content_selectors = [
                "#novel_honbun",
                "#novel_color",
                ".novel_view",
                ".p-novel__body",
                ".p-novel_main",
            ]

            chapter_content = ""
            for selector in content_selectors:
                elements = page.select(selector)
                if elements:
                    chapter_content = scrape_util.html_to_text(elements[0])
                    break

            if not chapter_title or not chapter_content:
                raise ValueError("Could not find chapter title or content")

            return {
                "title": chapter_title,
                "content": chapter_content,
                "url": chapter_url,
            }
        except Exception as e:
            raise ValueError(f"Failed to extract chapter content: {str(e)}")
