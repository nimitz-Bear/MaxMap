import mysql.connector
from mysql.connector import errorcode


# returns None if connecting throws an error
def makeDBConnection():
    try:
        cnx = mysql.connector.connect(user="root", password="root",
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

    mycursor.execute("CREATE TABLE if not exists Locations (featureID varchar(255), city varchar(255), country varchar(255), lat double, lng double);")
    return cnx


# inserts a new location into the DB
def insertLocation(featureID: str, city: str, country: str, lat: float, lng: float):
    database = makeDBConnection()

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


def deleteLocation(city: str, country: str):
    # first, find the location to delete
    database = makeDBConnection()
    cursor = database.cursor()

    try:
        sql = f"DELETE FROM Locations WHERE city = {city} AND country = {country};"
        cursor.execute(sql)
        database.commit()
        return True
    except Exception as e:
        print(e)
        return False


