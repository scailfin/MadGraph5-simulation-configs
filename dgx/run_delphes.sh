#!/bin/bash

IMAGE="scailfin/delphes-python-centos:3.5.0"
docker pull "${IMAGE}"

docker run \
    --rm \
    -ti \
    -v "$PWD/..":/root/inputs \
    -v "$PWD":/root/data/ \
    --privileged=true \
    "${IMAGE}"
