#!../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# speed_test.py

"""
Run speed tests with all available TDAs, and record results in output database
"""

import os
import argparse
import logging

from plato_wp36 import fetch_tda_list, settings

time_periods = [
    7 * 86400,
    14 * 86400,
    28 * 86400,
    3 * 28 * 86400,
    6 * 28 * 86400,
    365.25 * 86400,
    2 * 365.25 * 86400
]

available_tdas = fetch_tda_list.fetch_tda_list()


def run_speed_test():
    logging.info("Starting speed test of TDAs {}".format(available_tdas))


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
    run_speed_test()
