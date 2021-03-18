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
        def ctof(celc):
            return (float(celc) * 1.8) + 32.0
        use_location = args[0]
        aliases = dict()
        self['WEATHER_PLACE_ALIASES'] = aliases

        with self.mutable('WEATHER_PLACE_ALIASES') as aliases:
            try:
                if aliases.get(use_location):
                    use_location = aliases[args]
                weather = Yr(location_name=use_location)
                temp = weather.now()['temperature']['@value']
                return f"Weather for {weather.location_name}: {temp} C (or {ctof(temp)} F if you've got your shit together like Liberia or Burma)"
            except error.HTTPError as e:
                self.log.error(f"Got an error trying to access the {str(e)}")
                return f"Couldn't get the weather for {args}"


    @botcmd(split_args_with=None)
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
                return aliases
            if alias and not fullname:
                return aliases.get(alias, f"I couldn't find the fullname for {alias}")
            if alias and fullname:
                aliases[alias] = fullname
                return aliases[alias]



    @botcmd(split_args_with=' ')
    def delete_place_alias(self, alias, fullname=None):
        """(!delete_place_alias ilheus) delete any aliases associated with the short name "ilheus"
        (!delete_place_alias ilheus USA/New_York/New_York) - deletes the alias for ilheus associated with USA/New_York/New_York if it exists"
        """
        pass
