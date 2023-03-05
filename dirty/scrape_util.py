from time import sleep
import requests
from bs4 import BeautifulSoup as Soup



class scrape_util():
    @staticmethod
    def scrape_url(url):
        while True:
            try:
                return Soup(requests.get(url, timeout=10).content, features="lxml")
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
