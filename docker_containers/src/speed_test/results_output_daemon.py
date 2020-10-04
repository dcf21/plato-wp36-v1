#!../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# run_times_output_daemon.py

"""
Listen for transit-detection results which are broadcast through RabbitMQ, and record results in output database
"""

import os
import argparse
import logging

from plato_wp36 import results_logger, settings


def results_output_daemon():
    output_connection = results_logger.ResultsToMySQL()
    output_connection.read_from_rabbitmq()


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

    # Run speed test
    results_output_daemon()
