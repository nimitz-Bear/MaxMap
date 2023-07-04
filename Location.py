import mapbox
import databaseFunctions as db
import Utils


async def decrement(city: str, country: str, discordUserID: str, featureID: str, ctx):
    # delete the user from the DB and decrement mapbox feature
    db.delete_user(discordUserID, featureID, ctx.guild.id)
    count = db.server_location_count(city, country, ctx.guild.id)


    # if there's no one else in a location, delete it from the DB and the dataset
    if count == 0:
        await delete(featureID, city, country, guildID=ctx.guild.id)
        await ctx.followup.send(f"Location is now empty. Deleted {city}, {country}")
    else:
        # get list of users
        _, users = db.get_user_list_at_feature(featureID)
        _, lat, lng = Utils.get_lat_lng_from_city(city, country)

        # update the result in mapbox
        mapbox.upsert_feature(lat, lng, users, ctx.guild.id, count, featureID)
        await ctx.followup.send(f"Removed {ctx.author}'s entry from the map for {city}, {country}")


async def increment(city: str, country: str, ctx):
    # TODO: do a check to ensure that the user hasn't already added themselves to this place

    # find featureID to update
    success, featureID = db.get_feature_id(city, country, ctx.guild.id)

    # first, update Users DB (so that the user count will be correct)
    db.insert_user(str(ctx.author.id), str(ctx.author.name), featureID, ctx.guild.id)

    # get updated user list and number of users at location
    count = db.server_location_count(city, country, ctx.guild.id)
    success, users = db.get_user_list_at_feature(featureID)

    # get lat, lng for the city
    _, lat, lng = Utils.get_lat_lng_from_city(city, country)

    # update mapbox
    mapbox.upsert_feature(lat, lng, users, ctx.guild.id, count, featureID)

    # finally respond to the user
    await ctx.followup.send(f"{city}, {country} is already on the map and has been incremented")


async def new(city: str, country: str, ctx):
    success, lat, lng = Utils.get_lat_lng_from_city(city, country)
    if not success:
        await ctx.followup.send(f"Error: no coordinates found for {city}, {country}")
        return

    # add the new location feature to mapbox and to the Locations DB
    # FIXME: can de-synchronize DB and mapbox if one of the three below fails, and the other succeeds
    _, featureID, _ = mapbox.upsert_feature(lat, lng, [ctx.author.name], guildID=ctx.guild.id)
    db.insert_location(featureID=featureID, city=city, country=country, lat=lat, lng=lng, guildID=ctx.guild.id)
    # db.insert(f"INSERT INTO Locations (featureID, city, country, lat, lng) VALUES (%s, %s, %s, %s, %s);",
    #            (featureID, city, country, lng, lat))

    # finally, add user to Users DB (relies on featureID in locationDB)
    db.insert_user(str(ctx.author.id), str(ctx.author.name), featureID, ctx.guild.id)
    await ctx.followup.send(f"{city}, {country} has been added to the map")


async def delete(featureID: str, city: str, country: str, guildID: str):
    # FIXME: can de-synchronize DB and mapbox if one of the two below fails, and the other succeeds
    mapbox.delete_feature(featureID, guildID=guildID)
    db.delete_location(city, country, guildID)
