#!/bin/bash

image_name="scailfin/madgraph5-amc-nlo"
image_tag="mg5_amc3.1.0"
image="${image_name}:${image_tag}"

docker pull "${image}"
# docker run --rm -ti -v "${PWD}/..":"${PWD}/.." -w "${PWD}" "${image}" 'bash run_drell-yan.sh'
docker run --rm -v "${PWD}/..":"${PWD}/.." -w "${PWD}" "${image}" 'bash run_drell-yan.sh'
