# -*- coding: utf-8 -*-
# tls.py

import logging
import numpy as np
from astropy import units as u
from transitleastsquares import transitleastsquares

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

    time = lc.times
    flux = lc.fluxes

    # Fix normalisation
    flux_normalised = flux / np.mean(flux)
    logging.info("Lightcurve metadata: {}".format(lc.metadata))

    # Create a list of settings to pass to TLS
    tls_settings = {}

    if 'period_min' in search_settings:
        tls_settings['period_min'] = float(search_settings['period_min'])  # Minimum trial period, days
    if 'period_max' in search_settings:
        tls_settings['period_max'] = float(search_settings['period_max'])  # Maximum trial period, days

    # Run this lightcurve through Transit Least Squares
    model = transitleastsquares(time, flux_normalised)
    results = model.power(**tls_settings)

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
        'sde': results.SDE
    }

    # Extended results to save to disk
    results_extended = results

    # Return results
    return results, results_extended
