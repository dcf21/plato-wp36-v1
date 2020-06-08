#!/bin/bash

# Delete all the cached images that Docker accumulates.

# Make sure we're running in the right directory
cd "$(dirname "$0")"
cwd=`pwd`

# Build containers within minikube environment
eval $(minikube -p minikube docker-env)

# Build top-level Docker container containing python requirements
cd ${cwd}/..
docker system prune -f
docker rmi $(docker images -a -q)

