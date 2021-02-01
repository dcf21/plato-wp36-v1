# -*- coding: utf-8 -*-
# psls_wrapper.py

"""
Class for synthesising lightcurves using PSLS.
"""

import hashlib
import os
import random
import time

from plato_wp36 import settings

defaults = {
    'mode': 'main_sequence',
    'duration': 730,  # days
    'master_seed': time.time(),
    'datadir_input': settings.settings['inDataPath'],
    'enable_transit': True,
    'planet_radius': 1,  # Jupiter radii
    'orbital_period': 365,  # days
    'semi_major_axis': 1,  # AU
    'orbital_angle': 0  # degrees
}


class PslsWrapper:
    """
    Class for synthesising lightcurves using PSLS.
    """

    def __init__(self,
                 mode=None,
                 duration=None,
                 enable_transit=None,
                 planet_radius=None,
                 orbital_period=None,
                 semi_major_axis=None,
                 orbital_angle=None):
        """
        Instantiate wrapper for synthesising lightcurves using PSLS
        """

        # Create dictionary of settings
        self.settings = defaults.copy()
        if mode is not None:
            self.settings['mode'] = mode
        if duration is not None:
            self.settings['duration'] = duration
        if enable_transit is not None:
            self.settings['enable_transit'] = enable_transit
        if planet_radius is not None:
            self.settings['planet_radius'] = planet_radius
        if orbital_period is not None:
            self.settings['orbital_period'] = orbital_period
        if semi_major_axis is not None:
            self.settings['semi_major_axis'] = semi_major_axis
        if orbital_period is not None:
            self.settings['orbital_angle'] = orbital_angle

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
                  enable_transit=None,
                  planet_radius=None,
                  orbital_period=None,
                  semi_major_axis=None,
                  orbital_angle=None):
        """
        Change settings for synthesising lightcurves using PSLS
        """

        # Create dictionary of settings
        if mode is not None:
            self.settings['mode'] = mode
        if duration is not None:
            self.settings['duration'] = duration
        if enable_transit is not None:
            self.settings['enable_transit'] = enable_transit
        if planet_radius is not None:
            self.settings['planet_radius'] = planet_radius
        if orbital_period is not None:
            self.settings['orbital_period'] = orbital_period
        if semi_major_axis is not None:
            self.settings['semi_major_axis'] = semi_major_axis
        if orbital_period is not None:
            self.settings['orbital_angle'] = orbital_angle

    def synthesise(self, filename, gzipped=True, directory="psls_output"):
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

        # Create YAML configuration file for PSLS
        yaml_template = open(yaml_template_filename).read()
        yaml_filename = "{}.yaml".format(run_identifier)
        with open(yaml_filename, "w") as out:
            out.write(
                yaml_template.format(
                    duration=float(self.settings['duration']),
                    master_seed=int(self.settings['master_seed']),
                    datadir_input=settings.settings['inDataPath'],
                    enable_transit=int(self.settings['enable_transit']),
                    planet_radius=float(self.settings['planet_radius']),
                    orbital_period=float(self.settings['orbital_period']),
                    semi_major_axis=float(self.settings['semi_major_axis']),
                    orbital_angle=float(self.settings['orbital_angle'])
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
        elephant

        # Target path for this lightcurve
        target_path = os.path.join(settings.settings['lcPath'], directory, filename)

        # Copy PSLS output into lightcurve archive

        # Make sure there aren't any old data files lying around
        os.system("rm -Rf *.dat *.yaml")

        # Switch back into the user's cwd
        os.chdir(cwd)

        # Finished
        return
