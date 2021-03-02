# Building Docker containers

The scripts in this directory are used to build Docker containers for each transit-detection code. Each Docker container is based on a minimal Ubuntu Linux image, and contains a built/compiled version of one transit-detection code, plus the test-bench code used to run that algorithm.

For diagnostic purposes, an additional Docker container `plato/eas_all_tdas:v1` is produced which contains all the transit-detection codes in a single container.

The scripts are as follows:

* `docker_clear_cache.sh` -- Clear any cached Docker images from your local repository. This is useful before initiating a clean build.

* `docker_build.sh` -- Build all the Docker containers for each of the transit-detection codes.

* `docker_shell.sh` -- For diagnostic purposes, start the Docker container `plato/eas_all_tdas:v1` and yield a bash prompt. This is useful for manually running codes.

Additional diagnostic scripts are:

* `docker_clean_ubuntu.sh` -- Start a Docker container with a clean Ubuntu environment, and yield a bash prompt. Useful for diagnosing any build errors.

* `ubuntu_build.sh` -- Build all the transit codes natively on a Ubuntu Linux machine, not within a Docker container. Note that the build scripts explicitly assume a Ubuntu Linux environment.

