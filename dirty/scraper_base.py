from abc import ABC, abstractmethod
from scrape_util import scrape_util
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

            def scrape_index_list_threaded(page_index_url: str, records: dict[str, list[str]]):
                records[page_index_url] = self.scrape_chapter_list(page_index_url)
            
            page_index_url_list_chunked = scrape_util.divide_chunks(page_index_url_list, self.max_thread_num)
            page_index_url_list_scraped_records = {}
            for i, chunk in enumerate(page_index_url_list_chunked):
                scrape_index_thread_list = []
                for page_index_url in chunk:
                    thread = threading.Thread(target=scrape_index_list_threaded, args=(page_index_url,page_index_url_list_scraped_records,))
                    scrape_index_thread_list.append(thread)
                    thread.start()
                for thread in scrape_index_thread_list:
                    thread.join()
                for ii, page_index_url in enumerate(chunk):
                    print("\t[{}/{}] This index page has {} chapters...".format(i*self.max_thread_num+ii+1, len(page_index_url_list), len(page_index_url_list_scraped_records[page_index_url])))
                    chapter_url_list += page_index_url_list_scraped_records[page_index_url]

        print("We have found {} chapters.".format(len(chapter_url_list)))
        print("We are scraping per chapter content...")

        with open(text_file_name, "a") as file:
            with tqdm(total=len(chapter_url_list)) as pbar:
                if len(chapter_url_list) < 12:
                    for i, chapter_url in enumerate(chapter_url_list):
                        chapter_content = self.scrape_chatper(chapter_url)
                        file.write("{}".format(chapter_content))
                        pbar.update(1)
                        pbar.set_description("Scraping {} of {} chapters".format(i+1, len(chapter_url_list)))

                else: # we use multi thread to spped up
        
                    def scrape_chapter_list_threaded(chapter_url: str, index: int, records: dict[int, list[str]]):
                            records[index] = self.scrape_chatper(chapter_url)

                    chapter_url_list_chunked = scrape_util.divide_chunks(chapter_url_list, self.max_thread_num)
                    scraped_chapter_records = {}
                    for i, chunk in enumerate(chapter_url_list_chunked):
                        scrape_chapter_thread_list = []
                        for ii, chapter_url in enumerate(chunk):
                            thread = threading.Thread(target=scrape_chapter_list_threaded, args=(chapter_url,i*self.max_thread_num+ii,scraped_chapter_records,))
                            scrape_chapter_thread_list.append(thread)
                            thread.start()
                        for thread in scrape_chapter_thread_list:
                            thread.join()
                        pbar.update(len(chunk))
                        pbar.set_description("Scraping {} of {} chapters".format(i*self.max_thread_num+len(chunk), len(chapter_url_list)))
                        chunk_text = ""
                        for ii, chapter_url in enumerate(chunk):
                            if i*self.max_thread_num+ii not in scraped_chapter_records.keys():
                                print("We have missed {} whose index is {}!". format(chapter_url, i*self.max_thread_num+ii))
                                continue
                            chunk_text += scraped_chapter_records[i*self.max_thread_num+ii]
                        file.write("{}".format(chunk_text))

        print("We have finished scaping this book.")
        print("It saves as {}/{}.".format(os.getcwd(), text_file_name))

    @abstractmethod
    def scrape_index_list(self, url: str) -> list[str]:
        pass

    @abstractmethod
    def scrape_chapter_list(self, page_index_url: str) -> list[str]:
        pass

    @abstractmethod
    def scrape_chatper(self, chapter_url: str) -> str:
        pass
