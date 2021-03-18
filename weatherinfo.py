#!/usr/bin/env python3

from errbot import BotPlugin, botcmd
from yr.libyr import Yr
from urllib import error


class Weatherinfo(BotPlugin):
    """grab short weather informations around the globe
    """


    @botcmd(split_args_with=None)
    def weather(self, msg, args):
        """(!weather berlin) grab weather information for cities, regions, or alias names thereof
        """
        use_location = args[0]
        aliases = dict()
        self['WEATHER_PLACE_ALIASES'] = aliases

        with self.mutable('WEATHER_PLACE_ALIASES') as aliases:
            if aliases.get(use_location):
                use_location = aliases[args]
            try:
                weather = Yr(location_name=use_location)
                temperature = weather.now()
                return f"Weather for {weather.location_name}: {temperature}"
            except error.HTTPError:
                return f"Got an error trying to access the api. I have no idea how to log yet, so my best guess is that I couldn't look up the place name"


    @botcmd(split_args_with=' ')
    def place_alias(self, msg, args):
        """(!place_alias) returns aliases that've been defined for places
        (!place_alias Brasil/Bahia/Ilhéus ilheus) saves "ilheus" as an alias for the longer place name
        """
        aliases = dict()
        self['WEATHER_PLACE_ALIASES'] = aliases

        if len(args) == 0:
            fullname = None
            alias = None
        elif len(args) == 1:
            fullname = None
            alias = args[0]
        elif len(args) == 2:
            fullname = args[0]
            alias = args[1]
        else:
            pass  # Handle the wrong number of args

        with self.mutable('WEATHER_PLACE_ALIASES') as aliases:
            if fullname is None and alias is None:
                return aliases!wea
            if alias and not fullname:
                return aliases[alias]
            if alias and fullname:
                aliases[alias] = fullname
                return aliases[alias]



    @botcmd(split_args_with=' ')
    def delete_place_alias(self, alias, fullname=None):
        """(!delete_place_alias ilheus) delete any aliases associated with the short name "ilheus"
        (!delete_place_alias ilheus USA/New_York/New_York) - deletes the alias for ilheus associated with USA/New_York/New_York if it exists"
        """
        pass
