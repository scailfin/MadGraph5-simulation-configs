#!/bin/bash

IMAGE="scailfin/madgraph5-amc-nlo-centos:mg5_amc3.2.0"
docker pull "${IMAGE}"

docker run --rm -ti "${IMAGE}"
