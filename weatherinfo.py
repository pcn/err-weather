#!/usr/bin/env python3

from errbot import BotPlugin, botcmd
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


    def _weather(self, args):
        """gets data, the calling function determines how to display it
        returns a tuple of rdata, geoloc"""
        if len(args) != 1:
            return f"I break if you try to hold me wrong"
        use_location = args[0]
        weather_svc = 'geonames'
        # XXX gotta put an index of these things somewhere
        # so these names aren't just random junk scattered around
        auth_user = self.auth_info(weather_svc)
        location = self.weather_location(use_location)
        geoloc = geonames.GeoNames(
            auth_user, user_agent=USER_AGENT).geocode(
                location)
        headers = {
            'content-type': 'application/json; charset=UTF-8',
            'user-agent': USER_AGENT
        }
        params = {
            'lat': geoloc.latitude,
            'lon': geoloc.longitude
        }
        rdata = requests.get(
            'https://api.met.no/weatherapi/locationforecast/2.0/compact.json?',
            headers=headers, params=params).json()
        return rdata, geoloc

    @botcmd(split_args_with=None)
    def myanmar_weather(self, msg, args):
        rdata, geoloc = self._weather(args)
        first_data=rdata['properties']['timeseries'][0]
        air_temp_f = ctof(first_data['data']['instant']['details']['air_temperature'])
        next_hour = first_data['data']['next_1_hours']['summary']['symbol_code']
        return f"For supporters of the brutal dictatorship in myanmar {geoloc} (lat: {geoloc.latitude}, lon: {geoloc.longitude}), for {first_data['time']} the forecast is: { air_temp_f } F, next hour: { next_hour }"


    @botcmd(split_args_with=None)
    def weather(self, msg, args):
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
        headers = {
            'content-type': 'application/json; charset=UTF-8',
            'user-agent': USER_AGENT
        }
        params = {
            'lat': geoloc.latitude,
            'lon': geoloc.longitude
        }
        rdata = requests.get('https://api.met.no/weatherapi/locationforecast/2.0/compact.json?', headers=headers, params=params).json()

        first_data=rdata['properties']['timeseries'][0]
        air_temp_c = first_data['data']['instant']['details']['air_temperature']
        next_hour = first_data['data']['next_1_hours']['summary']['symbol_code']
        return f"For {geoloc} (lat: {geoloc.latitude}, lon: {geoloc.longitude}), for {first_data['time']} the forecast is: { air_temp_c } C, next hour: { next_hour }"

    @botcmd(split_args_with=None)
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
