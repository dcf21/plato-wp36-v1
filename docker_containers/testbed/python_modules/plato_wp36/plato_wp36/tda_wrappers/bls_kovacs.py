# -*- coding: utf-8 -*-
# bls_kovacs.py

import numpy as np
import bls
from plato_wp36.lightcurve import LightcurveArbitraryRaster


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

    time = lc.times  # Unit of days
    flux = lc.fluxes

    # Median subtract lightcurve
    median = np.median(flux)
    flux -= median

    # Run this light curve through original FORTRAN implementation of BLS
    u = np.zeros(len(time))
    v = np.zeros(len(time))

    # Minimum transit length
    qmi = 0.05

    # Maximum transit length
    qma = 0.2

    # Minimum transit period, days
    minimum_period = float(search_settings.get('period_min', 0.5))
    fmax = 1 / minimum_period

    # Maximum transit period, seconds
    # Arithmetic here based on <https://docs.astropy.org/en/stable/api/astropy.timeseries.BoxLeastSquares.html#astropy.timeseries.BoxLeastSquares.autoperiod>
    minimum_n_transits = 2
    maximum_period = float(search_settings.get('period_max', lc_duration / minimum_n_transits))
    fmin = 1 / maximum_period

    # Frequency spacing
    frequency_factor = 2
    df = frequency_factor * qmi / lc_duration ** 2
    nf = (fmax - fmin) / df

    # Number of bins (maximum 2000)
    # For large number of bins, the FORTRAN code seems to segfault, which limits usefulness of this code
    # See issue described here <https://github.com/dfm/python-bls/issues/4>
    nb = 10

    # results = {}
    results = bls.eebls(time, flux, u, v, nf, fmin, df, nb, qmi, qma)

    # Unpack results
    power, best_period, best_power, depth, q, in1, in2 = results

    results = {
        "period": best_period,
        "power": best_power,
        "depth": depth
    }

    # Extended results to save to disk
    results_extended = results

    # Return results
    return results, results_extended
