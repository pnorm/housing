import requests
import json
import time
import pandas as pd
import os


class GeocoderOSM:
    '''
    '''
    base_url = 'https://nominatim.openstreetmap.org/search'
    

    def __init__(self, date):
        self.date = date
        self.results = []


    def get_data(self):
        path = os.path.abspath(os.path.join(os.getcwd(), "..\\data-cleansing\\cleaned-data"))
        filename = "\\c-data" + str(self.date) + ".csv"
        df = pd.read_csv(path + filename, encoding="cp1250")
        
        df["lat"] = None
        df["lon"] = None

        return df


    def fetch(self, address):
        # headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'        
        }
        
        # string query parameters
        params = {
            'q': address,
            'format': 'geocodejson'
            }
        res = requests.get(url=self.base_url, params=params, headers=headers)
        print('HTTP GET request to URL: %s | Status code: %s | Response time: %s' % (res.url, res.status_code, res.elapsed.total_seconds()))

        if res.status_code == 200:
            return res
        else:
            pass


    def parse(self, res):
        try:
            coordinates = res['features'][0]['geometry']['coordinates']
            # retrieved data
            return coordinates
        except:
            pass


    def save_to_csv(self, df):
        path = os.path.abspath(os.path.join(os.getcwd(), "..\\final-data"))
        filename = "\\data-" + str(self.date) + ".csv"
        os.makedirs(path, exist_ok=True)
        
        df.to_csv(path_or_buf = (path + filename), encoding='cp1250', index = False)


    def run(self):
        df = self.get_data()

        count_none = 0

        for i in range(len(df)):
            address = df.iat[i, 3]
            res = self.fetch(address)
            
            # Retrieving Lon and lat
            coords = self.parse(res.json())

            if coords == None:
                count_none += 1
                print('None for address: {}'.format(address))
            else:
                lat = coords[1]
                lon = coords[0]
                print("Long: {} and Lat: {} for adddress: {}".format(coords[0], coords[1], address))
                df.iat[i, df.columns.get_loc("lat")] = lat
                df.iat[i, df.columns.get_loc("lon")] = lon
                                     
            time.sleep(1.5)

        print(count_none, ' NoneType objects.')
        
        # Saving to csv file
        self.save_to_csv(df)



if __name__ == '__main__':
    geocoder = GeocoderOSM('2020-12-23')
    geocoder.run()
