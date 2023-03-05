from scrape_util import scrape_util
from scraper_base import scraper_novel_with_saving



WEB_URL = "https://www.quanben.io"
URL = "https://www.quanben.io/n/nuanqichengyin/list.html"
BOOK_TITLE = "暖妻成瘾(全本)"
AUTHOR_NAME = "程小一"

class scraper_quanben(scraper_novel_with_saving):
    def __init__(self, web_url, url, book_title, author_name, **kwargs):
        super(scraper_quanben, self).__init__(**kwargs)
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
        chatper_url_end = str(page.select("li")[-1].select("a")[0]["href"])
        for i in range(1, int(chatper_url_end.replace("/n/nuanqichengyin/", "").replace(".html", "")) + 1):
            chapter_url_list.append("{}/n/nuanqichengyin/{}.html".format(self.web_url, i))
        return chapter_url_list

    def scrape_chatper(self, chapter_url: str) -> str:
        page = scrape_util.scrape_url(chapter_url)
        chapter_name = page.select("h1.headline")[0].text
        chapter_text = scrape_util.html_to_text(page.select("div.articlebody")[0])
        return "{}\n\n\n{}\n\n\n\n\n\n".format(chapter_name, chapter_text)

if __name__ == "__main__":
    WEB_URL = input("The web url is: ")
    URL = input("The book url is: ")
    BOOK_TITLE = input("The book title is: ")
    AUTHOR_NAME = input("The author name is: ")
    scraper_quanben(WEB_URL, URL, BOOK_TITLE, AUTHOR_NAME).run()
