FROM debian:bullseye-slim

# To improve : static hash make dynamic build of versions impossible.
ARG VERSION=1.14.5
ARG TARGETPLATFORM
ARG BUILDPLATFORM

ENV USER=dogecoin
ENV DATADIR=/${USER}/.dogecoin

# Root configuration to mimic user
ENV HOME=/${USER}

# Dependencies install
RUN useradd ${USER} --home-dir ${HOME}

RUN DEBIAN_FRONTEND=noninteractive \
    && apt-get update \
    && apt-get install -y man python3 wget \
    && rm -rf /var/lib/apt/lists/* /tmp/*

# Download Dogecoin Core from github releases,
# manage binary architecture using buildx & TARGETPLATFORM.
WORKDIR /tmp

RUN set -ex \
  && if [ "${TARGETPLATFORM}" = "linux/amd64" ]; then export TARGETPLATFORM=x86_64-linux-gnu; fi \
  && if [ "${TARGETPLATFORM}" = "linux/arm64" ]; then export TARGETPLATFORM=aarch64-linux-gnu; fi \
  && if [ "${TARGETPLATFORM}" = "linux/arm/v7" ]; then export TARGETPLATFORM=arm-linux-gnueabihf; fi \
    && wget https://github.com/dogecoin/dogecoin/releases/download/v${VERSION}/dogecoin-${VERSION}-$TARGETPLATFORM.tar.gz

# Move downloaded binaries and man pages in the container system.
# Setuid on binaries with $USER rights, to prevent
# root right with `docker exec`.
RUN tar -xvf dogecoin-${VERSION}-*.tar.gz --strip-components=1 && \
    cp share/man/man1/*.1 /usr/share/man/man1 && \
    cp bin/dogecoin* /usr/local/bin && \
    chown ${USER}:${USER} /usr/local/bin/dogecoin* && \
    chmod 4555 /usr/local/bin/dogecoin* && \
    rm -rf /tmp/* /var/tmp/*

COPY --chmod=500 docker-entrypoint.py /usr/local/bin/docker-entrypoint

WORKDIR ${HOME}

# P2P network (mainnet, testnet & regnet respectively)
EXPOSE 22556 44556 18444

# RPC interface (mainnet, testnet & regnet respectively)
EXPOSE 22555 44555 18332

VOLUME ["/dogecoin/.dogecoin"]

ENTRYPOINT ["docker-entrypoint"]
