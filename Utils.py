import requests

import databaseFunctions as db
import os
from dotenv import load_dotenv

# TODO: change this to use mapbox, too
# returns false as the first argument, if it can't find locations
def get_lat_lng_from_city(city: str, country: str):
    url = "http://api.positionstack.com/v1/forward?" + "access_key=" + os.getenv("POSITIONSTACK_KEY") + \
          "&query=" + city + " " + country + "&limit=1"
    response = requests.get(url)
    print(response.text)
    data = response.json()
    print(f"input city: {city}, {country} is at {data['data'][0]['latitude']}, {data['data'][0]['longitude']} ")
    if data['data'] == []:
        return False, 0.0, 0.0
    else:
        return True, data['data'][0]["latitude"], data['data'][0]["longitude"]


# returns the locationID based on city, country
# returns none, if city, country is not present in DB yet
# NOTE: only returns the first
def get_locationID(city: str, country: str):
    database = db.makeDBConnection()
    cursor = database.cursor()

    cursor.execute(f"SELECT locationID FROM Locations WHERE Country='{country}' AND City='{city}';")
    # print(f"test: {cursor.fetchall()}")
    output = cursor.fetchall()

    if len(output) == 0 or output is None:
        return None

    # only return the first value you find, however, location shouldn't have duplicates
    print(f"test: {output[0]}")
    return output[0][0]


# load_dotenv("secrets.env")
# get_lat_lng_from_city("manila", "Philippines")
