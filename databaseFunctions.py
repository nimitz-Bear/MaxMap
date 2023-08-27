import os

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import errorcode


# TODO: combine the select queries here into one select function
# returns None if connecting throws an error
def make_db_connection():

    try:
        cnx = mysql.connector.connect(user=os.getenv('DB_USERNAME'), password=os.getenv('DB_PASSWORD'),
                                      host="localhost",
                                      database="maxmap",
                                      use_pure=False)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Access to DB denied, likely an issue with username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Error: Database doesn't exist")
        else:
            print(err)
        return None

    mycursor = cnx.cursor()

    # create the tables if they're not already in place
    mycursor.execute(
        "CREATE TABLE if not exists Locations (featureID varchar(255), city varchar(255), country varchar(255), lat double, lng double, guildID varchar(255), PRIMARY KEY(featureID));")
    # need a seperate discordID since a single discordUserId may have put multiple locations in
    mycursor.execute(
        "CREATE TABLE if not exists Users (discordID int AUTO_INCREMENT PRIMARY KEY, discordUserID varchar(255), " +
        "discordUsername varchar(255), featureID varchar(255), guildID varchar(255), FOREIGN KEY (featureID) REFERENCES Locations(featureID));")
    mycursor.execute("CREATE TABLE if not exists Servers (guildID varchar(255) PRIMARY KEY, datasetID varchar(255));")
    return cnx


# for inserting into the table
# sql should be a string,
# such as "INSERT INTO Locations (featureID, city, country, lat, lng) VALUES (%s, %s, %s, %s, %s);"
# values should be a tuple, such as (hjfdgwy4713ul, Rome, Italy, 41.9028, 12.4964)
def insert(sqlInsertQuery: str, values: tuple):
    database = make_db_connection()
    cursor = database.cursor()

    try:
        cursor.execute(sqlInsertQuery, values)
        database.commit()
        return True
    except Exception as e:
        print(e)
        return False


# the argument is a string representing a DELETE FROM mysql command, such as
# f"DELETE FROM Locations WHERE city = '{city}' AND country = '{country}';"
def delete(sqlDeleteQuery: str):
    database = make_db_connection()
    cursor = database.cursor()

    # TODO: get rid of try-catch?
    try:
        cursor.execute(sqlDeleteQuery)
        database.commit()
        return True
    except Exception as e:
        print(e)
        return False


# inserts a new location into the DB
def insert_location(featureID: str, city: str, country: str, lat: float, lng: float, guildID: str):
    return insert(
        f"INSERT INTO Locations (featureID, city, country, lat, lng, guildID) VALUES (%s, %s, %s, %s, %s, %s);",
        (featureID, city, country, lat, lng, guildID))


def delete_location(city: str, country: str, guildID: str):
    sql = f"DELETE FROM Locations WHERE city = '{city}' AND country = '{country}' AND guildID = '{guildID}';"
    return delete(sqlDeleteQuery=sql)


# gets featureID based on city, country. Returns true if 1 or more entries found
# returns false if execution fails or 0 results
def get_feature_id(city: str, country: str, guildID: str):
    database = make_db_connection()
    cursor = database.cursor()

    try:
        sql = f"SELECT featureID FROM Locations WHERE city='{city}' AND country='{country}' AND guildID='{guildID}';"
        cursor.execute(sql)
        results = cursor.fetchall()
        # print(results)

        if len(results) == 0 or results is None:
            print("No results found")
            return False, []  # TODO: change this to ""?

        return True, str(results[0][0])
    except Exception as e:
        print(e)
        return False, ""


# returns the number of users at a given location, for one server
# returns 0, if the location is empty or this server
def server_location_count(city: str, country: str, guildID: str):
    # get the feature ID
    success, result = get_feature_id(city, country, guildID)
    database = make_db_connection()
    cursor = database.cursor()

    # return 0 if featureID cannot be found
    if success is False or result == []:
        return 0
    else:
        try:
            # get the number of users at the same location, in the same server
            sql = f"SELECT COUNT(featureID) As UserCount From Users WHERE featureID = '{result}' AND guildID='{guildID}';"
            cursor.execute(sql)
            results = cursor.fetchall()
            print(results[0][0])
            return results[0][0]
        except Exception as e:
            print(e)


# add a user to the DB
# NOTE: user may choose to have multiple entries
def insert_user(discordUserID: str, discordUsername: str, featureID: str, guildID: str):
    return insert(
        sqlInsertQuery=f"INSERT INTO Users (discordUserId, discordUsername, featureID, guildID) VALUES (%s, %s, %s, %s);",
        values=(f"{discordUserID}", f"{discordUsername}", f"{featureID}", f"{guildID}"))


def delete_user(discordUserID: str, featureID: str, guildID: str):
    return delete(
        f"DELETE FROM Users WHERE discordUserID = '{discordUserID}' AND featureID = '{featureID}' AND guildID ='{guildID}';")


def get_user_list_at_feature(featureID: str):
    database = make_db_connection()
    cursor = database.cursor()

    try:
        sql = f"SELECT discordUsername FROM Users WHERE featureID='{featureID}';"
        cursor.execute(sql)
        results = cursor.fetchall()
        columns = [x[0] for x in results]

        return True, columns
    except Exception as e:
        print(e)
        return False, []


# store a server's associated dataset in the table
def insert_server(guildID: str, datasetID: str):
    return insert(f"INSERT INTO Servers (guildID, datasetID) VALUES (%s, %s);", (guildID, datasetID))


# remove a server's configuration from the table
def delete_server(guildID: str):
    return delete(f"DELETE FROM Servers WHERE guildID = {guildID};")


# get a server's datasetID
def get_datasetID(guildID: str):
    database = make_db_connection()
    cursor = database.cursor()

    try:
        sql = f"SELECT datasetID FROM Servers WHERE guildID = '{guildID}';"
        cursor.execute(sql)
        result = cursor.fetchall()

        # store all results into an array
        columns = [x[0] for x in result]
        print(columns)

        # only return the first result (since you want a string, and there should only be 1 datasetID per guildID)
        if result == [] or result is None:
            return ""
        else:
            return str(columns[0])
    except Exception as e:
        print(e)
        return ""


# returns True if a user is already registered with a feature at a certain location
def is_duplicate(ctx, featureID: str):
    guildID = ctx.guild.id
    userID = ctx.author.id

    database = make_db_connection()
    cursor = database.cursor()

    try:
        cursor.execute("SELECT * FROM Users WHERE guildID=%s AND discordUserID=%s AND featureID=%s LIMIT 1;",
                       (guildID, userID, featureID))
        results = cursor.fetchall()
        if len(results) > 0:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

# load_dotenv("secrets.env")
# print(user_entry_exists("1120260208866885692", "223747505597317120", "f095f5b6-9b59-42a1-ba28-1a1dc4c3bb62"))
