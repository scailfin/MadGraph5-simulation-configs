#!/bin/bash

IMAGE="scailfin/delphes-python-centos:3.5.0"
docker pull "${IMAGE}"

PHYSICS_PROCESS="drell-yan_ll"

if [[ ! -d "outputs/${PHYSICS_PROCESS}/delphes" ]]; then
    mkdir -p "outputs/${PHYSICS_PROCESS}/delphes"
fi

docker run \
    --rm \
    -ti \
    -v "$PWD/..":/root/inputs \
    -v "$PWD":/root/data/ \
    --privileged=true \
    "${IMAGE}" "bash ${PHYSICS_PROCESS}/delphes.sh ${PHYSICS_PROCESS}"
