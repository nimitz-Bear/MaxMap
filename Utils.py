import databaseFunctions as db


# returns the locationID based on city, country
# returns none, if city, country is not present in DB yet
# NOTE: only returns the first
def get_locationID(city: str, country: str):
    database = db.make_DB_Connection()
    cursor = database.cursor()

    cursor.execute(f"SELECT locationID FROM Locations WHERE Country='{country}' AND City='{city}';")
    print(cursor.fetchall())
    output = cursor.fetchall()

    if len(output) == 0 or output == None:
        return None

    # only return the first value you find, however, location shouldn't have duplicates
    return cursor.fetchall()[0]
