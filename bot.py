import discord
from discord import option
import os

import Embeds
import Location

import databaseFunctions as db

def run_discord_bot():
    bot = discord.Bot()

    @bot.command(name="map", brief="shows map", description="Shows the map of the community")
    async def showMap(ctx):
        # print(ctx.guild.id)
        await ctx.respond(f"You can view the map at: https://maxmap-252b2.web.app/")

    @bot.command(name="addcity", description="Add the city closest to where you live to the map.")
    @option("city", description="Enter the city closest to you", required=True)
    @option("country", description="Enter the country you live in", required=True)
    async def addcity(ctx, city: str = None, country: str = None):
        if city is None or country is None:
            await ctx.respond(
                f"Missing arguments. Correct usage is `/addcity city country`, for example /addcity Nottingham UK")
            return

        # defer response to give time for api calls and DB queries
        await ctx.defer()

        # TODO: also check if the lat, lng exist already
        # if new location, create a new entry in the location DB and dataset
        if db.get_count_at_feature(city, country) == 0:
            await Location.new(city, country, ctx)

        # else increment the count and add the user's name to the list
        else:
            await Location.increment(city, country, ctx)

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
        _, featureID = db.get_feature_id(city, country)
        await Location.decrement(city, country, ctx.author.id, featureID)

        await ctx.followup.send(f"Deleted {ctx.author}'s entry for {city}, {country}")

    @bot.command(name="help", description="Shows info about the bot and lists commands")
    async def help(ctx):
        await ctx.respond(embed=Embeds.help())

    @bot.event
    async def on_guild_join(guild):
        pass

    bot.run(os.getenv("DISCORD_TOKEN"))
