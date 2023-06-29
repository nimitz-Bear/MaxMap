# this file handles communicating with mapbox using HTTP requests
import uuid
import datetime
import json

import requests
import os
from dotenv import load_dotenv


# adds a feature (i.e. a location on a map)
# returns True if it succeeds, else False
def addFeature(lat: float, lng: float, discordUsername: list[str], count: int = 1, featureID: str = None):
    print("adding/updating")
    print(count)

    # ensure lat, lng inputs are floats
    if not isinstance(lat, float) or not isinstance(lng, float):
        # TODO: may want to throw an error here, because this is very hard to see and solve
        print(f"Error while performing addFeature: lat or long values are not floats! \n {lat}, {lng}")
        return False, "", ""

    # create a unique id for the feature, unless updating
    feature_id = str(uuid.uuid4()) if featureID is None else featureID

    # mapbox lets you update/add a featureID with the same kind of request
    # make an http request to add/update the mapbox feature with a given featureID
    url = \
        f"https://api.mapbox.com/datasets/v1/nimitz-/{os.getenv('DATASET_ID')}/features/{feature_id}?access_token={os.getenv('MAPBOX_SECRET_TOKEN')}"
    headers = {"Content-Type": "application/json"}
    requestbody = {
        "id": f"{feature_id}",
        "type": "Feature",
        "properties": {
            "count": count,
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


# returns list of features as JSON
def listFeatures():
    url = \
        f"https://api.mapbox.com/datasets/v1/nimitz-/{os.getenv('DATASET_ID')}/features?access_token={os.getenv('MAPBOX_SECRET_TOKEN')}"
    r = requests.get(url)
    print(r.json())
    return r.json()

# FIXME: remove this
# load_dotenv("secrets.env")

# _, featureID, _ = addFeature(-20.556203, 139.161513, "nimitz#0")
# print("===== before deletion:")
# listFeatures()
# deleteFeature(featureID)
# print("===== after deleting:")
# listFeatures()



