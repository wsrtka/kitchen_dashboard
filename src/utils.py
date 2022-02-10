"""Contains functions used in other modules."""

import os
import logging
import datetime


def setup_logger():
    """What the name says: setup logger. Log to file and to console.
    """
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

    # set formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def prepare_mpk_data(data):
    """Prepare Kraków MPK data for dashboard.

    Args:
        data (dict): MPK Kraków data API.

    Returns:
        dict: Filtered and sorted data for dashboard.
    """
    if not data:
        return

    prepared_data = {
        'departures': [],
        'alerts': []
    }

    for d in data:
        # filter out unnecessary data
        departures = [{k: v for k, v in dep.items() if k in ['actualTime', 'direction', 'patternText', 'plannedTime']} for dep in d['departures']]
        alerts = [alert for alert in d['alerts'] if alert not in prepared_data['alerts']]
        # add this data to return values
        prepared_data['departures'].extend(departures)
        prepared_data['alerts'].extend(alerts)

    current_time = datetime.datetime.now().time()

    for dep in prepared_data['departures']:
        # set key depending on mpk api
        time_key = 'actualTime' if 'actualTime' in dep else 'plannedTime'

        # calculate the timedelta for departure
        departure_time = datetime.datetime.strptime(dep[time_key], '%H:%M')
        departure_time = departure_time.time()
        departure_time = datetime.datetime.combine(datetime.date.today(), departure_time) - datetime.datetime.combine(datetime.date.today(), current_time)
        
        # get minutes
        dep['departureTime'] = departure_time.total_seconds() / 60
        dep['departureTime'] = round(dep['departureTime'])

    # sort busses and trams ascending by departure time
    prepared_data['departures'].sort(key=lambda x: x['departureTime'])
    prepared_data['departures'] = [dep for dep in prepared_data['departures'] if dep['departureTime'] >= 0]

    return prepared_data


def remove_redundant_lines(stop1, stop2):
    """Remove lines that go throgh both stops.

    Args:
        stop1 (dict): departure data for closer stop.
        stop2 (dict): departure data for further stop.

    Returns:
        dict: departure data for further stop
    """
    if not stop1 or not stop2:
        return
    lines = [dep['patternText'] for dep in stop1['departures']]
    stop2 = [dep for dep in stop2['departures'] if dep['patternText'] not in lines]
    return stop2


def get_rain_message(data):
    """Parse OpenWeatherMap API data.

    Args:
        data (dict): raw API data

    Returns:
        str: Dashboard rain message.
    """
    if not data:
        return

    for m, d in enumerate(data['minutely']):
        if d['precipitation'] > 0:
            if m == 0:
                return 'It is raining.'
            elif m == 1:
                return f'It is going to rain in {m} minute.'
            else:
                return f'It is going to rain in {m} minutes.'

    for h, d in enumerate(data['hourly']):
        if h > 12:
            return 'It is not going to rain.'
        elif d['pop'] > 0:
            if h == 1:
                return f"There is a {d['pop'] * 100}% probability that it is going to rain in {h} hour."
            else:
                return f"There is a {d['pop'] * 100}% probability that it is going to rain in {h} hours."

    return "i'm afraid I cannot do this, Dave."
