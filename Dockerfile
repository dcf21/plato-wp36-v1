# Use Python 3.6 running on Debian Buster
FROM python:3.6-buster

# Install sqlite3
RUN apt-get update ; apt-get install -y apt-utils python-virtualenv python-sqlite sqlite3 ; apt-get clean

# Install Python requirements
WORKDIR /plato_eas
ADD requirements.txt requirements.txt

# We use a virtual environment, because this means it's easy to run code outside of Docker for testing
RUN mkdir -p datadir_local
RUN virtualenv -p python3 datadir_local/virtualenv
RUN /plato_eas/datadir_local/virtualenv/bin/pip install -r requirements.txt

# Copy PLATO EAS code into Docker container
WORKDIR /plato_eas
ADD configuration_local configuration_local
ADD src src

# Install plato_wp36 module
WORKDIR /plato_eas/src/python_modules/plato_wp36/
RUN /plato_eas/datadir_local/virtualenv/bin/python setup.py develop

# Write list of available TDAs
RUN echo '[]' > /plato_eas/tda_list.json

# Default working directory
WORKDIR /plato_eas
