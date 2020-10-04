# -*- coding: utf-8 -*-
# qats.py

from math import floor, log
import numpy as np
import os
import secrets
from subprocess import Popen, PIPE


def process_lightcurve(lc, lc_duration):
    # Convert input lightcurve to a fixed time step, and fill in gaps
    lc_fixed_step = lc.to_fixed_step()

    # Median subtract lightcurve
    median = np.median(lc_fixed_step.fluxes)
    lc_fixed_step.fluxes -= median

    # Normalise lightcurve
    std_dev = np.std(lc_fixed_step.fluxes)
    lc_fixed_step.fluxes /= std_dev

    # Store lightcurve to text file
    tmp_dir_name = secrets.token_hex(15)
    tmp_dir = "/tmp/qats/{}/".format(tmp_dir_name)
    lc_file = os.path.join(tmp_dir, "lc.dat")

    np.savetxt(lc_file, lc_fixed_step.fluxes)

    # List of transit durations to consider
    durations = np.linspace(0.05, 0.2, 10) / lc_fixed_step.time_step

    # Minimum transit period, days
    minimum_period = 0.5

    # Maximum transit period, days
    minimum_n_transits = 2
    maximum_period = lc_duration / minimum_n_transits

    # Maximum TTV relative magnitude f
    f = 0.1
    sigma_spans = int(floor(log(maximum_period / minimum_period)) / log(f))
    sigma_min = minimum_period / lc_fixed_step.time_step

    # Initialise empty results structure
    results = []

    # Loop over all values of q
    for transit_length in durations:
        for sigma_index in range(0, sigma_spans):
            # Equation 15
            sigma_min = sigma_min * pow(1 + f/2, sigma_index)

            # Equation 16
            sigma_max = sigma_min * (1 + f/2)

            # Run QATS
            p = Popen(['/plato_eas/qats/qats/call_qats',
                       lc_file, str(sigma_min), str(sigma_max), str(transit_length)],
                      stdin=None, stdout=PIPE, stderr=PIPE)
            output, err = p.communicate()
            rc = p.returncode

            # Store output
            results.append(output)

    # Return results
    return results
