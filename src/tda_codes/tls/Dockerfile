# Use standardised Python environment with EAS pipeline code
FROM plato/eas:v1

# Install DFM's Python binding to Kovács et al. (2002)
WORKDIR /plato_eas
RUN git clone https://github.com/hippke/tls.git
WORKDIR /plato_eas/tls
RUN /plato_eas/virtualenv/bin/python setup.py install

# Default working directory
WORKDIR /plato_eas
