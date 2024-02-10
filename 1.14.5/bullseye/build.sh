#!/bin/bash

docker buildx build --no-cache --build-arg "USER=$USERNAME" --build-arg "APP_UID=$APP_UID" --build-arg "APP_GID=$APP_GID" -t xanimo/1.14.5-dogecoin:modify-chown . --load