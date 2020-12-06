import pandas as pd
import numpy as np
import os


class DataCleansing:
    ''' Cleaning data from dom.trojmiasto.pl
            Concatenating primary and secondary dataset
            Changing price and sq_meter_price
            Sorting columns
            Removing duplicates
            Replacing '\xa0'
        Args:
            date (str): 'YYYY-MM-DD' format
    '''


    def __init__(self, date):
        self.date = date
        self.base_path = os.path.abspath(os.path.join(os.getcwd(), "..\\web-scraping\\trojmiasto-data"))


    def read_files(self):
        primary = pd.read_csv(self.base_path + "\\data-1-" + str(self.date) + ".csv", encoding="cp1250")
        secondary = pd.read_csv(self.base_path + "\\data-2-" + str(self.date) + ".csv", encoding="cp1250")

        primary["market"] = "pierwotny"
        secondary["market"] = "wtórny"

        df = pd.concat([primary, secondary], ignore_index=True)

        return df


    def clean_data(self, df):
        df['price'] = df['price'].str.replace(' zł','').str.replace(' ', '').str.replace(',', '.')
        df['sq_meter_price'] = df['sq_meter_price'].str.replace(' zł','').str.replace(' ', '').str.replace(',', '.')
        df['area'] = df['area'].str.replace(' ', '').str.replace(',', '.')

        # Dropping duplicated rows
        df = df.drop_duplicates()

        # Fitlering rows for type as a boolean expression
        values = ['Dom bliźniak', 'Dom szeregowy', 'Dom', 'Dom wolnostojący', 'Dom rekreacyjny', 'Mieszkanie']
        df = df[df.type.isin(values)]

        df = df[df.address.notnull()]
        df = df[df.price.notnull()]
        df = df[df.sq_meter_price.notnull()]
        df = df[df.area.notnull()]
        df = df[df.n_rooms.notnull()]

        df['address'] = df['address'].astype(str).str.replace(u'\xa0', ' ')
        df['address'] = df['address'].astype(str).str.replace(u'  ', ' ')

        df['floor'] = df['floor'].fillna(0)
        df['floor'] = df['floor'].replace('Parter', 0)
        df['build_year'] = df['build_year'].fillna(0)

        df['build_year'] = df['build_year'].astype(np.int64)
        df['n_rooms'] = df['n_rooms'].astype(np.int64)

        return df

    
    def save_to_csv(self, df): 
        path = 'cleaned-data/'
        filename = 'c-data' + self.date + '.csv'
        os.makedirs(path, exist_ok=True)
        
        df.to_csv(path_or_buf = (path + filename), encoding='cp1250', index = False)



    def run(self):
        df = self.read_files()
        cleaned_df = self.clean_data(df)

        # sort columns
        cleaned_df = cleaned_df[['company', 'type', 'address', 'price', 'sq_meter_price', 'area', 'n_rooms', 'floor', 'build_year', 'market']]

        # write to a csv file
        self.save_to_csv(cleaned_df)
        print("Dataframe saved to the .csv file\n")

        # print info about df
        cleaned_df.info()



if __name__ == '__main__':
    data = DataCleansing('2020-11-26')
    data.run()
        
