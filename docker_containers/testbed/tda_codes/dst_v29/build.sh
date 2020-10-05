#!/bin/bash

# Install DST version 29
cd /plato_eas/private_code
mkdir -p asalto29
cd asalto29 ; tar xvfz ../asalto29.tgz

# Patch Juan's Makefiles into a working state
cd /plato_eas/private_code/asalto29
cp Makefile Makefile.original
patch Makefile < Makefile.patch

# Make asalto29
make -j 4

# Write list of available TDAs
echo '["dst_v29"]' > /plato_eas/tda_list.json
