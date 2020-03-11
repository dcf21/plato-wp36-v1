#!/bin/bash

# Make sure we're running in the right directory
cd "$(dirname "$0")"
cwd=`pwd`

# Build top-level Docker container containing python requirements
cd ${cwd}/..
docker-compose build
