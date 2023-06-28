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

    # create the tables if they're not already in place
    mycursor.execute(
        "CREATE TABLE if not exists Locations (featureID varchar(255), city varchar(255), country varchar(255), lat double, lng double);")
    # need a seperate discordID since a single discordUserId may have put multiple locations in
    mycursor.execute("CREATE TABLE if not exists Users (discordID int AUTO_INCREMENT PRIMARY KEY, discordUserID varchar(255), featureID varchar(255));")
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
    database = makeDBConnection()
    cursor = database.cursor()

    try:
        sql = f"DELETE FROM Locations WHERE city = '{city}' AND country = '{country}';"
        cursor.execute(sql)
        database.commit()
        return True
    except Exception as e:
        print(e)
        return False


# gets featureID based on city, country. Returns true if 0 or more requests found
# returns false if execution fails
def getFeatureID(city: str, country: str):
    database = makeDBConnection()
    cursor = database.cursor()

    try:
        sql = f"SELECT featureID FROM Locations WHERE city='{city}' AND country='{country}';"
        cursor.execute(sql)
        results = cursor.fetchall()
        print(results)

        if len(results) == 0 or results is None:
            print("No results found")
            return True, ""

        return True, results[0][0]
    except Exception as e:
        print(e)
        return False, ""

