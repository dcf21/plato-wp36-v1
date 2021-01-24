#!/bin/bash

# Install the Transit Least Squares code
cd /plato_eas/datadir_local
git clone https://github.com/hippke/tls.git
cd tls
/plato_eas/datadir_local/virtualenv/bin/python setup.py install

# Write list of available TDAs
echo '["tls"]' > /plato_eas/docker_containers/tda_list.json
