#!/bin/bash

IMAGE="neubauergroup/bluewaters-mg5_amc:3.1.1"

docker run \
    --rm \
    -ti \
    -v "$PWD":/root/data/ \
    --privileged=true \
    "${IMAGE}" "rm -rf outputs"
