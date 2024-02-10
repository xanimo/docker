#!/bin/bash

OLD_UID=$APP_UID
OLD_GID=$APP_GID
. ./set.sh ${1:-1337} ${2:-69420}
. ./build.sh
. ./run.sh
sleep 5
docker exec -it dogecoin dogecoin-cli getnetworkinfo
docker stop dogecoin
echo "APP_UID:APP_GID=$APP_UID:$APP_GID (old or non-existent)"
echo "APP_UID:APP_GID=$OLD_UID:$OLD_GID (new)"