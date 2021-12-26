"""Contains functions used in other modules."""

import os
import logging  


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

    return prepared_data
