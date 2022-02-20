#!/bin/bash
docker run -u $1:$2 -it --rm -e APP_UID=$1 -e APP_GID=$2 --name dogecoin xanimo/1.14-5-dogecoin:modify-chown --regtest
