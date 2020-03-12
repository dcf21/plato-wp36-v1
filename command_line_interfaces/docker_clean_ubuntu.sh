#!/bin/bash

# Fire up a shell terminal in a clean Ubuntu Docker image, for testing purposes.

# Make sure we're running in the right directory
cd "$(dirname "$0")"
cwd=`pwd`

# Launch interactive shell using docker-compose
cd ${cwd}/..
docker run -it ubuntu
