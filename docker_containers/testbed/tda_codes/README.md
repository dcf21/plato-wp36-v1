# Transit detection code collection

This directory contains a collection of Dockerfiles which build transit
detection codes into Docker containers. Each code has a subdirectory,
containing a Dockerfile which makes the container for running that code. Each
subdirectory also has a shell script which builds / installs the code.

All of these Docker images are derived from the core `plato/eas:v1` image which
contains the test bench code.

Ideally the codes should be run in separate containers to eliminate any risk of
conflicts between them.  However, for diagnostic purposes, we additionally
include a master Dockerfile in this root directory, which builds all of the
transit detection codes into a single Docker container.

