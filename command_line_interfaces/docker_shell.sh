#!/bin/bash

# Open a shell terminal in the Docker image containing an installation of the WP36 pipeline code in a standardised
# Python 3.6 environment.

# Make sure we're running in the right directory
cd "$(dirname "$0")"
cwd=`pwd`

# Launch interactive shell using docker-compose
cd ${cwd}/..
docker-compose run plato_eas /bin/bash
