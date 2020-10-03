# Use standardised Python environment with EAS pipeline code
FROM plato/eas:v1

# Install FORTRAN compiler
RUN apt-get update ; apt-get install -y gfortran ; apt-get clean

# bls_reference
# Install DFM's optimised Python implementation of BLS
# https://github.com/dfm/bls.py
# This is already integrated into astropy

# bls_vanilla
# Install DFM's Python binding to Kovács et al. (2002)
WORKDIR /plato_eas
RUN git clone https://github.com/dfm/python-bls.git
WORKDIR /plato_eas/python-bls
RUN /plato_eas/datadir_local/virtualenv/bin/python setup.py install

# dst_v26

# tls
# Install the Transit Least Squares code
WORKDIR /plato_eas
RUN git clone https://github.com/hippke/tls.git
WORKDIR /plato_eas/tls
RUN /plato_eas/datadir_local/virtualenv/bin/python setup.py install

# Write list of available TDAs
RUN echo '["bls_reference","bls_vanilla","dst_v26","dst_v27","exotrans","qats","tls"]' > /plato_eas/tda_list.json

# Default working directory
WORKDIR /plato_eas
