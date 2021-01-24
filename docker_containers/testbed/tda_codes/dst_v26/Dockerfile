# Use standardised Python environment with EAS pipeline code
FROM plato/eas:v1

# Default working directory
WORKDIR /plato_eas/docker_containers/testbed

# Patch Juan's Makefiles into a working state
WORKDIR /plato_eas/docker_containers/private_code/juan
COPY Makefile.juan.patch Makefile.patch

WORKDIR /plato_eas/docker_containers/private_code/asalto26.5
COPY Makefile.asalto26.5.patch Makefile.patch

WORKDIR /plato_eas/docker_containers/private_code/asalto27
COPY Makefile.asalto27.patch Makefile.patch

# Default working directory
WORKDIR /plato_eas/docker_containers/testbed

# Build code
COPY build.sh build.sh
RUN ./build.sh
