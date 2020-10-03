#!/bin/bash

# Open a shell terminal in the Docker image containing an installation of the WP36 pipeline code in a standardised
# Python 3.6 environment.

# Make sure we're running in the right directory
cd "$(dirname "$0")"
cwd=`pwd`

# Build containers within minikube environment
eval $(minikube -p minikube docker-env)

# Launch interactive shell using docker-compose
cd ${cwd}/..
docker run -it plato/eas_dst_v26:v1 /bin/bash
