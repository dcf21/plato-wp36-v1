#!/bin/bash

# Build the Docker containers that we use for running the PLATO WP36 pipeline. There is one master container which
# contains a standardised Python environment with the WP36 pipeline code, plus individual derived Docker containers
# for each transit detection algorithm (TDA) to be tested.

# Make sure we're running in the right directory
cd "$(dirname "$0")"
cwd=`pwd`

# Build top-level Docker container containing python requirements
cd ${cwd}/..
docker-compose build 2>&1 | tee docker_build.log

# Build Docker images for each transit detection code
cd ${cwd}/../src/tda_codes/bls_vanilla
docker-compose build 2>&1 | tee docker_build.log

cd ${cwd}/../src/tda_codes/bls_reference
docker-compose build 2>&1 | tee docker_build.log

cd ${cwd}/../src/tda_codes/tls
docker-compose build 2>&1 | tee docker_build.log

