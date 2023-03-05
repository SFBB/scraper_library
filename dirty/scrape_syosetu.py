from scrape_util import scrape_util
from scraper_base import scraper_novel_with_saving



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
        page = scrape_util.scrape_url(page_index_url, "xml")
        chatper_urls = page.select("dl")
        for chapter_url in chatper_urls:
            chapter_url_list.append("{}{}".format(self.web_url, chapter_url.select("dd")[0].select("a")[0]["href"]))
        return chapter_url_list

    def scrape_chatper(self, chapter_url: str) -> str:
        page = scrape_util.scrape_url(chapter_url)
        chapter_name = page.select("p.novel_subtitle")[0].text
        chapter_text = scrape_util.html_to_text(page.select("div.novel_view")[0])
        return "{}\n\n\n{}\n\n\n\n\n\n".format(chapter_name, chapter_text)

if __name__ == "__main__":
    WEB_URL = input("The web url is: ")
    URL = input("The book url is: ")
    BOOK_TITLE = input("The book title is: ")
    AUTHOR_NAME = input("The author name is: ")
    scraper_syosetu(WEB_URL, URL, BOOK_TITLE, AUTHOR_NAME).run()
