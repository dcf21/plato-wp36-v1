# Docker containers

This directory contains the test-bench code, plus all the scripts needed to build / install various transit-detection codes. It contains a Dockerfile which copies all these files into a Docker container where the codes can be built and run.

The directory structure is as follows:

* `testbed` -- All the code comprising the algorithm test bed, including scripts for building all the transit-detection codes.

* `private_code` -- This directory should be populated with tar archives containing non-public transit-detection codes. If this is not done, then these codes cannot be run.

* `configuration_local` -- Test-bench settings.

* `Dockerfile`

	Build the Dockerfile in this directory to create a base Docker image containing the test-bench. Then go into the directory `testbed/tda_codes` to build derived Docker images in which specific transit-detection codes are integrated into the test-bench.

	This process is automated by the script `../build_docker_containers/docker_build.sh`.

