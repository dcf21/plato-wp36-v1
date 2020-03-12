#!/bin/bash

# Build a Python virtual environment containing all the dependencies for running the PLATO WP36 pipeline code. This
# is useful for diagnostic purposes, when trying to run the code natively on Ubuntu systems (without using Docker).

# Make sure we're running in the right directory
cd "$(dirname "$0")"
cwd=`pwd`

virtualenv -p python3 virtualenv
virtualenv/bin/pip install -r requirements.txt
