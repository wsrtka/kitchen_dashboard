"""Module containing functions to communicate with APIs."""


import logging
import json

import requests
from requests.models import HTTPError

from src.config import LOCATION


def setup_logger():
    logger = logging.getLogger('basic')

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

    res = res.json()
    return res['lat'], res['lon']


def get_weather_data():
    lat, lon = get_lon_lan

    request_params = {
        'lat': lat,
        'lon': lon,
        'appid': ''
    }
