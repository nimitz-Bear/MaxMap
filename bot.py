import datetime

import discord
from discord import option
import os

import Embeds
import Location
import Server
import Utils

import databaseFunctions as db
import keep_alive


def run_discord_bot():
    bot = discord.Bot()

    @bot.command(name="map", brief="shows map", description="Shows the map of the community")
    async def showMap(ctx):
        # get the dataset ID
        datasetID = db.get_datasetID(ctx.guild.id)

        if datasetID == "":
            await ctx.respond(f"Error. Could not find datasetID for this server.")
            return

        await ctx.respond(f"You can view the map at: https://maxmap-252b2.web.app?{datasetID}")

    @bot.command(name="add-city", description="Add the city closest to where you live to the map.")
    @option("city", description="Enter the city closest to you", required=True)
    @option("country", description="Enter the country you live in", required=True)
    async def addcity(ctx, city: str, country: str):
        if city is None or country is None:
            await ctx.respond(ephemeral=True, embed=Embeds.error(
                text=f"Missing arguments. Correct usage is `/add-city city country`, for example /add-city Nottingham United Kingdom"))
            return

        if not Utils.is_country(country):
            await ctx.respond(ephemeral=True, embed=Embeds.error(
                text=f"{country} is not a valid input for the country field. Please enter a valid ISO 3166 country name"))
            return

        # defer response to give time for api calls and DB queries
        await ctx.defer()

        # check if the user has already entered a feature here
        _, featureID = db.get_feature_id(city, country, ctx.guild.id)
        if db.is_duplicate(ctx, featureID):
            await ctx.respond(embed=Embeds.error(
                f"It looks like you already have an entry for {city}, {country}"))
            return

        # auto-suggest response if Mapbox doesn't recognize city, country
        not_recognized, rec_city, rec_country = Utils.auto_suggest_city_and_country(city, country)
        if rec_city == "" and rec_country == "":
            await ctx.respond(embed=Embeds.error(
                f"Invalid input {city}, {country}. Mapbox wasn't able to find a matching "
                              f"city/town/village/municipality"))
            return
        elif not_recognized:
            await ctx.respond(embed=Embeds.error(
                f"Mapbox did not recognize input. Perhaps you mean {rec_city}, {rec_country}"))
            return

        # if location doesn't exist for a server, make a new location and add it to dataset, DB
        if db.server_location_count(city, country, ctx.guild.id) == 0:
            await Location.new(city, country, ctx)
        # else increment the count and add username to list
        else:
            await Location.increment(city, country, ctx)

    @bot.command(name="remove-city", description="Delete where you live from the map")
    @option("city", description="Enter city entry to remove", required=True)
    @option("country", description="Entry country entry to remove", required=True)
    async def removecity(ctx, city: str = None, country: str = None):
        if city is None or country is None:
            await ctx.respond(ephemeral=True, embed=Embeds.error(
                "Missing arguments. Correct usage is `/remove-city city country`, for example "
                "/remove-city Nottingham United Kingdom"))
            return
        elif not Utils.is_country(country):
            await ctx.respond(ephemeral=True, embed=Embeds.error(
                f"{country} is not a valid input for the country field.  Please enter a valid ISO 3166 country"))
            return

        # ensure that a user can't delete a non-existent city
        _, featureID = db.get_feature_id(city, country, ctx.guild.id)
        if not db.is_duplicate(ctx, featureID):
            await ctx.respond(embed=Embeds.error(
                f"Failed to delete. You don't seem to have an entry for {city}, {country}"))
            return

        #  defer response to give time for api calls and DB queries
        await ctx.defer()

        _, featureID = db.get_feature_id(city, country, ctx.guild.id)
        await Location.decrement(city, country, ctx.author.id, featureID, ctx)

    @bot.command(name="help", description="Shows info about the bot and lists commands")
    async def help(ctx):
        await ctx.respond(embed=Embeds.help())

    @bot.event
    async def on_ready():
        print(f"LOGGING: Bot is running as {bot.user}")

    @bot.event
    async def on_guild_join(guild):
        print(f"LOGGING: creating a new dataset for joining: {guild.name}, {guild.id}")

        # create a new dataset for each server the bot joins and save datasetID to Servers table
        Server.on_join(guild)

    @bot.event
    async def on_guild_remove(guild):
        print(f"LOGGING: Left guild: {guild.id}")
        Server.on_leave(guild.id)

    @bot.event
    async def on_application_command_error(ctx, error):
        print(f"LOGGING: Error occurred at {datetime.datetime.utcnow()} UTC: ", str(error))
        await ctx.respond(f"An unexpected error occured")

    keep_alive.keep_alive()
    bot.run(os.getenv("DISCORD_TOKEN"))
