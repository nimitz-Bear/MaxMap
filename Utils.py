import string

from country_list import countries_for_language
import iso3166
import requests

import databaseFunctions as db
import os
from dotenv import load_dotenv


# check if each character in a string is ASCII
def remove_non_ascii(unicode_string: str):
    # if the unicode value is < 128, it's ascii
    return ''.join(filter(lambda x: x in string.printable, unicode_string))


def is_country(a_str: str):
    # check common country names
    country_names = [x[1] for x in list(countries_for_language('en'))]

    for x in country_names:
        if a_str == x:
            return True

    # check ISO3166 country names (used by mapbox)
    # i.e. Türkyie, United Kingdom of Great Britain and Northern Ireland
    iso_names = [o.name for o in list(iso3166.countries)]
    for x in iso_names:
        if a_str == x:
            return True

    return False


# TODO: change this to use mapbox, too
# returns false as the first argument, if it can't find locations
def get_lat_lng_from_city(city: str, country: str):
    # url = "http://api.positionstack.com/v1/forward?" + "access_key=" + os.getenv("POSITIONSTACK_KEY") + \
    #       "&query=" + city + " " + country + "&limit=1"

    # get the coordinates from mapbox
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{city}%20{country}.json?types=place&limit=1&access_token={os.getenv('MAPBOX_SECRET_TOKEN')}"
    response = requests.get(url)

    data = response.json()
    print(data)
    print(data['features'][0]['center'])

    if not response.ok:
        return False, 0.0, 0.0
    else:
        return True, data['features'][0]['center'][0], data['features'][0]['center'][1]


# used to convert a user-inputted location, country to mapbox place and ISO 3166 country
# for example, "8, Grange Knowe, Springfield, Linlithgow,  West Lothian", "Scotland" -> Linlithgow, United Kingdom.
def sanitize_input_city_country(city: str, country: str):
    # forward geocoding on url with a city, country input
    # language set to English to avoid results in other languages, for example Köln, Germany
    # limit set to 1, since only the first result is used
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{city}%20{country}.json?language=en&types=place&limit=1&access_token={os.getenv('MAPBOX_SECRET_TOKEN')}"
    response = requests.get(url)

    data = response.json()
    print(data)
    # print(data['features'][0]['context'])

    # if there are no features, the input is invalid
    if not data['features']:
        return "", ""

    # get the place_name (i.e. municipality, city, country) from the input string
    # for example, Nottingham, Nottinghamshire, England, United Kingdom
    # or Japan, Osaka
    place_name = data['features'][0]['place_name']

    # split the place name by comma
    csv_place_name = place_name.split(",")
    print(csv_place_name)

    # the first value can either be a place or the country (usually place)
    city = remove_non_ascii(str(csv_place_name[0]))

    # the last value can be the place or country (usually country)
    # remove non-ascii characters (i.e. Japanese) and remove leading/trailing whitespace
    country = remove_non_ascii(csv_place_name[len(csv_place_name) - 1]).strip()

    # edge cases for county names like Türkyie
    original_country = (csv_place_name[len(csv_place_name) - 1]).strip()

    print(country)
    # swap if output is Japan, Osaka (instead of Osaka, Japan)
    if not is_country(country) and not is_country(original_country):
        temp = city
        city = country
        country = temp

    return city, country


def auto_suggest_city_and_country(city: str, country: str):
    mapboxCity, mapboxCountry = sanitize_input_city_country(city, country)
    print(country)
    print(city)

    print(mapboxCity, ",", mapboxCountry)

    # if mapboxCity, mapboxCoutnry are both empty, then the user input is invalid
    if mapboxCity == "" and mapboxCountry == "":
        return True, "",""

    if city == mapboxCity and country == mapboxCountry:
        # return false for Hong Kong, Hong Kong is an exact match, indicating auto-suggest isn't needed
        return False, city, country
    elif city == mapboxCity and is_country(country):
        # return False, if city is valid and country is valid (according to countries api)
        return False, city, country
    else:
        # True, when they don't match
        return True, mapboxCity, mapboxCountry


# return locationID based on city, country
# returns none, if city, country is not present in DB yet
# NOTE: only returns the first
def get_locationID(city: str, country: str):
    database = db.make_db_connection()
    cursor = database.cursor()

    cursor.execute(f"SELECT locationID FROM Locations WHERE Country='{country}' AND City='{city}';")
    # print(f"test: {cursor.fetchall()}")
    output = cursor.fetchall()

    if len(output) == 0 or output is None:
        return None

    # only return the first value you find, however, location shouldn't have duplicates
    print(f"test: {output[0]}")
    return output[0][0]


load_dotenv("secrets.env")
# # print(auto_suggest_city_and_country("Northampton", "England"))
auto_suggest_city_and_country("4 Privet Drive, Surrey", "United Kingdom")

# print([o.name for o in list(iso3166.countries)])
# print(is_country("South Korea"))

# print(sanitize_input_city_country("Istanbul", "Turkey"))
# # print(is_country("United Kingdom"))
# # print(sanitize_input_city_country("8, Grange Knowe, Springfield, Linlithgow,  West Lothian", "Scotland"))
# # # print(sanitize_input_city_country("Tokyo", "Japan"))
# #
# #
# # # countries_for_language returns a list of tuples now, might be changed to an OrderedDict
# countries = [x[1] for x in list(countries_for_language('en'))]
# print(countries)
#
# # print(get_lat_lng_from_city("Osaka", "Japan"))
# print(sanitize_input_city_country("Molino IV, Bacoor", "Cavite"))
