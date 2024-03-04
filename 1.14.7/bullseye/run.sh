#!/bin/bash

if [[ ! -d /mnt/volumes/core ]]; then
    mkdir -p /mnt/volumes/core
fi

if docker inspect dogecoin | grep '"Status":' | grep "running"; then
    docker compose down
fi

docker compose up
