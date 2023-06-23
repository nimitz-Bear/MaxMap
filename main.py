import bot
import databaseFunctions as dbf
if __name__ == '__main__':
    # # start up the database
    dbf.make_DB_Connection()

    # start up the bot
    bot.run_discord_bot()


