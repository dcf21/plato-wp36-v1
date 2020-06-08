#!/bin/bash

# Build the Docker containers that we use for running the PLATO WP36 pipeline. There is one master container which
# contains a standardised Python environment with the WP36 pipeline code, plus individual derived Docker containers
# for each transit detection algorithm (TDA) to be tested.

# Make sure we're running in the right directory
cd "$(dirname "$0")"
cwd=`pwd`

# Build containers within minikube environment
eval $(minikube -p minikube docker-env)

# Build top-level Docker container containing python requirements
cd ${cwd}/..
docker build . --tag plato/eas:v1 2>&1 | tee docker_build.log

# Build Docker images for each transit detection code
cd ${cwd}/../src/tda_codes/bls_vanilla
docker build . --tag plato/eas_bls_vanilla:v1 2>&1 | tee docker_build.log

cd ${cwd}/../src/tda_codes/bls_reference
docker build . --tag plato/eas_bls_reference:v1 2>&1 | tee docker_build.log

cd ${cwd}/../src/tda_codes/tls
docker build . --tag plato/eas_tls:v1 2>&1 | tee docker_build.log

cd ${cwd}/../src/tda_codes/all_tdas
docker build . --tag plato/eas_all_tdas:v1 2>&1 | tee docker_build.log

