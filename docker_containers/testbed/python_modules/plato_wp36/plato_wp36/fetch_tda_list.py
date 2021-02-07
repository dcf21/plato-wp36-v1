# -*- coding: utf-8 -*-
# fetch_tda_list.py

"""
Module for fetching the list of transit detection algorithms available inside the current Docker
container
"""

import os
import json

from .settings import settings


def fetch_tda_list(tda_list_filename=None):
    """
    Read the contents of a JSON file in the root of the Docker container, which tells us which transit
    detection algorithms are available in this version of the container.

    :param tda_list_filename:
        The filename of the JSON file telling us which TDAs are available
    :type tda_list_filename:
        str
    :return:
        List of names of TDAs
    """

    # Default path for list of available TDAs
    if tda_list_filename is None:
        tda_list_filename = os.path.join(settings['pythonPath'], 'tda_list.json')

    with open(tda_list_filename) as in_stream:
        tda_list_json = in_stream.read()

    tda_list = json.loads(tda_list_json)

    return tda_list
