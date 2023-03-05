from abc import ABC, abstractmethod
from time import sleep
import requests
from bs4 import BeautifulSoup as Soup
from types import FunctionType
import threading



class scrape_util():
    @staticmethod
    def scrape_url(url, soup_features = "lxml"):
        while True:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                return Soup(requests.get(url, headers=headers, timeout=10).content, features=soup_features)
            except requests.exceptions.ReadTimeout or requests.exceptions.ConnectTimeout or requests.exceptions.Timeout:
                print("Timeout, we will try again in 3s!")
                sleep(3)
            except requests.exceptions.MissingSchema or requests.exceptions.InvalidJSONError as e:
                print("Scrape_url falied with exception: {}".format(str(e)))
                raise e
            except Exception as e:
                print("Ah, damn! {} happened! We will try again in 3s!".format(str(e)))
                sleep(3)

    @staticmethod
    def html_to_text(elem):
        text = ''
        for e in elem.descendants:
            if isinstance(e, str):
                text += e.strip()
            elif e.name in ['br',  'p', 'h1', 'h2', 'h3', 'h4','tr', 'th']:
                text += '\n'
            elif e.name == 'li':
                text += '\n- '
        return text

    @staticmethod
    def divide_chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i: i+n]


class multi_thread_scrape():
    def __init__(self, max_thread_num: int, scraping_list: list[str], method: FunctionType):
        self.max_thread_num = max_thread_num
        self.scraping_list = scraping_list
        self.method = method
        self.result_list = []
        
    def run(self):
        scraping_list_chunked = scrape_util.divide_chunks(self.scraping_list, self.max_thread_num)
        scraped_records = {}
        for i, chunk in enumerate(scraping_list_chunked):
            scrape_thread_list = []
            for ii, url in enumerate(chunk):
                thread = threading.Thread(target=self.scrape_handle, args=(url, i*self.max_thread_num+ii, scraped_records))
                scrape_thread_list.append(thread)
                thread.start()
            for thread in scrape_thread_list:
                thread.join()
            self.result_list += self.chunk_handle(i*self.max_thread_num, chunk, scraped_records)

    @abstractmethod
    def scrape_handle(self, url: str, index: int, scraped_records: dict[int, list[str]]):
        pass
        
    @abstractmethod        
    def chunk_handle(self, chunk_start_index: int, chunk: list[str], scraped_records: dict[int, list[str]]) -> list[str]:
        pass

    def get_result(self) -> list[str]:
        return self.result_list
