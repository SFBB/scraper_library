import os
from time import sleep
import requests
from bs4 import BeautifulSoup as Soup
from tqdm import tqdm



WEB_URL = "https://69shu.net"
URL = "https://69shu.net/1/1426_30/#all"
BOOK_TITLE = "暖妻成瘾"
AUTHOR_NAME = "程小一"



def scrape_url(url):
    while True:
        try:
            return Soup(requests.get(url, timeout=10).content, features="lxml")
        except requests.exceptions.ReadTimeout:
            print("Timeout, we will try again in 3s!")
            sleep(3)
        except Exception as e:
            print("Ah, damn! {} happened! We will try again in 3s!".format(str(e)))
            sleep(3)

def parse_html(elem):
    text = ''
    for e in elem.descendants:
        if isinstance(e, str):
            text += e.strip()
        elif e.name in ['br',  'p', 'h1', 'h2', 'h3', 'h4','tr', 'th']:
            text += '\n'
        elif e.name == 'li':
            text += '\n- '
    return text



text_file_name = "{} - {}.txt".format(BOOK_TITLE, AUTHOR_NAME)
with open(text_file_name, "w") as file:
    file.write("{}\n\n\n{}\n\n\n\n\n\n\n\n\n".format(BOOK_TITLE, AUTHOR_NAME))


page_url_list = []
chapter_url_list = []


print("We are building index page list right now...")

page = scrape_url(URL)
page_options = page.select('div.listpage')[0].find_all("option")
for page_option in page_options:
    page_url_list.append("{}{}".format(WEB_URL, page_option["value"]))

print("There are {} pages to list all chapter index.".format(len(page_url_list)))
print("We are building chapter url list right now...")

for i, page_url in enumerate(page_url_list):
    page = scrape_url(page_url)
    chatper_urls = page.select("div.info_chapters ul.p2")[1].find_all("li")
    print("\t[{}/{}] This index page has {} chapters...".format(i+1, len(page_url_list), len(chatper_urls)))
    for chapter_url in chatper_urls:
        chapter_url_list.append("{}{}".format(WEB_URL, chapter_url.select("a")[0]["href"]))

print("We have found {} chapters.".format(len(chapter_url_list)))
print("We are scraping per chapter content...")

with open(text_file_name, "a") as file:
    with tqdm(total=len(chapter_url_list)) as pbar:
        for i, chapter_url in enumerate(chapter_url_list):
            page = scrape_url(chapter_url)
            chapter_name = page.select("h2")[0].text
            chapter_text = parse_html(page.select("div.novelcontent")[0])
            file.write("{}\n\n\n{}\n\n\n\n\n\n".format(chapter_name, chapter_text))
            pbar.update(1)
            pbar.set_description("Scraping {} of {} chapters".format(i+1, len(chapter_url_list)))

print("We have finished scaping this book.")
print("It saves as {}/{}.".format(os.getcwd(), text_file_name))
