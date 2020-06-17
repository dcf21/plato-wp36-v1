# -*- coding: utf-8 -*-
# bls_vanilla.py

import numpy as np

import bls


def process_lightcurve(lc, lc_duration):
    time = lc.times
    flux = lc.fluxes

    # Run this light curve through original FORTRAN implementation of BLS
    u = np.zeros_like(time)
    v = np.zeros_like(time)

    qmi = 0.25
    qma = lc_duration / 2

    results = bls.eebls(time, flux, u, v, nf, fmin, df, nb, qmi, qma)

    # Return results
    return results
