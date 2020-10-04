#!/bin/bash

# Install the Transit Least Squares code
cd /plato_eas
git clone https://github.com/hippke/tls.git
cd /plato_eas/tls
/plato_eas/datadir_local/virtualenv/bin/python setup.py install

# Write list of available TDAs
echo '["tls"]' > /plato_eas/tda_list.json
