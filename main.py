import bot
import databaseFunctions as dbf
from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv("secrets.env")
    # start up the database
    dbf.make_db_connection()

    # start up the bot
    bot.run_discord_bot()


