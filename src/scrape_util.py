from abc import ABC, abstractmethod
from time import sleep
from enum import Enum
import requests
from bs4 import BeautifulSoup as Soup
from types import FunctionType
import threading
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile



class driver_type(Enum):
    Firefox = 0, "Firefox"
    Chrome = 1, "Chrome"
    def __new__(cls, value, name):
        member = object.__new__(cls)
        member._value_ = value
        return member

class scrape_util():
    @staticmethod
    def scrape_url(url, soup_features = "lxml", cookies={}, headers={}):
        while True:
            try:
                if headers == {}:
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                return Soup(requests.get(url, headers=headers, cookies=cookies, timeout=10).content, features=soup_features)
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
    def retrive_stream(url, cookies={}, headers={}):
        while True:
            try:
                if headers == {}:
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                return requests.get(url=url, headers=headers, cookies=cookies, timeout=10, stream=True)
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
    def write_stream(url, cookies={}, target_path="") -> bool:
        if target_path == "":
            return False
        while True:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                resp = requests.get(url=url, headers=headers, cookies=cookies, timeout=10, stream=True)
                with open(target_path, "wb") as file:
                    for chunk in resp.iter_content(chunk_size=512):
                        if chunk:
                            file.write(chunk)
                return True
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
    def make_webdriver(driver_type: driver_type, driver_path: str, driver_profile_path: str, headless = True):
        opts = None
        driver = None
        if driver_type == driver_type.Firefox:
            opts = webdriver.FirefoxOptions()
            opts.headless = headless
            profile = FirefoxProfile(driver_profile_path)
            driver = webdriver.Firefox(options=opts, firefox_profile=profile, executable_path=driver_path)
        if driver_type == driver_type.Chrome:
            opts = webdriver.ChromeOptions()
            opts.add_argument("user-data-dir={}".format(driver_path))
            opts.headless = headless
            driver = webdriver.Chrome(options=opts, executable_path=driver_path)
        return driver

    @staticmethod
    def scrape_url_with_webdriver(url, driver: webdriver, soup_features = "lxml"):
        try:
            if driver != None:
                driver.get(url)
                html_source_code = driver.execute_script("return document.body.innerHTML;")
                return Soup(html_source_code, features=soup_features)
            return Soup()
        except Exception as e:
            print(str(e))
            if driver != None:
                driver.quit()
            raise e

    @staticmethod
    def get_session_cookies(url, headers={}):
        while True:
            try:
                session = requests.Session()
                if headers == {}:
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                session.get(url, headers=headers, timeout=10)
                return session.cookies.get_dict(), session
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
    def post_request(url, request={}, cookies={}, headers={}, soup_features = "lxml"):
        while True:
            try:
                if headers == {}:
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
                return Soup(requests.post(url, json=request, headers=headers, cookies=cookies, timeout=10).content, features=soup_features)
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

    @staticmethod
    def parse_range(range_str: str, total_count: int) -> tuple[int, int]:
        """
        Parse a range string like '1-10', '5-', '-10', 'all' or '5'
        Returns (start_index, end_index) for slicing (0-based, end exclusive)
        """
        if not range_str or range_str.lower() == 'all':
            return 0, total_count
        
        if '-' not in range_str:
            try:
                val = int(range_str)
                # Single number N is treated as first N chapters (1-N)
                return 0, min(total_count, max(0, val))
            except ValueError:
                return 0, total_count

        parts = range_str.split('-')
        start_part = parts[0].strip()
        end_part = parts[1].strip()
        
        # If both are empty (just "-"), return all
        if not start_part and not end_part:
            return 0, total_count
            
        # Case "-10" (up to 10)
        if not start_part:
            try:
                end = int(end_part)
                return 0, min(total_count, max(0, end))
            except ValueError:
                return 0, total_count
                
        # Case "5-" (from 5 onwards)
        if not end_part:
            try:
                start = int(start_part) - 1
                return max(0, min(total_count, start)), total_count
            except ValueError:
                return 0, total_count
                
        # Case "5-10" or "10-5"
        try:
            val1 = int(start_part)
            val2 = int(end_part)
            
            start_val = min(val1, val2)
            end_val = max(val1, val2)
            
            start = max(0, start_val - 1)
            end = min(total_count, end_val)
            
            if start > total_count:
                start = total_count
            if end < 0:
                end = 0
                
            return start, end
        except ValueError:
            return 0, total_count


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
