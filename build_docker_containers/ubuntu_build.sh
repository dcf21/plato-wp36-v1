#!/bin/bash

# Build a Python virtual environment containing all the dependencies for
# running the PLATO WP36 pipeline code. This is useful for diagnostic purposes,
# when trying to run the code natively on Ubuntu systems (without using
# Docker).

# Make sure we're running in the right directory
cd "$(dirname "$0")"
cwd=`pwd`

# Create virtual environment
datadir=${cwd}/../docker_containers/datadir_local
mkdir -p ${datadir}
venv_dir=${datadir}/virtualenv
rm -Rf ${venv_dir}
virtualenv -p python3 ${venv_dir}

# Install required python libraries
${venv_dir}/bin/pip install numpy
${venv_dir}/bin/pip install -r ${cwd}/../docker_containers/requirements.txt

# Install plato_wp36 package
cd ${cwd}/../src/python_modules/plato_wp36/
${venv_dir}/bin/python setup.py develop

# Install bls_reference code

# Install bls_kovacs code
cd ${cwd}
rm -Rf ${datadir}/tda_build/bls_kovacs
mkdir -p ${datadir}/tda_build/bls_kovacs
cd ${datadir}/tda_build/bls_kovacs
git clone https://github.com/dfm/python-bls.git
cd python-bls
${venv_dir}/bin/python setup.py install

# Install TLS code
cd ${cwd}
rm -Rf ${datadir}/tda_build/tls
mkdir -p ${datadir}/tda_build/tls
cd ${datadir}/tda_build/tls
git clone https://github.com/hippke/tls.git
cd tls
${venv_dir}/bin/python setup.py install

