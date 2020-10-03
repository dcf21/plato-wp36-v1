# Use standardised Python environment with EAS pipeline code
FROM plato/eas:v1

# Install DST version 26
WORKDIR /plato_eas/proprietary
RUN mkdir -p asalto26.5
RUN cd asalto26.5 ; tar xvfz ../asalto26.5.tar.gz
RUN mkdir -p asalto27
RUN cd asalto27 ; tar xvfz ../asalto27.tar.gz
RUN mkdir -p juan
RUN cd juan ; tar xvfz ../juan.tar.gz

# Patch Juan's Makefiles into a working state
WORKDIR /plato_eas/proprietary/juan
COPY Makefile.juan.patch Makefile.patch
RUN cp Makefile Makefile.original
RUN patch Makefile < Makefile.patch

WORKDIR /plato_eas/proprietary/asalto26.5
COPY Makefile.asalto26.5.patch Makefile.patch
RUN cp Makefile Makefile.original
RUN patch Makefile < Makefile.patch

# Build Juan's code: libjuan
RUN make

# Write list of available TDAs
RUN echo '["dst_v26"]' > /plato_eas/tda_list.json

# Default working directory
WORKDIR /plato_eas
