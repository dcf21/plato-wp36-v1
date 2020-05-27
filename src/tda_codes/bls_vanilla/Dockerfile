# Use standardised Python environment with EAS pipeline code
FROM plato/eas:v1

# Install FORTRAN compiler
RUN apt-get update ; apt-get install -y gfortran ; apt-get clean

# Install DFM's Python binding to Kovács et al. (2002)
WORKDIR /plato_eas
RUN git clone https://github.com/dfm/python-bls.git
WORKDIR /plato_eas/python-bls
RUN /plato_eas/datadir_local/virtualenv/bin/python setup.py install

# Write list of available TDAs
RUN echo '["bls_vanilla"]' > /plato_eas/tda_list.json

# Default working directory
WORKDIR /plato_eas
