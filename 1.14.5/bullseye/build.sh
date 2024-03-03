#!/bin/bash

wget https://raw.githubusercontent.com/dogecoin/dogecoin/master/share/rpcuser/rpcuser.py
chmod +x rpcuser.py
./rpcuser.py dogecoin > auth
rpcauth=$(cat auth | grep "rpcauth")
rpcpassword=$(cat auth | sed '1,/Your password:/d')
echo daemon=1 > dogecoin.conf
echo server=1 >> dogecoin.conf
echo listen=1 >> dogecoin.conf
echo wallet=1 >> dogecoin.conf
echo bind=0.0.0.0:22556 >> dogecoin.conf
echo bind=[::]:22556 >> dogecoin.conf
echo rpcbind=127.0.0.1:22555 >> dogecoin.conf
echo rpcallowip=0.0.0.0/0 >> dogecoin.conf
echo rpcuser=dogecoin >> dogecoin.conf
echo $rpcauth >> dogecoin.conf
echo rpcpassword=$rpcpassword >> dogecoin.conf
echo harddustlimit=0.001 >> dogecoin.conf
rm rpcuser.py auth

docker build --no-cache --build-arg "APP_UID=$(id -u $USER)" --build-arg "APP_GID=$(id -g $USER)" --build-arg "USER=dogecoin" -t xanimo/dogecoin:1.14.5 .
