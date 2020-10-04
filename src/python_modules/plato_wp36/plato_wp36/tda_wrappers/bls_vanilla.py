# -*- coding: utf-8 -*-
# bls_vanilla.py

import numpy as np

import bls


def process_lightcurve(lc, lc_duration):
    time = lc.times  # Unit of days
    flux = lc.fluxes

    # Run this light curve through original FORTRAN implementation of BLS
    u = np.zeros_like(time)
    v = np.zeros_like(time)

    # Minimum transit length
    qmi = 0.05

    # Maximum transit length
    qma = 0.2

    # Minimum transit period, days
    minimum_period = 0.5
    fmax = 1 / minimum_period

    # Maximum transit period, days
    # Arithmetic here based on <https://docs.astropy.org/en/stable/api/astropy.timeseries.BoxLeastSquares.html#astropy.timeseries.BoxLeastSquares.autoperiod>
    minimum_n_transits = 2
    maximum_period = lc_duration / minimum_n_transits
    fmin = 1 / maximum_period

    # Frequency spacing
    frequency_factor = 2
    df = frequency_factor * qmi / lc_duration ** 2
    nf = (fmax - fmin) / df

    # Number of bins (maximum 2000)
    nb = 2000

    results = bls.eebls(time, flux, u, v, nf, fmin, df, nb, qmi, qma)

    # Return results
    return results
