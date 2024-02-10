#!/bin/bash

docker run -d -e APP_UID=$APP_UID -e APP_GID=$APP_GID -u $APP_UID:$APP_GID -it --rm --name dogecoin xanimo/dogecoin
