# -*- coding: utf-8 -*-
# quality_control.py

import logging
import numpy as np
from astropy import units as u
from transitleastsquares import transitleastsquares

from plato_wp36.lightcurve import LightcurveArbitraryRaster


def quality_control(metadata: dict):
    """
    Determine whether the metadata returned by a transit detection algorithm is a successful detection, or a failure.

    :param metadata:
        The metadata dictionary returned by the transit detection code.
    :type metadata:
        Dict
    :return:
        Updated metadata dictionary, with QC data added.
    """

    # Test success
    outcome = "UNDEFINED"
    target_period = np.nan
    if ('orbital_period' in metadata) and ('period' in metadata):
        target_period = metadata['orbital_period']
        observed_period = metadata['period']
        period_offset = target_period / observed_period

        # For now, pick an arbitrary target, of detection period to within 10%
        if 0.9 < period_offset < 1.1:
            outcome="PASS"
        else:
            outcome="FAIL"

    # Return summary results
    metadata['outcome':] = outcome

    # Return results
    return metadata
