# -*- coding: utf-8 -*-
# dst_v29.py

from plato_wp36.lightcurve import LightcurveArbitraryRaster
from plato_wp36.settings import settings


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

    results = {}

    # Return results
    return results
