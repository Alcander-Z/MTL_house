import os
import requests
from bs4 import BeautifulSoup
from queue import Queue
from time import sleep


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Crawler(object):

    def __init__(self):
        self.url_pool = list()
        self.file_path = os.path.join(BASE_DIR, 'jsonfiles')
        self.base_url = 'https://duproprio.com/en/search/list?search=true&is_for_sale=1&' \
                   'with_builders=1&parent={}&pageNumber={}&sort=-published_at'
        self.max_pages = 1
        self.data = list()

    def start(self):
        for page in range(1, self.max_pages+1):
            if page == 1:
                prev_page = 1
            else:
                prev_page = page - 1

        url = self.base_url.format(prev_page, page)

        self.parse_search_page(self.request(url))

        while self.url_pool:
            url = self.url_pool.pop(0)
            house = self.parser_house_page(self.request(url))
            self.data.append(house)

    def request(self, url, waittime=1):
        sleep(waittime)

        try:
            html = requests.get(url).text
            soup = BeautifulSoup(html, 'html.parser')
        except Exception:
            # todo: add logger
            soup = None

        return soup

    def parse_search_page(self, soup):

        def find_all_listings(tag):
            condition = False
            if tag.name == 'li' and tag.has_attr('id'):
                if tag['id'].startswith('listing'):
                    condition = True
            return condition

        listings = soup.find_all(find_all_listings)
        for item in listings:
            self.url_pool.append(item.a['href'])

    def parser_house_page(self, soup):
        # find price
        price_tag = soup.find('div', attrs={'class': "listing-price__amount"})
        for string in price_tag.stripped_strings:
            price = string[1:].replace(',', '')

        # find category
        category_tag = soup.find('h3', attrs={'class': "listing-location__title"})
        for string in category_tag.a.stripped_strings:
            category = string.split(' ')[0]

        # find address
        meta = {}
        address_tag = soup.find('div', attrs={'class': "listing-location__group-address"})
        for m in address_tag.find_all('meta'):
            meta[m['property'].strip()] = m['content']
        address = "{}, {}, {}, {}".format(
            meta['streetAddress'], meta['addressLocality'],
            meta['addressRegion'], meta['postalCode']
        )

        # find characteristics
        character = {}
        characteristics_tag = soup.find('div', attrs={'class': "listing-main-characteristics"})
        for item in characteristics_tag.find_all('div', attrs={'class': "listing-main-characteristics__item"}):
            elems = item.find_all('span')
            key = elems[-1].string.strip()
            val = elems[0].string.strip()
            if key in ['bedroom', 'bedrooms', 'bathroom', 'bathrooms', 'half bath', 'level']:
                character[key] = val

        # find detail
        detail = {}
        detail_tag = soup.find('div', attrs={'class': "listing-list-characteristics__viewport"})
        for item in detail_tag.find_all('div', attrs={'class': "listing-box__dotted-row"}):
            elems = item.find_all('div')
            key = elems[0].string.strip()
            val = elems[-1].string.strip()
            if key in ['Ownership', 'Located on which floor? (if condo)',
                       'Municipal Assessment', 'Backyard Faces', 'Year of construction']:
                detail[key] = val

        return {
            'category': category,
            'price': price,
            'address': address,
            **character,
            **detail
        }


if __name__ == "__main__":
    crawler = Crawler()

    crawler.start()

    from pprint import pprint

    pprint(crawler.data)
