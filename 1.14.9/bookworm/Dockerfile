FROM debian:bookworm-slim AS verify

WORKDIR /verify

# github repository locations
ARG REPO_DOGECOIN_CORE=https://github.com/dogecoin/dogecoin.git

# Specify release variables
ARG RLS_VERSION=1.14.9
ARG RLS_OS=linux
ARG RLS_LIB=gnu
ARG RLS_ARCH=

# Fingerprint of the key that signed this release's SHA256SUMS, pinned so a
# signature from any other key in the keyring is rejected. The key is shipped
# in contrib/gitian-keys at the release tag.
ARG RLS_SIGNER=DC6EF4A8BF9F1B1E4DE1EE522D3A345B98D0DC1F

# configure the shell before the first RUN
SHELL ["/bin/bash", "-ex", "-o", "pipefail", "-c"]

# pin known sha256sums, checked independently of the signed manifest so that
# swapping both the release asset and its signature is still not enough
RUN    echo 6928c895a20d0bcb6d5c7dcec753d35c884a471aaf8ad4242a89a96acb4f2985  dogecoin-1.14.9-aarch64-linux-gnu.tar.gz > SHASUMS \
    && echo 311fe8aee346d3f9a00c0a8ac594224ca3bfa297fec8a5fae20bb70f28961421  dogecoin-1.14.9-arm-linux-gnueabihf.tar.gz >> SHASUMS \
    && echo b8e1846a0979f369042dcf14435dfcea704b1456e34bc9657f0829d9eac0d3b0  dogecoin-1.14.9-i686-pc-linux-gnu.tar.gz >> SHASUMS \
    && echo 4f227117b411a7c98622c970986e27bcfc3f547a72bef65e7d9e82989175d4f8  dogecoin-1.14.9-x86_64-linux-gnu.tar.gz >> SHASUMS

# static derived variables
ARG RLS_LOCATION=https://github.com/dogecoin/dogecoin/releases/download/v${RLS_VERSION}

# install system requirements
# Versions are deliberately unpinned: Debian rotates point releases out of
# the archive, so a pin turns a security update into a build failure.
# hadolint ignore=DL3008
RUN apt-get update && apt-get install --no-install-recommends -y \
    wget \
    git \
    gpg \
    gpg-agent \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# import the maintainer keyring as published at the release tag
RUN git clone --depth 1 -b v${RLS_VERSION} ${REPO_DOGECOIN_CORE} dogecoin \
    && find dogecoin/contrib/gitian-keys -name "*.pgp" -exec gpg --import {} +

# Determine architecture, download the release binary, and verify it against
# the maintainer-signed manifest and against our own pinned sums.
#
# Unlike 1.14.5 this does not verify via gitian.sigs: no signer of
# 1.14.9-linux has a key in contrib/gitian-keys, so every signature there
# resolves to BAD SIGNATURE and there is nothing to select a random signer
# from. The release SHA256SUMS is signed directly by a maintainer key that
# is in the keyring, which is a stronger claim than a random third-party
# rebuild anyway. See the linked issue about restoring gitian coverage.
RUN ARCHITECTURE=$(dpkg --print-architecture) \
    && if [ "${ARCHITECTURE}" = "amd64" ]; then RLS_ARCH=x86_64 ; fi \
    && if [ "${ARCHITECTURE}" = "arm64" ]; then RLS_ARCH=aarch64; fi \
    && if [ "${ARCHITECTURE}" = "armhf" ]; then RLS_ARCH=arm && RLS_LIB=gnueabihf; fi \
    && if [ "${ARCHITECTURE}" = "i386" ]; then RLS_ARCH=i686-pc; fi \
    && if [ "${RLS_ARCH}" = "" ]; then echo "Could not determine architecture" >&2; exit 1; fi \
    && RLS_FILE_NAME="dogecoin-${RLS_VERSION}-${RLS_ARCH}-${RLS_OS}-${RLS_LIB}.tar.gz" \
    && wget -q "${RLS_LOCATION}/SHA256SUMS.asc" \
    && wget -q "${RLS_LOCATION}/${RLS_FILE_NAME}" \
    && gpg --status-fd 1 --output SHA256SUMS --decrypt SHA256SUMS.asc \
       | grep -q "^\[GNUPG:\] VALIDSIG ${RLS_SIGNER} " \
    && grep "${RLS_FILE_NAME}" SHA256SUMS | sha256sum -c \
    && grep "${RLS_FILE_NAME}" SHASUMS | sha256sum -c \
    && mv "${RLS_FILE_NAME}" dogecoin.tar.gz

FROM debian:bookworm-slim AS final

ENV USER=dogecoin
ENV DATADIR=/${USER}/.dogecoin

# Root configuration to mimic user
ENV HOME=/${USER}

# Pin the uid. An unpinned useradd takes whatever is free, so a base image
# change would silently move ownership of bind-mounted wallet files.
RUN useradd ${USER} --uid 1000 --user-group --home-dir ${HOME}

WORKDIR /tmp

# Copy the downloaded binary from the verify stage
COPY --from=verify /verify/dogecoin.tar.gz ./

# Install the binaries root-owned and not setuid, so the unprivileged
# runtime user can neither replace them nor escalate through them.
RUN tar -xvf dogecoin.tar.gz --strip-components=1 \
    && cp bin/dogecoind bin/dogecoin-cli bin/dogecoin-tx /usr/local/bin/ \
    && chown root:root /usr/local/bin/dogecoin* \
    && chmod 0555 /usr/local/bin/dogecoin* \
    && rm -rf -- *

# Group-own the home and datadir by root(0) and grant group write, so an
# operator overriding the uid (--user 1001:0) keeps write access.
RUN mkdir -p ${DATADIR} \
    && chown -R 1000:0 ${HOME} \
    && chmod -R g+rwX ${HOME}

WORKDIR ${HOME}

# P2P network (mainnet, testnet & regnet respectively)
EXPOSE 22556 44556 18444

# RPC interface (mainnet, testnet & regnet respectively)
EXPOSE 22555 44555 18332

VOLUME ["/dogecoin/.dogecoin"]

# Dependencies install
# hadolint ignore=DL3008
RUN apt-get update && apt-get install --no-install-recommends -y \
    python3 \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.py /usr/local/bin/entrypoint.py
# World-readable and executable: the entrypoint now runs as the
# unprivileged user, so a root-only mode would make the image unstartable.
RUN chmod 0555 /usr/local/bin/entrypoint.py

# Numeric, so that runAsNonRoot admission can verify it without running
# the image. Never root at runtime.
USER 1000:1000

ENTRYPOINT ["entrypoint.py"]
CMD ["dogecoind"]
