from scrape_util import scrape_util
from scraper_base import scraper_audio_novel_with_saving
import json



WEB_URL = "https://www.ximalaya.com"
URL = "https://www.ximalaya.com/album/57367509/"
BOOK_TITLE = "发型设计师杀人事件"
AUTHOR_NAME = "山村美纱"

class scraper_ximalaya(scraper_audio_novel_with_saving):
    def __init__(self, web_url, url, book_title, author_name, **kwargs):
        super(scraper_ximalaya, self).__init__(**kwargs)
        self.web_url = web_url
        self.url = url
        self.book_title = book_title
        self.author_name = author_name
        self.folder_name = "{} - {}".format(self.book_title, self.author_name)
        self.file_name = self.folder_name
        self.suffix = ".m4a"

    def scrape_index_list(self, url: str) -> list[str]:
        return [url]

    def scrape_chapter_list(self, page_index_url: str) -> list[str]:
        chapter_url_list = []
        page = scrape_util.scrape_url(page_index_url, "xml")
        chapter_urls = page.select("ul")[1].select("li")
        chapter_urls.reverse()
        print(chapter_urls[0].select("a")[0]["href"])
        for chapter_url in chapter_urls:
            chapter_url_list.append("{}".format(chapter_url.select("a")[0]["href"].split("/")[-1]))
        return chapter_url_list

    def scrape_chatper(self, chapter_url: str) -> dict[str, str]:
        metadata = scrape_util.scrape_url("https://www.ximalaya.com/tracks/{}.json".format(chapter_url))
        metadata_json = json.loads(metadata.text)
        play_path = metadata_json["play_path"]
        play_title = metadata_json["title"]
        play_info = {}
        play_info["path"] = play_path
        play_info["title"] = play_title
        return play_info


if __name__ == "__main__":
    WEB_URL = input("The web url is: ")
    URL = input("The book url is: ")
    BOOK_TITLE = input("The book title is: ")
    AUTHOR_NAME = input("The author name is: ")
    scraper_ximalaya(WEB_URL, URL, BOOK_TITLE, AUTHOR_NAME).run()
