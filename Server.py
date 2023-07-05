import mapbox
import databaseFunctions as db
from dotenv import load_dotenv


def on_join(guild):
    _, datasetID = mapbox.create_dataset(guild)
    db.insert_server(guild.id, datasetID)


def on_leave(guildID: str):
    datasetID = db.get_datasetID(guildID)
    print(datasetID)
    mapbox.delete_dataset(datasetID)
    db.delete_server(guildID)
    #TODO: delete all users by guild
    #TODO: delete all locations by guild


load_dotenv("secrets.env")
on_leave("1125361618360999977")
