# -*- coding: utf-8 -*-
# batman_wrapper.py

"""
Class for synthesising lightcurves using Batman.
"""

import gzip
import os

import batman
import numpy as np
from plato_wp36 import settings

sun_radius = 695500e3  # metres
earth_radius = 6371e3  # metres
jupiter_radius = 71492e3  # metres

defaults = {
    'duration': 730,  # days
    't0': 1,  # Time for inferior conjunction (days)
    'eccentricity': 0,
    'star_radius': sun_radius / jupiter_radius,  # Jupiter radii
    'planet_radius': 1,  # Jupiter radii
    'orbital_period': 365,  # days
    'semi_major_axis': 1,  # AU
    'orbital_angle': 0  # degrees
}


class BatmanWrapper:
    """
    Class for synthesising lightcurves using Batman.
    """

    def __init__(self,
                 duration=None,
                 eccentricity=None,
                 t0=None,
                 planet_radius=None,
                 orbital_period=None,
                 semi_major_axis=None,
                 orbital_angle=None):
        """
        Instantiate wrapper for synthesising lightcurves using Batman
        """

        # Create dictionary of settings
        self.settings = defaults.copy()
        if duration is not None:
            self.settings['duration'] = duration
        if eccentricity is not None:
            self.settings['eccentricity'] = eccentricity
        if t0 is not None:
            self.settings['t0'] = t0
        if planet_radius is not None:
            self.settings['planet_radius'] = planet_radius
        if orbital_period is not None:
            self.settings['orbital_period'] = orbital_period
        if semi_major_axis is not None:
            self.settings['semi_major_axis'] = semi_major_axis
        if orbital_period is not None:
            self.settings['orbital_angle'] = orbital_angle

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
                  planet_radius=None,
                  orbital_period=None,
                  semi_major_axis=None,
                  orbital_angle=None):
        """
        Change settings for synthesising lightcurves using PSLS
        """

        # Create dictionary of settings
        if duration is not None:
            self.settings['duration'] = duration
        if eccentricity is not None:
            self.settings['eccentricity'] = eccentricity
        if t0 is not None:
            self.settings['t0'] = t0
        if planet_radius is not None:
            self.settings['planet_radius'] = planet_radius
        if orbital_period is not None:
            self.settings['orbital_period'] = orbital_period
        if semi_major_axis is not None:
            self.settings['semi_major_axis'] = semi_major_axis
        if orbital_period is not None:
            self.settings['orbital_angle'] = orbital_angle

    def synthesise(self, filename, gzipped=True, directory="batman_output"):
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
        params.a = self.settings['semi_major_axis'] / self.settings['star_radius']

        # orbital inclination (in degrees)
        params.inc = 90 - self.settings['orbital_angle']

        # eccentricity
        params.ecc = self.settings['eccentricity']

        # longitude of periastron (in degrees)
        params.w = 90.

        # limb darkening coefficients [u1, u2]
        params.u = [0.1, 0.3]

        # limb darkening model
        params.limb_dark = "quadratic"

        # Create raster for output lightcurve
        time_step = 25  # seconds
        raster_step = time_step / 86400  # days
        t = np.arange(0., self.settings['duration'], raster_step)

        # Synthesise lightcurve
        m = batman.TransitModel(params, t)  # initializes model
        flux = m.light_curve(params)  # calculates light curve
        errors = np.zeros_like(t)

        # Target path for this lightcurve
        target_path = os.path.join(settings.settings['lcPath'], directory, filename)

        # Write Batman output into lightcurve archive
        if not gzipped:
            opener = open
        else:
            opener = gzip.open

        with opener(target_path, "w") as out:
            np.savetxt(out, np.transpose([t * 86400, flux, errors]))

        # Finished
        return
