# Import packages
from urllib.request import urlopen as ureq
from bs4 import BeautifulSoup as soup
import requests
import time
from datetime import date
import pandas as pd
import os


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
        columns = ['address', 'price', 'sq_meter_price', 'area', 'n_rooms', 'floor', 'build_year', 'type']
        self.df = pd.DataFrame(columns=columns)
        self.deleted = 0


    def fetch_html(self, url):
        res = requests.get(url=url, headers=self.headers)
        print('HTTP GET request to URL: %s | Status code: %s' % (res.url, res.status_code))

        if res.status_code == 200:
            return self.parse(url)
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
            row.append(self.ifelse_statement("class", "oglField--cena", "oglDetailsMoney", page))
            row.append(self.ifelse_statement("class", "oglField oglField--cena_za_m2", "oglDetailsMoney", page))
            row.append(self.ifelse_statement("id", "show-powierzchnia", "oglField__value", page))
            row.append(self.ifelse_statement("class", "oglField--l_pokoi", "oglField__value", page))
            row.append(self.ifelse_statement("class", "oglField--pietro", "oglField__value", page))
            row.append(self.ifelse_statement("class", "oglField--rok_budowy", "oglField__value", page))
            row.append(self.ifelse_statement("class", "oglField--rodzaj_nieruchomosci", "oglField__value", page))
            return row
        else:
            print("This offer has been removed.")
            self.deleted += 1


    def ifelse_statement(self, class_id, first_name, second_name, page):
        if page.find("div", {class_id: first_name}) == None:
            row = None
        else:
            row = page.find("div", {class_id: first_name}).find("span", {"class": second_name}).getText()

        return row
        

    def add_row_to_df(self, row):
        to_append = pd.Series(row, index = self.df.columns)
        self.df = self.df.append(to_append, ignore_index=True)


    def save_to_csv(self): 
        path = 'trojmiasto-data/'
        filename = 'data' + '-' + str(self.type_of_market) + '-' + self.date + '.csv'
        os.makedirs(path, exist_ok=True)
        
        self.df.to_csv(path_or_buf = (path + filename), encoding='cp1250', index = False)


    @execution_time
    def run(self):
        # urls list
        urls = ''
        
        # fetch urls from file
        source = 'trojmiasto-links/' + 'links' + str(self.type_of_market) + '-' + self.date + '.txt' 
        with open(source, 'r', encoding='utf-8') as f:
            for line in f.read():
                urls += line

        # convert links to list
        urls = urls.split('\n')

        # Looping through urls
        for url in urls:
            time.sleep(2)
            parsed_doc = self.fetch_html(url)
            row = self.fetch_data(parsed_doc)
            if row != None:
                self.add_row_to_df(row)

        # Saving data frame to the .csv file
        self.save_to_csv()

        # Summary
        print(self.deleted, " offers have been deleted.")
        print(len(self.df.index), " offers have been saved to the file.")



if __name__ == '__main__':
    primary_data_scraper = DataScraper(type_of_market = 1, date = '2020-11-26')
    primary_data_scraper.run()

    secondary_data_scraper = DataScraper(type_of_market = 2, date = '2020-11-26')
    secondary_data_scraper.run()
    
