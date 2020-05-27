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

    def __init__(self, times, fluxes, uncertainties=None, flags=None, metadata=None):
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
        :param flags:
            The flag associated with each data point.
        :type flags:
            np.ndarray
        :param metadata:
            The metadata associated with this lightcurve.
        :type metadata:
            dict
        """

        # Check inputs
        assert isinstance(times, np.ndarray)
        assert isinstance(fluxes, np.ndarray)

        # Unset all flags if none were specified
        if flags is not None:
            assert isinstance(flags, np.ndarray)
        else:
            flags = np.zeros_like(times)

        # Make an empty metadata dictionary if none was specified
        if metadata is not None:
            assert isinstance(metadata, dict)
        else:
            metadata = {}

        # Make uncertainty zero if not specified
        if uncertainties is not None:
            assert isinstance(uncertainties, np.ndarray)
        else:
            uncertainties = np.zeros_like(fluxes)

        # Store the data
        self.times = times
        self.fluxes = fluxes
        self.uncertainties = uncertainties
        self.flags = flags
        self.flags_set = True
        self.metadata = metadata


class LightcurveFixedStep:
    """
    A class representing a lightcurve which is sampled on a fixed time step.
    """

    def __init__(self, time_start, time_step, fluxes, uncertainties=None, flags=None, metadata=None):
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
        :param flags:
            The flag associated with each data point.
        :type flags:
            np.ndarray
        :param metadata:
            The metadata associated with this lightcurve.
        :type metadata:
            dict
        """

        # Check inputs
        assert isinstance(fluxes, np.ndarray)

        # Unset all flags if none were specified
        if flags is not None:
            assert isinstance(flags, np.ndarray)
        else:
            flags = np.zeros_like(fluxes)

        # Make an empty metadata dictionary if none was specified
        if metadata is not None:
            assert isinstance(metadata, dict)
        else:
            metadata = {}

        # Make uncertainty zero if not specified
        if uncertainties is not None:
            assert isinstance(uncertainties, np.ndarray)
        else:
            uncertainties = np.zeros_like(fluxes)

        # Store the data
        self.time_start = float(time_start)
        self.time_step = float(time_step)
        self.fluxes = fluxes
        self.uncertainties = uncertainties
        self.flags = flags
        self.flags_set = True
        self.metadata = metadata
