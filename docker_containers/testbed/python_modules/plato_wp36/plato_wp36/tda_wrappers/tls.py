# -*- coding: utf-8 -*-
# tls.py

import logging
import numpy as np
from astropy import units as u
from transitleastsquares import transitleastsquares

from plato_wp36.lightcurve import LightcurveArbitraryRaster


def process_lightcurve(lc: LightcurveArbitraryRaster, lc_duration: float):
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
    :return:
        dict containing the results of the transit search.
    """

    time = lc.times
    flux = lc.fluxes

    # Fix normalisation
    flux_normalised = flux / np.mean(flux)
    logging.info("Lightcurve metadata: {}".format(lc.metadata))

    # Run this lightcurve through Transit Least Squares
    model = transitleastsquares(time, flux_normalised)
    results = model.power()

    # Clean up results: Astropy Quantity objects are not serialisable
    # results = dict(results)
    #
    # for keyword in results:
    #     if isinstance(results[keyword], u.Quantity):
    #         value_quantity = results[keyword]
    #         value_numeric = value_quantity.value
    #         value_unit = str(value_quantity.unit)
    #
    #         if isinstance(value_numeric, np.ndarray):
    #             value_numeric = list(value_numeric)
    #
    #         results[keyword] = [value_numeric, value_unit]
    #
    #     elif isinstance(results[keyword], np.ndarray):
    #         value_numeric = list(results[keyword])
    #         results[keyword] = value_numeric

    # Work out how many transit we found
    transit_count = 0
    if isinstance(results.transit_times, list):
        transit_count = len(results.transit_times)

    # Return summary results
    results = {
        'period': results.period,
        'transit_count': transit_count,
        'depth': results.depth,
        'duration': results.duration,
        'sde': results.SDE,
        'target_period': target_period
    }

    # Extended results to save to disk
    results_extended = results

    # Return results
    return results, results_extended
