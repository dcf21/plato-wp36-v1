# DST (version 26)

This builds a Docker image containing version 26 (C code) of DST.

This code is not publicly available, and a tar file of the source code must be
placed in the `private_code` directory in the root of the pipeline
installation.

The distributed Makefiles need to be (substantially) modified to compile within a
standard Ubuntu Docker container, which is done using the patch files in this
directory.

### References

https://ui.adsabs.harvard.edu/abs/2012A%26A...548A..44C/abstract

