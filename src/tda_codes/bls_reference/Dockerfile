# Use standardised Python environment with EAS pipeline code
FROM plato/eas:v1

# Install DFM's optimised Python implementation of BLS
WORKDIR /plato_eas
RUN git clone https://github.com/dfm/bls.py.git
WORKDIR /plato_eas/bls.py
RUN /plato_eas/virtualenv/bin/python setup.py install

# Write list of available TDAs
RUN echo '["bls_reference"]' > /plato_eas/tda_list.json

# Default working directory
WORKDIR /plato_eas
