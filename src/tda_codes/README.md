Here we store Dockerfiles which build each of the baseline transit detection
algorithms into separate Docker containers, based on a standard Ubuntu Linux
environment. The codes run in separate containers to eliminate any risk of
conflicting dependencies between them.

For diagnostic purposes, we additionally include a master Dockerfile in this
root directory, which builds all of the transit detection codes into a single
Docker container.

