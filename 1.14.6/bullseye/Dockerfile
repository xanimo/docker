FROM debian:bullseye-slim AS verify

WORKDIR /verify

# github repository locations
ARG REPO_GITIAN_BUILDER=https://github.com/devrandom/gitian-builder.git
ARG REPO_GITIAN_SIGS=https://github.com/dogecoin/gitian.sigs.git
ARG REPO_DOGECOIN_CORE=https://github.com/dogecoin/dogecoin.git

# Specify release variables
ARG RLS_VERSION=1.14.6
ARG RLS_OS=linux
ARG RLS_LIB=gnu
ARG RLS_ARCH=

# static derived variables
ARG SIG_PATH=${RLS_VERSION}-${RLS_OS}
ARG DESCRIPTOR_PATH=dogecoin/contrib/gitian-descriptors/gitian-${RLS_OS}.yml
ARG RLS_LOCATION=https://github.com/dogecoin/dogecoin/releases/download/v${RLS_VERSION}

# install system requirements
RUN apt-get update && apt-get install --no-install-recommends -y \
    wget \
    git \
    ruby \
    gpg \
    gpg-agent \
    && rm -rf /var/lib/apt/lists/*

# fetch tools and setup signers
RUN bash -o pipefail \
    && git clone --depth 1 ${REPO_GITIAN_BUILDER} gitian \
    && git clone --depth 1 ${REPO_GITIAN_SIGS} sigs \
    && git clone --depth 1 -b v${RLS_VERSION} ${REPO_DOGECOIN_CORE} dogecoin \
    && find dogecoin/contrib/gitian-keys -name "*.pgp" |xargs -n 1 gpg --import

# determine architecture, download release binary
# and verify against random OK signer and pinned shasums
RUN set -ex && ARCHITECTURE=$(dpkg --print-architecture) \
    && if [ "${ARCHITECTURE}" = "amd64" ]; then RLS_ARCH=x86_64 ; fi \
    && if [ "${ARCHITECTURE}" = "arm64" ]; then RLS_ARCH=aarch64; fi \
    && if [ "${ARCHITECTURE}" = "armhf" ]; then RLS_ARCH=arm && RLS_LIB=gnueabihf; fi \
    && if [ "${ARCHITECTURE}" = "i386" ]; then RLS_ARCH=i686-pc; fi \
    && if [ "${RLS_ARCH}" = "" ]; then echo "Could not determine architecture" >&2; exit 1; fi \
    && RLS_FILE_NAME=dogecoin-${RLS_VERSION}-${RLS_ARCH}-${RLS_OS}-${RLS_LIB}.tar.gz \
    && wget ${RLS_LOCATION}/${RLS_FILE_NAME} \
    && wget ${RLS_LOCATION}/SHA256SUMS.asc \
    && gitian/bin/gverify --no-markup -d sigs -r ${SIG_PATH} ${DESCRIPTOR_PATH} \
       | grep OK | shuf -n 1 | sed s/:.*// > random_signer.txt \
    && grep ${RLS_FILE_NAME} sigs/${SIG_PATH}/$(cat random_signer.txt)/*assert | sha256sum -c \
    && grep ${RLS_FILE_NAME} SHA256SUMS.asc | sha256sum -c \
    && tar -zxvf ${RLS_FILE_NAME} \
        dogecoin-${RLS_VERSION}/bin/dogecoind \
        dogecoin-${RLS_VERSION}/bin/dogecoin-cli \
        dogecoin-${RLS_VERSION}/bin/dogecoin-tx \
        --strip-components=1

COPY entrypoint.py /entrypoint.py

FROM debian:bullseye-slim AS final

ARG USER=
ENV USER=${USER:-"dogecoin"}
ARG APP_UID=
ENV APP_UID=${APP_UID}
ARG APP_GID=
ENV APP_GID=${APP_GID}
ENV DATADIR=/home/${USER}/.dogecoin

# RUN echo ${USER} ${APP_UID} ${APP_GID} && exit 1

RUN groupadd -g ${APP_GID} ${USER} \
    && useradd -m --uid ${APP_UID} ${USER} -g ${APP_GID} \
    && mkdir -p ${DATADIR} \
    && chgrp -R ${APP_GID} ${DATADIR} \
    && chown -R "${APP_UID}:${APP_GID}" ${DATADIR} \
    && chmod -R 1007 ${DATADIR}

WORKDIR /home/${USER}

# Copy the downloaded binaries into the container system from the verify stage.
COPY --from=verify \
    /verify/bin/dogecoind \
    /verify/bin/dogecoin-cli \
    /verify/bin/dogecoin-tx /usr/local/bin/

COPY /entrypoint.py /usr/local/bin/

# Set permissions on copied files
RUN chmod g+x /usr/local/bin/*

# P2P network (mainnet, testnet & regnet respectively)
EXPOSE 22556 44556 18444

# RPC interface (mainnet, testnet & regnet respectively)
EXPOSE 22555 44555 18332

VOLUME ["${DATADIR}"]

# Dependencies install
RUN apt-get update && apt-get install --no-install-recommends -y \
    python3 \
    && rm -rf /var/lib/apt/lists/*

USER "${APP_UID}:${APP_GID}"

ENTRYPOINT ["entrypoint.py"]

CMD ["dogecoind", "-reindex"]
