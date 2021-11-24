#!/bin/sh

export DOCKER_BUILDKIT=1
docker build --platform=local -o . git://github.com/docker/buildx
mkdir -p ~/.docker/cli-plugins
mv buildx ~/.docker/cli-plugins/docker-buildx
docker buildx --help
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
ls /proc/sys/fs/binfmt_misc/qemu-aarch64
cat /proc/sys/fs/binfmt_misc/qemu-aarch64
docker buildx create --name multi-arch-builder
docker buildx use multi-arch-builder
docker buildx inspect --bootstrap
docker buildx build --platform linux/arm64,linux/arm,linux/amd64 -t xanimo/dogecoin-1.14.5 . --push
docker buildx imagetools inspect xanimo/dogecoin-1.14.5