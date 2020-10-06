# DST (version 29)

This builds a Docker image containing version 29 (C++ code) of Détection Spécialisée de Transits (DST).

This code is not publicly available, and a tar file of the source code must be
placed in the `private_code` directory in the root of the pipeline
installation.

Furthermore, the distributed Makefiles need to be (substantially) modified to compile within a
standard Ubuntu Docker container, which is done using the patch files in this
directory.

### References

https://ui.adsabs.harvard.edu/abs/2012A%26A...548A..44C/abstract

