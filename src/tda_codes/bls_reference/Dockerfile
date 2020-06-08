# Use standardised Python environment with EAS pipeline code
FROM plato/eas:v1

# Install DFM's optimised Python implementation of BLS
# https://github.com/dfm/bls.py
# This is already integrated into astropy

# Write list of available TDAs
RUN echo '["bls_reference"]' > /plato_eas/tda_list.json

# Default working directory
WORKDIR /plato_eas
