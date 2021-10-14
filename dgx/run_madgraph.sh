#!/bin/bash

# IMAGE="scailfin/madgraph5-amc-nlo-centos:mg5_amc3.2.0"
IMAGE="neubauergroup/bluewaters-mg5_amc:3.1.1"
docker pull "${IMAGE}"

PHYSICS_PROCESS="drell-yan_ll"

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
