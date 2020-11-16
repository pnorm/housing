# Import packages
from urllib.request import urlopen as ureq
from bs4 import BeautifulSoup as soup
import requests
import time
from datetime import date
import pandas as pd


class DataScraper:
    '''

    Args:
        type_of_market (int): 1 primary, 2 secondary market
        date (str): 'YYYY-MM-DD' format
    '''
    def __init__(self, type_of_market, date):
        self.type_of_market = type_of_market
        self.date = date
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
            }
        self.address_list = []
        self.price_list = []
        self.sq_meter_price_list = []
        self.area_list = []
        self.n_rooms_list = []
        self.floor_list = []
        self.build_year_list = []
        self.type_list = []
        self.market_list = []


    def fetch_html(self, url):
        '''
        # headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }
        '''
        
        res = requests.get(url=url, headers=self.headers)
        print('HTTP GET request to URL: %s | Status code: %s' % (res.url, res.status_code))

        if res.status_code == 200:
            parsed_doc = self.parse(url)
            self.fetch_data(parsed_doc)
            '''
            self.address
            self.price
            self.sq_meter_price
            self.area
            self.n_rooms
            self.floor
            self.build_year
            self.type_of
            self.market
            '''
        else:
            return None


    def parse(self, url):
        # Opening up connection ang grabbing the page
        client = ureq(url)
        page_html = client.read()
        client.close()
        
        # HTML parser
        page_soup = soup(page_html, "html5lib")
        return page_soup


    def fetch_data(self, page):
        oglDetailsMoney
        self.price_listpage.find("span", {"class": "oglDetailsMoney"})
        '''
        self.address
        self.price
        self.sq_meter_price
        self.area
        self.n_rooms
        self.floor
        self.build_year
        self.type_of
        self.market
        '''
        pass


    def save_to_csv(self):
        pass


    def run(self):
        # urls list
        urls = ''
        
        # fetch urls from file
        source = 'trojmiasto-links/' + str(self.type_of_market) + self.date + '.txt' 
        with open(source, 'r', encoding='utf-8') as f:
            for line in f.read():
                urls += line

        # convert links to list
        urls = urls.split('\n')

        # Looping through urls
        for url in urls[0:2]:
            self.fetch(url)
            


if __name__ == '__main__'
    data = DataScraper(type_of_market = 1, date = '2020-11-12')
    dara.run()
