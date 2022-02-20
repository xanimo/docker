#!/bin/bash
# echo "$1" | cut -c1
echo "$1"
echo "$2"
"$1:$2"

docker build -t xanimo/1.14.5-dogecoin:modify-chown . --build-arg USER=bluezr --build-arg APP_UID=$1 --build-arg APP_GID=$2
docker run -u "$1:$2" -it --rm --name dogecoin xanimo/1.14-5-dogecoin:modify-chown --regtest