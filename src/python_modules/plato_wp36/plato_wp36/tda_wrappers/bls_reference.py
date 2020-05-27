# -*- coding: utf-8 -*-
# bls_reference.py

import numpy as np

from astropy import units as u

from astropy.timeseries import BoxLeastSquares

def process_lightcurve(lc, lc_duration):
    t = lc.times * u.day
    y_filt = lc.fluxes

    durations = np.linspace(0.05, 0.2, 10) * u.day
    model = BoxLeastSquares(t, y_filt)
    results = model.autopower(durations,
                              minimum_period=0.25 * u.day,
                              maximum_period=lc_duration / 2 * u.day,
                              minimum_n_transit=2,
                              frequency_factor=1.0)

    return results
