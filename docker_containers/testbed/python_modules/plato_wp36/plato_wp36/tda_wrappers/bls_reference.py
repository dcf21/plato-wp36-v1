# -*- coding: utf-8 -*-
# bls_reference.py

import numpy as np
from astropy import units as u
from astropy.timeseries import BoxLeastSquares
from plato_wp36.lightcurve import LightcurveArbitraryRaster


def process_lightcurve(lc: LightcurveArbitraryRaster, lc_duration: float):
    """
    Perform a transit search on a light curve, using the bls_reference code.

    :param lc:
        The lightcurve object containing the input lightcurve.
    :type lc:
        LightcurveArbitraryRaster
    :param lc_duration:
        The duration of the lightcurve, in units of days.
    :type lc_duration:
        float
    :return:
        dict containing the results of the transit search.
    """

    t = lc.times * u.day
    y_filt = lc.fluxes

    # Run this lightcurve through the astropy implementation of BLS
    durations = np.linspace(0.05, 0.2, 10) * u.day
    model = BoxLeastSquares(t, y_filt)
    results = model.autopower(durations,
                              minimum_period=0.5 * u.day,
                              maximum_period=lc_duration / 2 * u.day,
                              minimum_n_transit=2,
                              frequency_factor=2.0)

    # Clean up results: Astropy Quantity objects are not serialisable
    results = dict(results)

    for keyword in results:
        if isinstance(results[keyword], u.Quantity):
            value_quantity = results[keyword]
            value_numeric = value_quantity.value
            value_unit = str(value_quantity.unit)

            if isinstance(value_numeric, np.ndarray):
                value_numeric = list(value_numeric)

            results[keyword] = [value_numeric, value_unit]

        elif isinstance(results[keyword], np.ndarray):
            value_numeric = list(results[keyword])
            results[keyword] = value_numeric

    # Return results
    return results
