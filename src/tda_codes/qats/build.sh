#!/bin/bash

# Download and install QATS code
cd /plato_eas
mkdir qats
cd qats
wget https://faculty.washington.edu/agol/QATS/qats.tgz
tar xvfz qats.tgz
cd qats
make

# Write list of available TDAs
echo '["qats"]' > /plato_eas/tda_list.json
