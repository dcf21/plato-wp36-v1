#!/usr/bin/python3
# -*- coding: utf-8 -*-
# dataFetch.py

"""
Automatically download all of the required data files from the internet.
"""

import logging
import os
import sys


def fetch_file(web_address, destination, force_refresh=False):
    """
    Download a file that we need, using wget.

    :param web_address:
        The URL that we should use to fetch the file
    :type web_address:
        str
    :param destination:
        The path we should download the file to
    :type destination:
        str
    :param force_refresh:
        Boolean flag indicating whether we should download a new copy if the file already exists.
    :type force_refresh:
        bool
    :return:
        Boolean flag indicating whether the file was downloaded. Raises IOError if the download fails.
    """
    logging.info("Fetching file <{}>".format(destination))

    # Check if the file already exists
    if os.path.exists(destination):
        if not force_refresh:
            logging.info("File already exists. Not downloading fresh copy.")
            return False
        else:
            logging.info("File already exists, but downloading fresh copy.")
            os.unlink(destination)

    # Fetch the file with wget
    os.system("wget -q '{}' -O {}".format(web_address, destination))

    # Check that the file now exists
    if not os.path.exists(destination):
        raise IOError("Could not download file <{}>".format(web_address))

    return True


def fetch_required_files():
    # List of the files we require
    required_files = [
        {
            'url': 'https://sites.lesia.obspm.fr/psls/files/2017/11/m0y27l.tar_.gz',
            'destination': 'datadir_input/m0y27l.tar_.gz',
            'force_refresh': False
        },
        {
            'url': 'https://sites.lesia.obspm.fr/psls/files/2017/11/m0y24h.tar_.gz',
            'destination': 'datadir_input/m0y24h.tar_.gz',
            'force_refresh': False
        },
        {
            'url': 'https://files.pythonhosted.org/packages/09/16/1657adaa7444e1ce1884baf25e6fb3333d809ef2dc1a82cf8b3d9fdbe4c5/psls-1.3.tar.gz',
            'destination': 'datadir_input/psls-1.3.tar.gz',
            'force_refresh': False
        }
    ]

    # Fetch all the files
    for required_file in required_files:
        fetch_file(web_address=required_file['url'],
                   destination=required_file['destination'],
                   force_refresh=required_file['force_refresh']
                   )

    # Unzip PSLS data files
    os.system("""
mkdir -p datadir_input/psls_data
cd datadir_input/psls_data
tar zxf ../psls-1.3.tar.gz
""")

    # Unzip the PSLS star frequency models
    os.system("""
mkdir -p datadir_input/psls_models
cd datadir_input/psls_models
tar zxf ../m0y24h.tar_.gz
tar zxf ../m0y27l.tar_.gz
""")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        stream=sys.stdout,
                        format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')
    logger = logging.getLogger(__name__)
    logger.info(__doc__.strip())

    fetch_required_files()
