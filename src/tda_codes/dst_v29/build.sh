#!/bin/bash

# Install DST version 29
cd /plato_eas/proprietary
mkdir -p asalto29
cd asalto29 ; tar xvfz ../asalto29.tgz

# Patch Juan's Makefiles into a working state
cd /plato_eas/proprietary/asalto29
cp Makefile Makefile.original
patch Makefile < Makefile.patch

# Write list of available TDAs
echo '["dst_v29"]' > /plato_eas/tda_list.json
