# Import packages
from urllib.request import urlopen as ureq
from bs4 import BeautifulSoup as soup
import requests
import time
from datetime import date
import pandas as pd


# Execution time decorator
def execution_time(func):
    def wrapper(*args, **kwargs):
        before = time.time()
        result = func(*args, **kwargs)
        print("The script execute in {} seconds".format(time.time() - before))
        return result

    return wrapper


class DataScraper:
    ''' Web scraper 

    Assumptions (https://www.trojmiasto.pl/robots.txt):
        Crawl-delay: 2
    
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
        columns = ['address', 'price', 'sq_meter_price', 'area', 'n_rooms', 'floor', 'build_year', 'type']
        self.df = pd.DataFrame(columns=columns)


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
            row = self.fetch_data(parsed_doc)
            self.add_row_to_df(row)
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
        if len(page.find_all("div", {"class": "blocked_box"})) == 0:
            row = list()
            row.append(page.find("div", {"class": "oglField--address"}).getText())
            row.append(page.find("div", {"class": "oglField--cena"}).find("span", {"class": "oglDetailsMoney"}).getText())
            row.append(page.find("div", {"class": "oglField oglField--cena_za_m2"}).find("span", {"class": "oglDetailsMoney"}).getText())
            row.append(page.find("div", {"id": "show-powierzchnia"}).find("span", {"class": "oglField__value"}).getText())
            row.append(page.find("div", {"class": "oglField--l_pokoi"}).find("span", {"class": "oglField__value"}).getText())
            row.append(page.find("div", {"class": "oglField--pietro"}).find("span", {"class": "oglField__value"}).getText())
            row.append(page.find("div", {"class": "oglField--rok_budowy"}).find("span", {"class": "oglField__value"}).getText())
            row.append(page.find("div", {"class": "oglField--rodzaj_nieruchomosci"}).find("span", {"class": "oglField__value"}).getText())
            return row
        else:
            print("This offer has been removed.")
            pass


    def add_row_to_df(self, row):
        to_append = pd.Series(row, index = self.df.columns)
        self.df = self.df.append(to_append, ignore_index=True)
        pass


    def save_to_csv(self, df):
        pass


    @execution_time
    def run(self):
        # urls list
        urls = ''
        
        # fetch urls from file
        source = 'trojmiasto-links/' + 'links' + str(self.type_of_market)+ '-' + self.date + '.txt' 
        with open(source, 'r', encoding='utf-8') as f:
            for line in f.read():
                urls += line

        # convert links to list
        urls = urls.split('\n')

        # Looping through urls
        for url in urls[0:5]:
            time.sleep(1)
            self.fetch_html(url)


        


if __name__ == '__main__':
    data = DataScraper(type_of_market = 1, date = '2020-11-12')
    data.run()
    print(data.df)
