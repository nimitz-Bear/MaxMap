# this file handles communicating with mapbox using HTTP requests
import uuid
import datetime
import json

import requests
import os
from dotenv import load_dotenv
import databaseFunctions as db


# insert/update a feature (i.e. a location on a map)
# featureID and count must be provided to update a feature
# returns True if it succeeds, else False
def upsert_feature(lat: float, lng: float, discordUsernames: list[str], guildID, count: int = 1, featureID: str = None):

    # ensure lat, lng inputs are floats
    if not isinstance(lat, float) or not isinstance(lng, float):
        # TODO: may want to throw an error here, because this is very hard to see and solve
        print(f"Error while performing addFeature: lat or long values are not floats! \n {lat}, {lng}")
        return False, "", ""

    # create a unique id for the feature, unless updating
    feature_id = str(uuid.uuid4()) if featureID is None else featureID

    # mapbox lets you update/add a featureID with the same kind of request
    # make an http request to add/update the mapbox feature with a given featureID
    temp = db.get_datasetID(guildID)

    url = \
        f"https://api.mapbox.com/datasets/v1/nimitz-/{db.get_datasetID(guildID)}/features/{feature_id}?access_token={os.getenv('MAPBOX_SECRET_TOKEN')}"
    headers = {"Content-Type": "application/json"}
    requestbody = {
        "id": f"{feature_id}",
        "type": "Feature",
        "properties": {
            "count": count,
            "DateAdded": f"{str(datetime.datetime.now())}",
            "discordUsers": discordUsernames,

        },
        "geometry": {
            "coordinates": [lng, lat],
            "type": "Point"
        }
    }

    response = requests.put(url=url, headers=headers, data=json.dumps(requestbody))
    response.close()

    if not response.ok:
        print(f"Error when upserting: [{response.status_code}] {response.text}")
        return False, feature_id, response.text

    return True, feature_id, response.text


# delete a feature (i.e. a location on the map)
# NOTE: this isn't just for one person. This location will cease to exist as part of the dataset
def delete_feature(featureID: str, guildID: str):
    url = f"https://api.mapbox.com/datasets/v1/nimitz-/{db.get_datasetID(guildID)}/features/{featureID}?access_token={os.getenv('MAPBOX_SECRET_TOKEN')}"
    header = {"Content-Type": "application/json"}
    response = requests.delete(url, headers=header)

    if response.status_code != 204:
        print(f"Error when deleting: [{response.status_code}] {response.text}")
        return False, response.text

    return True, response.text


# returns list of features as JSON
def list_features(guildID: str):
    url = \
        f"https://api.mapbox.com/datasets/v1/nimitz-/{db.get_datasetID(guildID)}/features?access_token={os.getenv('MAPBOX_SECRET_TOKEN')}"
    r = requests.get(url)
    print(r.json())
    return r.json()


# used to create a new dataset, when a new server is added
# returns status, datasetID
def create_dataset(guild):
    url = f"https://api.mapbox.com/datasets/v1/nimitz-?access_token={os.getenv('MAPBOX_SECRET_TOKEN')}"
    request = {
        "name": guild.name,
        "description": guild.id
    }
    response = requests.post(url=url,  headers={"Content-Type": "application/json"}, data=json.dumps(request))
    if not response.ok:
        print("Error! " + response.text)
        return False, ""

    result = response.json()
    featureID = result["id"]
    print(f"Creating dataset {featureID}")
    return True, result["id"]


# destroys a dataset and all features within it
def delete_dataset(datasetID: str):
    url = f"https://api.mapbox.com/datasets/v1/nimitz-/{datasetID}?access_token={os.getenv('MAPBOX_SECRET_TOKEN')}"
    response = requests.delete(url=url, headers={"Content-Type": "application/json"})
    if not response.status_code == 204:
        print(f"Error {response.status_code} " + response.text)
        return False

    print(response.text)
    return True
