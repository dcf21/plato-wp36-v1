# Use standardised Python environment with EAS pipeline code
FROM plato/eas:v1

# Download and install QATS code
WORKDIR /plato_eas
RUN mkdir qats
WORKDIR qats
RUN wget https://faculty.washington.edu/agol/QATS/qats.tgz
RUN tar xvfz qats.tgz
WORKDIR qats
RUN make

# Write list of available TDAs
RUN echo '["qats"]' > /plato_eas/tda_list.json

# Default working directory
WORKDIR /plato_eas
