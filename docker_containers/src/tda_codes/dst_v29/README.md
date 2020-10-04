This builds a Docker image containing version 29 (C++ code) of DST.

This code is not publicly available, and a tar file of the source code must be placed in the `proprietary` directory in the root of the pipeline installation.

Furthermore, the distributed Makefiles need to be modified to compile within a standard Ubuntu Docker container, which is done using the patch files in this directory. 

https://ui.adsabs.harvard.edu/abs/2012A%26A...548A..44C/abstract

