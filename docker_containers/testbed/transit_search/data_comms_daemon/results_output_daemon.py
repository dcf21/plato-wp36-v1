#!../../../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# run_times_output_daemon.py

"""
Listen for transit-detection results which are broadcast through RabbitMQ, and record results in output database
"""

import logging
import os
import time
import traceback

import MySQLdb
import argparse
from pika.exceptions import AMQPConnectionError
from plato_wp36 import results_logger, settings


def results_output_daemon():
    while True:
        try:
            output_connection = results_logger.ResultsToMySQL()
            output_connection.read_from_rabbitmq()
        except AMQPConnectionError:
            logging.info("AMPQ connection failure")
            time.sleep(30)
        except MySQLdb.OperationalError:
            logging.info("MySQL connection failure")
            logging.error(traceback.format_exc())
            time.sleep(30)


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

    # Run speed test
    results_output_daemon()
