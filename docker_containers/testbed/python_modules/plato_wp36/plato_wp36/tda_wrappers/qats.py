# -*- coding: utf-8 -*-
# qats.py

from math import floor, log
import logging
import numpy as np
import os
import secrets
from subprocess import Popen, PIPE

from plato_wp36.lightcurve import LightcurveArbitraryRaster
from plato_wp36.settings import settings


def process_lightcurve(lc: LightcurveArbitraryRaster, lc_duration: float, search_settings: dict):
    """
    Perform a transit search on a light curve, using the bls_kovacs code.

    :param lc:
        The lightcurve object containing the input lightcurve.
    :type lc:
        LightcurveArbitraryRaster
    :param lc_duration:
        The duration of the lightcurve, in units of days.
    :type lc_duration:
        float
    :param search_settings:
        Dictionary of settings which control how we search for transits.
    :type search_settings:
        dict
    :return:
        dict containing the results of the transit search.
    """

    # Convert input lightcurve to a fixed time step, and fill in gaps
    lc_fixed_step = lc.to_fixed_step()

    # Median subtract lightcurve
    median = np.median(lc_fixed_step.fluxes)
    lc_fixed_step.fluxes -= median

    # Normalise lightcurve
    std_dev = np.std(lc_fixed_step.fluxes)
    lc_fixed_step.fluxes /= std_dev

    # Pick a random filename to use to store lightcurve to a text file
    tmp_dir_name = secrets.token_hex(15)
    tmp_dir = "/tmp/qats/{}/".format(tmp_dir_name)
    lc_file = os.path.join(tmp_dir, "lc.dat")

    # Create temporary directory to hold light curve
    os.system("mkdir -p {}".format(tmp_dir))

    # Store lightcurve to text file
    np.savetxt(lc_file, lc_fixed_step.fluxes)

    # List of transit durations to consider
    lc_time_step = lc_fixed_step.time_step  # seconds
    lc_time_step_days = lc_time_step / 86400  # days
    durations_days = np.linspace(0.05, 0.2, 5)  # days
    durations = durations_days / lc_time_step_days  # time steps

    # Minimum transit period, days
    minimum_period = 0.5  # days

    # Maximum transit period, days
    minimum_n_transits = 2
    maximum_period = lc_duration / minimum_n_transits  # days

    # Maximum TTV relative magnitude f
    f = 0.15
    sigma_spans = int(floor(log(maximum_period / minimum_period) / log(1 + f)))
    sigma_min = minimum_period / lc_time_step_days  # time steps

    # Initialise empty results structure
    results_extended = []

    # Logging
    logging.info("QATS testing {:d} transit lengths".format(len(durations)))
    logging.info("QATS testing {} sigma spans".format(sigma_spans))

    # Loop over all values of q
    for transit_length in durations:
        for sigma_index in range(0, sigma_spans):
            # Equation 15
            sigma_min = sigma_min * pow(1 + f / 2, sigma_index)

            # Equation 16
            sigma_max = sigma_min * (1 + f / 2)

            # Run QATS
            qats_path = os.path.join(settings['pythonPath'], "../datadir_local/qats/qats/call_qats")
            p = Popen([qats_path,
                       lc_file, str(sigma_min), str(sigma_max), str(transit_length)],
                      stdin=None, stdout=PIPE, stderr=PIPE)
            output, err = p.communicate()
            rc = p.returncode

            # Logging
            logging.info("QATS returned status code <{}>".format(rc))
            logging.info("QATS returned error text <{}>".format(err))

            # Store output
            results_extended.append(output.decode('utf-8'))

    # Extended results to save to disk
    results = {}

    # Clean up temporary directory
    os.system("rm -Rf {}".format(tmp_dir))

    # Return results
    return results, results_extended
