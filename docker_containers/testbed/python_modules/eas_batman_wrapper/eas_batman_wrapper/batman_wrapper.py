# -*- coding: utf-8 -*-
# batman_wrapper.py

"""
Class for synthesising lightcurves using Batman.
"""

import multiprocessing
from math import acos, pi, sqrt

import batman
import numpy as np
from plato_wp36 import lightcurve
from plato_wp36.constants import *

defaults = {
    'duration': 730,  # days
    't0': 1,  # Time for inferior conjunction (days)
    'eccentricity': 0,
    'star_radius': sun_radius / jupiter_radius,  # Jupiter radii
    'planet_radius': 1,  # Jupiter radii
    'orbital_period': 365,  # days
    'semi_major_axis': 1,  # AU
    'orbital_angle': 0,  # degrees
    'impact_parameter': None,  # Impact parameter (0-1); overrides <orbital_angle> if not None
    'noise': 0,
    'sampling_cadence': 25,  # sampling cadence, seconds
    'threads': 1  # Number of threads to use. None means use all available CPU core. DO NOT SET != 1!!!
}


class BatmanWrapper:
    """
    Class for synthesising lightcurves using Batman.
    """

    def __init__(self,
                 duration=None,
                 eccentricity=None,
                 t0=None,
                 star_radius=None,
                 planet_radius=None,
                 orbital_period=None,
                 semi_major_axis=None,
                 orbital_angle=None,
                 impact_parameter=None,
                 noise=None,
                 sampling_cadence=None,
                 threads=None
                 ):
        """
        Instantiate wrapper for synthesising lightcurves using Batman
        """

        # Create dictionary of settings
        self.settings = defaults.copy()
        self.configure(duration=duration, eccentricity=eccentricity, t0=t0,
                       star_radius=star_radius, planet_radius=planet_radius,
                       orbital_period=orbital_period, semi_major_axis=semi_major_axis,
                       orbital_angle=orbital_angle, impact_parameter=impact_parameter,
                       noise=noise, sampling_cadence=sampling_cadence, threads=threads)

        self.active = True

    def close(self):
        """
        Clean up temporary working data.
        """

        self.active = False

    def configure(self,
                  duration=None,
                  eccentricity=None,
                  t0=None,
                  star_radius=None,
                  planet_radius=None,
                  orbital_period=None,
                  semi_major_axis=None,
                  orbital_angle=None,
                  impact_parameter=None,
                  noise=None,
                  sampling_cadence=None,
                  threads=None
                  ):
        """
        Change settings for synthesising lightcurves using PSLS
        """

        # Create dictionary of settings
        if duration is not None:
            self.settings['duration'] = float(duration)
        if eccentricity is not None:
            self.settings['eccentricity'] = float(eccentricity)
        if t0 is not None:
            self.settings['t0'] = float(t0)
        if star_radius is not None:
            self.settings['star_radius'] = float(star_radius)
        if planet_radius is not None:
            self.settings['planet_radius'] = float(planet_radius)
        if orbital_period is not None:
            self.settings['orbital_period'] = float(orbital_period)
        if semi_major_axis is not None:
            self.settings['semi_major_axis'] = float(semi_major_axis)
        if orbital_angle is not None:
            self.settings['orbital_angle'] = float(orbital_angle)
            self.settings['impact_parameter'] = None
        if impact_parameter is not None:
            self.settings['impact_parameter'] = float(impact_parameter)
            self.settings['orbital_angle'] = None
        if noise is not None:
            self.settings['noise'] = float(eval(str(noise)))
        if sampling_cadence is not None:
            self.settings['sampling_cadence'] = float(sampling_cadence)
        if threads is not None:
            self.settings['threads'] = int(threads)

    def synthesise(self):
        """
        Synthesise a lightcurve using Batman
        """

        # Create configuration for this run
        params = batman.TransitParams()

        # time of inferior conjunction (days)
        params.t0 = self.settings['t0']

        # orbital period (days)
        params.per = self.settings['orbital_period']

        # planet radius (in units of stellar radii)
        params.rp = self.settings['planet_radius'] / self.settings['star_radius']

        # semi-major axis (in units of stellar radii)
        params.a = self.settings['semi_major_axis'] * (phy_AU / jupiter_radius) / self.settings['star_radius']

        # orbital inclination (in degrees)
        if self.settings['impact_parameter'] is not None:
            orbital_angle = acos(self.settings['impact_parameter'] * self.settings['star_radius'] /
                                 (self.settings['semi_major_axis'] * (phy_AU / jupiter_radius))
                                 ) * 180 / pi
        else:
            orbital_angle = self.settings['orbital_angle']
        params.inc = 90 - orbital_angle

        # eccentricity
        params.ecc = self.settings['eccentricity']

        # longitude of periastron (in degrees)
        params.w = 90.

        # limb darkening coefficients [u1, u2]
        params.u = [0.1, 0.3]

        # limb darkening model
        params.limb_dark = "quadratic"

        # How many threads should we use?
        thread_count = self.settings['threads']
        if thread_count is None:
            thread_count = multiprocessing.cpu_count()
        thread_count = max(thread_count, 1)
        thread_count = min(thread_count, multiprocessing.cpu_count())

        # Create raster for output lightcurve
        time_step = self.settings['sampling_cadence']  # seconds
        raster_step = time_step / 86400  # days
        t = np.arange(0., self.settings['duration'], raster_step)

        # Synthesise lightcurve
        m = batman.TransitModel(params=params, t=t, nthreads=thread_count)  # initializes model
        flux = m.light_curve(params=params)  # calculates light curve
        errors = np.zeros_like(t)

        # Work out noise level per pixel
        noise_per_pixel = self.settings['noise'] * sqrt(25 / time_step)

        # Calculate multiple event statistic (MES) for this LC
        integrated_transit_power = np.sum(np.ones_like(flux) - flux)
        pixels_in_transit = np.count_nonzero(flux < 1)
        pixels_out_of_transit = len(flux) - pixels_in_transit
        if pixels_in_transit < 1:
            mes = 0
        elif noise_per_pixel<=0:
            mes = np.inf
        else:
            mes = integrated_transit_power / noise_per_pixel / sqrt(pixels_in_transit)

        # Add noise to lightcurve
        noise = np.random.normal(0, noise_per_pixel, size=len(flux))
        flux += noise

        # Output metadata
        output_metadata = {
            'integrated_transit_power': integrated_transit_power,
            'pixels_in_transit': pixels_in_transit,
            'pixels_out_of_transit': pixels_out_of_transit,
            'mes': mes
        }

        # Write Batman output into lightcurve archive
        lc = lightcurve.LightcurveArbitraryRaster(
            times=t,  # days
            fluxes=flux,
            uncertainties=errors,
            metadata={**self.settings, **output_metadata}
        )

        # Finished
        return lc
