#!/bin/bash

# Build the Docker containers that we use for running the PLATO WP36 pipeline. There is one master container which
# contains a standardised Python environment with the WP36 pipeline code, plus individual derived Docker containers
# for each transit-detection algorithm (TDA) to be tested.

# Make sure we're running in the right directory
cd "$(dirname "$0")"
cwd=`pwd`

# First build a copy of the base container in local Docker environment
cd ${cwd}/../docker_containers
docker build . --tag plato/eas:v1 2>&1 | tee docker_build.log

# Build containers within minikube environment
eval $(minikube -p minikube docker-env)

# Build top-level Docker container containing python requirements
cd ${cwd}/../docker_containers
docker build . --tag plato/eas:v1 2>&1 | tee docker_build.log

# Build Docker images for each transit-detection code
# cd ${cwd}/../docker_containers/testbed/tda_codes/bls_reference
# docker build . --tag plato/eas_bls_reference:v1 2>&1 | tee docker_build.log

# cd ${cwd}/../docker_containers/testbed/tda_codes/bls_kovacs
# docker build . --tag plato/eas_bls_kovacs:v1 2>&1 | tee docker_build.log

# cd ${cwd}/../docker_containers/testbed/tda_codes/dst_v26
# docker build . --tag plato/eas_dst_v26:v1 2>&1 | tee docker_build.log

# cd ${cwd}/../docker_containers/testbed/tda_codes/dst_v29
# docker build . --tag plato/eas_dst_v29:v1 2>&1 | tee docker_build.log

# cd ${cwd}/../docker_containers/testbed/tda_codes/qats
# docker build . --tag plato/eas_qats:v1 2>&1 | tee docker_build.log

# cd ${cwd}/../docker_containers/testbed/tda_codes/tls
# docker build . --tag plato/eas_tls:v1 2>&1 | tee docker_build.log

# Build a master Docker image containing all transit-detection codes
cd ${cwd}/../docker_containers/testbed/tda_codes
docker build . --tag plato/eas_all_tdas:v1 2>&1 | tee docker_build.log

