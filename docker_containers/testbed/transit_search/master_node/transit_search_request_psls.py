#!../../../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# transit_search_request_psls.py

"""
Populate message queue with speed test tasks with all available TDAs, using lightcurves synthesised on-the-fly with PSLS
"""

import logging
import os
import pika
import json

import argparse
from plato_wp36 import fetch_tda_list, settings

# List of all the lightcurve lengths we are to test
time_periods = [
    3 * 28 * 86400,
    4 * 28 * 86400,
    6 * 28 * 86400,
    9 * 28 * 86400,
    365.25 * 86400,
    2 * 365.25 * 86400
]

# Look up a list of all of the transit detection algorithms we have available
available_tdas = ['tls']

# Directory for input lightcurves, within the <datadir_input> directory
lightcurves_directory = "psls_temporary"

# Create list of all LCSG lightcurves
lightcurve_specs = [
    {
        'filename': 'lc0001'
    }
]


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
            for lc_info in lightcurve_specs:
                job_description = [
                    # 1) Synthesise LC using PSLS
                    {
                        'task': 'psls_synthesise',
                        'lc_source': 'psls',
                        'lc_duration': 3 * 365.25 * 86400,
                        'lc_directory': lightcurves_directory,
                        'lc_filename': lc_info['filename']
                    },
                    # 2) Verify lightcurve
                    {
                        'task': 'verify_lc',
                        'lc_source': 'psls',
                        'lc_directory': lightcurves_directory,
                        'lc_filename': lc_info['filename']
                    },
                    # 3) Perform transit search on LC
                    {
                        'task': 'transit_search',
                        'lc_source': 'psls',
                        'lc_duration': lc_duration,
                        'tda_name': tda_name,
                        'lc_directory': lightcurves_directory,
                        'lc_filename': lc_info['filename']
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
