#!/bin/bash

# image_name="neubauergroup/bluewaters-momemta"
# image_tag="1.0.1"
image_name="neubauergroup/momemta-python-centos"
# image_tag="mg5_amc3.1.0"
image_tag="latest"
image="${image_name}:${image_tag}"

docker pull "${image}"

docker run --rm -ti \
	-v "${PWD}":"${PWD}" \
	-v /data/hepmc_output:/data/hepmc_output \
	-w "${PWD}" \
	"${image}"
