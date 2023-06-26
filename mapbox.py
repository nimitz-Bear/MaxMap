# this file handles communicating with mapbox using HTTP requests
import uuid
import datetime
import json

import requests
import os
from dotenv import load_dotenv


# adds a feature (i.e. a location on a map) with a default count of 1
# returns True if it suceeds, else False
def addFeature(lat: float, lng: float, discordUsername):
    if not isinstance(lat, float) or not isinstance(lng, float):
        # TODO: may want to throw an error here, because this is very hard to see and solve
        print(f"Error while performing addFeature: lat or long values are not floats! \n {lat}, {lng}")
        return False, ""

    feature_id = str(uuid.uuid4())
    url = \
        f"https://api.mapbox.com/datasets/v1/nimitz-/{os.getenv('DATASET_ID')}/features/{feature_id}?access_token={os.getenv('MAPBOX_SECRET_TOKEN')}"
    headers = {"Content-Type": "application/json"}
    requestbody = {
        "id": f"{feature_id}",
        "type": "Feature",
        "properties": {
            "count": "1",
            # "username": f"{discordUsername}",
            "DateAdded": f"{str(datetime.datetime.now())}",
            "discordUsers": [
                f"{discordUsername}",
            ]
        },
        "geometry": {
            "coordinates": [lng, lat],
            "type": "Point"
        }
    }

    # print(json.dumps(requestbody))

    response = requests.put(url=url, headers=headers, data=json.dumps(requestbody))

    print(response.text)

    response.close()
    if not response.ok:
        print(f"Error when deleting: [{response.status_code}] {response.text}")
        return False, feature_id, response.text

    return True, feature_id, response.text


# delete a feature (i.e. a location on the map)
# NOTE: this isn't just for one person. This location will cease to exist as part of the dataset
def deleteFeature(featureID: str):
    url = f"https://api.mapbox.com/datasets/v1/nimitz-/{os.getenv('DATASET_ID')}/features/{featureID}?access_token={os.getenv('MAPBOX_SECRET_TOKEN')}"
    header = {"Content-Type": "application/json"}
    response = requests.delete(url, headers=header)

    if response.status_code != 204:
        print(f"Error when deleting: [{response.status_code}] {response.text}")
        return False, response.text

    return True, response.text


# remove a person from a feature (i.e. remove a person's association with a location on the map)
# Note: this is just for a person. The location will persist in the database
def deletePersonFromFeature():
    # decrement the counter property
    # then, remove the user from the list

    pass


# prints list of features in JSON format
def listFeatures():
    # TODO could move getting the DATASET_ID, Token out of the functions
    url = \
        f"https://api.mapbox.com/datasets/v1/nimitz-/{os.getenv('DATASET_ID')}/features?access_token={os.getenv('MAPBOX_SECRET_TOKEN')}"
    r = requests.get(url)
    print(r.json())


# get a feature's featureID
def findFeatureID(lat: float, lng: float):

    pass


# FIXME: remove this
load_dotenv("secrets.env")


_, featureID, _ = addFeature(-20.556203, 139.161513, "nimitz#0")
# print("===== before deletion:")
# listFeatures()
# deleteFeature(featureID)
# print("===== after deleting:")
# listFeatures()



