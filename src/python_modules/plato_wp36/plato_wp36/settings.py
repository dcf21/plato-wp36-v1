# -*- coding: utf-8 -*-
# settings.py

import os
import re
import sys

# Fetch path to local installation settings
our_path = os.path.abspath(__file__)
root_path = re.match(r"(.*/src/)", our_path).group(1)
if not os.path.exists(os.path.join(root_path, "../configuration_local/installation_settings.conf")):
    sys.stderr.write(
        "You must create a file <configuration_local/installation_settings.conf> with local settings.\n")
    sys.exit(1)

# Read the local installation information from <configuration_local/installation_settings.conf>
installation_info = {}
for line in open(os.path.join(root_path, "../configuration_local/installation_settings.conf")):
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

# The settings below control how the observatory controller works
data_directory = os.path.join(root_path, "../datadir")

settings = {
    'softwareVersion': 1,

    # The path to python scripts in the src directory
    'pythonPath': root_path,

    # The directory where we expect to find images and video files
    'dataPath': data_directory,

    # Flag specifying whether to produce debugging output from C code
    'debug': installation_info['debug'],
}

assert os.path.exists(settings['dataPath']), """
You need to create a directory or symlink <datadir> in the root of your working
copy of the pipeline, where we store all recorded data.
"""
