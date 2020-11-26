# Import packages
from urllib.request import urlopen as ureq
from bs4 import BeautifulSoup as soup
import requests
import time
from datetime import date
import os


# Execution time decorator
def execution_time(func):
    def wrapper(*args, **kwargs):
        before = time.time()
        result = func(*args, **kwargs)
        print("The script execute in {} seconds".format(time.time() - before))
        return result

    return wrapper


class LinkScraper:
    ''' Web scraper for links from dom.trojmiasto.pl

    Assumptions (https://www.trojmiasto.pl/robots.txt):
        Crawl-delay: 2

    Args:
        type_of_market (int): 1 for primary market or 2 for secondary market
        interval (tuple): pages you want to iterate through (from, to)
    '''
    
    def __init__(self, interval, type_of_market):
        ''' Contructor method '''
        self.base_url = 'https://dom.trojmiasto.pl/'
        self.type_of_market = type_of_market
        self.interval = interval
        self.url = ''
        self.list_of_offers = []


    def set_link(self):
        ''' Setting url parameters '''
        if self.type_of_market == 1:
            self.url = self.base_url + 'nieruchomosci-rynek-pierwotny/?strona='
        elif self.type_of_market == 2:
            self.url = self.base_url + 'nieruchomosci-rynek-wtorny/?strona='
        else:
            raise NameError('Choose 1 for primary or 2 for secondary market.')


    def fetch(self):
        ''' fetching '''
        # Setting Link
        self.set_link()
        
        # headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'        
        }

        # Looping through all the pages
        for i in range(self.interval[0], self.interval[1]+1):
            res = requests.get(url=self.url, headers=headers)
            response_url = res.url + str(i)
            print('HTTP GET request to URL: %s | Status code: %s' % (response_url, res.status_code))

            if res.status_code == 200:
                # passing reponse_url to parse() method as an argument
                self.parse(response_url)
                time.sleep(2)
            else:
                None


    def parse(self, url):
        ''' Parsing the data and adding to the list

        Args:
            url (str): 
        '''
        # Opening up connection ang grabbing the page
        client = ureq(url)
        page_html = client.read()
        client.close()
        
        # HTML parser
        page_soup = soup(page_html, "html5lib")

        # Extracting links and adding to list
        for link in page_soup.findAll("a", {"class": "ogloszeniaList__title"}):
            try:
                self.list_of_offers.append(link['href'])
            except KeyError:
                pass


    def save_to_txt(self):
        ''' Saving list to .txt file with one link to an offer in each line. '''
        today = date.today()
        directory = 'trojmiasto-links/'
        # Make directory if don't exist
        os.makedirs(directory, exist_ok=True) 
        filename = 'links' + str(self.type_of_market) + '-' + str(today) + '.txt'
        with open(directory + filename, 'w') as f:
            for s in self.list_of_offers:
                f.write(str(s) + '\n')

    
    @execution_time
    def run(self):
        '''  '''
        self.fetch()
        self.save_to_txt()
        length = len(self.list_of_offers)
        print(length, " links saved to .txt file.")



if __name__ == '__main__':
    # Check the page count first and update interval parameter.
    primary_links_scrapper = LinkScraper(interval = (0, 2), type_of_market = 1)
    primary_links_scrapper.run()

    secondary_links_scrapper = LinkScraper(interval = (0, 2), type_of_market = 2)
    secondary_links_scrapper.run()


    
