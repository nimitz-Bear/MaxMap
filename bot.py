import asyncio

import discord
from discord import option
import os
import mapbox

import databaseFunctions as db
import Utils


def run_discord_bot():
    bot = discord.Bot()

    @bot.command(name="map", brief="shows map", description="Shows the map of the community")
    async def showMap(ctx):
        await ctx.respond(f"You can view the map at: www.placeHolder.com")

    @bot.command(name="addcity", description="Add the city closest to where you live to the map.")
    @option("city", description="Enter the city closest to you", required=True)
    @option("country", description="Enter the country you live in", required=True)
    async def addcity(ctx, city: str = None, country: str = None):
        if city is None or country is None:
            await ctx.respond(
                f"Missing arguments. Correct usage is `/addcity city country`, for example /addcity Nottingham UK ")
            return

        # defer response to give time for api calls and DB queries
        await ctx.defer()
        # TODO: validate city and country are real

        # if new location, create a new entry in the location DB and dataset
        if db.getCountAtFeature(city, country) == 0:
            _, lat, lng = Utils.get_lat_lng_from_city(city, country)

            # FIXME: can de-synchronize DB and mapbox if one of the three below fails, and the other succeeds
            # add the new location feature to mapbox and to the Locations DB
            _, featureID, _ = mapbox.addFeature(lat, lng, [ctx.author.name])
            db.insertLocation(featureID=featureID, city=city, country=country, lng=lng, lat=lat)

            # finally, add user to Users DB
            db.insertUser(str(ctx.author.id), str(ctx.author.name), featureID)
            await ctx.followup.send(f"{city}, {country} has been added to the map")

        # else increment the count and add the user's name to the list
        else:
            await increment_city(city, country, ctx)

            await ctx.followup.send(f"{city}, {country} is already on the map and has been incremented")

    @bot.command(name="removecity", description="Delete where you live from the map")
    @option("city", description="Enter the ", required=True)
    @option("country", description="Entry the country you live in", required=True)
    async def removecity(ctx, city: str = None, country: str = None):
        if city is None or country is None:
            await ctx.respond(
                "Missing arguments. Correct usage is `/removecity city country`, for example /removecity Nottingham UK")
            return

        await ctx.defer()  # wait to send the message, since discord automatically times out after a few ms

        # TODO: check if the city is already in the DB
        # FIXME: can de-synchronize DB and mapbox if one of the two below fails, and the other succeeds
        _, featureID = db.getFeatureID(city, country)
        mapbox.deleteFeature(featureID) # FIXME: deleteFeature seems to fail
        db.deleteLocation(city, country)
        await ctx.followup.send(f"Deleted {ctx.author}'s entry for {city}, {country}")

    bot.run(os.getenv("DISCORD_TOKEN"))


async def increment_city(city: str, country: str, ctx):
    # TODO: do a check to ensure that the user hasn't already added themselves to this place

    # find featureID to update
    success, featureID = db.getFeatureID(city, country)

    # check if location doesn't exist
    if not success:
        # should never happen
        await ctx.followup.send(f"Error: failed when incrementing, locationCount > 0, but not in Locations DB")

    # first, update Users DB
    success = db.insertUser(str(ctx.author.id), str(ctx.author.name), featureID)

    # get updated user list and number of users at location
    count = db.getCountAtFeature(city, country)
    users = db.get_users_at_location(featureID)

    # get lat, lng for the city
    _, lat, lng = Utils.get_lat_lng_from_city(city, country)

    # update mapbox
    mapbox.addFeature(lat, lng, users, count, featureID)


async def decrement_city():
    pass
