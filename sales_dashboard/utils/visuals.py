import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import numpy as np

def geocode_dataframe(df):
    """Generate coordinates for all locations in the dataframe"""
    geolocator = Nominatim(user_agent="my_geocoder")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    
    # Create location strings
    df['location_string'] = df['CITY'] + ', ' + df['STATE_NAME'] + ', ' + df['COUNTRY_NAME']
    
    # Initialize result columns
    df['latitude'] = np.nan
    df['longitude'] = np.nan
    
    # Geocode each unique location
    unique_locations = df['location_string'].unique()
    location_coords = {}
    
    for location in unique_locations:
        try:
            result = geocode(location)
            if result:
                location_coords[location] = (result.latitude, result.longitude)
            else:
                location_coords[location] = (None, None)
        except:
            location_coords[location] = (None, None)
        
        print(f"Processed: {location}")
    

    for idx, row in df.iterrows():
        lat, lon = location_coords[row['location_string']]
        df.at[idx, 'latitude'] = lat
        df.at[idx, 'longitude'] = lon
    

    df.drop('location_string', axis=1, inplace=True)
    
    return df