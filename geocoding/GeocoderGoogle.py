import pandas as pd
import googlemaps

# Import dataset
df = pd.read_csv("dataset.csv", encoding="cp1250")

# Set Google Maps API key
API_KEY = ''
gmaps_key = googlemaps.Client(key = API_KEY)

# Get Lon and Lat
df["lat"] = None
df["lon"] = None

for i in  range(0, len(df), 1):
    geocode_result = gmaps_key.geocode(df.iat[i, 0])
    try:
        lat = geocode_result[0]["geometry"]["location"]["lat"]
        lon = geocode_result[0]["geometry"]["location"]["lng"]
        df.iat[i, df.columns.get_loc("lat")] = lat
        df.iat[i, df.columns.get_loc("lon")] = lon
    except:
        lat = None
        lon = None
