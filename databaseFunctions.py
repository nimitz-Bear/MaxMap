import os

import mysql.connector
from mysql.connector import errorcode


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
        "CREATE TABLE if not exists Locations (featureID varchar(255), city varchar(255), country varchar(255), lat double, lng double,  PRIMARY KEY(featureID));")
    # need a seperate discordID since a single discordUserId may have put multiple locations in
    mycursor.execute(
        "CREATE TABLE if not exists Users (discordID int AUTO_INCREMENT PRIMARY KEY, discordUserID varchar(255), " +
        "discordUsername varchar(255), featureID varchar(255), FOREIGN KEY (featureID) REFERENCES Locations(featureID));")
    mycursor.execute("CREATE TABLE if not exists Servers (guildID varchar(255) PRIMARY KEY, datasetID varchar(255));")
    return cnx


# inserts a new location into the DB
def insert_location(featureID: str, city: str, country: str, lat: float, lng: float):
    database = make_db_connection()

    try:
        sql = f"INSERT INTO Locations (featureID, city, country, lat, lng) VALUES (%s, %s, %s, %s, %s);"

        cursor = database.cursor()
        cursor.execute(sql, (featureID, city, country, lat, lng))
        database.commit()
        print(f"{featureID}, {city}, {country}, {lat}, {lng}")
        return True
    except Exception as e:
        print(e)
        return False


def delete_location(city: str, country: str):
    database = make_db_connection()
    cursor = database.cursor()

    try:
        sql = f"DELETE FROM Locations WHERE city = '{city}' AND country = '{country}';"
        cursor.execute(sql)
        database.commit()
        return True
    except Exception as e:
        print(e)
        return False


# gets featureID based on city, country. Returns true if 1 or more entries found
# returns false if execution fails or 0 results
def get_feature_id(city: str, country: str):
    database = make_db_connection()
    cursor = database.cursor()

    try:
        sql = f"SELECT featureID FROM Locations WHERE city='{city}' AND country='{country}';"
        cursor.execute(sql)
        results = cursor.fetchall()
        print(results)

        if len(results) == 0 or results is None:
            print("No results found")
            return False, []  # TODO: change this to ""?

        return True, str(results[0][0])
    except Exception as e:
        print(e)
        return False, ""


# returns the number of users at a given location, returns 0 if location doesn't yet exist in DB
def get_count_at_feature(city: str, country: str):
    # get the feature ID
    success, result = get_feature_id(city, country)
    database = make_db_connection()
    cursor = database.cursor()

    # return 0 if featureID cannot be found
    if success is False or result == []:
        return 0
    else:
        try:
            sql = f"SELECT COUNT(featureID) As UserCount From Users WHERE featureID = '{result}';"
            cursor.execute(sql)
            results = cursor.fetchall()
            print(results[0][0])
            return results[0][0]
        except Exception as e:
            print(e)


# add a user to the DB
# NOTE: user may choose to have multiple entries
def insert_user(discordUserID, discordUsername, featureID):
    database = make_db_connection()
    cursor = database.cursor()

    try:
        sql = "INSERT INTO Users (discordUserId, discordUsername, featureID) VALUES (%s, %s, %s);"
        val = (f"{discordUserID}", f"{discordUsername}", f"{featureID}")
        cursor.execute(sql, val)
        database.commit()
        return True
    except Exception as e:
        print(e)
        return False


def delete_user(discordUserID, featureID):
    database = make_db_connection()
    cursor = database.cursor()

    try:
        # a discordUserID may have multiple Locations (i.e. featureID's)
        # but a featureID can't have multiple of the same discordUserID (i.e. a user shouldn't
        # be registered in the same place twice)
        sql = f"DELETE FROM Users WHERE discordUserID = '{discordUserID}' AND featureID = '{featureID}';"
        cursor.execute(sql)
        database.commit()
        return True
    except Exception as e:
        print(e)
        return False


def get_users_at_location(featureID: str):
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


def add_server(guildID: str, datasetID: str):
    pass


def delete_server(guildID: str):
    pass


def get_datasetID(guildID: str):
    pass
