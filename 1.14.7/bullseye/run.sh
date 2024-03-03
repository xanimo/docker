#!/bin/bash

if [[ ! -d /mnt/volumes/.dogecoin ]]; then
    mkdir -p /mnt/volumes/.dogecoin
fi

if docker inspect dogecoin | grep '"Status":' | grep "running"; then
    docker compose down
fi

docker compose up
