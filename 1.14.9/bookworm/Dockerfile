FROM debian:bookworm-slim AS verify

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /verify

# github repository locations
ARG REPO_GITIAN_BUILDER=https://github.com/devrandom/gitian-builder.git
ARG REPO_GITIAN_SIGS=https://github.com/dogecoin/gitian.sigs.git
ARG REPO_DOGECOIN_CORE=https://github.com/dogecoin/dogecoin.git

# Specify release variables
ARG RLS_VERSION=1.14.9
ARG RLS_OS=linux
ARG RLS_LIB=gnu
ARG RLS_ARCH=

# pin known sha256sums
RUN    echo 6928c895a20d0bcb6d5c7dcec753d35c884a471aaf8ad4242a89a96acb4f2985  dogecoin-1.14.9-aarch64-linux-gnu.tar.gz > SHASUMS \
    && echo 311fe8aee346d3f9a00c0a8ac594224ca3bfa297fec8a5fae20bb70f28961421  dogecoin-1.14.9-arm-linux-gnueabihf.tar.gz >> SHASUMS \
    && echo b8e1846a0979f369042dcf14435dfcea704b1456e34bc9657f0829d9eac0d3b0  dogecoin-1.14.9-i686-pc-linux-gnu.tar.gz >> SHASUMS \
    && echo 4f227117b411a7c98622c970986e27bcfc3f547a72bef65e7d9e82989175d4f8  dogecoin-1.14.9-x86_64-linux-gnu.tar.gz >> SHASUMS

# static derived variables
ARG SIG_PATH=${RLS_VERSION}-${RLS_OS}
ARG DESCRIPTOR_PATH=dogecoin/contrib/gitian-descriptors/gitian-${RLS_OS}.yml
ARG RLS_LOCATION=https://github.com/dogecoin/dogecoin/releases/download/v${RLS_VERSION}

# Signature policy. By default the build FAILS if gverify finds no signer in
# the imported keyring whose assert matches the downloaded binary. Releases
# whose signers are not yet in contrib/gitian-keys can be built by setting
# ALLOW_UNTRUSTED_SIGNERS=1, which downgrades the missing-signer case to a
# warning. The pinned SHA256 check below is ALWAYS enforced regardless.
ARG ALLOW_UNTRUSTED_SIGNERS=0

# install system requirements
# hadolint ignore=DL3008
RUN apt-get update && apt-get install --no-install-recommends -y \
    wget \
    git \
    ruby \
    gpg \
    gpg-agent \
    && rm -rf /var/lib/apt/lists/*

# fetch tools and setup signers
RUN git clone --depth 1 "${REPO_GITIAN_BUILDER}" gitian \
    && git clone --depth 1 "${REPO_GITIAN_SIGS}" sigs \
    && git clone --depth 1 -b "v${RLS_VERSION}" "${REPO_DOGECOIN_CORE}" dogecoin \
    && find dogecoin/contrib/gitian-keys -name "*.pgp" -print0 | xargs -0 -n 1 gpg --import \
    && wget -qO- https://github.com/KunNw0n.gpg | gpg --import \
    && gpg --list-keys 7E453C9D37AC2EB246645C4B75055E4030051C37

# determine architecture, download release binary, then verify it against a
# trusted gitian signer (fail-closed unless ALLOW_UNTRUSTED_SIGNERS=1) and
# against the pinned sha256sums above
RUN set -ex && ARCHITECTURE=$(dpkg --print-architecture) \
    && if [ "${ARCHITECTURE}" = "amd64" ]; then RLS_ARCH=x86_64;    fi \
    && if [ "${ARCHITECTURE}" = "arm64" ]; then RLS_ARCH=aarch64;   fi \
    && if [ "${ARCHITECTURE}" = "armhf" ]; then RLS_ARCH=arm && RLS_LIB=gnueabihf; fi \
    && if [ "${ARCHITECTURE}" = "i386"  ]; then RLS_ARCH=i686-pc;   fi \
    && if [ "${RLS_ARCH}" = "" ]; then echo "Could not determine architecture" >&2; exit 1; fi \
    && RLS_FILE_NAME="dogecoin-${RLS_VERSION}-${RLS_ARCH}-${RLS_OS}-${RLS_LIB}.tar.gz" \
    && wget -q "${RLS_LOCATION}/${RLS_FILE_NAME}" \
    && gitian/bin/gverify --no-markup -d sigs -r "${SIG_PATH}" "${DESCRIPTOR_PATH}" \
       | grep OK | sed s/:.*// | sort -u > ok_signers.txt || true \
    && TRUSTED_SIGNER="" \
    && while read -r signer; do \
         [ -z "${signer}" ] && continue; \
         if grep -lq "${RLS_FILE_NAME}" "sigs/${SIG_PATH}/${signer}/"*assert 2>/dev/null; then \
           TRUSTED_SIGNER="${signer}"; break; \
         fi; \
       done < ok_signers.txt \
    && if [ -n "${TRUSTED_SIGNER}" ]; then \
         echo "Verifying against trusted signer: ${TRUSTED_SIGNER}"; \
         grep "${RLS_FILE_NAME}" "sigs/${SIG_PATH}/${TRUSTED_SIGNER}/"*assert | sha256sum -c; \
       elif [ "${ALLOW_UNTRUSTED_SIGNERS}" = "1" ]; then \
         echo "WARNING: no trusted signer for ${RLS_FILE_NAME} in keyring;" >&2; \
         echo "WARNING: proceeding on pinned SHA256 only (ALLOW_UNTRUSTED_SIGNERS=1)." >&2; \
       else \
         echo "ERROR: no trusted gitian signer found for ${RLS_FILE_NAME}." >&2; \
         echo "ERROR: import the release signer's key or set" >&2; \
         echo "ERROR: --build-arg ALLOW_UNTRUSTED_SIGNERS=1 to override." >&2; \
         exit 1; \
       fi \
    && grep "${RLS_FILE_NAME}" SHASUMS | sha256sum -c \
    && mv "${RLS_FILE_NAME}" dogecoin.tar.gz \
    && tar -xf dogecoin.tar.gz --strip-components=1


# Build rootlesskit as a fully static binary (CGO_ENABLED=0) from xanimo's fork.
# Enables optional user-namespace-based rootless execution inside the container,
# solving the host UID-mapping problem for bind-mounted volumes without root.
FROM golang:1.22-alpine AS rootlesskit

SHELL ["/bin/ash", "-o", "pipefail", "-c"]

# hadolint ignore=DL3018
RUN apk add --no-cache git make \
    && git clone --depth 1 https://github.com/xanimo/rootlesskit /src
WORKDIR /src
RUN CGO_ENABLED=0 make bin/rootlesskit


# Build minimal Debian-based rootfs; works on all Debian-supported arches
# including linux/386 (which ubuntu:22.04 dropped).
FROM debian:bookworm-slim AS installer

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG USER=dogecoin

WORKDIR /staging

# Install libstdc++6 (not in bookworm-slim), then copy exactly the files
# owned by each needed runtime package into /staging. Explicit package list
# avoids pulling in dpkg/tar/etc. via recursive dep resolution.
# cp -a preserves symlinks and arch-specific library paths.
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends libstdc++6 \
    && for pkg in \
         base-files \
         libc6 libgcc-s1 libstdc++6 \
         dash grep sed coreutils \
         libpcre2-8-0 libacl1 libattr1 libselinux1 libsigsegv2 libgmp10; \
       do \
         dpkg -L "$pkg" 2>/dev/null | grep -v '^\.$' \
           | while IFS= read -r f; do \
               if [ -d "$f" ] && [ ! -L "$f" ]; then \
                 mkdir -p "/staging$f"; \
               elif [ -e "$f" ]; then \
                 mkdir -p "/staging$(dirname "$f")"; \
                 cp -a "$f" "/staging$f"; \
               fi; \
             done; \
       done \
    && ln -sf dash /staging/usr/bin/sh \
    && rm -rf /var/lib/apt/lists/*

# Populate minimal /etc, create the dogecoin user's home + datadir,
# and regenerate the dynamic-linker cache for the chiselled rootfs.
# No setuid binary, no fixed-UID assumption beyond UID 1000:
# operators using Docker rootless / rootlesskit get full UID remapping.
RUN printf 'root:x:0:0:root:/root:/sbin/nologin\n%s:x:1000:1000::/%s:/sbin/nologin\n' \
        "${USER}" "${USER}" > /staging/etc/passwd \
    && printf 'root:x:0:\n%s:x:1000:\n' "${USER}" > /staging/etc/group \
    && printf 'hosts: files dns\n' > /staging/etc/nsswitch.conf \
    && mkdir -p "/staging/${USER}/.dogecoin" \
    && chown -R 1000:1000 "/staging/${USER}" \
    && printf 'include /etc/ld.so.conf.d/*.conf\n/lib\n/usr/lib\n' \
        > /staging/etc/ld.so.conf \
    && ldconfig -r /staging

# Install dogecoin binaries: owned by root, world-executable, no setuid bit.
# A process running as dogecoin:dogecoin cannot chmod or overwrite these files.
COPY --from=verify \
    /verify/bin/dogecoind \
    /verify/bin/dogecoin-cli \
    /verify/bin/dogecoin-tx \
    /staging/usr/local/bin/
RUN chmod 0755 /staging/usr/local/bin/dogecoin* \
    && chown root:root /staging/usr/local/bin/dogecoin*

# Include the static rootlesskit binary for operators who need user-namespace
# UID remapping (e.g. `docker run … rootlesskit dogecoind`).
COPY --from=rootlesskit /src/bin/rootlesskit /staging/usr/local/bin/rootlesskit
RUN chmod 0755 /staging/usr/local/bin/rootlesskit \
    && chown root:root /staging/usr/local/bin/rootlesskit

# Install the shell entrypoint (replaces Python; no extra runtime dep).
COPY entrypoint.sh /staging/usr/local/bin/entrypoint.sh
RUN chmod 0755 /staging/usr/local/bin/entrypoint.sh \
    && chown root:root /staging/usr/local/bin/entrypoint.sh


# Minimal scratch-based final image — no OS layer, no package manager,
# no shell outside /bin/sh, no root user.
FROM scratch

COPY --from=installer /staging/ /

# P2P network (mainnet, testnet & regtest respectively)
EXPOSE 22556 44556 18444

# RPC interface (mainnet, testnet & regtest respectively)
EXPOSE 22555 44555 18332

VOLUME ["/dogecoin/.dogecoin"]

# Run exclusively as the dogecoin user — root is never needed at runtime.
USER 1000:1000
WORKDIR /dogecoin

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["dogecoind"]
