# Use standardised Python environment with EAS pipeline code
FROM plato/eas:v1

# Patch Juan's Makefiles into a working state
WORKDIR /plato_eas/docker_containers/private_code/asalto29
COPY Makefile.asalto29.patch Makefile.patch

# Default working directory
WORKDIR /plato_eas/docker_containers/testbed

# Build code
COPY build.sh build.sh
RUN ./build.sh
