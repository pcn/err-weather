#!/usr/bin/env python3

from errbot import BotPlugin, botcmd
from yr.libyr import Yr
from urllib import error
import json
import requests

from geopy.geocoders import geonames


USER_AGENT='ernies-y-archer-bot'

def ctof(celc):
    """Convert celcius to farenheit"""
    return (float(celc) * 1.8) + 32.0


class Weatherinfo(BotPlugin):
    """grab short weather informations around the globe

    TODO: set up the WEATHER_PLACE_ALIASES to be initialized if it's empty, I think?
    """
    def initialize_persistence(self, key, empty):
        """Conditinonally initialize an empty
        container for persistence, but only if it
        is not currently bound"""
        self.log.info(f"Checking to see if {key} is available")
        if not self.get(key):
            self.log.info(f"Initializing {key} is available")
            self[key] = empty


    def weather_location(self, location_name):
        """Lookup a location alias."""
        with self.mutable('WEATHER_PLACE_ALIASES') as aliases:
            return aliases.get(location_name, location_name)


    def auth_info(self, auth_name):
        """Get the auth user that has been set by geo_auth()"""
        with self.mutable('WEATHER_AUTH_TOKENS') as tokens:
            return tokens.get(auth_name)


    @botcmd(split_args_with=None)
    def geo_auth(self, msg, args):
        """
        (!geo_auth geonames <username>) provide the username that is authorized to use the geonames API
        """
        key = 'WEATHER_AUTH_TOKENS'
        self.log.warning(f"Got these args: {msg} {args}")
        self.initialize_persistence(key, dict())
        try:
            with self.mutable(key) as auth_tokens:
                if len(args) == 2:
                    if args[0] == 'geonames':
                        auth_tokens['geonames'] = args[1]
                return auth_tokens
        except TypeError as e:
            self.log.warning(f"Tried to get the WEATHER_AUTH_TOKENS and failed with {str(e)}, so I'm going to initialize it")
            return f"I couldn't get {key} from the persistence layer!"


    @botcmd(split_args_with=None)
    def new_weather(self, msg, args):
        """
        (!new_weather ilheus) return the weather for a location
        """
        if len(args) != 1:
            return f"I break if you try to hold me wrong"
        use_location = args[0]
        alias_key = 'WEATHER_PLACE_ALIASES'
        auth_key = 'WEATHER_AUTH_TOKENS'
        weather_svc = 'geonames'
        # XXX gotta put an index of these things somewhere
        # so this isn't just random junk scattered around
        auth_user = self.auth_info(weather_svc)
        location = self.weather_location(use_location)
        geoloc = geonames.GeoNames(
            auth_user, user_agent=USER_AGENT).geocode(
                location)
        return f"The location is {geoloc}, lat: {geoloc.lat} lon: {geoloc.lon}"

    @botcmd(split_args_with=None)
    def weather(self, msg, args):
        """(!weather berlin) grab weather information for cities, regions, or alias names thereof
        """
        use_location = args[0]
        # aliases = dict()
        # self['WEATHER_PLACE_ALIASES'] = aliases

        with self.mutable('WEATHER_PLACE_ALIASES') as aliases:
            try:
                if aliases.get(use_location):
                    self.log.debug(f"{use_location} found as an alias to {aliases[use_location]}")
                    use_location = aliases[use_location]
                else:
                    self.log.debug(f"{use_location} wasn't found in aliases")
                weather = Yr(location_name=use_location)
                temp = weather.now()['temperature']['@value']
                return f"Weather for {weather.location_name}: {temp} C (or {ctof(temp)} F if you've got your shit together like Liberia or Burma)"
            except error.HTTPError as e:
                self.log.error(f"Got an error trying to access the {str(e)}")
                return f"Couldn't get the weather for {use_location}"


    @botcmd(split_args_with=None)
    def place_alias(self, msg, args):
        """(!place_alias) returns aliases that've been defined for places
        (!place_alias Brasil/Bahia/Ilhéus ilheus) saves "ilheus" as an alias for the longer place name
        """
        # aliases = dict()
        # self['WEATHER_PLACE_ALIASES'] = aliases

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
