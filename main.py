import bot
import databaseFunctions as dbf
from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv("secrets.env")
    # start up the database
    dbf.makeDBConnection()

    # start up the bot
    bot.run_discord_bot()


