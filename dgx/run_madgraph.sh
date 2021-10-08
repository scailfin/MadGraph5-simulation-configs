#!/bin/bash

# IMAGE="scailfin/madgraph5-amc-nlo-centos:mg5_amc3.2.0"
IMAGE="neubauergroup/bluewaters-mg5_amc:3.1.1"
docker pull "${IMAGE}"

docker run \
    --rm \
    -ti \
    -v "$PWD/..":/root/inputs \
    -v "$PWD":/root/data/ \
    --privileged=true \
    "${IMAGE}"
