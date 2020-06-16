#!../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# verify_lcs.py

"""
Check that the input lightcurves are sampled at a fixed time step
"""

import glob
import logging
import os

import argparse
from plato_wp36 import lcsg_lc_reader, settings

lightcurves_path = "lightcurves_v2/csvs/bright/plato_bright*"

lightcurve_list = glob.glob(
    os.path.join(settings.settings['dataPath'], lightcurves_path)
)

# Limit to 4 LCs for now
lightcurve_list = lightcurve_list[:1]


def verify_lcs():
    logging.info("Verifying that LCs are sampled at a fixed time step")

    # Loop over lightcurves
    for lc_filename in lightcurve_list:
        lc = lcsg_lc_reader.read_lcsg_lightcurve(
            filename=lc_filename,
            gzipped=True
        )

        lc.check_fixed_step()


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

    # Verify lightcurves
    verify_lcs()
