#!/bin/bash

if [[ -f .lock ]]; then
    touch .lock
    docker volume create dogecoin
fi

if docker inspect dogecoin | grep '"Status":' | grep "running"; then
    docker stop dogecoin
fi

docker run -d -e APP_UID=$(id -u $USER) -e APP_GID=$(id -g $USER) -u "$(id -u $USER):$(id -g $USER)" -it --rm --name dogecoin -t xanimo/dogecoin:1.14.5 --regtest
