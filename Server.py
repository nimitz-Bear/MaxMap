import mapbox
import databaseFunctions as db
from dotenv import load_dotenv


def on_join(guild):
    # create a dataset for the guild, and an entry in the Servers table for configurations
    _, datasetID = mapbox.create_dataset(guild)
    db.insert_server(guild.id, datasetID)


def on_leave(guildID: str):
    # find the dataset for the guild
    datasetID = db.get_datasetID(guildID)
    print(datasetID)

    # delete the servers configurations first
    db.delete_server(guildID)

    # delete all users and locations associated with the server
    delete_all_server_users(guildID)
    delete_all_server_locations(guildID)

    # delete the dataset last, since this seems to inexplicably fail a lot
    mapbox.delete_dataset(datasetID)


def delete_all_server_users(guildID: str):
    # delete all from the users table where the guildID = input
    db.delete(f"DELETE FROM Users WHERE guildID='{guildID}';")


def delete_all_server_locations(guildID: str):
    db.delete(f"DELETE FROM Locations WHERE guildID='{guildID}';")
