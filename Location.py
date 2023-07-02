import mapbox
import databaseFunctions as db
import Utils


async def decrement(city: str, country: str, discordUserID: str, featureID: str):
    # delete the user from the DB and decrement mapbox feature
    db.delete_user(discordUserID, featureID)
    count = db.get_count_at_feature(city, country)

    # if there's no one else in a location, delete it from the DB and the mapbox
    if count == 0:
        await delete(featureID, city, country)
    else:
        # get list of users
        _, users = db.get_users_at_location(featureID)
        _, lat, lng = Utils.get_lat_lng_from_city(city, country)

        # update the result in mapbox
        mapbox.upsert_feature(lat, lng, users, count, featureID)


async def increment(city: str, country: str, ctx):
    # TODO: do a check to ensure that the user hasn't already added themselves to this place

    # find featureID to update
    success, featureID = db.get_feature_id(city, country)

    # # check if location doesn't exist
    # if not success:
    #     # should never happen
    #  await ctx.followup.send(f"Error IC_1: failed when incrementing, locationCount > 0, but not in Locations DB")

    # first, update Users DB
    UserSuccess = db.insert_user(str(ctx.author.id), str(ctx.author.name), featureID)

    # get updated user list and number of users at location
    count = db.get_count_at_feature(city, country)
    success, users = db.get_users_at_location(featureID)

    # get lat, lng for the city
    _, lat, lng = Utils.get_lat_lng_from_city(city, country)

    # update mapbox
    mapbox.upsert_feature(lat, lng, users, count, featureID)


async def new(city: str, country: str, ctx):
    success, lat, lng = Utils.get_lat_lng_from_city(city, country)
    if not success:
        await ctx.followup.send(f"Error: no coordinates found for {city}, {country}")
        return

    # FIXME: can de-synchronize DB and mapbox if one of the three below fails, and the other succeeds
    # add the new location feature to mapbox and to the Locations DB
    _, featureID, _ = mapbox.upsert_feature(lat, lng, [ctx.author.name])
    db.insert_location(featureID=featureID, city=city, country=country, lng=lng, lat=lat)

    # finally, add user to Users DB (relies on featureID in locationDB)
    db.insert_user(str(ctx.author.id), str(ctx.author.name), featureID)
    await ctx.followup.send(f"{city}, {country} has been added to the map")


async def delete(featureID: str, city: str, country: str):
    # FIXME: can de-synchronize DB and mapbox if one of the two below fails, and the other succeeds
    mapbox.delete_feature(featureID)
    db.delete_location(city, country)
