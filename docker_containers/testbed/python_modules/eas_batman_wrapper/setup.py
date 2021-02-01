#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from codecs import open
from os import path, system
from re import compile as re_compile

from setuptools import setup, find_packages

# For convenience
if sys.argv[-1] == "publish":
    system("python setup.py sdist upload")
    sys.exit()


def read(filename):
    kwds = {"encoding": "utf-8"} if sys.version_info[0] >= 3 else {}
    with open(filename, **kwds) as fp:
        contents = fp.read()
    return contents


# Get the version information
here = path.abspath(path.dirname(__file__))
vre = re_compile("__version__ = \"(.*?)\"")
version = vre.findall(read(path.join(here, "eas_batman_wrapper", "__init__.py")))[0]

# Python module properties
setup(
    name="eas_batman_wrapper",
    version=version,
    author="Dominic Ford",
    author_email="dcf21@dcford.org.uk",
    description="Helper functions for the PLATO WP36 EAS pipeline",
    long_description=read(path.join(here, "README.md")),
    url="https://dcford.org.uk/",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics"
    ],
    keywords="PLATO",
    packages=find_packages(exclude=["docs", "tests"]),
    install_requires=[],
    extras_require={
        "test": ["coverage"]
    },
    package_data={
        "": ["LICENSE"],
    },
    include_package_data=True,
    data_files=None
)
