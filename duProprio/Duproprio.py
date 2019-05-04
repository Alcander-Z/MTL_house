import requests
from bs4 import BeautifulSoup
import csv

url = 'https://duproprio.com/en/search/list?search=true&is_for_sale=1&with_builders=1&parent=1&pageNumber=1&sort=-published_at'
r = requests.get(url).content
soup = BeautifulSoup(r,'html.parser')

links = []

urllink = soup.findAll('a')

#urllink = soup.find_all(class_='gtm-search-results-link-property search-results-listings-list__item-info-link ')

#print (urllink)


for link in urllink:
    links.append(link.get('href'))


with open('links.csv', 'w') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerows([links])
#    writer.writerows([urllink])

csvFile.close()


