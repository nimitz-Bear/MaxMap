
## Quickstart: Adding the bot to your server
1. Add this invite list

## Setup Process for Running the Bot

This setup process is intended for future iterations of the discord server in the University of Nottingham School of Computer Science mentor scheme

1. Ensure that you have Python 3.11 or higher installed
2. Create a `secrets.env` file and ensure that it is added to the .gitignore
3. Create a Discord developer account and create a bot token
4. Create a mapbox account and get a private token (with read/write dataset enabled)
5. Install mySQL and create a Database 
6. Install everything from `requirements.txt`
7. Run the bot from the main function in `main.py`
8. Host the website

`Dataset`s are analogous to being a table/collection of entries

`Feature`s represent individual entries in a `Dataset` and can be 

## Notes and Caveats

In order to see changes in `index.html` appear in the webpage, need to cd into the `web/` director and run 
`firebase deploy --only hosting` from command line

## Links used:
Setting up Datasets and their Features: https://docs.mapbox.com/api/maps/datasets/

Pycord (slash commands): https://guide.pycord.dev/interactions/application-commands/slash-commands

PositionStack (place -> coordinates): https://positionstack.com/documentation

Basic example for hosting a webpage for the map: https://docs.mapbox.com/mapbox-gl-js/example/toggle-layers/

Clustering nearby points: https://docs.mapbox.com/mapbox-gl-js/example/cluster/


For firebase hosting: https://firebase.google.com/docs/hosting/quickstart

