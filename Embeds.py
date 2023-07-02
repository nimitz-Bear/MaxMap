from discord import Colour, Embed


def help() -> Embed:
    info = Embed(
        title="Maxmap Information",
        description="Maxmap is a bot that allows you to add your city to a community map"
    )
    info.add_field(name='Add city to map',
                   value=f'Use`/addcity` with your city and country to add your city to the map, e.g. `/addcity Nottingham UK`')
    info.add_field(name='Delete city from map', value=f'Use `/removecity` with your city and country '
                                                      f'to remove your city from the map, e.g. `/removecity Paris France`')
    info.add_field(name='See the map', value=f"Use `/map` to see the map of your community!")
    info.add_field(name='Privacy Notice', value=f"Please note that the map is public."
                                               f"By adding your city to the map, you acknowledge this. You can delete "
                                               f"your city at any time. If there are any issues, please contact "
                                               f"nimitz_ on discord.")
    return info


def success(message: str) -> Embed:
    return Embed(
        title="Maxmap",
        color=Colour.og_blurple(),
        description=message
    )


def error(message: str) -> Embed:
    return Embed(
        title="Error",
        color=Colour.brand_red(),
        description=message
    )
