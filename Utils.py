import json
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


def country_code_to_name(a_country_code: str):
    # check if a_str is a country code
    country_codes = dict(countries_for_language('en'))
    for x in country_codes:
        if a_country_code.upper() == x.upper():
            return country_codes[x]

    return ""  # if a country code could not be found


def is_country(a_str: str):
    # check common country names
    country_names = [x[1] for x in list(countries_for_language('en'))]
    for x in country_names:
        if a_str == x:
            return True

    # check ISO3166 country names (used by mapbox)
    # i.e. Türkyie, United Kingdom of Great Britain and Northern Ireland
    iso_names = [o.name for o in list(iso3166.countries)]
    # print(iso_names)
    for x in iso_names:
        if a_str == x:
            return True

    return False


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


# used to convert a user-inputted location, country to mapbox place and ISO 3166 country
# for example, "8, Grange Knowe, Springfield, Linlithgow,  West Lothian", "Scotland" -> Linlithgow, United Kingdom.
def find_city_and_country(city: str, country: str):
    # forward geocoding on url with a city, country input
    # language set to English to avoid results in other languages, for example Köln, Germany
    # limit set to 1, since only the first result is used
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{city}%20{country}.json?language=en&types=place&limit=1&access_token={os.getenv('MAPBOX_SECRET_TOKEN')}"
    response = requests.get(url)

    data = response.json()
    print(data)

    # if there are no features, the input is invalid
    if not data['features']:
        return "", ""

    # use the context to get the country code
    context = data['features'][0]['context']

    # last element in context is the country
    short_code = context[len(context) - 1]['short_code']
    country = country_code_to_name(short_code)

    # get the place_name (i.e. municipality, city, country) from the input string
    # for example, Nottingham, Nottinghamshire, England, United Kingdom
    # or Japan, Osaka
    place_name = data['features'][0]['place_name']

    # split the place name by comma
    csv_place_name = place_name.split(",")
    # print(csv_place_name)

    # the first value can either be a place or the country (usually place)
    city = remove_non_ascii(str(csv_place_name[0]))

    return city, country


# TODO: for auto-suggest, get the country from the context maybe?
def auto_suggest_city_and_country(city: str, country: str):
    """

    :param city: user input city/town/municipality
    :param country: user input city
    :return: is_matching, suggested_city, suggested_country
    """
    mapboxCity, mapboxCountry = find_city_and_country(city, country)

    # if mapboxCity, mapboxCoutnry are both empty, then the user input is invalid
    if mapboxCity == "" and mapboxCountry == "":
        return True, "", ""

    if city == mapboxCity and country == mapboxCountry:
        # return false for Hong Kong, Hong Kong is an exact match, indicating auto-suggest isn't needed
        return False, city, country
    elif city == mapboxCity and is_country(country):
        # return False, if city is valid and country is valid (according to countries api)
        return False, city, country
    else:
        # True, when they don't match
        return True, mapboxCity, mapboxCountry


load_dotenv("secrets.env")
# print(country_code_to_name("dE"))

print(auto_suggest_city_and_country("Putian", "China"))