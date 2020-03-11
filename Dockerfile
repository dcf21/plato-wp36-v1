# Use Python 3.6 running on Debian Buster
FROM python:3.6-buster

# Install sqlite3
RUN apt-get update ; apt-get install -y apt-utils python-virtualenv python-sqlite sqlite3 ; apt-get clean

# Install Python requirements
WORKDIR /plato_eas
ADD requirements.txt requirements.txt

# We use a virtual environment, because this means it's easy to run code outside of Docker for testing
RUN virtualenv -p python3 virtualenv
RUN /plato_eas/virtualenv/bin/pip install -r requirements.txt

# Copy PLATO EAS code into Docker container
WORKDIR /plato_eas
ADD configuration_local configuration_local
ADD src src

# Install plato_wp36 module
WORKDIR /plato_eas/src/python_modules/plato_wp36/
RUN /plato_eas/virtualenv/bin/python setup.py develop

# Default working directory
WORKDIR /plato_eas