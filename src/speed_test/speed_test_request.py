#!../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# speed_test_request.py

"""
Populate message queue with speed test tasks with all available TDAs
"""

import glob
import logging
import os
import pika
import json

import argparse
from plato_wp36 import fetch_tda_list, settings

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
    #    365.25 * 86400,
    #    2 * 365.25 * 86400
]

available_tdas = fetch_tda_list.fetch_tda_list()

lightcurves_path = "csvs/bright/plato_bright*"

lightcurve_list = glob.glob(
    os.path.join(settings.settings['lcPath'], lightcurves_path)
)

# Limit to 8 LCs for now
lightcurve_list = lightcurve_list[:8]


def request_speed_tests(broker="amqp://guest:guest@rabbitmq-service:5672", queue="tasks"):
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
                test_description = {
                    'lc_duration': lc_duration,
                    'tda_name': tda_name,
                    'lc_filename': lc_filename
                }

                json_message = json.dumps(test_description)

                logging.info("Sending message <{}>".format(json_message))
                channel.basic_publish(exchange='', routing_key=queue, body=json_message)


if __name__ == "__main__":
    # Read commandline arguments
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
    request_speed_tests()
