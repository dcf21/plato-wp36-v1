# -*- coding: utf-8 -*-
# batman_wrapper.py

"""
Class for synthesising lightcurves using Batman.
"""

import hashlib
import os
import random
import time

from plato_wp36 import settings

defaults = {
    'duration': 730,  # days
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

        # Create unique ID for this run
        utc = time.time()
        key = "{}_{}".format(utc, random.random())
        tstr = time.strftime("%Y%m%d_%H%M%S", time.gmtime(utc))
        uid = hashlib.md5(key.encode()).hexdigest()
        run_identifier = "{}_{}".format(tstr, uid)[0:32]


        # Target path for this lightcurve
        target_path = os.path.join(settings.settings['lcPath'], directory, filename)

        # Write Batman output into lightcurve archive

        # Finished
        return
