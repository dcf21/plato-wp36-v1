# -*- coding: utf-8 -*-
# lightcurve.py

"""
Classes for representing light curves, either on arbitrary time rasters, or on rasters with fixed step.
"""

import numpy as np


class LightcurveArbitraryRaster:
    """
    A class representing a lightcurve which is sampled on an arbitrary raster of times.
    """

    def __init__(self, times, fluxes, uncertainties=None):
        """
        Create a lightcurve which is sampled on an arbitrary raster of times.

        :param times:
            The times of the data points.
        :type times:
            np.ndarray
        :param fluxes:
            The light fluxes at each data point.
        :type fluxes:
            np.ndarray
        :param uncertainties:
            The uncertainty in each data point.
        :type uncertainties:
            np.ndarray
        """

        # Check inputs
        assert isinstance(times, np.ndarray)
        assert isinstance(fluxes, np.ndarray)

        # Make uncertainty zero if not specified
        if uncertainties is None:
            uncertainties = np.zeros_like(fluxes)

        # Check inputs
        assert isinstance(uncertainties, np.ndarray)

        # Store the data
        self.times = times
        self.fluxes = fluxes


class LightcurveFixedStep:
    """
    A class representing a lightcurve which is sampled on a fixed time step.
    """

    def __init__(self, time_start, time_step, fluxes, uncertainties=None):
        """
        Create a lightcurve which is sampled on an arbitrary raster of times.

        :param time_start:
            The time at the start of the lightcurve.
        :type time_start:
            float
        :param time_step:
            The interval between the points in the lightcurve.
        :type time_step:
            float
        :param fluxes:
            The light fluxes at each data point.
        :type fluxes:
            np.ndarray
        :param uncertainties:
            The uncertainty in each data point.
        :type uncertainties:
            np.ndarray
        """

        # Check inputs
        assert isinstance(fluxes, np.ndarray)

        # Make uncertainty zero if not specified
        if uncertainties is None:
            uncertainties = np.zeros_like(fluxes)

        # Check inputs
        assert isinstance(uncertainties, np.ndarray)

        # Store the data
        self.time_start = float(time_start)
        self.time_step = float(time_step)
        self.fluxes = fluxes
        self.uncertainties = uncertainties
