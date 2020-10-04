#!/bin/bash

# Install FORTRAN compiler
apt-get update ; apt-get install -y gfortran ; apt-get clean

# Install DFM's Python binding to Kovács et al. (2002)
cd /plato_eas
git clone https://github.com/dfm/python-bls.git
cd /plato_eas/python-bls
/plato_eas/datadir_local/virtualenv/bin/python setup.py install

# Write list of available TDAs
echo '["bls_kovacs"]' > /plato_eas/tda_list.json
