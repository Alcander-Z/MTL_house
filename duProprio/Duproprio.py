import os
import requests
from bs4 import BeautifulSoup
from queue import Queue
from time import sleep


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Crawler(object):

    def __init__(self, max_page=1):
        # max search pages to crawl
        self.max_pages = max_page
        # house page url pools
        self.url_pool = list()
        # to-save file directory
        self.file_path = os.path.join(BASE_DIR, 'jsonfiles')
        os.makedirs(self.file_path, exist_ok=True)
        # base url to crawl, need .format(prev_page, current_page)
        self.base_url = 'https://duproprio.com/en/search/list?search=true&is_for_sale=1&' \
                   'with_builders=1&parent={}&pageNumber={}&sort=-published_at'
        # buffer for house information
        self.data = list()

    def start(self):
        for page in range(1, self.max_pages+1):
            if page == 1:
                prev_page = 1
            else:
                prev_page = page - 1

        url = self.base_url.format(prev_page, page)

        self._parse_search_page(self._request(url))

        while self.url_pool:
            url = self.url_pool.pop(0)
            house = self._parser_house_page(self._request(url))
            self.data.append(house)

    def _request(self, url, waittime=1):
        sleep(waittime)

        try:
            html = requests.get(url).text
            soup = BeautifulSoup(html, 'html.parser')
        except Exception:
            # todo: add logger
            soup = None

        return soup

    def _parse_search_page(self, soup):

        def find_all_listings(tag):
            condition = False
            if tag.name == 'li' and tag.has_attr('id'):
                if tag['id'].startswith('listing'):
                    condition = True
            return condition

        listings = soup.find_all(find_all_listings)
        for item in listings:
            self.url_pool.append(item.a['href'])

    def _parser_house_page(self, soup):
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
        character = {
            'bedrooms': 0.0,
            'bathrooms': 0.0,
            'level': None,
            'area': None,
        }
        characteristics_tag = soup.find('div', attrs={'class': "listing-main-characteristics"})
        for item in characteristics_tag.find_all('div', attrs={'class': "listing-main-characteristics__item"}):
            elems = item.find_all('span')
            key = elems[-1].string.strip()
            value = elems[0].string.strip()
            if key == 'bedroom':
                character['bedrooms'] = float(value)
            elif key == 'bedrooms':
                character['bedrooms'] = float(value)
            elif key == 'bathroom':
                character['bathrooms'] = float(value)
            elif key == 'half bath':
                character['bathrooms'] += 0.5
            elif key == 'level':
                character['level'] = int(value)
            elif value == 'Living space area (basement exclu.)':
                character['area'] = float(key.split()[0])
            elif value == 'Lot dimensions':
                if not character['area']:
                    character['area'] = float(key.split()[0])

        # find detail
        detail = {
            'ownership': None,
            'floor_if_condo': None,
            'municipal': None,
            'backyard': None,
            'year': None,
        }
        detail_tag = soup.find('div', attrs={'class': "listing-list-characteristics__viewport"})
        for item in detail_tag.find_all('div', attrs={'class': "listing-box__dotted-row"}):
            elems = item.find_all('div')
            key = elems[0].string.strip()
            value = elems[-1].string.strip()
            if key == 'Ownership':
                detail['ownership'] = value
            elif key == 'Located on which floor? (if condo)':
                detail['floor_if_condo'] = int(value)
            elif key == 'Municipal Assessment':
                detail['municipal'] = int(value[1:].replace(',', ''))
            elif key == 'Backyard Faces':
                detail['backyard'] = value
            elif key == 'Year of construction':
                detail['year'] = int(value)

        return {
            'category': category,
            'price': price,
            'address': address,
            **character,
            **detail
        }


if __name__ == "__main__":
    crawler = Crawler()

    soup = BeautifulSoup(open(r'sample_house.html', 'r'), 'html.parser')

    data = crawler.parser_house_page(soup)

    from pprint import pprint

    pprint(data)
