# -*- coding: utf-8 -*-
# tls.py


import numpy as np

from astropy import units as u

from transitleastsquares import transitleastsquares
def process_lightcurve(lc, lc_duration):
    time = lc.times
    flux = lc.fluxes
    model = transitleastsquares(time, flux)
    results = model.power()
    return