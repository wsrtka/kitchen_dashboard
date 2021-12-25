"""Module containing functions to communicate with APIs."""


import os
import logging

import requests
from requests.models import HTTPError

from src.config import LOCATION
from src.my_secrets import OWM_KEY


def setup_logger():
    logger = logging.getLogger('basic')

    # create log directory
    try:
        os.makedirs('../logs')
    except FileExistsError:
        pass

    # create debug log file
    with open('../logs/debug.log', 'w') as debug_file:
        pass

    # log debug messages into file
    fh = logging.FileHandler('../logs/debug.log')
    fh.setLevel(logging.DEBUG)

    # log error messages to console
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)


def get_lon_lan(location):
    logger = logging.getLogger('basic')
    request_params = {
        'q': location,
        'format': 'json'
    }

    res = requests.get('https://nominatim.openstreetmap.org/search', params=request_params)

    try:
        res.raise_for_status()
    except HTTPError:
        logger.exception("I'm afraid I cannot do this, Dave.")
        return

    res = res.json()[0]
    return res['lat'], res['lon']


def get_weather_data():
    lat, lon = get_lon_lan(LOCATION)

    logger = logging.getLogger('basic')
    request_params = {
        'lat': lat,
        'lon': lon,
        'appid': OWM_KEY
    }

    res = requests.get('https://api.openweathermap.org/data/2.5/onecall', params=request_params)

    try:
        res.raise_for_status()
    except HTTPError:
        logger.exception("I'm afraid I cannot do this, Dave.")
        return

    res = res.json()

    data = {
        'timezone': res['timezone'],
        'current': {
            'sunrise': res['current']['sunrise'],
            'sunset': res['current']['sunset'],
            'temp': res['current']['temp'],
            'feels_like': res['current']['feels_like'],
            'wind_speed': res['current']['wind_speed'],
            'weather': res['current']['weather'][0]['description']
        },
        'minutely': res['minutely'],
        'hourly': res['hourly'],
        'daily': res['daily'][:3]
    }

    # convert temperature to celsius
    data['current']['temp'] -= 273.15
    data['current']['feels_like'] -= 273.15

    data['current']['temp'] = round(data['current']['temp'], 2)
    data['current']['feels_like'] = round(data['current']['feels_like'], 2)

    try:
        data['alerts'] = res['alerts']
    except KeyError:
        logger.info('No weather alerts.')

    return data
