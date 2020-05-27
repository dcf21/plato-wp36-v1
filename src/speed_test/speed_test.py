#!../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# speed_test.py

"""
Run speed tests with all available TDAs, and record results in output database
"""

import glob
import logging
import os

import argparse
from plato_wp36 import fetch_tda_list, lcsg_lc_reader, settings, run_time_logger, task_timer

from plato_wp36.tda_wrappers import bls_reference, tls

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
    365.25 * 86400,
    2 * 365.25 * 86400
]

available_tdas = fetch_tda_list.fetch_tda_list()

lightcurves_path = "lightcurves_v2/csvs/bright/plato_bright*"

lightcurve_list = glob.glob(
    os.path.join(settings.settings['dataPath'], lightcurves_path)
)

# Limit to 4 LCs for now
lightcurve_list = lightcurve_list[:1]


def speed_test(lc_duration, tda_name, lc_filename):
    logging.info("Running <{lc_filename}> through <{tda_name}> with duration {lc_days:.1f}.".format(
        lc_filename=lc_filename,
        tda_name=tda_name,
        lc_days=lc_duration / 86400)
    )

    # Make sure that sqlite3 database exists to hold the run times for each transit detection algorithm
    time_log = run_time_logger.RunTimeLogger()

    # Load lightcurve
    with task_timer.TaskTimer(tda_code=tda_name, target_name=lc_filename, task_name='load', lc_length=lc_duration,
                              time_logger=time_log):
        lc = lcsg_lc_reader.read_lcsg_lightcurve(
            filename=lc_filename,
            gzipped=True,
            cut_off_time=lc_duration / 86400
        )

    # Process lightcurve
    with task_timer.TaskTimer(tda_code=tda_name, target_name=lc_filename, task_name='proc', lc_length=lc_duration,
                              time_logger=time_log):
        if tda_name == 'tls':
            tls.process_lightcurve(lc, lc_duration / 86400)
        else:
            bls_reference.process_lightcurve(lc, lc_duration / 86400)



def run_speed_test():
    logging.info("Starting speed test of TDAs {}".format(available_tdas))

    # Loop over time period
    for lc_duration in time_periods:
        # Loop over TDAs
        for tda_name in available_tdas:
            # Loop over lightcurves
            for lc_filename in lightcurve_list:
                # Process LC
                speed_test(
                    lc_duration=lc_duration,
                    tda_name=tda_name,
                    lc_filename=lc_filename
                )


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
