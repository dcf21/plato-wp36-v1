#!/bin/bash

# Download and install QATS code
cd /plato_eas/datadir_local
mkdir qats
cd qats
wget https://faculty.washington.edu/agol/QATS/qats.tgz
tar xvfz qats.tgz
cd qats
make

# Write list of available TDAs
echo '["qats"]' > /plato_eas/docker_containers/tda_list.json
