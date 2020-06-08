# Use standardised Python environment with EAS pipeline code
FROM plato/eas:v1

# Install the Transit Least Squares code
WORKDIR /plato_eas
RUN git clone https://github.com/hippke/tls.git
WORKDIR /plato_eas/tls
RUN /plato_eas/datadir_local/virtualenv/bin/python setup.py install

# Write list of available TDAs
RUN echo '["tls"]' > /plato_eas/tda_list.json

# Default working directory
WORKDIR /plato_eas
