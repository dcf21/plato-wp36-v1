# plato-wp36

This code is used to evaluate the performance of candidate transit detection algorithms (TDAs) which might be used
in the PLATO WP36 Exoplanet Analysis System (EAS). It also serves as a prototype for the pipeline architecture which the
EAS may use: using Docker and Kubernetes to run transit detection codes on large clusters of machines in heterogeneous
environments.

The code in this repository can read lightcurve data from a variety of data formats, pass it to a variety of transit
detection algorithms (TDAs), time how long the processing takes, and store the results to a database.

This allows the performance of each transit detection code to be evaluated, both in terms of computation requirements
and scientific performance.

### Building the code

For maximum cross-platform flexibility, this code is designed to run in a Docker container. One master Docker image is
made which contains a standardised Python 3.6 installation, and a built version of the pipeline code. Additional Docker
images are then built for each individual transit detection code. Each code runs in its own Docker environment, built
with all of the specific dependencies of that specific code.

To start, run the script `command_line_interfaces/docker_build.sh`.

Once the Docker container images are built, you can start a shell terminal inside the container by running
`command_line_interfaces/docker_shell.sh`.

We use `docker-compose` to mount the directory `datadir` within each Docker container in a read/write mode, allowing
results to be stored.

### Directory structure

* `src` - All the Python source code for the WP36 algorithm test environment.

* `configuration_local` - Local settings for this instance of the code. For example, debugging levels.

* `datadir` - Inside the Docker container, this must be an externally mounted volume where we can store input and output
data in a persistent manner.

---

### Author

This code is developed and maintained by Dominic Ford, at the Institute of Astronomy, Cambridge.