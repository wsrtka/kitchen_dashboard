"""Contains functions used in other modules."""

import os
import logging
import datetime


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


def prepare_mpk_data(data):
    prepared_data = {
        'departures': [],
        'alerts': []
    }

    for d in data:
        departures = [{k: v for k, v in dep.items() if k in ['actualTime', 'direction', 'patternText', 'plannedTime']} for dep in d['departures']]
        alerts = [alert for alert in d['alerts'] if alert not in prepared_data['alerts']]
        prepared_data['departures'].extend(departures)
        prepared_data['alerts'].extend(alerts)

    current_time = datetime.datetime.now().time()

    for dep in prepared_data['departures']:
        time_key = 'actualTime' if 'actualTime' in dep else 'plannedTime'

        departure_time = datetime.datetime.strptime(dep[time_key], '%H:%M')
        departure_time = departure_time.time()
        departure_time = datetime.datetime.combine(datetime.date.today(), departure_time) - datetime.datetime.combine(datetime.date.today(), current_time)
        
        dep['departureTime'] = departure_time.total_seconds() / 60
        dep['departureTime'] = round(dep['departureTime'])

    prepared_data['departures'].sort(key=lambda x: x['departureTime'])
    prepared_data['departures'] = [dep for dep in prepared_data['departures'] if dep['departureTime'] >= 0]

    return prepared_data


def remove_redundant_lines(stop1, stop2):
    lines = [dep['patternText'] for dep in stop1]
    stop2 = [dep for dep in stop2 if dep['patternText'] not in lines]
    return stop2
