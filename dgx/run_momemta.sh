#!/bin/bash

IMAGE="neubauergroup/bluewaters-momemta:1.0.1"
docker pull "${IMAGE}"

PHYSICS_PROCESS="${1:-drell-yan_ll}"

if [[ ! -d "outputs/${PHYSICS_PROCESS}/momemta" ]]; then
    mkdir -p "outputs/${PHYSICS_PROCESS}/momemta"
fi

docker run \
    --rm \
    -ti \
    -v "$PWD/..":/root/inputs \
    -v "$PWD":/root/data/ \
    --privileged=true \
    "${IMAGE}" "bash ${PHYSICS_PROCESS}/momemta.sh ${PHYSICS_PROCESS}"
