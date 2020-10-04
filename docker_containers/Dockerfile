# Use a Ubuntu base image
FROM ubuntu:latest

# Install various useful Ubuntu packages
RUN apt-get update
RUN apt-get install -y apt-utils dialog git vim net-tools wget rsync \
                       python3 python3-dev python3-virtualenv python3-mysqldb \
                       mysql-client libmysqlclient-dev make gcc g++ gfortran \
                       libcfitsio-dev libgsl-dev \
                       ; apt-get clean

# Install Python requirements
WORKDIR /plato_eas
ADD requirements.txt requirements.txt

# We use a virtual environment, because this means it's easy to run code outside of Docker for testing
RUN mkdir -p datadir_local
RUN virtualenv -p python3 datadir_local/virtualenv
RUN /plato_eas/datadir_local/virtualenv/bin/pip install numpy  # Required by batman installer
RUN /plato_eas/datadir_local/virtualenv/bin/pip install -r requirements.txt

# Copy PLATO EAS code into Docker container
WORKDIR /plato_eas
ADD configuration_local configuration_local
ADD src src

# Copy non open-source transit-detection codes into this Docker container
ADD proprietary proprietary

# Install plato_wp36 module
WORKDIR /plato_eas/src/python_modules/plato_wp36/
RUN /plato_eas/datadir_local/virtualenv/bin/python setup.py develop

# Write list of available TDAs
RUN echo '[]' > /plato_eas/tda_list.json

# Default working directory
WORKDIR /plato_eas
