from abc import ABC, abstractmethod
from scrape_util import scrape_util, multi_thread_scrape
from tqdm import tqdm
import os
import threading



class scraper_base(ABC):
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def run(self):
        pass

class scraper_base_with_saving(scraper_base):
    def __init__(self, **kwargs):
        super(scraper_base_with_saving, self).__init__(**kwargs)
        self.file_name = ""

    def run(self):
        try:
            # self.file_has_existed = os.path.exists(self.file_name)
            self.run_with_saving()
        except Exception as e:
            self.clean_file()
            raise e

    @abstractmethod
    def run_with_saving(self):
        pass

    def clean_file(self):
        # if os.path.exists(self.file_name) and not self.file_has_existed:
        if os.path.exists(self.file_name):
            os.remove(self.file_name)

class scraper_novel_with_saving(scraper_base_with_saving):
    def __init__(self, **kwargs):
        super(scraper_novel_with_saving, self).__init__(**kwargs)
        self.web_url = ""
        self.url = ""
        self.book_title = ""
        self.author_name = ""
        self.max_thread_num = 6

    def run_with_saving(self):
        text_file_name = self.file_name
        with open(text_file_name, "w") as file:
            file.write("{}\n\n\n{}\n\n\n\n\n\n\n\n\n".format(self.book_title, self.author_name))

        print("We are building index page list right now...")
        page_index_url_list = self.scrape_index_list(self.url)

        print("There are {} pages to list all chapter index.".format(len(page_index_url_list)))
        print("We are building chapter url list right now...")

        chapter_url_list= []
        if len(page_index_url_list) < 12:
            for i, page_index_url in enumerate(page_index_url_list):
                chapter_url_list_on_this_page = self.scrape_chapter_list(page_index_url)
                print("\t[{}/{}] This index page has {} chapters...".format(i+1, len(page_index_url_list), len(chapter_url_list_on_this_page)))
                chapter_url_list += chapter_url_list_on_this_page
        else: # we use multi thread to spped up

            class multi_thread_scrape_chapter_list(multi_thread_scrape):
                def __init__(self, max_thread_num, scraping_list, method):
                    super(multi_thread_scrape_chapter_list, self).__init__(max_thread_num, scraping_list, method)
                
                def scrape_handle(self, url: str, index: int, scraped_records: dict[int, list[str]]):
                    scraped_records[index] = self.method(url)
                
                def chunk_handle(self, chunk_start_index: int, chunk: list[str], scraped_records: dict[int, list[str]]):
                    index_list = []
                    for ii, url in enumerate(chunk):
                        index_list += scraped_records[chunk_start_index + ii]
                        print("\t[{}/{}] This index page has {} chapters...".format(chunk_start_index + ii, len(self.scraping_list), len(scraped_records[chunk_start_index + ii])))
                    return index_list

            scrape_chapter_list_mt = multi_thread_scrape_chapter_list(self.max_thread_num, page_index_url_list, self.scrape_chapter_list)
            scrape_chapter_list_mt.run()
            chapter_url_list = scrape_chapter_list_mt.get_result()

        print("We have found {} chapters.".format(len(chapter_url_list)))
        print("We are scraping per chapter content...")

        with tqdm(total=len(chapter_url_list)) as pbar:
            if len(chapter_url_list) < 12:
                for i, chapter_url in enumerate(chapter_url_list):
                    chapter_content = self.scrape_chatper(chapter_url)
                    self.write_file_handle(i, chapter_url, chapter_content)
                    pbar.update(1)
                    pbar.set_description("Scraping {} of {} chapters".format(i+1, len(chapter_url_list)))

            else: # we use multi thread to spped up
    
                class multi_thread_scrape_chapter(multi_thread_scrape):
                    def __init__(self, max_thread_num, scraping_list, method, pbar, write_op):
                        super(multi_thread_scrape_chapter, self).__init__(max_thread_num, scraping_list, method)
                        self.pbar = pbar
                        self.write_op = write_op
                    
                    def scrape_handle(self, url: str, index: int, scraped_records: dict[int, list[str]]):
                        scraped_records[index] = [self.method(url)]
                    
                    def chunk_handle(self, chunk_start_index: int, chunk: list[str], scraped_records: dict[int, list[str]]):
                        pbar.update(len(chunk))
                        pbar.set_description("Scraping {} of {} chapters".format(chunk_start_index+len(chunk), len(self.scraping_list)))
                        for ii, url in enumerate(chunk):
                            if chunk_start_index + ii not in scraped_records:
                                print("We have missed {} whose index is {}!". format(url, chunk_start_index+ii))
                                continue
                            self.write_op(ii, url, scraped_records[chunk_start_index + ii][0])
                        return []

                scrape_chapter_mt = multi_thread_scrape_chapter(self.max_thread_num, chapter_url_list, self.scrape_chatper, pbar, self.write_file_handle)
                scrape_chapter_mt.run()

        print("We have finished scaping this book.")
        print("It saves as {}/{}.".format(os.getcwd(), text_file_name))

    @abstractmethod
    def scrape_index_list(self, url: str) -> list[str]:
        pass

    @abstractmethod
    def scrape_chapter_list(self, page_index_url: str) -> list[str]:
        pass

    @abstractmethod
    def scrape_chatper(self, chapter_url: str):
        pass

    def write_file_handle(self, index: int, chapter_url: str, content):
        with open(self.file_name, "a") as file:
            file.write("{}".format(content))
