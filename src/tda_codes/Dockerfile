# Use standardised Python environment with EAS pipeline code
FROM plato/eas:v1

# *** bls_reference
# No files need to be copied

# *** bls_vanilla
# No files need to be copied

# *** dst_v26

# Patch Juan's Makefiles into a working state
WORKDIR /plato_eas/proprietary/juan
COPY Makefile.juan.patch Makefile.patch

WORKDIR /plato_eas/proprietary/asalto26.5
COPY Makefile.asalto26.5.patch Makefile.patch

WORKDIR /plato_eas/proprietary/asalto27
COPY Makefile.asalto27.patch Makefile.patch

# *** dst_v29

# Patch Juan's Makefiles into a working state
WORKDIR /plato_eas/proprietary/asalto29
COPY Makefile.asalto29.patch Makefile.patch

# *** exotrans
# No files need to be copied

# *** qats
# No files need to be copied

# *** tls
# No files need to be copied

# Now build all transit detection codes in turn
COPY bls_reference/build.sh build.sh
RUN ./build.sh
COPY bls_vanilla/build.sh build.sh
RUN ./build.sh
COPY dst_v26/build.sh build.sh
RUN ./build.sh
COPY dst_v29/build.sh build.sh
RUN ./build.sh
COPY exotrans/build.sh build.sh
RUN ./build.sh
COPY qats/build.sh build.sh
RUN ./build.sh
COPY tls/build.sh build.sh
RUN ./build.sh

# *** Write list of available TDAs
RUN echo '["bls_reference","bls_vanilla","dst_v26","dst_v27","exotrans","qats","tls"]' > /plato_eas/tda_list.json

# Default working directory
WORKDIR /plato_eas
