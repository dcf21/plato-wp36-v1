# PLATO EAS test-bench code

This directory contains the source code for the PLATO EAS test-bench. This directory is the root directory of the code hierarchy which is copied into the Docker containers in which the test-bench runs.

The directory structure is as follows:

* `transit_search` -- The high-level Python scripts used to control the test-bench (under `master_node`), and to run the processing nodes (under `worker_node`).

* `python_modules` -- Python modules which contain most of the code of the test-bench. These modules are as follows:

  * `plato_wp36` -- utility functions used by the test-bench. These include reading/writing light curves in text/FITS formats, and measuring the run time of operations. It also includes wrappers for each transit-detection code, so that they can all be called via a common Python interface.

  * `eas_batman_wrapper` -- A Python wrapper for Batman, allowing transit signals to be synthesized with a homogenoeous interface by both Batman and PSLS.
    
  * `eas_psls_wrapper` -- A Python wrapper for PSLS, allowing transit signals to be synthesized with a homogenoeous interface by both Batman and PSLS.

* `tda_codes` -- A collection of Dockerfiles which are used to build each transit-detection code and integrate it with the test-bench.

