#!/bin/bash

cp /usr/bin/etcdctl .
cp /usr/bin/docker .
cp /lib64/libdevmapper.so.1.02 .
cp /lib64/libsqlite3.so.0 .

docker build -t keyz182/docker-reg .
