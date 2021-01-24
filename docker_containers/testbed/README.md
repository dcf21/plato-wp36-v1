# PLATO EAS test bench code

This is the source code for the PLATO EAS test bench code.

The directory structure is as follows:

* `transit_search` -- The Python scripts used to measure the run time of transit detection codes.

* `python_modules` -- A helper module `plato_wp36` which contains utility functions used by the test bench. These include reading/writing light curves in text/FITS formats, and measuring the run time of operations. It also includes wrappers for each transit detection code, so that they can all be called via a common Python interface.

* `tda_codes` -- A collection of Dockerfiles which are used to build each transit detection code and integrate it with the test bench.

