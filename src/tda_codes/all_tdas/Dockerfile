# Use standardised Python environment with EAS pipeline code
FROM plato/eas:v1

# Install FORTRAN compiler
RUN apt-get update ; apt-get install -y gfortran ; apt-get clean

# bls_reference
# Install DFM's optimised Python implementation of BLS
# https://github.com/dfm/bls.py
# This is already integrated into astropy

# *** bls_vanilla
# Install DFM's Python binding to Kovács et al. (2002)
WORKDIR /plato_eas
RUN git clone https://github.com/dfm/python-bls.git
WORKDIR /plato_eas/python-bls
RUN /plato_eas/datadir_local/virtualenv/bin/python setup.py install

# *** dst_v26
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

WORKDIR /plato_eas/proprietary/asalto27
COPY Makefile.asalto27.patch Makefile.patch
RUN cp Makefile Makefile.original
RUN patch Makefile < Makefile.patch

# Build Juan's code: libjuan
WORKDIR /plato_eas/proprietary/juan
RUN make

# *** dst_v29
WORKDIR /plato_eas/proprietary
RUN mkdir -p asalto29
RUN cd asalto29 ; tar xvfz ../asalto29.tgz

# Patch Juan's Makefiles into a working state
WORKDIR /plato_eas/proprietary/asalto29
COPY Makefile.asalto29.patch Makefile.patch
RUN cp Makefile Makefile.original
RUN patch Makefile < Makefile.patch

# *** exotrans

# *** qats
WORKDIR /plato_eas
RUN mkdir qats
WORKDIR qats
RUN wget https://faculty.washington.edu/agol/QATS/qats.tgz
RUN tar xvfz qats.tgz
WORKDIR qats
RUN make

# *** tls
WORKDIR /plato_eas
RUN git clone https://github.com/hippke/tls.git
WORKDIR /plato_eas/tls
RUN /plato_eas/datadir_local/virtualenv/bin/python setup.py install

# *** Write list of available TDAs
RUN echo '["bls_reference","bls_vanilla","dst_v26","dst_v27","exotrans","qats","tls"]' > /plato_eas/tda_list.json

# Default working directory
WORKDIR /plato_eas
