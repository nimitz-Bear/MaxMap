import discord
from discord import option
from dotenv import load_dotenv
import os

import databaseFunctions as db


def run_discord_bot():
    load_dotenv("secrets.env")
    bot = discord.Bot()

    @bot.command(description="Send bot's latency.")
    async def ping(ctx):
        await ctx.respond(f"Pong! Latency is {bot.latency}")

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

        db.insert_Location(city, country, "test")  # TODO: figure out how to get a mapboxRef
        await ctx.respond(f"Set location of {ctx.author} to {city}, {country}")

    @bot.command(name="removecity", description="Delete your entry from the map")
    @option("city", description="Enter the ", required=True)
    @option("country", description="Entry the country you live in", required=True)
    async def removecity(ctx, city: str = None, country: str = None):
        if city is None or country is None:
            await ctx.respond(
                "Missing arguments. Correct usage is `/removecity city country`, for example /removecity Nottingham UK")
            return

        await ctx.respond(f"Delete {ctx.author}'s entry for {city}, {country}")

    # sets the map URL for a given server
    @bot.command(name='seturl')
    @option("mapurl",
            description="Enter the URL where the map will appear",
            required=True,
            default=''
            )
    async def setmapurl(ctx, mapurl):
        await ctx.send(f"Set the map URL for this server to: {mapurl}")
        # TODO insert GUILDID, URL into DB
        # FIXME crashes if no argument supplied

    bot.run(os.getenv("DISCORD_TOKEN"))
    print(f"{bot.user} is running")
