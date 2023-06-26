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

    @bot.command(name="addcity", description="Enter the city closest to where you live.")
    @option("city", description="Enter the city closest to you", required=True)
    @option("country", description="Enter the country you live in", required=True)
    async def addcity(ctx, city: str = None, country: str = None):
        if city is None or country is None:
            await ctx.respond(
                f"Missing arguments. Correct usage is `/addcity city country`, for example /addcity Nottingham UK ")
            return

        await ctx.defer()  # wait to send the message, since discord automatically times out after a few ms

        # TODO: do some kind of check if the city already exists
        _, lat, lng = Utils.get_lat_lng_from_city(city, country)

        # FIXME: can de-synchronize DB and mapbox if one of the two below fails, and the other succeeds
        _, featureID, _ = mapbox.addFeature(lat, lng, ctx.author.name)
        db.insertLocation(featureID=featureID, city=city, country=country, lng=lng, lat=lat)
        await ctx.followup.send(f"Set location of {ctx.author} to {city}, {country}")

    @bot.command(name="removecity", description="Delete your entry from the map")
    @option("city", description="Enter the ", required=True)
    @option("country", description="Entry the country you live in", required=True)
    async def removecity(ctx, city: str = None, country: str = None):
        if city is None or country is None:
            await ctx.respond(
                "Missing arguments. Correct usage is `/removecity city country`, for example /removecity Nottingham UK")
            return

        await ctx.defer()  # wait to send the message, since discord automatically times out after a few ms
        # FIXME: can de-synchronize DB and mapbox if one of the two below fails, and the other succeeds
        print()
        _, featureID = db.getFeatureID(city, country)
        mapbox.deleteFeature(featureID)
        db.deleteLocation(city, country)
        await ctx.followup.send(f"Deleted {ctx.author}'s entry for {city}, {country}")

    # sets the map URL for a given server
    @bot.command(name='seturl')
    @option("mapurl", description="Enter the URL where the map will appear", required=True)
    async def setmapurl(ctx, mapurl):
        await ctx.send(f"Set the map URL for this server to: {mapurl}")
        # TODO insert guildID, URL into DB
        # FIXME crashes if no argument supplied

    bot.run(os.getenv("DISCORD_TOKEN"))
