# -*- coding: utf-8 -*-
# tls.py

import numpy as np
from astropy import units as u
from transitleastsquares import transitleastsquares


def process_lightcurve(lc, lc_duration):
    time = lc.times
    flux = lc.fluxes

    # Run this lightcurve through Transit Least Squares
    model = transitleastsquares(time, flux)
    results = model.power()

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
