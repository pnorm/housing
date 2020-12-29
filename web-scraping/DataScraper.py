# Import packages
import urllib.request, urllib.error
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
        columns = ['company', 'address', 'price', 'sq_meter_price', 'area', 'n_rooms', 'floor', 'build_year', 'type', 'date']
        self.df = pd.DataFrame(columns=columns)
        self.deleted = 0
        self.incomplete = 0


    def parse(self, url):
        try:
            conn = urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            # Return code error (e.g. 404, 501, ...)
            print('HTTP GET request to URL: %s | Status code: %s' % (url, e.code))
            return 'Code specific error'
        except urllib.error.URLError as e:
            # Not an HTTP-specific error (e.g. connection refused)
            print('HTTP GET request to URL: %s | URLError: {}' % (url, e.reason))
            return 'Connection refused'
        else:
            print('HTTP GET request to URL: %s | Status code: %s' % (url, conn.getcode()))
            # HTML parser
            try:
                page_html = conn.read()
                page_soup = soup(page_html, "html5lib")
                conn.close()
                return page_soup
            except:
                print('IncompleteRead Exception')
                self.incomplete += 1
                return None



    def fetch_data(self, page):
        if len(page.find_all("div", {"class": "blocked_box"})) == 0:
            row = list()

            if len(page.find_all("div", {"class": "ogloszeniaShowName__element"})) == 2:
                row.append(page.find_all("div", {"class": "ogloszeniaShowName__element"})[0].find("a").getText().strip()) #developer
                row.append(page.find_all("div", {"class": "ogloszeniaShowName__element"})[1].find_all("span")[1].getText().strip()) #adres
            elif len(page.find_all("div", {"class": "ogloszeniaShowName__element"})) == 1:
                row.append(None)
                row.append(page.find_all("div", {"class": "ogloszeniaShowName__element"})[0].find_all("span")[1].getText().strip())
            else:
                row.append(None)
                row.append(page.find("div", {"class": "oglField--address"}).getText())
            
            row.append(self.ifelse_statement("class", "oglField--cena", "oglDetailsMoney", page))
            row.append(self.ifelse_statement("class", "oglField oglField--cena_za_m2", "oglDetailsMoney", page))
            row.append(self.ifelse_statement("id", "show-powierzchnia", "oglField__value", page))
            row.append(self.ifelse_statement("class", "oglField--l_pokoi", "oglField__value", page))
            row.append(self.ifelse_statement("class", "oglField--pietro", "oglField__value", page))
            row.append(self.ifelse_statement("class", "oglField--rok_budowy", "oglField__value", page))
            row.append(self.ifelse_statement("class", "oglField--rodzaj_nieruchomosci", "oglField__value", page))
            row.append(self.date)
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
            if url == '':
                pass
            else:
                time.sleep(0.9)
                parsed_doc = self.parse(url)
                if parsed_doc == 'Code specific error':
                    pass
                elif parsed_doc == 'Connection refused':
                    pass
                elif parsed_doc == None:
                    pass
                else:
                    row = self.fetch_data(parsed_doc)
                    if row != None:
                        self.add_row_to_df(row)

        # Saving data frame to the .csv file
        self.save_to_csv()

        # Summary
        print(self.deleted, " offers have been deleted.")
        print(self.incomplete, " incomplete pages also have been deleted.")
        print(len(self.df.index), " offers have been saved to the file.")



if __name__ == '__main__':
    primary_data_scraper = DataScraper(type_of_market = 1, date = '2020-12-23')
    primary_data_scraper.run()

    secondary_data_scraper = DataScraper(type_of_market = 2, date = '2020-12-23')
    secondary_data_scraper.run()
    
