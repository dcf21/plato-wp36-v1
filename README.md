# PLATO EAS baseline algorithm test bench

This code is used to evaluate the performance of transit detection algorithms (TDAs) which might be used
in the PLATO Exoplanet Analysis System (EAS). It also prototypes the pipeline architecture which the
EAS may use: using Kubernetes to deploy transit detection codes on large clusters of machines, where they run within Docker containers.

The code in this repository can read lightcurve data from a variety of data formats, pass it to a variety of transit
detection algorithms (TDAs), time how long the processing takes, and store the results to a database.

This allows the performance of each transit detection code to be evaluated, both in terms of computation requirements
and scientific performance.

### Building the code

The test bench is designed to run in Docker containers within a Kubernetes environment.

Instructions on how to deploy the pipeline can be found in the `kubernetes` directory.

The easiest way to create a Kubernetes environment on a single machine is to install the minikube package.

### Directory structure

* `docker_containers` -- The code used to build and run the test bench inside a Docker container. This also contains all the code needed to build each transit detection code.

* `build_docker_containers` - Scripts which automatically build the Docker containers containing the test bench and each transit detection code.

* `kubernetes` -- Scripts used to deploy the test bench within a Kubernetes cluster.

* `datadir_input` -- Storage for the light curves used as input to the test bench.

* `datadir_output` -- Storage for results output from the test bench.

### List of algorithms

The following transit detection algorithms are currently supported by the test bench:

* **BLS** - Boxed Least Squares.

    Two implementations are supported: the [original FORTRAN implementation](https://github.com/dfm/python-bls) of [Kovacs et al. (2002)](https://ui.adsabs.harvard.edu/abs/2002A%26A...391..369K/abstract), and an [optimised Python implementation](https://github.com/dfm/bls.py) by Dan Forman-Mackey.

* **DST** - Détection Spécialisée de Transits ([Cabrera et al. 2018](https://ui.adsabs.harvard.edu/abs/2012A%26A...548A..44C/abstract))

    This code is not publicly available, and must be obtained from teh author as a tar archive, which is placed in the `private_code` directory.

    Two implementations are supported: versions 26 (C) and version 29 (C++).
    
* **EXOTRANS** ([Grziwa et al. 2012](https://ui.adsabs.harvard.edu/abs/2012MNRAS.420.1045G/abstract))

    This code is not publicly available, and must be obtained from the author. We are awaiting permission from the authors to use it within PLATO.
    
* **QATS** - Quasiperiodic Automated Transit Search ([Carter & Agol 2018](https://ui.adsabs.harvard.edu/abs/2013ApJ...765..132C/abstract))

    This code is publicly available from [Eric Agol's website](https://faculty.washington.edu/agol/QATS/).

* **TLS** - Transit Least Squares ([Hippke & Heller 2019](https://ui.adsabs.harvard.edu/abs/2019A%26A...623A..39H/abstract))

    This code is publicly available from [GitHub](https://github.com/hippke/tls)
    
---

### Author

This code is developed and maintained by Dominic Ford, at the Institute of Astronomy, Cambridge.
