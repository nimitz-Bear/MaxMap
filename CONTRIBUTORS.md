# Contributors

## Project Overview
The project is broken down into two components. The bot and the website. 
- The website is where the map is hosted and viewable to the public and is hosted using Firebase.
- The bot is written in python, which handles all the commands.

The bot uses a MySQL Database and the Mapbox [GeoCoding](https://docs.mapbox.com/api/search/geocoding/)
and [Datasets](https://docs.mapbox.com/api/maps/datasets/#delete-a-feature) APIs. 

MySQL and Mapbox should be in sync, so MySQL is considered to be the authoritative version and is used to update the Mapbox API
when an inconsistency occurs.

## Environments
This discord bot runs on Linux Ubuntu. It should run on most other OS, but you'll likely need to modify some of the steps
described later in this file.

## Database Overview

> Note: when updating/deleting from MySQL, must update Mapbox and vice-versa

### Servers Table
Saves configuration info for each server. It saves which dataset is associated with a given server.


### Users Table
A table of Users. This stores location/s user's register themselves with. Each user entry
relies on having an associated location entry in the Locations table, using the `featureID` field as
a foreign key.

Users can have multiple locations, and register the same location in mutliple guilds.

### Locations Table
A table of Locations. Indexed by `featureID` as primary key. This stores the name and coordinates of a location.


## Folder Structure
A breakdown of the project directory and files:

```
├── Web
│   ├── public
│   │   ├── index.html (webpage where map appears)
│   ├── .firebase
|   ├── firebase.json
├── bot.py (discord commands)
├── main.py (file to start bot)
├── mapbox.py (connect to mapbox api)
├── databaseFunctions.py (MySQL DB connection)
├── requirements.txt
├── secrets.env
├── other py files
├── assets
└── .gitignore
```

### Notes and Caveats

In order to see changes in `index.html` appear in the webpage, need to cd into the `web/` directory and run 
`firebase deploy --only hosting` from command line

`Dataset`s are analogous to being a table/collection of entries, and represent a set of locations. Each discord server has a separate dataset.

`Feature`s represent individual entries in a `Dataset`, and represent a single location




## Setup Process for Running the Bot

To run the bot, you'll need to follow the following steps.

1. Ensure you have Python 3.11 or higher installed
2. Create a `secrets.env` file and ensure that it is added to the `.gitignore`. 
This file will store secrets like bot tokens and API keys.
3. Create a [Discord developer account](https://discord.com/developers/applications) and create a bot token and add it as `DISCORD_TOKEN=your_token` to `secrets.env`
4. Create a [mapbox account](https://account.mapbox.com/) and get a private token (with read/write dataset enabled) and call it `MAPBOX_SECRET_TOKEN`
5. Install MySQL and create a Database with the name `maxmap`
   1. If you have an error like `1044 (42000): Access denied for user 'maxmap'@'localhost' to database 'maxmap'`, then you need to open a mysql terminal and run `GRANT ALL PRIVILEGES ON maxmap.*  TO 'your_username'@'localhost';`
6. Run `pip install -r requirements.txt` to install all the Python dependencies
7. Create a [PositionStack](https://positionstack.com/documentation) API Key and add it to `secrets.env` as `POSITIONSTACK_KEY=Your_key`
8. Run `nohup python 3 main.py &`. Now your bot should be running and you should be able to execute commands in a Discord guild.
   1. The `&` detaches it from the terminal
9. If you want to see the map, host `web/index.html` using something like [Firebase](https://firebaseopensource.com/projects/firebaseextended/emberfire/docs/guide/deploying-to-firebase-hosting/)

By the end, you should have a `secrets.env` file that looks like:
```
DISCORD_TOKEN="Your discord bot token"

# Mapbox values
MAPBOX_SECRET_TOKEN="your mapbox secret key"
DATASET_ID="your mapbox dataset id"

# PositionStack keys
POSITIONSTACK_KEY="Your_positionstack_key"
```



### Links to other documentation:
Setting up Datasets and their Features: https://docs.mapbox.com/api/maps/datasets/

Pycord (slash commands): https://guide.pycord.dev/interactions/application-commands/slash-commands

PositionStack (place -> coordinates): https://positionstack.com/documentation

Basic example for hosting a webpage for the map: https://docs.mapbox.com/mapbox-gl-js/example/toggle-layers/

Clustering nearby points: https://docs.mapbox.com/mapbox-gl-js/example/cluster/

For firebase hosting: https://firebase.google.com/docs/hosting/quickstart

