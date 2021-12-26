"""Module containing functions to communicate with APIs."""


import logging

import requests
from requests.models import HTTPError

from src.config import LOCATION
from src.my_secrets import OWM_KEY


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


def get_departures(stop):
    logger = logging.getLogger('basic')
    
    try:
        assert stop in ('szwedzka', 'grunwaldzkie')
    except AssertionError:
        logger.exception("I'm afraid I cannot do this, Dave.")

    url_bus = 'http://ttss.mpk.krakow.pl/internetservice/services/passageInfo/stopPassages/stop'
    url_tram = 'http://www.ttss.krakow.pl/internetservice/services/passageInfo/stopPassages/stop'
    if stop == 'szwedzka':
        request_params = {'stop': 575}
    else:
        request_params = {'stop': 3338}

    busses_data = requests.get(url_bus, params=request_params)
    trams_data = requests.get(url_tram, params=request_params)

    try:
        busses_data.raise_for_status()
        trams_data.raise_for_status()
    except HTTPError:
        logger.exception("I'm afraid I cannot do this, Dave.")
        return

    busses_data = busses_data.json()
    trams_data = trams_data.json()

    busses = {
        'departures': busses_data['actual'],
        'alerts': busses_data['generalAlerts']
    }
    trams = {
        'departures': trams_data['actual'],
        'alerts': trams_data['generalAlerts']
    }

    return busses, trams
