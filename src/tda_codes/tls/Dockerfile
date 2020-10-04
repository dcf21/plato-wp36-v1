# Use standardised Python environment with EAS pipeline code
FROM plato/eas:v1

# Default working directory
WORKDIR /plato_eas

# Build code
COPY build.sh build.sh
RUN ./build.sh
