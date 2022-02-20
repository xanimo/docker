#!/bin/bash

OLD_UID=$APP_UID
OLD_GID=$APP_GID
. ./set.sh $RANDOM $RANDOM
. ./build.sh
. ./run.sh
sleep 5
docker exec -it dogecoin dogecoin-cli --regtest getnetworkinfo
docker stop dogecoin
echo "APP_UID:APP_GID=$APP_UID:$APP_GID (old or non-existent)"
echo "APP_UID:APP_GID=$OLD_UID:$OLD_GID (new)"