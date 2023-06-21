import discord
from discord.ext import commands

import responses
from dotenv import load_dotenv
import os


async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)

    except Exception as e:
        print(e)


def run_discord_bot():
    load_dotenv("secrets.env")

    TOKEN = os.getenv("DISCORD_TOKEN")

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents = intents)

    @bot.event
    async def on_ready():
        print(f'{bot.user} is now running!')

    @bot.command(name='ping')
    async def ping2(ctx, arg, arg2):
        await ctx.send(f'pong {arg} {arg2}')

    @bot.command(name='map')
    async def showMap(ctx):
        await ctx.send("Map: www.placeholderURL.com")
        # TODO: ask Max or create a URL

    # sets the map URL for a given server
    @bot.command(name='setMapURL')
    async def setMapURL(ctx, mapURL):
        await ctx.send(f"Set the map URL for this server to: {mapURL}")
        # TODO insert GUILDID, URL into DB
        # FIXME crashes if no argument supplied

    @bot.command(name='addCity')
    async def addCity(ctx, city, country):
        await ctx.send(f"Set location of {ctx.author.name} to {city}, {country}")

    @bot.command(name='deleteCity')
    async def deleteCity(ctx, city, country):
        await ctx.send(f"Deleted {ctx.author.name} from {city}, {country}")

    bot.run(TOKEN)
