# -*- coding: utf-8 -*-
# psls_wrapper.py

"""
Class for synthesising lightcurves using PSLS.
"""

import hashlib
import os
import random
import time
from math import acos, pi

import numpy as np
from eas_batman_wrapper.batman_wrapper import BatmanWrapper
from plato_wp36 import settings, lightcurve
from plato_wp36.constants import *

defaults = {
    'mode': 'main_sequence',
    'duration': 730,  # days
    'master_seed': time.time(),
    'datadir_input': settings.settings['inDataPath'],
    'enable_transits': True,
    'star_radius': sun_radius / jupiter_radius,  # Jupiter radii
    'planet_radius': 1,  # Jupiter radii
    'orbital_period': 365,  # days
    'semi_major_axis': 1,  # AU
    'orbital_angle': 0,  # degrees
    'impact_parameter': None,  # Impact parameter (0-1); overrides <orbital_angle> if not None
    'nsr': 73,  # noise-to-signal ratio (ppm/hr)
    'sampling_cadence': 25,  # sampling cadence, seconds
    'mask_updates': False,  # do we include mask updates?
    'enable_systematics': False  # do we include systematics?
}


class PslsWrapper:
    """
    Class for synthesising lightcurves using PSLS.
    """

    def __init__(self,
                 mode=None,
                 duration=None,
                 enable_transits=None,
                 star_radius=None,
                 planet_radius=None,
                 orbital_period=None,
                 semi_major_axis=None,
                 orbital_angle=None,
                 impact_parameter=None,
                 nsr=None,
                 sampling_cadence=None,
                 mask_updates=None,
                 enable_systematics=None
                 ):
        """
        Instantiate wrapper for synthesising lightcurves using PSLS
        """

        # Create dictionary of settings
        self.settings = defaults.copy()

        self.configure(mode=mode, duration=duration, enable_transits=enable_transits,
                       star_radius=star_radius, planet_radius=planet_radius,
                       orbital_period=orbital_period, semi_major_axis=semi_major_axis,
                       orbital_angle=orbital_angle, impact_parameter=impact_parameter,
                       nsr=nsr, sampling_cadence=sampling_cadence, mask_updates=mask_updates,
                       enable_systematics=enable_systematics)

        # Create temporary working directory
        identifier = "eas_psls"
        self.id_string = "eas_{:d}_{}".format(os.getpid(), identifier)
        self.tmp_dir = os.path.join("/tmp", self.id_string)
        os.system("mkdir -p {}".format(self.tmp_dir))
        self.active = True

    def close(self):
        """
        Clean up temporary working data.
        """

        # Remove temporary directory
        os.system("rm -Rf {}".format(self.tmp_dir))
        self.active = False

    def configure(self,
                  mode=None,
                  duration=None,
                  enable_transits=None,
                  star_radius=None,
                  planet_radius=None,
                  orbital_period=None,
                  semi_major_axis=None,
                  orbital_angle=None,
                  impact_parameter=None,
                  nsr=None,
                  sampling_cadence=None,
                  mask_updates=None,
                  enable_systematics=None
                  ):
        """
        Change settings for synthesising lightcurves using PSLS
        """

        # Create dictionary of settings
        if mode is not None:
            self.settings['mode'] = mode
        if duration is not None:
            self.settings['duration'] = float(eval(str(duration)))
        if enable_transits is not None:
            self.settings['enable_transits'] = int(eval(str(enable_transits)))
        if star_radius is not None:
            self.settings['star_radius'] = float(eval(str(star_radius)))
        if planet_radius is not None:
            self.settings['planet_radius'] = float(eval(str(planet_radius)))
        if orbital_period is not None:
            self.settings['orbital_period'] = float(eval(str(orbital_period)))
        if semi_major_axis is not None:
            self.settings['semi_major_axis'] = float(eval(str(semi_major_axis)))
        if orbital_angle is not None:
            self.settings['orbital_angle'] = float(eval(str(orbital_angle)))
            self.settings['impact_parameter'] = None
        if impact_parameter is not None:
            self.settings['impact_parameter'] = float(eval(str(impact_parameter)))
            self.settings['orbital_angle'] = None
        if nsr is not None:
            self.settings['nsr'] = float(eval(str(nsr)))
        if sampling_cadence is not None:
            self.settings['sampling_cadence'] = float(eval(str(sampling_cadence)))
        if mask_updates is not None:
            self.settings['mask_updates'] = int(eval(str(mask_updates)))
        if enable_systematics is not None:
            self.settings['enable_systematics'] = int(eval(str(enable_systematics)))

    def synthesise(self):
        """
        Synthesise a lightcurve using PSLS
        """

        # Switch into our temporary working directory where PSLS can find all its input files
        cwd = os.getcwd()
        os.chdir(self.tmp_dir)

        # Create unique ID for this run
        utc = time.time()
        key = "{}_{}".format(utc, random.random())
        tstr = time.strftime("%Y%m%d_%H%M%S", time.gmtime(utc))
        uid = hashlib.md5(key.encode()).hexdigest()
        run_identifier = "{}_{}".format(tstr, uid)[0:32]

        # Find template to use for PSLS configuration
        path_to_yaml_templates = os.path.split(os.path.abspath(__file__))[0]
        yaml_template_filename = os.path.join(path_to_yaml_templates, "{}_template.yaml".format(self.settings['mode']))

        assert os.path.exists(yaml_template_filename), \
            """Could not find PSLS template for mode <{}>. Recognised modes are "main_sequence" or "red_giant".\
               File <{}> does not exist.\
            """.format(self.settings['mode'], yaml_template_filename)

        # Make filename for YAML configuration file for PSLS
        yaml_template = open(yaml_template_filename).read()
        yaml_filename = "{}.yaml".format(run_identifier)

        # Work out inclination of orbit
        if self.settings['impact_parameter'] is not None:
            orbital_angle = acos(self.settings['impact_parameter'] * self.settings['star_radius'] /
                                 (self.settings['semi_major_axis'] * (phy_AU / jupiter_radius))
                                 ) * 180 / pi
        else:
            orbital_angle = self.settings['orbital_angle']

        # Work out which systematics file we are to use
        systematics_file = ("PLATO_systematics_BOL_V2.npy"
                            if self.settings['mask_updates'] else
                            "PLATO_systematics_BOL_FixedMask_V2.npy")

        enable_systematics = int(self.settings['enable_systematics'])

        # Create YAML configuration file for PSLS
        with open(yaml_filename, "w") as out:
            out.write(
                yaml_template.format(
                    duration=float(self.settings['duration']),
                    master_seed=int(self.settings['master_seed']),
                    nsr=float(self.settings['nsr']),
                    datadir_input=settings.settings['inDataPath'],
                    enable_transits=int(self.settings['enable_transits']),
                    planet_radius=float(self.settings['planet_radius']),
                    orbital_period=float(self.settings['orbital_period']),
                    semi_major_axis=float(self.settings['semi_major_axis']),
                    orbital_angle=float(orbital_angle),
                    sampling_cadence=float(self.settings['sampling_cadence']),
                    integration_time=float(self.settings['sampling_cadence']) * 22 / 25,
                    systematics=systematics_file,
                    enable_systematics=enable_systematics,
                    noise_type="PLATO_SIMU" if enable_systematics else "PLATO_SCALING"
                )
            )

        # Path to PSLS binary
        psls_binary = os.path.join(
            settings.settings['localDataPath'],
            "virtualenv/bin/psls.py"
        )

        # Run PSLS
        command = "{} {}".format(psls_binary, yaml_filename)
        os.system(command)

        # Filename of the output that PSLS produced
        psls_output = "0012069449"

        # Read output from PSLS
        psls_filename = "{}.dat".format(psls_output)
        data = np.loadtxt(psls_filename).T

        # Read times and fluxes from text file
        times = data[0]  # seconds
        fluxes = 1 + 1e-6 * data[1]
        flags = data[2]

        # Compute MES statistic
        if not self.settings['enable_transits']:
            integrated_transit_power = 0
            pixels_in_transit = 0
            pixels_out_of_transit = len(times)
            mes = 0
        else:
            batman_instance = BatmanWrapper(duration=self.settings['duration'],
                                            eccentricity=0,
                                            t0=0,
                                            star_radius=self.settings['star_radius'],
                                            planet_radius=self.settings['planet_radius'],
                                            orbital_period=self.settings['orbital_period'],
                                            semi_major_axis=self.settings['semi_major_axis'],
                                            orbital_angle=self.settings['orbital_angle'],
                                            impact_parameter=self.settings['impact_parameter'],
                                            noise=plato_noise,
                                            sampling_cadence=self.settings['sampling_cadence']
                )
            batman_lc = batman_instance.synthesise()
            integrated_transit_power = batman_lc.metadata['integrated_transit_power']
            pixels_in_transit = batman_lc.metadata['pixels_in_transit']
            pixels_out_of_transit = batman_lc.metadata['pixels_out_of_transit']
            mes = batman_lc.metadata['mes']

        output_metadata = {
            'integrated_transit_power': integrated_transit_power,
            'pixels_in_transit': pixels_in_transit,
            'pixels_out_of_transit': pixels_out_of_transit,
            'mes': mes
        }

        # Write Batman output into lightcurve archive
        lc = lightcurve.LightcurveArbitraryRaster(
            times=times / 86400,  # psls outputs seconds; we use days
            fluxes=fluxes,
            flags=flags,
            metadata={**self.settings, **output_metadata}
        )

        # Make sure there aren't any old data files lying around
        os.system("rm -Rf *.modes *.yaml *.dat")

        # Switch back into the user's cwd
        os.chdir(cwd)

        # Finished
        return lc
