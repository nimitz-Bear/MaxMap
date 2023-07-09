# MaxMap

---
**Maxmap** is a bot that allows discord users to create an interactive map of server member's cities.
You can use [this invite link](https://discord.com/api/oauth2/authorize?client_id=1120211992947478588&permissions=397284730944&scope=bot) 
to add it to your discord server. 

![img.png](assets/img.png)
Example map

This version was created using PyCord, the [Mapbox](https://www.mapbox.com) Datasets API and MySQL. 
This project also uses [PositionStack](https://positionstack.com/documentation) to convert coordinates a location string and vice-versa.


## Commands

---

- `map` returns a URL that will show a map of cities representing your server's members
- `add-city` add your city to the map
  - users can add multiple cities to the map
- `remove-city` remove your city from the map

## Data

---
**Maxmap** stores the minimal amount of user information in a MySQL database. It only stores server info like the guildID 
so that it knows which dataset to show.

- `add-city` stores your userid, the city and country that you input
- `remove-city` removes your userid, city and country from the database

## Credits
Credits to [Joe Sieniwaski](https://github.com/jozefws) for creating much of the initial codebase. 
You can see the original version [here](https://github.com/jozefws/MaxMap).
