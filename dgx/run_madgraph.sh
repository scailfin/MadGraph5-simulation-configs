#!/bin/bash

IMAGE="neubauergroup/bluewaters-mg5_amc:3.1.1"
docker pull "${IMAGE}"

PHYSICS_PROCESS="${1:-drell-yan_ll}"

if [[ ! -d "outputs/${PHYSICS_PROCESS}/madgraph" ]]; then
    mkdir -p "outputs/${PHYSICS_PROCESS}/madgraph"
fi

docker run \
    --rm \
    -ti \
    -v "$PWD/..":/root/inputs \
    -v "$PWD":/root/data/ \
    --privileged=true \
    "${IMAGE}" "bash ${PHYSICS_PROCESS}/madgraph.sh ${PHYSICS_PROCESS}"
