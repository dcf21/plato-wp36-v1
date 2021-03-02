# PLATO EAS baseline algorithm test-bench

The EAS baseline algorithm test-bench is a framework for evaluating candidate transit-detection algorithms for use on PLATO data.

It allows us to generate simulated lightcurves using synthesis packages including PSLS and Batman, and to test the ability of transit-detection codes to recover the injected transits. All operations are timed, allowing us to estimate the computation requirements of EAS.

The test-bench also serves as a prototype for many of the parallel-computing technologies that have been proposed for use within EAS. We run the test-bench in a scaleable cluster environment using Docker, Kubernetes and RabbitMQ.

### Building the code

The test-bench is designed to run in Docker containers within a Kubernetes environment, though it is also possible to run it natively under Ubuntu Linux.

Instructions on how to deploy the pipeline can be found in the `kubernetes` directory. The easiest way to create a Kubernetes environment on a single machine is to install the `minikube` package.

Alternatively, the script `build_docker_containers/ubuntu_build.sh` will build the pipeline for use natively within a Ubuntu Linux environment.

### Usage overview

The following tasks can be performed by the test-bench, and sequenced together to build more complex tests:

* Synthesising lightcurves with PSLS.
* Synthesising lightcurves with Batman.
* Injecting white noise into lightcurves.
* Importing lightcurves from external sources, including the light-curve stitching group (LCSG) or from the WP38 PLATO-DB prototype.
* Multiplying lightcurves together to inject transits.
* Searching for transits with a range of transit-detection codes, including: BLS, TLS, QATS, (DST and EXOTRANS).
* Lightcurve diagnostics - verifying that lightcurves are readable.
* Success test - checking whether a transit search returned the expected result.

All of these tasks are specified via JSON descriptions, and can be requested without writing any code. For example, a request to synthesise a lightcurve for the Earth using PSLS would look as follows:

```
{
    "task": ”psls_synthesise",
    "lc_directory": ”my_output",
    "lc_filename": "earth.lc",
    "lc_specs":
        "duration": 730,
        "planet_radius": 0.089114866,
        "orbital_period": 365,
        "semi_major_axis": 1
    }
}
```

More complex tests can easily be built in very few lines of code, by sequencing operations together and introducing iterations over quantities which are to be varied.

For example, the following task description simulates 30 different model planets in a 4-day period around their host stars. The planets have a range of radii which are logathmically spaced between 0.04 and 0.2 Jupiter radii. The lightcurves for each are synthesised using PSLS, and then passed to TLS.

A pass/fail outcome is recorded, indicating whether TLS recovered the period of the input planet. Currently, this simply tests whether the period of the planet is recovered to within 3%.

Running on our Iris cluster in Cambridge (6 nodes), this entire process completes in around 50 minutes.

```
{
    "test_name": “vary_planet_size",
    "iterations": [
    {
        "name": "size",
        "log_range": [0.04, 0.2, 30]
    }],
    "task_list": [[{
        "task": “psls_synthesise”,
        "lc_filename": “my_test_${index}.gz",
        "lc_specs": {
            "duration": 90,
            "planet_radius": "${size}",
            "orbital_period": 4,
            "semi_major_axis": 0.05
        }},  {
            "task": "transit_search",
            "lc_duration": 90,
            "tda_name": "tls",
            "lc_filename": “my_test_${index}.gz"
        }]}
```

### Directory structure

* `docker_containers` -- The code used to build and run the test-bench inside a Docker container. This also contains all the code needed to build each transit-detection code.

* `build_docker_containers` - Scripts which automatically build the Docker containers containing the test-bench and each transit-detection code.

* `kubernetes` -- Scripts used to deploy the test-bench within a Kubernetes cluster.

* `datadir_input` -- Storage for the light curves used as input to the test-bench.

* `datadir_output` -- Storage for results output from the test-bench.

### List of transit-detection codes

The following transit-detection codes are currently supported by the test-bench:

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
