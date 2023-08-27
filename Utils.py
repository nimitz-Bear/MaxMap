import string

from country_list import countries_for_language
import requests

import os
from dotenv import load_dotenv


# check if each character in a string is ASCII
def remove_non_ascii(unicode_string: str):
    # if the unicode value is < 128, it's ascii
    return ''.join(filter(lambda x: x in string.printable, unicode_string))


def country_name_to_code(a_country: str):
    country_codes = dict(countries_for_language('en'))
    # switch the keys and the values
    inv_map = {v: k for k, v in country_codes.items()}
    print(inv_map)

    # iterate over the country names and find the code
    for x in inv_map:
        if x == a_country:
            return inv_map[x]

    # country name could not be found
    return ""


def is_country(a_str: str):
    # check common country names
    country_names = [x[1] for x in list(countries_for_language('en'))]
    for x in country_names:
        if a_str == x:
            return True

    return False


# returns false as the first argument, if it can't find locations
def get_lat_lng_from_city(city: str, country: str):
    city = replaceSpaces(city)
    country = replaceSpaces(country)

    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{city}%20{country}.json?access_token={os.getenv('MAPBOX_SECRET_TOKEN')}&limit=1"
    print(url)

    response = requests.get(url)
    data = response.json()
    print(data)

    # erorr checking to ensure json has the right fields
    if not 'features' in data:
        print(f"ERROR: json is missing [features] field when geocoding")
        raise ValueError('Mapbox api failed', response.text)

       
    if not "center" in data['features'][0].keys():
        print(f"ERROR: json is missing [center] field when geocoding")
        raise ValueError('Mapbox api failed', response.text)
        
    
    print(data['features'][0]["center"])
    coords = data['features'][0]["center"]

    lat = coords[0]
    lng = coords[1]
    return True, lat, lng
    



# used to convert a user-inputted location, country to mapbox place and ISO 3166 country
# for example, "8, Grange Knowe, Springfield, Linlithgow,  West Lothian", "Scotland" -> Linlithgow, United Kingdom.
def find_matching_city(city: str, country: str):
    country_code = country_name_to_code(country)
    # forward geocoding on url with a city, country input
    # language set to English to avoid results in other languages, for example Köln, Germany
    # limit set to 1, since only the first result is used
    print("s"+country_code)
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{city}.json?country={country_code}&language=en&types=place&types=locality&limit=1&access_token={os.getenv('MAPBOX_SECRET_TOKEN')}"
    print(url)
    response = requests.get(url)

    data = response.json()
    print(data)

    # if features isn't in the json, then there was an API error
    if 'features' not in data:
        return ""

    # if there are no features, the input is invalid
    if not data['features']:
        return ""

    # get the place_name (i.e. municipality, city, country) from the input string
    # for example, Nottingham, Nottinghamshire, England, United Kingdom
    # or Japan, Osaka
    place_name = data['features'][0]['place_name']

    # split the place name by comma
    csv_place_name = place_name.split(",")
    # print(csv_place_name)

    # the first value can either be a place or the country (usually place)
    city = remove_non_ascii(str(csv_place_name[0]))

    return city


# TODO: for auto-suggest, get the country from the context maybe?
def fuzzy_search_city(city: str, country: str):
    """

    :param city: user input city/town/municipality
    :param country: user input city
    :return: is_exact_Match,suggested_city, suggested_country
    """
    suggested_city = find_matching_city(city, country)

    # if both are both empty, then the user input is invalid
    if suggested_city == "":
        return False, ""

    if city == suggested_city:
        # return false for Hong Kong, Hong Kong is an exact match, indicating auto-suggest isn't needed
        return True, city
    else:
        # True, when they don't match
        return False, suggested_city
    
# replaces all the spaces in the input string with %20 to make it URL-compatible
def replaceSpaces(input):
    rep = "%20"
    for i in range(len(input)):
        if(input[i] == ' '):
            input = input.replace(input[i],rep)
    # print(input)
    return input

