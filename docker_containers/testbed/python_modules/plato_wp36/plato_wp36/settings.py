# -*- coding: utf-8 -*-
# settings.py

"""
Compile the settings to be used for this installation of the EAS pipeline code. We merge default values for each
setting below with local overrides which can be placed in the YAML file
<configuration_local/installation_settings.conf>.
"""

import os
import re
import sys

# Fetch path to local installation settings file
our_path = os.path.abspath(__file__)
root_path = re.match(r"(.*/docker_containers/)", our_path).group(1)
if not os.path.exists(os.path.join(root_path, "docker_containers/configuration_local/installation_settings.conf")):
    sys.stderr.write(
        "You must create a file <configuration_local/installation_settings.conf> with local settings.\n")
    sys.exit(1)

# Read the local installation information from <configuration_local/installation_settings.conf>
installation_info = {}
for line in open(os.path.join(root_path, "docker_containers/configuration_local/installation_settings.conf")):
    line = line.strip()

    # Ignore blank lines and comment lines
    if len(line) == 0 or line[0] == '#':
        continue

    # Remove any comments from the ends of lines
    if '#' in line:
        line = line.split('#')[0]

    # Split this configuration parameter into the setting name, and the setting value
    words = line.split(':')
    value = words[1].strip()

    # Try and convert the value of this setting to a float
    try:
        value = float(value)
    except ValueError:
        pass

    installation_info[words[0].strip()] = value

# The path to the <datadir> directory which is shared between Docker containers, used to store both input and output
# data from the pipeline
data_directory = os.path.join(root_path, "../datadir_output")

# The path to the directory which contains input lightcurves
lc_directory = os.path.join(root_path, "../datadir_input")

# The path to the directory which contains input data such as PSLS's frequency data
input_directory = os.path.join(root_path, "../datadir_input")

# The default settings are below
settings = {
    'softwareVersion': 1,

    # The path to python scripts in the src directory
    'pythonPath': root_path,

    # The directory where we can store persistent data
    'dataPath': data_directory,

    # The directory where we expect to find input data
    'inDataPath': input_directory,

    # The directory where we expect to find lightcurves to work on
    'lcPath': lc_directory,

    # Flag specifying whether to produce debugging output from C code
    'debug': installation_info['debug'],
}

# If the <datadir> directory isn't mounted properly, then things will be badly wrong, as the Docker container can't
# access persistent data volume.
assert os.path.exists(settings['dataPath']), """
You need to create a directories or symlinks <datadir_input> and <datadir_output> in the root of your working
copy of the pipeline, where we store all persistent data.
"""
