import mysql.connector
from mysql.connector import errorcode


# returns None if connecting throws an error
def make_DB_Connection():
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
    else:
        # print("SQL DB connection should be working")
        pass

    mycursor = cnx.cursor()

    mycursor.execute("CREATE TABLE if not exists Locations (locationID int PRIMARY KEY AUTO_INCREMENT, city varchar(255), country varchar(255), lat DOUBLE, lng DOUBLE,  mapboxref varchar(255), count int );")
    mycursor.execute("CREATE TABLE if not exists Users (discordID int PRIMARY KEY AUTO_INCREMENT, discordUserId varchar(255), locationID int, FOREIGN KEY (locationID) REFERENCES Locations(locationID) );")
    return cnx


def insert_Location(city: str, country: str, mapboxref: str):
    database = make_DB_Connection()

    try:
        # TODO: use city, country to determine lat, lng
        # TODO: figure out how to get mapbox reference
        # TODO: make the count increment if the location already exists
        sql = f"INSERT INTO Locations (city, country, lat, lng, mapboxref, count) VALUES ('{city}', '{country}', 0.0, 0.0, '{mapboxref}', 1);"

        cursor = database.cursor()
        # cursor.execute(sql, (city, country, 0.0, 0.0, mapboxref, 1))
        cursor.execute(sql)
        database.commit()
        return True
    except Exception as e:
        # TODO: can probably use error codes instead
        print(e)
        return False

    # TODO: insert into the User's database


def delete_Location(city: str, country: str):
    # first, find the location to delete
    cnx = make_DB_Connection()

    pass


# returns -1 if an error
# returns 0 if the location doesn't exist yet
def get_Count_At_Location(locationID):
    database = make_DB_Connection()

    cursor = database.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM Users WHERE locationID = {locationID};")
    print(cursor.fetchall())


def insert_User_Info(discordUserID, locationID):
    database = make_DB_Connection()
    cursor = database.cursor()

    # try:
    print(discordUserID)
    print(locationID)
    sql = "INSERT INTO Users (discordUserId, locationID) VALUES (%s, %s);"
    print(sql)

    val = (f"{discordUserID}", f"{locationID}")
    cursor.execute(sql, val)

    # cursor.execute(f"INSERT INTO Users (discordUserId, locationID) VALUES (${discordUserID}, ${locationID});")
    database.commit()
    #FIXME: have a single database.commit(), when all the queries succeed
    # otherwise database might crash or become out of sync

        # return True
    # except Exception as e:
    #     # TODO: can probably use error codes instead
    #     print(e)
    #     return False
