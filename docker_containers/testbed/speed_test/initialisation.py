#!../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# initialisation.py

"""
Initialise the light curve speed test output database
"""

import os
import argparse
import logging

from plato_wp36 import settings, results_database


def initialise_speed_test():
    logging.info("Initialising speed test database")

    # Make sure that SQL database exists to hold the run times for each transit detection algorithm
    results_database.ResultsDatabase(refresh=True)

    # Wipe JSON files
    os.system("rm -Rf {}/*".format(os.path.join(settings.settings['dataPath'], "json_out")))

    # Wipe scratch space
    os.system("rm -Rf {}/*".format(os.path.join(settings.settings['dataPath'], "scratch")))


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

    # Do initialisation
    initialise_speed_test()
