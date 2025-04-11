from scrape_util import scrape_util
from scraper_base import scraper_novel_with_saving
from selenium import webdriver


WEB_URL = "https://ncode.syosetu.com"
URL = "https://ncode.syosetu.com/n2267be/"
BOOK_TITLE = "Ｒｅ：ゼロから始める異世界生活"
AUTHOR_NAME = "鼠色猫長月達平"

class scraper_syosetu(scraper_novel_with_saving):
    def __init__(self, web_url, url, book_title, author_name, **kwargs):
        super(scraper_syosetu, self).__init__(**kwargs)
        self.web_url = web_url
        self.url = url
        self.book_title = book_title
        self.author_name = author_name
        self.file_name = "{} - {}.txt".format(self.book_title, self.author_name)

    def scrape_index_list(self, url: str) -> list[str]:
        return [url]

    def scrape_chapter_list(self, page_index_url: str) -> list[str]:
        chapter_url_list = []
        page = scrape_util.scrape_url(page_index_url, "html.parser")
        chapter_links = page.select("a.p-eplist__subtitle")
        print(f"Found {len(chapter_links)} chapter links")
        for chapter_link in chapter_links:
            chapter_url = "{}{}".format(self.web_url, chapter_link["href"])
            chapter_url_list.append(chapter_url)
        return chapter_url_list

    def scrape_chatper(self, chapter_url: str) -> str:
        page = scrape_util.scrape_url(chapter_url)
        try:
            # Try multiple possible selectors for chapter title
            title_selectors = [
                ".novel_subtitle",
                ".p-novel__subtitle", 
                "h1.novel_title",
                "h2.novel_subtitle"
            ]
            
            chapter_name = ""
            for selector in title_selectors:
                elements = page.select(selector)
                if elements:
                    chapter_name = elements[0].text.strip()
                    break
            
            # If still no title found, try to get it from the URL or page title
            if not chapter_name:
                # Try to get from page title
                title_element = page.select("title")
                if title_element:
                    full_title = title_element[0].text.strip()
                    if " - " in full_title:
                        chapter_name = full_title.split(" - ")[1]
            
            # Try multiple possible selectors for chapter content
            content_selectors = [
                "#novel_honbun", 
                "#novel_color", 
                ".novel_view",
                ".p-novel__body",
                ".p-novel_main"
            ]
            
            chapter_text = ""
            for selector in content_selectors:
                elements = page.select(selector)
                if elements:
                    chapter_text = scrape_util.html_to_text(elements[0])
                    break
            
            if not chapter_name or not chapter_text:
                raise ValueError("Could not find chapter title or content")
                
            return "{}\n\n\n{}\n\n\n\n\n\n".format(chapter_name, chapter_text)
        except Exception as e:
            print(f"Error scraping chapter {chapter_url}: {str(e)}")
            print("HTML structure might be different than expected.")
            return f"ERROR: Could not scrape chapter {chapter_url}. {str(e)}"

if __name__ == "__main__":
    # WEB_URL = input("The web url is: ")
    # URL = input("The book url is: ")
    # BOOK_TITLE = input("The book title is: ")
    # AUTHOR_NAME = input("The author name is: ")
    scraper_syosetu(WEB_URL, URL, BOOK_TITLE, AUTHOR_NAME).run()
