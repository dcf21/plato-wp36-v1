#!../../../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# transit_search_request_psls.py

"""
Populate message queue with speed test tasks with all available TDAs, using lightcurves synthesised on-the-fly with PSLS
"""

import json
import logging
import os

import argparse
import pika
from plato_wp36 import settings

# List of all the lightcurve lengths we are to test (days)
time_periods = [
    3 * 28,
    4 * 28,
    6 * 28,
    9 * 28,
    365.25,
    2 * 365.25
]

# Look up a list of all of the transit-detection algorithms we have available
available_tdas = ['tls']

# Directory for input lightcurves, within the <datadir_input> directory
lightcurves_directory = "psls_output"

# Create list of all lightcurves we are to generate
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

    # ID for the job that these tasks are part of
    job_name = 'psls_transit_search'

    # Loop over time period
    for lc_duration in time_periods:
        # Loop over TDAs
        for tda_name in available_tdas:
            # Loop over lightcurves
            for lc_info in lightcurve_specs:
                storage = {
                    'source': 'archive',
                    'directory': lightcurves_directory,
                    'filename': lc_info['filename']

                }

                task_list = [
                    # 1) Synthesise LC using PSLS
                    {
                        'task': 'psls_synthesise',
                        'target': storage,
                        'specs': {
                            'duration': lc_duration,  # days
                            'planet_radius': 0.1,  # Jupiter radii
                            'orbital_period': 1,  # days
                            'semi_major_axis': 0.01,  # AU
                            'orbital_angle': 0  # degrees
                        }
                    },
                    # 2) Verify lightcurve
                    {
                        'task': 'verify',
                        'source': storage
                    },
                    # 3) Perform transit search on LC
                    {
                        'task': 'transit_search',
                        'source': storage,
                        'lc_duration': lc_duration,
                        'tda_name': tda_name
                    }
                ]

                json_message = json.dumps({
                    'job_name': job_name,
                    "clean_up": 0,
                    'task_list': task_list
                })

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
