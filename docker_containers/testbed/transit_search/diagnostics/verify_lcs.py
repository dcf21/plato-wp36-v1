#!../../../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# verify_lcs.py

"""
Check that the input lightcurves are sampled at a fixed time step
"""

import glob
import logging
import os

import argparse
from plato_wp36 import lc_reader_lcsg, settings

lightcurves_path = "csvs/bright/plato_bright*"

lightcurve_list = glob.glob(
    os.path.join(settings.settings['lcPath'], lightcurves_path)
)

# Limit to 2 LCs for now
lightcurve_list = lightcurve_list[:2]


def verify_lcs():
    logging.info("Verifying that LCs are sampled at a fixed time step")

    # Loop over lightcurves
    for lc_filename in lightcurve_list:
        lc = lc_reader_lcsg.read_lcsg_lightcurve(
            filename=lc_filename,
            gzipped=True
        )

        display_name = os.path.split(lc_filename)[1]

        # Run first code for checking LCs
        error_count = lc.check_fixed_step(verbose=True, max_errors=4)

        if error_count == 0:
            logging.info("V1: Lightcurve <{}> has fixed step".format(display_name))
        else:
            logging.info("V1: Lightcurve <{}> doesn't have fixed step ({:d} errors)".format(display_name, error_count))

        # Run second code for checking LCs
        error_count = lc.check_fixed_step_v2(verbose=True, max_errors=4)

        if error_count == 0:
            logging.info("V2: Lightcurve <{}> has fixed step".format(display_name))
        else:
            logging.info("V2: Lightcurve <{}> doesn't have fixed step ({:d} errors)".format(display_name, error_count))


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

    # Verify lightcurves
    verify_lcs()
