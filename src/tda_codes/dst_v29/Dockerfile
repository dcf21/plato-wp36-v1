# Use standardised Python environment with EAS pipeline code
FROM plato/eas:v1

# Install DST version 26
WORKDIR /plato_eas/proprietary
RUN mkdir -p asalto29
RUN cd asalto29 ; tar xvfz ../asalto29.tgz

# Patch Juan's Makefiles into a working state
WORKDIR /plato_eas/proprietary/asalto29
COPY Makefile.asalto29.patch Makefile.patch
RUN cp Makefile Makefile.original
RUN patch Makefile < Makefile.patch

# Write list of available TDAs
RUN echo '["dst_v29"]' > /plato_eas/tda_list.json

# Default working directory
WORKDIR /plato_eas
