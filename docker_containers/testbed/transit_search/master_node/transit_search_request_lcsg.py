#!../../../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# transit_search_request_lcsg.py

"""
Populate message queue with speed test tasks with all available TDAs, using LCSG lightcurves
"""

import glob
import logging
import os
import pika
import json

import argparse
from plato_wp36 import fetch_tda_list, settings

# List of all the lightcurve lengths we are to test
time_periods = [
    7 * 86400,
    10 * 86400,
    14 * 86400,
    21 * 86400,
    28 * 86400,
    1.5 * 28 * 86400,
    2 * 28 * 86400,
    2.5 * 28 * 86400,
    3 * 28 * 86400,
    4 * 28 * 86400,
    6 * 28 * 86400,
    9 * 28 * 86400,
    365.25 * 86400,
    #    2 * 365.25 * 86400
]

# Look up a list of all of the transit detection algorithms we have available
available_tdas = fetch_tda_list.fetch_tda_list()

# Directory for input lightcurves, within the <datadir_input> directory
lightcurves_directory = "lightcurves_v2"

# Path to the lightcurves we are to process, within the <lightcurves_v2> directory
lightcurves_path = "csvs/bright/"

# Create list of all LCSG lightcurves
lightcurve_list = glob.glob(
    os.path.join(settings.settings['lcPath'], lightcurves_directory, lightcurves_path, "plato_bright*")
)

# Remove lcPath from beginning of filenames
lightcurve_list = [
    os.path.join(lightcurves_path, os.path.split(filename)[1]) for filename in lightcurve_list
]

# Limit to 2 LCs for now
lightcurve_list = lightcurve_list[:2]


def request_transit_searches(broker="amqp://guest:guest@rabbitmq-service:5672", queue="tasks"):
    connection = pika.BlockingConnection(pika.URLParameters(url=broker))
    channel = connection.channel()

    channel.queue_declare(queue=queue)

    logging.info("Requesting speed tests of TDAs {}".format(available_tdas))

    # Loop over time period
    for lc_duration in time_periods:
        # Loop over TDAs
        for tda_name in available_tdas:
            # Loop over lightcurves
            for lc_filename in lightcurve_list:
                job_description = [
                    {
                        'task': 'transit_search',
                        'lc_source': 'lcsg',
                        'lc_duration': lc_duration,
                        'tda_name': tda_name,
                        'lc_directory': lightcurves_directory,
                        'lc_filename': lc_filename
                    }
                ]

                json_message = json.dumps(job_description)

                logging.info("Sending message <{}>".format(json_message))
                channel.basic_publish(exchange='', routing_key=queue, body=json_message)


if __name__ == "__main__":
    # Read command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()

    # Set up logging
    log_file_path = os.path.join(settings.settings['dataPath'], 'plato_wp36.log')
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S',
                        handlers=[
                            logging.FileHandler(log_file_path),
                            logging.StreamHandler()
                        ])
    logger = logging.getLogger(__name__)
    logger.info(__doc__.strip())

    # Request speed tests
    request_transit_searches()
