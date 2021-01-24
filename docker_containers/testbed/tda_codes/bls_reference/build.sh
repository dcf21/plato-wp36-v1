#!/bin/bash

# Install DFM's optimised Python implementation of BLS
# https://github.com/dfm/bls.py
# This is already integrated into astropy

# Write list of available TDAs
echo '["bls_reference"]' > /plato_eas/docker_containers/tda_list.json
