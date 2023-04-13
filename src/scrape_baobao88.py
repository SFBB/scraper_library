from scrape_util import scrape_util, driver_type
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper_base import scraper_audio_novel_with_saving
import json



WEB_URL = "http://www.baobao88.com"
URL = "http://www.baobao88.com/lianbo/1384.html"
BOOK_TITLE = "达芬奇密码"
AUTHOR_NAME = "丹·布朗"

class baobao88(scraper_audio_novel_with_saving):
    def __init__(self, web_url, url, book_title, author_name, **kwargs):
        super(baobao88, self).__init__(**kwargs)
        self.web_url = web_url
        self.url = url
        self.book_title = book_title
        self.author_name = author_name
        self.folder_name = "{} - {}".format(self.book_title, self.author_name)
        self.file_name = self.folder_name
        self.suffix = "mp3"
        if self.url.endswith("/"):
            self.url = self.url[:-1]

    def scrape_index_list(self, url: str) -> list[str]:
        return [url]

    def scrape_chapter_list(self, page_index_url: str) -> list[str]:
        page = scrape_util.scrape_url(page_index_url)
        plist = page.select("li.list_t2")
        
        chapter_url_list = []
        for p in plist:
            chapter_url_list.append("{}".format(p.select("a")[0].text))
        return chapter_url_list

    def scrape_chatper(self, chapter_url: str) -> dict[str, str]:
        audio_path = "{}/{}.mp3".format("http://play.baobao88.com/bbfile/media/000007/%E5%B0%8F%E8%AF%B4", chapter_url)
        play_info = {}
        play_info["path"] = audio_path
        play_info["title"] = chapter_url
        return play_info


if __name__ == "__main__":
    WEB_URL = input("The web url is: ")
    URL = input("The book url is: ")
    BOOK_TITLE = input("The book title is: ")
    AUTHOR_NAME = input("The author name is: ")
    baobao88(WEB_URL, URL, BOOK_TITLE, AUTHOR_NAME).run()
